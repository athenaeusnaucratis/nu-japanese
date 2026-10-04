// Detail sheet (Round B1, batch 1). Written BEFORE the sheet code.
const test = require('node:test');
const assert = require('node:assert/strict');
const { loadPage } = require('./helpers');

const cell = (p, ch) => [...p.doc.querySelectorAll('.kana-cell')].find(c => c.querySelector('.glyph')?.textContent === ch);
const sheet = p => p.doc.getElementById('glyph-sheet');
const isOpen = p => !!sheet(p) && !sheet(p).hidden;

test('kana cells are buttons; tap plays the sound and opens the sheet', async () => {
  const p = await loadPage();
  p.go('appx-hiragana');
  const a = cell(p, 'あ');
  assert.equal(a.tagName, 'BUTTON');
  a.click();
  assert.deepEqual(p.spoken, ['あ']);
  assert.ok(isOpen(p));
  const s = sheet(p);
  assert.equal(s.getAttribute('role'), 'dialog');
  assert.equal(s.hasAttribute('aria-modal'), false);          // non-modal
  assert.equal(s.querySelector('.sheet-glyph').textContent, 'あ');
  assert.ok(s.querySelector('.sheet-hook').textContent.length > 10);
  assert.match(s.querySelector('.sheet-origin').textContent, /安/);
  assert.match(s.querySelector('.sheet-example').textContent, /あお/);
});

test('next tap updates the same sheet; grid stays usable', async () => {
  const p = await loadPage();
  p.go('appx-hiragana');
  cell(p, 'あ').click();
  cell(p, 'い').click();
  assert.equal(p.doc.querySelectorAll('#glyph-sheet').length, 1);
  assert.equal(sheet(p).querySelector('.sheet-glyph').textContent, 'い');
  assert.deepEqual(p.spoken, ['あ', 'い']);
});

test('look-alike button opens that character', async () => {
  const p = await loadPage();
  p.go('appx-hiragana');
  cell(p, 'さ').click();
  const btn = [...sheet(p).querySelectorAll('.sheet-alike button')].find(b => b.textContent.includes('ち'));
  assert.ok(btn, 'ち listed as a look-alike of さ');
  btn.click();
  assert.equal(sheet(p).querySelector('.sheet-glyph').textContent, 'ち');
});

test('voiced cell shows its base + mark and links back', async () => {
  const p = await loadPage();
  p.go('appx-hiragana');
  cell(p, 'が').click();
  const s = sheet(p);
  assert.equal(s.querySelector('.sheet-glyph').textContent, 'が');
  // base chip shows "か ka"; then the mark
  assert.equal(s.querySelector('.sheet-base .glyph-chip .g').textContent, 'か');
  assert.match(s.querySelector('.sheet-base').textContent, /\+\s*゛/);
  s.querySelector('.sheet-base button').click();
  assert.equal(s.querySelector('.sheet-glyph').textContent, 'か');
  assert.ok([...s.querySelectorAll('.sheet-voiced button')].some(b => b.textContent.includes('が')));
});

test('Esc and ✕ close; focus returns to the cell that opened it', async () => {
  const p = await loadPage();
  p.go('appx-hiragana');
  const k = cell(p, 'か');
  k.focus(); k.click();
  sheet(p).querySelector('.sheet-close').focus();
  p.doc.dispatchEvent(new p.w.KeyboardEvent('keydown', { key: 'Escape', bubbles: true }));
  assert.equal(isOpen(p), false);
  assert.equal(p.doc.activeElement, k);
  k.click();
  assert.ok(isOpen(p));
  sheet(p).querySelector('.sheet-close').click();
  assert.equal(isOpen(p), false);
  assert.equal(p.doc.activeElement, k);
});

test('sheet respects "Hide readings" on the grid that opened it', async () => {
  const p = await loadPage();
  p.go('appx-hiragana');
  const grid = cell(p, 'あ').closest('.kana-grid');
  grid.previousElementSibling.querySelector('button').click();     // Hide readings
  cell(p, 'あ').click();
  const roma = sheet(p).querySelector('.sheet-roma');
  assert.ok(roma.classList.contains('concealed'));
  roma.click();
  assert.equal(roma.classList.contains('concealed'), false);
});

test('katakana opens the sheet; origin says "part of"', async () => {
  const p = await loadPage();
  p.go('appx-katakana');
  cell(p, 'ア').click();
  assert.deepEqual(p.spoken, ['ア']);
  assert.ok(isOpen(p));
  assert.match(sheet(p).querySelector('.sheet-origin').textContent, /part of the kanji 阿/);
  // hiragana keeps its own wording
  p.go('appx-hiragana');
  cell(p, 'あ').click();
  assert.match(sheet(p).querySelector('.sheet-origin').textContent, /Simplified from the kanji 安/);
});

test('look-alike outside the course is shown but not tappable', async () => {
  const p = await loadPage();
  p.go('appx-katakana');
  cell(p, 'エ').click();
  const chips = [...sheet(p).querySelectorAll('.sheet-alike .glyph-chip')];
  const ko = chips.find(c => c.textContent.includes('工'));
  assert.ok(ko);
  assert.notEqual(ko.tagName, 'BUTTON');
});

test('ン has no origin line; ヲ has no example', async () => {
  const p = await loadPage();
  p.go('appx-katakana');
  cell(p, 'ン').click();
  assert.equal(sheet(p).querySelector('.sheet-origin'), null);
  cell(p, 'ヲ').click();
  assert.equal(sheet(p).querySelector('.sheet-example'), null);
});

test('leaving the page closes the sheet', async () => {
  const p = await loadPage();
  p.go('appx-hiragana');
  cell(p, 'あ').click();
  p.go('week-1');
  assert.equal(isOpen(p), false);
});

// ------------------------------------------------------------- kanji (batch 3)
const card = (p, k) => [...p.doc.querySelectorAll('.kanji-card')].find(c => c.querySelector('.k')?.textContent === k);

test('kanji card is a button: speaks and opens the sheet', async () => {
  const p = await loadPage();
  p.go('week-11');
  const c = card(p, '山');
  assert.equal(c.tagName, 'BUTTON');
  c.click();
  assert.deepEqual(p.spoken, ['山']);
  const s = sheet(p);
  assert.ok(isOpen(p));
  assert.equal(s.querySelector('.sheet-glyph').textContent, '山');
  assert.match(s.querySelector('.sheet-meaning').textContent, /mountain/);
  assert.match(s.querySelector('.sheet-readings').textContent, /yama/);
  assert.ok(s.querySelector('.sheet-drawing svg'), 'pictograph drawing shown');
  assert.ok(s.querySelector('.sheet-origin'));
});

test('compound kanji lists its parts; a part that is itself a kanji is tappable', async () => {
  const p = await loadPage();
  p.go('week-12');
  card(p, '休').click();
  const parts = [...sheet(p).querySelectorAll('.sheet-parts .glyph-chip')];
  const tree = parts.find(c => c.textContent.includes('木'));
  assert.ok(tree);
  assert.equal(tree.tagName, 'BUTTON');
  tree.click();
  assert.equal(sheet(p).querySelector('.sheet-glyph').textContent, '木');
  assert.ok(sheet(p).querySelector('.sheet-origin'));
});

test('non-pictograph kanji: memory hook, no origin, no drawing', async () => {
  const p = await loadPage();
  p.go('appx-kanji-100');
  card(p, '何').click();
  const s = sheet(p);
  assert.ok(s.querySelector('.sheet-hook'));
  assert.equal(s.querySelector('.sheet-origin'), null);
  assert.equal(s.querySelector('.sheet-drawing'), null);
});
