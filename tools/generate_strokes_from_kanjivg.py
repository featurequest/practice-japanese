#!/usr/bin/env python3
"""Extract stroke data from local KanjiVG SVG files.

KanjiVG provides accurate stroke order data for Japanese characters.
Each SVG contains individual stroke paths in drawing order.
We parse the SVG path 'd' attribute to extract the start point and
initial direction of each stroke, normalized to 0-1 coordinates.

Used as a library by `generate.py --update-strokes`.
"""
import os
import re
import xml.etree.ElementTree as ET

# KanjiVG SVG viewBox is 109x109
VIEWBOX_SIZE = 109.0

# All characters we need stroke data for (base + dakuten + handakuten)
HIRAGANA_CHARS = {
    "a": "あ", "i": "い", "u": "う", "e": "え", "o": "お",
    "ka": "か", "ki": "き", "ku": "く", "ke": "け", "ko": "こ",
    "sa": "さ", "shi": "し", "su": "す", "se": "せ", "so": "そ",
    "ta": "た", "chi": "ち", "tsu": "つ", "te": "て", "to": "と",
    "na": "な", "ni": "に", "nu": "ぬ", "ne": "ね", "no": "の",
    "ha": "は", "hi": "ひ", "fu": "ふ", "he": "へ", "ho": "ほ",
    "ma": "ま", "mi": "み", "mu": "む", "me": "め", "mo": "も",
    "ya": "や", "yu": "ゆ", "yo": "よ",
    "ra": "ら", "ri": "り", "ru": "る", "re": "れ", "ro": "ろ",
    "wa": "わ", "wo": "を", "n": "ん",
    # Dakuten
    "ga": "が", "gi": "ぎ", "gu": "ぐ", "ge": "げ", "go": "ご",
    "za": "ざ", "ji": "じ", "zu": "ず", "ze": "ぜ", "zo": "ぞ",
    "da": "だ", "di": "ぢ", "du": "づ", "de": "で", "do": "ど",
    "ba": "ば", "bi": "び", "bu": "ぶ", "be": "べ", "bo": "ぼ",
    # Handakuten
    "pa": "ぱ", "pi": "ぴ", "pu": "ぷ", "pe": "ぺ", "po": "ぽ",
}

KATAKANA_CHARS = {
    "a": "ア", "i": "イ", "u": "ウ", "e": "エ", "o": "オ",
    "ka": "カ", "ki": "キ", "ku": "ク", "ke": "ケ", "ko": "コ",
    "sa": "サ", "shi": "シ", "su": "ス", "se": "セ", "so": "ソ",
    "ta": "タ", "chi": "チ", "tsu": "ツ", "te": "テ", "to": "ト",
    "na": "ナ", "ni": "ニ", "nu": "ヌ", "ne": "ネ", "no": "ノ",
    "ha": "ハ", "hi": "ヒ", "fu": "フ", "he": "ヘ", "ho": "ホ",
    "ma": "マ", "mi": "ミ", "mu": "ム", "me": "メ", "mo": "モ",
    "ya": "ヤ", "yu": "ユ", "yo": "ヨ",
    "ra": "ラ", "ri": "リ", "ru": "ル", "re": "レ", "ro": "ロ",
    "wa": "ワ", "wo": "ヲ", "n": "ン",
    # Dakuten
    "ga": "ガ", "gi": "ギ", "gu": "グ", "ge": "ゲ", "go": "ゴ",
    "za": "ザ", "ji": "ジ", "zu": "ズ", "ze": "ゼ", "zo": "ゾ",
    "da": "ダ", "di": "ヂ", "du": "ヅ", "de": "デ", "do": "ド",
    "ba": "バ", "bi": "ビ", "bu": "ブ", "be": "ベ", "bo": "ボ",
    # Handakuten
    "pa": "パ", "pi": "ピ", "pu": "プ", "pe": "ペ", "po": "ポ",
}

# Small kana for yōon composition
SMALL_HIRAGANA = {"ya": "ゃ", "yu": "ゅ", "yo": "ょ"}
SMALL_KATAKANA = {"ya": "ャ", "yu": "ュ", "yo": "ョ"}


def char_to_codepoint(char: str) -> str:
    """Convert a character to its zero-padded hex codepoint for KanjiVG filename."""
    return f"{ord(char):05x}"


def load_svg(char: str, kanjivg_dir: str) -> str | None:
    """Load SVG for a character from local KanjiVG directory."""
    cp = char_to_codepoint(char)
    path = os.path.join(kanjivg_dir, f"{cp}.svg")
    if os.path.exists(path):
        with open(path) as f:
            return f.read()
    print(f"  Warning: SVG not found for {char} (U+{cp}) at {path}")
    return None


def _tokenize_svg_numbers(s: str) -> list[float]:
    """Extract all numbers from an SVG path data string.

    Handles cases like '12.38-2.75' where - acts as separator,
    and '1.5.6' where a second decimal point starts a new number.
    """
    return [float(m) for m in re.findall(r"[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?", s)]


def parse_svg_path_start(d: str) -> tuple[float, float] | None:
    """Extract the starting point (M command) from an SVG path 'd' attribute."""
    d = d.strip()
    if not d or d[0] not in "Mm":
        return None
    # Get numbers after the M command
    # Find where the M command's data ends (next letter or end)
    rest = d[1:]
    nums = _tokenize_svg_numbers(re.split(r"[A-Za-z]", rest, maxsplit=1)[0])
    if len(nums) >= 2:
        return nums[0], nums[1]
    return None


def parse_svg_path_direction(d: str) -> tuple[float, float] | None:
    """Extract the initial direction point from the first segment after M.

    Returns the first control/end point after the M command to determine direction.
    """
    d = d.strip()
    # Split path into commands
    # Find all command letters and their positions
    commands = re.finditer(r"[MmCcSsQqTtLlHhVvAaZz]", d)
    cmd_list = list(commands)

    if len(cmd_list) < 2:
        # Only M command, check for implicit lineto (numbers after M's coords)
        if cmd_list and cmd_list[0].group() in "Mm":
            nums = _tokenize_svg_numbers(d[cmd_list[0].end():])
            if len(nums) >= 4:  # M x,y then implicit x,y
                return nums[2], nums[3]
        return None

    # Get the second command and its numbers
    second_cmd = cmd_list[1]
    cmd_char = second_cmd.group()
    # Get the data between this command and the next (or end)
    start_pos = second_cmd.end()
    end_pos = cmd_list[2].start() if len(cmd_list) > 2 else len(d)
    nums = _tokenize_svg_numbers(d[start_pos:end_pos])

    if not nums:
        return None

    # For relative commands (lowercase), add to start point
    start = parse_svg_path_start(d)
    if not start:
        return None

    # Handle single-axis commands (h/H, v/V)
    if cmd_char in "hH" and len(nums) >= 1:
        px = start[0] + nums[0] if cmd_char == "h" else nums[0]
        return px, start[1]
    if cmd_char in "vV" and len(nums) >= 1:
        py = start[1] + nums[0] if cmd_char == "v" else nums[0]
        return start[0], py

    # All two-coordinate commands (c/C, s/S, q/Q, l/L, and fallback)
    if len(nums) >= 2:
        if cmd_char.islower():
            return start[0] + nums[0], start[1] + nums[1]
        return nums[0], nums[1]

    return None


def extract_strokes_from_svg(svg_content: str) -> list[dict]:
    """Parse KanjiVG SVG and extract stroke data.

    Returns list of dicts with start/direction points (normalized 0-1)
    and the raw SVG path 'd' attribute for full rendering.
    """
    root = ET.fromstring(svg_content)
    strokes = []

    paths = root.findall(".//{http://www.w3.org/2000/svg}path")
    if not paths:
        paths = root.findall(".//path")

    for i, path in enumerate(paths):
        d = path.get("d", "")
        if not d:
            continue

        start = parse_svg_path_start(d)
        if start is None:
            continue

        direction = parse_svg_path_direction(d)
        if direction is None:
            direction = (start[0] + 5, start[1])

        # Normalize start/direction to 0-1
        sx, sy = start[0] / VIEWBOX_SIZE, start[1] / VIEWBOX_SIZE
        dx_pt, dy_pt = direction[0] / VIEWBOX_SIZE, direction[1] / VIEWBOX_SIZE

        strokes.append({
            "start": (round(sx, 3), round(sy, 3)),
            "direction": (round(dx_pt, 3), round(dy_pt, 3)),
            "order": i + 1,
            "svg_d": d.strip(),
        })

    return strokes


def format_stroke_data(romaji: str, strokes: list[dict]) -> str:
    """Format a single character's stroke data as Python code."""
    lines = []
    for s in strokes:
        sx, sy = s["start"]
        dx, dy = s["direction"]
        svg_d = s.get("svg_d", "")
        svg_part = f', svg_d="{svg_d}"' if svg_d else ""
        lines.append(
            f"        Stroke(path=[({sx}, {sy}), ({dx}, {dy})], order={s['order']}{svg_part}),"
        )
    return f'    "{romaji}": [\n' + "\n".join(lines) + "\n    ],"


def _generate_stroke_entries(chars: dict[str, str], kanjivg_dir: str,
                             label: str = "") -> list[str]:
    """Generate stroke data lines for a set of characters.

    Returns list of formatted Python code lines for a stroke dictionary.
    Raises SystemExit if any character's SVG is missing or has no strokes.
    """
    lines = []
    for romaji, char in chars.items():
        print(f"  Fetching {label}{char} ({romaji})...")
        svg = load_svg(char, kanjivg_dir)
        if not svg:
            raise SystemExit(f"Error: SVG file missing for {label}{char} ({romaji}). "
                             f"Check KanjiVG directory.")
        strokes = extract_strokes_from_svg(svg)
        if not strokes:
            raise SystemExit(f"Error: No strokes found in SVG for {label}{char} ({romaji}).")
        lines.append(format_stroke_data(romaji, strokes))
    return lines


def generate_stroke_file(chars: dict[str, str], small_chars: dict[str, str],
                         script_name: str, kanjivg_dir: str) -> str:
    """Generate the full Python stroke data file for a script (hiragana or katakana)."""
    header = f'''"""Stroke order data for all {script_name} characters.

Auto-generated from KanjiVG (https://github.com/KanjiVG/kanjivg).
Start/direction points are normalized 0-1. svg_d contains the original KanjiVG path
data (109x109 viewBox) for rendering actual brush strokes.
"""
from data.models import Stroke
from data.strokes.helpers import make_yoon, YOON_TRIPLES

'''

    base_entries = _generate_stroke_entries(chars, kanjivg_dir)
    base_lines = ["_BASE: dict[str, list[Stroke]] = {"] + base_entries + ["}"]

    small_entries = _generate_stroke_entries(small_chars, kanjivg_dir, label="small ")
    small_lines = ["\n_SMALL: dict[str, list[Stroke]] = {"] + small_entries + ["}"]

    # Composition code — dakuten/handakuten come directly from KanjiVG now,
    # only yōon still needs composition
    compose = f'''

# --- Compose all variants ---

{script_name.upper()}_STROKES: dict[str, list[Stroke]] = {{}}

# Add all base strokes (includes dakuten/handakuten from KanjiVG)
{script_name.upper()}_STROKES.update(_BASE)

# Yōon variants — compose base (including dakuten/handakuten) + small kana
for base_rom, small_rom, yoon_rom in YOON_TRIPLES:
    {script_name.upper()}_STROKES[yoon_rom] = make_yoon(_BASE[base_rom], _SMALL[small_rom])
'''

    return header + "\n".join(base_lines) + "\n" + "\n".join(small_lines) + compose


