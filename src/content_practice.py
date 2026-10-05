# Practice sets for the tap-to-build recall engine (Round C).
#
# Each item is (answer, prompt): `answer` is the kana the learner builds by
# tapping tiles; `prompt` is the English shown. An item links to a course vocab
# word by sharing its reading, but the answer is stated here so a slashed row
# like "ぎゅうにゅう / ミルク" has one clear thing to build.
#
# Keep answers kana-only (hiragana/katakana, ー ゛ ゜ included) — no kanji, no
# latin — so every answer can be built from tiles. tests/test_practice.py checks
# this. The `image` slot (Cloudinary URL, later) is reserved and left empty now.

PRACTICE_SETS = [
    {
        'id': 'food',
        'title': 'Food & Drink',
        'blurb': 'Everyday words for what’s on the table — build each one from the tiles.',
        'items': [
            ('ごはん', 'rice; a cooked meal'),
            ('あさごはん', 'breakfast'),
            ('ひるごはん', 'lunch'),
            ('ばんごはん', 'dinner'),
            ('パン', 'bread'),
            ('みず', 'water'),
            ('おちゃ', 'green tea'),
            ('コーヒー', 'coffee'),
            ('ビール', 'beer'),
            ('おさけ', 'sake; alcohol'),
            ('ぎゅうにゅう', 'milk'),
            ('ジュース', 'juice'),
            ('ワイン', 'wine'),
            ('くだもの', 'fruit'),
            ('やさい', 'vegetables'),
            ('にく', 'meat'),
            ('さかな', 'fish (to eat)'),
            ('たまご', 'egg'),
            ('チーズ', 'cheese'),
            ('バター', 'butter'),
            ('ピザ', 'pizza'),
            ('ケーキ', 'cake'),
            ('アイスクリーム', 'ice cream'),
            ('すし', 'sushi'),
            ('ラーメン', 'ramen'),
            ('うどん', 'udon noodles'),
            ('そば', 'soba noodles'),
            ('てんぷら', 'tempura'),
            ('カレー', 'curry'),
        ],
    },
]
