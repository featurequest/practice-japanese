import os
import tempfile
import subprocess
import sys

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_generate_creates_pdf():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "test.pdf")
        result = subprocess.run(
            [sys.executable, "generate.py", "-o", out],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, result.stderr
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0


def test_generate_hiragana_only():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "test.pdf")
        result = subprocess.run(
            [sys.executable, "generate.py", "--hiragana-only", "-o", out],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, result.stderr


def test_generate_katakana_only():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "test.pdf")
        result = subprocess.run(
            [sys.executable, "generate.py", "--katakana-only", "-o", out],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, result.stderr
