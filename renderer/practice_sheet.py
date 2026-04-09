"""Generates practice worksheet PDFs with a grid of boxes for handwriting practice.

Each row starts with a KanjiVG-rendered character, followed by empty boxes.
Pages are landscape A4 with ~2cm boxes.
"""
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from data.models import KanaCard
from renderer.stroke_diagram import _draw_svg_path, draw_stroke_diagram
import config

# Layout constants for practice sheets
_PAGE_W = 297 * mm  # A4 landscape
_PAGE_H = 210 * mm
_BOX = 20 * mm
_MARGIN = 5 * mm
_LINE_COLOR = (0.75, 0.75, 0.75)
_LINE_WIDTH = 0.3 * mm
_GUIDE_COLOR = (0.85, 0.85, 0.85)
_GUIDE_WIDTH = 0.15 * mm
_GUIDE_DASH = [1.5 * mm, 1.5 * mm]


def _register_fonts():
    if "KleeOne" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("KleeOne", config.FONT_PATH_KLEE))


def _draw_character(c: Canvas, card: KanaCard, x: float, y: float, size: float):
    """Draw a KanjiVG character inside a box, with font fallback."""
    c.saveState()
    padding = size * 0.08
    inner = size - 2 * padding

    has_svg = card.strokes and any(s.svg_d for s in card.strokes)
    if has_svg:
        c.setStrokeColorRGB(0, 0, 0)
        c.setLineWidth(config.STROKE_LINE_WIDTH * 1.5)
        c.setLineCap(1)
        c.setLineJoin(1)
        for stroke in card.strokes:
            if stroke.svg_d:
                _draw_svg_path(c, stroke.svg_d, x + padding, y + padding, inner, inner)
    else:
        font_size = inner * 0.85
        c.setFillColorRGB(0, 0, 0)
        c.setFont("KleeOne", font_size)
        cx = x + size / 2
        cy = y + size / 2 - font_size / 3
        c.drawCentredString(cx, cy, card.character)

    c.restoreState()


def generate_practice_pdf(cards: list[KanaCard], output_path: str):
    """Generate a practice worksheet PDF with landscape A4 pages."""
    _register_fonts()
    c = Canvas(output_path, pagesize=(_PAGE_W, _PAGE_H))
    types = sorted({card.kana_type.capitalize() for card in cards})
    c.setTitle(" / ".join(types) + " Practice Sheets")

    cols = int((_PAGE_W - 2 * _MARGIN) // _BOX)
    rows = int((_PAGE_H - 2 * _MARGIN) // _BOX)

    # Center the grid on the page
    grid_w = cols * _BOX
    grid_h = rows * _BOX
    offset_x = (_PAGE_W - grid_w) / 2
    offset_y = (_PAGE_H - grid_h) / 2

    rows_per_char = 3
    chars_per_page = rows // rows_per_char
    card_idx = 0

    while card_idx < len(cards):
        # How many characters fit on this page
        page_chars = min(chars_per_page, len(cards) - card_idx)
        used_rows = page_chars * rows_per_char

        # Draw grid lines for used rows only
        used_h = used_rows * _BOX
        top_y = offset_y + grid_h  # align to top
        c.saveState()
        c.setStrokeColorRGB(*_LINE_COLOR)
        c.setLineWidth(_LINE_WIDTH)
        for col in range(cols + 1):
            x = offset_x + col * _BOX
            c.line(x, top_y - used_h, x, top_y)
        for row in range(used_rows + 1):
            y = top_y - row * _BOX
            c.line(offset_x, y, offset_x + grid_w, y)
        # Draw centered cross guides in each box
        c.setStrokeColorRGB(*_GUIDE_COLOR)
        c.setLineWidth(_GUIDE_WIDTH)
        c.setDash(*_GUIDE_DASH)
        half = _BOX / 2
        for row in range(used_rows):
            for col in range(cols):
                bx = offset_x + col * _BOX
                by = top_y - (row + 1) * _BOX
                # Horizontal center line
                c.line(bx, by + half, bx + _BOX, by + half)
                # Vertical center line
                c.line(bx + half, by, bx + half, by + _BOX)
        c.restoreState()

        # Fill rows — character in first box of first row of each group
        for char_i in range(page_chars):
            if card_idx >= len(cards):
                break
            first_row = char_i * rows_per_char
            y = top_y - (first_row + 1) * _BOX
            _draw_character(c, cards[card_idx], offset_x, y, _BOX)
            card_idx += 1

        c.showPage()

    c.save()


def generate_combined_practice_pdf(cards: list[KanaCard], output_path: str):
    """Practice sheet with 2×2 stroke order diagram per character."""
    _DIAG = 2  # diagram spans this many boxes in each direction
    _register_fonts()
    c = Canvas(output_path, pagesize=(_PAGE_W, _PAGE_H))
    types = sorted({card.kana_type.capitalize() for card in cards})
    c.setTitle(" / ".join(types) + " Combined Stroke Practice")

    cols = int((_PAGE_W - 2 * _MARGIN) // _BOX)
    rows = int((_PAGE_H - 2 * _MARGIN) // _BOX)

    grid_w = cols * _BOX
    grid_h = rows * _BOX
    offset_x = (_PAGE_W - grid_w) / 2
    offset_y = (_PAGE_H - grid_h) / 2

    rows_per_char = 3
    chars_per_page = rows // rows_per_char
    card_idx = 0

    while card_idx < len(cards):
        page_chars = min(chars_per_page, len(cards) - card_idx)
        used_rows = page_chars * rows_per_char
        used_h = used_rows * _BOX
        top_y = offset_y + grid_h

        # Grid lines
        c.saveState()
        c.setStrokeColorRGB(*_LINE_COLOR)
        c.setLineWidth(_LINE_WIDTH)
        for col in range(cols + 1):
            x = offset_x + col * _BOX
            c.line(x, top_y - used_h, x, top_y)
        for row in range(used_rows + 1):
            y = top_y - row * _BOX
            c.line(offset_x, y, offset_x + grid_w, y)
        # Dashed guides — skip the 2×2 diagram area (first 2 cols × first 2 rows of each char)
        c.setStrokeColorRGB(*_GUIDE_COLOR)
        c.setLineWidth(_GUIDE_WIDTH)
        c.setDash(*_GUIDE_DASH)
        half = _BOX / 2
        for row in range(used_rows):
            rel_row = row % rows_per_char
            for col in range(cols):
                if rel_row < _DIAG and col < _DIAG:
                    continue
                bx = offset_x + col * _BOX
                by = top_y - (row + 1) * _BOX
                c.line(bx, by + half, bx + _BOX, by + half)
                c.line(bx + half, by, bx + half, by + _BOX)
        c.restoreState()

        # Draw stroke diagrams — each spans a 2×2 block of boxes
        diag_size = _DIAG * _BOX
        for char_i in range(page_chars):
            if card_idx >= len(cards):
                break
            first_row = char_i * rows_per_char
            x = offset_x
            y = top_y - (first_row + _DIAG) * _BOX  # bottom-left of 2×2 area
            # White fill to erase interior grid lines inside the diagram block
            c.saveState()
            c.setFillColorRGB(1, 1, 1)
            c.setStrokeColorRGB(*_LINE_COLOR)
            c.setLineWidth(_LINE_WIDTH)
            c.rect(x, y, diag_size, diag_size, fill=1, stroke=1)
            c.restoreState()
            padding = diag_size * 0.04
            draw_stroke_diagram(
                c,
                cards[card_idx].character,
                cards[card_idx].strokes,
                x=x + padding,
                y=y + padding,
                width=diag_size - 2 * padding,
                height=diag_size - 2 * padding,
            )
            card_idx += 1

        c.showPage()

    c.save()
