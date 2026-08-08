# rec23-03-website — static site for the ReC23-03 project

Public website for **ReC23-03 — The Japan Sea paleoceanography and paleoclimatology
during the Miocene** (J-DESC ReCoRD program, PI Arisa Seki). An-Sheng Lee maintains it.
Plain static HTML/CSS + a few lines of vanilla JS — **no build step, no frameworks**.
See `README.md` for the file-by-file overview.

## Sources of truth

Three artifacts hold overlapping copies of this site. Keeping all three in step by
hand does not work — it has already silently dropped content twice. So they are split
by role, and only two of them are authoritative:

| Artifact | Role |
|---|---|
| **`Website content` gsheet** (Drive, below) | **Content** source of truth — members, presentations, activities, grants, news |
| **Static HTML in this repo** | What ships. The build output; edit it directly |
| **Claude Design project** — `layout.jsx`, `styles.css`, page prototypes | **Design** source of truth — chrome, tokens, layout |
| Design project `data.js` | Design-time fixture only. **Expected to lag content** — do not treat it as canonical |

`data.js` was canonical while the site was being designed. That ended at launch:
content now originates in Seki's spreadsheet and ships from this repo, so a third
canonical copy inside a design tool just adds a sync step that gets skipped. Refresh
`data.js` only when you are about to do *design* work and want the prototypes
rendering against realistic data — not on every content change.

**Content changes therefore go: gsheet → this repo's HTML.** Do not route them through
the Design project. After any content change run the drift check:

```bash
python3 tools/check_content.py            # newest Website content_*.xlsx on Drive
python3 tools/check_content.py <file>     # or an explicit export
```

It reports sheet entries that never reached a page (exit 1 if any). It is
one-directional and presence-only by design — it will not flag whitespace or
bilingual-markup differences, which are noise. **Caveat:** it can only see what is in
the export you give it, so content added straight to the gsheet needs a fresh export
to be checked. See [[website-content-sheet-lineage]] — the gsheet and Seki's dated
xlsx snapshots are divergent branches that each carry unique rows, so **never** update
the sheet via *File → Import → Replace spreadsheet*.

### Design project

Id `01988d24-923f-4c8b-8bd8-7baa15376bc8`. Read with the **DesignSync** tool
(`list_files`, `get_file`); it can also write (`finalize_plan` → `write_files`) if you
ever do need to push a refresh. If auth fails, ask An-Sheng to run `/design-login`.
- `layout.jsx` / `styles.css` — shared chrome (utility bar, masthead, nav, footer) and
  design system. Local `styles.css` = remote one + appended production sections.
- `members.html`, `presentations.html`, etc. — per-page React/Babel prototypes.
- Do NOT fetch binary assets via `get_file` (256 KiB cap + base64 floods context) —
  photo originals are on Drive (below).

## Status

- **Live** at https://dispink.github.io/rec23-03-website/ since 2026-08-07 (GitHub
  Pages, legacy build from `main` root, repo public, HTTPS enforced). Pending: a
  custom domain to get past university filters that block `*.github.io` (Kochi U.
  does) — preferred route is asking J-DESC for `rec23-03.j-desc.org` → CNAME to
  `dispink.github.io`; once granted, set the domain in Pages settings and add the
  `CNAME` file.
- All seven pages implemented and verified in Chrome (EN + JP, desktop + 390 px)
  2026-08-07. Home hero/highlights verified 2026-08-06.
- The Seki content edits (remove Tagaya; Tojima → former; Aoyagi → current; newest
  presentation rows from `Website content_20260617.xlsx`) are in `data.js` and in the
  built pages. The remote `__newdata.json` is a stale dump of the older sheet — ignore
  it.
- **2026-08-08** — the gsheet was brought up to `20260617` by hand (member moves,
  6 new presentations, 4 author fixes) and An-Sheng's KAKENHI 若手研究 26K21423
  (2026-04→2029-03, "Repurposing Legacy Archives") was added to Others → Research
  Grants and to `others.html`. Also fixed a launch-day gap: **Nomura Hinako** and
  **Mori Sara** are gsheet-only former students that `data.js` never had, so they were
  missing from `members.html` — now added, former-members kicker 3 → 5. `data.js`
  itself is *not* updated for any of this, which is expected (see above).
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
