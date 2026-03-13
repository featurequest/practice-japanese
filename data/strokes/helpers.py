"""Shared helpers for composing stroke variants (dakuten, handakuten, yōon)."""
import math
import re
from data.models import Stroke


def _transform_svg_d(d: str, scale_x: float, scale_y: float,
                     offset_x: float, offset_y: float) -> str:
    """Transform an SVG path 'd' attribute by scaling and offsetting coordinates.

    Handles absolute commands (M, C, S, Q, L, H, V) and relative commands
    (m, c, s, q, l, h, v). Absolute coords are scaled then offset; relative
    coords are only scaled.
    """
    if not d:
        return d

    # Tokenize: split into command letters and number tokens
    tokens = re.findall(r"[MmCcSsQqTtLlHhVvAaZz]|[+-]?(?:\d+\.?\d*|\.\d+)(?:[eE][+-]?\d+)?", d)

    result = []
    cmd = ""
    nums: list[float] = []

    def flush():
        if not cmd:
            return
        # Determine how many numbers per coordinate pair for this command
        transformed = _transform_nums(cmd, nums, scale_x, scale_y, offset_x, offset_y)
        result.append(cmd)
        for n in transformed:
            result.append(f"{n:.2f}")

    for token in tokens:
        if re.match(r"[A-Za-z]", token):
            flush()
            cmd = token
            nums = []
        else:
            nums.append(float(token))

    flush()
    return ",".join(result).replace(",M", " M").replace(",m", " m")


def _transform_nums(cmd: str, nums: list[float],
                    sx: float, sy: float, ox: float, oy: float) -> list[float]:
    """Transform coordinate numbers based on SVG command type."""
    out = list(nums)
    is_relative = cmd.islower()

    if cmd in ("Z", "z"):
        return out

    if cmd in ("H", "h"):
        # Single x coordinates
        for i in range(len(out)):
            if is_relative:
                out[i] *= sx
            else:
                out[i] = out[i] * sx + ox
        return out

    if cmd in ("V", "v"):
        # Single y coordinates
        for i in range(len(out)):
            if is_relative:
                out[i] *= sy
            else:
                out[i] = out[i] * sy + oy
        return out

    # All other commands: pairs of (x, y)
    for i in range(0, len(out) - 1, 2):
        if is_relative:
            out[i] *= sx
            out[i + 1] *= sy
        else:
            out[i] = out[i] * sx + ox
            out[i + 1] = out[i + 1] * sy + oy

    return out


def add_dakuten(base_strokes: list[Stroke]) -> list[Stroke]:
    """Add two short diagonal dakuten strokes at top-right."""
    n = len(base_strokes)
    return base_strokes + [
        Stroke(path=[(0.75, 0.05), (0.80, 0.15)], order=n + 1),
        Stroke(path=[(0.85, 0.05), (0.90, 0.15)], order=n + 2),
    ]


def add_handakuten(base_strokes: list[Stroke]) -> list[Stroke]:
    """Add a small circle (handakuten) at top-right."""
    n = len(base_strokes)
    cx, cy, r = 0.85, 0.10, 0.05
    pts = [(cx + r * math.cos(a), cy + r * math.sin(a))
           for a in [i * math.pi / 4 for i in range(9)]]
    return base_strokes + [Stroke(path=pts, order=n + 1)]


def make_yoon(base_strokes: list[Stroke], small_strokes: list[Stroke]) -> list[Stroke]:
    """Compose yōon: base char uniformly scaled + small char at bottom-right.

    Both characters are scaled uniformly (same factor for x and y) to preserve
    their natural proportions. Base is 0.6x size at left, small is 0.4x at
    bottom-right.
    """
    base_scale = 0.75
    small_scale = 0.55
    # Base: nearly full size, shifted slightly left
    base_ox = -0.02
    base_oy = (1.0 - base_scale) / 2  # center vertically
    # Small: tucked into bottom-right, bottom-aligned with base
    # Nudge up slightly (-0.04) to compensate for KanjiVG internal padding
    small_ox = 0.58
    small_oy = base_oy + base_scale - small_scale - 0.04

    result = []
    for s in base_strokes:
        result.append(Stroke(
            path=[(base_ox + x * base_scale, base_oy + y * base_scale) for x, y in s.path],
            order=s.order,
            svg_d=_transform_svg_d(s.svg_d, base_scale, base_scale,
                                   base_ox * 109, base_oy * 109) if s.svg_d else "",
        ))
    offset = len(base_strokes)
    for s in small_strokes:
        result.append(Stroke(
            path=[(small_ox + x * small_scale, small_oy + y * small_scale)
                  for x, y in s.path],
            order=offset + s.order,
            svg_d=_transform_svg_d(s.svg_d, small_scale, small_scale,
                                   small_ox * 109, small_oy * 109) if s.svg_d else "",
        ))
    return result


# Dakuten mappings: (base_romaji, dakuten_romaji)
DAKUTEN_PAIRS = [
    ("ka", "ga"), ("ki", "gi"), ("ku", "gu"), ("ke", "ge"), ("ko", "go"),
    ("sa", "za"), ("shi", "ji"), ("su", "zu"), ("se", "ze"), ("so", "zo"),
    ("ta", "da"), ("chi", "di"), ("tsu", "du"), ("te", "de"), ("to", "do"),
    ("ha", "ba"), ("hi", "bi"), ("fu", "bu"), ("he", "be"), ("ho", "bo"),
]

# Handakuten mappings: (base_romaji, handakuten_romaji)
HANDAKUTEN_PAIRS = [
    ("ha", "pa"), ("hi", "pi"), ("fu", "pu"), ("he", "pe"), ("ho", "po"),
]

# Yōon mappings: (base_romaji, small_romaji, yoon_romaji)
YOON_TRIPLES = [
    ("ki", "ya", "kya"), ("ki", "yu", "kyu"), ("ki", "yo", "kyo"),
    ("shi", "ya", "sha"), ("shi", "yu", "shu"), ("shi", "yo", "sho"),
    ("chi", "ya", "cha"), ("chi", "yu", "chu"), ("chi", "yo", "cho"),
    ("ni", "ya", "nya"), ("ni", "yu", "nyu"), ("ni", "yo", "nyo"),
    ("hi", "ya", "hya"), ("hi", "yu", "hyu"), ("hi", "yo", "hyo"),
    ("mi", "ya", "mya"), ("mi", "yu", "myu"), ("mi", "yo", "myo"),
    ("ri", "ya", "rya"), ("ri", "yu", "ryu"), ("ri", "yo", "ryo"),
    ("gi", "ya", "gya"), ("gi", "yu", "gyu"), ("gi", "yo", "gyo"),
    ("ji", "ya", "ja"), ("ji", "yu", "ju"), ("ji", "yo", "jo"),
    ("bi", "ya", "bya"), ("bi", "yu", "byu"), ("bi", "yo", "byo"),
    ("pi", "ya", "pya"), ("pi", "yu", "pyu"), ("pi", "yo", "pyo"),
]
