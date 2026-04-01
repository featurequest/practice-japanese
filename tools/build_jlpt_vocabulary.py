#!/usr/bin/env python3
"""
tools/build_jlpt_vocabulary.py — Build data/vocabulary.json from JLPT word lists + JMdict.

Usage:
    python tools/build_jlpt_vocabulary.py              # download + build
    python tools/build_jlpt_vocabulary.py --dry-run    # preview stats, no write
    python tools/build_jlpt_vocabulary.py --cache-only # use cached files, skip network
"""
import argparse
import csv
import gzip
import json
import re
import sys
import urllib.request
from pathlib import Path
from xml.etree import ElementTree as ET

import pykakasi

CACHE_DIR   = Path(".jlpt_cache")
OUTPUT_FILE = Path("data/vocabulary.json")

# Jonathan Waller JLPT word list URLs (mirror: elzup/jlpt-word-list on GitHub).
# Format: CSV with header row "expression,reading,meaning[,tags]"
#   expression = kanji form if present, else kana
#   reading    = kana reading
# Original tanos.co.uk URLs return 404 as of 2026; using GitHub mirror instead.
JLPT_CSV_URLS = {
    "N5": "https://raw.githubusercontent.com/elzup/jlpt-word-list/master/src/n5.csv",
    "N4": "https://raw.githubusercontent.com/elzup/jlpt-word-list/master/src/n4.csv",
    "N3": "https://raw.githubusercontent.com/elzup/jlpt-word-list/master/src/n3.csv",
    "N2": "https://raw.githubusercontent.com/elzup/jlpt-word-list/master/src/n2.csv",
    "N1": "https://raw.githubusercontent.com/elzup/jlpt-word-list/master/src/n1.csv",
}

# ftp.edrdg.org has an SSL cert hostname mismatch; HTTP works fine.
JMDICT_URL  = "http://ftp.edrdg.org/pub/Nihongo/JMdict.gz"
VALID_TAGS  = {'uk', 'col', 'hon', 'hum', 'arch', 'sl'}

POS_MAP = {
    'n': 'noun', 'n-adv': 'noun', 'n-t': 'noun',
    'v1': 'verb', 'vk': 'verb', 'vs-i': 'verb',
    'adj-i': 'adjective', 'adj-na': 'adjective',
    'adv': 'adverb', 'adv-to': 'adverb',
    'prt': 'particle',
    'exp': 'expression',
}


def _map_pos(pos_name: str) -> str:
    if pos_name in POS_MAP:
        return POS_MAP[pos_name]
    if pos_name.startswith('v5'):
        return 'verb'
    return 'other'


def _get_priority_score(priority_tags: list) -> int:
    for tag in priority_tags:
        if tag in ('ichi1', 'news1'): return 1
        if tag in ('ichi2', 'news2'): return 2
        if tag in ('spec1', 'gai1'):  return 3
        if tag in ('spec2', 'gai2'):  return 4
    return 5


def _preprocess_jmdict(text: str) -> str:
    """Strip DOCTYPE and replace SGML entity references with their names as plain text.

    JMdict uses SGML entities like &n; &adj-i; &v1; inside XML elements.
    Python's ElementTree cannot parse SGML entity declarations, so we:
    1. Extract entity names from the DOCTYPE block.
    2. Remove the DOCTYPE entirely.
    3. Replace each &entity-name; with the entity name as text content.
    Standard XML entities (lt, gt, amp, quot, apos) are left alone.
    """
    entity_names = re.findall(r'<!ENTITY\s+(\S+)\s+"[^"]*"', text)
    text = re.sub(r'<!DOCTYPE[^[]*\[.*?\]>', '', text, flags=re.DOTALL)
    xml_builtins = {'lt', 'gt', 'amp', 'quot', 'apos'}
    for name in entity_names:
        if name not in xml_builtins:
            text = text.replace(f'&{name};', name)
    return text


def _parse_jmdict_xml(xml_text: str) -> tuple:
    """Parse JMdict XML text (already preprocessed or entity-free).

    Returns (kana_index, kanji_index).
    Each index: str -> list of entry dicts:
    {
        'kana_forms': list[str],
        'kanji_forms': list[str],
        'priority_score': int,
        'senses': list of {
            'localized': {'en': str, 'sv': str},
            'note': str,
        },
        'pos': str,
        'tags': list[str],
        'antonym_kanji': str,
    }
    """
    root = ET.fromstring(xml_text)
    kana_idx  = {}
    kanji_idx = {}

    for entry_el in root.findall('entry'):
        kanji_forms = []
        k_priorities = []
        for k_ele in entry_el.findall('k_ele'):
            keb = k_ele.findtext('keb', '')
            if keb:
                kanji_forms.append(keb)
            k_priorities += [el.text for el in k_ele.findall('ke_pri') if el.text]

        kana_forms = []
        r_priorities = []
        for r_ele in entry_el.findall('r_ele'):
            reb = r_ele.findtext('reb', '')
            if reb:
                kana_forms.append(reb)
            r_priorities += [el.text for el in r_ele.findall('re_pri') if el.text]

        priority_score = _get_priority_score(k_priorities + r_priorities)

        senses_data   = []   # [(en_list, sv_list, note)]
        sv_overflow   = []   # SV glosses from senses with no EN (JMdict puts
                             # each language in its own <sense> element)
        pos_name      = 'other'
        tags          = []
        antonym_kanji = ''

        for sense_el in entry_el.findall('sense'):
            pos_els = sense_el.findall('pos')
            if pos_els and pos_name == 'other':
                pos_name = _map_pos(pos_els[0].text or '')

            for misc_el in sense_el.findall('misc'):
                if misc_el.text in VALID_TAGS and misc_el.text not in tags:
                    tags.append(misc_el.text)

            # Skip sense if it only has field-domain tags and we already have content
            has_gloss  = bool(sense_el.findall('gloss'))
            field_only = sense_el.findall('field') and not has_gloss
            if field_only and (senses_data or sv_overflow):
                continue

            ant_el = sense_el.find('ant')
            if ant_el is not None and ant_el.text and not antonym_kanji:
                antonym_kanji = ant_el.text

            # Collect glosses for this sense (up to 3 glosses per sense)
            sense_en = []
            sense_sv = []
            for gloss_el in sense_el.findall('gloss'):
                lang = gloss_el.get(
                    '{http://www.w3.org/XML/1998/namespace}lang', 'eng')
                text = gloss_el.text or ''
                if not text:
                    continue
                if lang == 'eng' and len(sense_en) < 3:
                    sense_en.append(text)
                elif lang == 'swe' and len(sense_sv) < 3:
                    sense_sv.append(text)

            sinf_els = sense_el.findall('s_inf')
            sense_note = sinf_els[0].text if sinf_els and sinf_els[0].text else ''

            if sense_en:
                if len(senses_data) < 3:
                    senses_data.append((sense_en, sense_sv, sense_note))
            elif sense_sv:
                # SV-only sense: collect for pairing with EN senses later
                sv_overflow.extend(sense_sv)

        # Pair overflow SV with the first EN sense that has no SV.
        # JMdict often puts all SV translations in a single standalone sense,
        # so we can't map them 1:1 to EN senses; attaching to the first EN
        # sense is a reasonable approximation.
        for i, (en, sv, note) in enumerate(senses_data):
            if not sv and sv_overflow:
                senses_data[i] = (en, sv_overflow[:3], note)
                break

        senses = [{
            'localized': {
                'en': '; '.join(en),
                'sv': '; '.join(sv) if sv else '',
            },
            'note': note,
        } for en, sv, note in senses_data]

        entry_dict = {
            'kana_forms':    kana_forms,
            'kanji_forms':   kanji_forms,
            'priority_score': priority_score,
            'senses':        senses,
            'pos':           pos_name,
            'tags':          tags,
            'antonym_kanji': antonym_kanji,
        }

        for kana in kana_forms:
            kana_idx.setdefault(kana, []).append(entry_dict)
        for kanji in kanji_forms:
            kanji_idx.setdefault(kanji, []).append(entry_dict)

    return kana_idx, kanji_idx


def _best_entry(entries: list) -> dict:
    return min(entries, key=lambda e: e['priority_score'])


_kks = None

def _to_romaji(text: str) -> str:
    global _kks
    if _kks is None:
        _kks = pykakasi.kakasi()
    return ''.join(item['hepburn'] for item in _kks.convert(text))


def _build_no_match_entry(kana: str, kanji: str, en_gloss: str,
                           jlpt: str, stderr) -> dict:
    print(f"WARNING: no JMdict match for {kana} ({kanji}) [{jlpt}]", file=stderr)
    meanings = ([{'localized': {'en': en_gloss, 'sv': ''}, 'note': ''}]
                if en_gloss else [])
    return {
        'kana':    kana,
        'kanji':   kanji,
        'romaji':  _to_romaji(kana),
        'meanings': meanings,
        'pos':     'other',
        'jlpt':    jlpt,
        'frequency_rank': 0,
        '_priority': 5,
        'tags':    [],
        'antonym': '',
        'category': '',
    }


def _build_vocab_entry(kana: str, kanji: str, en_gloss: str,
                        jmdict_entry: dict, jlpt: str,
                        romaji_lookup: dict) -> dict:
    romaji = _to_romaji(kana)

    # uk tag: clear kanji field
    actual_kanji = '' if 'uk' in jmdict_entry['tags'] else kanji

    # Antonym romaji: check built words first, then pykakasi
    ant_kanji = jmdict_entry['antonym_kanji']
    antonym   = ''
    if ant_kanji:
        antonym = romaji_lookup.get(ant_kanji) or _to_romaji(ant_kanji)

    return {
        'kana':    kana,
        'kanji':   actual_kanji,
        'romaji':  romaji,
        'meanings': jmdict_entry['senses'],
        'pos':     jmdict_entry['pos'],
        'jlpt':    jlpt,
        'frequency_rank': 0,
        '_priority': jmdict_entry['priority_score'],
        'tags':    jmdict_entry['tags'],
        'antonym': antonym,
        'category': '',
    }


def _assign_frequency_ranks(words: list) -> list:
    """Assign 1-based frequency_rank within each JLPT level.
    Sort by _priority (asc), then kana alphabetically within ties.
    Removes the _priority helper field.
    """
    result = []
    for level in ('N5', 'N4', 'N3', 'N2', 'N1'):
        level_words = [w for w in words if w['jlpt'] == level]
        level_words.sort(key=lambda w: (w['_priority'], w['kana']))
        for i, w in enumerate(level_words):
            w = dict(w)
            w['frequency_rank'] = i + 1
            del w['_priority']
            result.append(w)
    return result


def _parse_jlpt_csv(content: str) -> list:
    """Parse JLPT word list CSV.

    Accepts two header formats (case-insensitive):
      - Original tanos format:  Expression,Reading,English[,...]
      - GitHub mirror format:   expression,reading,meaning[,tags,...]
    In both cases column 0 = kanji/expression, col 1 = kana reading,
    col 2 = English gloss (may be quoted and contain commas).
    """
    lines = content.strip().splitlines()
    if not lines:
        return []
    header = lines[0].lower()
    # Determine the meaning column name to confirm we have a recognised header,
    # but we always use positional columns 0/1/2 regardless.
    if not any(tok in header for tok in ('expression', 'meaning', 'english')):
        raise ValueError(f"Unrecognised CSV header: {lines[0]!r}")

    words = []
    for line in lines[1:]:   # skip header row
        parts = line.strip().split(',')
        if len(parts) < 3:
            continue
        expression = parts[0].strip()
        reading    = parts[1].strip()
        # Meaning may be a quoted field containing commas; reassemble it.
        # We only keep up to the next unquoted field (tags), so just join
        # the remaining parts and strip surrounding quotes.
        raw_meaning = ','.join(parts[2:]).strip()
        # Strip optional surrounding double-quotes and any trailing tag column.
        # The tags column (if present) is never quoted and contains spaces, e.g.
        # "JLPT JLPT_N5" — but since we joined all remaining parts with commas
        # the tags will already be inside the string.  We only want the gloss,
        # which appears first.  Handle the quoted-gloss case:
        #   "to meet, to see",JLPT ...  → parts[2]= '"to meet' parts[3]='to see"'  parts[4]='JLPT ...'
        # Rebuild properly using a CSV-aware approach.
        try:
            parsed = next(csv.reader([line]))
            expression = parsed[0].strip()
            reading    = parsed[1].strip()
            raw_meaning = parsed[2].strip() if len(parsed) > 2 else ''
        except Exception:
            pass  # fall back to the split above

        if not reading:
            continue
        if expression == reading or not expression:
            kana, kanji = reading, ''
        else:
            kana, kanji = reading, expression
        words.append({'kana': kana, 'kanji': kanji, 'en_gloss': raw_meaning})
    return words


def _download(url: str, dest: Path, cache_only: bool) -> bytes:
    if dest.exists():
        return dest.read_bytes()
    if cache_only:
        raise FileNotFoundError(f"Cache miss (--cache-only): {dest}")
    print(f"Downloading {url} ...", file=sys.stderr)
    with urllib.request.urlopen(url, timeout=60) as resp:
        data = resp.read()
    dest.write_bytes(data)
    return data


def build(dry_run: bool = False, cache_only: bool = False,
          stderr=sys.stderr) -> list:
    CACHE_DIR.mkdir(exist_ok=True)

    jmdict_bytes = _download(JMDICT_URL, CACHE_DIR / "JMdict.gz", cache_only)
    raw_text     = gzip.decompress(jmdict_bytes).decode('utf-8')
    xml_text     = _preprocess_jmdict(raw_text)
    kana_idx, kanji_idx = _parse_jmdict_xml(xml_text)
    print(f"JMdict: {len(kana_idx)} kana entries indexed", file=stderr)

    romaji_lookup: dict = {}
    all_words = []

    for level in ('N5', 'N4', 'N3', 'N2', 'N1'):
        cache_path = CACHE_DIR / f"jlpt_{level.lower()}.csv"
        csv_bytes  = _download(JLPT_CSV_URLS[level], cache_path, cache_only)
        jlpt_words = _parse_jlpt_csv(csv_bytes.decode('utf-8'))
        print(f"{level}: {len(jlpt_words)} words in source list", file=stderr)

        for word in jlpt_words:
            kana  = word['kana']
            kanji = word['kanji']

            jmdict_entry = None
            if kanji and kanji in kanji_idx:
                candidates = kanji_idx[kanji]
                narrowed   = [e for e in candidates if kana in e['kana_forms']]
                if narrowed:
                    jmdict_entry = _best_entry(narrowed)
                elif kana in kana_idx:
                    jmdict_entry = _best_entry(kana_idx[kana])
                # else: jmdict_entry remains None → no-match fallback
            elif kana in kana_idx:
                jmdict_entry = _best_entry(kana_idx[kana])

            if jmdict_entry:
                entry = _build_vocab_entry(kana, kanji, word['en_gloss'],
                                            jmdict_entry, level, romaji_lookup)
            else:
                entry = _build_no_match_entry(kana, kanji, word['en_gloss'],
                                               level, stderr)

            if kanji:
                romaji_lookup[kanji] = entry['romaji']

            all_words.append(entry)

    # Deduplicate by (jlpt, kana) — keep first occurrence
    seen   = set()
    deduped = []
    for w in all_words:
        key = (w['jlpt'], w['kana'])
        if key not in seen:
            seen.add(key)
            deduped.append(w)

    result = _assign_frequency_ranks(deduped)

    for level in ('N5', 'N4', 'N3', 'N2', 'N1'):
        n = sum(1 for w in result if w['jlpt'] == level)
        print(f"{level}: {n} words", file=stderr)
    print(f"Total: {len(result)} words", file=stderr)
    return result


def main():
    parser = argparse.ArgumentParser(
        description="Build data/vocabulary.json from JLPT word lists + JMdict")
    parser.add_argument('--dry-run',    action='store_true')
    parser.add_argument('--cache-only', action='store_true')
    args = parser.parse_args()

    words = build(dry_run=args.dry_run, cache_only=args.cache_only)

    if args.dry_run:
        print("Dry run — not writing output.")
        return

    OUTPUT_FILE.parent.mkdir(parents=True, exist_ok=True)

    # Preserve any manually-assigned categories from the existing file
    if OUTPUT_FILE.exists():
        with open(OUTPUT_FILE, encoding='utf-8') as f:
            existing = json.load(f)
        category_map = {(w['jlpt'], w['kana']): w.get('category', '')
                        for w in existing if w.get('category')}
        for w in words:
            w['category'] = category_map.get((w['jlpt'], w['kana']), '')

    with open(OUTPUT_FILE, 'w', encoding='utf-8') as f:
        json.dump(words, f, ensure_ascii=False, indent=2)
    print(f"Written {len(words)} words to {OUTPUT_FILE}")


if __name__ == '__main__':
    main()
