"""tools/vocabulary_pdf.py — Build per-JLPT vocabulary PDFs from data/vocabulary.json."""
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


FONT_PATH = "fonts/KleeOne-SemiBold.ttf"
JSON_FILE = "data/vocabulary.json"

COLOR_HEADER_BG = colors.HexColor("#0d2137")
COLOR_ROW_ALT   = colors.HexColor("#f7f7f7")
COLOR_CAT_HDR   = colors.HexColor("#2d5a8c")

CIRCLED = ['①', '②', '③']


def font_has_chars(font_obj, text):
    """Return True if every character in text has a glyph in the given TTFont."""
    return all(font_obj.face.charToGlyph.get(ord(c)) is not None for c in text)


def _output_path(level: str, lang: str) -> Path:
    level_lower = level.lower()
    if lang == 'en':
        return Path(f"output/vocabulary_{level_lower}.pdf")
    return Path(f"output/vocabulary_{lang}_{level_lower}.pdf")


def _format_meanings(entry: dict, lang: str) -> str:
    """Build plain-text meaning cell content for a single entry."""
    senses      = entry.get('meanings', [])
    is_fallback = False

    if not senses:
        return '—'

    def _sense_text(sense: dict) -> str:
        nonlocal is_fallback
        loc  = sense.get('localized', {})
        text = loc.get(lang, '')
        if not text and lang != 'en':
            text        = loc.get('en', '')
            is_fallback = True
        note   = sense.get('note', '')
        result = text or '—'
        if note:
            result += f' — {note}'
        return result

    if len(senses) == 1:
        text = _sense_text(senses[0])
    else:
        text = '  '.join(f'{CIRCLED[i]} {_sense_text(s)}'
                         for i, s in enumerate(senses[:3]))

    tags = entry.get('tags', [])
    if tags:
        text += '  ' + ' '.join(f'[{t}]' for t in tags)

    antonym = entry.get('antonym', '')
    if antonym:
        text += f'  ↔ {antonym}'

    if is_fallback and lang != 'en':
        text += '  [en]'

    return text


def _footer_legend(lang: str) -> tuple:
    """Return (line1, line2) for the per-page footer legend."""
    sep = '  ·  '
    line1 = sep.join([
        '① ② … multiple meanings',
        '↔ antonym',
        '[uk] usually written in kana',
        '[col] informal/casual',
    ])
    line2_parts = ['[hon] honorific', '[hum] humble', '[arch] archaic', '[sl] slang']
    if lang != 'en':
        line2_parts.append('[en] meaning shown in English (no Swedish translation available)')
    return line1, sep.join(line2_parts)


def _group_by_category(words: list) -> list:
    """Group words by category field. Returns [(category_name, [words])] sorted
    alphabetically, with 'Other' last. Empty/None category counts as 'Other'.
    Within each group the existing word order (frequency_rank) is preserved.
    """
    groups = {}
    for word in words:
        cat = word.get('category') or 'Other'
        groups.setdefault(cat, []).append(word)

    sorted_keys = sorted(k for k in groups if k != 'Other')
    if 'Other' in groups:
        sorted_keys.append('Other')

    return [(k, groups[k]) for k in sorted_keys]


def build_pdf(words: list, level: str, lang: str, output_path: Path):
    klee_font = TTFont("KleeOne", FONT_PATH)
    pdfmetrics.registerFont(klee_font)
    output_path.parent.mkdir(parents=True, exist_ok=True)

    level_upper      = level.upper()
    footer_line1, footer_line2 = _footer_legend(lang)
    attribution  = (
        "Word list: Jonathan Waller JLPT lists. "
        "Definitions: JMdict by the Electronic Dictionary Research and Development Group "
        "(CC BY-SA 3.0)."
    )

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("KleeOne", 5.5)
        canvas.setFillColor(colors.HexColor("#888888"))
        canvas.drawString(12 * mm, 11 * mm, footer_line1)
        canvas.drawString(12 * mm,  7 * mm, footer_line2)
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=12 * mm,
        bottomMargin=18 * mm,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        title=f"JLPT {level_upper} Vocabulary",
        author="japanese-practice",
    )

    page_w     = A4[0] - 24 * mm
    col_widths = [page_w * 0.30, page_w * 0.18, page_w * 0.52]

    word_style    = ParagraphStyle("word",    fontName="KleeOne", fontSize=9,  leading=12)
    kana_style    = ParagraphStyle("kana",    fontName="KleeOne", fontSize=7,  leading=9,
                                   textColor=colors.HexColor("#555555"))
    romaji_style  = ParagraphStyle("romaji",  fontName="KleeOne", fontSize=8,  leading=11)
    meaning_style = ParagraphStyle("meaning", fontName="KleeOne", fontSize=8,  leading=11)
    col_hdr_style = ParagraphStyle("col_hdr", fontName="Helvetica-Bold", fontSize=9,
                                   leading=12, textColor=colors.white)
    title_style   = ParagraphStyle("title",   fontName="KleeOne", fontSize=16, leading=20,
                                   spaceAfter=2 * mm,
                                   textColor=colors.HexColor("#1a3a5c"))
    sub_style     = ParagraphStyle("sub",     fontName="KleeOne", fontSize=8,  leading=11,
                                   spaceAfter=4 * mm,
                                   textColor=colors.HexColor("#888888"))
    cat_hdr_style = ParagraphStyle("cat_hdr", fontName="Helvetica-Bold", fontSize=9,
                                   leading=12, textColor=colors.white)

    table_data = [[
        Paragraph("Word",    col_hdr_style),
        Paragraph("Romaji",  col_hdr_style),
        Paragraph("Meaning", col_hdr_style),
    ]]
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_HEADER_BG),
        ("GRID",       (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("VALIGN",     (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING",    (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING",   (0, 0), (-1, -1), 5),
        ("RIGHTPADDING",  (0, 0), (-1, -1), 5),
    ]

    row_idx = 1
    word_row_count = 0
    for entry in words:
        kana  = entry['kana']
        kanji = entry.get('kanji', '')

        if kanji and font_has_chars(klee_font, kanji):
            word_cell = [Paragraph(kanji, word_style), Paragraph(f'({kana})', kana_style)]
        else:
            word_cell = Paragraph(kana, word_style)

        table_data.append([
            word_cell,
            Paragraph(entry.get('romaji', ''), romaji_style),
            Paragraph(_format_meanings(entry, lang), meaning_style),
        ])
        if word_row_count % 2 == 1:
            style_cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), COLOR_ROW_ALT))
        word_row_count += 1
        row_idx += 1

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle(style_cmds))

    story = [
        Paragraph(f"JLPT {level_upper} — {len(words)} words", title_style),
        Paragraph(attribution, sub_style),
        table,
    ]
    doc.build(story, onFirstPage=on_page, onLaterPages=on_page)
