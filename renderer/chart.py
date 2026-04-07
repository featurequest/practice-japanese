"""Generates landscape A4 reference chart PDFs for hiragana and katakana.

Lays out the standard gojūon table with three sections:
- Basic characters (10 columns × 5 rows)
- Dakuten / Handakuten (5 columns × 5 rows)
- Yōon combinations (basic + dakuten, 3 rows each)
"""
from reportlab.lib.units import mm
from reportlab.pdfgen.canvas import Canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from renderer.stroke_diagram import _draw_svg_path
import config

# Page layout — landscape A4
_PAGE_W = 297 * mm
_PAGE_H = 210 * mm
_MARGIN = 8 * mm

# Cell sizing
_CELL_W = 17.5 * mm
_CELL_H = 18 * mm
# Yōon cell width computed to fill the page: 7 basic + gap + 5 dakuten columns
_YOON_GAP = 5 * mm
_YOON_TOTAL_COLS = len(["ky", "sh", "ch", "ny", "hy", "my", "ry"]) + len(["gy", "j", "dy", "by", "py"])
_YOON_CELL_W = (_PAGE_W - 2 * _MARGIN - _YOON_GAP) / _YOON_TOTAL_COLS
_YOON_CELL_H = _YOON_CELL_W  # keep square
_ROMAJI_FONT_SIZE = 2.5 * mm
_KANA_FONT_SIZE = 10 * mm
_TITLE_FONT_SIZE = 6 * mm
_SECTION_FONT_SIZE = 3 * mm
_BORDER_WIDTH = 0.3 * mm
_BORDER_COLOR = (0.3, 0.3, 0.3)
_HEADER_BG = (0.9, 0.9, 0.9)

# Vowel order (rows)
_VOWELS = ["a", "i", "u", "e", "o"]

# Basic table: column consonant prefixes and their display headers
_BASIC_COLS = [
    ("", ""),       # vowel column (a, i, u, e, o)
    ("k", "K"),
    ("s", "S"),
    ("t", "T"),
    ("n", "N"),
    ("h", "H"),
    ("m", "M"),
    ("y", "Y"),
    ("r", "R"),
    ("w", "W"),
]

# Dakuten / Handakuten columns
_DAKUTEN_COLS = [
    ("g", "G"),
    ("z", "Z"),
    ("d", "D"),
    ("b", "B"),
    ("p", "P"),
]

# Irregulars: consonant+vowel -> actual romaji
_IRREGULARS = {
    "si": "shi", "ti": "chi", "tu": "tsu", "hu": "fu",
    "zi": "ji", "di": "ji", "du": "zu",
    "yi": None, "ye": None, "wi": None, "wu": None, "we": None,
    "ya": "ya", "yi_": None, "yu": "yu", "ye_": None, "yo": "yo",
}

# Yōon basic groups: (base consonant romaji prefix, display prefix)
_YOON_BASIC = [
    ("ky", "KY"),
    ("sh", "SH"),
    ("ch", "CH"),
    ("ny", "NY"),
    ("hy", "HY"),
    ("my", "MY"),
    ("ry", "RY"),
]

# Yōon dakuten groups
_YOON_DAKUTEN = [
    ("gy", "GY"),
    ("j", "J"),
    ("dy", "DY"),
    ("by", "BY"),
    ("py", "PY"),
]

# Yōon suffixes
_YOON_SUFFIXES = ["a", "u", "o"]


def _register_fonts():
    if "KleeOne" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("KleeOne", config.FONT_PATH_KLEE))


def _build_romaji_to_char(kana_type: str) -> dict[str, str]:
    """Build a mapping from romaji to character for the given kana type."""
    from data.kana import HIRAGANA, KATAKANA
    cards = HIRAGANA if kana_type == "hiragana" else KATAKANA
    mapping = {}
    for card in cards:
        mapping[card.romaji] = card.character
    # Disambiguate homophonous pairs — the first loop leaves "ji"/"zu" pointing
    # to ぢ/づ (last-write wins) because they appear after じ/ず in the list.
    # Restore "ji"→じ/ジ and "zu"→ず/ズ (z-row), and add "di"→ぢ/ヂ, "du"→づ/ヅ.
    for card in cards:
        if card.character in ("じ", "ジ"):
            mapping["ji"] = card.character
        elif card.character in ("ず", "ズ"):
            mapping["zu"] = card.character
        elif card.character in ("ぢ", "ヂ"):
            mapping["di"] = card.character
        elif card.character in ("づ", "ヅ"):
            mapping["du"] = card.character
    return mapping


def _build_romaji_to_card(kana_type: str) -> dict:
    """Build a mapping from romaji to KanaCard for stroke data access."""
    from data.kana import HIRAGANA, KATAKANA
    cards = HIRAGANA if kana_type == "hiragana" else KATAKANA
    mapping = {}
    for card in cards:
        mapping[card.romaji] = card
    for card in cards:
        if card.character in ("じ", "ジ"):
            mapping["ji"] = card
        elif card.character in ("ず", "ズ"):
            mapping["zu"] = card
        elif card.character in ("ぢ", "ヂ"):
            mapping["di"] = card
        elif card.character in ("づ", "ヅ"):
            mapping["du"] = card
    return mapping


def _get_basic_romaji(consonant: str, vowel: str) -> str | None:
    """Get the romaji for a basic table cell, or None if empty."""
    if consonant == "":
        return vowel  # a, i, u, e, o
    raw = consonant + vowel
    # Check for empty cells
    if raw in _IRREGULARS and _IRREGULARS[raw] is None:
        return None
    # Check for irregular readings
    if raw in _IRREGULARS:
        return _IRREGULARS[raw]
    # Special: wa-row only has wa, wo, n
    if consonant == "w":
        if vowel == "a":
            return "wa"
        elif vowel == "o":
            return "wo"
        else:
            return None
    # Special: ya-row only has ya, yu, yo
    if consonant == "y":
        if vowel in ("a", "u", "o"):
            return consonant + vowel
        else:
            return None
    # Special: n-row has na, ni, nu, ne, no (not the standalone n)
    return raw


def _draw_cell(c: Canvas, x: float, y: float, w: float, h: float,
               kana: str, romaji: str, font_name: str):
    """Draw a single chart cell with romaji header and kana character."""
    c.saveState()

    # Romaji header background (draw fill first, then borders on top)
    romaji_area_h = _romaji_header_h(h)
    c.setFillColorRGB(*_HEADER_BG)
    c.rect(x, y + h - romaji_area_h, w, romaji_area_h, fill=1, stroke=0)

    # Cell border + divider line (drawn after fill so borders are crisp)
    c.setStrokeColorRGB(*_BORDER_COLOR)
    c.setLineWidth(_BORDER_WIDTH)
    c.rect(x, y, w, h)
    c.line(x, y + h - romaji_area_h, x + w, y + h - romaji_area_h)

    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.setFont("Helvetica-Bold", _ROMAJI_FONT_SIZE)
    c.drawCentredString(x + w / 2, y + h - romaji_area_h + (romaji_area_h - _ROMAJI_FONT_SIZE) / 2,
                        romaji.upper())

    # Kana character (center of remaining area)
    kana_area_h = h - romaji_area_h
    c.setFillColorRGB(0, 0, 0)
    font_size = _KANA_FONT_SIZE
    c.setFont(font_name, font_size)

    if len(kana) > 1:
        # Tighten spacing so yōon fits in cell at full size
        natural_w = c.stringWidth(kana, font_name, font_size)
        max_w = w * 0.9
        squeeze = -(natural_w - max_w) / (len(kana) - 1) if natural_w > max_w else -font_size * 0.15
        total_w = natural_w + squeeze * (len(kana) - 1)
        start_x = x + w / 2 - total_w / 2
        c._code.append(f"{squeeze:.2f} Tc")
        c.drawString(start_x, y + kana_area_h / 2 - font_size / 3, kana)
        c._code.append("0 Tc")
    else:
        c.drawCentredString(x + w / 2, y + kana_area_h / 2 - font_size / 3, kana)

    c.restoreState()


def _romaji_header_h(h: float) -> float:
    """Compute romaji header height — fixed size, capped at 25% of cell."""
    return min(h * 0.25, _ROMAJI_FONT_SIZE + 3 * mm)


def _draw_stroke_cell(c: Canvas, x: float, y: float, w: float, h: float,
                      card, romaji: str):
    """Draw a chart cell with romaji header and KanjiVG stroke order diagram."""
    from renderer.stroke_diagram import draw_stroke_diagram
    c.saveState()

    # Romaji header background (draw fill first, then borders on top)
    romaji_area_h = _romaji_header_h(h)
    c.setFillColorRGB(*_HEADER_BG)
    c.rect(x, y + h - romaji_area_h, w, romaji_area_h, fill=1, stroke=0)

    # Cell border + divider line
    c.setStrokeColorRGB(*_BORDER_COLOR)
    c.setLineWidth(_BORDER_WIDTH)
    c.rect(x, y, w, h)
    c.line(x, y + h - romaji_area_h, x + w, y + h - romaji_area_h)

    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.setFont("Helvetica-Bold", _ROMAJI_FONT_SIZE)
    c.drawCentredString(x + w / 2, y + h - romaji_area_h + (romaji_area_h - _ROMAJI_FONT_SIZE) / 2,
                        romaji.upper())

    # Stroke diagram — square, centered in the available area
    kana_area_h = h - romaji_area_h
    padding = max(1 * mm, min(w, kana_area_h) * 0.04)
    avail_w = w - 2 * padding
    avail_h = kana_area_h - 2 * padding
    diagram_size = min(avail_w, avail_h)
    dx = x + padding + (avail_w - diagram_size) / 2
    dy = y + padding + (avail_h - diagram_size) / 2
    draw_stroke_diagram(c, card.character, card.strokes,
                        dx, dy, diagram_size, diagram_size)

    c.restoreState()


def _draw_empty_cell(c: Canvas, x: float, y: float, w: float, h: float):
    """Draw an empty cell (no character for this position)."""
    c.saveState()
    c.setStrokeColorRGB(*_BORDER_COLOR)
    c.setLineWidth(_BORDER_WIDTH)
    c.setFillColorRGB(0.96, 0.96, 0.96)
    c.rect(x, y, w, h, fill=1, stroke=1)
    c.restoreState()


def _draw_section_header(c: Canvas, x: float, y: float, text: str):
    """Draw a section header label."""
    c.saveState()
    c.setFillColorRGB(0.2, 0.2, 0.2)
    c.setFont("Helvetica-Bold", _SECTION_FONT_SIZE)
    c.drawString(x, y, text)
    c.restoreState()


def _draw_n_cell(c: Canvas, x: float, y: float, w: float, h: float,
                 kana: str, font_name: str):
    """Draw the standalone N cell."""
    _draw_cell(c, x, y, w, h, kana, "N", font_name)


def _draw_chart_page(c: Canvas, kana_type: str, stroke_order: bool = False):
    """Draw one full chart page for the given kana type."""
    font_name = "KleeOne"
    lookup = _build_romaji_to_char(kana_type)
    card_lookup = _build_romaji_to_card(kana_type) if stroke_order else {}
    label = "HIRAGANA" if kana_type == "hiragana" else "KATAKANA"
    title = f"{label} STROKE ORDER" if stroke_order else f"{label} CHART"

    # Title
    c.saveState()
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", _TITLE_FONT_SIZE)
    c.drawCentredString(_PAGE_W / 2, _PAGE_H - _MARGIN - _TITLE_FONT_SIZE, title)
    c.restoreState()

    top_y = _PAGE_H - _MARGIN - _TITLE_FONT_SIZE - 5 * mm

    def draw_filled_cell(x, y, romaji, lookup_key=None,
                         cell_w=_CELL_W, cell_h=_CELL_H):
        """Draw a cell with either font character or stroke diagram."""
        key = lookup_key or romaji
        char = lookup.get(key)
        if not char:
            _draw_empty_cell(c, x, y, cell_w, cell_h)
            return
        if stroke_order:
            card = card_lookup.get(key)
            if card and card.strokes:
                _draw_stroke_cell(c, x, y, cell_w, cell_h, card, romaji)
                return
        _draw_cell(c, x, y, cell_w, cell_h, char, romaji, font_name)

    # --- BASIC + DAKUTEN sections (centered on page) ---
    section_label_h = _SECTION_FONT_SIZE + 1 * mm
    gap = 5 * mm
    total_top_w = 11 * _CELL_W + gap + 5 * _CELL_W
    basic_x = (_PAGE_W - total_top_w) / 2
    _draw_section_header(c, basic_x, top_y, "BASIC")
    grid_top = top_y - section_label_h

    for col_idx, (consonant, col_label) in enumerate(_BASIC_COLS):
        for row_idx, vowel in enumerate(_VOWELS):
            x = basic_x + col_idx * _CELL_W
            y = grid_top - (row_idx + 1) * _CELL_H
            romaji = _get_basic_romaji(consonant, vowel)
            if romaji is None:
                _draw_empty_cell(c, x, y, _CELL_W, _CELL_H)
                continue
            draw_filled_cell(x, y, romaji)

    # N cell — after the wa-row
    n_char = lookup.get("n")
    if n_char:
        n_x = basic_x + 10 * _CELL_W
        n_y = grid_top - 1 * _CELL_H
        draw_filled_cell(n_x, n_y, "n")

    # --- DAKUTEN / HANDAKUTEN section ---
    dakuten_x = basic_x + 11 * _CELL_W + gap
    _draw_section_header(c, dakuten_x, top_y, "DAKUTEN / HANDAKUTEN")

    for col_idx, (consonant, col_label) in enumerate(_DAKUTEN_COLS):
        for row_idx, vowel in enumerate(_VOWELS):
            x = dakuten_x + col_idx * _CELL_W
            y = grid_top - (row_idx + 1) * _CELL_H
            raw = consonant + vowel
            romaji = _IRREGULARS.get(raw, raw)
            if romaji is None:
                _draw_empty_cell(c, x, y, _CELL_W, _CELL_H)
                continue
            lookup_key = raw if raw in ("di", "du") else romaji
            draw_filled_cell(x, y, romaji, lookup_key)

    # --- COMBINATIONS (YŌON) section (centered on page) ---
    yoon_top = grid_top - 5 * _CELL_H - 7 * mm
    total_yoon_w = len(_YOON_BASIC) * _YOON_CELL_W + _YOON_GAP + len(_YOON_DAKUTEN) * _YOON_CELL_W
    yoon_x = (_PAGE_W - total_yoon_w) / 2
    _draw_section_header(c, yoon_x, yoon_top, "COMBINATIONS")
    yoon_grid_top = yoon_top - section_label_h

    # Basic yōon
    for col_idx, (prefix, display) in enumerate(_YOON_BASIC):
        for row_idx, suffix in enumerate(_YOON_SUFFIXES):
            x = yoon_x + col_idx * _YOON_CELL_W
            y = yoon_grid_top - (row_idx + 1) * _YOON_CELL_H
            romaji = prefix + suffix
            draw_filled_cell(x, y, romaji, cell_w=_YOON_CELL_W, cell_h=_YOON_CELL_H)

    # Dakuten yōon (with gap)
    dakuten_yoon_x = yoon_x + len(_YOON_BASIC) * _YOON_CELL_W + _YOON_GAP
    for col_idx, (prefix, display) in enumerate(_YOON_DAKUTEN):
        for row_idx, suffix in enumerate(_YOON_SUFFIXES):
            x = dakuten_yoon_x + col_idx * _YOON_CELL_W
            y = yoon_grid_top - (row_idx + 1) * _YOON_CELL_H
            romaji = prefix + suffix
            draw_filled_cell(x, y, romaji, cell_w=_YOON_CELL_W, cell_h=_YOON_CELL_H)

    c.showPage()


# Portrait A4 for stroke order pages
_PORT_W = 210 * mm
_PORT_H = 297 * mm


def _draw_stroke_grid_page(c: Canvas, title: str, cols_data, rows,
                           row_fn, lookup, card_lookup, font_name):
    """Draw a single stroke order grid page filling the available space.

    Args:
        title: Page title text.
        cols_data: List of column definitions (passed to row_fn).
        rows: List of row labels/keys.
        row_fn: Callable(col, row) -> (romaji, lookup_key) or None for empty.
        lookup: romaji -> character mapping.
        card_lookup: romaji -> KanaCard mapping.
    """
    section_label_h = _SECTION_FONT_SIZE + 2 * mm

    c.saveState()
    c.setFillColorRGB(0, 0, 0)
    c.setFont("Helvetica-Bold", _TITLE_FONT_SIZE)
    c.drawCentredString(_PORT_W / 2, _PORT_H - _MARGIN - _TITLE_FONT_SIZE, title)
    c.restoreState()

    top_y = _PORT_H - _MARGIN - _TITLE_FONT_SIZE - 5 * mm
    num_cols = len(cols_data)
    num_rows = len(rows)

    avail_w = _PORT_W - 2 * _MARGIN
    avail_h = top_y - section_label_h - _MARGIN
    cell_w = avail_w / num_cols
    cell_h = avail_h / num_rows

    total_w = num_cols * cell_w
    total_h = num_rows * cell_h
    grid_x = (_PORT_W - total_w) / 2
    grid_top = top_y - section_label_h + (avail_h - total_h) / 2

    for col_idx, col in enumerate(cols_data):
        for row_idx, row in enumerate(rows):
            x = grid_x + col_idx * cell_w
            y = grid_top - (row_idx + 1) * cell_h
            result = row_fn(col, row)
            if result is None:
                _draw_empty_cell(c, x, y, cell_w, cell_h)
                continue
            romaji, lookup_key = result
            key = lookup_key or romaji
            char = lookup.get(key)
            if not char:
                _draw_empty_cell(c, x, y, cell_w, cell_h)
                continue
            card = card_lookup.get(key)
            if card and card.strokes:
                _draw_stroke_cell(c, x, y, cell_w, cell_h, card, romaji)
            else:
                _draw_cell(c, x, y, cell_w, cell_h, char, romaji, font_name)

    c.showPage()


def _draw_stroke_order_pages(c: Canvas, kana_type: str):
    """Draw stroke order charts on four portrait A4 pages.

    Page 1: Basic (11 cols × 5 rows)
    Page 2: Dakuten / Handakuten (5 cols × 5 rows)
    Page 3: Basic combinations (7 cols × 3 rows)
    Page 4: Dakuten combinations (4 cols × 3 rows)
    """
    font_name = "KleeOne"
    lookup = _build_romaji_to_char(kana_type)
    card_lookup = _build_romaji_to_card(kana_type)
    label = "HIRAGANA" if kana_type == "hiragana" else "KATAKANA"

    # Page 1: Basic
    def basic_row_fn(col, vowel):
        consonant = col[0]
        romaji = _get_basic_romaji(consonant, vowel)
        if romaji is None:
            return None
        return (romaji, romaji)

    # Include N as an extra column
    basic_cols = list(_BASIC_COLS) + [("n_col", "N")]

    def basic_with_n_fn(col, vowel):
        consonant, _ = col
        if consonant == "n_col":
            # Only show N in the first row
            if vowel == "a":
                return ("n", "n")
            return None
        romaji = _get_basic_romaji(consonant, vowel)
        if romaji is None:
            return None
        return (romaji, romaji)

    _draw_stroke_grid_page(c, f"{label} STROKE ORDER — BASIC",
                           basic_cols, _VOWELS, basic_with_n_fn,
                           lookup, card_lookup, font_name)

    # Page 2: Dakuten / Handakuten
    def dakuten_row_fn(col, vowel):
        consonant, _ = col
        raw = consonant + vowel
        romaji = _IRREGULARS.get(raw, raw)
        if romaji is None:
            return None
        lookup_key = raw if raw in ("di", "du") else romaji
        return (romaji, lookup_key)

    _draw_stroke_grid_page(c, f"{label} STROKE ORDER — DAKUTEN / HANDAKUTEN",
                           _DAKUTEN_COLS, _VOWELS, dakuten_row_fn,
                           lookup, card_lookup, font_name)

    # Page 3: Basic combinations — transposed: 3 cols (ya/yu/yo) × 7 rows
    _YOON_SUFFIX_COLS = [("a", "YA"), ("u", "YU"), ("o", "YO")]

    def yoon_row_fn(suffix_col, group_row):
        suffix, _ = suffix_col
        prefix, _ = group_row
        romaji = prefix + suffix
        return (romaji, romaji)

    # Split basic combinations: 4 + 3 rows across two pages
    _draw_stroke_grid_page(c, f"{label} STROKE ORDER — COMBINATIONS (1/2)",
                           _YOON_SUFFIX_COLS, _YOON_BASIC[:4], yoon_row_fn,
                           lookup, card_lookup, font_name)

    _draw_stroke_grid_page(c, f"{label} STROKE ORDER — COMBINATIONS (2/2)",
                           _YOON_SUFFIX_COLS, _YOON_BASIC[4:], yoon_row_fn,
                           lookup, card_lookup, font_name)

    # Dakuten combinations — 3 cols × 4 rows
    _draw_stroke_grid_page(c, f"{label} STROKE ORDER — DAKUTEN COMBINATIONS",
                           _YOON_SUFFIX_COLS, _YOON_DAKUTEN, yoon_row_fn,
                           lookup, card_lookup, font_name)


def generate_chart_pdf(kana_types: list[str], output_path: str):
    """Generate a character reference chart PDF (landscape A4).

    Args:
        kana_types: List of "hiragana" and/or "katakana".
        output_path: Path to write the PDF.
    """
    _register_fonts()
    c = Canvas(output_path, pagesize=(_PAGE_W, _PAGE_H))
    for kana_type in kana_types:
        _draw_chart_page(c, kana_type)
    c.save()


def generate_stroke_order_pdf(kana_types: list[str], output_path: str):
    """Generate a stroke order reference PDF (portrait A4).

    Args:
        kana_types: List of "hiragana" and/or "katakana".
        output_path: Path to write the PDF.
    """
    _register_fonts()
    c = Canvas(output_path, pagesize=(_PORT_W, _PORT_H))
    for kana_type in kana_types:
        _draw_stroke_order_pages(c, kana_type)
    c.save()
