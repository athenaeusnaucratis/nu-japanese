"""
Build the interactive single-file HTML version of the Japanese course.

Usage:
    python3 src/build.py              # writes ./index.html at the repo root
    python3 src/build.py path/to.html # writes somewhere else

index.html is GENERATED. Never hand-edit it — edit app.css / app.js, the
content_*.py modules or this file, and rebuild, or your changes get overwritten.
"""
import copy
import json
import os
import re
import sys

SRC = os.path.dirname(os.path.abspath(__file__))
REPO_ROOT = os.path.dirname(SRC)
sys.path.insert(0, SRC)
from content_front import FRONT_MATTER, RESOURCES
from content_weeks import WEEKS
from content_appx import APPENDICES
import content_glyphs
from content_kanji import KANJI
import content_practice

# Vocab rows that existed before stable IDs and were deliberately removed:
# the week 9 te-form rules, now a table. Stars on them are dropped silently.
RETIRED_IDS = [
    'v:う, つ, る → って|u, tsu, ru → tte',
    'v:ぶ, む, ぬ → んで|bu, mu, nu → nde',
    'v:く → いて|ku → ite',
    'v:ぐ → いで|gu → ide',
    'v:す → して|su → shite',
]


def _read(name):
    # newline='' keeps bytes exactly as stored (incl. the leading newline).
    with open(os.path.join(SRC, name), encoding='utf-8', newline='') as f:
        return f.read()


def _read_json(name):
    with open(os.path.join(SRC, name), encoding='utf-8') as f:
        return json.load(f)


CSS = _read('app.css')
JS = _read('app.js')

# ------------------------------------------------------------------ vocab IDs
def vocab_id(row):
    """Stable ID of a vocab row: the word itself, not its position."""
    return 'v:' + row[0] + '|' + row[1]


_KANA = re.compile(r'^[\u3040-\u30ff〜～、 ]+$')   # hiragana, katakana (incl. ー), tilde, comma


def speak_text(jp):
    """Text handed to speechSynthesis for a vocab cell (see tests/test_content.py)."""
    s = jp
    if ' / ' in s:
        parts = [p.strip() for p in s.split(' / ')]
        kana = [p for p in parts if _KANA.match(p)]
        s = '、'.join(kana) if kana else parts[0]
    s = re.sub(r'\[[^\]]*\]', '', s)          # [noun], [name] placeholders
    s = s.replace('(な)', '')
    s = s.replace('〜', '').replace('～', '')
    s = s.replace('…', '、')
    return s.strip()


def all_vocab_rows():
    for w in WEEKS:
        for sec in w['sections']:
            if sec['type'] == 'vocab':
                yield from sec['rows']
    for a in APPENDICES:
        for sec in a['sections']:
            if sec['type'] == 'vocab':
                yield from sec['rows']


def _annotate(sections):
    for sec in sections:
        if sec['type'] == 'vocab':
            sec['ids'] = [vocab_id(r) for r in sec['rows']]
            # optional 4th element overrides the derived speak text
            sec['speak'] = [r[3] if len(r) > 3 else speak_text(r[0]) for r in sec['rows']]
            sec['rows'] = [list(r[:3]) for r in sec['rows']]


def _chart_romaji():
    """glyph -> romaji, taken from every kana chart (the single source)."""
    out = {}
    for sec in [s for w in WEEKS for s in w['sections']] + [s for a in APPENDICES for s in a['sections']]:
        if sec['type'] == 'kana':
            for row in sec['rows']:
                for cell in row:
                    if cell:
                        out.setdefault(cell[0], cell[1])
    return out


_SVG_OPEN = ('<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100" fill="none" '
             'stroke="currentColor" stroke-width="5" stroke-linecap="round" '
             'stroke-linejoin="round" aria-hidden="true">')


def make_glyphs():
    """Records for the detail sheet, keyed by character (see content_glyphs.py)."""
    romaji = _chart_romaji()
    g = {}
    for script, rows in (('hiragana', content_glyphs.HIRAGANA), ('katakana', content_glyphs.KATAKANA)):
        for ch, origin, hook, example in rows:
            g[ch] = {'romaji': romaji[ch], 'script': script, 'hook': hook,
                     'looksLike': [], 'voiced': []}
            if origin:
                g[ch]['origin'] = origin
            if example:
                g[ch]['example'] = list(example)
    for ch, meaning, info in KANJI:
        hook, origin, parts = content_glyphs.KANJI_HOOKS[ch]
        g[ch] = {'script': 'kanji', 'meaning': meaning, 'readings': info, 'hook': hook,
                 'looksLike': [], 'voiced': []}
        if origin:
            g[ch]['origin'] = origin
        if parts:
            g[ch]['parts'] = [list(p) for p in parts]
        if ch in content_glyphs.KANJI_SVG:
            g[ch]['svg'] = (_SVG_OPEN + content_glyphs.KANJI_SVG[ch] + '</svg>')
    for base, voiced, mark in content_glyphs.VOICED:
        g[voiced] = {'romaji': romaji[voiced], 'base': base, 'mark': mark,
                     'looksLike': [], 'voiced': []}
        g[base]['voiced'].append(voiced)
    for group in content_glyphs.LOOKALIKE_GROUPS:
        for ch in group:
            if ch in g:
                for other in group:
                    if other != ch and other not in g[ch]['looksLike']:
                        g[ch]['looksLike'].append(other)
    return g


def make_meaning_pool():
    """Distinct English glosses from every vocab row (weeks + appendices), for
    the recognise card's wrong-answer choices. A big pool keeps decoys varied."""
    seen, pool = set(), []
    for sec in [s for w in WEEKS for s in w['sections']] + [s for a in APPENDICES for s in a['sections']]:
        if sec.get('type') == 'vocab':
            for row in sec['rows']:
                g = row[2]
                if g not in seen:
                    seen.add(g); pool.append(g)
    return pool


def make_practice_sets():
    sets = []
    for st in content_practice.PRACTICE_SETS:
        items = []
        for entry in st['items']:
            answer, prompt = entry[0], entry[1]
            image = entry[2] if len(entry) > 2 else ''
            items.append({'id': 'p:' + st['id'] + ':' + answer, 'answer': answer, 'prompt': prompt, 'image': image})
        sets.append({'id': st['id'], 'title': st['title'], 'blurb': st.get('blurb', ''), 'items': items})
    return sets


def make_course():
    weeks = copy.deepcopy(WEEKS)
    appendices = copy.deepcopy(APPENDICES)
    for w in weeks:
        _annotate(w['sections'])
    for a in appendices:
        _annotate(a['sections'])
    return {
        'title': 'Beginner Japanese',
        'titleJp': 'はじめての にほんご',
        'subtitle': 'A 12-Week Course',
        'front': FRONT_MATTER,
        'resources': RESOURCES,
        'weeks': weeks,
        'appendices': appendices,
        # Old positional star keys -> stable IDs; frozen, see tools/make_legacy_keys.py
        'legacyKeys': _read_json('legacy_keys.json'),
        # Old stable ID -> current ID, for when a word is corrected later.
        'idAliases': _read_json('id_aliases.json'),
        # Detail-sheet data per character (hooks, origins, look-alikes, voicing).
        'glyphs': make_glyphs(),
        # Tap-to-build practice sets (Round C).
        'practiceSets': make_practice_sets(),
        # Wrong-answer pool for the recognise card.
        'meaningPool': make_meaning_pool(),
    }


HTML_TEMPLATE = """<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1, viewport-fit=cover">
<meta name="apple-mobile-web-app-capable" content="yes">
<meta name="apple-mobile-web-app-status-bar-style" content="default">
<meta name="apple-mobile-web-app-title" content="Japanese">
<meta name="theme-color" content="#8B2635">
<title>Beginner Japanese — A 12-Week Course</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Noto+Sans+JP:wght@400;500;700&display=swap" rel="stylesheet">
<style>__CSS__</style>
</head>
<body>
<div class="app">
    <div class="scrim"></div>
    <nav class="sidebar"><div id="nav-inner"></div></nav>
    <div>
        <div class="mobile-header">
            <button id="menu-btn" class="menu-btn" aria-label="Menu"><svg viewBox="0 0 24 24" fill="none" stroke-width="2" stroke-linecap="round"><path d="M3 6h18M3 12h18M3 18h18"/></svg></button>
            <div class="ttl" id="mobile-title">Beginner Japanese</div>
        </div>
        <main id="content" class="content"></main>
    </div>
</div>
<script>
const COURSE = __COURSE_JSON__;
__JS__
</script>
</body>
</html>
"""


def render_html():
    course_json = json.dumps(make_course(), ensure_ascii=False)
    # Content holds HTML like </b>; inside <script> a literal "</" could end the
    # script early (e.g. "</script>" in an SVG string). "<\/" is the same JSON.
    course_json = course_json.replace('</', '<\\/')
    parts = {'CSS': CSS, 'COURSE_JSON': course_json, 'JS': JS}
    # One pass over the template only, so a placeholder name appearing inside
    # app.css / app.js / content can never be substituted.
    return re.sub(r'__(CSS|COURSE_JSON|JS)__', lambda m: parts[m.group(1)], HTML_TEMPLATE)


def build(out):
    os.makedirs(os.path.dirname(os.path.abspath(out)), exist_ok=True)
    with open(out, 'w', encoding='utf-8') as f:
        f.write(render_html())
    print(f'OK: {out}  ({os.path.getsize(out)/1024:.1f} KB)')


if __name__ == '__main__':
    # Default: index.html at the repo root (one level up from src/).
    build(sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, 'index.html'))
