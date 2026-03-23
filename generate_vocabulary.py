#!/usr/bin/env python3
"""Generate a vocabulary reference PDF from data/vocabulary.json."""

import json
import sys
from pathlib import Path

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import ParagraphStyle
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

JSON_FILE = "data/vocabulary.json"
PDF_FILE = "output/vocabulary.pdf"
FONT_PATH = "fonts/KleeOne-SemiBold.ttf"

COLOR_H2_BG = colors.HexColor("#1a3a5c")
COLOR_H3_BG = colors.HexColor("#2d6a9f")
COLOR_H4_BG = colors.HexColor("#d0e8f5")
COLOR_ROW_ALT = colors.HexColor("#f7f7f7")
COLOR_HEADER_BG = colors.HexColor("#0d2137")


def _entries_from_words(words):
    """Reconstruct header+word entry list from the flat words list."""
    entries = []
    prev = {"section": None, "subsection": None, "sub_subsection": None}

    for word in words:
        s, ss, sss = word["section"], word["subsection"], word["sub_subsection"]

        if s != prev["section"]:
            entries.append({"type": "header", "level": 2, "text": s})
            prev = {"section": s, "subsection": None, "sub_subsection": None}

        if ss and ss != prev["subsection"]:
            entries.append({"type": "header", "level": 3, "text": ss})
            prev["subsection"] = ss
            prev["sub_subsection"] = None

        if sss and sss != prev["sub_subsection"]:
            entries.append({"type": "header", "level": 4, "text": sss})
            prev["sub_subsection"] = sss

        entries.append(word)

    return entries


def build_pdf(words, output_path):
    pdfmetrics.registerFont(TTFont("KleeOne", FONT_PATH))
    Path(output_path).parent.mkdir(parents=True, exist_ok=True)

    doc = SimpleDocTemplate(
        output_path,
        pagesize=A4,
        topMargin=12 * mm,
        bottomMargin=12 * mm,
        leftMargin=12 * mm,
        rightMargin=12 * mm,
        title="1000 Basic Japanese Words",
        author="Wiktionary / japanese-practice",
    )

    page_w = A4[0] - 24 * mm
    col_widths = [page_w * 0.36, page_w * 0.22, page_w * 0.42]

    word_style = ParagraphStyle("word", fontName="KleeOne", fontSize=9, leading=12)
    romaji_style = ParagraphStyle("romaji", fontName="KleeOne", fontSize=8, leading=11)
    meaning_style = ParagraphStyle("meaning", fontName="KleeOne", fontSize=8, leading=11)
    h2_style = ParagraphStyle("h2", fontName="Helvetica-Bold", fontSize=10, leading=13, textColor=colors.white)
    h3_style = ParagraphStyle("h3", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.white)
    h4_style = ParagraphStyle("h4", fontName="Helvetica-Bold", fontSize=8, leading=11, textColor=colors.HexColor("#1a3a5c"))
    col_hdr_style = ParagraphStyle("col_hdr", fontName="Helvetica-Bold", fontSize=9, leading=12, textColor=colors.white)
    title_style = ParagraphStyle("title", fontName="KleeOne", fontSize=16, leading=20, spaceAfter=4 * mm, textColor=COLOR_H2_BG)
    subtitle_style = ParagraphStyle("subtitle", fontName="KleeOne", fontSize=9, leading=12, spaceAfter=4 * mm, textColor=colors.grey)

    table_data = [[
        Paragraph("Word", col_hdr_style),
        Paragraph("Romaji", col_hdr_style),
        Paragraph("Meaning", col_hdr_style),
    ]]
    style_cmds = [
        ("BACKGROUND", (0, 0), (-1, 0), COLOR_HEADER_BG),
        ("GRID", (0, 0), (-1, -1), 0.25, colors.HexColor("#cccccc")),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("TOPPADDING", (0, 0), (-1, -1), 3),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 3),
        ("LEFTPADDING", (0, 0), (-1, -1), 5),
        ("RIGHTPADDING", (0, 0), (-1, -1), 5),
    ]

    row_idx = 1
    word_row_count = 0

    for entry in _entries_from_words(words):
        if entry["type"] == "header":
            level = entry["level"]
            text = entry["text"]
            if level == 2:
                para, bg, pad = Paragraph(text.upper(), h2_style), COLOR_H2_BG, 5
            elif level == 3:
                para, bg, pad = Paragraph(text, h3_style), COLOR_H3_BG, 4
            else:
                para, bg, pad = Paragraph(text, h4_style), COLOR_H4_BG, 3

            table_data.append([para, "", ""])
            style_cmds += [
                ("SPAN", (0, row_idx), (-1, row_idx)),
                ("BACKGROUND", (0, row_idx), (-1, row_idx), bg),
                ("TOPPADDING", (0, row_idx), (-1, row_idx), pad),
                ("BOTTOMPADDING", (0, row_idx), (-1, row_idx), pad),
            ]
        else:
            kana, kanji = entry["kana"], entry["kanji"]
            word_display = f"{kanji} ({kana})" if kanji else kana
            table_data.append([
                Paragraph(word_display, word_style),
                Paragraph(entry["romaji"], romaji_style),
                Paragraph(entry["meaning"], meaning_style),
            ])
            if word_row_count % 2 == 1:
                style_cmds.append(("BACKGROUND", (0, row_idx), (-1, row_idx), COLOR_ROW_ALT))
            word_row_count += 1

        row_idx += 1

    table = Table(table_data, colWidths=col_widths, repeatRows=1)
    table.setStyle(TableStyle(style_cmds))

    doc.build([
        Paragraph("1000 Basic Japanese Words｜日本語基本語彙1000", title_style),
        Paragraph("Source: Wiktionary Appendix:1000 Japanese basic words (CC BY-SA 4.0)", subtitle_style),
        table,
    ])


def main():
    if not Path(JSON_FILE).exists():
        print(f"Error: {JSON_FILE} not found.", file=sys.stderr)
        sys.exit(1)

    with open(JSON_FILE, encoding="utf-8") as f:
        words = json.load(f)

    print(f"Generating PDF from {len(words)} words...")
    build_pdf(words, PDF_FILE)
    print(f"Saved to {PDF_FILE}")


if __name__ == "__main__":
    main()
