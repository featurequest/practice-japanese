"""tools/stories_pdf.py — PDF renderer for Japanese folk tale reading practice."""
import re
from pathlib import Path

import pykakasi
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import (
    SimpleDocTemplate, Paragraph, HRFlowable, KeepTogether,
)
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont

from data.stories import Story

FONT_PATH = "fonts/KleeOne-SemiBold.ttf"

COLOR_SUBTITLE = colors.HexColor("#888888")
COLOR_ROMAJI   = colors.HexColor("#888888")
COLOR_TITLE    = colors.HexColor("#1a3a5c")
COLOR_RULE     = colors.HexColor("#dddddd")

_KAKASI = pykakasi.kakasi()


def _to_romaji(text: str) -> str:
    result = _KAKASI.convert(text)
    raw = "".join(item["hepburn"] for item in result)
    return re.sub(r' ([,\.!\?;:）」』\)])', r'\1', raw).strip()


def _register_font() -> None:
    if "KleeOne" not in pdfmetrics.getRegisteredFontNames():
        pdfmetrics.registerFont(TTFont("KleeOne", FONT_PATH))


def generate_story_pdf(story: Story, output_path: Path) -> None:
    _register_font()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("KleeOne", 8)
        canvas.setFillColor(COLOR_ROMAJI)
        canvas.drawCentredString(
            A4[0] / 2, 8 * mm,
            f"{story.title_en}  ·  {story.title_ja}  ·  {doc.page}",
        )
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        title=story.title_en,
        author="japanese-practice",
    )

    title_style = ParagraphStyle(
        "story_title", fontName="KleeOne", fontSize=20, leading=26,
        spaceAfter=1 * mm, textColor=COLOR_TITLE,
    )
    title_ja_style = ParagraphStyle(
        "story_title_ja", fontName="KleeOne", fontSize=13, leading=18,
        spaceAfter=6 * mm, textColor=COLOR_SUBTITLE,
    )
    jp_style = ParagraphStyle(
        "jp", fontName="KleeOne", fontSize=13, leading=19, spaceAfter=1 * mm,
    )
    romaji_style = ParagraphStyle(
        "romaji", fontName="KleeOne", fontSize=9, leading=13,
        spaceAfter=1 * mm, textColor=COLOR_ROMAJI,
    )
    en_style = ParagraphStyle(
        "en", fontName="KleeOne", fontSize=10, leading=14, spaceAfter=2 * mm,
    )

    flowables = [
        Paragraph(story.title_en, title_style),
        Paragraph(story.title_ja, title_ja_style),
    ]

    for sentence in story.sentences:
        romaji = _to_romaji(sentence.japanese)
        flowables.append(KeepTogether([
            Paragraph(sentence.japanese, jp_style),
            Paragraph(romaji, romaji_style),
            Paragraph(sentence.english, en_style),
            HRFlowable(width="100%", thickness=0.5, color=COLOR_RULE,
                       spaceAfter=3 * mm),
        ]))

    doc.build(flowables, onFirstPage=on_page, onLaterPages=on_page)


def generate_reading_practice_pdf(story: Story, output_path: Path) -> None:
    """Generate a reading practice sheet: Japanese sentence + blank line + answer key."""
    _register_font()
    output_path.parent.mkdir(parents=True, exist_ok=True)

    def on_page(canvas, doc):
        canvas.saveState()
        canvas.setFont("KleeOne", 8)
        canvas.setFillColor(COLOR_ROMAJI)
        canvas.drawCentredString(
            A4[0] / 2, 8 * mm,
            f"{story.title_en}  ·  {story.title_ja}  ·  Reading Practice  ·  {doc.page}",
        )
        canvas.restoreState()

    doc = SimpleDocTemplate(
        str(output_path),
        pagesize=A4,
        topMargin=15 * mm,
        bottomMargin=20 * mm,
        leftMargin=20 * mm,
        rightMargin=20 * mm,
        title=f"{story.title_en} – Reading Practice",
        author="japanese-practice",
    )

    title_style = ParagraphStyle(
        "rp_title", fontName="KleeOne", fontSize=20, leading=26,
        spaceAfter=1 * mm, textColor=COLOR_TITLE,
    )
    title_ja_style = ParagraphStyle(
        "rp_title_ja", fontName="KleeOne", fontSize=13, leading=18,
        spaceAfter=8 * mm, textColor=COLOR_SUBTITLE,
    )
    jp_style = ParagraphStyle(
        "rp_jp", fontName="KleeOne", fontSize=14, leading=22, spaceAfter=1 * mm,
    )
    blank_label_style = ParagraphStyle(
        "rp_blank_label", fontName="KleeOne", fontSize=8, leading=10,
        spaceAfter=1 * mm, textColor=COLOR_SUBTITLE,
    )
    answer_heading_style = ParagraphStyle(
        "rp_ans_head", fontName="KleeOne", fontSize=10, leading=14,
        spaceBefore=8 * mm, spaceAfter=2 * mm, textColor=COLOR_SUBTITLE,
    )
    answer_style = ParagraphStyle(
        "rp_ans", fontName="KleeOne", fontSize=9, leading=14,
        spaceAfter=1 * mm, textColor=COLOR_SUBTITLE,
    )

    flowables = [
        Paragraph(story.title_en, title_style),
        Paragraph(story.title_ja, title_ja_style),
    ]

    for i, sentence in enumerate(story.sentences, 1):
        flowables.append(KeepTogether([
            Paragraph(f"{i}. {sentence.japanese}", jp_style),
            Paragraph("Translation:", blank_label_style),
            HRFlowable(width="100%", thickness=0.5, color=COLOR_RULE, spaceAfter=6 * mm),
        ]))

    # Answer key
    flowables.append(Paragraph("Answer Key", answer_heading_style))
    flowables.append(HRFlowable(width="100%", thickness=0.5, color=COLOR_RULE, spaceAfter=3 * mm))
    for i, sentence in enumerate(story.sentences, 1):
        flowables.append(Paragraph(f"{i}. {sentence.english}", answer_style))

    doc.build(flowables, onFirstPage=on_page, onLaterPages=on_page)
