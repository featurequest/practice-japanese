"""Centralized configuration for flash card generation."""
from reportlab.lib.units import mm

# Paper
PAGE_WIDTH = 210 * mm
PAGE_HEIGHT = 297 * mm

# Card
CARD_WIDTH = 55 * mm
CARD_HEIGHT = 82 * mm

# Grid (auto-computed from card size)
COLS = int(PAGE_WIDTH // CARD_WIDTH)
ROWS = int(PAGE_HEIGHT // CARD_HEIGHT)
CARDS_PER_PAGE = COLS * ROWS

# Margins (centered on page)
MARGIN_X = (PAGE_WIDTH - COLS * CARD_WIDTH) / 2
MARGIN_Y = (PAGE_HEIGHT - ROWS * CARD_HEIGHT) / 2


def set_card_size(width_mm, height_mm):
    """Override card dimensions and recompute derived layout values."""
    if width_mm <= 0 or height_mm <= 0:
        raise ValueError(f"Card dimensions must be positive, got {width_mm}x{height_mm}mm")
    global CARD_WIDTH, CARD_HEIGHT, COLS, ROWS, CARDS_PER_PAGE, MARGIN_X, MARGIN_Y
    CARD_WIDTH = width_mm * mm
    CARD_HEIGHT = height_mm * mm
    COLS = int(PAGE_WIDTH // CARD_WIDTH)
    ROWS = int(PAGE_HEIGHT // CARD_HEIGHT)
    if COLS == 0 or ROWS == 0:
        raise ValueError(
            f"Card size {width_mm}x{height_mm}mm is too large to fit on "
            f"A4 ({PAGE_WIDTH / mm:.0f}x{PAGE_HEIGHT / mm:.0f}mm)")
    CARDS_PER_PAGE = COLS * ROWS
    MARGIN_X = (PAGE_WIDTH - COLS * CARD_WIDTH) / 2
    MARGIN_Y = (PAGE_HEIGHT - ROWS * CARD_HEIGHT) / 2


# Typography
KANA_FONT_SIZE = 34 * mm  # large character on front
ROMAJI_FONT_SIZE = 8 * mm  # romaji on back
LABEL_FONT_SIZE = 3 * mm  # corner label on front
STROKE_NUMBER_FONT_SIZE = 2.5 * mm  # stroke order numbers

# Stroke diagram
STROKE_LINE_WIDTH = 0.8 * mm
STROKE_DOT_RADIUS = 1.0 * mm
STROKE_COLOR = (0.2, 0.2, 0.2)  # dark gray
STROKE_NUMBER_COLOR = (0.8, 0.1, 0.1)  # red for visibility

# Font path
FONT_PATH_KLEE = "fonts/KleeOne-SemiBold.ttf"

# Back page offset — tweak to compensate for printer duplex misalignment
# Positive = shift back page content up, negative = shift down
BACK_PAGE_OFFSET_Y = -2.0 * mm

# Cut lines
CUT_LINE_WIDTH = 0.2 * mm
CUT_LINE_COLOR = (0.7, 0.7, 0.7)  # light gray
