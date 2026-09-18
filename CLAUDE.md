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

**Content changes therefore go: Seki's xlsx → gsheet → this repo's HTML.** Never route
them through the Design project.

### Runbook — new content arrives (a `Website content_YYYYMMDD.xlsx` from Seki)

Follow these in order. Steps 1 and 2 are the ones that go wrong.

**1. Merge the xlsx into the gsheet — merge, never replace.**
Diff *both* directions first and treat gsheet-only rows as content to preserve, then
hand-edit the deltas. The gsheet and Seki's dated snapshots are divergent branches;
neither is a superset. *File → Import → Replace spreadsheet* looks like a clean
one-step update and silently deletes whatever only the gsheet had — in 2026-08 that
would have been two former students. Read/write mechanics and the full evidence are in
the Claude memory notes `website-content-sheet-lineage` and `gsheet-edit-technique`
(`~/.claude/projects/-Users-aslee-agents-rec23-03-website/memory/`).

**2. Export the merged gsheet to xlsx.**
Do not skip to step 3 using Seki's file. The moment step 1 lands, her xlsx is stale
relative to the gsheet — checking against it re-blinds you to exactly the gsheet-only
content step 1 just protected.

**3. Update this repo's HTML, then check.**

```bash
python3 tools/check_content.py <fresh-export.xlsx>
python3 tools/check_content.py                      # newest Website content_*.xlsx on Drive
```

Reports sheet entries that never reached a page; exits 1 on drift. Also flags the
reverse case — anyone in the sheet's `Deleted (not upload for website)` block who
appears on a page.

**4. Read the diff before committing.**
The checker answers "did every sheet entry reach a page?" — nothing more. It is
one-directional and presence-only on purpose (whitespace and bilingual-markup diffing
buries real findings in noise), so it will not catch a mistyped affiliation, a person
in the wrong section, or an EN string pasted into a JP span. Verify rendered pages in
Chrome, both languages, desktop + 390 px.

Note `main` is the deploy branch — pushing publishes to the live public site.

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
- **2026-09-17/18** — from Seki's two September mails and her
  `Website content_20260917.xlsx`: **Watanabe Rikuto** (渡辺 陸斗, Kwansei Gakuin,
  卒論生 under Kuwahara) added — active members 26 → 27, institutions still 15; the
  4 September-2026 talks (JGS 133rd ×2, GSJ geochemistry 73rd ×2) added — contributions
  53 → 57; 2 meetings (2026-05-27 JpGU, 2026-06-29 stratigraphy) added to
  `activities.html`. Two errors in her file were corrected in the gsheet *and* the
  page: rows 55–56 said "The 132nd Annual Meeting of the Geological Society of Japan"
  where the JP cell and the date say the 133rd (2026 Kanazawa), and row 56's JP author
  list lacked the separator before 多田隆治. The gsheet is therefore **ahead of her
  20260917 file** by those two fixes plus Watanabe, Nomura, Mori and the 26K21423
  grant — her next export must start from the gsheet. Watanabe is a 卒論生, so expect
  a move to former members around 2027-03 (27 → 26, former kicker 5 → 6).
- Home news line says the 2026-03 workshop had **25** contributions (derived from the
  content data at build time; the design's original copy said 24). No news line was
  added for the JpGU-AGU 2026 or the September 2026 meetings.
- The gsheet is **link-readable without auth**, so a fresh export needs no browser:
  `curl -sSL -o <file>.xlsx "https://docs.google.com/spreadsheets/d/<id>/export?format=xlsx"`.
  Keep exports out of the Drive `website/` folder and away from the
  `Website content_*.xlsx` name — that pattern is Seki's snapshots, and
  `check_content.py` auto-picks the newest one.

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
- Data inconsistencies: prefer counts derivable from **the content sheet** (e.g. hero
  says **15** institutions, not the design's stale 13). Counts appear in the pages as
  literals — the members page carries an active-members count and a former-members
  kicker — so re-derive them whenever rows are added or moved between sections. The
  drift checker does not verify counts.

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
