// UI behaviour of the built page. Written BEFORE the schema-2 code.
const test = require('node:test');
const assert = require('node:assert/strict');
const { loadPage, legacyKeys, KEY } = require('./helpers');

const LEGACY = legacyKeys();
const keyFor = (id, prefix) => Object.keys(LEGACY).find(k => LEGACY[k] === id && k.startsWith(prefix));

// A real-shape pre-schema blob: what every existing user has today.
function oldBlob(knownVocab, extra = {}) {
  return JSON.stringify(Object.assign({
    view: 'welcome', weekStatus: { 1: 'complete', 2: 'started' },
    knownVocab, hideEn: false, hideRoma: false, theme: null,
  }, extra));
}

// ------------------------------------------------------------- migration
test('migration: blob without schema moves stars to stable IDs', async () => {
  const w5 = Object.keys(LEGACY).find(k => k.startsWith('w5-'));
  const raw = oldBlob({ 'w1-s6-v8': true, 'w10-s2-v6': true, [w5]: true });
  const p = await loadPage({ storage: { [KEY]: raw } });
  const s = p.state();
  assert.equal(s.schema, 2);
  assert.equal(s.known['v:ねこ|neko'], true);
  assert.equal(s.known['v:はん|han'], true);
  assert.equal(s.known[LEGACY[w5]], true);
  assert.equal(Object.keys(s.known).length, 3);
  assert.deepEqual(s.weekStatus, { 1: 'complete', 2: 'started' });
});

test('migration: backup written, old field kept for rollback', async () => {
  const raw = oldBlob({ 'w1-s6-v8': true });
  const p = await loadPage({ storage: { [KEY]: raw } });
  p.go('week-1');                                   // triggers a save
  assert.equal(p.stored(KEY + '_bak'), raw);
  const saved = JSON.parse(p.stored());
  assert.deepEqual(saved.knownVocab, { 'w1-s6-v8': true });
  assert.equal(saved.schema, 2);
  assert.equal(saved.known['v:ねこ|neko'], true);
});

test('migration: true anywhere wins over false elsewhere; false alone is dropped', async () => {
  const raw = oldBlob({
    'w1-s6-v8': true, 'appx-vocab-index-s21-v13': false,     // ねこ: true + false
    [keyFor('v:いぬ|inu', 'w1-')]: false,                     // いぬ: false only
  });
  const s = (await loadPage({ storage: { [KEY]: raw } })).state();
  assert.equal(s.known['v:ねこ|neko'], true);
  assert.equal('v:いぬ|inu' in s.known, false);
});

test('migration: unknown keys are kept aside, not applied', async () => {
  const s = (await loadPage({ storage: { [KEY]: oldBlob({ 'zz-unknown': true }) } })).state();
  assert.deepEqual(s.known, {});
  assert.deepEqual(s.legacyUnmapped, { 'zz-unknown': true });
});

test('migration: second load is a no-op', async () => {
  const first = await loadPage({ storage: { [KEY]: oldBlob({ 'w1-s6-v8': true }) } });
  first.go('week-1');
  const migrated = first.stored();
  const second = await loadPage({ storage: { [KEY]: migrated, [KEY + '_bak']: 'sentinel' } });
  assert.deepEqual(second.state().known, { 'v:ねこ|neko': true });
  second.go('week-2');
  assert.equal(second.stored(KEY + '_bak'), 'sentinel');
});

test('corrupted storage is never overwritten', async () => {
  const p = await loadPage({ storage: { [KEY]: '{not json' } });
  p.go('week-1');                                   // used to save defaults here
  p.go('week-2');
  assert.equal(p.stored(), '{not json');
  assert.match(p.text(), /couldn.t be read/i);
});

test('fresh visitor gets schema 2 without migration', async () => {
  const p = await loadPage();
  p.go('week-1');
  const saved = JSON.parse(p.stored());
  assert.equal(saved.schema, 2);
  assert.equal(p.stored(KEY + '_bak'), null);
});

// ---------------------------------------------------------------- counts
test('dashboard: total = unique starrable words; stale IDs not counted', async () => {
  const blob = JSON.stringify({ schema: 2, known: { 'v:ねこ|neko': true, 'v:gone|gone': true }, weekStatus: {} });
  const p = await loadPage({ storage: { [KEY]: blob } });
  const ids = p.w.eval(`[...new Set([].concat(
      ...COURSE.weeks.map(w => w.sections), ...COURSE.appendices.map(a => a.sections))
      .filter(s => s.type === 'vocab').flatMap(s => s.ids))].length`);
  const stats = [...p.doc.querySelectorAll('.stat .n')].map(n => n.textContent);
  assert.equal(stats[1], '1');            // known
  assert.equal(stats[2], String(ids));    // total
  assert.equal(ids, 431);
});

// ---------------------------------------------------------------- toggle
test('star: same word on one page stays in sync; unstar deletes', async () => {
  const p = await loadPage();
  p.go('appx-vocab-index');
  const rows = () => [...p.doc.querySelectorAll('tr[data-vid="v:さかな|sakana"]')];
  assert.equal(rows().length, 2);
  rows()[0].querySelector('button[title="Mark known"]').click();
  assert.ok(rows().every(r => r.classList.contains('known')));
  assert.equal(p.state().known['v:さかな|sakana'], true);
  const counts = [...p.doc.querySelectorAll('.vocab-toolbar .count')].map(c => c.textContent);
  assert.equal(counts.filter(c => c.startsWith('1 /')).length, 2);
  rows()[1].querySelector('button[title="Mark known"]').click();
  assert.ok(rows().every(r => !r.classList.contains('known')));
  assert.equal('v:さかな|sakana' in p.state().known, false);
});

// ---------------------------------------------------------------- speech
test('speaker speaks the kana side, not the display cell', async () => {
  const p = await loadPage();
  p.go('week-4');
  const row = p.doc.querySelector('tr[data-vid="v:日本人 / にほんじん|nihon-jin"]');
  row.querySelector('button[title="Play audio"]').click();
  assert.deepEqual(p.spoken, ['にほんじん']);
});

// --------------------------------------------------------------- content
test('no literal entities in any view; W9 rules render as a table', async () => {
  const p = await loadPage();
  const views = ['welcome', 'resources', ...Array.from({ length: 12 }, (_, i) => 'week-' + (i + 1)),
    ...p.w.eval('COURSE.appendices.map(a => "appx-" + a.id)')];
  for (const v of views) {
    p.go(v);
    assert.doesNotMatch(p.text(), /&(?:[a-z]+|#\d+);/, v);
  }
  p.go('week-9');
  const vocabCells = [...p.doc.querySelectorAll('table.vocab td.jp-cell')].map(td => td.textContent);
  assert.equal(vocabCells.some(t => t.includes('→')), false);
  assert.ok([...p.doc.querySelectorAll('table td')].some(td => td.textContent.includes('う, つ, る → って')));
});
