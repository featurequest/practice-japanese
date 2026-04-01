# tests/test_build_jlpt_vocabulary.py
import io, sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from tools.build_jlpt_vocabulary import (
    _parse_jmdict_xml,
    _map_pos,
    _get_priority_score,
    _build_no_match_entry,
    _assign_frequency_ranks,
    _build_vocab_entry,
    _parse_jlpt_csv,
)

# Minimal JMdict XML (no DOCTYPE needed — use the already-resolved form
# that _parse_jmdict_xml expects: entity refs replaced with their names)
SAMPLE_JMDICT = """<?xml version="1.0" encoding="UTF-8"?>
<JMdict>
<entry>
  <ent_seq>1578850</ent_seq>
  <k_ele><keb>遅い</keb><ke_pri>ichi1</ke_pri></k_ele>
  <r_ele><reb>おそい</reb><re_pri>ichi1</re_pri></r_ele>
  <sense>
    <pos>adj-i</pos>
    <gloss xml:lang="eng">slow</gloss>
    <gloss xml:lang="eng">late</gloss>
    <gloss xml:lang="eng">dull</gloss>
    <gloss xml:lang="swe">långsam</gloss>
    <ant>早い</ant>
    <s_inf>not used for clock time</s_inf>
  </sense>
</entry>
<entry>
  <ent_seq>1234567</ent_seq>
  <r_ele><reb>たべる</reb></r_ele>
  <sense>
    <pos>v1</pos>
    <misc>col</misc>
    <gloss xml:lang="eng">to eat</gloss>
    <gloss xml:lang="eng">to consume</gloss>
    <gloss xml:lang="eng">to munch</gloss>
    <gloss xml:lang="eng">should be capped at 3</gloss>
  </sense>
</entry>
</JMdict>
"""

def test_parse_indexes_by_kana():
    kana_idx, _ = _parse_jmdict_xml(SAMPLE_JMDICT)
    assert 'おそい' in kana_idx
    assert 'たべる' in kana_idx

def test_parse_indexes_by_kanji():
    _, kanji_idx = _parse_jmdict_xml(SAMPLE_JMDICT)
    assert '遅い' in kanji_idx

def test_meanings_en_capped_at_3():
    # One sense with 4 glosses: glosses are joined, 4th is dropped (cap at 3 per sense)
    kana_idx, _ = _parse_jmdict_xml(SAMPLE_JMDICT)
    entry = kana_idx['たべる'][0]
    assert entry['senses'][0]['localized']['en'] == 'to eat; to consume; to munch'

def test_meanings_sv():
    kana_idx, _ = _parse_jmdict_xml(SAMPLE_JMDICT)
    entry = kana_idx['おそい'][0]
    assert entry['senses'][0]['localized']['sv'] == 'långsam'

def test_meanings_sv_empty_when_none():
    # Sense has EN glosses but no SV → sv = ''
    kana_idx, _ = _parse_jmdict_xml(SAMPLE_JMDICT)
    entry = kana_idx['たべる'][0]
    assert entry['senses'][0]['localized']['sv'] == ''

def test_sv_from_separate_sense():
    # JMdict puts each language in its own <sense> element; SV-only senses
    # should be paired with the first EN sense that lacks SV.
    jmdict_sep = """<?xml version="1.0" encoding="UTF-8"?>
<JMdict>
<entry>
  <ent_seq>9999001</ent_seq>
  <r_ele><reb>テスト</reb></r_ele>
  <sense><pos>n</pos><gloss>test</gloss></sense>
  <sense><gloss xml:lang="swe">prov</gloss><gloss xml:lang="swe">test</gloss></sense>
</entry>
</JMdict>"""
    kana_idx, _ = _parse_jmdict_xml(jmdict_sep)
    entry = kana_idx['テスト'][0]
    assert entry['senses'][0]['localized']['en'] == 'test'
    assert entry['senses'][0]['localized']['sv'] == 'prov; test'

def test_pos_adjective():
    kana_idx, _ = _parse_jmdict_xml(SAMPLE_JMDICT)
    assert kana_idx['おそい'][0]['pos'] == 'adjective'

def test_pos_verb():
    kana_idx, _ = _parse_jmdict_xml(SAMPLE_JMDICT)
    assert kana_idx['たべる'][0]['pos'] == 'verb'

def test_tags_col():
    kana_idx, _ = _parse_jmdict_xml(SAMPLE_JMDICT)
    assert 'col' in kana_idx['たべる'][0]['tags']

def test_antonym_stored():
    kana_idx, _ = _parse_jmdict_xml(SAMPLE_JMDICT)
    assert kana_idx['おそい'][0]['antonym_kanji'] == '早い'

def test_priority_score_ichi1():
    assert _get_priority_score(['ichi1']) == 1
    assert _get_priority_score(['news1']) == 1

def test_priority_score_ichi2():
    assert _get_priority_score(['ichi2']) == 2
    assert _get_priority_score(['news2']) == 2

def test_priority_score_spec1():
    assert _get_priority_score(['spec1']) == 3
    assert _get_priority_score(['gai1']) == 3

def test_priority_score_spec2():
    assert _get_priority_score(['spec2']) == 4
    assert _get_priority_score(['gai2']) == 4

def test_priority_score_none():
    assert _get_priority_score([]) == 5
    assert _get_priority_score(['nf10']) == 5

def test_map_pos_noun():
    assert _map_pos('n') == 'noun'
    assert _map_pos('n-adv') == 'noun'
    assert _map_pos('n-t') == 'noun'

def test_map_pos_verb():
    assert _map_pos('v1') == 'verb'
    assert _map_pos('v5r') == 'verb'
    assert _map_pos('v5b') == 'verb'
    assert _map_pos('vk') == 'verb'
    assert _map_pos('vs-i') == 'verb'

def test_map_pos_adjective():
    assert _map_pos('adj-i') == 'adjective'
    assert _map_pos('adj-na') == 'adjective'

def test_map_pos_adverb():
    assert _map_pos('adv') == 'adverb'
    assert _map_pos('adv-to') == 'adverb'

def test_map_pos_particle():
    assert _map_pos('prt') == 'particle'

def test_map_pos_expression():
    assert _map_pos('exp') == 'expression'

def test_map_pos_other():
    assert _map_pos('xyz') == 'other'
    assert _map_pos('conj') == 'other'

def test_sinf_notes_extracted():
    # note lives inside the sense object it belongs to
    kana_idx, _ = _parse_jmdict_xml(SAMPLE_JMDICT)
    assert kana_idx['おそい'][0]['senses'][0]['note'] == 'not used for clock time'

def test_no_match_fallback_fields():
    stderr = io.StringIO()
    entry = _build_no_match_entry('じんこうちのう', '人工知能', 'artificial intelligence', 'N3', stderr)
    assert entry['kana'] == 'じんこうちのう'
    assert entry['meanings'] == [{'localized': {'en': 'artificial intelligence', 'sv': ''}, 'note': ''}]
    assert entry['pos'] == 'other'
    assert entry['tags'] == []
    assert entry['antonym'] == ''
    assert entry['jlpt'] == 'N3'
    assert entry['category'] == ''

def test_no_match_fallback_warns_stderr():
    stderr = io.StringIO()
    _build_no_match_entry('てすと', '', 'test', 'N5', stderr)
    assert 'てすと' in stderr.getvalue()

def test_frequency_ranks_within_level():
    words = [
        {'kana': 'う', 'jlpt': 'N5', '_priority': 3},
        {'kana': 'い', 'jlpt': 'N5', '_priority': 1},
        {'kana': 'あ', 'jlpt': 'N5', '_priority': 1},
        {'kana': 'え', 'jlpt': 'N4', '_priority': 2},
    ]
    result = _assign_frequency_ranks(words)
    n5 = sorted([w for w in result if w['jlpt'] == 'N5'], key=lambda w: w['frequency_rank'])
    # priority-1 words come first, alphabetical within ties
    assert n5[0]['kana'] == 'あ'
    assert n5[0]['frequency_rank'] == 1
    assert n5[1]['kana'] == 'い'
    assert n5[1]['frequency_rank'] == 2
    assert n5[2]['kana'] == 'う'
    assert n5[2]['frequency_rank'] == 3

def test_frequency_ranks_independent_per_level():
    words = [
        {'kana': 'あ', 'jlpt': 'N5', '_priority': 5},
        {'kana': 'い', 'jlpt': 'N4', '_priority': 5},
    ]
    result = _assign_frequency_ranks(words)
    for w in result:
        assert w['frequency_rank'] == 1  # each is rank 1 in its own level

def test_frequency_ranks_removes_priority_field():
    words = [{'kana': 'あ', 'jlpt': 'N5', '_priority': 1}]
    result = _assign_frequency_ranks(words)
    assert '_priority' not in result[0]

def test_uk_tag_clears_kanji():
    jmdict_uk = """<?xml version="1.0" encoding="UTF-8"?>
<JMdict>
<entry>
  <ent_seq>9999999</ent_seq>
  <k_ele><keb>有難う</keb></k_ele>
  <r_ele><reb>ありがとう</reb></r_ele>
  <sense>
    <pos>exp</pos>
    <misc>uk</misc>
    <gloss xml:lang="eng">thank you</gloss>
  </sense>
</entry>
</JMdict>"""
    kana_idx, _ = _parse_jmdict_xml(jmdict_uk)
    jmdict_entry = kana_idx['ありがとう'][0]
    assert 'uk' in jmdict_entry['tags']
    vocab_entry = _build_vocab_entry(
        kana='ありがとう', kanji='有難う', en_gloss='thank you',
        jmdict_entry=jmdict_entry, jlpt='N5', romaji_lookup={}
    )
    assert vocab_entry['kanji'] == ''
    assert 'uk' in vocab_entry['tags']

def test_parse_jlpt_csv_basic():
    csv = "Expression,Reading,English\n食べる,たべる,to eat"
    words = _parse_jlpt_csv(csv)
    assert len(words) == 1
    assert words[0]['kana'] == 'たべる'
    assert words[0]['kanji'] == '食べる'
    assert words[0]['en_gloss'] == 'to eat'

def test_parse_jlpt_csv_kana_only():
    # When Expression == Reading, kanji should be empty
    csv = "Expression,Reading,English\nたべる,たべる,to eat"
    words = _parse_jlpt_csv(csv)
    assert words[0]['kana'] == 'たべる'
    assert words[0]['kanji'] == ''

def test_parse_jlpt_csv_gloss_with_comma():
    # English gloss may contain commas; the field must be quoted (standard CSV)
    csv = 'Expression,Reading,English\n食べる,たべる,"to eat, to consume"'
    words = _parse_jlpt_csv(csv)
    assert words[0]['en_gloss'] == 'to eat, to consume'

def test_parse_jlpt_csv_skips_short_lines():
    csv = "Expression,Reading,English\n食べる,たべる\n水,みず,water"
    words = _parse_jlpt_csv(csv)
    assert len(words) == 1
    assert words[0]['kana'] == 'みず'
