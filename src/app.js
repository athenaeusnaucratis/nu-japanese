
const STORAGE_KEY = 'jp_course_v1';
// No `schema` here on purpose: it must come from storage (or be set after a
// successful load), so Object.assign can never make an old blob look migrated.
let state = {
    view: 'welcome',
    weekStatus: {},     // {1: 'started'|'complete', ...}
    known: {},          // {'v:ねこ|neko': true} — stable vocab IDs (schema 2)
    practice: {},       // {setId: {answer: 'known'|'learning'}}
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
    else if (v === 'practice') main.appendChild(renderPracticeHome());
    else if (v.startsWith('practice-')) main.appendChild(renderPractice(v.slice(9)));
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
    if (v === 'practice') return 'Practice';
    if (v.startsWith('practice-')) {
        const st = COURSE.practiceSets.find(x => x.id === v.slice(9));
        return st ? st.title : 'Practice';
    }
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
    nav.appendChild(navItem('practice', 'Practice', ''));
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
        g.romaji ? el('span', {class: 'r' + (sheetConceal ? ' concealed' : '')}, g.romaji)
                 : el('span', {class: 'r', html: richText(g.meaning)}));
}

function label(text) { return el('span', {class: 'sheet-label'}, text); }

// A component of a kanji: tappable when it is itself a character with a record.
function partChip(part, meaning) {
    const inner = [el('span', {class: 'g inline-jp'}, part), el('span', {class: 'r'}, meaning)];
    if (!COURSE.glyphs[part]) return el('span', {class: 'glyph-chip static'}, ...inner);
    return el('button', {type: 'button', class: 'glyph-chip', onclick: () => { speak(part); openSheet(part); }}, ...inner);
}

// Returns false when the character has no record yet (sound still plays).
function openSheet(ch, opener, conceal) {
    const g = COURSE.glyphs[ch];
    if (!g) return false;
    if (opener) { sheetOpener = opener; sheetConceal = !!conceal; }
    const s = sheetEl();
    s.innerHTML = '';
    s.appendChild(el('div', {class: 'sheet-head'},
        el('div', {class: 'sheet-glyph inline-jp'}, ch),
        g.script === 'kanji' ? el('div', {class: 'sheet-meaning', html: richText(g.meaning)})
                             : concealable('sheet-roma', g.romaji),
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
    if (g.readings) s.appendChild(el('p', {class: 'sheet-readings inline-jp'}, label('Readings'),
        el('span', {class: 'readings', html: richText(g.readings)})));
    if (g.svg) s.appendChild(el('div', {class: 'sheet-drawing'},
        el('span', {class: 'pic', html: g.svg}), el('span', {class: 'arrow'}, '\u2192'),
        el('span', {class: 'inline-jp to'}, ch)));
    if (g.hook) s.appendChild(el('p', {class: 'sheet-hook'}, label('Memory hook'), g.hook));
    if (g.origin) s.appendChild(el('p', {class: 'sheet-origin'}, label('Origin'),
        ...(g.script === 'kanji' ? [g.origin] : [
            g.script === 'katakana' ? 'Taken from part of the kanji ' : 'Simplified from the kanji ',
            el('span', {class: 'inline-jp'}, g.origin), '.'])));
    if (g.parts) s.appendChild(el('div', {class: 'sheet-parts'}, label('Built from'),
        ...g.parts.map(([part, meaning]) => partChip(part, meaning))));
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
        grid.appendChild(el('button', {class: 'kanji-card', type: 'button', onclick: ev => {
                const b = ev.currentTarget;
                playFromRow(b, it[0]);
                openSheet(it[0], b, false);
            }},
            el('div', {class: 'k inline-jp', html: richText(it[0])}),
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
    if (!confirm('Reset all progress? This clears which weeks are complete, which vocabulary you\u2019ve marked known, and your practice.')) return;
    state.weekStatus = {};
    state.known = {};
    state.practice = {};
    saveState();
    render();
}

// =================== Practice (tap-to-build recall) ===================
// Answer-checking: name the Japanese-specific slip, kindly. Pure + exported.
const SMALL_KANA = {'\u3041':'\u3042','\u3043':'\u3044','\u3045':'\u3046','\u3047':'\u3048','\u3049':'\u304a','\u3083':'\u3084','\u3085':'\u3086','\u3087':'\u3088','\u3063':'\u3064','\u308e':'\u308f',
    '\u30a1':'\u30a2','\u30a3':'\u30a4','\u30a5':'\u30a6','\u30a7':'\u30a8','\u30a9':'\u30aa','\u30e3':'\u30e4','\u30e5':'\u30e6','\u30e7':'\u30e8','\u30c3':'\u30c4','\u30ee':'\u30ef'};
function stripMarks(s) {
    return [...s].map(ch => (COURSE.glyphs[ch] && COURSE.glyphs[ch].base) || ch).join('');
}
function normSmall(s) {
    return [...s].map(ch => SMALL_KANA[ch] || ch).join('');
}
function checkAnswer(built, answer) {
    if (built === answer) return 'correct';
    if (stripMarks(built) === stripMarks(answer)) return 'dakuten';
    if (normSmall(built) === normSmall(answer)) return 'small-kana';
    if (answer.includes('\u30fc') && built.replace(/\u30fc/g, '') === answer.replace(/\u30fc/g, '')) return 'long-vowel';
    if ([...built].length < [...answer].length) return 'short';
    return 'wrong';
}
const FEEDBACK = {
    correct: '\u2713 Nice.',
    dakuten: '\u261d So close \u2014 check the dakuten / handakuten (\u309b \u309c).',
    'small-kana': '\u261d Nearly \u2014 one of those should be a small kana.',
    'long-vowel': '\u261d Almost \u2014 you dropped the long-vowel mark \u30fc.',
    short: '\u261d A kana or two short. Keep going.',
    wrong: '\u261d Not quite \u2014 try again, or reveal it.',
};

// --- session state (in-memory; per-item result is persisted to state.practice) ---
let P = null;   // {setId, queue:[item...], i, built:[], done, revealed}

function practiceRecord(setId, answer, status) {
    if (!state.practice) state.practice = {};
    if (!state.practice[setId]) state.practice[setId] = {};
    state.practice[setId][answer] = status;
    saveState();
}

function startPractice(setId, mode) {
    const set = COURSE.practiceSets.find(s => s.id === setId);
    if (!set) return;
    // New/learning first, known last \u2014 but everything is included.
    const prog = (state.practice && state.practice[setId]) || {};
    const order = set.items.slice().sort((a, b) =>
        (prog[a.answer] === 'known' ? 1 : 0) - (prog[b.answer] === 'known' ? 1 : 0));
    // 'build' = see English, build the Japanese. 'recognise' = see/hear the
    // Japanese, choose the English.
    P = {setId: setId, title: set.title, total: set.items.length, mode: mode || 'build',
         items: set.items, queue: order, i: 0, built: [], done: 0, revealed: false};
}

function practiceCurrentItem() { return P && P.queue[P.i]; }
function practiceCurrentAnswer() { const it = practiceCurrentItem(); return it ? it.answer : ''; }
function practiceCurrentCard() { const it = practiceCurrentItem(); return it ? {mode: P.mode, answer: it.answer, prompt: it.prompt} : null; }

// Reduce a gloss to its core so near-synonyms don't collide:
// "fish (to eat)" and "fish" -> "fish"; "rice; a cooked meal" -> "rice".
function normalizeMeaning(s) {
    return String(s).toLowerCase().replace(/\([^)]*\)/g, '').split(/[;/]/)[0].replace(/[^a-z0-9 ]/g, '').trim();
}
// For the recognise card: the right English plus three decoys drawn from the
// whole course vocabulary (COURSE.meaningPool) so choices stay varied. No decoy
// may mean the same thing as the answer.
function meaningOptions(item) {
    const bad = normalizeMeaning(item.prompt);
    const pool = (COURSE.meaningPool || P.items.map(x => x.prompt))
        .filter(m => m !== item.prompt && normalizeMeaning(m) !== bad);
    const picked = [];
    const used = new Set([bad]);
    const bag = pool.slice();
    for (let k = bag.length - 1; k > 0; k--) { const j = Math.floor(Math.random() * (k + 1)); [bag[k], bag[j]] = [bag[j], bag[k]]; }
    for (const m of bag) {
        const n = normalizeMeaning(m);
        if (used.has(n)) continue;           // no two decoys that read the same
        used.add(n); picked.push(m);
        if (picked.length === 3) break;
    }
    const opts = [item.prompt].concat(picked);
    for (let k = opts.length - 1; k > 0; k--) { const j = Math.floor(Math.random() * (k + 1)); [opts[k], opts[j]] = [opts[j], opts[k]]; }
    return opts;
}

// Tiles: the answer's kana (as a multiset) plus a few plausible decoys drawn
// from look-alikes and dakuten partners, shuffled.
function makeTiles(answer) {
    const chars = [...answer];
    const have = new Set(chars);
    const pool = [];
    chars.forEach(ch => {
        const g = COURSE.glyphs[ch];
        if (g) {
            (g.looksLike || []).forEach(x => { if (x.length === 1 && !have.has(x)) pool.push(x); });
            (g.voiced || []).forEach(x => { if (!have.has(x)) pool.push(x); });
            if (g.base && !have.has(g.base)) pool.push(g.base);
        }
    });
    const decoys = [];
    const want = Math.min(4, Math.max(2, Math.round(chars.length / 2)));
    const uniq = [...new Set(pool)];
    while (decoys.length < want && uniq.length) decoys.push(uniq.splice(Math.floor(Math.random() * uniq.length), 1)[0]);
    const tiles = chars.concat(decoys);
    for (let k = tiles.length - 1; k > 0; k--) { const j = Math.floor(Math.random() * (k + 1)); [tiles[k], tiles[j]] = [tiles[j], tiles[k]]; }
    return tiles;
}

function renderPracticeHome() {
    const main = el('div', {});
    main.appendChild(el('h1', {}, 'Practice'));
    main.appendChild(el('hr', {class: 'divider'}));
    main.appendChild(el('p', {class: 'lead'}, 'Pick a set and build each word from its kana. No timers, no streaks \u2014 miss as many as you like; the ones you miss just come round again.'));
    COURSE.practiceSets.forEach(set => {
        const prog = (state.practice && state.practice[set.id]) || {};
        const known = set.items.filter(it => prog[it.answer] === 'known').length;
        main.appendChild(el('button', {class: 'set-card', onclick: () => go('practice-' + set.id)},
            el('div', {class: 'set-main'},
                el('div', {class: 'set-title'}, set.title),
                set.blurb ? el('div', {class: 'set-blurb'}, set.blurb) : null),
            el('div', {class: 'set-count'}, known + ' / ' + set.items.length)));
    });
    return main;
}

function renderPractice(setId) {
    if (!P || P.setId !== setId) startPractice(setId);
    if (!P) return el('div', {}, 'Set not found.');
    const main = el('div', {class: 'practice'});
    if (P.i >= P.queue.length) {
        main.appendChild(el('h1', {}, P.title));
        main.appendChild(el('hr', {class: 'divider'}));
        main.appendChild(el('p', {class: 'lead'}, '\u2713 Set complete. Come back any time \u2014 it will remember where you were.'));
        main.appendChild(el('div', {class: 'practice-actions'},
            el('button', {class: 'btn primary', onclick: () => { startPractice(setId); render(); }}, 'Go again'),
            el('button', {class: 'btn', onclick: () => go('practice')}, 'All sets')));
        P = null;
        return main;
    }
    const item = practiceCurrentItem();
    const switchMode = m => { if (P.mode !== m) { startPractice(setId, m); render(); } };
    main.appendChild(el('div', {class: 'practice-top'},
        el('button', {class: 'nav-btn', onclick: () => go('practice')}, '\u2190 Sets'),
        el('div', {class: 'mode-switch'},
            el('button', {class: 'mode-build' + (P.mode === 'build' ? ' active' : ''), type: 'button',
                onclick: () => switchMode('build')}, 'Build'),
            el('button', {class: 'mode-recognise' + (P.mode === 'recognise' ? ' active' : ''), type: 'button',
                onclick: () => switchMode('recognise')}, 'Recognise')),
        el('span', {class: 'practice-progress'}, P.done + ' / ' + P.total)));
    const card = el('div', {class: 'practice-card'});
    const feedback = el('div', {class: 'card-feedback'});
    const controls = el('div', {class: 'practice-controls'});

    if (P.mode === 'recognise') {
        // See/hear the Japanese, choose the English.
        card.appendChild(el('div', {class: 'card-jp inline-jp'}, item.answer,
            el('button', {class: 'row-btn', type: 'button', title: 'Play audio',
                onclick: ev => playFromRow(ev.currentTarget, item.answer)}, svgSpeaker())));
        card.appendChild(el('div', {class: 'card-sub'}, 'What does this mean?'));
        card.appendChild(feedback);
        const opts = el('div', {class: 'option-list'});
        let answered = false;
        meaningOptions(item).forEach(text => {
            const o = el('button', {class: 'btn option', type: 'button', onclick: ev => {
                if (answered || P.revealed) return;
                if (text === item.prompt) {
                    answered = true;
                    opts.querySelectorAll('.option').forEach(b => b.disabled = true);
                    ev.currentTarget.classList.add('right');
                    feedback.textContent = FEEDBACK.correct; feedback.className = 'card-feedback ok';
                    practiceRecord(setId, item.answer, 'known'); speak(item.answer); showNext();
                } else {
                    ev.currentTarget.classList.add('wrong'); ev.currentTarget.disabled = true;
                    feedback.textContent = '\u261d Not that one \u2014 try again, or reveal.'; feedback.className = 'card-feedback off';
                }
            }}, text);
            opts.appendChild(o);
        });
        card.appendChild(opts);
        const reveal = el('button', {class: 'btn btn-reveal', type: 'button', onclick: () => {
            if (answered) return;
            P.revealed = true;
            opts.querySelectorAll('.option').forEach(b => { b.disabled = true; if (b.textContent === item.prompt) b.classList.add('right'); });
            feedback.textContent = 'Answer: ' + item.prompt; feedback.className = 'card-feedback';
            practiceRecord(setId, item.answer, 'learning');
            showNext(true);
        }}, 'Reveal');
        controls.appendChild(reveal);
        card.appendChild(controls);
        main.appendChild(card);
        return main;
    }

    // Build mode: see English (+ picture, if any), build the Japanese from tiles.
    if (item.image) {
        const img = el('img', {class: 'card-image', src: item.image, alt: item.prompt, loading: 'lazy', decoding: 'async'});
        img.addEventListener('error', () => img.remove());   // a broken URL just vanishes
        card.appendChild(img);
    }
    card.appendChild(el('div', {class: 'card-prompt', html: richText(item.prompt)}));
    const slots = el('div', {class: 'answer-slots inline-jp'});
    const paint = () => { slots.textContent = P.built.length ? P.built.join('') : '\u00a0'; };
    paint();
    card.appendChild(slots);
    card.appendChild(feedback);
    const tray = el('div', {class: 'tile-tray inline-jp'});
    const used = [];   // track which tile buttons are spent
    const tileChars = makeTiles(item.answer);
    tileChars.forEach(ch => {
        const t = el('button', {class: 'tile', type: 'button', onclick: () => {
            if (P.revealed) return;
            P.built.push(ch); used.push(t); t.disabled = true; paint(); feedback.textContent = '';
        }}, ch);
        tray.appendChild(t);
    });
    card.appendChild(tray);
    const back = el('button', {class: 'btn btn-back', type: 'button', onclick: () => {
        if (P.revealed || !P.built.length) return;
        P.built.pop(); const t = used.pop(); if (t) t.disabled = false; paint(); feedback.textContent = '';
    }}, '\u232b Back');
    const check = el('button', {class: 'btn primary btn-check', type: 'button', onclick: () => {
        if (P.revealed || !P.built.length) return;
        const verdict = checkAnswer(P.built.join(''), item.answer);
        feedback.textContent = FEEDBACK[verdict];
        feedback.className = 'card-feedback ' + (verdict === 'correct' ? 'ok' : 'off');
        if (verdict === 'correct') { practiceRecord(setId, item.answer, 'known'); speak(item.answer); showNext(); }
    }}, 'Check');
    const reveal = el('button', {class: 'btn btn-reveal', type: 'button', onclick: () => {
        P.revealed = true; P.built = [...item.answer]; paint();
        feedback.textContent = 'Answer: ' + item.answer; feedback.className = 'card-feedback';
        speak(item.answer);
        practiceRecord(setId, item.answer, 'learning');
        showNext(true);
    }}, 'Reveal');
    controls.appendChild(back); controls.appendChild(reveal); controls.appendChild(check);
    card.appendChild(controls);
    main.appendChild(card);

    function showNext(again) {
        // again=true (revealed) => requeue this item later in the session
        controls.querySelectorAll('button').forEach(b => b.disabled = true);
        const next = el('button', {class: 'btn primary btn-next', type: 'button', onclick: () => {
            if (again) P.queue.push(item); else P.done++;
            P.i++; P.built = []; P.revealed = false; render();
        }}, P.i + 1 >= P.queue.length && !again ? 'Finish \u2192' : 'Next \u2192');
        controls.appendChild(next);
    }
    return main;
}

// --- test hooks (no-ops in normal use) ---
function practiceMarkAgain() { if (P) { const it = P.queue[P.i]; P.queue.push(it); } }
function practiceDebugSetBuilt(s) { if (P) { P.built = [...s]; } }

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
