"""Content-level tests (stdlib only). Run: npm test  (or python3 -m unittest discover -s tests)

The speak-text fixture below was written by hand BEFORE speak_text() existed.
"""
import importlib.util
import json
import os
import sys
import unittest

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(ROOT, 'src')
sys.path.insert(0, SRC)


def load_build():
    spec = importlib.util.spec_from_file_location('build', os.path.join(SRC, 'build.py'))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


build = load_build()

# ---------------------------------------------------------------- speak text
# jp cell -> text handed to speechSynthesis.
SPEAK_MUST_PASS = {
    # kanji / kana pairs: speak the kana side only
    '日本人 / にほんじん': 'にほんじん', '学生 / がくせい': 'がくせい',
    '会社員 / かいしゃいん': 'かいしゃいん', '先生 / せんせい': 'せんせい',
    '医者 / いしゃ': 'いしゃ', '何歳 / なんさい': 'なんさい', '本 / ほん': 'ほん',
    '日本 / にほん': 'にほん', 'ゼロ / 零': 'ゼロ', 'コック / 料理人': 'コック',
    '月曜日 / げつようび': 'げつようび', '火曜日 / かようび': 'かようび',
    '水曜日 / すいようび': 'すいようび', '木曜日 / もくようび': 'もくようび',
    '金曜日 / きんようび': 'きんようび', '土曜日 / どようび': 'どようび',
    '日曜日 / にちようび': 'にちようび', '今日 / きょう': 'きょう',
    '明日 / あした': 'あした', '昨日 / きのう': 'きのう',
    '今週 / こんしゅう': 'こんしゅう', '来週 / らいしゅう': 'らいしゅう',
    '先週 / せんしゅう': 'せんしゅう',
    # counters: kana side, tilde dropped
    '〜人 / 〜にん': 'にん', '〜枚 / 〜まい': 'まい', '〜本 / 〜ほん': 'ほん',
    '〜匹 / 〜ひき': 'ひき', '〜個 / 〜こ': 'こ', '〜回 / 〜かい': 'かい',
    '〜時間 / 〜じかん': 'じかん',
    # kana / kana alternatives: speak both, with a pause
    'なん / なに': 'なん、なに', 'なに / なん': 'なに、なん', 'いい / よい': 'いい、よい',
    'うち / いえ': 'うち、いえ', 'いえ / うち': 'いえ、うち', 'ばん / よる': 'ばん、よる',
    'なぜ / どうして': 'なぜ、どうして', 'でんわ / けいたい': 'でんわ、けいたい',
    'ぎゅうにゅう / ミルク': 'ぎゅうにゅう、ミルク',
    'おはよう / おはようございます': 'おはよう、おはようございます',
    'ありがとう / ありがとうございます': 'ありがとう、ありがとうございます',
    'ちち / おとうさん': 'ちち、おとうさん', 'はは / おかあさん': 'はは、おかあさん',
    'あに / おにいさん': 'あに、おにいさん', 'あね / おねえさん': 'あね、おねえさん',
    # placeholders and grammar marks
    'この [noun]': 'この', 'その [noun]': 'その', 'あの [noun]': 'あの', 'どの [noun]': 'どの',
    'きれい(な)': 'きれい', 'しずか(な)': 'しずか', 'ざんねん(な)': 'ざんねん',
    'にぎやか(な)': 'にぎやか', 'ゆうめい(な)': 'ゆうめい', 'しんせつ(な)': 'しんせつ',
    'げんき(な)': 'げんき', 'ひま(な)': 'ひま', 'べんり(な)': 'べんり', 'ふべん(な)': 'ふべん',
    'すき(な)': 'すき', 'きらい(な)': 'きらい', 'じょうず(な)': 'じょうず', 'へた(な)': 'へた',
    'たいせつ(な)': 'たいせつ', 'しんぱい(な)': 'しんぱい',
    'この〜、その〜、あの〜': 'この、その、あの', 'どれ、どの〜': 'どれ、どの',
    'いちがつ…じゅうにがつ': 'いちがつ、じゅうにがつ',
}
# Things the rule must leave alone (controls and near-misses).
SPEAK_MUST_NOT_CHANGE = [
    'いち、に、さん、よん、ご', 'ひとつ、ふたつ、みっつ', 'これ、それ、あれ',
    'ごぜん 7じ', 'ごご 3じはん', 'おなまえは？', 'すし', '一', 'アイスクリーム',
    'おとこの ひと', 'はじめまして', 'どうぞよろしくおねがいします',
    '1/2',            # no spaces around the slash: not an alternative list
]
SPEAK_EDGE = {
    '一 / 二': '一',                                   # no kana side: first part
    '日本人 / にほんじん / ニホンジン': 'にほんじん、ニホンジン',
    '[name] です': 'です',
}
# Judgement calls, pinned so a change is deliberate.
SPEAK_UNSURE = {
    '〜つ': 'つ',          # lone counter; examples might serve better
}


class SpeakText(unittest.TestCase):
    def check(self, cases):
        bad = {jp: (build.speak_text(jp), want) for jp, want in cases.items()
               if build.speak_text(jp) != want}
        self.assertEqual(bad, {}, 'got / wanted')

    def test_must_pass(self):
        self.check(SPEAK_MUST_PASS)

    def test_must_not_change(self):
        self.check({jp: jp for jp in SPEAK_MUST_NOT_CHANGE})

    def test_edges(self):
        self.check(SPEAK_EDGE)

    def test_unsure_pinned(self):
        self.check(SPEAK_UNSURE)

    def test_every_course_cell_is_covered_or_plain(self):
        """Any cell with a separator must be in the fixture, so new content gets a decision."""
        known = set(SPEAK_MUST_PASS) | set(SPEAK_MUST_NOT_CHANGE) | set(SPEAK_UNSURE)
        missing = sorted({r[0] for r in build.all_vocab_rows()
                          if any(c in r[0] for c in '/[]→…〜～()') and r[0] not in known})
        self.assertEqual(missing, [])


# ----------------------------------------------------------- IDs + migration
class StableIds(unittest.TestCase):
    def setUp(self):
        self.course = build.make_course()

    def vocab_sections(self):
        for w in self.course['weeks']:
            yield from (s for s in w['sections'] if s['type'] == 'vocab')
        for a in self.course['appendices']:
            yield from (s for s in a['sections'] if s['type'] == 'vocab')

    def test_every_vocab_row_has_id_and_speak(self):
        for s in self.vocab_sections():
            self.assertEqual(len(s['ids']), len(s['rows']))
            self.assertEqual(len(s['speak']), len(s['rows']))
            for r, i in zip(s['rows'], s['ids']):
                self.assertEqual(i, 'v:' + r[0] + '|' + r[1])

    def test_legacy_table_is_complete_and_frozen(self):
        with open(os.path.join(SRC, 'legacy_keys.json'), encoding='utf-8') as f:
            legacy = json.load(f)
        self.assertEqual(len(legacy), 538)
        self.assertEqual(sum(k.startswith('w') for k in legacy), 273)
        self.assertEqual(sum(k.startswith('appx-') for k in legacy), 265)
        self.assertEqual(legacy['w10-s2-v6'], 'v:はん|han')   # was はんぶん / はん before 35f3e69
        self.assertEqual(legacy['w1-s6-v8'], 'v:ねこ|neko')
        self.assertEqual(legacy['appx-vocab-index-s21-v13'], 'v:ねこ|neko')
        self.assertEqual(self.course['legacyKeys'], legacy)

    def test_legacy_targets_resolve(self):
        """Every old key lands on a current word, an alias, or a deliberately retired row."""
        current = {i for s in self.vocab_sections() for i in s['ids']}
        aliases = self.course['idAliases']
        for target in aliases.values():
            self.assertIn(target, current)
        retired = set(build.RETIRED_IDS)
        dangling = sorted({v for v in self.course['legacyKeys'].values()
                           if v not in current and v not in aliases and v not in retired})
        self.assertEqual(dangling, [])

    def test_retired_ids_are_only_the_w9_rule_rows(self):
        self.assertEqual(len(build.RETIRED_IDS), 5)
        self.assertTrue(all('→' in i for i in build.RETIRED_IDS))


# ------------------------------------------------------------- single sources
class Structure(unittest.TestCase):
    def setUp(self):
        self.course = build.make_course()

    def test_w9_rules_are_a_table(self):
        w9 = next(w for w in self.course['weeks'] if w['num'] == 9)
        self.assertFalse(any(s['type'] == 'vocab' and any('→' in r[0] for r in s['rows'])
                             for s in w9['sections']))
        tables = [s for s in w9['sections'] if s['type'] == 'table']
        self.assertEqual(len(tables), 1)
        self.assertEqual(len(tables[0]['rows']), 5)

    def test_kanji_single_source(self):
        from content_kanji import KANJI
        self.assertEqual(len(KANJI), 100)
        self.assertEqual(len({k[0] for k in KANJI}), 100)
        week_items = [tuple(it) for w in self.course['weeks'] for s in w['sections']
                      if s['type'] == 'kanji-grid' for it in s['items']]
        appx = next(a for a in self.course['appendices'] if a['id'] == 'kanji-100')
        appx_items = [tuple(it) for s in appx['sections'] if s['type'] == 'kanji-grid'
                      for it in s['items']]
        self.assertEqual(week_items, [tuple(k) for k in KANJI])
        self.assertEqual(appx_items, [tuple(k) for k in KANJI])

    def test_no_script_breakout_in_json(self):
        html = build.render_html()
        start = html.index('const COURSE = ')
        blob = html[start:html.index('\n', start)]
        self.assertNotIn('</', blob)


if __name__ == '__main__':
    unittest.main()
