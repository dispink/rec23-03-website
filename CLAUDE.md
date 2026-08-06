# rec23-03-website — static site for the ReC23-03 project

Public website for **ReC23-03 — The Japan Sea paleoceanography and paleoclimatology
during the Miocene** (J-DESC ReCoRD program, PI Arisa Seki). An-Sheng Lee maintains it.
Plain static HTML/CSS + a few lines of vanilla JS — **no build step, no frameworks**.
See `README.md` for the file-by-file overview.

## Design source of truth

The Claude Design project **"ReC23-03 website"**, id
`01988d24-923f-4c8b-8bd8-7baa15376bc8`, holds the designs for ALL pages and the full
site content. Read it with the **DesignSync** tool (`list_files`, `get_file`); if auth
fails, ask An-Sheng to run `/design-login`.

Key remote files:
- `data.js` — canonical content: members, presentations, activities, grants, news,
  gallery captions (EN + JP). Treat it as the data source when implementing pages.
- `layout.jsx` / `styles.css` — shared chrome (utility bar, masthead, nav, footer) and
  design system. Local `styles.css` = remote one + appended production sections.
- `members.html`, `presentations.html`, etc. — per-page React/Babel prototypes.
- Do NOT fetch binary assets via `get_file` (256 KiB cap + base64 floods context) —
  photo originals are on Drive (below).

## Status

- All seven pages implemented and verified in Chrome (EN + JP, desktop + 390 px)
  2026-08-07. Home hero/highlights verified 2026-08-06.
- The pending Seki content edits (remove Tagaya; Tojima → former; Aoyagi → current;
  newest presentation rows from `Website content_20260617.xlsx`) were already merged
  into the Design project's `data.js` and are reflected in the built pages. The
  remote `__newdata.json` is a stale dump of the older sheet — ignore it.
- Home news line says the 2026-03 workshop had **25** contributions (derived from
  `data.js`; the design's original copy said 24).

## Conventions (follow these when implementing pages)

- **Compile prototypes away**: convert each page's JSX to static HTML; move its inline
  JSX styles into a clearly-marked appended section of `styles.css`. Keep the design's
  class names and tokens; don't restyle.
- **Bilingual EN/JP**: every translatable node gets sibling `<span class="en">` /
  `<span class="jp">` (block elements: two siblings classed `en`/`jp`). Visibility is
  driven by `data-lang` on `<html>`; toggle + persistence (`localStorage["rec23.lang"]`)
  is the small script at the bottom of `index.html` — reuse it verbatim on new pages,
  along with the head snippet that applies the saved language before first paint.
- Shared chrome (utility bar, masthead, nav, footer) is currently duplicated per page —
  copy it from `index.html` and set the page's nav link to `class="active"`.
- Numbers/dates use `.numeral`; keep the light theme default (`color-scheme: light`).
- Data inconsistencies: prefer counts derivable from `data.js` (e.g. hero says
  **15** institutions, not the design's stale 13).

## Assets

Photo originals: `~/Library/CloudStorage/GoogleDrive-a59052705@gmail.com/My Drive/Acadamics/Projects/ReC23-03/website/`.
Web-size into `assets/` with sips, then check EXIF GPS before committing to a public page:

```bash
sips -Z 1400 --setProperty formatOptions 75 assets/<name>.jpg
mdls -name kMDItemLatitude assets/<name>.jpg   # must be (null)
```

## Preview & verification

```bash
python3 -m http.server 8743   # from this folder → http://127.0.0.1:8743/
```

Verify rendered pages in Chrome (both languages, desktop + narrow). Caveat: An-Sheng's
Chrome runs **Dark Reader**, which repaints the light design dark — that is not a site
bug. To see true colors, inject `<meta name="darkreader-lock">` into the tab (JS) or
use a profile without the extension. His window manager may ignore `resize_window`;
test responsive layouts by loading the page in a fixed-width iframe instead.
