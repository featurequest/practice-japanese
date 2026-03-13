from unittest.mock import MagicMock
from data.models import KanaCard
from renderer.card_front import draw_card_front


def test_draw_card_front_calls_canvas():
    canvas = MagicMock()
    card = KanaCard(character="あ", romaji="a", kana_type="hiragana", row="a")
    draw_card_front(canvas, card, x=0, y=0, width=100, height=150)
    assert canvas.drawCentredString.called or canvas.drawString.called
