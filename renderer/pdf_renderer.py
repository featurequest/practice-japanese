"""Main PDF generation — page layout, front/back pairing, cut lines."""
import math
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from data.models import KanaCard
from renderer.card_front import draw_card_front
from renderer.card_back import draw_card_back
import config


def _register_fonts():
    if "KleeOne" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("KleeOne", config.FONT_PATH_KLEE))


def _card_positions_front() -> list[tuple[float, float]]:
    """Return (x, y) for each of the 9 card slots, top-left to bottom-right.
    PDF origin is bottom-left, so row 0 (top) has the highest y.
    """
    positions = []
    for row in range(config.ROWS):
        for col in range(config.COLS):
            x = config.MARGIN_X + col * config.CARD_WIDTH
            y = config.PAGE_HEIGHT - config.MARGIN_Y - (row + 1) * config.CARD_HEIGHT
            positions.append((x, y))
    return positions


def _card_positions_back() -> list[tuple[float, float]]:
    """Back page: reverse row order for short-edge flip alignment.
    Columns stay the same; rows are mirrored vertically so that flipping on the
    top short edge aligns each back card with its front.
    Includes BACK_PAGE_OFFSET_Y to compensate for printer duplex misalignment.
    """
    positions = []
    for row in range(config.ROWS):
        for col in range(config.COLS):
            x = config.MARGIN_X + col * config.CARD_WIDTH
            back_row = config.ROWS - 1 - row
            y = config.PAGE_HEIGHT - config.MARGIN_Y - (back_row + 1) * config.CARD_HEIGHT + config.BACK_PAGE_OFFSET_Y
            positions.append((x, y))
    return positions


def _draw_cut_lines(c: Canvas, offset_y: float = 0):
    """Draw light grid lines for cutting."""
    c.saveState()
    c.setStrokeColorRGB(*config.CUT_LINE_COLOR)
    c.setLineWidth(config.CUT_LINE_WIDTH)

    for col in range(config.COLS + 1):
        x = config.MARGIN_X + col * config.CARD_WIDTH
        c.line(x, config.MARGIN_Y + offset_y, x, config.PAGE_HEIGHT - config.MARGIN_Y + offset_y)

    for row in range(config.ROWS + 1):
        y = config.MARGIN_Y + row * config.CARD_HEIGHT + offset_y
        c.line(config.MARGIN_X, y, config.MARGIN_X + config.COLS * config.CARD_WIDTH, y)

    c.restoreState()


def generate_pdf(cards: list[KanaCard], output_path: str):
    """Generate a double-sided flash card PDF."""
    _register_fonts()
    c = Canvas(output_path, pagesize=(config.PAGE_WIDTH, config.PAGE_HEIGHT))

    front_positions = _card_positions_front()
    back_positions = _card_positions_back()
    pages = math.ceil(len(cards) / config.CARDS_PER_PAGE) if cards else 0

    for page_idx in range(pages):
        start = page_idx * config.CARDS_PER_PAGE
        page_cards = cards[start:start + config.CARDS_PER_PAGE]

        # Front page
        _draw_cut_lines(c)
        for i, card in enumerate(page_cards):
            x, y = front_positions[i]
            draw_card_front(c, card, x, y, config.CARD_WIDTH, config.CARD_HEIGHT)
        c.showPage()

        # Back page (rows reversed for short-edge flip alignment)
        _draw_cut_lines(c, offset_y=config.BACK_PAGE_OFFSET_Y)
        for i, card in enumerate(page_cards):
            x, y = back_positions[i]
            draw_card_back(c, card, x, y, config.CARD_WIDTH, config.CARD_HEIGHT)
        c.showPage()

    c.save()
