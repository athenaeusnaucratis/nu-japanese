"""Practice-set data (Round C). Written BEFORE the engine.

Answers must be kana-only so every one can be built by tapping tiles.
"""
import os
import re
import sys
import unittest

sys.path.insert(0, os.path.dirname(__file__))
from test_content import build  # noqa: E402  (loads src/build.py)

KANA_ONLY = re.compile(r'^[぀-ヿー]+$')   # hiragana, katakana, ー


class PracticeData(unittest.TestCase):
    def setUp(self):
        self.sets = build.make_course()['practiceSets']

    def test_food_set_present(self):
        ids = [s['id'] for s in self.sets]
        self.assertIn('food', ids)
        food = next(s for s in self.sets if s['id'] == 'food')
        self.assertEqual(food['title'], 'Food & Drink')
        self.assertEqual(len(food['items']), 29)

    def test_items_are_buildable_and_glossed(self):
        # Thematic sets deliberately include recognise-only words (kanji with no
        # kana form, multi-word items) whose build `answer` is '' — so IDs, not
        # answers, are the uniqueness key, and the kana rule applies only to the
        # items that actually have a build target.
        for s in self.sets:
            ids = [it['id'] for it in s['items']]
            self.assertEqual(len(ids), len(set(ids)), f'{s["id"]}: duplicate ids')
            for it in s['items']:
                with self.subTest(set=s['id'], id=it['id']):
                    self.assertTrue(it['prompt'].strip(), 'prompt must be non-empty')
                    self.assertIn('image', it)
                    if it['answer']:
                        self.assertTrue(KANA_ONLY.match(it['answer']), 'build answer must be kana-only')
                    if it['image']:
                        self.assertTrue(it['image'].startswith('https://'), 'image must be an https URL')

    def test_food_items_all_have_pictures(self):
        food = next(s for s in self.sets if s['id'] == 'food')
        self.assertTrue(all(it['image'].startswith('https://res.cloudinary.com/') for it in food['items']))

    def test_item_id_is_stable_and_set_scoped(self):
        food = next(s for s in self.sets if s['id'] == 'food')
        ids = [it['id'] for it in food['items']]
        self.assertEqual(len(ids), len(set(ids)))
        self.assertEqual(food['items'][0]['id'], 'p:food:ごはん')

    def test_every_answer_kana_has_a_glyph_record(self):
        """Tiles and the dakuten/small feedback rely on COURSE.glyphs; every
        base kana used in an answer must have a record (voiced ones too)."""
        glyphs = build.make_course()['glyphs']
        small = set('ぁぃぅぇぉゃゅょっゎァィゥェォャュョッ')
        for s in self.sets:
            for it in s['items']:
                for ch in it['answer']:
                    if ch == 'ー' or ch in small:
                        continue
                    with self.subTest(answer=it['answer'], ch=ch):
                        self.assertIn(ch, glyphs)


if __name__ == '__main__':
    unittest.main()


class KanaAnswerAndIndex(unittest.TestCase):
    def test_kana_answer(self):
        cases = {
            'ねこ': 'ねこ', 'すし': 'すし', 'アイスクリーム': 'アイスクリーム',
            '日本人 / にほんじん': 'にほんじん', '本 / ほん': 'ほん', 'うち / いえ': 'うち',
            'この [noun]': 'この', 'きれい(な)': 'きれい', 'ぎゅうにゅう / ミルク': 'ぎゅうにゅう',
            '四': '', '一': '', '日本 / にほん': 'にほん',
            'いち、に、さん、よん、ご': '',          # a list, not a single word
        }
        bad = {jp: (build.kana_answer(jp), want) for jp, want in cases.items() if build.kana_answer(jp) != want}
        self.assertEqual(bad, {})

    def test_vocab_index_shape(self):
        idx = build.make_course()['vocabById']
        self.assertGreater(len(idx), 300)
        self.assertEqual(idx['v:ねこ|neko'], {'prompt': 'cat', 'answer': 'ねこ', 'display': 'ねこ', 'image': ''})
        # a kanji-written word: recognise shows the kanji, build target is the kana reading
        jpn = idx['v:日本人 / にほんじん|nihon-jin']
        self.assertEqual(jpn['prompt'], 'Japanese person')
        self.assertEqual(jpn['answer'], 'にほんじん')
        self.assertEqual(jpn['display'], '日本人 / にほんじん')
        # a bare-kanji number has no kana build target
        self.assertEqual(idx['v:四|yon / shi']['answer'], '')

    def test_every_index_id_is_a_real_vocab_id(self):
        course = build.make_course()
        real = {i for s in [sec for w in course['weeks'] for sec in w['sections']]
                + [sec for a in course['appendices'] for sec in a['sections']]
                if s['type'] == 'vocab' for i in s['ids']}
        self.assertEqual(set(course['vocabById']), real)


class GlossCleaning(unittest.TestCase):
    def test_clean_gloss(self):
        cases = {
            'close \u2192 \u3057\u3081\u307e\u3059': 'close',          # drop the dict->masu arrow
            'eat \u2192 \u305f\u3079\u307e\u3059': 'eat',
            'to know (usually used as \u3057\u3063\u3066\u3044\u307e\u3059)': 'to know',  # JP in parens
            '300 (sound change!)': '300',                              # "!" annotation
            'I&rsquo;m home': 'I\u2019m home',                        # decode entity
            'which [noun]?': 'which?',                                # drop placeholder
            'cold (weather)': 'cold (weather)',                       # keep disambiguation
            'fish (to eat)': 'fish (to eat)',
            'you (use sparingly)': 'you (use sparingly)',
            'to listen / to ask': 'to listen / to ask',
            'Thank you (polite)': 'Thank you (polite)',
            'rice; a cooked meal': 'rice; a cooked meal',
        }
        bad = {g: (build.clean_gloss(g), want) for g, want in cases.items() if build.clean_gloss(g) != want}
        self.assertEqual(bad, {})

    def test_clean_display(self):
        self.assertEqual(build.clean_display('\u3069\u306e [noun]'), '\u3069\u306e')
        self.assertEqual(build.clean_display('\u3053\u306e [noun]'), '\u3053\u306e')
        self.assertEqual(build.clean_display('\u65e5\u66dc\u65e5 / \u306b\u3061\u3088\u3046\u3073'),
                         '\u65e5\u66dc\u65e5 / \u306b\u3061\u3088\u3046\u3073')
        self.assertEqual(build.clean_display('\u306d\u3053'), '\u306d\u3053')

    def test_pool_and_index_are_clean(self):
        course = build.make_course()
        import re as _re
        dirty = _re.compile(r'&[a-z]+;|&#\d+;|\u2192|\[|[\u3040-\u30ff\u4e00-\u9fff][^)]*\)')
        bad_pool = [m for m in course['meaningPool'] if dirty.search(m)]
        self.assertEqual(bad_pool, [])
        bad_prompt = [v['prompt'] for v in course['vocabById'].values() if dirty.search(v['prompt'])]
        self.assertEqual(bad_prompt, [])
        self.assertEqual(course['vocabById']['v:\u3057\u3081\u308b|shimeru']['prompt'], 'close')
        self.assertEqual(course['vocabById']['v:\u3069\u306e [noun]|dono [noun]']['display'], '\u3069\u306e')


# Grouped reference rows ("1\u20135" -> \u3044\u3061\u3001\u306b\u3001\u3055\u3093\u3001\u3088\u3093\u3001\u3054) make poor
# recall cards and can't be built from tiles. is_list_row() marks them so the
# thematic sets drop them, while keeping every real single word. Fixture BEFORE
# the rule (tests/CLAUDE.md): must-list, must-word, and human-judgment cases.
class ListRowClassifier(unittest.TestCase):
    MUST_LIST = [
        '\u3044\u3061\u3001\u306b\u3001\u3055\u3093\u3001\u3088\u3093\u3001\u3054',   # ichi, ni, san, yon, go
        '\u308d\u304f\u3001\u306a\u306a\u3001\u306f\u3061\u3001\u304d\u3085\u3046\u3001\u3058\u3085\u3046',   # roku...juu
        '\u3072\u3083\u304f\u3001\u305b\u3093\u3001\u307e\u3093',           # hyaku, sen, man
        '\u3053\u308c\u3001\u305d\u308c\u3001\u3042\u308c',                 # kore, sore, are
        '\u3053\u306e\u301c\u3001\u305d\u306e\u301c\u3001\u3042\u306e\u301c',  # kono~, sono~, ano~
        '\u3069\u308c\u3001\u3069\u306e\u301c',                             # dore, dono~
        '\u3053\u3053\u3001\u305d\u3053\u3001\u3042\u305d\u3053',           # koko, soko, asoko
        '\u3075\u3064\u304b\u3001\u307f\u3063\u304b\u3001\u3088\u3063\u304b',  # futsuka, mikka, yokka
        '\u3044\u3061\u304c\u3064\u2026\u3058\u3085\u3046\u306b\u304c\u3064',  # ichi-gatsu...juuni-gatsu
    ]
    MUST_WORD = [
        '\u306d\u3053',                         # neko
        '\u3044\u3061\u3058\u304b\u3093',       # ichi-jikan (a counter, but one word)
        '\u3069\u3053', '\u3044\u3064', '\u3060\u308c',  # doko / itsu / dare
        '\u304a\u3068\u3053\u306e \u3072\u3068',          # otoko no hito -- a SPACE, not a comma
        '\u304a\u306f\u3088\u3046 / \u304a\u306f\u3088\u3046\u3054\u3056\u3044\u307e\u3059',  # ' / ' variant
        '\u3061\u3061 / \u304a\u3068\u3046\u3055\u3093',  # chichi / otousan
        '\u306a\u306b / \u306a\u3093',          # nani / nan
        '\u30a2\u30e1\u30ea\u30ab\u4eba',       # amerika-jin (kanji, but one word)
        '\u3070\u3093 / \u3088\u308b',          # ban / yoru
        '\u3044\u305f\u3060\u304d\u307e\u3059',  # itadakimasu (one set phrase)
    ]
    # Human judgment: long set phrases stay single recall items despite being a
    # mouthful; they carry no comma/ellipsis, so the rule keeps them.
    UNSURE_KEEP = [
        '\u3069\u3046\u305e\u3088\u308d\u3057\u304f\u304a\u306d\u304c\u3044\u3057\u307e\u3059',  # douzo yoroshiku...
        '\u3054\u3061\u305d\u3046\u3055\u307e\u3067\u3057\u305f',                               # gochisousama deshita
    ]

    def test_lists_detected(self):
        bad = [j for j in self.MUST_LIST if not build.is_list_row(j)]
        self.assertEqual(bad, [])

    def test_words_not_lists(self):
        bad = [j for j in self.MUST_WORD if build.is_list_row(j)]
        self.assertEqual(bad, [])

    def test_unsure_kept_as_words(self):
        bad = [j for j in self.UNSURE_KEEP if build.is_list_row(j)]
        self.assertEqual(bad, [])


class ThematicSets(unittest.TestCase):
    def setUp(self):
        self.sets = build.make_course()['practiceSets']
        self.by = {s['id']: s for s in self.sets}

    def test_expected_sets_present(self):
        for sid in ['food', 'greetings', 'people', 'countries', 'things', 'verbs',
                    'i-adjectives', 'na-adjectives', 'time', 'nature', 'questions']:
            self.assertIn(sid, self.by)

    def test_numbers_set_dropped(self):
        # Numbers & counters collapses to a single word once list rows are gone.
        self.assertNotIn('numbers', self.by)
        self.assertNotIn('Numbers & counters', [s['title'] for s in self.sets])

    def test_food_not_duplicated_and_keeps_pictures(self):
        foods = [s for s in self.sets if 'Food' in s['title']]
        self.assertEqual(len(foods), 1)
        self.assertEqual(foods[0]['id'], 'food')
        self.assertTrue(all(it['image'].startswith('https://res.cloudinary.com/') for it in foods[0]['items']))

    def test_thematic_sets_are_text_only(self):
        # Only the curated Food set carries pictures; image credits are spent.
        for sid, s in self.by.items():
            if sid == 'food':
                continue
            self.assertTrue(all(it['image'] == '' for it in s['items']), sid)

    def test_thematic_items_shape_and_clean(self):
        import re as _re
        dirty = _re.compile(r'&[a-z]+;|&#\d+;|\u2192|\[|[\u3040-\u30ff\u4e00-\u9fff][^)]*\)')
        for sid in ['verbs', 'i-adjectives', 'greetings', 'questions', 'time', 'people']:
            s = self.by[sid]
            self.assertGreaterEqual(len(s['items']), 6, sid)
            self.assertTrue(s['title'])
            for it in s['items']:
                with self.subTest(set=sid, id=it['id']):
                    self.assertTrue(it['id'].startswith('v:'))
                    self.assertTrue(it['prompt'].strip())
                    self.assertFalse(dirty.search(it['prompt']), it['prompt'])
                    self.assertEqual(it['image'], '')
                    self.assertFalse(build.is_list_row(it['display']))
                    if it['answer']:
                        self.assertTrue(KANA_ONLY.match(it['answer']))

    def test_known_words_land_in_sets(self):
        tabe = next(it for it in self.by['verbs']['items'] if it['id'] == 'v:\u305f\u3079\u307e\u3059|tabemasu')
        self.assertEqual(tabe['answer'], '\u305f\u3079\u307e\u3059')
        self.assertEqual(tabe['prompt'], 'to eat')
        # a kanji word is recognise-only: no kana build target, but still glossed
        aj = next(it for it in self.by['countries']['items'] if it['id'] == 'v:\u30a2\u30e1\u30ea\u30ab\u4eba|amerika-jin')
        self.assertEqual(aj['answer'], '')
        self.assertEqual(aj['prompt'], 'American')
