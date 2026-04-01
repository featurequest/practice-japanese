"""data/stories.py — Story data model and markdown parser."""
from __future__ import annotations
from dataclasses import dataclass, field
from pathlib import Path

STORIES_DIR = Path(__file__).parent / "stories"


@dataclass
class Sentence:
    japanese: str
    english: str
    romaji: str = ""


@dataclass
class Story:
    slug: str
    title_en: str
    title_ja: str
    sentences: list[Sentence] = field(default_factory=list)


def _parse_story(path: Path) -> Story:
    slug = path.stem
    lines = path.read_text(encoding="utf-8").splitlines()

    title_en, title_ja = "", ""
    title_found = False
    sentence_lines = []

    for line in lines:
        stripped = line.strip()
        if not title_found:
            if stripped.startswith("#"):
                raw = stripped.lstrip("#").strip()
                if "·" in raw:
                    title_en, title_ja = [p.strip() for p in raw.split("·", 1)]
                else:
                    title_en = raw
                title_found = True
            continue
        sentence_lines.append(stripped)

    sentences = []
    pending: str | None = None
    for line in sentence_lines:
        if not line or line.startswith("#"):
            continue  # skip blank/comment lines; leave pending untouched
        if pending is None:
            pending = line
        else:
            sentences.append(Sentence(japanese=pending, english=line))
            pending = None

    return Story(slug=slug, title_en=title_en, title_ja=title_ja, sentences=sentences)


def load_story(slug: str) -> Story:
    return _parse_story(STORIES_DIR / f"{slug}.md")


def load_stories() -> list[Story]:
    if not STORIES_DIR.exists():
        return []
    return [_parse_story(p) for p in sorted(STORIES_DIR.glob("*.md"))]
