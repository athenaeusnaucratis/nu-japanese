# Data for the kana detail sheet: memory hooks, origins, look-alikes, voicing.
#
# Hooks are ORIGINAL to this course (do not copy published hook sets). They are
# memory aids, not history. `origin` IS history: the kanji each hiragana was
# simplified from (man'yōgana written in cursive) — shown as a fact.
# Romaji is not repeated here; build.py takes it from the kana charts.
#
# Batch 1: hiragana. Batch 2 adds KATAKANA in the same shape.

# (glyph, origin kanji, hook, (example word, reading, meaning))
HIRAGANA = [
    ('あ', '安', 'A cross with a loop swung through it — someone walking into a signpost: "Ah!"', ('あお', 'ao', 'blue')),
    ('い', '以', 'Two short strokes standing side by side, like the two i’s in "skiing".', ('いぬ', 'inu', 'dog')),
    ('う', '宇', 'A small cap over a wide curve — a hand cupped behind an ear: "Oo, what was that?"', ('うえ', 'ue', 'above')),
    ('え', '衣', 'A dash over a Z-shaped body with a kick at the foot — someone hopping on one leg: "Eh!"', ('えき', 'eki', 'station')),
    ('お', '於', 'Like あ, but with a dot flying off the top right — something flung away: "Oh!"', ('おちゃ', 'ocha', 'tea')),
    ('か', '加', 'A blade with a short slash beside it — a karate chop cutting the air: "Ka!"', ('かお', 'kao', 'face')),
    ('き', '幾', 'Two bars crossed by a slanting stick, the tail curling below — a kite’s frame and string.', ('きく', 'kiku', 'to listen')),
    ('く', '久', 'One bent stroke shaped like "<" — an arrow cueing you to look back: "ku(e)".', ('くに', 'kuni', 'country')),
    ('け', '計', 'A post beside a cross with a long tail — it looks like a lowercase k with an extra bar.', ('いけ', 'ike', 'pond')),
    ('こ', '己', 'Two short strokes, one above the other — two coins lying flat: "ko(in)".', ('こうえん', 'kouen', 'park')),
    ('さ', '左', 'A cross over a curve opening left — a little sake cup on its stand.', ('さかな', 'sakana', 'fish')),
    ('し', '之', 'One stroke that drops and swings up — a backwards J. Think "she" with a J’s swing.', ('した', 'shita', 'below')),
    ('す', '寸', 'A bar crossed by a stem that loops once — a soup ladle hanging from a rail: "su(p)".', ('すし', 'sushi', 'sushi')),
    ('せ', '世', 'A bar with two uprights, the right one folding down and back — a seat with its back: "se(at)".', ('せんせい', 'sensei', 'teacher')),
    ('そ', '曽', 'A lightning zig-zag that softens into a curl — a sharp "so!" that trails off.', ('そと', 'soto', 'outside')),
    ('た', '太', 'A cross with two short bars beside it — a table with two plates on it: "ta(ble)".', ('たべる', 'taberu', 'to eat')),
    ('ち', '知', 'Like さ, but the belly faces right — a chin jutting out: "chi(n)".', ('ちかい', 'chikai', 'near')),
    ('つ', '川', 'One wide wave lying on its side — say "tsu" with the hiss of air rushing over it.', ('なつ', 'natsu', 'summer')),
    ('て', '天', 'A bar that bends down into a curve — a hand reaching out. 手 (te) means "hand".', ('てんき', 'tenki', 'weather')),
    ('と', '止', 'A small slanted mark leaning on a C-curve — a torch resting in its holder: "to(rch)".', ('ともだち', 'tomodachi', 'friend')),
    ('な', '奈', 'A cross, a dot, and a loop tied below — a napkin knotted at a picnic: "na(pkin)".', ('なまえ', 'namae', 'name')),
    ('に', '仁', 'A post in front of two short bars — the bars are 二 (ni), "two".', ('にく', 'niku', 'meat')),
    ('ぬ', '奴', 'め with an extra curl on its tail — the curl is the "n" that turns め into ぬ.', ('いぬ', 'inu', 'dog')),
    ('ね', '祢', 'Like れ, but the tail ties off in a loop — a necktie knot: "ne(cktie)".', ('ねこ', 'neko', 'cat')),
    ('の', '乃', 'A single spiral — the most common character in Japanese; as a particle it means "of".', ('のむ', 'nomu', 'to drink')),
    ('は', '波', 'A post beside a cross with a loop — arms thrown out in a laugh: "Ha!"', ('はな', 'hana', 'flower')),
    ('ひ', '比', 'One stroke dipping like a shallow bowl, peaked at the left — a hill and its valley: "hi(ll)".', ('ひと', 'hito', 'person')),
    ('ふ', '不', 'Four separate strokes — a face puffing out a candle: "fu!" is barely more than breath.', ('ふるい', 'furui', 'old')),
    ('へ', '部', 'One low peak, like a hat — and almost identical in katakana (ヘ).', ('へや', 'heya', 'room')),
    ('ほ', '保', 'は with a lid on top — a hot pot with its lid on: "ho(t)".', ('ほん', 'hon', 'book')),
    ('ま', '末', 'Two bars, a stem and a loop at the foot — it is the right half of ほ standing alone.', ('まいにち', 'mainichi', 'every day')),
    ('み', '美', 'Looks like "21" written in a hurry — "mi" sounds like "me", and I’m 21.', ('みず', 'mizu', 'water')),
    ('む', '武', 'A cross, a long loop and a drop flicked away — a squiggle like a music mark: "mu(sic)".', ('むずかしい', 'muzukashii', 'difficult')),
    ('め', '女', 'Two crossing strokes closing in a soft loop — an eye with a lash. 目 (me) means "eye".', ('あめ', 'ame', 'rain')),
    ('も', '毛', 'し with two bars across it — two strokes "mo(re)" than し.', ('もくようび', 'mokuyoubi', 'Thursday')),
    ('や', '也', 'A curve, a dash and a long leaning stroke — a yacht’s sail heeling in the wind: "ya(cht)".', ('やま', 'yama', 'mountain')),
    ('ゆ', '由', 'A loop with a tall stroke through it. ゆ on a shop curtain marks a bathhouse — 湯 (yu), hot water.', ('ゆき', 'yuki', 'snow')),
    ('よ', '与', 'A short bar on a post that ends in a small loop — a hand raised in greeting: "Yo!"', ('よる', 'yoru', 'night')),
    ('ら', '良', 'A tick above a round belly — a rabbit’s ear over its back: "ra(bbit)".', ('らいしゅう', 'raishuu', 'next week')),
    ('り', '利', 'A short stroke beside a long flowing one — a bank and the river running by it: "ri(ver)".', ('りょこう', 'ryokou', 'travel')),
    ('る', '留', 'A zig-zag that ends in a closed loop — the route ends in a ring. Loop: る (ru). No loop: ろ (ro).', ('くるま', 'kuruma', 'car')),
    ('れ', '礼', 'A post with a stroke that zig-zags and kicks outward — someone beating a retreat: "re(treat)".', ('これ', 'kore', 'this')),
    ('ろ', '呂', 'る without the loop — the road stays open: "ro(ad)".', ('ろく', 'roku', 'six')),
    ('わ', '和', 'A post with a stroke that rolls into a wide arc — a wave breaking: "wa(ve)".', ('わたし', 'watashi', 'I / me')),
    ('を', '遠', 'Only ever the object particle, said "o". A bar, a zig-zag, a broken curve — tripping over an object: "Whoa!"', ('パンを たべます', 'pan o tabemasu', 'I eat bread')),
    ('ん', '无', 'One stroke shaped like a lowercase n with a tail — and it really is n.', ('えん', 'en', 'yen')),
]

# (base, voiced form, mark). Explicit on purpose — no codepoint arithmetic.
VOICED = [
    ('か', 'が', '゛'), ('き', 'ぎ', '゛'), ('く', 'ぐ', '゛'), ('け', 'げ', '゛'), ('こ', 'ご', '゛'),
    ('さ', 'ざ', '゛'), ('し', 'じ', '゛'), ('す', 'ず', '゛'), ('せ', 'ぜ', '゛'), ('そ', 'ぞ', '゛'),
    ('た', 'だ', '゛'), ('ち', 'ぢ', '゛'), ('つ', 'づ', '゛'), ('て', 'で', '゛'), ('と', 'ど', '゛'),
    ('は', 'ば', '゛'), ('ひ', 'び', '゛'), ('ふ', 'ぶ', '゛'), ('へ', 'べ', '゛'), ('ほ', 'ぼ', '゛'),
    ('は', 'ぱ', '゜'), ('ひ', 'ぴ', '゜'), ('ふ', 'ぷ', '゜'), ('へ', 'ぺ', '゜'), ('ほ', 'ぽ', '゜'),
]

# Characters learners confuse. Each string is one group; every member lists the
# others. Members without a record (e.g. katakana before batch 2, or 工 力 二
# outside the course) are still shown, just not tappable.
LOOKALIKE_GROUPS = [
    # hiragana
    'さち', 'さき', 'ぬめ', 'るろ', 'いり', 'れわね', 'はほ', 'あお', 'こに', 'うら',
    # across scripts
    'へヘ', 'りリ', 'かカ', 'きキ', 'やヤ',
    # katakana (records arrive in batch 2)
    'シツ', 'ソン', 'クケタ', 'ウワフ', 'ユコ', 'ナメ', 'エ工', 'カ力', 'ニ二', 'ロ口',
]
