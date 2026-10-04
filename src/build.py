"""
Build the interactive single-file HTML version of the Japanese course.

Usage:
    python3 src/build.py              # writes ./index.html at the repo root
    python3 src/build.py path/to.html # writes somewhere else

index.html is GENERATED. Never hand-edit it — edit app.css / app.js, the
content_*.py modules or this file, and rebuild, or your changes get overwritten.
"""
import json
import os
import re
import sys

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
from content_front import FRONT_MATTER, RESOURCES
from content_weeks import WEEKS
from content_appx import APPENDICES

# Default: index.html at the repo root (one level up from src/).
REPO_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = sys.argv[1] if len(sys.argv) > 1 else os.path.join(REPO_ROOT, 'index.html')
_outdir = os.path.dirname(os.path.abspath(OUT))
if _outdir:
    os.makedirs(_outdir, exist_ok=True)

COURSE = {
    'title': 'Beginner Japanese',
    'titleJp': 'はじめての にほんご',
    'subtitle': 'A 12-Week Course',
    'front': FRONT_MATTER,
    'resources': RESOURCES,
    'weeks': WEEKS,
    'appendices': APPENDICES,
}

SRC = os.path.dirname(os.path.abspath(__file__))


def _read(name):
    # newline='' keeps bytes exactly as stored (incl. the leading newline).
    with open(os.path.join(SRC, name), encoding='utf-8', newline='') as f:
        return f.read()


CSS = _read('app.css')
JS = _read('app.js')

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


def build():
    parts = {
        'CSS': CSS,
        'COURSE_JSON': json.dumps(COURSE, ensure_ascii=False),
        'JS': JS,
    }
    # One pass over the template only, so a placeholder name appearing inside
    # app.css / app.js / content can never be substituted.
    html = re.sub(r'__(CSS|COURSE_JSON|JS)__', lambda m: parts[m.group(1)], HTML_TEMPLATE)
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    size = os.path.getsize(OUT)
    print(f'OK: {OUT}  ({size/1024:.1f} KB)')


if __name__ == '__main__':
    build()
