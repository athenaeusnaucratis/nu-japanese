"""Glyph data for the detail sheet (Round B1). Written BEFORE content_glyphs.py.

Batch 1 covers hiragana. Katakana is pending (batch 2): its cells keep working
(sound only) but get no sheet until their records exist.
"""
import os
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from test_content import build  # noqa: E402  (loads src/build.py)

HIRAGANA_BASE = list('あいうえおかきくけこさしすせそたちつてとなにぬねの'
                     'はひふへほまみむめもやゆよらりるれろわをん')
HIRAGANA_VOICED = list('がぎぐげござじずぜぞだぢづでどばびぶべぼぱぴぷぺぽ')
PENDING_SCRIPTS = {'katakana'}       # remove when batch 2 lands


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
        self.assertEqual(len(HIRAGANA_BASE), 46)
        self.assertEqual(len(HIRAGANA_VOICED), 25)

    def test_every_hiragana_in_any_grid_has_a_record(self):
        missing = sorted({c for c in grid_glyphs(self.course) if is_hiragana(c) and c not in self.g})
        self.assertEqual(missing, [])

    def test_base_records_are_complete(self):
        for ch in HIRAGANA_BASE:
            r = self.g[ch]
            with self.subTest(ch=ch):
                self.assertTrue(r['romaji'])
                self.assertTrue(r['hook'].strip())
                self.assertLessEqual(len(r['hook']), 140, 'hooks are one-liners')
                self.assertEqual(len(r['origin']), 1, 'origin is the source kanji')
                jp, reading, en = r['example']
                self.assertTrue(reading and en)
                if ch != 'を':                           # を only occurs as a particle
                    self.assertIn(ch, jp)

    def test_romaji_matches_the_chart(self):
        chart = {c[0]: c[1] for w in self.course['weeks'] for s in w['sections']
                 if s['type'] == 'kana' for row in s['rows'] for c in row if c}
        for ch in HIRAGANA_BASE + HIRAGANA_VOICED:
            self.assertEqual(self.g[ch]['romaji'], chart[ch], ch)

    def test_pending_scripts_are_deliberate(self):
        self.assertEqual(PENDING_SCRIPTS, {'katakana'})
        self.assertFalse(any('ァ' <= ch <= 'ヿ' and 'hook' in r for ch, r in self.g.items()))


class Voicing(unittest.TestCase):
    def setUp(self):
        self.g = build.make_course()['glyphs']

    def test_voiced_records_point_to_their_base(self):
        # must pass: が -> か + ゛ ; ぱ -> は + ゜
        self.assertEqual((self.g['が']['base'], self.g['が']['mark']), ('か', '゛'))
        self.assertEqual((self.g['ぱ']['base'], self.g['ぱ']['mark']), ('は', '゜'))
        self.assertEqual((self.g['ぢ']['base'], self.g['ぢ']['mark']), ('ち', '゛'))
        for ch in HIRAGANA_VOICED:
            self.assertIn(ch, self.g[self.g[ch]['base']]['voiced'], ch)

    def test_base_voiced_lists(self):
        self.assertEqual(self.g['は']['voiced'], ['ば', 'ぱ'])
        self.assertEqual(self.g['か']['voiced'], ['が'])
        # must fail cases: no voicing for these
        for ch in 'あなまやらわをん':
            self.assertEqual(self.g[ch]['voiced'], [], ch)

    def test_voiced_have_no_hook_of_their_own(self):
        for ch in HIRAGANA_VOICED:
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
                     ('れ', 'わ'), ('ね', 'れ'), ('は', 'ほ'), ('あ', 'お')]:
            self.assertIn(b, self.g[a]['looksLike'], (a, b))
        # must fail: not look-alikes
        for a, b in [('あ', 'ん'), ('の', 'め'), ('か', 'さ')]:
            self.assertNotIn(b, self.g[a]['looksLike'], (a, b))

    def test_no_self_reference_and_single_chars(self):
        for ch, r in self.g.items():
            self.assertNotIn(ch, r['looksLike'])
            self.assertTrue(all(len(x) == 1 for x in r['looksLike']))


if __name__ == '__main__':
    unittest.main()
