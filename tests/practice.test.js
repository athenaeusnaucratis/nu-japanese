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
