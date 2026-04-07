"""Draws the back of a flash card."""
from reportlab.pdfgen.canvas import Canvas
from data.models import KanaCard
from renderer.stroke_diagram import draw_stroke_diagram
import config

# Characters with two common romanizations — show both on the card back.
# The more common Hepburn reading is primary; the d-row reading in parentheses.
_DISPLAY_ROMAJI = {
    "ぢ": "ji (di)",   "づ": "zu (du)",
    "ぢゃ": "ja (dya)", "ぢゅ": "ju (dyu)", "ぢょ": "jo (dyo)",
    "ヂ": "ji (di)",   "ヅ": "zu (du)",
    "ヂャ": "ja (dya)", "ヂュ": "ju (dyu)", "ヂョ": "jo (dyo)",
}


def draw_card_back(c: Canvas, card: KanaCard, x: float, y: float, width: float, height: float):
    """Draw the back of a card: romaji in top third, stroke diagram in bottom two-thirds."""
    # Romaji centered in top third
    top_third = height / 3
    c.setFont("Helvetica-Bold", config.ROMAJI_FONT_SIZE)
    cx = x + width / 2
    cy = y + height - top_third / 2 - config.ROMAJI_FONT_SIZE / 3
    c.setFillColorRGB(0, 0, 0)
    c.drawCentredString(cx, cy, _DISPLAY_ROMAJI.get(card.character, card.romaji))

    # Stroke diagram in bottom two-thirds
    diagram_height = height * 2 / 3
    padding = width * 0.1
    avail_w = width - 2 * padding
    avail_h = diagram_height - 2 * padding
    side = min(avail_w, avail_h)
    dw = side
    dh = side
    draw_stroke_diagram(
        c, card.character, card.strokes,
        x=x + padding + (avail_w - dw) / 2,
        y=y + padding + (avail_h - dh) / 2,
        width=dw,
        height=dh,
    )
