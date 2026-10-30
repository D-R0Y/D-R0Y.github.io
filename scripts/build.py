#!/usr/bin/env python3
"""Dependency-free static site builder. Run from any directory with Python 3.10+."""
import datetime as dt
import html
import json
import re
import shutil
from pathlib import Path
from urllib.parse import urlparse, parse_qs
ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / 'dist'
def esc(x): return html.escape(str(x), quote=True)
def safe_url(url):
    if urlparse(url).scheme not in ('https', 'http', 'mailto'):
        raise ValueError(f'Unsupported URL: {url}')
    return esc(url)
def link(url, label, cls=''):
    return f'<a class="{cls}" href="{safe_url(url)}">{esc(label)}</a>'
def inline(text):
    # Escape all HTML; allow a small documented Markdown subset.
    tokens=[]
    def stash(m):
        tokens.append(link(m[2],m[1])); return f'\x00{len(tokens)-1}\x00'
    text=re.sub(r'\[([^\]]+)\]\(([^\s)]+)\)',stash,text)
    text=esc(text)
    text=re.sub(r'\*\*(.+?)\*\*',r'<strong>\1</strong>',text)
    text=re.sub(r'(?<!\*)\*([^*]+)\*(?!\*)',r'<em>\1</em>',text)
    text=re.sub(r'`([^`]+)`',r'<code>\1</code>',text)
    return re.sub(r'\x00(\d+)\x00',lambda m:tokens[int(m[1])],text)
def markdown(text):
    out=[]; para=[]; items=[]
    def flush():
        if para: out.append('<p>'+inline(' '.join(para))+'</p>'); para.clear()
        if items: out.append('<ul>'+''.join('<li>'+inline(i)+'</li>' for i in items)+'</ul>');items.clear()
    for line in text.splitlines():
        if not line.strip(): flush()
        elif line.startswith(('## ', '### ')):
            flush(); n=len(line.split(' ')[0]);out.append(f'<h{n}>{inline(line[n+1:])}</h{n}>')
        elif line.startswith('- '):
            if para: flush()
            items.append(line[2:])
        else:
            if items: flush()
            para.append(line)
    flush(); return '\n'.join(out)
def video_embed(url):
    p=urlparse(url); host=(p.hostname or '').lower()
    if p.scheme!='https': raise ValueError('Video URL must use HTTPS')
    if host in ('youtube.com','www.youtube.com','m.youtube.com','youtu.be','www.youtube-nocookie.com'):
        if host=='youtu.be': key=p.path.strip('/')
        elif p.path.startswith(('/embed/','/shorts/','/live/')): key=p.path.split('/')[2]
        else: key=parse_qs(p.query).get('v',[''])[0]
        if not re.fullmatch(r'[A-Za-z0-9_-]{11}',key): raise ValueError('YouTube video ID must contain 11 characters')
        return 'https://www.youtube-nocookie.com/embed/'+key
    if host in ('vimeo.com','www.vimeo.com','player.vimeo.com'):
        key=p.path.rstrip('/').split('/')[-1]
        if not key.isdigit(): raise ValueError('Vimeo URL requires a numeric video ID')
        return 'https://player.vimeo.com/video/'+key
    raise ValueError('Use a YouTube or Vimeo video URL')
def load_posts(directory):
    posts=[]
    for path in sorted(directory.glob('*.md')):
        text=path.read_text(encoding='utf-8')
        parts=text.split('---',2)
        if len(parts)!=3 or parts[0].strip(): raise ValueError(f'{path.name}: expected --- metadata block')
        meta={}
        for row in parts[1].splitlines():
            if not row.strip():continue
            if ':' not in row: raise ValueError(f'{path.name}: invalid metadata row')
            k,v=row.split(':',1); meta[k.strip()]=v.strip().strip('"').strip("'")
        if meta.get('draft','true').lower() not in ('true','false'):raise ValueError(f'{path.name}: draft must be true or false')
        if meta.get('draft','true').lower()=='true':continue
        for key in ('title','date','description','video_url'):
            if not meta.get(key):raise ValueError(f'{path.name}: missing {key}')
        date=dt.date.fromisoformat(meta['date']); meta['date']=date.isoformat()
        meta['display_date']=date.strftime('%d %B %Y');meta['embed']=video_embed(meta['video_url'])
        meta['body']=markdown(parts[2]); meta['slug']=path.stem
        posts.append(meta)
    return sorted(posts,key=lambda x:(x['date'],x['slug']),reverse=True)
def shell(p, title, description, body, vlog=False):
    nav=[('about','About'),('interests','Interests'),('research','Research'),('projects','Projects'),('education','Education'),('experience','Teaching'),('skills','Skills'),('contact','Contact')]
    navhtml=''.join(f'<a href="{"index.html" if vlog else ""}#{i}">{t}</a>' for i,t in nav)
    if vlog:navhtml='<a href="index.html">← Academic profile</a>'
    canonical=''
    if p.get('site_url'):
        base=p['site_url'].rstrip('/')+'/';safe_url(base)
        url=base+('vlog.html' if vlog else 'index.html')
        canonical=f'<link rel="canonical" href="{esc(url)}"><meta property="og:url" content="{esc(url)}"><meta property="og:image" content="{esc(base)}assets/social.png"><meta name="twitter:image" content="{esc(base)}assets/social.png">'
    return f'''<!doctype html>
<html lang="en"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">
<title>{esc(title)}</title><meta name="description" content="{esc(description)}"><meta name="author" content="{esc(p['name'])}">
<meta property="og:title" content="{esc(title)}"><meta property="og:description" content="{esc(description)}"><meta property="og:type" content="website"><meta property="og:site_name" content="{esc(p['name'])}"><meta name="twitter:card" content="summary_large_image">{canonical}
<meta name="theme-color" content="#203d38"><link rel="icon" href="assets/favicon.svg" type="image/svg+xml"><link rel="stylesheet" href="assets/style.css"><script src="assets/site.js" defer></script></head>
<body><a class="skip" href="#main">Skip to content</a><header><div class="header-inner"><a class="brand" href="index.html" aria-label="Aninda Roy Dhruba home">ARD<span> / RESEARCH & TEACHING</span></a><button class="menu-toggle" aria-expanded="false" aria-controls="navigation">Menu</button><nav id="navigation" aria-label="Main navigation">{navhtml}<a href="vlog.html" {'aria-current="page"' if vlog else ''}>Vlog ↗</a><a class="nav-cv" href="assets/cv.pdf" download="Aninda-Roy-Dhruba-CV.pdf">CV ↓</a></nav></div></header>
<main id="main">{body}</main><footer><span>{esc(p['name'])} · Academic portfolio</span><span>Research with structure. Evaluation with care.</span></footer></body></html>'''
def heading(n,title):return f'<div class="section-heading"><span class="number">{n:02}</span><h2>{title}</h2></div>'
def build():
    p=json.loads((ROOT/'content/profile.json').read_text())
    if OUT.exists():shutil.rmtree(OUT)
    OUT.mkdir();shutil.copytree(ROOT/'assets',OUT/'assets');(OUT/'.nojekyll').touch()
    b=f'''<section class="hero" aria-labelledby="intro-title"><div><div class="eyebrow">Computer science · Doctoral research aspirations</div><h1 id="intro-title">{esc(p['name'])}<span style="color:var(--accent)">.</span></h1><p class="role">{esc(p['role'])}<br>{esc(p['affiliation'])}</p><p class="intro">{esc(p['intro'])}</p><div class="actions"><a class="button" href="#research">View research <span aria-hidden="true">↗</span></a><a class="text-link" href="assets/cv.pdf" download="Aninda-Roy-Dhruba-CV.pdf">Download CV ↓</a><a class="text-link" href="#contact">Contact</a></div><p style="font-size:11px;margin-top:18px"><a href="assets/cv.pdf" target="_blank" rel="noopener">View CV in browser ↗</a></p></div><aside class="research-map" aria-label="Research focus: structured learning, medical AI, and careful evaluation"><div class="map-top label"><span>Research coordinates</span><span>01—03</span></div><div class="map-center"><span class="label">A connected research agenda</span><h2>Learning from structure.<br>Looking beyond scores.</h2><div class="map-row"><span>01</span> Hierarchical medical classification</div><div class="map-row"><span>02</span> Bias in language models</div><div class="map-row"><span>03</span> Optimization & temporal modeling</div></div><div class="map-bottom">PATIENT DIALOGUE → STRUCTURED OBJECTIVES → EVALUATION<br>Grounded in medical AI. Informed by NLP and time series.</div></aside></section>
<div class="summary-strip"><div><strong>CUET</strong><span>B.Sc. in Computer Science & Engineering</span></div><div><strong>3.89 / 4.00</strong><span>Undergraduate CGPA · Dean’s List</span></div><div><strong>Research & teaching</strong><span>{esc(p['location'])}</span></div></div>
<section class="block" id="about">{heading(1,'A research-led path')}<div class="two-col"><p class="body-copy">{esc(p['about'])}</p><div class="direction"><span class="label">Looking ahead / Doctoral direction</span><p>{esc(p['direction'])}</p></div></div></section>
<section class="block" id="interests">{heading(2,'Questions that guide my work')}<div class="themes">'''
    for t in p['themes']:b+=f'<article class="theme"><h3>{esc(t["title"])}</h3><p>{esc(t["text"])}</p><p class="question">{esc(t["question"])}</p></article>'
    b+='</div></section><section class="block" id="research">'+heading(3,'Research & publications')+'<div>'
    for r in p['research']:
        b+=f'<article class="research-item"><div class="research-side"><strong>{esc(r["role"])}</strong>{esc(r["dates"])}</div><div><h3>{esc(r["title"])}</h3><p>{esc(r["problem"])}</p><p>{esc(r["contribution"])}</p><p class="outcome">{esc(r["outcome"])}</p><div class="methods">{esc(r["methods"])}</div></div></article>'
    b+='</div><h3 class="pub-heading">Publication records</h3>'
    for r in p['publications']:b+=f'<article class="publication"><div><div class="status">{esc(r["venue"])} / {esc(r["status"])}</div><h3>{esc(r["label"])}</h3><p class="note">{esc(r["note"])}</p></div><div>{link(r["url"],"Publisher record ↗")}</div></article>'
    b+='</section><section class="block" id="projects">'+heading(4,'Selected implementations')+'<div class="projects">'
    for r in p['projects']:b+=f'<article class="project"><h3>{esc(r["title"])}</h3><p>{esc(r["text"])}</p><div class="methods">{esc(r["tools"])}</div>{link(r["url"],"Explore code ↗")}</article>'
    e=p['education'];b+=f'</div></section><section class="block" id="education">{heading(5,"Academic foundation")}<div class="education"><div><div class="meta">{esc(e["date"])}</div><h3>{esc(e["degree"])}</h3><p>{esc(e["institution"])}</p></div><div class="score">{esc(e["detail"])}</div></div></section><section class="block" id="experience">{heading(6,"Teaching & professional experience")}<div class="experience">'
    for e in p['experience']:b+=f'<article><span class="meta">{esc(e["dates"])}</span><h3>{esc(e["title"])}</h3><p><strong>{esc(e["institution"])}</strong></p><p>{esc(e["text"])}</p></article>'
    b+='</div></section><section class="block" id="skills">'+heading(7,'Toolkit & distinctions')+'<div class="two-col"><div class="skills"><dl>'
    for s in p['skills']:b+=f'<dt>{esc(s["label"])}</dt><dd>{esc(s["text"])}</dd>'
    b+='</dl></div><div><h3>Achievements</h3><ul class="achievements">'+''.join('<li>'+esc(a)+'</li>' for a in p['achievements'])+'</ul></div></div></section>'
    b+=f'<section class="block" id="contact" style="border:0"><div class="contact"><span class="label">08 / Contact & academic profiles</span><h2>Let’s connect around research.</h2><p>I welcome conversations about doctoral research opportunities and shared interests in medical AI, structured learning, and NLP evaluation.</p>{link("mailto:"+p["email"],p["email"],"email")}<div class="actions">'+''.join(link(x['url'],x['label']+' ↗') for x in p['profiles'])+'<a href="assets/cv.pdf" download="Aninda-Roy-Dhruba-CV.pdf">Download CV ↓</a></div></div></section>'
    (OUT/'index.html').write_text(shell(p,p['name']+' | Computer Science & Medical AI Research',p['intro'],b))
    posts=load_posts(ROOT/'content/vlog')
    b='<section class="vlog-hero"><div class="eyebrow">Research notebook / Video & reflections</div><h1>Notes from the<br>research process.</h1><p>A space for research updates, project demonstrations, academic experiences, and reflections on preparing for doctoral study.</p></section>'
    if not posts:b+='<section class="empty"><div class="symbol" aria-hidden="true">[ 01 ]</div><div><span class="label">The notebook is open</span><h2 style="margin:15px 0">Updates will appear here.</h2><p>No entries have been published yet. In the meantime, explore my research and selected projects on the academic profile.</p><a class="text-link" href="index.html#research">Explore my research ↗</a></div></section>'
    for post in posts:
        b+=f'<article class="vlog-entry" id="{esc(post["slug"])}"><time class="meta" datetime="{post["date"]}">{esc(post["display_date"])}</time><h2>{esc(post["title"])}</h2><p>{esc(post["description"])}</p><iframe class="video" src="{esc(post["embed"])}" title="{esc(post["title"])} — video" loading="lazy" referrerpolicy="strict-origin-when-cross-origin" allow="accelerometer; autoplay; clipboard-write; encrypted-media; gyroscope; picture-in-picture; fullscreen" allowfullscreen></iframe><p>{link(post["video_url"],"Watch on video platform ↗")}</p><div class="post-body">{post["body"]}</div></article>'
    (OUT/'vlog.html').write_text(shell(p,'Vlog | '+p['name'],'Research updates, project demonstrations, and academic reflections by '+p['name']+'.',b,True))
    print(f'Built {OUT}: 2 pages, {len(posts)} published vlog entries')
if __name__=='__main__':build()
