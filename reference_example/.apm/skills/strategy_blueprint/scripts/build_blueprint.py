"""Build a KaxaNuk Strategy Blueprint PDF from a content.json file.

Run from the skill folder root, e.g.:

    python scripts/build_blueprint.py \
        --content content.json \
        --strategy-name "Liquidity-Weighted Trend Strategy" \
        --output Liquidity_Weighted_Trend_Strategy_Blueprint.pdf

The script encodes the KaxaNuk brand (colours, typography, layout) so the SKILL
just has to fill in content.json. See ``references/BRANDING_GUIDELINES.md`` and
``references/content_schema.md`` for the spec this script implements.

Dependencies:
    pip install reportlab pillow
"""
from __future__ import annotations

import argparse
import json
import os
import sys
from pathlib import Path
from typing import Any

# Lazy-import reportlab so a missing dependency yields a friendly error.
try:
    from reportlab.lib.colors import HexColor, white, black
    from reportlab.lib.enums import TA_CENTER, TA_LEFT
    from reportlab.lib.pagesizes import LETTER
    from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
    from reportlab.lib.units import inch
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    from reportlab.platypus import (
        BaseDocTemplate, Frame, Image, KeepTogether, NextPageTemplate,
        PageBreak, PageTemplate, Paragraph, Spacer, Table, TableStyle,
    )
except ImportError:  # pragma: no cover - install hint
    print(
        "reportlab is not installed. Run: pip install reportlab pillow",
        file=sys.stderr,
    )
    raise

# ---------------------------------------------------------------------------
# Brand constants (mirror references/BRANDING_GUIDELINES.md)
# ---------------------------------------------------------------------------

ORANGE = HexColor("#E84328")
BODY = HexColor("#000000")
BODY_SOFT = HexColor("#434343")
FOOTER_GREY = HexColor("#7F7F7F")
DIVIDER = HexColor("#C7C7C7")
LIGHT_BORDER = HexColor("#E1E1E1")
SCORE_HIGH = HexColor("#008A0E")
SCORE_MID = HexColor("#FFE599")
SCORE_LOW = HexColor("#F8696B")
LINK_BLUE = HexColor("#1071E5")

PAGE_W, PAGE_H = LETTER
MARGIN = 1.0 * inch

# ---------------------------------------------------------------------------
# Font registration. Falls back gracefully if Montserrat isn't installed.
# ---------------------------------------------------------------------------

def _register_fonts() -> tuple[str, str]:
    """Register Montserrat if available, return (regular_name, bold_name)."""
    candidates_regular = [
        "Montserrat-Regular.ttf",
        "/usr/share/fonts/truetype/montserrat/Montserrat-Regular.ttf",
        "/Library/Fonts/Montserrat-Regular.ttf",
        "C:/Windows/Fonts/Montserrat-Regular.ttf",
    ]
    candidates_bold = [
        "Montserrat-Bold.ttf",
        "/usr/share/fonts/truetype/montserrat/Montserrat-Bold.ttf",
        "/Library/Fonts/Montserrat-Bold.ttf",
        "C:/Windows/Fonts/Montserrat-Bold.ttf",
    ]
    reg = next((p for p in candidates_regular if Path(p).exists()), None)
    bold = next((p for p in candidates_bold if Path(p).exists()), None)
    if reg and bold:
        try:
            pdfmetrics.registerFont(TTFont("Montserrat", reg))
            pdfmetrics.registerFont(TTFont("Montserrat-Bold", bold))
            return "Montserrat", "Montserrat-Bold"
        except Exception as exc:  # pragma: no cover
            print(f"WARN: Montserrat registration failed: {exc}", file=sys.stderr)
    print(
        "WARN: Montserrat not found. Falling back to Helvetica. "
        "Install Montserrat for a brand-faithful render.",
        file=sys.stderr,
    )
    return "Helvetica", "Helvetica-Bold"


FONT_REG, FONT_BOLD = _register_fonts()

# ---------------------------------------------------------------------------
# Paragraph styles
# ---------------------------------------------------------------------------

styles = getSampleStyleSheet()

S_COVER_TITLE = ParagraphStyle(
    "CoverTitle", parent=styles["Title"], fontName=FONT_REG, fontSize=36,
    leading=44, textColor=ORANGE, alignment=TA_CENTER, spaceAfter=12,
)
S_COVER_SUBTITLE = ParagraphStyle(
    "CoverSubtitle", parent=styles["Title"], fontName=FONT_BOLD, fontSize=20,
    leading=26, textColor=BODY, alignment=TA_CENTER,
)
S_H1 = ParagraphStyle(
    "H1", parent=styles["Heading1"], fontName=FONT_BOLD, fontSize=24,
    leading=30, textColor=ORANGE, alignment=TA_LEFT, spaceBefore=24, spaceAfter=8,
)
S_H2 = ParagraphStyle(
    "H2", parent=styles["Heading2"], fontName=FONT_BOLD, fontSize=20,
    leading=26, textColor=ORANGE, alignment=TA_LEFT, spaceBefore=18, spaceAfter=6,
)
S_H3 = ParagraphStyle(
    "H3", parent=styles["Heading3"], fontName=FONT_BOLD, fontSize=16,
    leading=22, textColor=ORANGE, alignment=TA_LEFT, spaceBefore=12, spaceAfter=4,
)
S_H4 = ParagraphStyle(
    "H4", parent=styles["Heading4"], fontName=FONT_BOLD, fontSize=14,
    leading=20, textColor=BODY, alignment=TA_LEFT, spaceBefore=10, spaceAfter=4,
)
S_BODY = ParagraphStyle(
    "Body", parent=styles["BodyText"], fontName=FONT_REG, fontSize=10,
    leading=14, textColor=BODY, spaceAfter=6,
)
S_BODY_BOLD = ParagraphStyle(
    "BodyBold", parent=S_BODY, fontName=FONT_BOLD,
)
S_BULLET = ParagraphStyle(
    "Bullet", parent=S_BODY, leftIndent=18, bulletIndent=6, spaceAfter=2,
)
S_SUB_BULLET = ParagraphStyle(
    "SubBullet", parent=S_BULLET, leftIndent=36, bulletIndent=24,
)
S_NUMBERED = ParagraphStyle(
    "Numbered", parent=S_BODY, leftIndent=18, spaceAfter=4,
)
S_CAPTION = ParagraphStyle(
    "Caption", parent=S_BODY, fontSize=10, textColor=BODY_SOFT,
    alignment=TA_CENTER, spaceBefore=4, spaceAfter=8,
)
S_FOOTER = ParagraphStyle(
    "Footer", parent=S_BODY, fontSize=10, textColor=FOOTER_GREY,
    alignment=TA_CENTER,
)
S_TOC_PROCESS = ParagraphStyle(
    "TocProcess", parent=S_BODY, fontSize=15, leading=22, spaceAfter=10,
)
S_SIGNAL = ParagraphStyle(
    "Signal", parent=S_BODY, fontSize=9, leading=14, spaceAfter=2,
)

# ---------------------------------------------------------------------------
# Page templates: cover (no header/footer) + content (header mark + page no.)
# ---------------------------------------------------------------------------

ASSETS = Path(__file__).resolve().parent.parent / "assets"
HEADER_MARK = ASSETS / "kaxanuk_mark_header.png"
COVER_LOGO = ASSETS / "kaxanuk_logo_full.png"


def _draw_content_chrome(canvas, doc):
    canvas.saveState()
    # Top-right KaxaNuk mark
    if HEADER_MARK.exists():
        try:
            mark_w = 0.45 * inch
            mark_h = 0.45 * inch
            canvas.drawImage(
                str(HEADER_MARK),
                PAGE_W - MARGIN - mark_w,
                PAGE_H - 0.55 * inch - mark_h / 2,
                width=mark_w, height=mark_h, mask="auto",
            )
        except Exception as exc:  # pragma: no cover
            print(f"WARN: header mark could not be drawn: {exc}", file=sys.stderr)
    # Footer page number, centered
    canvas.setFont(FONT_REG, 10)
    canvas.setFillColor(FOOTER_GREY)
    canvas.drawCentredString(PAGE_W / 2, 0.5 * inch, str(doc.page))
    canvas.restoreState()


def _draw_cover_chrome(canvas, doc):  # pragma: no cover - empty by design
    # No header, no footer, no page number on the cover.
    return


def _build_doc(output_path: str) -> BaseDocTemplate:
    doc = BaseDocTemplate(
        output_path,
        pagesize=LETTER,
        leftMargin=MARGIN, rightMargin=MARGIN,
        topMargin=MARGIN, bottomMargin=MARGIN,
        title="Strategy Blueprint",
        author="KaxaNuk",
    )
    frame_cover = Frame(0, 0, PAGE_W, PAGE_H, id="cover")
    frame_content = Frame(MARGIN, MARGIN, PAGE_W - 2 * MARGIN, PAGE_H - 2 * MARGIN, id="content")
    doc.addPageTemplates([
        PageTemplate(id="Cover", frames=[frame_cover], onPage=_draw_cover_chrome),
        PageTemplate(id="Content", frames=[frame_content], onPage=_draw_content_chrome),
    ])
    return doc


# ---------------------------------------------------------------------------
# Helpers for rendering recurring patterns
# ---------------------------------------------------------------------------

def _bullets(items: list[str], style: ParagraphStyle = S_BULLET) -> list[Paragraph]:
    return [Paragraph(text, style, bulletText="●") for text in items]


def _numbered(items: list[str]) -> list[Paragraph]:
    return [
        Paragraph(f"{i + 1}. {text}", S_NUMBERED) for i, text in enumerate(items)
    ]


def _placeholder_image(caption: str, width: float = 6.0 * inch, height: float = 3.0 * inch) -> Table:
    cell = Paragraph(
        f"<font color='#7F7F7F'>[{caption} pending]</font>", S_CAPTION,
    )
    tbl = Table([[cell]], colWidths=[width], rowHeights=[height])
    tbl.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, -1), HexColor("#F2F2F2")),
        ("BOX", (0, 0), (-1, -1), 0.5, DIVIDER),
        ("ALIGN", (0, 0), (-1, -1), "CENTER"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
    ]))
    return tbl


def _image_or_placeholder(path: str | None, caption: str) -> list[Any]:
    full = Path(path) if path else None
    flow: list[Any] = []
    if full and full.exists():
        try:
            img = Image(str(full))
            max_w = PAGE_W - 2 * MARGIN
            scale = min(1.0, max_w / img.imageWidth)
            img.drawWidth = img.imageWidth * scale
            img.drawHeight = img.imageHeight * scale
            img.hAlign = "CENTER"
            flow.append(img)
        except Exception as exc:
            print(f"WARN: could not embed {full}: {exc}", file=sys.stderr)
            flow.append(_placeholder_image(caption))
    else:
        flow.append(_placeholder_image(caption))
    flow.append(Paragraph(caption, S_CAPTION))
    return flow


def _config_table(rows: list[dict], headers: list[str]) -> Table:
    keys = [h.lower().replace(" ", "_") for h in headers]
    data = [headers] + [[r.get(k, "") for k in keys] for r in rows]
    col_w = [(PAGE_W - 2 * MARGIN) / len(headers)] * len(headers)
    tbl = Table(data, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTNAME", (0, 1), (-1, -1), FONT_REG),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, 0), BODY),
        ("TEXTCOLOR", (0, 1), (-1, -1), BODY_SOFT),
        ("BACKGROUND", (0, 0), (-1, 0), white),
        ("LINEBELOW", (0, 0), (-1, 0), 1.0, DIVIDER),
        ("INNERGRID", (0, 1), (-1, -1), 0.25, LIGHT_BORDER),
        ("BOX", (0, 0), (-1, -1), 0.5, DIVIDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 6),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 6),
    ]))
    return tbl


def _interpolate_color(value: float, lo: float, hi: float) -> HexColor:
    """3-color gradient: SCORE_LOW -> SCORE_MID -> SCORE_HIGH between lo and hi."""
    if hi == lo:
        return SCORE_MID
    t = max(0.0, min(1.0, (value - lo) / (hi - lo)))
    if t < 0.5:
        # blend low->mid
        s = t / 0.5
        rgb1 = (0xF8, 0x69, 0x6B)
        rgb2 = (0xFF, 0xE5, 0x99)
    else:
        s = (t - 0.5) / 0.5
        rgb1 = (0xFF, 0xE5, 0x99)
        rgb2 = (0x00, 0x8A, 0x0E)
    r = int(rgb1[0] + (rgb2[0] - rgb1[0]) * s)
    g = int(rgb1[1] + (rgb2[1] - rgb1[1]) * s)
    b = int(rgb1[2] + (rgb2[2] - rgb1[2]) * s)
    return HexColor(f"#{r:02X}{g:02X}{b:02X}")


def _strategy_score_table(score: dict) -> Table:
    rows_in = score.get("rows", [])
    headers = ["Strategy Blueprint", "Scoring Concept", "Weight",
               "Score (0-100)", "Weighted Score", "Gap (Score)"]
    body: list[list[Any]] = [headers]
    weighted_values: list[float] = []
    total_weight = 0.0
    total_weighted = 0.0
    last_section = None
    for row in rows_in:
        section = row.get("section", "")
        concept = row.get("concept", "")
        weight = float(row.get("weight", 0))
        score_v = row.get("score", "")
        if isinstance(score_v, (int, float)):
            weighted = weight * float(score_v) / 100.0
            gap = weight - weighted
            score_cell = f"{int(score_v)}"
            weighted_cell = f"{weighted:.1f}"
            gap_cell = f"{gap:.1f}"
            weighted_values.append(weighted)
            total_weighted += weighted
        else:
            weighted_cell = ""
            gap_cell = ""
            score_cell = "TODO"
        total_weight += weight
        # collapse duplicate section labels (visual merge)
        section_cell = section if section != last_section else ""
        last_section = section
        body.append([section_cell, concept, f"{weight:.2f}%", score_cell,
                     weighted_cell, gap_cell])
    body.append(["Overall Score", "", f"{total_weight:.2f}%", "",
                 f"{total_weighted:.1f}", ""])

    col_w = [1.4 * inch, 2.0 * inch, 0.7 * inch, 0.85 * inch, 1.0 * inch, 0.85 * inch]
    tbl = Table(body, colWidths=col_w, repeatRows=1)

    style_cmds: list[tuple] = [
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, 0), BODY),
        ("LINEBELOW", (0, 0), (-1, 0), 1.0, BODY),
        ("FONTNAME", (0, 1), (-1, -2), FONT_REG),
        ("FONTNAME", (0, -1), (-1, -1), FONT_BOLD),
        ("ALIGN", (2, 0), (-1, -1), "RIGHT"),
        ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
        ("INNERGRID", (0, 0), (-1, -1), 0.25, LIGHT_BORDER),
        ("BOX", (0, 0), (-1, -1), 0.5, DIVIDER),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]
    # First-column section labels in bold
    style_cmds.append(("FONTNAME", (0, 1), (0, -2), FONT_BOLD))

    # Conditional formatting on Weighted Score column (col index 4)
    if weighted_values:
        lo = min(weighted_values)
        hi = max(weighted_values)
        for i, w in enumerate(weighted_values, start=1):
            colour = _interpolate_color(w, lo, hi)
            style_cmds.append(("BACKGROUND", (4, i), (4, i), colour))

    # Coral on Gap column where gap > 0 (i.e. negative gap from per-row max)
    for i, row in enumerate(rows_in, start=1):
        score_v = row.get("score", None)
        if isinstance(score_v, (int, float)):
            weight = float(row.get("weight", 0))
            gap = weight - (weight * float(score_v) / 100.0)
            if gap > 1e-6:
                style_cmds.append(("BACKGROUND", (5, i), (5, i), SCORE_LOW))
                style_cmds.append(("TEXTCOLOR", (5, i), (5, i), white))

    tbl.setStyle(TableStyle(style_cmds))
    return tbl


# ---------------------------------------------------------------------------
# Section renderers
# ---------------------------------------------------------------------------

def render_cover(content: dict) -> list[Any]:
    flow: list[Any] = []
    flow.append(Spacer(1, 1.6 * inch))
    flow.append(Paragraph("Strategy Blueprint", S_COVER_TITLE))
    flow.append(Spacer(1, 1.6 * inch))
    if COVER_LOGO.exists():
        try:
            img = Image(str(COVER_LOGO), width=3.0 * inch, height=0.7 * inch,
                        kind="proportional")
            img.hAlign = "CENTER"
            flow.append(img)
        except Exception as exc:
            print(f"WARN: cover logo failed: {exc}", file=sys.stderr)
    else:
        print("WARN: cover logo missing at " + str(COVER_LOGO), file=sys.stderr)
    flow.append(Spacer(1, 2.4 * inch))
    flow.append(Paragraph(content.get("strategy_name", ""), S_COVER_SUBTITLE))
    flow.append(NextPageTemplate("Content"))
    flow.append(PageBreak())
    return flow


def render_process_flow(pf: dict) -> list[Any]:
    flow: list[Any] = [Paragraph("Table of Contents", S_H1)]
    flow.append(Paragraph(f"<b>{pf.get('intro', 'The Process Flow:')}</b>",
                          S_TOC_PROCESS))
    for item in pf.get("items", []):
        label = item.get("label", "")
        desc = item.get("description", "")
        flow.append(Paragraph(f"<b>{label}</b> - {desc}", S_TOC_PROCESS))
    flow.append(PageBreak())
    return flow


def render_strategy_definition(sd: dict, missing: list[str]) -> list[Any]:
    flow: list[Any] = [Paragraph("Strategy Definition", S_H1)]

    # Idea Description
    flow.append(Paragraph("Idea Description", S_H2))
    idea = sd.get("idea_description", {})
    if idea.get("paragraph"):
        flow.append(Paragraph(idea["paragraph"], S_BODY))
    if idea.get("mechanisms"):
        flow.extend(_bullets(idea["mechanisms"]))
    if idea.get("closing_paragraph"):
        flow.append(Paragraph(idea["closing_paragraph"], S_BODY))
    if not idea:
        missing.append("Idea Description")

    # Background Research
    flow.append(Paragraph("Background Research", S_H2))
    flow.append(Paragraph(
        "Momentum and trend-following strategies have been extensively documented "
        "in academic financial research." if not sd.get("background_research_intro")
        else sd["background_research_intro"], S_BODY))
    for paper in sd.get("background_research", []) or []:
        flow.append(Paragraph(paper.get("title", ""), S_H3))
        if paper.get("date"):
            flow.append(Paragraph(f"<b>Date:</b> {paper['date']}", S_BODY))
        if paper.get("authors"):
            flow.append(Paragraph(
                f"<b>Authors:</b> {', '.join(paper['authors'])}", S_BODY))
        if paper.get("link"):
            flow.append(Paragraph(
                f"<b>Link:</b> <link href='{paper['link']}'>"
                f"<font color='#1071E5'>{paper['link']}</font></link>", S_BODY))
        flow.extend(_bullets(paper.get("findings", [])))

    # Universe & Constraints
    flow.append(Paragraph("Investable Universe and Constraints", S_H2))
    flow.append(Paragraph("Universe", S_H3))
    flow.extend(_bullets(sd.get("universe", []) or []))
    flow.append(Paragraph("Strategy Constraints", S_H3))
    flow.extend(_bullets(sd.get("constraints", []) or []))

    # Benchmark
    flow.append(Paragraph("Benchmark", S_H2))
    bench = sd.get("benchmark", {})
    if bench.get("primary"):
        flow.append(Paragraph(f"● {bench['primary']}", S_BODY))
    if bench.get("secondary"):
        s = bench["secondary"]
        flow.append(Paragraph(f"● {s.get('name', '')}", S_BODY))
        for key, label in [("fmp_ticker", "FMP Ticker"),
                           ("isin", "ISIN"),
                           ("ipo", "IPO"),
                           ("purpose", "Used as")]:
            if s.get(key):
                flow.append(Paragraph(f"     ○ {label}: {s[key]}",
                                      S_SUB_BULLET))
    if bench.get("closing_paragraph"):
        flow.append(Paragraph(bench["closing_paragraph"], S_BODY))

    # Hypothesis
    flow.append(Paragraph("Hypothesis", S_H2))
    hyp = sd.get("hypothesis", {})
    flow.append(Paragraph("Market Inefficiency", S_H3))
    flow.extend(_bullets(hyp.get("market_inefficiency", []) or []))
    flow.append(Paragraph("Behavioral", S_H3))
    flow.extend(_bullets(hyp.get("behavioral", []) or []))
    flow.append(Paragraph("Structural", S_H3))
    flow.extend(_bullets(hyp.get("structural", []) or []))
    flow.append(Paragraph("Null Hypothesis", S_H3))
    if hyp.get("null"):
        flow.append(Paragraph(f"● {hyp['null']}", S_BODY))

    # UML
    flow.append(Paragraph("Unified Modeling Language Diagrams", S_H2))
    uml = sd.get("uml_diagram", {})
    flow.extend(_image_or_placeholder(uml.get("image_path"),
                                      uml.get("caption", "Strategy UML Diagram")))

    flow.append(PageBreak())
    return flow


def render_feature_engineering(fe: dict, missing: list[str]) -> list[Any]:
    flow: list[Any] = [Paragraph("Feature Engineering", S_H1)]

    flow.append(Paragraph("Data", S_H2))
    data = fe.get("data", {})
    flow.append(Paragraph("The strategy relies primarily on market price data."
                          if not data.get("intro") else data["intro"], S_BODY))
    flow.append(Paragraph("Key Variables", S_H3))
    flow.extend(_bullets(data.get("key_variables", []) or []))
    flow.append(Paragraph("Adjusted Prices Incorporate", S_H3))
    flow.extend(_bullets(data.get("adjusted_prices_incorporate", []) or []))
    if data.get("adjustment_note"):
        flow.append(Paragraph(data["adjustment_note"], S_BODY))

    flow.append(Paragraph("Data Analysis", S_H2))
    da = fe.get("data_analysis", {})
    flow.append(Paragraph("Time Series and Cross-Sectional Analysis", S_H3))
    flow.extend(_bullets(da.get("time_series_and_cross_sectional", []) or []))
    flow.append(Paragraph("Key Financial Metrics", S_H3))
    flow.extend(_bullets(da.get("key_financial_metrics", []) or []))
    flow.append(Paragraph("Common Visualizations", S_H3))
    flow.extend(_bullets(da.get("common_visualizations", []) or []))

    flow.append(Paragraph("Features", S_H2))
    feats = fe.get("features", {})
    if feats.get("intro_paragraph"):
        flow.append(Paragraph(feats["intro_paragraph"], S_BODY))
    for grp in feats.get("groups", []) or []:
        flow.append(Paragraph(grp.get("title", "Features"), S_H3))
        rows = grp.get("rows", [])
        tbl_data = [["Feature", "Description"]]
        tbl_data.extend([[r.get("feature", ""), r.get("description", "")]
                         for r in rows])
        col_w = [1.5 * inch, PAGE_W - 2 * MARGIN - 1.5 * inch]
        tbl = Table(tbl_data, colWidths=col_w, repeatRows=1)
        tbl.setStyle(TableStyle([
            ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
            ("FONTNAME", (0, 1), (-1, -1), FONT_REG),
            ("FONTSIZE", (0, 0), (-1, -1), 10),
            ("TEXTCOLOR", (0, 0), (-1, 0), BODY),
            ("TEXTCOLOR", (0, 1), (-1, -1), BODY_SOFT),
            ("LINEBELOW", (0, 0), (-1, 0), 1.0, DIVIDER),
            ("INNERGRID", (0, 1), (-1, -1), 0.25, LIGHT_BORDER),
            ("BOX", (0, 0), (-1, -1), 0.5, DIVIDER),
            ("VALIGN", (0, 0), (-1, -1), "TOP"),
            ("LEFTPADDING", (0, 0), (-1, -1), 6),
            ("RIGHTPADDING", (0, 0), (-1, -1), 6),
            ("TOPPADDING", (0, 0), (-1, -1), 4),
            ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
        ]))
        flow.append(tbl)
        if grp.get("note"):
            flow.append(Spacer(1, 4))
            flow.append(Paragraph(f"<i>Note: {grp['note']}</i>", S_BODY))
    if feats.get("overview_image"):
        flow.extend(_image_or_placeholder(feats["overview_image"],
                                          "Features Overview"))

    flow.append(Paragraph("Strategy Signals", S_H2))
    for sig in fe.get("strategy_signals", []) or []:
        flow.append(Paragraph(sig.get("name", "Signal"), S_H3))
        if sig.get("intro"):
            flow.append(Paragraph(sig["intro"], S_BODY))
        for line in sig.get("branches", []) or []:
            flow.append(Paragraph(line, S_SIGNAL))
        flow.append(Paragraph("Signal Logic", S_H4))
        flow.extend([Paragraph(f"• {b}", S_BODY)
                     for b in sig.get("logic", []) or []])

    flow.append(PageBreak())
    return flow


def render_strategy_design(sd: dict, missing: list[str]) -> list[Any]:
    flow: list[Any] = [Paragraph("Strategy Design", S_H1)]

    flow.append(Paragraph("Strategy Modeling", S_H2))
    sm = sd.get("strategy_modeling", {})
    for para in sm.get("intro_paragraphs", []) or []:
        flow.append(Paragraph(para, S_BODY))
    sm_rows = sm.get("table", [])
    tbl_data = [["Dimension", "Question"]]
    tbl_data.extend([[r.get("dimension", ""), r.get("question", "")]
                     for r in sm_rows])
    col_w = [1.4 * inch, PAGE_W - 2 * MARGIN - 1.4 * inch]
    tbl = Table(tbl_data, colWidths=col_w, repeatRows=1)
    tbl.setStyle(TableStyle([
        ("FONTNAME", (0, 0), (-1, 0), FONT_BOLD),
        ("FONTNAME", (0, 1), (-1, -1), FONT_REG),
        ("FONTSIZE", (0, 0), (-1, -1), 10),
        ("TEXTCOLOR", (0, 0), (-1, 0), BODY),
        ("TEXTCOLOR", (0, 1), (-1, -1), BODY_SOFT),
        ("LINEBELOW", (0, 0), (-1, 0), 1.0, DIVIDER),
        ("INNERGRID", (0, 1), (-1, -1), 0.25, LIGHT_BORDER),
        ("BOX", (0, 0), (-1, -1), 0.5, DIVIDER),
        ("VALIGN", (0, 0), (-1, -1), "TOP"),
        ("LEFTPADDING", (0, 0), (-1, -1), 6),
        ("RIGHTPADDING", (0, 0), (-1, -1), 6),
        ("TOPPADDING", (0, 0), (-1, -1), 4),
        ("BOTTOMPADDING", (0, 0), (-1, -1), 4),
    ]))
    flow.append(tbl)

    flow.append(Paragraph("Portfolio Construction", S_H2))
    pc = sd.get("portfolio_construction", {})
    flow.append(Paragraph("Selection Rules", S_H3))
    flow.extend([Paragraph(f"• {b}", S_BODY)
                 for b in pc.get("selection_rules", []) or []])
    flow.append(Paragraph("Sizing Rules", S_H3))
    flow.extend([Paragraph(f"• {b}", S_BODY)
                 for b in pc.get("sizing_rules", []) or []])
    flow.append(Paragraph("Rebalancing Logic — Event-Driven", S_H3))
    rb = pc.get("rebalancing_logic", {})
    if rb.get("intro"):
        flow.append(Paragraph(rb["intro"], S_BODY))
    flow.extend([Paragraph(f"• {b}", S_BODY)
                 for b in rb.get("bullets", []) or []])
    flow.append(Paragraph("Market Regime Handling", S_H3))
    if pc.get("market_regime_handling"):
        flow.append(Paragraph(pc["market_regime_handling"], S_BODY))

    flow.append(Paragraph("Backtesting", S_H2))
    bt = sd.get("backtesting", {})
    flow.append(Paragraph("Backtesting Config", S_H3))
    cfg_rows = bt.get("config", [])
    if cfg_rows:
        flow.append(_config_table(cfg_rows, ["Parameter", "Value", "Description"]))
    for sub_title, key in [
        ("Performance Top 20", "performance_image"),
        ("Commissions Top 20", "commissions_image"),
        ("Drawdown Top 20", "drawdown_image"),
        ("Annual Returns Top 20", "annual_returns_image"),
    ]:
        flow.append(Paragraph(sub_title, S_H3))
        flow.extend(_image_or_placeholder(bt.get(key), sub_title))

    flow.append(Paragraph("Attribution Analysis", S_H2))
    attr = sd.get("attribution_analysis", {})
    if attr.get("image_path"):
        flow.extend(_image_or_placeholder(attr["image_path"],
                                          "Attribution Analysis"))
    for i, finding in enumerate(attr.get("findings", []) or [], start=1):
        flow.append(Paragraph(
            f"{i}. <b>{finding.get('headline', '')}</b> {finding.get('body', '')}",
            S_NUMBERED,
        ))

    flow.append(Paragraph("Strategy Score", S_H2))
    score = sd.get("strategy_score", {})
    if score.get("rows"):
        flow.append(_strategy_score_table(score))
    if score.get("observations"):
        flow.append(Spacer(1, 6))
        flow.extend(_numbered(score["observations"]))

    flow.append(PageBreak())
    return flow


def render_conclusions(cc: dict, missing: list[str]) -> list[Any]:
    flow: list[Any] = [Paragraph("Conclusions", S_H1)]

    flow.append(Paragraph("Hypothesis Validation.", S_H2))
    hv = cc.get("hypothesis_validation", {})
    if hv.get("lead_question"):
        flow.append(Paragraph(f"<b>{hv['lead_question']}</b>", S_BODY_BOLD))
    if hv.get("key_findings"):
        flow.append(Paragraph("<b>Key Findings:</b>", S_BODY_BOLD))
        flow.extend(_bullets(hv["key_findings"]))
    if hv.get("interpretation"):
        flow.append(Paragraph("<b>Interpretation:</b>", S_BODY_BOLD))
        flow.extend(_bullets(hv["interpretation"]))
    if hv.get("conclusion"):
        flow.append(Paragraph("<b>Conclusion:</b>", S_BODY_BOLD))
        flow.append(Paragraph(f"● {hv['conclusion']}", S_BODY))

    flow.append(Paragraph("Is This An Implementable Strategy?", S_H2))
    impl = cc.get("implementable", {})
    if impl.get("implementation_risks"):
        flow.append(Paragraph("<b>Implementation Risks</b>", S_BODY_BOLD))
        for risk in impl["implementation_risks"]:
            flow.append(Paragraph(f"<b>{risk.get('name', '')}</b>", S_BODY_BOLD))
            flow.append(Paragraph(f"➔ {risk.get('explanation', '')}", S_BODY))
    if impl.get("operational_requirements"):
        flow.append(Paragraph("<b>Operational Requirements</b>", S_BODY_BOLD))
        for line in impl["operational_requirements"]:
            flow.append(Paragraph(f"➔ {line}", S_BODY))
    if impl.get("decision"):
        flow.append(Paragraph("<b>Decision</b>", S_BODY_BOLD))
        flow.append(Paragraph(f"\U0001F449 {impl['decision']}", S_BODY))
    if impl.get("key_condition"):
        flow.append(Paragraph("<b>Key Condition</b>", S_BODY_BOLD))
        flow.append(Paragraph(impl["key_condition"], S_BODY))

    flow.append(Paragraph("Next Steps", S_H2))
    for i, group in enumerate(cc.get("next_steps", []) or [], start=1):
        flow.append(Paragraph(f"{i}. <b>{group.get('category', '')}</b>",
                              S_NUMBERED))
        for item in group.get("items", []) or []:
            flow.append(Paragraph(f"● {item}", S_SUB_BULLET))

    flow.append(PageBreak())
    return flow


def render_findings(ff: dict, missing: list[str]) -> list[Any]:
    flow: list[Any] = [Paragraph("Findings, Concerns and Decisions", S_H1)]
    for it in ff.get("iterations", []) or []:
        flow.append(Paragraph(it.get("title", "Iteration"), S_H2))
        for entry in it.get("entries", []) or []:
            flow.append(Paragraph(entry.get("date", ""), S_H3))
            flow.append(Paragraph(entry.get("body", ""), S_BODY))
    return flow


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def build(content_path: str, output_path: str, strategy_name: str | None) -> None:
    with open(content_path, "r", encoding="utf-8") as fh:
        content = json.load(fh)
    if strategy_name:
        content["strategy_name"] = strategy_name

    # Validate weights sum.
    score_rows = (
        content.get("strategy_design", {})
        .get("strategy_score", {})
        .get("rows", [])
    )
    if score_rows:
        total = sum(float(r.get("weight", 0)) for r in score_rows)
        if abs(total - 100.0) > 0.05:
            raise ValueError(
                f"strategy_score.rows[*].weight must sum to 100.0 (got {total})"
            )

    missing: list[str] = []
    flow: list[Any] = []
    flow.extend(render_cover(content))
    flow.extend(render_process_flow(content.get("process_flow", {
        "intro": "The Process Flow:",
        "items": [
            {"label": "Strategy Definition",
             "description": "Moving from intuition to a clear, testable hypothesis with an explicit source of returns."},
            {"label": "Feature Engineering",
             "description": "Transforming raw data into meaningful, hypothesis-driven signals."},
            {"label": "Strategy Design",
             "description": "Translating signals into portfolio decisions — selection, sizing, and timing — and validating results through robust testing and analysis."},
        ],
    })))
    flow.extend(render_strategy_definition(content.get("strategy_definition", {}), missing))
    flow.extend(render_feature_engineering(content.get("feature_engineering", {}), missing))
    flow.extend(render_strategy_design(content.get("strategy_design", {}), missing))
    flow.extend(render_conclusions(content.get("conclusions", {}), missing))
    flow.extend(render_findings(content.get("findings", {}), missing))

    doc = _build_doc(output_path)
    doc.build(flow)
    print(f"Wrote {output_path}")
    if missing:
        print("Missing sections (rendered as TODO placeholders):", file=sys.stderr)
        for m in missing:
            print(f"  - {m}", file=sys.stderr)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--content", required=True, help="Path to content.json")
    parser.add_argument("--output", required=True, help="Output PDF path")
    parser.add_argument("--strategy-name", default=None,
                        help="Override strategy name (otherwise read from content.json)")
    args = parser.parse_args()
    build(args.content, args.output, args.strategy_name)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
