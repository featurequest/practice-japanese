import os
import tempfile
import subprocess
import sys

from renderer.chart import (
    _build_romaji_to_char,
    _get_basic_romaji,
    _DUAL_DISPLAY,
    generate_chart_pdf,
    generate_stroke_order_pdf,
)

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_build_romaji_to_char_hiragana():
    lookup = _build_romaji_to_char("hiragana")
    assert lookup["a"] == "あ"
    assert lookup["ka"] == "か"
    assert lookup["n"] == "ん"
    # Dakuten special keys
    assert lookup["di"] == "ぢ"
    assert lookup["du"] == "づ"
    # Yōon combinations from ぢ
    assert lookup["dya"] == "ぢゃ"
    assert lookup["dyu"] == "ぢゅ"
    assert lookup["dyo"] == "ぢょ"


def test_dual_display_entries():
    assert _DUAL_DISPLAY["di"]  == "ji (di)"
    assert _DUAL_DISPLAY["du"]  == "zu (du)"
    assert _DUAL_DISPLAY["dya"] == "ja (dya)"
    assert _DUAL_DISPLAY["dyu"] == "ju (dyu)"
    assert _DUAL_DISPLAY["dyo"] == "jo (dyo)"


def test_build_romaji_to_char_katakana():
    lookup = _build_romaji_to_char("katakana")
    assert lookup["a"] == "ア"
    assert lookup["ka"] == "カ"
    assert lookup["n"] == "ン"


def test_get_basic_romaji_vowels():
    assert _get_basic_romaji("", "a") == "a"
    assert _get_basic_romaji("", "i") == "i"
    assert _get_basic_romaji("", "u") == "u"
    assert _get_basic_romaji("", "e") == "e"
    assert _get_basic_romaji("", "o") == "o"


def test_get_basic_romaji_irregulars():
    assert _get_basic_romaji("s", "i") == "shi"
    assert _get_basic_romaji("t", "i") == "chi"
    assert _get_basic_romaji("t", "u") == "tsu"
    assert _get_basic_romaji("h", "u") == "fu"


def test_get_basic_romaji_empty_cells():
    assert _get_basic_romaji("y", "i") is None
    assert _get_basic_romaji("y", "e") is None
    assert _get_basic_romaji("w", "i") is None
    assert _get_basic_romaji("w", "u") is None
    assert _get_basic_romaji("w", "e") is None


def test_get_basic_romaji_wa_row():
    assert _get_basic_romaji("w", "a") == "wa"
    assert _get_basic_romaji("w", "o") == "wo"


def test_generate_chart_pdf_creates_file():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    try:
        generate_chart_pdf(["hiragana", "katakana"], path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_generate_chart_pdf_single_type():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    try:
        generate_chart_pdf(["hiragana"], path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_generate_chart_cli():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "test_chart.pdf")
        result = subprocess.run(
            [sys.executable, "generate.py", "--kana", "--chart", "-o", out],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, result.stderr
        assert os.path.exists(out)


def test_generate_stroke_order_pdf():
    with tempfile.NamedTemporaryFile(suffix=".pdf", delete=False) as f:
        path = f.name
    try:
        generate_stroke_order_pdf(["hiragana", "katakana"], path)
        assert os.path.exists(path)
        assert os.path.getsize(path) > 0
    finally:
        os.unlink(path)


def test_generate_stroke_order_cli():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "test_stroke.pdf")
        result = subprocess.run(
            [sys.executable, "generate.py", "--kana", "--stroke-order", "-o", out],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, result.stderr
        assert os.path.exists(out)


def test_generate_chart_cli_hiragana_only():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "test_chart.pdf")
        result = subprocess.run(
            [sys.executable, "generate.py", "--kana", "--chart", "--hiragana-only", "-o", out],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, result.stderr
