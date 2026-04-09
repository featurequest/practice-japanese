# tests/test_stories_pdf.py
import tempfile
from pathlib import Path

from data.stories import Story, Sentence
from tools.stories_pdf import generate_story_pdf, _to_romaji, generate_reading_practice_pdf


SAMPLE_STORY = Story(
    slug="test",
    title_en="Test Story",
    title_ja="てすとすとーりー",
    sentences=[
        Sentence(japanese="むかしむかし、おじいさんがいました。",
                 english="Long ago there was an old man."),
        Sentence(japanese="おじいさんはやまへいきました。",
                 english="The old man went to the mountain."),
    ],
)


def test_to_romaji_basic():
    result = _to_romaji("あいうえお")
    assert result.strip() != ""
    assert "a" in result.lower()


def test_to_romaji_hiragana_words():
    result = _to_romaji("むかし むかし")  # add explicit space
    assert "mukashi" in result.lower()


def test_to_romaji_preserves_spaces():
    result = _to_romaji("むかしむかし おじいさんが いました。")
    # spaces in input should appear as spaces in romaji output
    parts = result.split()
    assert len(parts) >= 2  # at least one space preserved


def test_generate_story_pdf_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "test.pdf"
        generate_story_pdf(SAMPLE_STORY, out)
        assert out.exists()
        assert out.stat().st_size > 1000


def test_to_romaji_no_space_before_punctuation():
    result = _to_romaji("むかしむかし、おじいさんがいました。")
    assert " ," not in result
    assert " ." not in result


def test_generate_story_pdf_creates_parent_dirs():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / "subdir" / "story.pdf"
        generate_story_pdf(SAMPLE_STORY, out)
        assert out.exists()


def test_generate_reading_practice_pdf_creates_file(tmp_path):
    out = tmp_path / "practice.pdf"
    generate_reading_practice_pdf(SAMPLE_STORY, out)
    assert out.exists()
    assert out.stat().st_size > 1000


def test_generate_reading_practice_pdf_all_stories(tmp_path):
    from data.stories import load_stories
    for story in load_stories():
        out = tmp_path / f"{story.slug}_practice.pdf"
        generate_reading_practice_pdf(story, out)
        assert out.exists()
        assert out.stat().st_size > 1000
