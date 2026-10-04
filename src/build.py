"""
Build the interactive single-file HTML version of the Japanese course.

Usage:
    python3 src/build.py              # writes ./index.html at the repo root
    python3 src/build.py path/to.html # writes somewhere else

index.html is GENERATED. Never hand-edit it — edit this file or the
content_*.py modules and rebuild, or your changes get overwritten.
"""
import json
import os
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

CSS = r"""
:root {
    --accent: #8B2635;
    --accent-dim: #a1455a;
    --ink: #1a1a1a;
    --muted: #5b5b5b;
    --very-muted: #8c8c8c;
    --bg: #fafaf7;
    --bg-raised: #ffffff;
    --rule: #e3e0da;
    --grammar-bg: #fff8f0;
    --grammar-border: #d9a86c;
    --grammar-head: #8B2635;
    --exercise-bg: #f1f6fa;
    --exercise-border: #8aa6c2;
    --exercise-head: #2c3e50;
    --resource-bg: #f1faf2;
    --resource-border: #8ac295;
    --resource-head: #2a6b3a;
    --table-head-bg: #8B2635;
    --table-row-alt: #f6f0f0;
    --nav-bg: #f3efe8;
    --nav-active: #ffffff;
    --focus-ring: rgba(139, 38, 53, 0.35);
    box-sizing: border-box;
    padding-top: env(safe-area-inset-top, 0px);
    padding-bottom: env(safe-area-inset-bottom, 0px);
}
@media (prefers-color-scheme: dark) {
    :root:not([data-theme="light"]) {
        --ink: #ecebe6;
        --muted: #b4b1a9;
        --very-muted: #8c8a84;
        --bg: #15161a;
        --bg-raised: #1e1f24;
        --rule: #35363c;
        --nav-bg: #1a1b1f;
        --nav-active: #262830;
        --grammar-bg: #2a2520;
        --grammar-border: #a5783d;
        --grammar-head: #e07a8f;
        --exercise-bg: #1e2730;
        --exercise-border: #4a6a85;
        --exercise-head: #8caacc;
        --resource-bg: #1d2c22;
        --resource-border: #4d7a5a;
        --resource-head: #86c296;
        --table-head-bg: #6b1d29;
        --table-row-alt: #26202a;
    }
}
:root[data-theme="dark"] {
    --ink: #ecebe6;
    --muted: #b4b1a9;
    --very-muted: #8c8a84;
    --bg: #15161a;
    --bg-raised: #1e1f24;
    --rule: #35363c;
    --nav-bg: #1a1b1f;
    --nav-active: #262830;
    --grammar-bg: #2a2520;
    --grammar-border: #a5783d;
    --grammar-head: #e07a8f;
    --exercise-bg: #1e2730;
    --exercise-border: #4a6a85;
    --exercise-head: #8caacc;
    --resource-bg: #1d2c22;
    --resource-border: #4d7a5a;
    --resource-head: #86c296;
    --table-head-bg: #6b1d29;
    --table-row-alt: #26202a;
}
* { box-sizing: border-box; }
html, body { margin: 0; padding: 0; }
html { scroll-padding-top: env(safe-area-inset-top, 0px); }
body {
    font-family: -apple-system, BlinkMacSystemFont, "Segoe UI", Roboto,
                 "Noto Sans", "Noto Sans JP", "Helvetica Neue", Helvetica, Arial, sans-serif;
    font-size: 16px;
    line-height: 1.55;
    color: var(--ink);
    background: var(--bg);
    -webkit-font-smoothing: antialiased;
    -moz-osx-font-smoothing: grayscale;
}
.jp, .jp * {
    font-family: "Noto Sans JP", -apple-system, "Hiragino Kaku Gothic Pro",
                 "Yu Gothic", Meiryo, sans-serif;
    font-feature-settings: "palt";
}

/* ---------- Layout ---------- */
.app {
    display: grid;
    grid-template-columns: 260px 1fr;
    min-height: 100vh;
}
nav.sidebar {
    background: var(--nav-bg);
    border-right: 1px solid var(--rule);
    padding: 20px 0 40px;
    position: sticky;
    top: 0;
    max-height: 100vh;
    overflow-y: auto;
}
nav .brand {
    padding: 0 20px 16px;
    border-bottom: 1px solid var(--rule);
    margin-bottom: 10px;
}
nav .brand .title {
    font-size: 15px;
    font-weight: 700;
    color: var(--ink);
    margin: 0;
    letter-spacing: -0.01em;
}
nav .brand .title-jp {
    font-size: 14px;
    color: var(--accent);
    margin: 2px 0 0;
}
nav .brand .sub {
    font-size: 11px;
    color: var(--muted);
    margin: 4px 0 0;
    text-transform: uppercase;
    letter-spacing: 0.06em;
}
nav .section-label {
    font-size: 10px;
    font-weight: 700;
    text-transform: uppercase;
    letter-spacing: 0.08em;
    color: var(--very-muted);
    padding: 14px 20px 4px;
}
nav a.item {
    display: flex;
    align-items: center;
    gap: 10px;
    padding: 7px 20px;
    color: var(--ink);
    text-decoration: none;
    font-size: 14px;
    border-left: 3px solid transparent;
    cursor: pointer;
    user-select: none;
}
nav a.item:hover { background: rgba(0,0,0,0.04); }
nav a.item.active {
    background: var(--nav-active);
    border-left-color: var(--accent);
    font-weight: 500;
}
nav a.item .num {
    font-size: 11px;
    color: var(--very-muted);
    min-width: 18px;
    font-variant-numeric: tabular-nums;
}
nav a.item .label { flex: 1; }
nav a.item .status {
    width: 14px;
    height: 14px;
    border-radius: 50%;
    border: 1.5px solid var(--very-muted);
    flex-shrink: 0;
}
nav a.item .status.started {
    border-color: var(--accent);
    background: linear-gradient(to right, var(--accent) 50%, transparent 50%);
}
nav a.item .status.complete {
    background: var(--accent);
    border-color: var(--accent);
    position: relative;
}
nav a.item .status.complete::after {
    content: "";
    position: absolute;
    left: 3px; top: 1px;
    width: 4px; height: 7px;
    border: solid white;
    border-width: 0 1.5px 1.5px 0;
    transform: rotate(45deg);
}

main.content {
    padding: 32px 48px 80px;
    max-width: 820px;
    margin: 0 auto;
    width: 100%;
}

/* Mobile */
.menu-btn, .mobile-header { display: none; }
.scrim { display: none; }
@media (max-width: 820px) {
    .app { grid-template-columns: 1fr; }
    nav.sidebar {
        position: fixed;
        top: 0; left: 0;
        width: 85%;
        max-width: 320px;
        height: 100vh;
        max-height: 100vh;
        z-index: 20;
        transform: translateX(-100%);
        transition: transform 0.22s ease;
        box-shadow: 2px 0 16px rgba(0,0,0,0.2);
        padding-top: calc(20px + env(safe-area-inset-top, 0px));
    }
    nav.sidebar.open { transform: translateX(0); }
    .scrim {
        display: block;
        position: fixed; inset: 0;
        background: rgba(0,0,0,0.45);
        z-index: 15;
        opacity: 0;
        pointer-events: none;
        transition: opacity 0.2s;
    }
    .scrim.open { opacity: 1; pointer-events: auto; }
    .mobile-header {
        display: flex;
        align-items: center;
        gap: 12px;
        padding: 10px 14px;
        padding-top: calc(10px + env(safe-area-inset-top, 0px));
        background: var(--bg-raised);
        border-bottom: 1px solid var(--rule);
        position: sticky;
        top: 0;
        z-index: 10;
    }
    .menu-btn {
        display: flex;
        align-items: center;
        justify-content: center;
        width: 36px; height: 36px;
        border: 1px solid var(--rule);
        background: var(--bg-raised);
        border-radius: 6px;
        cursor: pointer;
        padding: 0;
    }
    .menu-btn svg { width: 20px; height: 20px; stroke: var(--ink); }
    .mobile-header .ttl { font-size: 14px; font-weight: 600; }
    main.content { padding: 20px 16px 60px; }
}

/* ---------- Typography ---------- */
h1 { font-size: 28px; line-height: 1.2; color: var(--accent); margin: 0 0 14px; font-weight: 700; letter-spacing: -0.02em; }
h2 { font-size: 20px; line-height: 1.3; color: var(--exercise-head); margin: 32px 0 10px; font-weight: 600; letter-spacing: -0.01em; }
h3 { font-size: 15px; line-height: 1.3; color: var(--ink); margin: 20px 0 6px; font-weight: 600; }
p { margin: 0 0 12px; }
ul, ol { margin: 0 0 14px; padding-left: 22px; }
ul li, ol li { margin-bottom: 4px; }
.lead { font-size: 17px; color: var(--muted); }
.week-marker {
    font-size: 11px;
    letter-spacing: 0.14em;
    text-transform: uppercase;
    color: var(--accent);
    margin-bottom: 2px;
}
hr.divider {
    border: none;
    border-top: 1px solid var(--rule);
    margin: 10px 0 20px;
}
.goals {
    background: var(--bg-raised);
    border: 1px solid var(--rule);
    border-radius: 8px;
    padding: 14px 18px;
    margin-bottom: 24px;
}
.goals h3 { margin-top: 0; }
.goals ul { margin-bottom: 0; }

/* ---------- Boxes ---------- */
.box { border-radius: 8px; padding: 14px 18px; margin: 16px 0; }
.box .box-title { font-weight: 700; font-size: 14px; margin-bottom: 8px; }
.box.grammar { background: var(--grammar-bg); border: 1px solid var(--grammar-border); }
.box.grammar .box-title { color: var(--grammar-head); }
.box.exercise { background: var(--exercise-bg); border: 1px solid var(--exercise-border); }
.box.exercise .box-title { color: var(--exercise-head); }
.box.exercise ol { padding-left: 24px; margin-bottom: 0; }
.box.exercise ol li { margin-bottom: 6px; }
.box.resource { background: var(--resource-bg); border: 1px solid var(--resource-border); }
.box.resource .box-title { color: var(--resource-head); }
.box.resource ul { list-style: none; padding-left: 0; margin-bottom: 0; }
.box.resource ul li { padding-left: 16px; position: relative; margin-bottom: 4px; font-size: 14px; }
.box.resource ul li::before { content: "•"; position: absolute; left: 4px; color: var(--resource-head); }
.box .jp { font-size: 1.05em; }

/* ---------- Vocab tables ---------- */
.vocab-wrapper { margin: 12px 0 20px; }
.vocab-toolbar {
    display: flex;
    gap: 8px;
    align-items: center;
    flex-wrap: wrap;
    margin-bottom: 8px;
    padding: 6px 2px;
}
.vocab-toolbar .count { font-size: 12px; color: var(--muted); margin-left: auto; }
.btn {
    display: inline-flex;
    align-items: center;
    gap: 6px;
    padding: 5px 11px;
    border-radius: 999px;
    border: 1px solid var(--rule);
    background: var(--bg-raised);
    color: var(--ink);
    font-size: 12px;
    cursor: pointer;
    user-select: none;
    font-family: inherit;
}
.btn:hover { background: var(--table-row-alt); }
.btn.active { background: var(--accent); color: white; border-color: var(--accent); }
.btn svg { width: 12px; height: 12px; }
.btn.primary { background: var(--accent); color: white; border-color: var(--accent); font-weight: 600; padding: 8px 18px; font-size: 14px; }
.btn.primary:hover { background: var(--accent-dim); }

table.vocab {
    width: 100%;
    border-collapse: collapse;
    font-size: 14px;
    background: var(--bg-raised);
    border-radius: 8px;
    overflow: hidden;
    box-shadow: 0 1px 0 var(--rule);
}
table.vocab th {
    background: var(--table-head-bg);
    color: white;
    text-align: left;
    padding: 8px 12px;
    font-weight: 600;
    font-size: 12px;
    text-transform: uppercase;
    letter-spacing: 0.04em;
}
table.vocab td {
    padding: 10px 12px;
    border-top: 1px solid var(--rule);
    vertical-align: middle;
}
table.vocab tr.known { opacity: 0.55; }
table.vocab tr.known td.en { text-decoration: line-through; }
table.vocab tr:nth-child(even):not(.header) td { background: var(--table-row-alt); }
table.vocab td.jp-cell { font-size: 1.08em; min-width: 90px; }
table.vocab td.actions { white-space: nowrap; text-align: right; width: 1%; }
.row-btn {
    width: 28px; height: 28px;
    padding: 0;
    margin-left: 4px;
    display: inline-flex;
    align-items: center;
    justify-content: center;
    border: 1px solid var(--rule);
    background: var(--bg-raised);
    border-radius: 6px;
    cursor: pointer;
}
.row-btn:hover { background: var(--table-row-alt); }
.row-btn svg { width: 14px; height: 14px; stroke: var(--muted); fill: none; }
.row-btn.known svg { stroke: var(--accent); fill: var(--accent); }
.row-btn.playing { background: var(--accent); border-color: var(--accent); }
.row-btn.playing svg { stroke: white; fill: white; }

/* Hidden-meaning mode */
.vocab.hide-en td.en { color: transparent; background: var(--table-row-alt); cursor: pointer; border-radius: 4px; }
.vocab.hide-en tr:nth-child(even):not(.header) td.en { background: var(--rule); }
.vocab.hide-en td.en.revealed { color: var(--ink); background: transparent !important; }
.vocab.hide-pr td.pr { color: transparent; background: var(--table-row-alt); cursor: pointer; border-radius: 4px; }
.vocab.hide-pr tr:nth-child(even):not(.header) td.pr { background: var(--rule); }
.vocab.hide-pr td.pr.revealed { color: var(--ink); background: transparent !important; }

/* ---------- Kana / alphabet charts ---------- */
.kana-grid { display: grid; gap: 4px; margin: 14px 0 20px; }
.kana-grid.c5 { grid-template-columns: repeat(5, minmax(0, 1fr)); }
.kana-cell {
    aspect-ratio: 1 / 1;
    background: var(--bg-raised);
    border: 1px solid var(--rule);
    border-radius: 6px;
    display: flex;
    flex-direction: column;
    align-items: center;
    justify-content: center;
    cursor: pointer;
    user-select: none;
    position: relative;
    transition: transform 0.08s, background 0.1s;
}
.kana-cell:hover { background: var(--table-row-alt); }
.kana-cell:active { transform: scale(0.96); }
.kana-cell.empty { background: transparent; border: none; cursor: default; }
.kana-cell .glyph { font-size: 1.6em; line-height: 1; }
.kana-cell .roma { font-size: 0.7em; color: var(--very-muted); margin-top: 3px; font-family: -apple-system, sans-serif; }
.kana-cell.playing { background: var(--accent); color: white; }
.kana-cell.playing .roma { color: rgba(255,255,255,0.8); }
.hide-roma .kana-cell .roma { opacity: 0; }

/* ---------- Kanji reference grid ---------- */
.kanji-grid { display: grid; gap: 8px; grid-template-columns: repeat(3, 1fr); margin: 16px 0; }
.kanji-card {
    background: var(--bg-raised);
    border: 1px solid var(--rule);
    border-radius: 6px;
    padding: 10px 12px;
    display: flex;
    gap: 10px;
    align-items: center;
}
.kanji-card .k { font-size: 32px; line-height: 1; color: var(--accent); }
.kanji-card .info { font-size: 11px; color: var(--muted); line-height: 1.35; }
.kanji-card .info .n { color: var(--very-muted); font-size: 9px; }
.kanji-card .info .m { color: var(--ink); font-weight: 500; font-size: 13px; }
@media (max-width: 600px) { .kanji-grid { grid-template-columns: repeat(2, 1fr); } }

/* ---------- Reading passage ---------- */
.reading {
    background: var(--bg-raised);
    border: 1px solid var(--rule);
    border-radius: 8px;
    padding: 18px 22px;
    margin: 16px 0;
    font-size: 1.08em;
    line-height: 1.9;
}

/* ---------- Progress / nav footer ---------- */
.week-footer {
    display: flex;
    justify-content: space-between;
    gap: 10px;
    align-items: center;
    margin-top: 42px;
    padding-top: 20px;
    border-top: 1px solid var(--rule);
    flex-wrap: wrap;
}
.week-footer .nav-btn {
    padding: 10px 16px;
    font-size: 13px;
    border-radius: 6px;
    border: 1px solid var(--rule);
    background: var(--bg-raised);
    cursor: pointer;
    color: var(--ink);
    text-decoration: none;
    display: inline-flex;
    align-items: center;
    gap: 6px;
    font-family: inherit;
}
.week-footer .nav-btn:hover { background: var(--table-row-alt); }
.mark-done { padding: 10px 20px; font-size: 14px; font-weight: 600; }
.mark-done.done { background: #2a6b3a; color: white; border-color: #2a6b3a; }

/* ---------- Welcome / dashboard ---------- */
.dashboard { }
.hero {
    text-align: center;
    padding: 24px 10px 20px;
    border-bottom: 1px solid var(--rule);
    margin-bottom: 28px;
}
.hero h1 { font-size: 38px; color: var(--ink); margin-bottom: 6px; }
.hero .hero-jp { font-size: 22px; color: var(--accent); margin-bottom: 10px; }
.hero .hero-sub { color: var(--muted); font-size: 15px; }
.progress-overview {
    display: grid;
    grid-template-columns: repeat(3, 1fr);
    gap: 12px;
    margin: 20px 0 30px;
}
.stat {
    background: var(--bg-raised);
    border: 1px solid var(--rule);
    border-radius: 8px;
    padding: 14px;
    text-align: center;
}
.stat .n { font-size: 28px; font-weight: 700; color: var(--accent); font-variant-numeric: tabular-nums; }
.stat .l { font-size: 11px; color: var(--muted); text-transform: uppercase; letter-spacing: 0.06em; margin-top: 2px; }
.progress-bar {
    height: 6px;
    background: var(--rule);
    border-radius: 3px;
    overflow: hidden;
    margin: 10px 0 20px;
}
.progress-bar .fill { height: 100%; background: var(--accent); transition: width 0.4s; }

.inline-jp { font-family: "Noto Sans JP", -apple-system, "Hiragino Kaku Gothic Pro", "Yu Gothic", Meiryo, sans-serif; }

.footer-settings {
    display: flex;
    gap: 10px;
    padding: 14px 20px;
    border-top: 1px solid var(--rule);
    margin-top: 20px;
    flex-wrap: wrap;
}
.footer-settings .btn { font-size: 11px; }
.gift-note {
    text-align: center;
    color: var(--very-muted);
    font-style: italic;
    font-size: 12px;
    padding: 20px;
    margin-top: 20px;
}
"""

JS = r"""
const STORAGE_KEY = 'jp_course_v1';
let state = {
    view: 'welcome',
    weekStatus: {},     // {1: 'started'|'complete', ...}
    knownVocab: {},     // {'w1-0': true, ...}
    hideEn: false,
    hideRoma: false,
    theme: null,        // null = system, 'light', 'dark'
};

function saveState() {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {}
}
function loadState() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        if (raw) {
            const loaded = JSON.parse(raw);
            state = Object.assign(state, loaded);
        }
    } catch (e) {}
    if (state.theme) document.documentElement.dataset.theme = state.theme;
}

// Scope all route handling to the hash, so first paint can read it directly.
function readRouteFromHash() {
    const hash = (location.hash || '').replace(/^#\/?/, '');
    if (hash) state.view = hash;
}

// --------- Speech synthesis ----------
let jpVoice = null;
function initVoice() {
    const voices = speechSynthesis.getVoices();
    jpVoice = voices.find(v => v.lang === 'ja-JP') || voices.find(v => v.lang.startsWith('ja'));
}
if ('speechSynthesis' in window) {
    initVoice();
    speechSynthesis.onvoiceschanged = initVoice;
}
function speak(text, cb) {
    if (!('speechSynthesis' in window)) { cb && cb(); return; }
    try {
        speechSynthesis.cancel();
        const u = new SpeechSynthesisUtterance(text);
        u.lang = 'ja-JP';
        if (jpVoice) u.voice = jpVoice;
        u.rate = 0.85;
        u.onend = () => cb && cb();
        u.onerror = () => cb && cb();
        speechSynthesis.speak(u);
    } catch (e) { cb && cb(); }
}

// --------- Helpers ----------
function esc(s) {
    return String(s || '').replace(/[&<>"']/g, c => ({'&':'&amp;','<':'&lt;','>':'&gt;','"':'&quot;',"'":'&#39;'}[c]));
}
// Content strings are authored HTML (entities, <b>, <i>, <span>, <br>) and are
// trusted. Every content string must go through this into innerHTML — inserting
// one as a text node shows entities like &rsquo; literally.
function richText(s) {
    s = String(s || '');
    s = s.replace(/<font[^>]*>/g, '').replace(/<\/font>/g, '');
    return s;
}
function el(tag, attrs, ...children) {
    const n = document.createElement(tag);
    for (const k in (attrs || {})) {
        if (k === 'class') n.className = attrs[k];
        else if (k === 'html') n.innerHTML = attrs[k];
        else if (k.startsWith('on')) n.addEventListener(k.slice(2), attrs[k]);
        else n.setAttribute(k, attrs[k]);
    }
    for (const c of children) {
        if (c == null) continue;
        if (Array.isArray(c)) c.forEach(x => x && n.appendChild(x.nodeType ? x : document.createTextNode(x)));
        else n.appendChild(c.nodeType ? c : document.createTextNode(c));
    }
    return n;
}

// --------- Routing ----------
function go(view) {
    state.view = view;
    saveState();
    if (location.hash !== '#/' + view) location.hash = '/' + view;
    render();
    closeNav();
    window.scrollTo(0, 0);
}
window.addEventListener('hashchange', () => {
    const hash = (location.hash || '').replace(/^#\/?/, '');
    if (hash && hash !== state.view) {
        state.view = hash;
        render();
        window.scrollTo(0, 0);
    }
});

// --------- Rendering ----------
function render() {
    renderNav();
    const main = document.getElementById('content');
    main.innerHTML = '';
    const v = state.view;
    if (v === 'welcome' || !v) main.appendChild(renderWelcome());
    else if (v === 'resources') main.appendChild(renderResources());
    else if (v.startsWith('week-')) main.appendChild(renderWeek(parseInt(v.slice(5), 10)));
    else if (v.startsWith('appx-')) main.appendChild(renderAppendix(v.slice(5)));
    else main.appendChild(renderWelcome());
    // Mobile header title update
    const mt = document.getElementById('mobile-title');
    if (mt) mt.innerHTML = richText(currentViewLabel());
}

function currentViewLabel() {
    const v = state.view;
    if (v === 'welcome') return 'Welcome';
    if (v === 'resources') return 'Resources';
    if (v.startsWith('week-')) return 'Week ' + v.slice(5);
    if (v.startsWith('appx-')) {
        const a = COURSE.appendices.find(x => x.id === v.slice(5));
        return a ? a.title : 'Reference';
    }
    return 'Beginner Japanese';
}

function renderNav() {
    const nav = document.getElementById('nav-inner');
    nav.innerHTML = '';
    nav.appendChild(el('div', {class: 'brand'},
        el('h1', {class: 'title'}, COURSE.title),
        el('p', {class: 'title-jp inline-jp'}, COURSE.titleJp),
        el('p', {class: 'sub'}, COURSE.subtitle)
    ));
    nav.appendChild(navItem('welcome', 'Welcome', ''));
    nav.appendChild(navItem('resources', 'Resources', ''));
    nav.appendChild(el('div', {class: 'section-label'}, 'Weeks'));
    COURSE.weeks.forEach(w => {
        const status = state.weekStatus[w.num] || '';
        nav.appendChild(navItem('week-' + w.num, w.title, String(w.num).padStart(2, '0'), status));
    });
    nav.appendChild(el('div', {class: 'section-label'}, 'Reference'));
    COURSE.appendices.forEach(a => nav.appendChild(navItem('appx-' + a.id, a.title, '')));
    nav.appendChild(el('div', {class: 'footer-settings'},
        el('button', {class: 'btn', onclick: toggleTheme}, '◐ Theme'),
        el('button', {class: 'btn', onclick: resetProgress}, '⟲ Reset progress')
    ));
    nav.appendChild(el('div', {class: 'gift-note'}, 'A gift, with care.'));
}

function navItem(id, label, num, status) {
    const active = state.view === id ? ' active' : '';
    const statusEl = typeof status === 'string'
        ? el('span', {class: 'status' + (status ? ' ' + status : '')})
        : null;
    return el('a', {class: 'item' + active, onclick: () => go(id)},
        num ? el('span', {class: 'num'}, num) : null,
        el('span', {class: 'label', html: richText(label)}),
        statusEl
    );
}

function renderWelcome() {
    const totalVocab = COURSE.weeks.reduce((n, w) => n + countVocab(w), 0);
    const knownCount = Object.keys(state.knownVocab).filter(k => state.knownVocab[k]).length;
    const completedWeeks = COURSE.weeks.filter(w => state.weekStatus[w.num] === 'complete').length;
    const firstUnfinished = COURSE.weeks.find(w => state.weekStatus[w.num] !== 'complete') || COURSE.weeks[0];
    const main = el('div', {class: 'dashboard'});
    main.appendChild(el('div', {class: 'hero'},
        el('h1', {}, COURSE.title),
        el('div', {class: 'hero-jp inline-jp'}, COURSE.titleJp),
        el('div', {class: 'hero-sub'}, COURSE.subtitle + ' · For an absolute beginner, aimed at JLPT N5 and conversational basics.')
    ));
    main.appendChild(el('div', {class: 'progress-overview'},
        el('div', {class: 'stat'}, el('div', {class: 'n'}, completedWeeks + '/' + COURSE.weeks.length), el('div', {class: 'l'}, 'Weeks done')),
        el('div', {class: 'stat'}, el('div', {class: 'n'}, knownCount), el('div', {class: 'l'}, 'Vocab known')),
        el('div', {class: 'stat'}, el('div', {class: 'n'}, totalVocab), el('div', {class: 'l'}, 'Total vocab'))
    ));
    const pct = (completedWeeks / COURSE.weeks.length) * 100;
    main.appendChild(el('div', {class: 'progress-bar'}, el('div', {class: 'fill', style: 'width: ' + pct + '%'})));
    main.appendChild(el('div', {style: 'text-align: center; margin-bottom: 30px;'},
        el('button', {class: 'btn primary', onclick: () => go('week-' + firstUnfinished.num)},
            completedWeeks === 0 ? 'Start Week 1 →' : 'Continue to Week ' + firstUnfinished.num + ' →')
    ));
    COURSE.front.forEach(section => main.appendChild(renderSection(section, 'welcome')));
    return main;
}

function renderResources() {
    const main = el('div', {});
    main.appendChild(el('h1', {}, 'Core Resources'));
    main.appendChild(el('hr', {class: 'divider'}));
    main.appendChild(el('p', {class: 'lead'}, 'Keep this page bookmarked. These are the free, high-quality references you\u2019ll return to all twelve weeks.'));
    COURSE.resources.forEach(group => {
        main.appendChild(el('h2', {html: richText(group.title)}));
        const ul = el('ul', {});
        group.items.forEach(it => ul.appendChild(el('li', {html: richText(it)})));
        main.appendChild(ul);
    });
    return main;
}

function countVocab(week) {
    let n = 0;
    week.sections.forEach(s => { if (s.type === 'vocab') n += s.rows.length; });
    return n;
}

function renderWeek(num) {
    const week = COURSE.weeks.find(w => w.num === num);
    if (!week) return el('div', {}, 'Week not found.');
    if (!state.weekStatus[num]) { state.weekStatus[num] = 'started'; saveState(); }
    const main = el('div', {});
    main.appendChild(el('div', {class: 'week-marker'}, 'Week ' + num));
    main.appendChild(el('h1', {html: richText(week.title)}));
    main.appendChild(el('hr', {class: 'divider'}));
    main.appendChild(el('div', {class: 'goals'},
        el('h3', {}, 'Goals this week'),
        el('ul', {}, ...week.goals.map(g => el('li', {html: richText(g)})))
    ));
    week.sections.forEach((s, i) => main.appendChild(renderSection(s, 'w' + num + '-s' + i, num)));
    main.appendChild(renderWeekFooter(num));
    return main;
}

function renderSection(section, keyBase, weekNum) {
    switch (section.type) {
        case 'h2': return el('h2', {html: richText(section.text)});
        case 'h3': return el('h3', {html: richText(section.text)});
        case 'p': return el('p', {html: richText(section.text)});
        case 'ul': {
            const ul = el('ul', {});
            section.items.forEach(it => ul.appendChild(el('li', {html: richText(it)})));
            return ul;
        }
        case 'vocab': return renderVocab(section, keyBase, weekNum);
        case 'kana': return renderKanaGrid(section);
        case 'grammar': return el('div', {class: 'box grammar'},
            section.title ? el('div', {class: 'box-title', html: richText(section.title)}) : null,
            el('div', {html: richText(section.body)})
        );
        case 'exercise': return el('div', {class: 'box exercise'},
            el('div', {class: 'box-title', html: richText(section.title || 'Exercises')}),
            el('ol', {}, ...section.items.map(it => el('li', {html: richText(it)})))
        );
        case 'resource': return el('div', {class: 'box resource'},
            el('div', {class: 'box-title', html: richText(section.title || 'Resources this week')}),
            el('ul', {}, ...section.items.map(it => el('li', {html: richText(it)})))
        );
        case 'reading': return el('div', {class: 'reading inline-jp', html: richText(section.text)});
        case 'kanji-grid': return renderKanjiGrid(section);
        case 'table': return renderPlainTable(section);
        case 'selfcheck': {
            const wrap = el('div', {});
            wrap.appendChild(el('h2', {html: richText(section.title || 'Self-check')}));
            wrap.appendChild(el('ul', {}, ...section.items.map(it => el('li', {html: richText(it)}))));
            if (section.note) wrap.appendChild(el('p', {class: 'lead', style: 'font-size: 14px; font-style: italic;', html: richText(section.note)}));
            return wrap;
        }
    }
    return document.createTextNode('');
}

function renderVocab(section, keyBase, weekNum) {
    const wrap = el('div', {class: 'vocab-wrapper'});
    const toolbar = el('div', {class: 'vocab-toolbar'});
    const hideEnBtn = el('button', {class: 'btn' + (state.hideEn ? ' active' : ''),
        onclick: () => { state.hideEn = !state.hideEn; saveState(); render(); }}, 'Hide English');
    const hidePrBtn = el('button', {class: 'btn' + (state.hideRoma ? ' active' : ''),
        onclick: () => { state.hideRoma = !state.hideRoma; saveState(); render(); }}, 'Hide reading');
    toolbar.appendChild(hideEnBtn);
    toolbar.appendChild(hidePrBtn);
    const knownKeys = section.rows.map((_, i) => keyBase + '-v' + i);
    const knownNow = knownKeys.filter(k => state.knownVocab[k]).length;
    toolbar.appendChild(el('span', {class: 'count'}, knownNow + ' / ' + section.rows.length + ' known'));
    wrap.appendChild(toolbar);
    if (section.title) wrap.appendChild(el('h3', {html: richText(section.title)}));
    const table = el('table', {class: 'vocab' + (state.hideEn ? ' hide-en' : '') + (state.hideRoma ? ' hide-pr' : '')});
    const thead = el('tr', {class: 'header'},
        el('th', {html: richText(section.cols && section.cols[0] || 'Japanese')}),
        el('th', {html: richText(section.cols && section.cols[1] || 'Reading')}),
        el('th', {html: richText(section.cols && section.cols[2] || 'English')}),
        el('th', {})
    );
    table.appendChild(thead);
    section.rows.forEach((row, i) => {
        const key = keyBase + '-v' + i;
        const known = !!state.knownVocab[key];
        const tr = el('tr', {class: known ? 'known' : ''},
            el('td', {class: 'jp-cell inline-jp', html: richText(row[0])}),
            el('td', {class: 'pr', html: richText(row[1]), onclick: ev => ev.currentTarget.classList.toggle('revealed')}),
            el('td', {class: 'en', html: richText(row[2]), onclick: ev => ev.currentTarget.classList.toggle('revealed')}),
            el('td', {class: 'actions'},
                el('button', {class: 'row-btn', title: 'Play audio', onclick: ev => playFromRow(ev.currentTarget, row[0])},
                    svgSpeaker()),
                el('button', {class: 'row-btn' + (known ? ' known' : ''), title: 'Mark known', onclick: ev => toggleKnown(ev.currentTarget, key)},
                    svgStar())
            )
        );
        table.appendChild(tr);
    });
    wrap.appendChild(table);
    return wrap;
}

function playFromRow(btn, text) {
    document.querySelectorAll('.row-btn.playing').forEach(b => b.classList.remove('playing'));
    btn.classList.add('playing');
    speak(text, () => btn.classList.remove('playing'));
}
function toggleKnown(btn, key) {
    const now = !state.knownVocab[key];
    state.knownVocab[key] = now;
    saveState();
    btn.classList.toggle('known', now);
    const tr = btn.closest('tr'); if (tr) tr.classList.toggle('known', now);
    // update count label without full re-render
    const wrap = btn.closest('.vocab-wrapper');
    if (wrap) {
        const total = wrap.querySelectorAll('tr:not(.header)').length;
        const known = wrap.querySelectorAll('tr.known').length;
        const cnt = wrap.querySelector('.count'); if (cnt) cnt.textContent = known + ' / ' + total + ' known';
    }
}

function svgSpeaker() {
    const s = document.createElementNS('http://www.w3.org/2000/svg','svg');
    s.setAttribute('viewBox','0 0 24 24'); s.setAttribute('fill','none'); s.setAttribute('stroke-width','2');
    s.innerHTML = '<path d="M11 5L6 9H2v6h4l5 4V5z" stroke-linecap="round" stroke-linejoin="round"/><path d="M19 12c0-2-1-3.8-2.5-5M15.5 8.5c.8.8 1.5 2 1.5 3.5s-.7 2.7-1.5 3.5" stroke-linecap="round"/>';
    return s;
}
function svgStar() {
    const s = document.createElementNS('http://www.w3.org/2000/svg','svg');
    s.setAttribute('viewBox','0 0 24 24'); s.setAttribute('stroke-width','1.8');
    s.innerHTML = '<path d="M12 3l2.6 5.6 6.1.7-4.6 4.2 1.3 6-5.4-3.1-5.4 3.1 1.3-6-4.6-4.2 6.1-.7z" stroke-linejoin="round"/>';
    return s;
}

function renderKanaGrid(section) {
    const wrap = el('div', {});
    if (section.title) wrap.appendChild(el('h3', {html: richText(section.title)}));
    const toolbar = el('div', {class: 'vocab-toolbar'},
        el('button', {class: 'btn', onclick: ev => ev.currentTarget.parentElement.nextElementSibling.classList.toggle('hide-roma')}, 'Hide readings')
    );
    wrap.appendChild(toolbar);
    const grid = el('div', {class: 'kana-grid c5 inline-jp'});
    section.rows.forEach(row => {
        row.forEach(cell => {
            if (cell == null) grid.appendChild(el('div', {class: 'kana-cell empty'}));
            else {
                const [g, r] = cell;
                const c = el('div', {class: 'kana-cell', onclick: ev => playFromRow(ev.currentTarget, g)},
                    el('div', {class: 'glyph', html: richText(g)}),
                    el('div', {class: 'roma', html: richText(r)})
                );
                grid.appendChild(c);
            }
        });
    });
    wrap.appendChild(grid);
    return wrap;
}

function renderKanjiGrid(section) {
    const wrap = el('div', {});
    if (section.title) wrap.appendChild(el('h3', {html: richText(section.title)}));
    const grid = el('div', {class: 'kanji-grid'});
    section.items.forEach((it, idx) => {
        grid.appendChild(el('div', {class: 'kanji-card'},
            el('div', {class: 'k inline-jp', html: richText(it[0]), onclick: () => speak(it[0])}),
            el('div', {class: 'info'},
                el('div', {class: 'n'}, '#' + (section.startAt ? section.startAt + idx : idx + 1)),
                el('div', {class: 'm', html: richText(it[1])}),
                it[2] ? el('div', {html: richText(it[2])}) : null
            )
        ));
    });
    wrap.appendChild(grid);
    return wrap;
}

function renderPlainTable(section) {
    const wrap = el('div', {});
    if (section.title) wrap.appendChild(el('h3', {html: richText(section.title)}));
    const table = el('table', {class: 'vocab'});
    const headers = section.headers || [];
    if (headers.length) {
        const tr = el('tr', {class: 'header'});
        headers.forEach(h => tr.appendChild(el('th', {html: richText(h)})));
        table.appendChild(tr);
    }
    section.rows.forEach(row => {
        const tr = el('tr', {});
        row.forEach(c => tr.appendChild(el('td', {html: richText(c), class: 'inline-jp'})));
        table.appendChild(tr);
    });
    wrap.appendChild(table);
    return wrap;
}

function renderWeekFooter(num) {
    const done = state.weekStatus[num] === 'complete';
    const prev = num > 1 ? el('button', {class: 'nav-btn', onclick: () => go('week-' + (num - 1))}, '← Week ' + (num - 1)) : el('span');
    const next = num < COURSE.weeks.length ? el('button', {class: 'nav-btn', onclick: () => go('week-' + (num + 1))}, 'Week ' + (num + 1) + ' →') : el('span');
    const mark = el('button', {class: 'btn mark-done' + (done ? ' done' : ''),
        onclick: ev => {
            state.weekStatus[num] = done ? 'started' : 'complete';
            saveState();
            render();
        }
    }, done ? '✓ Completed' : 'Mark week complete');
    return el('div', {class: 'week-footer'}, prev, mark, next);
}

function renderAppendix(id) {
    const a = COURSE.appendices.find(x => x.id === id);
    if (!a) return el('div', {}, 'Not found.');
    const main = el('div', {});
    main.appendChild(el('h1', {html: richText(a.title)}));
    main.appendChild(el('hr', {class: 'divider'}));
    if (a.intro) main.appendChild(el('p', {class: 'lead', html: richText(a.intro)}));
    a.sections.forEach((s, i) => main.appendChild(renderSection(s, 'appx-' + id + '-s' + i)));
    return main;
}

// --------- Theme ---------
function toggleTheme() {
    const cur = state.theme;
    const next = cur === 'dark' ? 'light' : cur === 'light' ? null : 'dark';
    state.theme = next;
    if (next) document.documentElement.dataset.theme = next;
    else delete document.documentElement.dataset.theme;
    saveState();
}
function resetProgress() {
    if (!confirm('Reset all progress? This clears which weeks are complete and which vocabulary you\u2019ve marked known.')) return;
    state.weekStatus = {};
    state.knownVocab = {};
    saveState();
    render();
}

// --------- Mobile nav ---------
function openNav() {
    document.querySelector('nav.sidebar').classList.add('open');
    document.querySelector('.scrim').classList.add('open');
}
function closeNav() {
    document.querySelector('nav.sidebar').classList.remove('open');
    document.querySelector('.scrim').classList.remove('open');
}

// --------- Boot ---------
window.addEventListener('DOMContentLoaded', () => {
    loadState();
    readRouteFromHash();
    render();
    document.getElementById('menu-btn').addEventListener('click', openNav);
    document.querySelector('.scrim').addEventListener('click', closeNav);
});
"""

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
    html = (HTML_TEMPLATE
            .replace('__CSS__', CSS)
            .replace('__COURSE_JSON__', json.dumps(COURSE, ensure_ascii=False))
            .replace('__JS__', JS))
    with open(OUT, 'w', encoding='utf-8') as f:
        f.write(html)
    size = os.path.getsize(OUT)
    print(f'OK: {OUT}  ({size/1024:.1f} KB)')


if __name__ == '__main__':
    build()
