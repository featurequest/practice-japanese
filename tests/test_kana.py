from data.models import KanaCard, Stroke
from data.kana import HIRAGANA, KATAKANA


def test_stroke_has_path_and_order():
    s = Stroke(path=[(0.0, 0.0), (1.0, 1.0)], order=1)
    assert s.path == [(0.0, 0.0), (1.0, 1.0)]
    assert s.order == 1


def test_kana_card_creation():
    card = KanaCard(
        character="あ",
        romaji="a",
        kana_type="hiragana",
        row="a",
        strokes=[Stroke(path=[(0.1, 0.2), (0.9, 0.2)], order=1)],
    )
    assert card.character == "あ"
    assert card.romaji == "a"
    assert card.kana_type == "hiragana"
    assert len(card.strokes) == 1


def test_hiragana_count():
    assert len(HIRAGANA) == 104


def test_katakana_count():
    assert len(KATAKANA) == 104


def test_all_hiragana_have_romaji():
    for card in HIRAGANA:
        assert card.romaji, f"{card.character} missing romaji"
        assert card.kana_type == "hiragana"


def test_all_katakana_have_romaji():
    for card in KATAKANA:
        assert card.romaji, f"{card.character} missing romaji"
        assert card.kana_type == "katakana"


def test_hiragana_katakana_romaji_match():
    """Each hiragana should have a matching katakana with the same romaji."""
    h_romaji = sorted(c.romaji for c in HIRAGANA)
    k_romaji = sorted(c.romaji for c in KATAKANA)
    assert h_romaji == k_romaji


def test_gojuon_order():
    """First 5 hiragana should be a-i-u-e-o."""
    first_five = [c.romaji for c in HIRAGANA[:5]]
    assert first_five == ["a", "i", "u", "e", "o"]
