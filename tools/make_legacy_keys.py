"""Generate src/legacy_keys.json ONCE: old positional star keys -> stable vocab IDs.

Before schema 2, a "known" star was stored under its position, e.g. 'w1-s4-v0'
(week 1, section 4, row 0) or 'appx-vocab-index-s1-v3'. This table lets the app
move those stars to stable IDs. It describes the layout users actually saved
against, so it is taken from the published builds and must never be regenerated
from current content. Refuses to overwrite an existing file.

    python3 tools/make_legacy_keys.py
"""
import json, os, re, subprocess, sys

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
OUT = os.path.join(ROOT, 'src', 'legacy_keys.json')
# Every commit whose index.html was live before stable IDs shipped.
PUBLISHED = ['007f42b', '55e2e5d', '2c4f1af', '35f3e69']


def vocab_id(jp, reading):
    return 'v:' + jp + '|' + reading


def course_at(rev):
    html = subprocess.check_output(['git', '-C', ROOT, 'show', f'{rev}:index.html']).decode('utf-8')
    m = re.search(r'const COURSE = (\{.*?\});\n', html, re.S)
    return json.loads(m.group(1))


def positional(course):
    keys = {}
    for w in course['weeks']:
        for i, s in enumerate(w['sections']):
            if s['type'] == 'vocab':
                for j, r in enumerate(s['rows']):
                    keys[f"w{w['num']}-s{i}-v{j}"] = (r[0], r[1])
    for a in course['appendices']:
        for i, s in enumerate(a['sections']):
            if s['type'] == 'vocab':
                for j, r in enumerate(s['rows']):
                    keys[f"appx-{a['id']}-s{i}-v{j}"] = (r[0], r[1])
    return keys


if __name__ == '__main__':
    if os.path.exists(OUT):
        sys.exit(f'refusing to overwrite {OUT}')
    layouts = {rev: positional(course_at(rev)) for rev in PUBLISHED}
    base = layouts[PUBLISHED[-1]]
    for rev, lay in layouts.items():
        assert lay.keys() == base.keys(), f'{rev}: key set differs'
        diff = {k: (lay[k], base[k]) for k in lay if lay[k] != base[k]}
        print(f'{rev}: {len(lay)} keys, rows differing from {PUBLISHED[-1]}: {diff}')
    # A differing row is only acceptable if it is the same word re-labelled.
    table = {k: vocab_id(*v) for k, v in sorted(base.items())}
    with open(OUT, 'w', encoding='utf-8') as f:
        json.dump(table, f, ensure_ascii=False, indent=0, sort_keys=True)
        f.write('\n')
    print(f'wrote {OUT}: {len(table)} keys -> {len(set(table.values()))} distinct IDs')
