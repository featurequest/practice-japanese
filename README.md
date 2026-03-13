# Japanese Kana Practice

Generate printable flash cards and handwriting practice sheets for all hiragana and katakana characters with stroke order diagrams.

Produces two types of PDF:
- **Flash cards** — 208 double-sided cards (104 hiragana + 104 katakana) arranged in a 3×3 grid on A4 pages, designed for duplex printing and cutting.
- **Practice sheets** — Landscape A4 pages with 2cm grid boxes. Each character gets 3 rows: the first box shows the KanjiVG stroke-order character, the rest are empty for handwriting practice. Boxes include dashed cross guides for centering.

## Downloads

Download the latest pre-built PDFs:

- [Flash cards 55×82mm](https://github.com/featurequest/practice-japanese/releases/latest/download/flashcards-55x82.pdf)
- [Flash cards 63×88mm](https://github.com/featurequest/practice-japanese/releases/latest/download/flashcards-63x88.pdf)
- [Flash cards 74×105mm](https://github.com/featurequest/practice-japanese/releases/latest/download/flashcards-74x105.pdf)
- [Practice sheets — Hiragana](https://github.com/featurequest/practice-japanese/releases/latest/download/practice-hiragana.pdf)
- [Practice sheets — Katakana](https://github.com/featurequest/practice-japanese/releases/latest/download/practice-katakana.pdf)

## Examples

**Flash cards — front (character) and back (romaji + stroke order):**

<p float="left">
  <img src="docs/example_flashcards_front.jpg" width="45%" />
  <img src="docs/example_flashcards_back.jpg" width="45%" />
</p>

**Practice sheet:**

<img src="docs/example_practice.jpg" width="90%" />

## Coverage

Each script includes:
- 46 basic gojūon (あ→ん / ア→ン)
- 20 dakuten variants (が, ざ, だ, ば / ガ, ザ, ダ, バ)
- 5 handakuten variants (ぱ行 / パ行)
- 33 yōon combinations (きゃ, しゅ, ちょ, etc.)

## Card Layout

| Front | Back |
|-------|------|
| Large kana character | Romaji reading |
| Type label (hiragana/katakana) | Stroke order diagram |

Cards are 55×82mm (roughly A7), printed 9 per A4 sheet with cut lines.

## Setup

```bash
pip install -r requirements.txt
```

Requires Python 3.10+ and [ReportLab](https://www.reportlab.com/). The Klee One font is bundled in the repository.

## Usage

```bash
# Flash cards
python generate.py                     # Full deck (208 cards)
python generate.py --hiragana-only     # Hiragana only
python generate.py --katakana-only     # Katakana only
python generate.py -o my_cards.pdf     # Custom output path

# Practice sheets
python generate.py --practice                    # Full set
python generate.py --practice --hiragana-only    # Hiragana only
python generate.py --practice --katakana-only    # Katakana only

# Custom card size (in mm, default: 55×82)
python generate.py --card-width 60 --card-height 90

# Maintenance
python generate.py --update-strokes      # Re-download KanjiVG and regenerate stroke data
python generate.py --generate-examples   # Regenerate example images in docs/
```

Flash cards default to `output/kana_flashcards.pdf`, practice sheets to `output/kana_practice.pdf`.

## Printing

1. Print the PDF double-sided with **long-edge flip**
2. Cut along the gray grid lines
3. Each card's front (character) aligns with its back (romaji + strokes)

Adjust `BACK_PAGE_OFFSET_Y` in `config.py` if your printer's duplex alignment is off.

## Licenses and Attribution

### Stroke Data — KanjiVG

Stroke order data derived from [KanjiVG](https://kanjivg.tagaini.net/) by Ulrich Apel, licensed under [Creative Commons Attribution-ShareAlike 3.0](https://creativecommons.org/licenses/by-sa/3.0/).

Adaptations: SVG stroke paths extracted, dakuten/handakuten/yōon variants composed from base characters for flash card and practice sheet rendering.

### Fonts

- **[Klee One SemiBold](https://github.com/fontworks-fonts/Klee)** by Fontworks — used for all Japanese text and labels. Licensed under the [SIL Open Font License 1.1](fonts/OFL-KleeOne.txt).
