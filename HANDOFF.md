# Handoff — nu-japanese

**Written:** 2026-10-04, end of a Claude Code session in WSL (`/home/alpha/projects/nu-japanese`).

## Why this file exists

Work continues in a **fresh Claude Code session**. The project stays in WSL at
`/home/alpha/projects/nu-japanese` and the next session should run **inside
WSL** too (desktop app → open the WSL folder), not as a Windows session pointed at
`\\wsl.localhost\...` — that would run Windows Python/Git/npm against the
files and bring back CRLF output, slow Git over the network path, and npm's
dislike of network-path working directories.

What this session could and couldn't use (measured):
- **GitHub** — works (`gh`, account `athenaeusnaucratis`).
- **Vercel** — the claude.ai Vercel connector works (`list_deployments` etc.);
  only the separate Vercel *plugin* asked for `/mcp` login. Use the connector to
  get preview URLs — previews are public (HTTP 200) and serve the build plus
  one Vercel toolbar `<script>` (163 bytes); strip it before comparing hashes.
- **Chrome DevTools MCP** — works since the user installed Chrome 154 in WSL.
  Use an `isolatedContext`, and `emulate` with `375x812x3,mobile,touch` for
  phone width (a window can't be narrower than ~500 px). A hash-only change to
  the same URL does **not** reload the page — use `navigate_page type=reload`.
  Chrome in WSL has no Japanese voice: it can check what text is spoken, not
  how it sounds.

A new session starts with no memory of this one, and the session memory folder
is tied to the old path. **This file is the memory.** It records what was done,
what is in flight, what was decided and why, so nothing has to be re-derived or
re-litigated.

---

## 1. Project snapshot

| | |
|---|---|
| What | 12-week beginner Japanese course (JLPT N5 target), one self-contained `index.html` |
| Live | https://nu-japanese-course-athenaeusnaucratis-projects.vercel.app |
| Repo | https://github.com/athenaeusnaucratis/nu-japanese (GitHub account `athenaeusnaucratis`) |
| Deploy | Vercel project `nu-japanese-course`, team `athenaeusnaucratis-projects`; **push to `main` deploys to live**; every other branch gets a preview |
| Build | `python3 src/build.py` → `index.html` (stdlib only) |
| Tests | `npm install` once, then `npm test` (Python content tests + jsdom UI tests) |
| Live SHA1 | `06006ef6e81175e1b949fa1a6406c0c938ba8303` (commit `35f3e69`) |
| Audience | Adult learners. Calm, private, non-competitive. **Not** a language game. |

Read `README.md` for layout, content block types, stable IDs and storage.

## 2. Working rules for this project

The user's global rules (from `~/.claude/CLAUDE.md` — **copy it, plus
`settings.json` and `hooks/`, to `C:\Users\<you>\.claude\`; see §7 step 4**) apply. The ones that mattered most here:

- Every report opens with `READ / NOT READ / INFERRING`, and groups findings under
  **Confident wrong / Need your judgment / Confident right**, marking results
  *measured* or *produced*.
- Never say "verified" unless the check was written before the code or by
  something that didn't write it. Otherwise: "passes my own checks".
- Fixture before rule: ≥20 hand-checked cases (must pass / must fail / unsure)
  before writing any matcher or rule.
- Bug class, not instance: grep for siblings and count them before fixing.
- Two failed attempts at the same defect → stop and report.
- Shortcuts are labelled as shortcuts, with the better option and its cost.
- A hook blocks `tail`/`head` on test output — write output to a file, read it whole.

Project practice that worked:
- One branch per change; `main` is touched only after the user says so.
- Tests are written first and must fail on the old code for the right reason.
- After every merge: `npm test` green → push → **live SHA1 == local SHA1**.
- Saved progress is user data: never overwrite it; keep rollback possible.

## 3. Previous — what was done (with commits)

| Commit | What |
|---|---|
| `007f42b`, `55e2e5d` | Earlier agent: site uploaded; mobile scrim fix. |
| `2c4f1af` | Earlier agent: build source moved into the repo (`src/`), README, `.gitignore`. |
| `35f3e69` | **Live now.** 13 strings showed raw entities (`What&rsquo;s your name?`) → every content string now renders as HTML. 7 content errors fixed (godan ぐ; 14th/24th よっか; はん not はんぶん for clock time; sound changes before h- and s-; kanji examples for 九 日 下 入; "500 words" → "few hundred"). Self-checks added to weeks 3, 5–12. |
| `d3d67b8` | CSS and JS moved from Python strings into `src/app.css` / `src/app.js`. Output byte-identical. |
| `a19acf2` | **Round A** (see §4). |

Also established:
- The local WSL folder had been a flattened, non-git copy; it was replaced by a
  real clone. The earlier agent's note that `~/projects/nu-japanese` tracked
  `origin/main` was not true for this machine (`git rev-parse` exit 128).
- **Bug found in the live site:** if stored progress can't be parsed, the first
  week visit overwrites it with defaults (reproduced in a test). Fixed in Round A,
  not yet live.

## 4. Current — in flight

**Branch `round-a-foundations` @ `a19acf2`**, pushed. Vercel preview:
*Deployment has completed*
(https://vercel.com/athenaeusnaucratis-projects/nu-japanese-course/8StgU6XsX4ryvkJM5KrSREBQVgrD).
**Not merged.** Expected live SHA1 after merge (when built on Linux/LF):
`bced61981420f347ceb93e0ce5e25cee721ca880`.

What Round A does:
- **Stable vocab IDs** `v:<japanese>|<reading>`; stars stored in `known` by ID.
- **One-time migration** for every existing user (blobs without `schema`):
  raw blob → `jp_course_v1_bak`; positional keys mapped via the **frozen**
  `src/legacy_keys.json` (538 keys → 436 IDs; layout identical in all 4
  published builds; never regenerate); true-anywhere wins, `false` dropped,
  unknown keys kept in `legacyUnmapped`; old `knownVocab` left in place for rollback.
- Unreadable storage → notice shown, saving disabled for the visit.
- Unstar deletes the ID; duplicate rows of a word stay in sync.
- Dashboard total = unique starrable words: **273 → 431** (visible change).
- `src/content_kanji.py` = single kanji source (appendix had 15 drifted glosses).
- Week 9 te-form rules are a `table`, not vocab.
- Audio speaks derived text (kana side of `日本人 / にほんじん`, placeholders dropped).
- `npm test`: 12 content + 11 UI tests, all passing; fixtures written first.
- Approved design: `docs/superpowers/specs/2026-10-04-visual-hooks-design.md`.

**Real-browser check done (Chrome, isolated profile, 2026-10-04):** old-format
blob migrated (ねこ true+false → known, はん carried, unknown key set aside,
backup written, `knownVocab` kept), dashboard 2 / 431, speech text にほんじん and
にん, Week 9 table, duplicate さかな rows in sync, unstar deletes, corrupted
storage untouched after real reload + two week visits, notice shown; no console
errors. **Merged to `main` on the user's go (2026-10-04).**

### Round B1, batch 1 — done (branch `round-b1-hiragana`)
Detail sheet + 46 hiragana hooks (`src/content_glyphs.py`, built into
`COURSE.glyphs` by `make_glyphs()` in `build.py`). Tap a kana: plays the sound
and opens a non-modal sheet (bottom sheet ≤820px, 340px side panel above) with
glyph, romaji, memory hook, origin kanji, voiced forms, look-alikes, example.
Voiced kana link back to their base ("か + ゛"). Katakana cells still play
sound but open no sheet until batch 2. Tests: `tests/test_glyphs.py`,
`tests/sheet.test.js` (written first). Checked in Chrome at 375 (light) and
1024 (dark). Review list for the user: `docs/reviews/b1-hiragana-hooks.md`.
**Reviewed and approved by the user; merged to `main` (2026-10-04).**

### Round B1, batch 2 — done (branch `round-b1-katakana`)
46 katakana hooks + 25 voiced katakana in `content_glyphs.py`; every kana in
every grid (142) now opens the sheet. Records carry `script`; katakana origins
read "Taken from part of the kanji X" (hiragana: "Simplified from"). ン shows
no origin (disputed), ヲ no example. Tests extended first. Review list:
`docs/reviews/b1-katakana-hooks.md`. **Reviewed and approved; merged to `main` (2026-10-04).**

### Round B1, batch 3 — in flight (branch `round-b1-kanji`)
All 100 kanji open the sheet (kanji cards are buttons now): meaning, readings,
memory hook, and — only for the pinned set — an origin line. 20 pictographs
get a simple line drawing (picture → character); their hooks explain how the
drawing became the character. Compound kanji list "Built from" parts, each
checked against KRADFILE (`tests/fixtures/kradfile_subset.txt`, EDRDG
CC BY-SA 4.0, credited on the Resources page). 英's 央 part was dropped
because KRADFILE lists 英 without 央's 一 (user may want to override).
Review list: `docs/reviews/b1-kanji-hooks.md`. **Waiting on:** user review, then merge.

## 5. Next — decided, in order

**Task 1 (cheap insurance, only urgent if Windows tools ever write files here)
— make the build line-ending-proof:**
- add `.gitattributes`: `* text=auto eol=lf`
- `src/build.py` `build()`: `open(out, 'w', encoding='utf-8', newline='\n')`
- `package.json` / `tests/helpers.js` call `python3`; on Windows it may be
  `python` or `py` — make it configurable or detect it.
- Gate: rebuild → SHA1 must still be `bced6198…`.

**Then:** real-browser check of Round A (preview:
https://nu-japanese-course-gjgb7sve3-athenaeusnaucratis-projects.vercel.app,
bytes confirmed = `bced6198…` + Vercel toolbar) (Chrome DevTools MCP at 375 / 820 / 821 /
1024 px) → merge → live SHA1 check.

**Round B1 — visual hooks** (user's top priority; full spec in the design doc):
1. Detail sheet + **hiragana** hooks (46) → preview → user review → merge.
2. **Katakana** hooks (46) → same.
3. **Kanji**: hooks for 100, simple SVG drawings for ~20 picture-origin kanji,
   component parts where meaningful (check against KRADFILE, EDRDG,
   CC BY-SA 4.0 → attribution in Resources).

Decisions behind B1 (user's choices):
- Hooks are **original** (no copying Tofugu or other copyrighted sets); a kanji
  story is labelled "memory hook" unless its origin is well established.
- Tap = play sound + open a **non-modal** detail sheet (bottom sheet on phone,
  side panel on desktop); next tap updates it; respects "Hide readings".
- 142 kana in the grids: the 92 base kana get hooks; the 50 voiced forms link to their base.
- Look-alike groups (シツ, ソン, クケタ, ぬめ, れわね, …) defined once, symmetric.

**Later rounds (order agreed, not yet designed):**
- **C — Active practice:** quick checks inside lessons, model answers you can
  reveal for the 61 exercises, recognition-first replacements for the
  copying drills.
- **D — Gentle daily review:** capped spaced-repetition queue; no streaks; no backlog pile-up.
- **E — Calm UI:** ~20-minute sessions, resume point, romaji fading by week, study tips.
- Deferred from B: particle colour code (needs hand markup of ~89 sentences;
  automatic detection rejected because は sits inside はじめまして and に inside にほん),
  plus word-type badges.

**Non-goals:** streaks, points, leaderboards, timers, lives, notifications,
handwriting/stroke-order features.

## 6. Open items (logged once)

- Two handwriting self-check items in weeks 11–12 (written in `35f3e69`) should be
  revised in Round C, in line with the decision to make handwriting optional.
- About 25 KB of the page (raw) is `legacyKeys`; drop it in a later release
  once returning users have migrated.
- Vocab index: up to 99 of 265 rows don't appear in the weeks (crude match,
  likely an overcount); decide whether that's intended.
- Unverified external resource claims (Netflix availability of Terrace House,
  Italki pricing, etc.).
- iOS Enhanced Japanese voice test (earlier agent's item): needs a device.
- **Dark-mode contrast of accent-coloured text (on the live site already):** `--accent` (#8B2635) as
  text on dark backgrounds is 1.9–2.1:1. B1 added `--accent-text` (#e07a8f in
  dark, 5.76:1) and uses it for the sheet glyph only. Six older uses still on
  `--accent`, for Round E: `nav .brand .title-jp`, `h1`, `.week-marker`,
  `.kanji-card .k`, `.hero .hero-jp`, `.stat .n`.
- **Mobile horizontal overflow (on the live site, not caused by Round A)**, measured at
  375 px: week-1 399, week-4 383, week-9 394, week-10 392, vocab index 426 px
  wide. Cause 1: `.app` grid column is `1fr` (min-content) → fix with
  `grid-template-columns: minmax(0, 1fr)` in the ≤820px block (tested in-page:
  fixes week-4/10, others drop to 376–410). Cause 2: 4-column vocab table with
  two nowrap buttons is wider than a phone → needs a small design choice
  (horizontally scrolling table vs stacked action buttons).
  **User decision: fix it in Round E (calm UI), not now — foundations first.**

## 7. Only if the project ever moves to Windows — checklist

1. **Clone, don't copy:** `gh repo clone athenaeusnaucratis/nu-japanese`, then
   `git checkout round-a-foundations`. (Copying would bring Linux
   `node_modules` and risk CRLF conversion.)
2. Check `git config core.autocrlf` — `false` or `input` is safest, and
   `.gitattributes` (task 1) makes it moot.
3. Install Python 3 and Node; run `npm install`.
4. Copy your global Claude config to the Windows `~/.claude/`:
   `CLAUDE.md`, `settings.json`, and the folder `hooks/` (three scripts:
   `no-secret-writes.py`, `no-truncated-verification.py`, `fixture-gate.py`).
   **`settings.json` points to them by absolute WSL path
   (`/home/alpha/.claude/hooks/...`) with `[ -f "$f" ] || exit 0`, so on
   Windows they silently do nothing** until the paths are changed to the
   Windows location (and `python3` to whatever runs Python there). Test one:
   a `... | tail` on test output should be blocked.
5. In the desktop app, authorise the Vercel connector and make sure Chrome is
   installed for the DevTools MCP.

## 8. Prompt to start the new session

> Read `HANDOFF.md`, `README.md` and
> `docs/superpowers/specs/2026-10-04-visual-hooks-design.md`. We're on branch
> `round-a-foundations`. Next step: real-browser check of the Round A preview
> (HANDOFF §5), then merge on my go.
