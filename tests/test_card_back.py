from unittest.mock import MagicMock
from data.models import KanaCard, Stroke
from renderer.card_back import draw_card_back


def test_draw_card_back_shows_romaji_and_strokes():
    canvas = MagicMock()
    card = KanaCard(
        character="あ", romaji="a", kana_type="hiragana", row="a",
        strokes=[Stroke(path=[(0.1, 0.2), (0.9, 0.2)], order=1)],
    )
    draw_card_back(canvas, card, x=0, y=0, width=100, height=150)
    assert canvas.drawCentredString.called
