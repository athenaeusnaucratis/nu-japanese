"""Glyph data for the detail sheet (Round B1). Written BEFORE content_glyphs.py.

Batch 1: hiragana. Batch 2: katakana (tests extended before the data existed).
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from test_content import build  # noqa: E402  (loads src/build.py)

HIRAGANA_BASE = list('あいうえおかきくけこさしすせそたちつてとなにぬねの'
                     'はひふへほまみむめもやゆよらりるれろわをん')
HIRAGANA_VOICED = list('がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ')
KATAKANA_BASE = list('アイウエオカキクケコサシスセソタチツテトナニヌネノ'
                     'ハヒフヘホマミムメモヤユヨラリルレロワヲン')
KATAKANA_VOICED = list('ガギグゲゴザジズゼゾダヂヅデドバビブベボパピプペポ')
BASE = HIRAGANA_BASE + KATAKANA_BASE
VOICED = HIRAGANA_VOICED + KATAKANA_VOICED
NO_ORIGIN = {'ン'}          # origin disputed: shown without one
NO_EXAMPLE_WORD = {'を', 'ヲ'}  # particle only / not used in modern words


def grid_glyphs(course, appendix_id=None):
    out = []
    for w in course['weeks']:
        for s in w['sections']:
            if s['type'] == 'kana':
                out += [c[0] for row in s['rows'] for c in row if c]
    for a in course['appendices']:
        for s in a['sections']:
            if s['type'] == 'kana':
                out += [c[0] for row in s['rows'] for c in row if c]
    return out


def is_hiragana(ch):
    return 'ぁ' <= ch <= 'ゟ'


class Coverage(unittest.TestCase):
    def setUp(self):
        self.course = build.make_course()
        self.g = self.course['glyphs']

    def test_counts(self):
        self.assertEqual((len(HIRAGANA_BASE), len(KATAKANA_BASE)), (46, 46))
        self.assertEqual((len(HIRAGANA_VOICED), len(KATAKANA_VOICED)), (25, 25))

    def test_every_kana_in_any_grid_has_a_record(self):
        missing = sorted({c for c in grid_glyphs(self.course) if c not in self.g})
        self.assertEqual(missing, [])
        self.assertEqual(len({c for c in grid_glyphs(self.course)}), 142)

    def test_base_records_are_complete(self):
        for ch in BASE:
            r = self.g[ch]
            with self.subTest(ch=ch):
                self.assertTrue(r['romaji'])
                self.assertTrue(r['hook'].strip())
                self.assertLessEqual(len(r['hook']), 140, 'hooks are one-liners')
                self.assertEqual(r['script'], 'hiragana' if is_hiragana(ch) else 'katakana')
                if ch in NO_ORIGIN:
                    self.assertNotIn('origin', r)
                else:
                    self.assertEqual(len(r['origin']), 1, 'origin is the source kanji')
                if 'example' in r:
                    jp, reading, en = r['example']
                    self.assertTrue(reading and en)
                    if ch not in NO_EXAMPLE_WORD:
                        self.assertIn(ch, jp)
                else:
                    self.assertIn(ch, NO_EXAMPLE_WORD)

    def test_katakana_hooks_differ_from_hiragana(self):
        hira = {self.g[c]['hook'] for c in HIRAGANA_BASE}
        self.assertFalse(hira & {self.g[c]['hook'] for c in KATAKANA_BASE})

    def test_romaji_matches_the_chart(self):
        chart = {c[0]: c[1] for w in self.course['weeks'] for s in w['sections']
                 if s['type'] == 'kana' for row in s['rows'] for c in row if c}
        appx = {c[0]: c[1] for a in self.course['appendices'] for s in a['sections']
                if s['type'] == 'kana' for row in s['rows'] for c in row if c}
        chart = {**appx, **chart}
        for ch in BASE + VOICED:
            self.assertEqual(self.g[ch]['romaji'], chart[ch], ch)


class Voicing(unittest.TestCase):
    def setUp(self):
        self.g = build.make_course()['glyphs']

    def test_voiced_records_point_to_their_base(self):
        # must pass: が -> か + ゛ ; ぱ -> は + ゜
        self.assertEqual((self.g['が']['base'], self.g['が']['mark']), ('か', '゛'))
        self.assertEqual((self.g['ぱ']['base'], self.g['ぱ']['mark']), ('は', '゜'))
        self.assertEqual((self.g['ぢ']['base'], self.g['ぢ']['mark']), ('ち', '゛'))
        self.assertEqual((self.g['ガ']['base'], self.g['ガ']['mark']), ('カ', '゛'))
        self.assertEqual((self.g['ポ']['base'], self.g['ポ']['mark']), ('ホ', '゜'))
        for ch in VOICED:
            self.assertIn(ch, self.g[self.g[ch]['base']]['voiced'], ch)

    def test_base_voiced_lists(self):
        self.assertEqual(self.g['は']['voiced'], ['ば', 'ぱ'])
        self.assertEqual(self.g['か']['voiced'], ['が'])
        # must fail cases: no voicing for these
        self.assertEqual(self.g['ハ']['voiced'], ['バ', 'パ'])
        for ch in 'あなまやらわをんアナマヤラワヲン':
            self.assertEqual(self.g[ch]['voiced'], [], ch)

    def test_voiced_have_no_hook_of_their_own(self):
        for ch in VOICED:
            self.assertNotIn('hook', self.g[ch], ch)


class LookAlikes(unittest.TestCase):
    def setUp(self):
        self.g = build.make_course()['glyphs']

    def test_symmetric(self):
        for ch, r in self.g.items():
            for other in r['looksLike']:
                if other in self.g:
                    self.assertIn(ch, self.g[other]['looksLike'], (ch, other))

    def test_known_pairs(self):
        # must pass
        for a, b in [('さ', 'ち'), ('さ', 'き'), ('ぬ', 'め'), ('る', 'ろ'), ('い', 'り'),
                     ('れ', 'わ'), ('ね', 'れ'), ('は', 'ほ'), ('あ', 'お'),
                     ('シ', 'ツ'), ('ソ', 'ン'), ('ク', 'ケ'), ('ク', 'タ'), ('ウ', 'ワ'),
                     ('ユ', 'コ'), ('ナ', 'メ'), ('エ', '工'), ('カ', '力'), ('ニ', '二'),
                     ('ロ', '口'), ('へ', 'ヘ'), ('り', 'リ')]:
            self.assertIn(b, self.g[a]['looksLike'], (a, b))
        # must fail: not look-alikes
        for a, b in [('あ', 'ん'), ('の', 'め'), ('か', 'さ'), ('シ', 'ア'), ('ツ', 'ン')]:
            self.assertNotIn(b, self.g[a]['looksLike'], (a, b))

    def test_no_self_reference_and_single_chars(self):
        for ch, r in self.g.items():
            self.assertNotIn(ch, r['looksLike'])
            self.assertTrue(all(len(x) == 1 for x in r['looksLike']))


if __name__ == '__main__':
    unittest.main()


# ------------------------------------------------------------------ kanji (batch 3)
import xml.etree.ElementTree as ET  # noqa: E402

FIXTURES = os.path.join(os.path.dirname(__file__), 'fixtures')
# Picture-origin kanji that get a drawing. Pinned: adding one is a decision.
PICTOGRAPHS = set('日月火水木山川田口目耳手人子女大雨魚犬車')
# The only kanji allowed an "Origin" line: the pictographs above plus a few
# whose origin is textbook-standard. Everything else is labelled "memory hook".
ORIGIN_OK = PICTOGRAPHS | set('一二三上下本立生行母')
# KRADFILE uses stand-in characters for elements outside JIS X 0208.
KRAD_STANDIN = {'亻': '化', '刂': '刈', '艹': '艾', '辶': '込', '⺌': '尚', '灬': '杰', '罒': '買'}


def kradfile():
    out = {}
    with open(os.path.join(FIXTURES, 'kradfile_subset.txt'), encoding='utf-8') as f:
        for line in f:
            if line.startswith('#') or ' : ' not in line:
                continue
            k, v = line.rstrip('\n').split(' : ', 1)
            out[k] = set(v.split())
    return out


def part_ok(krad, kanji, part):
    """A part is backed if KRADFILE lists it (or its stand-in) for the kanji,
    or if every component of the part also appears in the kanji."""
    comps = krad[kanji]
    return KRAD_STANDIN.get(part, part) in comps or (part in krad and krad[part] <= comps)


class Kanji(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        from content_kanji import KANJI
        cls.KANJI = KANJI
        cls.g = build.make_course()['glyphs']
        cls.krad = kradfile()

    def test_every_kanji_has_a_record(self):
        for glyph, meaning, info in self.KANJI:
            r = self.g.get(glyph)
            with self.subTest(k=glyph):
                self.assertIsNotNone(r)
                self.assertEqual(r['script'], 'kanji')
                self.assertEqual(r['meaning'], meaning)
                self.assertEqual(r['readings'], info)
                self.assertTrue(r['hook'].strip())
                self.assertLessEqual(len(r['hook']), 160)

    def test_parts_are_backed_by_kradfile(self):
        for glyph, r in self.g.items():
            if r.get('script') != 'kanji':
                continue
            for part, meaning in r.get('parts', []):
                with self.subTest(k=glyph, part=part):
                    self.assertTrue(meaning)
                    self.assertTrue(part_ok(self.krad, glyph, part), f'{part} not a component of {glyph}')

    def test_part_rule_rejects_near_misses(self):
        # must pass
        self.assertTrue(part_ok(self.krad, '休', '亻'))     # via stand-in 化
        self.assertTrue(part_ok(self.krad, '休', '木'))
        self.assertTrue(part_ok(self.krad, '時', '寺'))     # 寺 = 土 寸, both in 時
        self.assertTrue(part_ok(self.krad, '話', '舌'))
        # must fail
        self.assertFalse(part_ok(self.krad, '休', '口'))
        self.assertFalse(part_ok(self.krad, '男', '木'))
        self.assertFalse(part_ok(self.krad, '時', '寸口'[1]))
        self.assertFalse(part_ok(self.krad, '読', '売口'[1]))

    def test_drawings_only_for_pictographs_and_safe(self):
        drawn = {k for k, r in self.g.items() if r.get('svg')}
        self.assertEqual(drawn, PICTOGRAPHS)
        for k in drawn:
            svg = self.g[k]['svg']
            with self.subTest(k=k):
                root = ET.fromstring(svg)                  # well-formed XML
                self.assertTrue(root.tag.endswith('svg'))
                self.assertEqual(root.get('viewBox'), '0 0 100 100')
                low = svg.lower()
                self.assertNotIn('<script', low)
                self.assertNotIn('href', low)
                self.assertFalse(any(a.lower().startswith('on') for el in root.iter() for a in el.attrib))

    def test_origin_only_where_well_established(self):
        with_origin = {k for k, r in self.g.items() if r.get('script') == 'kanji' and r.get('origin')}
        self.assertLessEqual(with_origin, ORIGIN_OK)
        self.assertLessEqual(PICTOGRAPHS, with_origin)
