// Shared jsdom harness: build index.html once, then load it with chosen storage.
const { execFileSync } = require('node:child_process');
const fs = require('node:fs');
const os = require('node:os');
const path = require('node:path');
const { JSDOM } = require('jsdom');

const ROOT = path.resolve(__dirname, '..');
const KEY = 'jp_course_v1';
let builtPath = null;

function buildOnce() {
  if (builtPath) return builtPath;
  const dir = fs.mkdtempSync(path.join(os.tmpdir(), 'nujp-'));
  builtPath = path.join(dir, 'index.html');
  execFileSync('python3', ['-B', path.join(ROOT, 'src', 'build.py'), builtPath], { stdio: 'pipe' });
  return builtPath;
}

function legacyKeys() {
  return JSON.parse(fs.readFileSync(path.join(ROOT, 'src', 'legacy_keys.json'), 'utf8'));
}

// storage: {key: string} written to localStorage before any page script runs.
async function loadPage({ storage = {}, url = 'http://localhost/' } = {}) {
  const html = fs.readFileSync(buildOnce(), 'utf8');
  const spoken = [];
  const dom = new JSDOM(html, {
    runScripts: 'dangerously',
    url,
    beforeParse(w) {
      w.localStorage.clear();
      for (const k in storage) w.localStorage.setItem(k, storage[k]);
      w.scrollTo = () => {};
      w.SpeechSynthesisUtterance = function (text) { this.text = text; };
      w.speechSynthesis = {
        getVoices: () => [],
        cancel() {},
        speak(u) { spoken.push(u.text); if (u.onend) u.onend(); },
      };
    },
  });
  const w = dom.window;
  if (w.document.readyState !== 'complete') {
    await new Promise(r => w.addEventListener('load', r));
  }
  return {
    w,
    doc: w.document,
    spoken,
    go: v => w.eval(`go(${JSON.stringify(v)})`),
    // Parse in Node's realm: objects built inside jsdom fail deepStrictEqual on prototype.
    state: () => JSON.parse(w.eval('JSON.stringify(state)')),
    stored: k => w.localStorage.getItem(k === undefined ? KEY : k),
    text: () => w.document.getElementById('content').textContent,
  };
}

module.exports = { loadPage, legacyKeys, buildOnce, KEY };
