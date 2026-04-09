from unittest.mock import MagicMock, patch
from data.models import KanaCard, Stroke
from renderer.practice_sheet import generate_combined_practice_pdf


def _card(char="あ", romaji="a"):
    return KanaCard(
        character=char, romaji=romaji, kana_type="hiragana", row="a",
        strokes=[Stroke(path=[(0.1, 0.2), (0.9, 0.8)], order=1, svg_d="M 10 10 L 90 90")],
    )


def test_generate_combined_practice_pdf_calls_draw_stroke_diagram(tmp_path):
    cards = [_card("あ", "a"), _card("い", "i")]
    out = tmp_path / "combined.pdf"
    with patch("renderer.practice_sheet.draw_stroke_diagram") as mock_diagram, \
         patch("renderer.practice_sheet.Canvas") as MockCanvas:
        canvas = MagicMock()
        MockCanvas.return_value = canvas
        generate_combined_practice_pdf(cards, str(out))
    assert mock_diagram.call_count == len(cards)


def test_generate_combined_practice_pdf_saves_file(tmp_path):
    cards = [_card()]
    out = tmp_path / "combined.pdf"
    generate_combined_practice_pdf(cards, str(out))
    assert out.exists()
