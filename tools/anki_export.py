"""tools/anki_export.py — Build Anki .apkg vocabulary decks from data/vocabulary.json."""
import hashlib
import json
from pathlib import Path

import genanki


# ── Private helpers ────────────────────────────────────────────────────────────

def _stable_id(name: str) -> int:
    """Return a stable positive 31-bit int for use as a genanki model/deck ID."""
    return int(hashlib.sha1(name.encode()).hexdigest(), 16) % (2**31)


def _build_model() -> genanki.Model:
    """Create the shared genanki.Model with 7 fields and two card templates."""
    return genanki.Model(
        _stable_id("Japanese Vocabulary"),
        "Japanese Vocabulary",
        fields=[
            {"name": "Expression"},
            {"name": "Reading"},
            {"name": "Romaji"},
            {"name": "Meaning_Short"},
            {"name": "Meaning_Full"},
            {"name": "POS"},
            {"name": "Info"},
        ],
        templates=[
            {
                "name": "Forward",
                "qfmt": (
                    "<div style='font-size:2em'>{{Expression}}</div>"
                    "{{#Reading}}<div style='font-size:1.2em;color:#555'>{{Reading}}</div>{{/Reading}}"
                ),
                "afmt": (
                    "{{FrontSide}}<hr>"
                    "<div>{{Meaning_Full}}</div>"
                    "<div style='color:#777;font-size:0.9em'>{{Romaji}}</div>"
                    "{{#POS}}<div style='color:#888;font-size:0.85em'>[{{POS}}]</div>{{/POS}}"
                    "{{#Info}}<div style='color:#888;font-size:0.85em'>{{Info}}</div>{{/Info}}"
                ),
            },
            {
                "name": "Reverse",
                "qfmt": "<div style='font-size:1.4em'>{{Meaning_Short}}</div>",
                "afmt": (
                    "{{FrontSide}}<hr>"
                    "<div style='font-size:2em'>{{Expression}}</div>"
                    "{{#Reading}}<div style='font-size:1.2em;color:#555'>{{Reading}}</div>{{/Reading}}"
                    "<div style='color:#777;font-size:0.9em'>{{Romaji}}</div>"
                    "{{#POS}}<div style='color:#888;font-size:0.85em'>[{{POS}}]</div>{{/POS}}"
                ),
            },
        ],
    )


def _format_meaning_short(word: dict) -> str:
    """Return the first gloss of the first English sense."""
    meanings = word.get("meanings", [])
    if not meanings:
        return ""
    first_en = meanings[0].get("localized", {}).get("en", "")
    return first_en.split(";")[0].strip()


_CIRCLED = "①②③④⑤⑥⑦⑧⑨⑩"


def _format_meaning_full(word: dict) -> str:
    """Return all English senses formatted with ①②③ prefixes."""
    meanings = word.get("meanings", [])
    en_senses = [m.get("localized", {}).get("en", "") for m in meanings if m.get("localized", {}).get("en")]
    if not en_senses:
        return ""
    if len(en_senses) == 1:
        return en_senses[0]
    parts = []
    for i, sense in enumerate(en_senses):
        prefix = _CIRCLED[i] if i < len(_CIRCLED) else f"({i+1})"
        parts.append(f"{prefix} {sense}")
    return " ".join(parts)


def _format_info(word: dict) -> str:
    """Return tags, antonym, and usage notes as a compact string."""
    parts = []
    tags = word.get("tags", [])
    if tags:
        parts.append(" ".join(f"[{t}]" for t in tags))
    antonym = word.get("antonym", "")
    if antonym:
        parts.append(f"↔ {antonym}")
    for m in word.get("meanings", []):
        note = m.get("note", "")
        if note:
            parts.append(note)
            break  # only first note to keep cards concise
    return "  ".join(parts)


def _build_note(word: dict, model: genanki.Model) -> genanki.Note:
    """Build a genanki.Note for one vocabulary word."""
    kanji = word.get("kanji", "")
    kana = word.get("kana", "")
    expression = kanji if kanji else kana
    reading = kana if kanji else ""

    fields = [
        expression,
        reading,
        word.get("romaji", ""),
        _format_meaning_short(word),
        _format_meaning_full(word),
        word.get("pos", ""),
        _format_info(word),
    ]
    return genanki.Note(model=model, fields=fields)


# ── Public API ─────────────────────────────────────────────────────────────────

_JSON_FILE = Path(__file__).parent.parent / "data" / "vocabulary.json"
_OUTPUT_DIR = Path(__file__).parent.parent / "output"


def run_anki_export(level: str, output_path=None):
    """Build an Anki .apkg deck for one JLPT level and write it to output_path.

    Args:
        level: JLPT level string — normalised to uppercase internally (e.g. 'n5' → 'N5').
        output_path: str or Path to write the .apkg file, or None to use the default
                     <project_root>/output/anki_{level_lower}.apkg path.
    """
    level = level.upper()
    if output_path is None:
        _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = _OUTPUT_DIR / f"anki_{level.lower()}.apkg"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(_JSON_FILE, encoding="utf-8") as f:
        all_words = json.load(f)
    words = [w for w in all_words if w.get("jlpt") == level]

    model = _build_model()
    deck_name = f"Japanese {level} Vocabulary"
    deck = genanki.Deck(
        _stable_id(deck_name),
        deck_name,
        description=(
            "Word list: Jonathan Waller JLPT lists. "
            "Definitions: JMdict by the Electronic Dictionary Research "
            "and Development Group (CC BY-SA 3.0)."
        ),
    )
    for word in words:
        deck.add_note(_build_note(word, model))

    package = genanki.Package(deck)
    package.write_to_file(str(output_path))
    print(f"Generated {level} Anki deck ({len(words)} words) → {output_path}")


_ALL_LEVELS = ["N5", "N4", "N3", "N2", "N1"]


def run_anki_export_all(output_path=None):
    """Build a single .apkg containing all 5 JLPT levels as separate decks.

    Args:
        output_path: str or Path to write the .apkg file, or None to use the default
                     <project_root>/output/anki_all.apkg path.
    """
    if output_path is None:
        _OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        output_path = _OUTPUT_DIR / "anki_all.apkg"
    else:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)

    with open(_JSON_FILE, encoding="utf-8") as f:
        all_words = json.load(f)

    model = _build_model()
    decks = []
    total = 0
    for level in _ALL_LEVELS:
        words = [w for w in all_words if w.get("jlpt") == level]
        deck_name = f"Japanese {level} Vocabulary"
        deck = genanki.Deck(
            _stable_id(deck_name),
            deck_name,
            description=(
                "Word list: Jonathan Waller JLPT lists. "
                "Definitions: JMdict by the Electronic Dictionary Research "
                "and Development Group (CC BY-SA 3.0)."
            ),
        )
        for word in words:
            deck.add_note(_build_note(word, model))
        decks.append(deck)
        total += len(words)

    package = genanki.Package(decks)
    package.write_to_file(str(output_path))
    print(f"Generated all-levels Anki deck ({total} words, N5–N1) → {output_path}")
