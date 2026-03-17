# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

A Python tool that generates printable flash cards and handwriting practice sheets for Japanese hiragana and katakana characters with stroke order diagrams. Outputs PDFs with 208 cards (104 per script) in configurable sizes, plus landscape practice worksheets.

## Commands

```bash
# Install dependencies
pip install -r requirements.txt

# Generate flash cards
python generate.py                     # Full deck (208 cards)
python generate.py --hiragana-only     # Hiragana only
python generate.py --katakana-only     # Katakana only
python generate.py -o path/to/out.pdf  # Custom output path
python generate.py --card-width 63 --card-height 88  # Custom card size (mm)

# Generate practice sheets
python generate.py --practice                    # Full set
python generate.py --practice --hiragana-only    # Hiragana only

# Generate reference charts (landscape A4)
python generate.py --chart                       # Both scripts
python generate.py --chart --hiragana-only       # Hiragana only

# Generate stroke order (portrait A4)
python generate.py --stroke-order                       # Both scripts
python generate.py --stroke-order --hiragana-only       # Hiragana only

# Run tests
python -m pytest tests/ -v
python -m pytest tests/test_stroke_diagram.py -v      # Single test file
python -m pytest tests/test_kana.py::test_name -v     # Single test

# Download latest KanjiVG and regenerate stroke data
python generate.py --update-strokes

# Regenerate example images in docs/ (requires poppler-utils)
python generate.py --generate-examples
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
Single entry point for all operations: PDF generation, stroke data updates (`--update-strokes`), and example image regeneration (`--generate-examples`). The `--generate-examples` flag requires `pdftoppm` (poppler-utils) and writes JPEGs to `docs/`.

### Tools (`tools/`)
- `generate_strokes_from_kanjivg.py` — Library that extracts stroke data from local KanjiVG SVG files. Called by `generate.py --update-strokes`. Fails hard if any character's SVG is missing (no stub data). The `.kanjivg_cache/` directory is gitignored.

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

When adding new functionality or changing existing behavior, update both `CLAUDE.md` and `README.md` to reflect the changes. This includes new CLI flags, architecture changes, new files/modules, and configuration options.

## Licenses

- **KanjiVG** stroke data: CC BY-SA 3.0 — attribution and share-alike required
- **Klee One** font: SIL Open Font License 1.1 — OFL text in `fonts/OFL-KleeOne.txt`
