# tests/test_stories.py
import textwrap
from pathlib import Path

from data.stories import _parse_story, load_story, load_stories, Sentence, Story

SAMPLE_MD = textwrap.dedent("""\
    # Momotarō · もものたろう

    むかしむかし、あるところにおじいさんがいました。
    Long ago, in a certain place, there lived an old man.

    おじいさんはやまへいきました。
    The old man went to the mountain.
""")


def _write_md(tmp: Path, name: str, content: str) -> Path:
    p = tmp / name
    p.write_text(content, encoding="utf-8")
    return p


def test_parse_story_slug(tmp_path):
    p = _write_md(tmp_path, "momotaro.md", SAMPLE_MD)
    story = _parse_story(p)
    assert story.slug == "momotaro"


def test_parse_story_titles(tmp_path):
    p = _write_md(tmp_path, "momotaro.md", SAMPLE_MD)
    story = _parse_story(p)
    assert story.title_en == "Momotarō"
    assert story.title_ja == "もものたろう"


def test_parse_story_sentence_count(tmp_path):
    p = _write_md(tmp_path, "momotaro.md", SAMPLE_MD)
    story = _parse_story(p)
    assert len(story.sentences) == 2


def test_parse_story_sentence_content(tmp_path):
    p = _write_md(tmp_path, "momotaro.md", SAMPLE_MD)
    story = _parse_story(p)
    assert story.sentences[0].japanese == "むかしむかし、あるところにおじいさんがいました。"
    assert story.sentences[0].english == "Long ago, in a certain place, there lived an old man."
    assert story.sentences[0].romaji == ""  # not populated yet


def test_parse_story_ignores_blank_lines(tmp_path):
    md = textwrap.dedent("""\
        # Test · てすと

        # a comment

        あいうえお。
        AEIOU.

    """)
    p = _write_md(tmp_path, "test.md", md)
    story = _parse_story(p)
    assert len(story.sentences) == 1


def test_load_stories_returns_sorted(tmp_path):
    import data.stories as stories_mod
    for name, content in [
        ("beta.md", "# Beta · べた\nあ。\nA."),
        ("alpha.md", "# Alpha · あるふぁ\nい。\nI."),
    ]:
        (tmp_path / name).write_text(content, encoding="utf-8")
    original = stories_mod.STORIES_DIR
    try:
        stories_mod.STORIES_DIR = tmp_path
        stories = stories_mod.load_stories()
        assert stories[0].slug == "alpha"
        assert stories[1].slug == "beta"
    finally:
        stories_mod.STORIES_DIR = original


def test_load_stories_empty_when_dir_missing(tmp_path):
    import data.stories as stories_mod
    original = stories_mod.STORIES_DIR
    try:
        stories_mod.STORIES_DIR = tmp_path / "nonexistent"
        result = stories_mod.load_stories()
        assert result == []
    finally:
        stories_mod.STORIES_DIR = original


def test_parse_story_blank_line_between_pair(tmp_path):
    md = textwrap.dedent("""\
        # Test · てすと

        あいうえお。

        AEIOU.
    """)
    p = _write_md(tmp_path, "test.md", md)
    story = _parse_story(p)
    assert len(story.sentences) == 1
    assert story.sentences[0].japanese == "あいうえお。"
    assert story.sentences[0].english == "AEIOU."
