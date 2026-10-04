
const STORAGE_KEY = 'jp_course_v1';
// No `schema` here on purpose: it must come from storage (or be set after a
// successful load), so Object.assign can never make an old blob look migrated.
let state = {
    view: 'welcome',
    weekStatus: {},     // {1: 'started'|'complete', ...}
    known: {},          // {'v:ねこ|neko': true} — stable vocab IDs (schema 2)
    hideEn: false,
    hideRoma: false,
    theme: null,        // null = system, 'light', 'dark'
};
// Set when stored progress can't be read. Saving is then disabled for the
// session, so unreadable data is never overwritten with defaults.
let storageBroken = false;

function saveState() {
    if (storageBroken) return;
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {}
}

function resolveId(id) {
    const seen = new Set();
    while (COURSE.idAliases[id] && !seen.has(id)) { seen.add(id); id = COURSE.idAliases[id]; }
    return id;
}

// Schema 1 stored stars by position ('w1-s6-v8'). Move them to stable IDs.
// Returns a new object; `knownVocab` is kept untouched so an older build
// still finds its stars after a rollback.
function migrateToSchema2(loaded) {
    const known = Object.assign({}, loaded.known || {});
    const legacyUnmapped = {};
    const old = loaded.knownVocab || {};
    for (const k in old) {
        const id = COURSE.legacyKeys[k];
        if (!id) { legacyUnmapped[k] = old[k]; continue; }
        if (old[k] === true) known[resolveId(id)] = true;   // true anywhere wins; false is dropped
    }
    return Object.assign({}, loaded, { known, legacyUnmapped, schema: 2 });
}

function loadState() {
    let raw = null;
    try { raw = localStorage.getItem(STORAGE_KEY); } catch (e) { storageBroken = true; }
    if (raw) {
        try {
            let loaded = JSON.parse(raw);
            if (!loaded || typeof loaded !== 'object' || Array.isArray(loaded)) throw new Error('not an object');
            if (!(loaded.schema >= 2)) {
                try { localStorage.setItem(STORAGE_KEY + '_bak', raw); } catch (e) {}
                loaded = migrateToSchema2(loaded);
            }
            state = Object.assign(state, loaded);
        } catch (e) {
            storageBroken = true;
        }
    }
    if (!storageBroken) state.schema = 2;
    if (state.theme) document.documentElement.dataset.theme = state.theme;
}

// Every starrable vocab ID in the course (weeks + appendices), deduplicated.
let _allVocabIds = null;
function allVocabIds() {
    if (!_allVocabIds) {
        _allVocabIds = new Set();
        const secs = [].concat(...COURSE.weeks.map(w => w.sections), ...COURSE.appendices.map(a => a.sections));
        secs.filter(s => s.type === 'vocab').forEach(s => s.ids.forEach(id => _allVocabIds.add(id)));
    }
    return _allVocabIds;
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
    hideSheet();
    sheetOpener = null;
    const main = document.getElementById('content');
    main.innerHTML = '';
    if (storageBroken) main.appendChild(el('div', {class: 'notice'},
        'Your saved progress couldn\u2019t be read, so nothing will be saved during this visit. ' +
        'The stored data has been left untouched.'));
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
    const ids = allVocabIds();
    const totalVocab = ids.size;
    const knownCount = Object.keys(state.known).filter(id => state.known[id] && ids.has(id)).length;
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
        case 'vocab': return renderVocab(section);
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

function renderVocab(section) {
    const wrap = el('div', {class: 'vocab-wrapper'});
    const toolbar = el('div', {class: 'vocab-toolbar'});
    const hideEnBtn = el('button', {class: 'btn' + (state.hideEn ? ' active' : ''),
        onclick: () => { state.hideEn = !state.hideEn; saveState(); render(); }}, 'Hide English');
    const hidePrBtn = el('button', {class: 'btn' + (state.hideRoma ? ' active' : ''),
        onclick: () => { state.hideRoma = !state.hideRoma; saveState(); render(); }}, 'Hide reading');
    toolbar.appendChild(hideEnBtn);
    toolbar.appendChild(hidePrBtn);
    toolbar.appendChild(el('span', {class: 'count'}, vocabCountLabel(section.ids)));
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
        const id = section.ids[i];
        const known = !!state.known[id];
        const tr = el('tr', {class: known ? 'known' : '', 'data-vid': id},
            el('td', {class: 'jp-cell inline-jp', html: richText(row[0])}),
            el('td', {class: 'pr', html: richText(row[1]), onclick: ev => ev.currentTarget.classList.toggle('revealed')}),
            el('td', {class: 'en', html: richText(row[2]), onclick: ev => ev.currentTarget.classList.toggle('revealed')}),
            el('td', {class: 'actions'},
                el('button', {class: 'row-btn', title: 'Play audio', onclick: ev => playFromRow(ev.currentTarget, section.speak[i])},
                    svgSpeaker()),
                el('button', {class: 'row-btn' + (known ? ' known' : ''), title: 'Mark known', onclick: () => toggleKnown(id)},
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
function vocabCountLabel(ids) {
    return ids.filter(id => state.known[id]).length + ' / ' + ids.length + ' known';
}
function toggleKnown(id) {
    const now = !state.known[id];
    if (now) state.known[id] = true; else delete state.known[id];
    saveState();
    // The same word can appear more than once on a page: update every row,
    // then every table's count, without a full re-render.
    document.querySelectorAll('tr[data-vid]').forEach(tr => {
        if (tr.getAttribute('data-vid') !== id) return;
        tr.classList.toggle('known', now);
        const star = tr.querySelector('button[title="Mark known"]');
        if (star) star.classList.toggle('known', now);
    });
    document.querySelectorAll('.vocab-wrapper').forEach(wrap => {
        const ids = [...wrap.querySelectorAll('tr[data-vid]')].map(tr => tr.getAttribute('data-vid'));
        const cnt = wrap.querySelector('.count'); if (cnt) cnt.textContent = vocabCountLabel(ids);
    });
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
                const c = el('button', {class: 'kana-cell', type: 'button', onclick: ev => {
                        const b = ev.currentTarget;
                        playFromRow(b, g);
                        openSheet(g, b, !!b.closest('.hide-roma'));
                    }},
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

// --------- Detail sheet ----------
// Non-modal: the grid stays usable and the next tap updates the sheet, so
// playing sounds in a row is never interrupted.
let sheetOpener = null;     // element to return focus to on close
let sheetConceal = false;   // the opening grid had "Hide readings" on

function sheetEl() {
    let s = document.getElementById('glyph-sheet');
    if (!s) {
        s = el('aside', {id: 'glyph-sheet', class: 'sheet', role: 'dialog', 'aria-label': 'Character details'});
        s.hidden = true;
        document.body.appendChild(s);
    }
    return s;
}

function concealable(cls, text) {
    return el('button', {type: 'button', class: cls + (sheetConceal ? ' concealed' : ''),
        title: sheetConceal ? 'Tap to show' : '',
        onclick: ev => ev.currentTarget.classList.remove('concealed')}, text);
}

function glyphChip(ch) {
    const g = COURSE.glyphs[ch];
    if (!g) return el('span', {class: 'glyph-chip static inline-jp'}, el('span', {class: 'g'}, ch));
    return el('button', {type: 'button', class: 'glyph-chip', onclick: () => { speak(ch); openSheet(ch); }},
        el('span', {class: 'g inline-jp'}, ch),
        el('span', {class: 'r' + (sheetConceal ? ' concealed' : '')}, g.romaji));
}

function label(text) { return el('span', {class: 'sheet-label'}, text); }

// Returns false when the character has no record yet (sound still plays).
function openSheet(ch, opener, conceal) {
    const g = COURSE.glyphs[ch];
    if (!g) return false;
    if (opener) { sheetOpener = opener; sheetConceal = !!conceal; }
    const s = sheetEl();
    s.innerHTML = '';
    s.appendChild(el('div', {class: 'sheet-head'},
        el('div', {class: 'sheet-glyph inline-jp'}, ch),
        concealable('sheet-roma', g.romaji),
        el('button', {class: 'row-btn', type: 'button', title: 'Play audio',
            onclick: ev => playFromRow(ev.currentTarget, ch)}, svgSpeaker()),
        el('button', {class: 'sheet-close', type: 'button', 'aria-label': 'Close', onclick: closeSheet}, '✕')));
    if (g.base) {
        s.appendChild(el('div', {class: 'sheet-base'}, label('Made from'),
            glyphChip(g.base), ' + ' + g.mark + ' ',
            el('span', {class: 'sheet-note'}, g.mark === '゛'
                ? 'dakuten — the two ticks voice the consonant'
                : 'handakuten — the small circle turns h into p')));
    }
    if (g.hook) s.appendChild(el('p', {class: 'sheet-hook'}, label('Memory hook'), g.hook));
    if (g.origin) s.appendChild(el('p', {class: 'sheet-origin'}, label('Origin'),
        'Simplified from the kanji ', el('span', {class: 'inline-jp'}, g.origin), '.'));
    if (g.voiced.length) s.appendChild(el('div', {class: 'sheet-voiced'}, label('With marks'), ...g.voiced.map(glyphChip)));
    if (g.looksLike.length) s.appendChild(el('div', {class: 'sheet-alike'}, label('Don’t confuse with'), ...g.looksLike.map(glyphChip)));
    if (g.example) {
        const [jp, reading, en] = g.example;
        s.appendChild(el('div', {class: 'sheet-example'}, label('Example'),
            el('span', {class: 'inline-jp ex-jp'}, jp), ' ',
            concealable('sheet-reading', reading), ' ',
            el('span', {class: 'ex-en'}, en), ' ',
            el('button', {class: 'row-btn', type: 'button', title: 'Play example',
                onclick: ev => playFromRow(ev.currentTarget, jp)}, svgSpeaker())));
    }
    s.hidden = false;
    document.body.classList.add('sheet-open');
    // Phone: keep the tapped cell visible above the bottom sheet.
    if (opener && opener.getBoundingClientRect) {
        const r = opener.getBoundingClientRect(), top = s.getBoundingClientRect().top;
        if (top > 0 && r.bottom > top - 8) window.scrollBy(0, r.bottom - top + 16);
    }
    return true;
}

function hideSheet() {
    const s = document.getElementById('glyph-sheet');
    if (s) s.hidden = true;
    document.body.classList.remove('sheet-open');
}

function closeSheet() {
    hideSheet();
    if (sheetOpener && document.contains(sheetOpener)) sheetOpener.focus();
    sheetOpener = null;
}

document.addEventListener('keydown', ev => {
    const s = document.getElementById('glyph-sheet');
    if (ev.key === 'Escape' && s && !s.hidden) closeSheet();
});

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
    state.known = {};
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
