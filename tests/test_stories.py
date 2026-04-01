# tests/test_stories.py
import os, sys, textwrap, tempfile
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from data.stories import _parse_story, load_story, load_stories, Sentence, Story

SAMPLE_MD = textwrap.dedent("""\
    # Momotarō · もものたろう

    むかしむかし、あるところにおじいさんがいました。
    Long ago, in a certain place, there lived an old man.

    おじいさんはやまへいきました。
    The old man went to the mountain.
""")


def _write_md(tmp: str, name: str, content: str) -> Path:
    p = Path(tmp) / name
    p.write_text(content, encoding="utf-8")
    return p


def test_parse_story_slug(tmp_path):
    p = _write_md(str(tmp_path), "momotaro.md", SAMPLE_MD)
    story = _parse_story(p)
    assert story.slug == "momotaro"


def test_parse_story_titles(tmp_path):
    p = _write_md(str(tmp_path), "momotaro.md", SAMPLE_MD)
    story = _parse_story(p)
    assert story.title_en == "Momotarō"
    assert story.title_ja == "もものたろう"


def test_parse_story_sentence_count(tmp_path):
    p = _write_md(str(tmp_path), "momotaro.md", SAMPLE_MD)
    story = _parse_story(p)
    assert len(story.sentences) == 2


def test_parse_story_sentence_content(tmp_path):
    p = _write_md(str(tmp_path), "momotaro.md", SAMPLE_MD)
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
    p = _write_md(str(tmp_path), "test.md", md)
    story = _parse_story(p)
    assert len(story.sentences) == 1


def test_load_stories_returns_sorted(tmp_path):
    for name, content in [
        ("beta.md", "# Beta · べた\nあ。\nA."),
        ("alpha.md", "# Alpha · あるふぁ\nい。\nI."),
    ]:
        (tmp_path / name).write_text(content, encoding="utf-8")
    stories = _load_from_dir(tmp_path)
    assert stories[0].slug == "alpha"
    assert stories[1].slug == "beta"


def _load_from_dir(directory: Path):
    from data.stories import _parse_story
    return [_parse_story(p) for p in sorted(directory.glob("*.md"))]
