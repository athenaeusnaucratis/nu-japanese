# Beginner Japanese — A 12-Week Course

A self-contained, offline-capable web course for absolute beginners in Japanese.
Live at https://nu-japanese-course-athenaeusnaucratis-projects.vercel.app

## ⚠️ `index.html` is generated — do not edit it

`index.html` is **build output**. Hand-editing it works until the next build,
then your changes are silently overwritten. Edit the source and rebuild:

```bash
python3 src/build.py      # regenerates ./index.html
npm test                  # content tests (Python) + UI tests (jsdom)
```

**No runtime dependencies** — the shipped `index.html` loads nothing but a web
font. Building needs only the Python 3 standard library. Tests need Node and a
one-time `npm install` (jsdom, dev-only). Run `npm test` before every push.

## Layout

| Path                   | What it is                                                |
| ---------------------- | --------------------------------------------------------- |
| `index.html`           | **Generated.** Single-file app — HTML + CSS + JS + content. |
| `src/build.py`         | Build script: loads content, adds stable IDs, inlines assets. |
| `src/app.js`, `src/app.css` | The app's JavaScript and styles (inlined at build).    |
| `src/content_front.py` | Welcome section + the external resources list.              |
| `src/content_weeks.py` | Weeks 1–12. The bulk of the course.                         |
| `src/content_kanji.py` | The 100 kanji — single source for weeks 11–12 and appendix. |
| `src/content_appx.py`  | Kana charts, kanji appendix, grammar sheet, vocab index.    |
| `src/legacy_keys.json` | **Frozen.** Old positional star keys → stable IDs.          |
| `src/id_aliases.json`  | Old vocab ID → new ID, when a word is corrected later.      |
| `tests/`               | `test_*.py` (content) and `*.test.js` (UI, jsdom).          |
| `tools/`               | One-off generators (`make_legacy_keys.py` — never rerun).   |

Content is plain Python data structures, kept separate from rendering. To change
a lesson you edit a list in a `content_*.py` file; you don't touch markup.

## Deploying

Vercel is linked to this repo and auto-deploys on push to `main`.

```bash
python3 src/build.py
git add -A && git commit -m "..." && git push
```

Confirm the deploy actually carries your bytes:

```bash
sha1sum index.html
curl -s https://nu-japanese-course-athenaeusnaucratis-projects.vercel.app | sha1sum
```

The two hashes must match. (A past inline deploy silently shipped a truncated
file, so this check is worth keeping.)

## Content block types

Each week is `{num, title, goals[], sections[]}`. Each section is a dict with a
`type`, rendered by the matching branch in `build.py`:

`p` · `h2` · `h3` · `ul` · `vocab` · `kana` · `kanji-grid` · `grammar` ·
`exercise` · `resource` · `reading` · `table` · `selfcheck`

`vocab` rows are `(japanese, reading, english[, speak])` and render with a
speaker button and a star toggle. The optional 4th element overrides the spoken
text; otherwise `speak_text()` in `build.py` derives it (kana side of
`日本人 / にほんじん`, placeholders dropped). Any new cell containing `/ [ ] ( ) 〜 …`
must be added to the fixture in `tests/test_content.py`. `kana` is `rows[][]`
of `[char, romaji]`.

**Stable IDs.** A vocab row's ID is `v:` + japanese + `|` + reading. Stars are
stored by ID, so reordering or inserting rows is safe — but **editing the
japanese or reading cell of an existing row changes its ID**; add the old → new
pair to `src/id_aliases.json` so learners keep their star.

## How it works

- **No backend, no build toolchain, no dependencies.** One HTML file.
- **Progress** is stored in `localStorage` under `jp_course_v1` — week status,
  known-vocab stars (`known`, by stable ID), hide toggles, theme, `schema: 2`.
  Per-device; nothing is uploaded, no sign-in. Blobs without `schema` (saved
  before Oct 2026) are migrated once on load: the raw blob is copied to
  `jp_course_v1_bak`, stars are mapped via `legacy_keys.json`, and the old
  `knownVocab` field is left in place so a rollback still works. If stored data
  can't be parsed, the app shows a notice and saves nothing that visit.
- **Audio** uses the browser `SpeechSynthesis` API with a `ja-JP` voice at
  `rate 0.85`. Voice quality is the device's, not ours: desktop Chrome has the
  neural Google 日本語 voice; iOS ships a compact Apple voice that sounds
  robotic until the user downloads an Enhanced/Premium Japanese voice under
  Settings → Accessibility → Spoken Content → Voices.
- **Routing** is hash-based (`#/week-1`), so it works from any static host.
- **Responsive** at 820px: the sidebar becomes a slide-in drawer with a scrim.
  The scrim must stay `display: none` outside that breakpoint or it consumes a
  CSS grid column and breaks the desktop layout.

## Known gaps

- No cross-device sync. Progress lives in one browser's `localStorage`.
- Not a PWA — no service worker, no offline install beyond Add to Home Screen.
- Audio depends entirely on the device's installed voices.
