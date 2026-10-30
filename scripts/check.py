"""Checks built links, CV bytes, content integrity, and a real vlog build lifecycle."""
import hashlib
import tempfile
from pathlib import Path
from html.parser import HTMLParser
from urllib.parse import urlparse, unquote
import build
class Page(HTMLParser):
    def __init__(self,text):
        super().__init__();self.ids=[];self.refs=[];self.downloads=[];self.feed(text)
    def handle_starttag(self,tag,attrs):
        a=dict(attrs)
        if 'id' in a:self.ids.append(a['id'])
        for key in ('href','src'):
            if a.get(key):self.refs.append(a[key])
        if 'download' in a:self.downloads.append(a.get('href'))
def validate_pages():
    out=build.OUT
    for pagepath in out.glob('*.html'):
        page=Page(pagepath.read_text());assert len(page.ids)==len(set(page.ids)), 'Duplicate IDs'
        for ref in page.refs:
            p=urlparse(ref)
            if p.scheme or p.netloc:continue
            assert not p.path.startswith('/'),f'Root-relative URL breaks repository hosting: {ref}'
            dest=pagepath.parent / unquote(p.path) if p.path else pagepath
            assert dest.is_file(),f'Missing asset {dest}'
            if p.fragment and dest.suffix=='.html':assert p.fragment in Page(dest.read_text()).ids,ref
        for download in page.downloads:assert (out/download).read_bytes().startswith(b'%PDF-')
    assert hashlib.sha256((out/'assets/cv.pdf').read_bytes()).digest()==hashlib.sha256((build.ROOT/'assets/cv.pdf').read_bytes()).digest()
    print('PASS: both pages, anchors, local assets, relative deployment paths, CV download targets and exact PDF bytes')
validate_pages()
original_root,original_out=build.ROOT,build.OUT
with tempfile.TemporaryDirectory() as d:
    import shutil
    root=Path(d);shutil.copytree(original_root/'content',root/'content');shutil.copytree(original_root/'assets',root/'assets')
    build.ROOT=root;build.OUT=root/'dist'
    posts=root/'content/vlog'
    for f in posts.glob('*.md'):f.unlink()
    def post(name,date,draft='false',title=None):
        (posts/name).write_text(f'---\ntitle: {title or name}\ndate: {date}\nvideo_url: https://youtu.be/dQw4w9WgXcQ\ndescription: Temporary test only\ndraft: {draft}\n---\n## Notes\n\n**Bold** and [link](https://example.org).\n\n- Item\n<script>alert(1)</script>')
    post('older.md','2025-01-01');post('newer.md','2026-01-01');post('hidden.md','2027-01-01','true')
    build.build();page=(build.OUT/'vlog.html').read_text()
    assert page.index('id="newer"')<page.index('id="older"')
    assert 'id="hidden"' not in page and 'youtube-nocookie.com/embed/' in page
    assert '<strong>Bold</strong>' in page and '<script>alert' not in page
    post('newer.md','2026-01-01',title='Updated entry');build.build();assert 'Updated entry' in (build.OUT/'vlog.html').read_text()
    (posts/'newer.md').unlink();(posts/'older.md').unlink();build.build();assert 'No entries have been published yet' in (build.OUT/'vlog.html').read_text()
    for url in ('javascript:alert(1)','https://example.org/video','https://youtube.com/watch?v=BAD'):
        try:build.video_embed(url)
        except ValueError:pass
        else:raise AssertionError('Unsafe or invalid video accepted')
    assert build.video_embed('https://vimeo.com/123456')=='https://player.vimeo.com/video/123456'
    print('PASS: vlog add/edit/remove, newest-first ordering, drafts, Markdown, safe embeds and empty state')
build.ROOT,build.OUT=original_root,original_out
