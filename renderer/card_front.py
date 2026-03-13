"""Draws the front of a flash card."""
from reportlab.pdfgen.canvas import Canvas
from data.models import KanaCard
import config


def draw_card_front(c: Canvas, card: KanaCard, x: float, y: float, width: float, height: float):
    """Draw the front of a card: large character using Klee One font + type label."""
    c.saveState()

    c.setFillColorRGB(0, 0, 0)
    font_size = config.KANA_FONT_SIZE
    c.setFont("KleeOne", font_size)
    cx = x + width / 2
    cy = y + height / 2 - font_size / 3

    if len(card.character) > 1:
        # Tighten spacing for yōon (e.g. きょ) — reduce gap between glyphs
        squeeze = -font_size * 0.25
        total_w = c.stringWidth(card.character, "KleeOne", font_size) + squeeze * (len(card.character) - 1)
        start_x = cx - total_w / 2
        c._code.append(f"{squeeze:.2f} Tc")
        c.drawString(start_x, cy, card.character)
        c._code.append("0 Tc")
    else:
        c.drawCentredString(cx, cy, card.character)

    c.restoreState()

    # Card number (black circle with white number) and type label in top-left
    c.saveState()
    label_size = config.LABEL_FONT_SIZE
    radius = label_size * 0.85
    circle_cx = x + label_size + radius
    circle_cy = y + height - label_size - radius

    c.setFillColorRGB(0, 0, 0)
    c.circle(circle_cx, circle_cy, radius, fill=1, stroke=0)

    c.setFillColorRGB(1, 1, 1)
    num_font_size = label_size * 0.85
    c.setFont("Helvetica-Bold", num_font_size)
    num_str = str(card.card_number)
    num_width = c.stringWidth(num_str, "Helvetica-Bold", num_font_size)
    c.drawString(circle_cx - num_width / 2, circle_cy - label_size * 0.3, num_str)

    label = "ひらがな" if card.kana_type == "hiragana" else "カタカナ"
    c.setFillColorRGB(0.5, 0.5, 0.5)
    c.setFont("KleeOne", label_size)
    c.drawString(circle_cx + radius + label_size * 0.5, circle_cy - label_size * 0.35, label)
    c.restoreState()
