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
        for s in self.sets:
            answers = [it['answer'] for it in s['items']]
            self.assertEqual(len(answers), len(set(answers)), f'{s["id"]}: duplicate answers')
            for it in s['items']:
                with self.subTest(set=s['id'], answer=it['answer']):
                    self.assertTrue(KANA_ONLY.match(it['answer']), 'answer must be kana-only')
                    self.assertTrue(it['prompt'].strip(), 'prompt must be non-empty')
                    self.assertIn('image', it)
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
