# tests/test_generate_vocabulary.py
import os, sys, tempfile
from pathlib import Path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.vocabulary_pdf import (
    _output_path, _format_meanings, _footer_legend, _group_by_category,
    build_pdf,
)

# ── Output path ──────────────────────────────────────────────────────────────

def test_output_path_en():
    assert str(_output_path('N5', 'en')) == 'output/vocabulary_n5.pdf'

def test_output_path_sv():
    assert str(_output_path('N5', 'sv')) == 'output/vocabulary_sv_n5.pdf'

def test_output_path_n1_sv():
    assert str(_output_path('N1', 'sv')) == 'output/vocabulary_sv_n1.pdf'

def test_output_path_n2_en():
    assert str(_output_path('N2', 'en')) == 'output/vocabulary_n2.pdf'

# ── Meaning formatting ───────────────────────────────────────────────────────

MULTI = {'meanings': [
    {'localized': {'en': 'slow', 'sv': 'sakta'}, 'note': ''},
    {'localized': {'en': 'late', 'sv': ''},       'note': ''},
    {'localized': {'en': 'dull', 'sv': ''},       'note': ''},
], 'tags': [], 'antonym': ''}

SINGLE = {'meanings': [
    {'localized': {'en': 'to eat', 'sv': 'att äta'}, 'note': ''},
], 'tags': ['col'], 'antonym': ''}

WITH_ANT = {'meanings': [
    {'localized': {'en': 'slow', 'sv': ''}, 'note': ''},
], 'tags': [], 'antonym': 'hayai'}

WITH_NOTES = {'meanings': [
    {'localized': {'en': 'blue', 'sv': ''}, 'note': 'esp. of sky and sea'},
], 'tags': [], 'antonym': ''}

NO_SV = {'meanings': [
    {'localized': {'en': 'test', 'sv': ''}, 'note': ''},
], 'tags': [], 'antonym': ''}

def test_single_sense_no_circled_number():
    text = _format_meanings(SINGLE, 'en')
    assert '①' not in text
    assert 'to eat' in text

def test_multi_sense_circled_numbers():
    text = _format_meanings(MULTI, 'en')
    assert '① slow' in text
    assert '② late' in text
    assert '③ dull' in text

def test_tag_appended():
    text = _format_meanings(SINGLE, 'en')
    assert '[col]' in text

def test_antonym_appended():
    text = _format_meanings(WITH_ANT, 'en')
    assert '↔ hayai' in text

def test_notes_appended():
    # Note appears inline with its sense using ' — ' separator
    text = _format_meanings(WITH_NOTES, 'en')
    assert 'blue — esp. of sky and sea' in text

def test_sv_fallback_adds_en_marker():
    text = _format_meanings(NO_SV, 'sv')
    assert '[en]' in text
    assert 'test' in text

def test_sv_no_fallback_marker_when_sv_present():
    text = _format_meanings(SINGLE, 'sv')
    assert '[en]' not in text
    assert 'att äta' in text

# ── Footer legend ─────────────────────────────────────────────────────────────

def test_footer_en_has_no_en_marker():
    legend = ' '.join(_footer_legend('en'))
    assert '[en]' not in legend
    assert '[col]' in legend
    assert '↔' in legend

def test_footer_sv_has_en_marker():
    legend = ' '.join(_footer_legend('sv'))
    assert '[en]' in legend
    assert 'no Swedish translation available' in legend

# ── Category grouping ─────────────────────────────────────────────────────────

def test_group_by_category_basic():
    words = [
        {'category': 'Food', 'frequency_rank': 1},
        {'category': 'Colors', 'frequency_rank': 2},
        {'category': 'Food', 'frequency_rank': 3},
    ]
    groups = _group_by_category(words)
    names = [name for name, _ in groups]
    assert names == ['Colors', 'Food']

def test_group_by_category_other_last():
    words = [
        {'category': 'Food', 'frequency_rank': 1},
        {'category': '',     'frequency_rank': 2},
        {'category': 'Days', 'frequency_rank': 3},
    ]
    groups = _group_by_category(words)
    names = [name for name, _ in groups]
    assert names[-1] == 'Other'
    assert 'Days' in names
    assert 'Food' in names

def test_group_by_category_empty_string_is_other():
    words = [{'category': '', 'frequency_rank': 1},
             {'category': None, 'frequency_rank': 2}]
    groups = _group_by_category(words)
    assert len(groups) == 1
    assert groups[0][0] == 'Other'
    assert len(groups[0][1]) == 2

def test_group_by_category_preserves_order():
    words = [
        {'category': 'Food', 'frequency_rank': 1},
        {'category': 'Food', 'frequency_rank': 2},
        {'category': 'Food', 'frequency_rank': 3},
    ]
    groups = _group_by_category(words)
    food_words = groups[0][1]
    assert [w['frequency_rank'] for w in food_words] == [1, 2, 3]

# ── PDF build integration ─────────────────────────────────────────────────────

SAMPLE_WORDS = [
    {'kana': 'みず',   'kanji': '水',   'romaji': 'mizu',
     'meanings': [{'localized': {'en': 'water', 'sv': 'vatten'}, 'note': ''}],
     'pos': 'noun', 'jlpt': 'N5', 'frequency_rank': 1, 'tags': [], 'antonym': '', 'category': ''},
    {'kana': 'たべる', 'kanji': '食べる', 'romaji': 'taberu',
     'meanings': [{'localized': {'en': 'to eat', 'sv': ''},      'note': ''},
                  {'localized': {'en': 'to consume', 'sv': ''},  'note': ''}],
     'pos': 'verb', 'jlpt': 'N5', 'frequency_rank': 2, 'tags': ['col'], 'antonym': '', 'category': ''},
]

def test_build_pdf_creates_file():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'test_n5.pdf'
        build_pdf(SAMPLE_WORDS, 'N5', 'en', out)
        assert out.exists()
        assert out.stat().st_size > 500

def test_build_pdf_swedish():
    with tempfile.TemporaryDirectory() as tmp:
        out = Path(tmp) / 'test_sv_n5.pdf'
        build_pdf(SAMPLE_WORDS, 'N5', 'sv', out)
        assert out.exists()
        assert out.stat().st_size > 500
