#!/usr/bin/env python3
"""Generate printable kana flash cards and practice sheets."""
import argparse
import os
import sys
import config
from data.kana import HIRAGANA, KATAKANA
from renderer.pdf_renderer import generate_pdf
from renderer.practice_sheet import generate_practice_pdf
from renderer.chart import generate_chart_pdf, generate_stroke_order_pdf


def _update_strokes():
    """Download latest KanjiVG release and regenerate stroke data."""
    import json
    import shutil
    import tempfile
    import urllib.request
    import zipfile

    api_url = "https://api.github.com/repos/KanjiVG/kanjivg/releases/latest"
    cache_dir = os.path.join(os.path.dirname(__file__), ".kanjivg_cache")

    print("Finding latest KanjiVG release...")
    try:
        req = urllib.request.Request(api_url, headers={"Accept": "application/vnd.github+json"})
        with urllib.request.urlopen(req) as resp:
            release = json.loads(resp.read())
        url = None
        for asset in release.get("assets", []):
            if asset["name"].endswith("-all.zip"):
                url = asset["browser_download_url"]
                break
        if not url:
            print("Error: No '-all.zip' asset found in latest KanjiVG release")
            sys.exit(1)
    except Exception as e:
        print(f"Error finding KanjiVG release: {e}")
        sys.exit(1)

    print(f"Downloading {url}...")
    with tempfile.NamedTemporaryFile(suffix=".zip", delete=False) as tmp:
        tmp_path = tmp.name
    try:
        urllib.request.urlretrieve(url, tmp_path)
    except Exception as e:
        print(f"Error downloading KanjiVG: {e}")
        os.unlink(tmp_path)
        sys.exit(1)

    print(f"Extracting to {cache_dir}...")
    if os.path.exists(cache_dir):
        shutil.rmtree(cache_dir)
    os.makedirs(cache_dir)
    with zipfile.ZipFile(tmp_path) as zf:
        for member in zf.namelist():
            if member.endswith(".svg"):
                filename = os.path.basename(member)
                with zf.open(member) as src, open(os.path.join(cache_dir, filename), "wb") as dst:
                    dst.write(src.read())
    os.unlink(tmp_path)

    print("Regenerating stroke data...")
    from tools.generate_strokes_from_kanjivg import (
        HIRAGANA_CHARS, KATAKANA_CHARS, SMALL_HIRAGANA, SMALL_KATAKANA,
        generate_stroke_file,
    )

    hiragana_code = generate_stroke_file(HIRAGANA_CHARS, SMALL_HIRAGANA, "hiragana", cache_dir)
    out_h = os.path.join("data", "strokes", "hiragana.py")
    with open(out_h, "w") as f:
        f.write(hiragana_code)
    print(f"  Written to {out_h}")

    katakana_code = generate_stroke_file(KATAKANA_CHARS, SMALL_KATAKANA, "katakana", cache_dir)
    out_k = os.path.join("data", "strokes", "katakana.py")
    with open(out_k, "w") as f:
        f.write(katakana_code)
    print(f"  Written to {out_k}")

    print("Done! Run 'python -m pytest tests/test_strokes.py -v' to verify.")


def _generate_examples():
    """Generate example JPEG images from the first pages of flashcards and practice PDFs."""
    import shutil
    import subprocess
    import tempfile

    if not subprocess.run(["which", "pdftoppm"], capture_output=True).returncode == 0:
        print("Error: pdftoppm not found. Install poppler-utils:")
        print("  sudo apt install poppler-utils  (Debian/Ubuntu)")
        print("  brew install poppler             (macOS)")
        sys.exit(1)

    out_dir = "docs"
    os.makedirs(out_dir, exist_ok=True)

    with tempfile.TemporaryDirectory() as tmp:
        # Generate temporary PDFs
        flashcards_pdf = os.path.join(tmp, "flashcards.pdf")
        practice_pdf = os.path.join(tmp, "practice.pdf")
        chart_pdf = os.path.join(tmp, "chart.pdf")
        stroke_order_pdf = os.path.join(tmp, "stroke_order.pdf")

        cards = HIRAGANA + KATAKANA
        generate_pdf(cards, flashcards_pdf)
        generate_practice_pdf(cards, practice_pdf)

        kana_types = ["hiragana", "katakana"]
        generate_chart_pdf(kana_types, chart_pdf)
        generate_stroke_order_pdf(kana_types, stroke_order_pdf)

        # Extract pages as JPEG
        import glob
        for label, pdf, page in [
            ("flashcards-front", flashcards_pdf, 1),
            ("flashcards-back", flashcards_pdf, 2),
            ("practice", practice_pdf, 1),
            ("chart", chart_pdf, 1),
            ("stroke-order", stroke_order_pdf, 1),
        ]:
            prefix = os.path.join(tmp, label)
            subprocess.run([
                "pdftoppm", "-jpeg", "-f", str(page), "-l", str(page),
                "-r", "200", pdf, prefix,
            ], check=True)
            # pdftoppm zero-pads based on total pages; find the output file
            matches = glob.glob(f"{prefix}-*.jpg")
            tmp_jpg = matches[0]
            dest = os.path.join(out_dir, f"example_{label.replace('-', '_')}.jpg")
            shutil.move(tmp_jpg, dest)
            print(f"  Written to {dest}")

    print("Done! Example images updated in docs/.")


def main():
    parser = argparse.ArgumentParser(description="Generate kana flash cards and practice sheets")
    parser.add_argument("-o", "--output", default="output/kana_flashcards.pdf",
                        help="Output PDF path")
    parser.add_argument("--hiragana-only", action="store_true",
                        help="Only include hiragana")
    parser.add_argument("--katakana-only", action="store_true",
                        help="Only include katakana")
    parser.add_argument("--card-width", type=float, default=None,
                        help="Card width in mm (default: 55)")
    parser.add_argument("--card-height", type=float, default=None,
                        help="Card height in mm (default: 82)")
    parser.add_argument("--practice", action="store_true",
                        help="Generate practice worksheet instead of flash cards")
    parser.add_argument("--chart", action="store_true",
                        help="Generate reference chart instead of flash cards")
    parser.add_argument("--stroke-order", action="store_true",
                        help="Generate stroke order reference instead of flash cards")
    parser.add_argument("--update-strokes", action="store_true",
                        help="Download latest KanjiVG and regenerate stroke data")
    parser.add_argument("--generate-examples", action="store_true",
                        help="Regenerate example JPEG images in docs/")
    args = parser.parse_args()

    if args.update_strokes:
        _update_strokes()
        return

    if args.generate_examples:
        _generate_examples()
        return

    if args.card_width is not None or args.card_height is not None:
        config.set_card_size(
            args.card_width if args.card_width is not None else 55,
            args.card_height if args.card_height is not None else 82,
        )

    cards = []
    if not args.katakana_only:
        cards.extend(HIRAGANA)
    if not args.hiragana_only:
        cards.extend(KATAKANA)

    os.makedirs(os.path.dirname(args.output) or ".", exist_ok=True)
    kana_types = []
    if not args.katakana_only:
        kana_types.append("hiragana")
    if not args.hiragana_only:
        kana_types.append("katakana")

    if args.chart:
        if args.output == "output/kana_flashcards.pdf":
            args.output = "output/kana_chart.pdf"
        generate_chart_pdf(kana_types, args.output)
        print(f"Generated chart ({', '.join(kana_types)}) → {args.output}")
    elif args.stroke_order:
        if args.output == "output/kana_flashcards.pdf":
            args.output = "output/kana_stroke_order.pdf"
        generate_stroke_order_pdf(kana_types, args.output)
        print(f"Generated stroke order ({', '.join(kana_types)}) → {args.output}")
    elif args.practice:
        if args.output == "output/kana_flashcards.pdf":
            args.output = "output/kana_practice.pdf"
        generate_practice_pdf(cards, args.output)
    else:
        generate_pdf(cards, args.output)
    if not args.chart and not args.stroke_order:
        print(f"Generated {len(cards)} cards → {args.output}")


if __name__ == "__main__":
    main()
