# KaxaNuk Strategy Blueprint — Branding Guidelines

These guidelines are extracted directly from the canonical `Strategy Blueprint.pdf` (the *Liquidity-Weighted Trend Strategy* deliverable) and govern every Strategy Blueprint produced through this skill. The point of fixing them is consistency: a reader should be able to open any blueprint and recognise it as a KaxaNuk document on the first page.

## 1. Brand Identity

KaxaNuk — *Sharing knowledge*. The blueprint is a research artefact, so the tone is technical, calm, and confident. The visual language is minimal: a lot of white space, a single warm accent colour, and a strict typographic hierarchy in Montserrat.

## 2. Colour Palette

Use these exact hex values. Do not invent new tints.

| Role | Hex | RGB | Where it is used |
|------|-----|-----|------------------|
| Primary Orange (KaxaNuk Orange) | `#E84328` | 232, 67, 40 | Cover title, all H1 / H2 / H3 headings, KaxaNuk logo accent, key UI accents |
| Body Text | `#000000` | 0, 0, 0 | Default body copy in Montserrat Regular 10pt |
| Body Text Soft | `#434343` | 67, 67, 67 | Captions, table body text, secondary copy |
| Page Number / Footer | `#7F7F7F` | 127, 127, 127 | Page numbers and document footer |
| Divider / Border | `#C7C7C7` | 199, 199, 199 | Table grid lines, section separators |
| Light Border | `#E1E1E1` | 225, 225, 225 | Inner table dividers, light shading |
| Score — High (good) | `#008A0E` | 0, 138, 14 | Strategy Score weighted-score "good" cells |
| Score — Mid (warning) | `#FFE599` | 255, 229, 153 | Strategy Score weighted-score "neutral" cells |
| Score — Low (bad) | `#F8696B` | 248, 105, 107 | Strategy Score weighted-score "poor" cells, gap callouts |
| Hyperlink Blue | `#1071E5` | 16, 113, 229 | Inline links to papers and external resources |

The conditional formatting on the Strategy Score table follows a green → yellow → red gradient (Excel-style 3-color scale) interpolating between the three Score colours above based on the cell value.

## 3. Typography

The whole document is set in **Montserrat** with **Arial** used only as the bullet glyph. Embed both fonts in the output PDF.

| Role | Font | Size | Colour | Notes |
|------|------|------|--------|-------|
| Cover Title (`Strategy Blueprint`) | Montserrat Regular | 36 pt | `#E84328` | Centered, top third of the cover page |
| Cover Subtitle (strategy name) | Montserrat Bold | 20 pt | `#000000` | Centered, lower third, below the logo |
| H1 — Section title (e.g. *Strategy Definition*, *Feature Engineering*, *Strategy Design*, *Conclusions*, *Findings, Concerns and Decisions*) | Montserrat Bold | 24 pt | `#E84328` | Left-aligned. ~24 pt space before, 6 pt after |
| H2 — Subsection (e.g. *Idea Description*, *Hypothesis*, *Backtesting*, *Strategy Score*) | Montserrat Bold | 20 pt | `#E84328` | Left-aligned. ~18 pt space before, 6 pt after |
| H3 — Topic (e.g. *Universe*, *Market Inefficiency*, *Trend Indicators*, *Selection Rules*) | Montserrat Bold | 16 pt | `#E84328` | Left-aligned. ~12 pt space before, 4 pt after |
| H4 — Sub-topic (e.g. *Signal Logic*) | Montserrat Bold | 14 pt | `#000000` | Used inside a subsection that already has an H3. Note the colour shift to black |
| Body | Montserrat Regular | 10 pt | `#000000` | Line height ~1.4, paragraph spacing 6 pt |
| Body Bold (lead-in) | Montserrat Bold | 10 pt | `#000000` | Used for *Date:*, *Authors:*, *Link:*, *Key Findings:* style lead-ins |
| Bullet Glyph | Arial Regular | 10 pt | `#000000` | The bullet character `●` (U+25CF). Indented, with a 6 pt gap before the body text |
| Numbered List | Montserrat Regular | 10 pt | `#000000` | `1.`, `2.`, `3.` followed by a tab |
| Table Header | Montserrat Bold | 10 pt | `#000000` | Background: white or `#F2F2F2`; bottom border `#C7C7C7` 1pt |
| Table Body | Montserrat Regular | 10 pt | `#434343` | 1pt `#E1E1E1` inner gridlines |
| Code / Mono token (e.g. `c_sma_50d`) | Inline run kept in Montserrat Regular | 10 pt | `#000000` | The example PDF does not switch to a monospace font; tokens stay in Montserrat for visual continuity. Do not introduce a new font. |
| Footer / Page Number | Montserrat Regular | 10 pt | `#7F7F7F` | Bottom-center, e.g. `5` |

## 4. Page Layout

- Page size: **US Letter** (8.5 × 11 in) portrait.
- Margins: **1.0 in** (≈ 72 pt) on all four sides.
- Header: every page **except the cover** carries the small KaxaNuk circular mark in the top-right corner (≈ 0.5 in tall). Provided as `assets/kaxanuk_mark_header.png`.
- Footer: every page **except the cover** shows the page number bottom-center (`#7F7F7F`, Montserrat Regular 10 pt). The Table of Contents page also prints the document title `Strategy Blueprint` bottom-left.
- Cover page: no header, no footer, no page number.

## 5. Cover Page Anatomy

Three vertically-stacked, centered blocks separated by white space:

1. **Title block** at ~25 % from top: `Strategy Blueprint` in Montserrat Regular 36 pt, `#E84328`.
2. **Logo block** at ~50 %: the full horizontal KaxaNuk logo (`assets/kaxanuk_logo_full.png`) — the orange "K" / "N" mark with the *KaxaNuk* wordmark and *Sharing knowledge* tagline below. Width ≈ 3.0 in, centred.
3. **Subtitle block** at ~80 %: the strategy name (e.g. `Liquidity-Weighted Trend Strategy`) in Montserrat Bold 20 pt, `#000000`, centred.

## 6. Table of Contents

There are **two** TOC artefacts in the document and both must be reproduced:

- **Page 2 — *The Process Flow* concept page.** Renders the title `Table of Contents` (H1 Bold 24 pt orange), the prompt `The Process Flow:` (Bold 15 pt), then three paragraph entries describing *Strategy Definition*, *Feature Engineering*, *Strategy Design*, each using mixed Bold (the section name) and Regular (the description) Montserrat at 15 pt. The footer of this page reads `Strategy Blueprint` bottom-left and the page number `2` bottom-right.
- **Pages 3-4 — Detailed dotted TOC.** A traditional table of contents with `Section............................page` entries built from the document's H1 / H2 / H3 hierarchy. Set in Montserrat Regular 10 pt, the page numbers right-aligned, the dot leader rendered with `.` characters in `#C7C7C7`. Section names are H2-style entries (no indent) and child entries are indented by ~0.25 in per level.

## 7. Bulleted and Numbered Lists

- Use the Arial bullet glyph `●` followed by a 6 pt gap, then the body run in Montserrat Regular 10 pt.
- Indent first-level bullets by 0.25 in; second-level bullets (the sub-bullets shown under each background-research paper) by 0.5 in and use the same `●` glyph.
- Numbered lists use `1.`, `2.`, `3.` in Montserrat Regular 10 pt, with the same 0.25 in indent.
- Inline arrow bullets `➔` (used in the *Implementation Risks* section) stay in the body font, in `#000000`, with a single space after the arrow.

## 8. Tables

Two distinct table styles appear in the source PDF and must be honoured:

### 8.1 Reference / Config Table

Used for *Trend Indicators*, *Strategy Modeling — Dimension / Question*, and *Backtesting Config*.

- Header row: Montserrat Bold 10 pt, `#000000`, white background, 1 pt `#C7C7C7` bottom border.
- Body rows: Montserrat Regular 10 pt, `#434343`, white background, 0.5 pt `#E1E1E1` inner horizontal lines.
- Outer border: 1 pt `#C7C7C7`.
- Column widths: first column wider for the descriptive label.

### 8.2 Strategy Score Table (page 17)

This is the only colour-coded table.

- Columns: *Strategy Blueprint*, *Scoring Concept*, *Weight*, *Score (0–100)*, *Weighted Score*, *Gap (Score)*.
- Header row: Montserrat Bold 10 pt black on white, with a 1 pt `#000000` bottom rule.
- The first column merges cells per section (`Strategy Definition`, `Feature Engineering`, `Strategy Design`) and uses Montserrat Bold 10 pt black on white.
- The *Weighted Score* column carries the 3-colour gradient: `#F8696B` for low, `#FFE599` for mid, `#008A0E` for high. Cells for the `Overall Score` row use Montserrat Bold.
- The *Gap (Score)* column shades only negative gaps in `#F8696B` with white text; zero or positive gaps stay white.
- Numeric cells right-align; the `Weight` column is formatted as a percentage with one decimal (e.g. `11.11%`), `Score` as integer, `Weighted Score` and `Gap (Score)` to one decimal.

## 9. Figures and Diagrams

- All inline figures (UML diagrams, performance charts, attribution charts) are centered with a 6 pt margin above and below.
- Figure captions are Montserrat Regular 10 pt centered in `#434343`. Captions read like `Liquidity-Weighted Trend Strategy` (the strategy name) — short and descriptive, **no `Figure N:` prefix**.
- Charts use the Primary Orange `#E84328` for the first/primary series. Secondary series should use neutral greys (`#434343`, `#7F7F7F`) before introducing `#1071E5` for a third series.

## 10. Hyperlinks

External links (papers, tickers) are rendered in Montserrat Regular 10 pt, colour `#1071E5`, with an underline. Always show the literal URL — the example PDF does not hide URLs behind label text.

## 11. Voice and Tone

- Third-person, neutral, technical. Never first-person "I" or "we" except in the *Findings, Concerns and Decisions* journal section, which is permitted to use "we" (matching the example PDF).
- Use the active voice; lead each bullet with a noun or verb, not a hedge ("Possibly", "Maybe").
- Avoid emoji except for the `➔` arrow bullet and the `👉` callout used in the *Decision* line of the *Is This An Implementable Strategy?* section. These two glyphs are reproduced verbatim from the source PDF.

## 12. Asset Inventory

| File | Purpose |
|------|---------|
| `assets/kaxanuk_logo_full.png` | Full horizontal KaxaNuk logo with tagline. Cover page only. |
| `assets/kaxanuk_mark_header.png` | The square KaxaNuk mark (orange ring on white). Top-right of every page after the cover. |

If either asset is missing, the skill must stop and surface the error to the user instead of substituting a placeholder.
