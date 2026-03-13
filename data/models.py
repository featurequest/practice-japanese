"""Kana data model — shared by kana.py and stroke modules."""
from dataclasses import dataclass, field


@dataclass
class Stroke:
    path: list[tuple[float, float]]  # normalized 0-1, first point is start
    order: int  # 1-based stroke number
    svg_d: str = ""  # full SVG path 'd' attribute (KanjiVG 109x109 coords)


@dataclass
class KanaCard:
    character: str
    romaji: str
    kana_type: str  # "hiragana" or "katakana"
    strokes: list[Stroke] = field(default_factory=list)
    row: str = ""  # base consonant group
    card_number: int = 0  # 1-based position within kana type
