# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python tool that generates printable flash cards and handwriting practice sheets for Japanese hiragana and katakana characters with stroke order diagrams. Outputs PDFs with 208 cards (104 per script) in configurable sizes, plus landscape practice worksheets.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Check prerequisites (font, vocabulary data, packages)
python generate.py --setup

# Generate kana PDFs
python generate.py --kana                              # Flash cards (208 cards)
python generate.py --kana --hiragana-only              # Hiragana only
python generate.py --kana --katakana-only              # Katakana only
python generate.py --kana -o path/to/out.pdf           # Custom output path
python generate.py --kana --card-width 63 --card-height 88  # Custom size (mm)
python generate.py --kana --practice                   # Practice sheets
python generate.py --kana --chart                      # Reference chart
python generate.py --kana --stroke-order               # Stroke order guide

# Vocabulary data
python generate.py --build-vocabulary                  # Download JMdict + JLPT lists (~50MB), build vocabulary.json
python tools/build_jlpt_vocabulary.py --dry-run        # Preview stats, no write
python tools/build_jlpt_vocabulary.py --cache-only     # Use cached downloads

# Generate vocabulary PDFs
python generate.py --vocabulary --jlpt n5              # N5 English → output/vocabulary_n5.pdf
python generate.py --vocabulary --jlpt n5 --lang sv    # N5 Swedish → output/vocabulary_sv_n5.pdf
python generate.py --anki --jlpt n5                    # N5 Anki deck → output/anki_n5.apkg
python generate.py --anki                              # All 5 levels + combined output/anki_all.apkg

# Run tests
python -m pytest tests/ -v
python -m pytest tests/test_stroke_diagram.py -v      # Single test file
python -m pytest tests/test_kana.py::test_name -v     # Single test

# Maintenance (developer)
python generate.py --update-strokes       # Re-download KanjiVG and regenerate stroke data
python generate.py --generate-examples    # Regenerate example images in docs/
```

The Klee One SemiBold font is bundled in `fonts/` (SIL OFL licensed).

## Architecture

**Data/rendering separation** — `data/` contains pure data models and kana definitions; `renderer/` handles all PDF drawing. Neither crosses into the other's domain.

### Data Layer (`data/`)
- `models.py` — `Stroke` (normalized 0-1 polyline + SVG path) and `KanaCard` dataclasses
- `kana.py` — All 208 card definitions (HIRAGANA, KATAKANA lists)
- `strokes/` — Stroke order data from KanjiVG. Base characters and dakuten/handakuten are fetched directly from KanjiVG SVGs. Yōon variants are composed via `make_yoon()` in `helpers.py`.

### Rendering Layer (`renderer/`)
- `pdf_renderer.py` — Flash card page layout, auto-computed grid, front/back page pairing with column mirroring for duplex
- `card_front.py` — Large character (Klee One font) + type label
- `card_back.py` — Romaji + stroke diagram
- `stroke_diagram.py` — Renders KanjiVG SVG paths with numbered stroke indicators
- `practice_sheet.py` — Landscape A4 practice worksheets with 2cm grid boxes and dashed cross guides
- `chart.py` — Reference chart (landscape A4, gojūon table with romaji) and stroke order (portrait A4, KanjiVG diagrams split across multiple pages for readability)

### Configuration (`config.py`)
All tunables are centralized: paper size, card dimensions, grid layout (auto-computed from card size), font sizes, stroke colors, cut line style, and `BACK_PAGE_OFFSET_Y` for printer duplex alignment compensation. `set_card_size()` validates dimensions and recomputes grid/margins.

### CLI (`generate.py`)
Single entry point for all operations. Run without arguments to see help. Dispatches to `tools/` modules:
- `--kana` — kana PDF generation (flash cards, practice, chart, stroke order)
- `--vocabulary` — vocabulary PDFs via `tools/vocabulary_pdf.py`
- `--setup` — prerequisite check via `tools/setup.py`
- `--build-vocabulary` — vocabulary data build via `tools/build_jlpt_vocabulary.py`
- `--update-strokes` — KanjiVG update via `tools/update_strokes.py`
- `--generate-examples` — example image generation via `tools/generate_examples.py`

### Tools (`tools/`)
- `build_jlpt_vocabulary.py` — Downloads JLPT word lists + JMdict; builds `data/vocabulary.json`
- `vocabulary_pdf.py` — PDF rendering logic for vocabulary reference sheets
- `anki_export.py` — Builds Anki `.apkg` decks from vocabulary data
- `setup.py` — Checks prerequisites; auto-builds vocabulary data if absent
- `update_strokes.py` — Downloads latest KanjiVG release; regenerates `data/strokes/*.py`
- `generate_examples.py` — Renders example JPEGs for `docs/`; requires poppler-utils
- `generate_strokes_from_kanjivg.py` — Library for extracting stroke paths from KanjiVG SVGs

## Coordinate Systems

Three coordinate spaces in use — mixing them up is the most common source of bugs:
- **Stroke data (0-1 normalized):** X: 0=left→1=right, Y: 0=top→1=bottom
- **KanjiVG SVG (109×109):** Raw SVG viewBox coordinates from external source
- **ReportLab PDF:** Origin at bottom-left, Y increases upward (inverted from stroke data)

`stroke_diagram.py` has `to_pdf_x()`/`to_pdf_y()` for conversion.

## Key Patterns

- **Canvas state isolation:** All drawing functions use `saveState()`/`restoreState()` pairs
- **Double-sided mirroring:** Front columns map to reversed back columns for long-edge duplex flip. Back page Y is offset by `BACK_PAGE_OFFSET_Y`.
- **Auto grid:** `COLS`/`ROWS` are computed from card size, so custom dimensions always fit the page
- **Mock canvas testing:** Renderer tests use `MagicMock()` instead of generating actual PDFs

## Documentation

When adding new CLI flags, new commands, or changing existing behavior: update **both** the `README.md` Usage section and the argparse help text in `generate.py` in the same commit. The README and `--help` output are the primary user-facing docs and must stay in sync with the code.

When adding new modules or changing architecture, update the Architecture section of this file and `README.md`.

## Licenses

- **KanjiVG** stroke data: CC BY-SA 3.0 — attribution and share-alike required
- **Klee One** font: SIL Open Font License 1.1 — OFL text in `fonts/OFL-KleeOne.txt`
