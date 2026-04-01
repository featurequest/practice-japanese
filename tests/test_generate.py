import os
import shutil
import tempfile
import subprocess
import sys
from pathlib import Path
from unittest.mock import patch

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def test_no_args_shows_help():
    result = subprocess.run(
        [sys.executable, "generate.py"],
        capture_output=True, text=True, cwd=PROJECT_ROOT,
    )
    assert result.returncode == 0
    assert "usage" in result.stdout.lower() or "kana" in result.stdout.lower()


def test_generate_creates_pdf():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "test.pdf")
        result = subprocess.run(
            [sys.executable, "generate.py", "--kana", "-o", out],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, result.stderr
        assert os.path.exists(out)
        assert os.path.getsize(out) > 0


def test_generate_hiragana_only():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "test.pdf")
        result = subprocess.run(
            [sys.executable, "generate.py", "--kana", "--hiragana-only", "-o", out],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, result.stderr


def test_generate_katakana_only():
    with tempfile.TemporaryDirectory() as tmpdir:
        out = os.path.join(tmpdir, "test.pdf")
        result = subprocess.run(
            [sys.executable, "generate.py", "--kana", "--katakana-only", "-o", out],
            capture_output=True, text=True, cwd=PROJECT_ROOT,
        )
        assert result.returncode == 0, result.stderr


def test_stories_flag(tmp_path, monkeypatch):
    monkeypatch.chdir(tmp_path)
    shutil.copytree(os.path.join(PROJECT_ROOT, 'data'), str(tmp_path / 'data'))
    shutil.copytree(os.path.join(PROJECT_ROOT, 'fonts'), str(tmp_path / 'fonts'))
    (tmp_path / 'output').mkdir()
    with patch('sys.argv', ['generate.py', '--stories']):
        from generate import main
        main()
    pdfs = list((tmp_path / 'output').glob('story_*.pdf'))
    story_files = list(Path(PROJECT_ROOT, 'data', 'stories').glob('*.md'))
    assert len(pdfs) == len(story_files)
