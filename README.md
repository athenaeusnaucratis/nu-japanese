# Beginner Japanese — A 12-Week Course

A self-contained, offline-capable web course for absolute beginners in Japanese.
Live at https://nu-japanese-course-athenaeusnaucratis-projects.vercel.app

## ⚠️ `index.html` is generated — do not edit it

`index.html` is **build output**. Hand-editing it works until the next build,
then your changes are silently overwritten. Edit the source and rebuild:

```bash
python3 src/build.py      # regenerates ./index.html
```

No dependencies beyond the Python 3 standard library.

## Layout

| Path                   | What it is                                                |
| ---------------------- | --------------------------------------------------------- |
| `index.html`           | **Generated.** Single-file app — HTML + CSS + JS + content. |
| `src/build.py`         | Build script. Holds all CSS and JS, assembles the output.   |
| `src/content_front.py` | Welcome section + the external resources list.              |
| `src/content_weeks.py` | Weeks 1–12. The bulk of the course.                         |
| `src/content_appx.py`  | Kana charts, 100 N5 kanji, grammar sheet, vocab index.      |

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

`vocab` rows are `[japanese, reading, english]` and render with a speaker button
and a star toggle. `kana` is `rows[][]` of `[char, romaji]`.

## How it works

- **No backend, no build toolchain, no dependencies.** One HTML file.
- **Progress** is stored in `localStorage` under `jp_course_v1` — week status,
  known-vocab stars, hide-English/hide-reading toggles, theme. Per-device;
  nothing is uploaded, no sign-in.
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
