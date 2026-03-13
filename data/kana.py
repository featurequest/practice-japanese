"""Kana character dataset."""
from data.models import Stroke, KanaCard

# (character, romaji, row)
_HIRAGANA_DATA = [
    # Vowels
    ("あ", "a", "a"), ("い", "i", "a"), ("う", "u", "a"), ("え", "e", "a"), ("お", "o", "a"),
    # Ka-row
    ("か", "ka", "ka"), ("き", "ki", "ka"), ("く", "ku", "ka"), ("け", "ke", "ka"), ("こ", "ko", "ka"),
    # Sa-row
    ("さ", "sa", "sa"), ("し", "shi", "sa"), ("す", "su", "sa"), ("せ", "se", "sa"), ("そ", "so", "sa"),
    # Ta-row
    ("た", "ta", "ta"), ("ち", "chi", "ta"), ("つ", "tsu", "ta"), ("て", "te", "ta"), ("と", "to", "ta"),
    # Na-row
    ("な", "na", "na"), ("に", "ni", "na"), ("ぬ", "nu", "na"), ("ね", "ne", "na"), ("の", "no", "na"),
    # Ha-row
    ("は", "ha", "ha"), ("ひ", "hi", "ha"), ("ふ", "fu", "ha"), ("へ", "he", "ha"), ("ほ", "ho", "ha"),
    # Ma-row
    ("ま", "ma", "ma"), ("み", "mi", "ma"), ("む", "mu", "ma"), ("め", "me", "ma"), ("も", "mo", "ma"),
    # Ya-row
    ("や", "ya", "ya"), ("ゆ", "yu", "ya"), ("よ", "yo", "ya"),
    # Ra-row
    ("ら", "ra", "ra"), ("り", "ri", "ra"), ("る", "ru", "ra"), ("れ", "re", "ra"), ("ろ", "ro", "ra"),
    # Wa-row + n
    ("わ", "wa", "wa"), ("を", "wo", "wa"), ("ん", "n", "n"),
    # Dakuten - Ga
    ("が", "ga", "ka"), ("ぎ", "gi", "ka"), ("ぐ", "gu", "ka"), ("げ", "ge", "ka"), ("ご", "go", "ka"),
    # Dakuten - Za
    ("ざ", "za", "sa"), ("じ", "ji", "sa"), ("ず", "zu", "sa"), ("ぜ", "ze", "sa"), ("ぞ", "zo", "sa"),
    # Dakuten - Da
    ("だ", "da", "ta"), ("ぢ", "di", "ta"), ("づ", "du", "ta"), ("で", "de", "ta"), ("ど", "do", "ta"),
    # Dakuten - Ba
    ("ば", "ba", "ha"), ("び", "bi", "ha"), ("ぶ", "bu", "ha"), ("べ", "be", "ha"), ("ぼ", "bo", "ha"),
    # Handakuten - Pa
    ("ぱ", "pa", "ha"), ("ぴ", "pi", "ha"), ("ぷ", "pu", "ha"), ("ぺ", "pe", "ha"), ("ぽ", "po", "ha"),
    # Yōon
    ("きゃ", "kya", "ka"), ("きゅ", "kyu", "ka"), ("きょ", "kyo", "ka"),
    ("しゃ", "sha", "sa"), ("しゅ", "shu", "sa"), ("しょ", "sho", "sa"),
    ("ちゃ", "cha", "ta"), ("ちゅ", "chu", "ta"), ("ちょ", "cho", "ta"),
    ("にゃ", "nya", "na"), ("にゅ", "nyu", "na"), ("にょ", "nyo", "na"),
    ("ひゃ", "hya", "ha"), ("ひゅ", "hyu", "ha"), ("ひょ", "hyo", "ha"),
    ("みゃ", "mya", "ma"), ("みゅ", "myu", "ma"), ("みょ", "myo", "ma"),
    ("りゃ", "rya", "ra"), ("りゅ", "ryu", "ra"), ("りょ", "ryo", "ra"),
    ("ぎゃ", "gya", "ka"), ("ぎゅ", "gyu", "ka"), ("ぎょ", "gyo", "ka"),
    ("じゃ", "ja", "sa"), ("じゅ", "ju", "sa"), ("じょ", "jo", "sa"),
    ("びゃ", "bya", "ha"), ("びゅ", "byu", "ha"), ("びょ", "byo", "ha"),
    ("ぴゃ", "pya", "ha"), ("ぴゅ", "pyu", "ha"), ("ぴょ", "pyo", "ha"),
]

_KATAKANA_DATA = [
    # Vowels
    ("ア", "a", "a"), ("イ", "i", "a"), ("ウ", "u", "a"), ("エ", "e", "a"), ("オ", "o", "a"),
    # Ka-row
    ("カ", "ka", "ka"), ("キ", "ki", "ka"), ("ク", "ku", "ka"), ("ケ", "ke", "ka"), ("コ", "ko", "ka"),
    # Sa-row
    ("サ", "sa", "sa"), ("シ", "shi", "sa"), ("ス", "su", "sa"), ("セ", "se", "sa"), ("ソ", "so", "sa"),
    # Ta-row
    ("タ", "ta", "ta"), ("チ", "chi", "ta"), ("ツ", "tsu", "ta"), ("テ", "te", "ta"), ("ト", "to", "ta"),
    # Na-row
    ("ナ", "na", "na"), ("ニ", "ni", "na"), ("ヌ", "nu", "na"), ("ネ", "ne", "na"), ("ノ", "no", "na"),
    # Ha-row
    ("ハ", "ha", "ha"), ("ヒ", "hi", "ha"), ("フ", "fu", "ha"), ("ヘ", "he", "ha"), ("ホ", "ho", "ha"),
    # Ma-row
    ("マ", "ma", "ma"), ("ミ", "mi", "ma"), ("ム", "mu", "ma"), ("メ", "me", "ma"), ("モ", "mo", "ma"),
    # Ya-row
    ("ヤ", "ya", "ya"), ("ユ", "yu", "ya"), ("ヨ", "yo", "ya"),
    # Ra-row
    ("ラ", "ra", "ra"), ("リ", "ri", "ra"), ("ル", "ru", "ra"), ("レ", "re", "ra"), ("ロ", "ro", "ra"),
    # Wa-row + n
    ("ワ", "wa", "wa"), ("ヲ", "wo", "wa"), ("ン", "n", "n"),
    # Dakuten - Ga
    ("ガ", "ga", "ka"), ("ギ", "gi", "ka"), ("グ", "gu", "ka"), ("ゲ", "ge", "ka"), ("ゴ", "go", "ka"),
    # Dakuten - Za
    ("ザ", "za", "sa"), ("ジ", "ji", "sa"), ("ズ", "zu", "sa"), ("ゼ", "ze", "sa"), ("ゾ", "zo", "sa"),
    # Dakuten - Da
    ("ダ", "da", "ta"), ("ヂ", "di", "ta"), ("ヅ", "du", "ta"), ("デ", "de", "ta"), ("ド", "do", "ta"),
    # Dakuten - Ba
    ("バ", "ba", "ha"), ("ビ", "bi", "ha"), ("ブ", "bu", "ha"), ("ベ", "be", "ha"), ("ボ", "bo", "ha"),
    # Handakuten - Pa
    ("パ", "pa", "ha"), ("ピ", "pi", "ha"), ("プ", "pu", "ha"), ("ペ", "pe", "ha"), ("ポ", "po", "ha"),
    # Yōon
    ("キャ", "kya", "ka"), ("キュ", "kyu", "ka"), ("キョ", "kyo", "ka"),
    ("シャ", "sha", "sa"), ("シュ", "shu", "sa"), ("ショ", "sho", "sa"),
    ("チャ", "cha", "ta"), ("チュ", "chu", "ta"), ("チョ", "cho", "ta"),
    ("ニャ", "nya", "na"), ("ニュ", "nyu", "na"), ("ニョ", "nyo", "na"),
    ("ヒャ", "hya", "ha"), ("ヒュ", "hyu", "ha"), ("ヒョ", "hyo", "ha"),
    ("ミャ", "mya", "ma"), ("ミュ", "myu", "ma"), ("ミョ", "myo", "ma"),
    ("リャ", "rya", "ra"), ("リュ", "ryu", "ra"), ("リョ", "ryo", "ra"),
    ("ギャ", "gya", "ka"), ("ギュ", "gyu", "ka"), ("ギョ", "gyo", "ka"),
    ("ジャ", "ja", "sa"), ("ジュ", "ju", "sa"), ("ジョ", "jo", "sa"),
    ("ビャ", "bya", "ha"), ("ビュ", "byu", "ha"), ("ビョ", "byo", "ha"),
    ("ピャ", "pya", "ha"), ("ピュ", "pyu", "ha"), ("ピョ", "pyo", "ha"),
]

HIRAGANA = [KanaCard(character=c, romaji=r, kana_type="hiragana", row=row, card_number=i + 1) for i, (c, r, row) in enumerate(_HIRAGANA_DATA)]
KATAKANA = [KanaCard(character=c, romaji=r, kana_type="katakana", row=row, card_number=i + 1) for i, (c, r, row) in enumerate(_KATAKANA_DATA)]


def _apply_strokes():
    """Attach stroke data to all kana cards."""
    from data.strokes import HIRAGANA_STROKES, KATAKANA_STROKES
    for card in HIRAGANA:
        card.strokes = HIRAGANA_STROKES.get(card.romaji, [])
    for card in KATAKANA:
        card.strokes = KATAKANA_STROKES.get(card.romaji, [])


_apply_strokes()
