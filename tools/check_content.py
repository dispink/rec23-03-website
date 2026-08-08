#!/usr/bin/env python3
"""Report drift between the content source and the built pages.

The `Website content` spreadsheet is the content source of truth; the static HTML
in this repo is what ships. Nothing keeps them in step automatically, so run this
after every content update.

    python3 tools/check_content.py "path/to/Website content_20260617.xlsx"

With no argument it picks the newest `Website content_*.xlsx` from the Drive folder.
Exit status is 1 if anything is missing, so it can gate a commit.

This checks *presence*, not formatting: for each person / presentation / grant in
the sheet it asks whether a distinctive string reaches the corresponding page. It
deliberately does not try to diff whitespace or bilingual markup — those produce
noise, not findings. See CLAUDE.md for why data.js is not checked.
"""

import glob
import html
import os
import re
import sys
import zipfile
import xml.etree.ElementTree as ET

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
DRIVE = os.path.expanduser(
    '~/Library/CloudStorage/GoogleDrive-a59052705@gmail.com/My Drive/'
    'Acadamics/Projects/ReC23-03/website'
)

NS = {
    'm': 'http://schemas.openxmlformats.org/spreadsheetml/2006/main',
    'r': 'http://schemas.openxmlformats.org/officeDocument/2006/relationships',
}


# ---------------------------------------------------------------- xlsx reading

def _shared_strings(z):
    out = []
    if 'xl/sharedStrings.xml' not in z.namelist():
        return out
    root = ET.fromstring(z.read('xl/sharedStrings.xml'))
    for si in root.findall('m:si', NS):
        # Skip <rPh> (furigana) — including it corrupts Japanese cells
        # e.g. 読売新聞 -> 読売新聞ヨミウリ.
        parts = [t.text or '' for t in si.findall('m:t', NS)]
        for run in si.findall('m:r', NS):
            parts += [t.text or '' for t in run.findall('m:t', NS)]
        out.append(''.join(parts))
    return out


def _col(ref):
    n = 0
    for ch in re.match(r'([A-Z]+)', ref).group(1):
        n = n * 26 + (ord(ch) - 64)
    return n - 1


def read_sheets(path):
    """{sheet name: {row number: [cell, ...]}} — sheet names keep trailing spaces."""
    z = zipfile.ZipFile(path)
    ss = _shared_strings(z)
    wb = ET.fromstring(z.read('xl/workbook.xml'))
    rels = {r.get('Id'): r.get('Target')
            for r in ET.fromstring(z.read('xl/_rels/workbook.xml.rels'))}
    sheets = {}
    for sh in wb.find('m:sheets', NS):
        target = rels[sh.get('{%s}id' % NS['r'])]
        if not target.startswith('xl/'):
            target = 'xl/' + target.lstrip('/')
        rows = {}
        for row in ET.fromstring(z.read(target)).find('m:sheetData', NS).findall('m:row', NS):
            cells = {}
            for c in row.findall('m:c', NS):
                v = c.find('m:v', NS)
                if c.get('t') == 's':
                    val = ss[int(v.text)] if v is not None else ''
                elif c.get('t') == 'inlineStr':
                    el = c.find('m:is', NS)
                    val = ''.join(x.text or '' for x in el.iter('{%s}t' % NS['m'])) if el is not None else ''
                else:
                    val = v.text if v is not None else ''
                if (val or '').strip():
                    cells[_col(c.get('r'))] = val.strip()
            if cells:
                rows[int(row.get('r'))] = [cells.get(i, '') for i in range(max(cells) + 1)]
        sheets[sh.get('name')] = rows
    return sheets


def sheet_named(sheets, prefix):
    """Tab names carry stray trailing spaces (e.g. 'Presentation ')."""
    for name in sheets:
        if name.strip() == prefix:
            return sheets[name]
    return {}


# ----------------------------------------------------------------- page text

def page_text(name):
    with open(os.path.join(REPO, name), encoding='utf-8') as fh:
        raw = fh.read()
    # Strip tags so a name split across <span>s still matches, and unescape
    # entities so "Former members &amp; students" compares as written.
    return html.unescape(re.sub(r'<[^>]+>', '', raw))


def cell(row, i):
    return row[i].strip() if i < len(row) else ''


# ------------------------------------------------------------------- checks

def check_members(sheets, problems):
    rows = sheet_named(sheets, 'Member list')
    text = page_text('members.html')
    section = None
    for n in sorted(rows):
        row = rows[n]
        head = cell(row, 0)
        if head.startswith('Former members'):
            section = 'former'
            continue
        if head.startswith('Deleted'):
            section = 'deleted'          # explicitly not for the website
            continue
        if n == 1 or not head:
            continue
        if section is None:
            section = 'current'
        family, given = head, cell(row, 1)
        if section == 'deleted':
            if family in text:
                problems.append(
                    f'members.html: "{family} {given}" is in the sheet\'s '
                    f'"Deleted (not upload for website)" block but appears on the page')
            continue
        # Match on the Japanese surname+given, which is unambiguous; fall back
        # to the romanised family name for non-Japanese members.
        needle = (cell(row, 2) + ' ' + cell(row, 3)).strip() or family
        if needle not in text and family not in text:
            problems.append(f'members.html: missing {section} member "{family} {given}" ({needle})')


def check_presentations(sheets, problems):
    rows = sheet_named(sheets, 'Presentation')
    text = page_text('presentations.html')
    for n in sorted(rows):
        title = cell(rows[n], 3)
        if n == 1 or not title or title == 'Title':
            continue
        # Titles wrap in the source cells; compare on a distinctive slice.
        probe = ' '.join(title.split())[:60]
        if probe and probe not in ' '.join(text.split()):
            problems.append(f'presentations.html: missing row {n} — "{probe}…"')


def check_grants(sheets, problems):
    rows = sheet_named(sheets, 'Others')
    text = ' '.join(page_text('others.html').split())
    inside = False
    for n in sorted(rows):
        first = cell(rows[n], 0)
        if first.startswith('Research Grants'):
            inside = True
            continue
        if inside and first.startswith('Related '):
            break
        if not inside or first in ('', 'Date'):
            continue
        title = ' '.join(cell(rows[n], 2).split())[:60]
        if title and title not in text:
            problems.append(f'others.html: missing grant row {n} — "{title}…"')


def main():
    if len(sys.argv) > 1:
        src = sys.argv[1]
    else:
        found = sorted(glob.glob(os.path.join(DRIVE, 'Website content_*.xlsx')))
        if not found:
            sys.exit(f'No "Website content_*.xlsx" found in {DRIVE}\n'
                     f'Pass one explicitly, or export the gsheet first.')
        src = found[-1]

    print(f'source : {os.path.basename(src)}')
    print(f'pages  : members.html, presentations.html, others.html\n')

    sheets = read_sheets(src)
    problems = []
    check_members(sheets, problems)
    check_presentations(sheets, problems)
    check_grants(sheets, problems)

    if not problems:
        print('No drift: every sheet entry reaches its page.')
        return 0
    print(f'{len(problems)} item(s) in the sheet do not reach the built pages:\n')
    for p in problems:
        print(f'  - {p}')
    print('\nNote: content the gsheet has but no xlsx export does (e.g. members added\n'
          'directly to the sheet) will only be caught if you check against a fresh\n'
          'export rather than an old Website content_*.xlsx.')
    return 1


if __name__ == '__main__':
    sys.exit(main())
