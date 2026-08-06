# ReC23-03 project website

Static website for **ReC23-03 — The Japan Sea paleoceanography and paleoclimatology
during the Miocene** (J-DESC ReCoRD program, PI Arisa Seki).

Implemented from the Claude Design project **"ReC23-03 website"**
(claude.ai/design/p/01988d24-923f-4c8b-8bd8-7baa15376bc8), which remains the design
source of truth (layouts for the other pages, `data.js` content, tweak variants).

## Pages

All pages are implemented (compiled from the Design project prototypes):

- `index.html` — Home (editorial hero variant, per the design's tweak defaults).
- `members.html` — member list with a List / By-institution view toggle (vanilla JS),
  plus former members. Content reflects the June 2026 sheet (Tojima → former,
  Aoyagi → current, Tagaya removed).
- `activities.html` — major activities, recurring meetings, outreach cards.
- `publications.html` — peer-reviewed placeholder box, news & coverage, funded grants.
- `presentations.html` — all 53 contributions grouped by event, newest first.
- `gallery.html` — photo grid with a click-to-zoom lightbox (vanilla JS).
- `others.html` — related websites, grants, outreach, related news.

## How it works

- Plain static HTML + CSS + a few lines of vanilla JS — no build step, no frameworks.
  The design prototype's React/Babel runtime was compiled away by hand.
- **Bilingual EN/JP**: every translatable node has `.en`/`.jp` sibling spans; the
  `data-lang` attribute on `<html>` picks one (CSS in `styles.css`). The EN/JP buttons
  in the utility bar toggle it, persisted to `localStorage["rec23.lang"]` (same key as
  the prototype). Without JS the page renders in English.
- `styles.css` = the design system stylesheet from the Design project, plus appended
  sections: bilingual visibility, home-page section classes, and a sub-pages section
  (all converted from the prototypes' inline JSX styles), with mobile breakpoints.
  Sub-page `<main class="shell sub">` opts out of the home page's per-section divider.
  A dark palette exists under `[data-theme="dark"]` but is not wired to a toggle
  (design default is light).
- `assets/` — web-sized JPEGs (≤1800 px, quality ~75) generated from the originals in
  `My Drive/Acadamics/Projects/ReC23-03/website/` (`AORI_workshop_GroupPhoto.jpg` →
  `team-kashiwa-2026.jpg`; `Sampling_party_*.jpg` → `sampling_party_*.jpg`).
  No GPS EXIF (checked).

## Preview

```bash
cd "$(dirname "$0")" && python3 -m http.server 8743
# → http://127.0.0.1:8743/
```

(Opening `index.html` directly via `file://` also works.)
