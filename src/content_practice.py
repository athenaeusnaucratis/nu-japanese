# Practice sets for the tap-to-build recall engine (Round C).
#
# Each item is (answer, prompt) or (answer, prompt, image_url): `answer` is the
# kana the learner builds by tapping tiles; `prompt` is the English shown;
# `image_url` is an optional picture.
#
# Keep answers kana-only (hiragana/katakana, ー ゛ ゜ included) — no kanji, no
# latin — so every answer can be built from tiles. tests/test_practice.py checks
# this.
#
# The pictures are AI-generated and stored in the project's Cloudinary
# (cloud "mqhcplej", folder nu-japanese/food/). The delivery URL carries the
# transform f_auto,q_auto,c_fill,ar_4:3,w_520, so each one arrives as a small,
# correctly-cropped WebP/JPEG. To replace a picture, regenerate or upload under
# the same public_id, or point the tuple at any other https URL. The picture
# shows only on the "Build" card; the "Recognise" card hides it.

_CLOUD = ('https://res.cloudinary.com/mqhcplej/image/upload/'
          'f_auto,q_auto,c_fill,ar_4:3,w_520/nu-japanese/food/')


def _img(slug):
    return _CLOUD + slug + '.jpg'


PRACTICE_SETS = [
    {
        'id': 'food',
        'title': 'Food & Drink',
        'blurb': 'Everyday words for what’s on the table — build each one from the tiles.',
        'items': [
            ('ごはん', 'rice; a cooked meal', _img('gohan')),
            ('あさごはん', 'breakfast', _img('asagohan')),
            ('ひるごはん', 'lunch', _img('hirugohan')),
            ('ばんごはん', 'dinner', _img('bangohan')),
            ('パン', 'bread', _img('pan')),
            ('みず', 'water', _img('mizu')),
            ('おちゃ', 'green tea', _img('ocha')),
            ('コーヒー', 'coffee', _img('koohii')),
            ('ビール', 'beer', _img('biiru')),
            ('おさけ', 'sake; alcohol', _img('osake')),
            ('ぎゅうにゅう', 'milk', _img('gyuunyuu')),
            ('ジュース', 'juice', _img('juusu')),
            ('ワイン', 'wine', _img('wain')),
            ('くだもの', 'fruit', _img('kudamono')),
            ('やさい', 'vegetables', _img('yasai')),
            ('にく', 'meat', _img('niku')),
            ('さかな', 'fish (to eat)', _img('sakana')),
            ('たまご', 'egg', _img('tamago')),
            ('チーズ', 'cheese', _img('chiizu')),
            ('バター', 'butter', _img('bataa')),
            ('ピザ', 'pizza', _img('piza')),
            ('ケーキ', 'cake', _img('keeki')),
            ('アイスクリーム', 'ice cream', _img('aisukuriimu')),
            ('すし', 'sushi', _img('sushi')),
            ('ラーメン', 'ramen', _img('raamen')),
            ('うどん', 'udon noodles', _img('udon')),
            ('そば', 'soba noodles', _img('soba')),
            ('てんぷら', 'tempura', _img('tenpura')),
            ('カレー', 'curry', _img('karee')),
        ],
    },
]
