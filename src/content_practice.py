# Practice sets for the tap-to-build recall engine (Round C).
#
# Each item is (answer, prompt): `answer` is the kana the learner builds by
# tapping tiles; `prompt` is the English shown. An item links to a course vocab
# word by sharing its reading, but the answer is stated here so a slashed row
# like "ぎゅうにゅう / ミルク" has one clear thing to build.
#
# Keep answers kana-only (hiragana/katakana, ー ゛ ゜ included) — no kanji, no
# latin — so every answer can be built from tiles. tests/test_practice.py checks
# this.
#
# To add a picture to a word, make its tuple (answer, prompt, image_url):
#     ('すし', 'sushi', 'https://res.cloudinary.com/<cloud>/image/upload/.../sushi.jpg'),
# Any https image URL works (Cloudinary, your own host, etc.). Leave it a
# 2-tuple for no image. The picture shows only on the "Build" card (English +
# picture → make the Japanese); the "Recognise" card hides it so it can't give
# the answer away.

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
