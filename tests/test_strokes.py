from data.kana import HIRAGANA, KATAKANA


def test_all_hiragana_have_strokes():
    for card in HIRAGANA:
        assert len(card.strokes) > 0, f"{card.character} ({card.romaji}) missing strokes"


def test_all_katakana_have_strokes():
    for card in KATAKANA:
        assert len(card.strokes) > 0, f"{card.character} ({card.romaji}) missing strokes"


def test_stroke_coordinates_in_range():
    for card in HIRAGANA + KATAKANA:
        for stroke in card.strokes:
            for x, y in stroke.path:
                assert 0.0 <= x <= 1.0, f"{card.character} stroke {stroke.order}: x={x} out of range"
                assert 0.0 <= y <= 1.0, f"{card.character} stroke {stroke.order}: y={y} out of range"


def test_stroke_orders_sequential():
    for card in HIRAGANA + KATAKANA:
        orders = [s.order for s in card.strokes]
        assert orders == list(range(1, len(orders) + 1)), (
            f"{card.character}: stroke orders {orders} not sequential"
        )


def test_each_stroke_has_at_least_two_points():
    for card in HIRAGANA + KATAKANA:
        for stroke in card.strokes:
            assert len(stroke.path) >= 2, (
                f"{card.character} stroke {stroke.order}: needs at least 2 points"
            )


def test_known_stroke_counts():
    """Sanity check: verify stroke counts for well-known characters."""
    h_by_romaji = {c.romaji: c for c in HIRAGANA}
    expected = {"a": 3, "i": 2, "u": 2, "e": 2, "o": 3, "ka": 3, "n": 1, "shi": 1}
    for romaji, count in expected.items():
        card = h_by_romaji[romaji]
        assert len(card.strokes) == count, (
            f"{card.character} ({romaji}): expected {count} strokes, got {len(card.strokes)}"
        )
