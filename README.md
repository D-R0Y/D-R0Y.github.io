# Aninda Roy Dhruba — academic portfolio

A two-page, research-first portfolio designed for GitHub Pages. Warm paper, forest green, restrained terracotta, system sans-serif and Georgia typography. All fonts and assets work without a third-party CDN. The source CV is included unchanged.

## Quick preview

Requires Python 3.10 or newer. There are **no packages to install**.

```sh
python scripts/build.py
python scripts/check.py
python -m http.server 8000 --directory dist
```

Open http://localhost:8000. The supplied `dist/index.html` can also be opened directly for a quick offline look; video embeds need an internet connection. Rebuild after changing content. The build replaces `dist`, so never edit generated files there.

## Deploy to GitHub Pages

1. Create a GitHub repository. For a root personal site, use `D-R0Y.github.io` under the `D-R0Y` account. For a project site, any repository name works (for example, `academic-portfolio`). Use a public repository unless your GitHub plan supports private-repository Pages.
2. Upload the **contents** of this project to the repository root, not the enclosing `academic-portfolio` folder. Keep `assets`, `content`, `scripts`, `templates`, and `.github/workflows/pages.yml`. The bundled `dist` folder is a preview, not required in Git. Hidden folders may be missed by a browser or file manager: if `.github` was omitted, use GitHub **Add file → Create new file**, enter `.github/workflows/pages.yml`, and paste the supplied file exactly.
3. Use `main` as the default branch. If using another branch, change the workflow's `branches: [main]` value.
4. Open repository **Settings → Pages**, and choose **GitHub Actions** as the build/deployment source.
5. Open **Actions → Build and deploy academic portfolio → Run workflow**, selecting `main`. Later commits to `main` trigger deployment automatically. The workflow builds, checks, uploads `dist`, and deploys it.
6. Open the URL reported by the completed deployment. A personal repository typically uses `https://D-R0Y.github.io/`; a project repository uses `https://D-R0Y.github.io/academic-portfolio/`.
7. Edit `content/profile.json` and set `site_url` to your actual deployed URL, including the repository name if applicable. Commit. This enables correct canonical URLs and absolute social-image URLs. Until set, the site deliberately omits those tags rather than publishing a fictional address.

Every internal link and asset is relative, so root sites and repository subpaths both work without changing a base path. No custom domain is required. The repository has not been created or deployed on your behalf.

## Folder guide

| Path | Purpose |
|---|---|
| `content/profile.json` | Editable profile, research, publications, projects, education, skills and contact |
| `content/vlog/*.md` | Published and draft vlog source files; discovered automatically |
| `templates/vlog-entry.md` | Copyable draft template, never published automatically |
| `assets/cv.pdf` | Actual CV; replace this file to update every CV link |
| `assets/style.css` | Responsive styling, reduced-motion support and print rules |
| `assets/site.js` | Mobile menu and active-section highlighting |
| `assets/social.png` | 1200 × 630 social-sharing image |
| `assets/favicon.svg` | Initial-based icon |
| `scripts/build.py` | Static page layout, Markdown subset and content validation |
| `scripts/check.py` | Asset/anchor/CV and vlog lifecycle checks |
| `.github/workflows/pages.yml` | Automated GitHub Pages build and deployment |
| `dist/` | Generated, ready-to-serve website |

## Edit your academic profile

Open `content/profile.json` on GitHub, click the pencil, edit text and commit. Preserve JSON quotes, commas, and square/curly brackets. GitHub Actions validates the build. Add or remove list items by copying or removing complete objects. Content is HTML-escaped automatically. `profiles` supports additional academic accounts, including LinkedIn, by adding a `label` and full HTTPS `url`.

The research questions and doctoral-direction paragraph are proposed aspirations grounded in the CV, not claims of completed research. Review them before publishing. Publication records intentionally use descriptive labels rather than invented exact titles. All source links come from the PDF annotations. External availability and bibliographic details could not be independently verified in this environment.

Structural headings, hero graphic labels, summary strip and navigation live in `scripts/build.py`. Routine biography and work edits belong in JSON; a substantial change in degree, research direction, or identity may also warrant updating these concise design labels and `assets/social.png`.

## Replace the CV

Upload the new PDF to `assets/cv.pdf`, replacing the existing file, then commit. Keep the lowercase filename. All download buttons and the browser-view link update together. The PDF includes the contact information present in your original CV.

## Publish a vlog using GitHub's web interface

1. Open `templates/vlog-entry.md` and copy its contents.
2. Choose **Add file → Create new file** and name it `content/vlog/2026-11-05-your-topic.md` (use your actual date and a unique lowercase slug).
3. Paste the template, then edit its metadata. Each metadata field is a single line. This deliberately simple front-matter parser supports plain text or one pair of surrounding quotes, not full YAML.

```markdown
---
title: My actual research update title
date: 2026-11-05
video_url: https://www.youtube.com/watch?v=YOUR_11_CHARACTER_ID
description: A concise explanation of the video.
draft: false
---
## Context

Write an optional reflection here.

- One observation
- A next step
```

4. Replace the example URL with a real **YouTube or Vimeo** URL whose owner allows embedding. The placeholder above is intentionally not a valid video ID. Supported YouTube forms: `watch?v=`, `youtu.be/`, `/shorts/`, `/live/`, `/embed/`; Vimeo numeric video URLs are supported. Other providers require extending `video_embed()` in the builder.
5. Use an ISO date (`YYYY-MM-DD`) and set `draft: false` only when ready. Drafts default to hidden. Future dates are not scheduling: any file with `draft: false` is published on the next build.
6. Commit. GitHub Actions rebuilds automatically; no component or index file needs editing. Entries sort newest first by the metadata date, then filename for ties.

The body supports paragraphs, `##`/`###` headings, `**bold**`, `*emphasis*`, backtick inline code, HTTPS/HTTP links, and `-` bullet lists. Arbitrary HTML, Markdown tables, images, nested lists, and fenced code blocks are not supported by this intentionally small renderer. The body is optional. YouTube embeds use the privacy-enhanced domain and all videos are lazy-loaded. Embedded media still uses third-party services; a direct watch link is provided if embedding is blocked.

**Edit:** change the entry file and commit. **Unpublish:** set `draft: true`. **Remove:** delete the file and commit. The page returns to its empty state when no published entries remain. The template is outside the content directory and cannot appear as a fabricated post.

## Items to confirm or supply

- Full author lists, exact paper titles, publication year, and DOI for both publication records. The CV describes Array as published and ICCIT as accepted; these statuses are retained. The Array entry says 2025, while its supplied URL includes a 2026 identifier; the site leaves the year unspecified pending confirmation. Q1 ranking is omitted because it was not independently verified.
- PGCB data period: the CV says ten years in Research Experience and nine years in Selected Projects. The site says historical load data. Please supply the correct period and evaluation protocol for the reported 1.09% MAPE.
- Actual deployed `site_url`, needed for canonical and social-image URLs.
- Your first real vlog video, title, date, and description. No fabricated entries are included.
- Optional LinkedIn URL, headshot, thesis repository link and exact UNLP track names. These are omitted rather than filled with placeholders.
- Review the proposed future research direction and confirm that the CV's “Present” appointments remain current.

## Verification

`python scripts/check.py` checks both generated pages, every local link and fragment, all local assets, relative-path compatibility, PDF download targets, and byte-for-byte CV copying. It builds temporary vlog fixtures to test adding, editing, deleting, draft exclusion, reverse chronology, Markdown escaping, and supported video formats. Temporary posts never enter the delivered site.

The supplied navigation script supports a mobile toggle, Escape-to-close, active-section indication, and reduced-motion-aware smooth scrolling. The core content and links also work without JavaScript. CSS contains desktop/tablet/mobile layouts, visible keyboard focus, and a skip link.

**Verification limitation:** the development environment's browser-preview relay was unavailable. Actual browser interaction, rendered mobile layout, live video playback, external publisher availability and GitHub deployment were not visually/live verified. Before public use, check at 375px, 768px, and 1440px widths; use Tab/Enter/Escape on the menu; click section links and CV links; and publish one real video with embedding enabled. Build and automated link/content checks passed.

## Why this approach

Two generated HTML files, a small Python standard-library build, and a GitHub Actions workflow keep hosting static and updates file-based. There is no Node dependency tree, backend, database, or runtime API. The tradeoff is a deliberately limited Markdown dialect and a required rebuild after edits; GitHub handles that automatically. Full Markdown or a visual CMS can be added later if the publication workflow grows.
