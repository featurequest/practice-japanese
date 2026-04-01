# tests/test_anki_export.py
import os
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.anki_export import (
    _stable_id,
    _format_meaning_short,
    _format_meaning_full,
    _format_info,
    _build_note,
    _build_model,
)

# ── Sample word dicts ──────────────────────────────────────────────────────────

WORD_WITH_KANJI = {
    "kana": "おそい",
    "kanji": "遅い",
    "romaji": "osoi",
    "meanings": [
        {"localized": {"en": "slow; late; dull"}, "note": "not used for clock time"},
        {"localized": {"en": "late (in the day)"}, "note": ""},
    ],
    "pos": "adjective",
    "tags": [],
    "antonym": "早い",
    "jlpt": "N5",
}

WORD_KANA_ONLY = {
    "kana": "ありがとう",
    "kanji": "",
    "romaji": "arigatou",
    "meanings": [
        {"localized": {"en": "thank you"}, "note": ""},
    ],
    "pos": "expression",
    "tags": ["uk"],
    "antonym": "",
    "jlpt": "N5",
}

WORD_MULTI_SENSE = {
    "kana": "あお",
    "kanji": "青",
    "romaji": "ao",
    "meanings": [
        {"localized": {"en": "blue; azure"}, "note": ""},
        {"localized": {"en": "green"}, "note": "mostly in compound words"},
        {"localized": {"en": "green light (traffic)"}, "note": ""},
    ],
    "pos": "noun",
    "tags": [],
    "antonym": "",
    "jlpt": "N5",
}


# ── Tests ──────────────────────────────────────────────────────────────────────

def test_stable_id_is_positive_int():
    result = _stable_id("Japanese N5 Vocabulary")
    assert isinstance(result, int)
    assert result >= 0
    assert result < 2**31


def test_stable_id_is_deterministic():
    assert _stable_id("Japanese N5 Vocabulary") == _stable_id("Japanese N5 Vocabulary")


def test_stable_id_differs_per_name():
    assert _stable_id("Japanese N5 Vocabulary") != _stable_id("Japanese N4 Vocabulary")


def test_note_fields_with_kanji():
    model = _build_model()
    note = _build_note(WORD_WITH_KANJI, model)
    fields = note.fields
    assert fields[0] == "遅い"        # Expression = kanji
    assert fields[1] == "おそい"      # Reading = kana (non-empty)


def test_note_fields_kana_only():
    model = _build_model()
    note = _build_note(WORD_KANA_ONLY, model)
    fields = note.fields
    assert fields[0] == "ありがとう"  # Expression = kana
    assert fields[1] == ""            # Reading = blank


def test_meaning_short_single_sense():
    result = _format_meaning_short(WORD_KANA_ONLY)
    assert result == "thank you"


def test_meaning_full_multiple_senses():
    result = _format_meaning_full(WORD_MULTI_SENSE)
    assert "①" in result
    assert "②" in result
    assert "blue" in result
    assert "green" in result


def test_info_includes_tags():
    result = _format_info(WORD_KANA_ONLY)
    assert "[uk]" in result


def test_info_includes_antonym():
    result = _format_info(WORD_WITH_KANJI)
    assert "↔ 早い" in result


def test_run_anki_export_creates_file(tmp_path):
    from tools.anki_export import run_anki_export
    out = tmp_path / "n5.apkg"
    run_anki_export("N5", out)
    assert out.exists()
    assert out.stat().st_size > 0


def test_run_anki_export_all_creates_file(tmp_path):
    from tools.anki_export import run_anki_export_all
    out = tmp_path / "all.apkg"
    run_anki_export_all(out)
    assert out.exists()
    # combined deck should be larger than a single level
    assert out.stat().st_size > 100_000
