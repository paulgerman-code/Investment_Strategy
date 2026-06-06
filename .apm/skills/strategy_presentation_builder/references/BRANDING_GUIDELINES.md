# KaxaNuk Brand Guidelines — Strategy Presentation

These guidelines were extracted from `Deliverables_Templates/Strategy Presentation Template.pdf`. Apply them whenever you build a Strategy Presentation deck so that every output matches the corporate template.

---

## 1. Color Palette

| Role | Hex | RGB | Usage |
|------|-----|-----|-------|
| Brand Red (Primary) | `#CB2E15` | (203, 46, 21) | Cover slide background, logo glyph fill, full-bleed accents. |
| Brand Red (Accent) | `#E84328` | (232, 67, 40) | Slide titles on light backgrounds, arrow bullets `>`, table-header fills, hyperlink emphasis. The slightly brighter shade is used for typography on white; the darker `#CB2E15` is used for solid panels. |
| Charcoal | `#2C2C2C` | (44, 44, 44) | Section-divider background; primary body text on white. |
| Subtitle Gray | `#DCDCDC` | (220, 220, 220) | Subtitle text on the charcoal section dividers. |
| Page-Number Gray | `#A0A0A0` | (160, 160, 160) | Slide-number footer (`9pt`, bottom-right). |
| White | `#FFFFFF` | (255, 255, 255) | Content-slide background; title text on the brand-red cover. |
| Hyperlink Blue | `#1155CC` | (17, 85, 204) | Email / URL links (e.g. `research@kaxanuk.mx`). |

Treat `#E84328` and `#CB2E15` as the same brand red — pick the lighter accent for text, the darker primary for fills. Never substitute another red.

---

## 2. Typography

The deck is set in **Montserrat** with **Arial** as the system fallback (both are embedded in the source PDF).

| Element | Font / Weight | Size (pt) | Color |
|---------|---------------|-----------|-------|
| Cover title (`Strategy Presentation`) | Montserrat Regular | 54 | `#FFFFFF` |
| Cover subtitle | Montserrat Regular | 24 | `#FFFFFF` (~85% opacity) |
| Section-divider title | Montserrat Regular | 54 | `#FFFFFF` |
| Section-divider subtitle | Montserrat Regular | 22 | `#DCDCDC` |
| Content slide title | Montserrat Regular | 32 | `#E84328` |
| Section header inside body (e.g. `Trend Indicators`) | Montserrat Bold | 16 | `#2C2C2C` |
| Body text | Montserrat Regular | 14 | `#2C2C2C` |
| Bullet text | Montserrat Regular | 14 | `#2C2C2C` |
| Inline emphasis | Montserrat Bold | 14 | `#2C2C2C` |
| Page number | Montserrat Regular | 9 | `#A0A0A0` |

Titles are always set in **Montserrat Regular** (never Bold) — the weight contrast in this template comes from color, not weight.

Use sentence-case for body copy and Title Case for slide titles, matching the source deck.

---

## 3. Slide Geometry

- Slide size: **13.33 in × 7.5 in** (16:9 widescreen, equivalent to PDF `720 × 405 pt`).
- Safe content area: 0.5 in margin on all sides.
- Title position on content slides: top-left, baseline at ~0.55 in from top, x = 0.5 in.
- Logo position on content slides: top-right, x ≈ 12.45 in, y ≈ 0.30 in, width ≈ 0.65 in, height ≈ 0.65 in (uses `assets/kaxanuk_logo_red.png`).
- Page number on content slides: bottom-right, x ≈ 12.7 in, y ≈ 7.15 in.

---

## 4. Slide Templates

### 4.1 Cover Slide (`pdf p.1`)
- Background: white.
- Centered/right-of-center: full KaxaNuk wordmark (`assets/kaxanuk_wordmark.png`) with the gray fingerprint motif (`assets/kaxanuk_fingerprint_gray.png`) anchored to the left.
- No title text on this page; the wordmark is the title.

### 4.2 Title Slide (`pdf p.2`)
- Full-bleed background fill: `#CB2E15`.
- Centered title: `Strategy Presentation`, Montserrat Regular, 54 pt, white.
- Centered subtitle directly below the title: the strategy name (e.g. `Liquidity-Weighted Trend Strategy`), 24 pt, white.
- No logo, no page number.

### 4.3 Section Divider (`pdf p.4, p.12, p.17, p.35`)
- Full-bleed background fill: `#2C2C2C`.
- Title left-aligned at ~33% vertical: section name, Montserrat Regular, 54 pt, `#FFFFFF`.
- Subtitle directly below the title: one-line tagline (typically `Liquidity-Weighted Trend Strategy` or another contextual phrase), Montserrat Regular, 22 pt, `#DCDCDC`.
- No logo, no page number.

### 4.4 Content Slide (most slides — `pdf p.3, p.5–11, p.13–34, p.36–41`)
- Background: white.
- Title top-left in `#E84328`, 32 pt.
- Body region beneath the title (starting ~1.5 in from top) holds:
  - Plain paragraph copy in 14 pt charcoal, single column.
  - Bullet lists using a **filled black disc** (`●`) for normal bullets, indented 0.4 in.
  - Top-level navigation/agenda items use a **brand-red right-arrow** (`➔` U+2794) instead of a disc — see the `Content` slide and the `Selection / Sizing / Timing` slide.
  - "Decision" callouts may use the pointing-finger glyph (`👉`) followed by bold copy — used sparingly.
- Logo (top-right) and page number (bottom-right) per Section 3.

### 4.5 Visual / Chart Slide (`pdf p.11 UML`, `p.23 Historical Portfolios`, `p.25 Backtest Config`, `p.27 Performance`, `p.29 Commissions`, `p.30 Drawdown`, `p.31 Annual Returns`, `p.34 Scoring`)
- Same chrome as the content slide (white bg, red title top-left, logo top-right, page number bottom-right).
- The body region is filled with a single embedded image — chart, diagram, or table screenshot — centered horizontally and sized to ~10.5 in × 5 in maximum so the chrome stays visible.
- Captions or titles inside the embedded image must not duplicate the slide title.

### 4.6 Contact Slide (`pdf p.42`, last slide)
- Background: white with the gray fingerprint motif (`assets/kaxanuk_fingerprint_gray.png`) anchored to the right edge.
- Left-of-center: small `Contact` heading (Montserrat Regular, 32 pt, `#E84328`), with the contact email below it as a hyperlink (Montserrat Regular, 18 pt, `#1155CC`, underlined). The brand red logo (`assets/kaxanuk_logo_red.png`) sits inside the fingerprint motif on the right.
- No page number.

---

## 5. Iconography & Imagery

- The brand-red logo (`assets/kaxanuk_logo_red.png`) is the only logo used on chrome (top-right of every content slide).
- The wordmark (`assets/kaxanuk_wordmark.png`) is reserved for the cover slide.
- The gray fingerprint motif (`assets/kaxanuk_fingerprint_gray.png`) is reserved for the cover and contact slides.
- Charts must use the brand red `#E84328` as the highlight color. Greys for secondary series; never introduce other primaries (no native blue/green).
- Diagrams (UML, flow charts) should be embedded as raster screenshots if produced outside PowerPoint — the source deck does this on slide 11.

---

## 6. Bullet & Arrow Glyphs

| Glyph | Code point | Use |
|-------|-----------|-----|
| `●` | U+25CF | Standard body bullet, charcoal `#2C2C2C`. |
| `➔` | U+2794 | Section/agenda arrow, brand-red `#E84328`. Used for top-level enumerations like the Content slide and "Selection / Sizing / Timing" slide. |
| `👉` | U+1F449 | Decision callout — use exactly once per deck, on the implementation-decision slide. |
| `≤`, `≥` | U+2264 / U+2265 | Use the actual Unicode glyphs in formulas, not `<=` / `>=`. |

---

## 7. Voice & Tone (visual-text alignment)

The visual brand pairs with a precise, technical tone — short declarative sentences, no marketing fluff. Bullet stems are noun phrases or short clauses, not full paragraphs. Bold is reserved for the *one* key term in a sentence. This matches the audience ("CFA-holders and quants — no dumbing down, no hype" per `AGENTS.md`).
