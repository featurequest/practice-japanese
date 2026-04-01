"""tools/generate_examples.py — Render example JPEG images for docs/."""
import glob
import os
import shutil
import subprocess
import sys
import tempfile
from pathlib import Path


def run_generate_examples():
    """Generate example JPEG images from the first pages of various PDFs."""
    if not subprocess.run(["which", "pdftoppm"], capture_output=True).returncode == 0:
        print("Error: pdftoppm not found. Install poppler-utils:")
        print("  sudo apt install poppler-utils  (Debian/Ubuntu)")
        print("  brew install poppler             (macOS)")
        sys.exit(1)

    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    out_dir = os.path.join(project_root, "docs")
    os.makedirs(out_dir, exist_ok=True)

    from data.kana import HIRAGANA, KATAKANA
    from renderer.pdf_renderer import generate_pdf
    from renderer.practice_sheet import generate_practice_pdf
    from renderer.chart import generate_chart_pdf, generate_stroke_order_pdf

    with tempfile.TemporaryDirectory() as tmp:
        flashcards_pdf  = os.path.join(tmp, "flashcards.pdf")
        practice_pdf    = os.path.join(tmp, "practice.pdf")
        chart_pdf       = os.path.join(tmp, "chart.pdf")
        stroke_order_pdf = os.path.join(tmp, "stroke_order.pdf")
        vocabulary_pdf  = os.path.join(tmp, "vocabulary.pdf")

        cards = HIRAGANA + KATAKANA
        generate_pdf(cards, flashcards_pdf)
        generate_practice_pdf(cards, practice_pdf)
        generate_chart_pdf(["hiragana", "katakana"], chart_pdf)
        generate_stroke_order_pdf(["hiragana", "katakana"], stroke_order_pdf)

        import json
        vocab_path = os.path.join(project_root, "data", "vocabulary.json")
        with open(vocab_path, encoding="utf-8") as f:
            all_words = json.load(f)
        # Use N5 English as the vocabulary example page
        n5_words = [w for w in all_words if w.get("jlpt") == "N5"]
        from tools.vocabulary_pdf import build_pdf
        build_pdf(n5_words, "N5", "en", Path(vocabulary_pdf))

        for label, pdf, page in [
            ("flashcards-front", flashcards_pdf, 1),
            ("flashcards-back",  flashcards_pdf, 2),
            ("practice",         practice_pdf,   1),
            ("chart",            chart_pdf,      1),
            ("stroke-order",     stroke_order_pdf, 1),
            ("vocabulary",       vocabulary_pdf, 1),
        ]:
            prefix = os.path.join(tmp, label)
            subprocess.run([
                "pdftoppm", "-jpeg", "-f", str(page), "-l", str(page),
                "-r", "200", pdf, prefix,
            ], check=True)
            matches = glob.glob(f"{prefix}-*.jpg")
            tmp_jpg = matches[0]
            dest = os.path.join(out_dir, f"example_{label.replace('-', '_')}.jpg")
            shutil.move(tmp_jpg, dest)
            print(f"  Written to {dest}")

    print("Done! Example images updated in docs/.")
