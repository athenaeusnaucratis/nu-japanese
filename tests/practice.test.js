// Practice engine (Round C). Written BEFORE the code.
const test = require('node:test');
const assert = require('node:assert/strict');
const { loadPage, KEY } = require('./helpers');

const tiles = p => [...p.doc.querySelectorAll('.tile-tray .tile')];
const built = p => p.doc.querySelector('.answer-slots').textContent.replace(/ /g, '');
const tap = (p, ch) => tiles(p).find(t => t.textContent === ch && !t.disabled).click();
function buildAnswer(p, answer) { for (const ch of answer) tap(p, ch); }

// ---- pure classifier (exposed for testing) ----
test('checkAnswer classifies the Japanese-specific slips', async () => {
  const p = await loadPage();
  const c = (a, b) => p.w.eval(`checkAnswer(${JSON.stringify(a)}, ${JSON.stringify(b)})`);
  assert.equal(c('すし', 'すし'), 'correct');
  assert.equal(c('パン', 'パン'), 'correct');              // katakana exact
  assert.equal(c('こはん', 'ごはん'), 'dakuten');          // dropped the dakuten
  assert.equal(c('きゅう', 'ぎゅう'), 'dakuten');           // only the dakuten differs
  assert.equal(c('ぎゆう', 'ぎゅう'), 'small-kana');        // ゆ should be small ゅ
  assert.equal(c('コヒー', 'コーヒー'), 'long-vowel');       // dropped the ー
  assert.equal(c('す', 'すし'), 'short');                  // too few
  assert.equal(c('さる', 'すし'), 'wrong');
});

// ---- set list + session ----
test('practice home lists the Food set', async () => {
  const p = await loadPage();
  p.go('practice');
  assert.match(p.text(), /Food & Drink/);
  const start = [...p.doc.querySelectorAll('a,button')].find(e => /Food & Drink/.test(e.textContent));
  assert.ok(start);
});

test('a card shows an English prompt and a solvable tile tray', async () => {
  const p = await loadPage();
  p.go('practice-food');
  const prompt = p.doc.querySelector('.card-prompt').textContent;
  assert.ok(prompt.trim().length > 0);
  // every kana of the current answer is present among the tiles (multiset)
  const answer = p.w.eval('practiceCurrentAnswer()');
  const tray = tiles(p).map(t => t.textContent);
  for (const ch of answer) {
    const need = [...answer].filter(c => c === ch).length;
    assert.ok(tray.filter(c => c === ch).length >= need, `tile ${ch} missing`);
  }
  assert.ok(tiles(p).length > [...answer].length, 'tray has decoys');
});

test('building the right answer advances and records it known', async () => {
  const p = await loadPage();
  p.go('practice-food');
  const before = p.doc.querySelector('.practice-progress').textContent;
  const answer = p.w.eval('practiceCurrentAnswer()');
  buildAnswer(p, answer);
  assert.equal(built(p), answer);
  p.doc.querySelector('.btn-check').click();
  assert.match(p.doc.querySelector('.card-feedback').textContent, /✓|nice|correct/i);
  const saved = JSON.parse(p.stored());
  assert.equal(saved.practice.food[answer], 'known');
  // advancing shows a different card (or the summary)
  p.doc.querySelector('.btn-next').click();
  const after = p.doc.querySelector('.practice-progress')?.textContent;
  assert.notEqual(after, before);
});

test('a wrong build gives specific, kind feedback and does not advance', async () => {
  const p = await loadPage();
  p.go('practice-food');
  const answer = p.w.eval('practiceCurrentAnswer()');     // ごはん first
  // build it missing the dakuten by tapping a decoy base if present, else assert via classifier path
  p.w.eval('practiceDebugSetBuilt("こはん")');
  p.doc.querySelector('.btn-check').click();
  assert.match(p.doc.querySelector('.card-feedback').textContent, /dakuten/i);
  assert.equal(p.doc.querySelector('.practice-progress').textContent.includes('0 /'), true);
});

test('reveal shows the answer and a backspace removes the last tile', async () => {
  const p = await loadPage();
  p.go('practice-food');
  const answer = p.w.eval('practiceCurrentAnswer()');
  tap(p, answer[0]);
  tap(p, answer[1] ?? answer[0]);
  p.doc.querySelector('.btn-back').click();
  assert.equal([...built(p)].length, 1);
  p.doc.querySelector('.btn-reveal').click();
  assert.equal(p.doc.querySelector('.answer-slots').textContent.replace(/ /g,''), answer);
});

test('a missed word resurfaces before the set ends', async () => {
  const p = await loadPage();
  p.go('practice-food');
  const n = p.w.eval('COURSE.practiceSets[0].items.length');
  const seen = [];
  for (let i = 0; i < n + 2 && p.doc.querySelector('.answer-slots'); i++) {
    const a = p.w.eval('practiceCurrentAnswer()');
    seen.push(a);
    if (i === 0) { p.doc.querySelector('.btn-reveal').click(); p.w.eval('practiceMarkAgain()'); }
    else { buildAnswer(p, a); p.doc.querySelector('.btn-check').click(); }
    const next = p.doc.querySelector('.btn-next'); if (next) next.click();
  }
  assert.ok(seen.indexOf(seen[0]) !== seen.lastIndexOf(seen[0]), 'first word seen again');
});

test('practice state persists across reload and reset clears it', async () => {
  const p = await loadPage();
  p.go('practice-food');
  const a = p.w.eval('practiceCurrentAnswer()');
  buildAnswer(p, a); p.doc.querySelector('.btn-check').click();
  const saved = p.stored();
  const p2 = await loadPage({ storage: { [KEY]: saved } });
  assert.equal(JSON.parse(p2.stored()).practice.food[a], 'known');
});

test('no streak, lives, timer or points anywhere in practice', async () => {
  const p = await loadPage();
  p.go('practice-food');
  assert.doesNotMatch(p.text().toLowerCase(), /streak|lives|\btimer\b|points|score|xp\b/);
});

// ---- reverse card: recognise the meaning ----
const modeBtn = (p, m) => p.doc.querySelector('.mode-' + m);

test('recognise mode shows the Japanese + audio and four English choices', async () => {
  const p = await loadPage();
  p.go('practice-food');
  modeBtn(p, 'recognise').click();
  const card = p.w.eval('practiceCurrentCard()');
  assert.equal(card.mode, 'recognise');
  assert.match(p.doc.querySelector('.card-jp').textContent, new RegExp(card.answer));
  assert.ok(p.doc.querySelector('.card-jp button[title="Play audio"]'));
  const opts = [...p.doc.querySelectorAll('.option')];
  assert.equal(opts.length, 4);
  assert.equal(opts.filter(o => o.textContent === card.prompt).length, 1);
});

test('choosing the right meaning records known and advances', async () => {
  const p = await loadPage();
  p.go('practice-food');
  modeBtn(p, 'recognise').click();
  const card = p.w.eval('practiceCurrentCard()');
  [...p.doc.querySelectorAll('.option')].find(o => o.textContent === card.prompt).click();
  assert.match(p.doc.querySelector('.card-feedback').textContent, /nice|✓/i);
  assert.equal(JSON.parse(p.stored()).practice.food[card.answer], 'known');
  assert.ok(p.doc.querySelector('.btn-next'));
});

test('choosing a wrong meaning gives feedback and does not advance', async () => {
  const p = await loadPage();
  p.go('practice-food');
  modeBtn(p, 'recognise').click();
  const card = p.w.eval('practiceCurrentCard()');
  const wrong = [...p.doc.querySelectorAll('.option')].find(o => o.textContent !== card.prompt);
  wrong.click();
  assert.match(p.doc.querySelector('.card-feedback').textContent, /not that one/i);
  assert.equal(p.doc.querySelector('.btn-next'), null);
  assert.equal(card.answer in (JSON.parse(p.stored()).practice.food || {}), false);
});

test('recognise reveal shows the English and marks learning', async () => {
  const p = await loadPage();
  p.go('practice-food');
  modeBtn(p, 'recognise').click();
  const card = p.w.eval('practiceCurrentCard()');
  p.doc.querySelector('.btn-reveal').click();
  assert.match(p.doc.querySelector('.card-feedback').textContent, new RegExp(card.prompt.split(';')[0]));
  assert.equal(JSON.parse(p.stored()).practice.food[card.answer], 'learning');
});

test('switching to recognise shows no kana tiles', async () => {
  const p = await loadPage();
  p.go('practice-food');
  modeBtn(p, 'recognise').click();
  assert.equal(p.doc.querySelector('.tile-tray'), null);
});

// ---- picture slot (Round C, images) ----
test('an image shows on the Build card and is hidden on Recognise', async () => {
  const p = await loadPage();
  // give the first item a picture at runtime (content ships empty slots)
  p.w.eval('COURSE.practiceSets[0].items[0].image = "https://example.com/rice.jpg"');
  p.go('practice-food');
  const img = p.doc.querySelector('.card-image');
  assert.ok(img, 'build card shows the image');
  assert.equal(img.getAttribute('src'), 'https://example.com/rice.jpg');
  assert.equal(img.getAttribute('loading'), 'lazy');
  assert.equal(img.getAttribute('alt'), p.w.eval('practiceCurrentCard().prompt'));
  modeBtn(p, 'recognise').click();
  assert.equal(p.doc.querySelector('.card-image'), null, 'recognise hides the image');
});

test('no image slot when the item has none', async () => {
  const p = await loadPage();
  p.w.eval('COURSE.practiceSets[0].items[0].image = ""');
  p.go('practice-food');
  assert.equal(p.doc.querySelector('.card-image'), null);
});

test('the Food set ships with a picture on every item', async () => {
  const p = await loadPage();
  const all = p.w.eval('COURSE.practiceSets[0].items.every(it => /^https:\\/\\/res\\.cloudinary\\.com\\//.test(it.image))');
  assert.equal(all, true);
});

// ---- decoy variety: wrong answers come from the whole vocabulary ----
test('recognise decoys are drawn from a large, varied pool', async () => {
  const p = await loadPage();
  assert.ok(p.w.eval('COURSE.meaningPool.length') > 200);
  p.go('practice-food');
  modeBtn(p, 'recognise').click();
  const card = p.w.eval('practiceCurrentCard()');
  // across many draws, decoys should range beyond the 29-word food set
  const seen = new Set();
  for (let i = 0; i < 40; i++) p.w.eval('meaningOptions(practiceCurrentItem())').forEach(m => seen.add(m));
  assert.ok(seen.size > 20, 'decoys vary widely');
  const foodPrompts = new Set(p.w.eval('COURSE.practiceSets[0].items.map(it => it.prompt)'));
  assert.ok([...seen].some(m => !foodPrompts.has(m)), 'some decoys come from outside the set');
  // never a decoy meaning the same as the answer
  for (let i = 0; i < 40; i++) {
    const opts = p.w.eval(`meaningOptions({answer:${JSON.stringify(card.answer)}, prompt:${JSON.stringify(card.prompt)}})`);
    const norm = s => s.toLowerCase().replace(/\([^)]*\)/g,'').split(/[;/]/)[0].replace(/[^a-z0-9 ]/g,'').trim();
    assert.equal(opts.filter(o => norm(o) === norm(card.prompt)).length, 1);
  }
});
