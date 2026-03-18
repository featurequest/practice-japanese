import os
import tempfile
from data.kana import HIRAGANA
from renderer.pdf_renderer import generate_pdf


def test_generate_pdf_creates_file():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    try:
        generate_pdf(HIRAGANA[:9], path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_generate_pdf_empty_list():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    try:
        generate_pdf([], path)
        assert os.path.exists(path)
    finally:
        os.unlink(path)


def test_card_position_mirroring():
    import config
    from renderer.pdf_renderer import _card_positions_front, _card_positions_back

    front = _card_positions_front()
    back = _card_positions_back()

    # X positions match: short-edge flip keeps columns in the same order
    for row in range(config.ROWS):
        for col in range(config.COLS):
            fx, _ = front[row * config.COLS + col]
            bx, _ = back[row * config.COLS + col]
            assert abs(fx - bx) < 0.01, f"Col {col} x should match between front and back"

    # Y positions: back row r physically aligns with front row (ROWS-1-r) plus offset
    for row in range(config.ROWS):
        for col in range(config.COLS):
            _, fy_mirror = front[(config.ROWS - 1 - row) * config.COLS + col]
            _, by = back[row * config.COLS + col]
            assert abs((fy_mirror + config.BACK_PAGE_OFFSET_Y) - by) < 0.01, \
                f"Back row {row} y should align with front row {config.ROWS - 1 - row} y"
