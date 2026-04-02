#!/usr/bin/env python3
"""Generate Japanese study materials: flash cards, practice sheets, vocabulary PDFs."""
import argparse
import json
import os
import subprocess
import sys
from pathlib import Path


def _default_output(args) -> str:
    """Return the default output path for the active mode."""
    if args.vocabulary:
        level = (args.jlpt or "n5").lower()
        if args.lang and args.lang != "en":
            return f"output/vocabulary_{args.lang}_{level}.pdf"
        return f"output/vocabulary_{level}.pdf"
    # kana modes
    if args.practice:
        return "output/kana_practice.pdf"
    if args.chart:
        return "output/kana_chart.pdf"
    if args.stroke_order:
        return "output/kana_stroke_order.pdf"
    return "output/kana_flashcards.pdf"


def main():
    parser = argparse.ArgumentParser(
        description="Generate Japanese study materials",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""\
Examples:
  python generate.py --kana                             Flash cards (208 cards)
  python generate.py --kana --practice                  Practice sheets
  python generate.py --kana --chart --hiragana-only     Hiragana reference chart
  python generate.py --kana --stroke-order              Stroke order guide
  python generate.py --vocabulary --jlpt n5             N5 vocabulary PDF (English)
  python generate.py --vocabulary --jlpt n3 --lang sv   N3 vocabulary PDF (Swedish)
  python generate.py --anki --jlpt n5                   N5 Anki deck → output/anki_n5.apkg
  python generate.py --anki                             All 5 levels (N5–N1)
  python generate.py --setup                            Check/download prerequisites
  python generate.py --build-vocabulary                 Rebuild vocabulary data from source
""",
    )

    kana_grp = parser.add_argument_group("Kana")
    kana_grp.add_argument("--kana", action="store_true",
                          help="Generate kana PDF (flash cards by default)")
    kana_grp.add_argument("--practice", action="store_true",
                          help="Practice sheets (use with --kana)")
    kana_grp.add_argument("--chart", action="store_true",
                          help="Reference chart (use with --kana)")
    kana_grp.add_argument("--stroke-order", action="store_true", dest="stroke_order",
                          help="Stroke order guide (use with --kana)")
    kana_grp.add_argument("--hiragana-only", action="store_true",
                          help="Hiragana only (use with --kana)")
    kana_grp.add_argument("--katakana-only", action="store_true",
                          help="Katakana only (use with --kana)")
    kana_grp.add_argument("--card-width", type=float, metavar="MM",
                          help="Card width in mm, default 55 (use with --kana)")
    kana_grp.add_argument("--card-height", type=float, metavar="MM",
                          help="Card height in mm, default 82 (use with --kana)")

    vocab_grp = parser.add_argument_group("Vocabulary")
    vocab_grp.add_argument("--vocabulary", action="store_true",
                           help="Generate vocabulary PDF")
    vocab_grp.add_argument("--jlpt", choices=["n5", "n4", "n3", "n2", "n1"],
                           metavar="{n5,n4,n3,n2,n1}",
                           help="JLPT level (required with --vocabulary)")
    vocab_grp.add_argument("--lang", choices=["en", "sv"], default="en",
                           help="Language, default en (use with --vocabulary)")
    vocab_grp.add_argument("--anki", action="store_true",
                           help="Generate Anki deck(s) (.apkg) for vocabulary")

    stories_grp = parser.add_argument_group("Stories")
    stories_grp.add_argument("--stories", action="store_true",
                             help="Generate reading-practice PDFs for all folk tales")

    maint_grp = parser.add_argument_group("Maintenance")
    maint_grp.add_argument("--setup", action="store_true",
                           help="Check prerequisites and download missing data")
    maint_grp.add_argument("--build-vocabulary", action="store_true", dest="build_vocabulary",
                           help="Force rebuild data/vocabulary.json from source")

    dev_grp = parser.add_argument_group("Developer")
    dev_grp.add_argument("--update-strokes", action="store_true", dest="update_strokes",
                         help="Re-download KanjiVG and regenerate stroke data")
    dev_grp.add_argument("--generate-examples", action="store_true", dest="generate_examples",
                         help="Regenerate example images in docs/ (requires poppler-utils)")

    parser.add_argument("-o", "--output", default=None,
                        help="Output PDF path (applies to --kana and --vocabulary)")

    if len(sys.argv) == 1:
        parser.print_help()
        return

    args = parser.parse_args()

    if args.setup:
        from tools.setup import run_setup
        run_setup()
        return

    if args.build_vocabulary:
        result = subprocess.run(
            [sys.executable, "tools/build_jlpt_vocabulary.py"],
            cwd=os.path.dirname(os.path.abspath(__file__)),
        )
        sys.exit(result.returncode)


    if args.update_strokes:
        from tools.update_strokes import run_update_strokes
        run_update_strokes()
        return

    if args.generate_examples:
        from tools.generate_examples import run_generate_examples
        run_generate_examples()
        return

    if args.vocabulary:
        if not args.jlpt:
            parser.error("--vocabulary requires --jlpt {n5,n4,n3,n2,n1}")
        from tools.vocabulary_pdf import build_pdf, JSON_FILE
        if not Path(JSON_FILE).exists():
            print(f"Error: {JSON_FILE} not found. Run: python generate.py --setup",
                  file=sys.stderr)
            sys.exit(1)
        with open(JSON_FILE, encoding="utf-8") as f:
            all_words = json.load(f)
        level = args.jlpt.upper()
        words = [w for w in all_words if w.get("jlpt") == level]
        out = Path(args.output) if args.output else Path(_default_output(args))
        print(f"Generating {level} vocabulary ({len(words)} words, lang={args.lang}) → {out}")
        build_pdf(words, level, args.lang, out)
        print(f"Saved to {out}")
        return

    if args.anki:
        from tools.anki_export import run_anki_export, run_anki_export_all
        if args.jlpt:
            run_anki_export(args.jlpt.upper(), args.output)
        else:
            if args.output:
                print("Warning: -o ignored when generating all levels", file=sys.stderr)
            for level in ["N5", "N4", "N3", "N2", "N1"]:
                run_anki_export(level)
            run_anki_export_all()
        return

    if args.stories:
        from data.stories import load_stories
        from tools.stories_pdf import generate_story_pdf
        for story in load_stories():
            out = Path(f"output/story_{story.slug}.pdf")
            print(f"Generating {story.title_en} → {out}")
            generate_story_pdf(story, out)
            print(f"Saved to {out}")
        return

    if args.kana:
        if args.hiragana_only and args.katakana_only:
            parser.error("--hiragana-only and --katakana-only are mutually exclusive")
        import config
        from data.kana import HIRAGANA, KATAKANA
        from renderer.pdf_renderer import generate_pdf
        from renderer.practice_sheet import generate_practice_pdf
        from renderer.chart import generate_chart_pdf, generate_stroke_order_pdf

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

        kana_types = []
        if not args.katakana_only:
            kana_types.append("hiragana")
        if not args.hiragana_only:
            kana_types.append("katakana")

        out = args.output or _default_output(args)
        os.makedirs(os.path.dirname(out) or ".", exist_ok=True)

        if args.chart:
            generate_chart_pdf(kana_types, out)
            print(f"Generated chart ({', '.join(kana_types)}) → {out}")
        elif args.stroke_order:
            generate_stroke_order_pdf(kana_types, out)
            print(f"Generated stroke order ({', '.join(kana_types)}) → {out}")
        elif args.practice:
            generate_practice_pdf(cards, out)
            print(f"Generated {len(cards)} cards → {out}")
        else:
            generate_pdf(cards, out)
            print(f"Generated {len(cards)} cards → {out}")
        return

    parser.print_help()


if __name__ == "__main__":
    main()
