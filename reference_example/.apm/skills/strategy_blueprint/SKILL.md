---
name: strategy_blueprint
description: >
  Author a KaxaNuk Strategy Blueprint as a PDF or a Word (.docx) document
  that mirrors the canonical Liquidity-Weighted Trend Strategy example
  exactly in structure, typography, and colour. Use this skill whenever the
  user wants to write, draft, fill in, update, or generate a Strategy
  Blueprint for an investment / trading / portfolio strategy, or mentions
  phrases like "blueprint", "strategy doc", "strategy write-up",
  "research write-up", "investment thesis document", "hypothesis doc",
  "Liquidity-Weighted Trend Strategy template", "KaxaNuk blueprint", or any
  time they ask to turn an investment idea, factor, signal, alpha, or
  backtest into a formal document. The skill supports both .pdf and .docx
  output (the user picks the format), enforces a structured interview
  before writing, the exact section hierarchy used in the example, and the
  KaxaNuk visual brand. It MUST be consulted before producing any Strategy
  Blueprint output.
metadata:
  version: 1.0
---

# KaxaNuk — Strategy Blueprint Author

## Purpose
Turn an investment idea into a publication-quality KaxaNuk **Strategy Blueprint** that follows the exact section hierarchy, typography, and colour palette of the canonical example (`examples/Strategy_Blueprint_Example.pdf` — *Liquidity-Weighted Trend Strategy*). The deliverable is either a **.pdf** (default) or a **.docx** Word document — never a slide deck or Markdown file. Prioritise faithfulness to the example over creativity — a reader should be unable to tell which document was Claude-authored and which was the original.

The output **must** look like a KaxaNuk artefact: orange (`#E84328`) section titles, Montserrat throughout, the small KaxaNuk mark in the top-right of every page after the cover, and the full KaxaNuk logo on the cover. Branding is non-negotiable — read `references/BRANDING_GUIDELINES.md` **before drafting any visual element**. The same brand applies to both PDF and DOCX output; the only difference is the rendering tool.

## Phase 0 — Confirm Inputs (MANDATORY)
Before any interview question, confirm four things in a single short message:

1. **Strategy name** — used as the cover subtitle, e.g. `Liquidity-Weighted Trend Strategy`. If the user has not given a name, propose 2-3 short options and ask them to pick one.
2. **Output format** — `.pdf` or `.docx`. PDF is the default and the visually faithful render. Choose DOCX when the user explicitly asks for a Word file or says they want to keep editing the document afterwards. If the user asks for *both*, build the DOCX first (so it is the editable master) and then export the PDF from the same `content.json`.
3. **Output path** — confirm the deliverable is written under `<strategy_slug>_Strategy_Blueprint.<pdf|docx>` in the working directory, or ask for a different location.
4. **Available source material** — ask the user to point at any of: an existing draft, a research note, a backtest output (e.g. the `Strategy Scoring.xlsx`), a UML diagram image, performance / drawdown / attribution chart images. Any artefact that already exists should be ingested rather than re-asked in the interview.

Do not start the interview until these four things are answered.

## Phase 1 — Structured Interview (MANDATORY)
The blueprint has a fixed structure. Conduct the interview **section by section** in the same order the document is read, asking only the questions that the user has not already answered through their source material. For every question, restate the user's answer in your own words to confirm understanding before moving on.

For each section below the skill must collect *enough* content to fill it. If a user resists a question, capture that as a `TODO: [section]` placeholder in the output and surface the list of TODOs at the end so they can iterate. Never silently invent content — making up a citation, ticker, or statistic is the worst failure mode of this skill.

Read `references/structure_outline.md` once before the interview begins. It contains the full section tree with the question prompts and per-section guidance the example uses.

### 1.1 Strategy Definition
Ask, in this order:
- One-paragraph **Idea Description** in plain English: what mispricing or behaviour are we exploiting, and through which mechanism (information diffusion, behavioural underreaction, structural flow, etc.)?
- 3-4 pieces of **Background Research**. For each: title, date (DD-MM-YYYY), authors, link / DOI, and 1-3 bullet findings that support the hypothesis.
- **Investable Universe and Constraints**: the universe (e.g. `KN US Equity Benchmark Historical Holdings`), any geography / market-cap / liquidity constraints, long-only vs long-short, max position size, target number of holdings, fallback rules.
- **Benchmark**: the primary benchmark and any secondary benchmark (with FMP ticker, ISIN, IPO date if it is an ETF).
- **Hypothesis**, broken into *Market Inefficiency*, *Behavioral*, *Structural*, and a one-line *Null Hypothesis*. Every blueprint must state all four — see `references/section_strategy_definition.md` for examples and the falsification test for the null.
- A **UML diagram** (or another flow diagram) of the strategy. If the user does not have one, prompt them to either (a) upload an image, or (b) accept a placeholder block in the PDF labelled `[UML Diagram pending]` so the document can still be generated.

### 1.2 Feature Engineering
- **Data**: which raw fields drive the signals (`m_close_dividend_and_split_adjusted`, volume, traded value, fundamentals, etc.) and a short note on **what the adjusted prices incorporate** (dividends, splits, corporate actions).
- **Data Analysis**: 2-4 bullets on time-series and cross-sectional behaviour, key financial metrics (means, dispersion, persistence), and the **common visualisations** the user will produce (price + overlay, ranking distribution, signal coverage over time, etc.).
- **Features**: a small table of named features with a brief description per row. Capture exact column names (e.g. `c_sma_50d`) — these names must match the production code.
- **Strategy Signals**: define each signal as a piecewise function (e.g. `Signal = 1 when SMA(50) > SMA(200)`), the data sufficiency rule, and the *Signal Logic* prose explaining why warmups exist and what the signal captures.

See `references/section_feature_engineering.md` for the exact phrasing and table formatting.

### 1.3 Strategy Design
- **Strategy Modeling**: capture answers to the three classic dimensions — *Selection*, *Sizing*, *Timing* — as a 2-column table (Dimension / Question). The questions must be specific to this strategy.
- **Portfolio Construction**:
  - *Selection Rules* — bulleted, exact column expressions.
  - *Sizing Rules* — weighting scheme, caps, normalisation.
  - *Rebalancing Logic* — events that trigger a rebalance.
  - *Market Regime Handling* — fallback when the universe shrinks.
- **Backtesting**: collect the *Backtesting Config* (parameters of the backtest engine — universe, dates, capital, costs, slippage model, etc.) as a 3-column table (`parameter`, `value`, `description`). Then the user must provide screenshots / images for: *Performance Top 20*, *Commissions Top 20*, *Drawdown Top 20*, *Annual Returns Top 20*. If any image is missing, leave a captioned placeholder.
- **Attribution Analysis**: the user supplies the prose findings — typically 3 numbered observations explaining where returns come from (factor vs idiosyncratic, beta drag, size / momentum contribution, etc.).
- **Strategy Score**: collect or compute the scoring table that mirrors `Strategy Scoring.xlsx`. Schema is fixed: columns *Strategy Blueprint* (section grouping), *Scoring Concept*, *Weight* (%), *Score (0–100)*, *Weighted Score*, *Gap (Score)*. The skill renders the green→yellow→red gradient on the *Weighted Score* column and a coral fill on negative *Gap (Score)* values, exactly as the example PDF does.

See `references/section_strategy_design.md`.

### 1.4 Conclusions
- **Hypothesis Validation**: did the data support the source of returns? Capture *Key Findings*, *Interpretation*, and a one-line *Conclusion*.
- **Is This An Implementable Strategy?**: the user lists *Implementation Risks*, *Operational Requirements*, a *Decision* line (prefixed with `👉`), and a *Key Condition*.
- **Next Steps**: a 4-bucket numbered list — *Strategy Improvements*, *Implementation & Infrastructure*, *Validation & Monitoring*, *Scaling & Deployment*.

See `references/section_conclusions.md`.

### 1.5 Findings, Concerns and Decisions
A dated journal of design decisions, framed under a single H2 (the iteration name, e.g. `Initial Strategy Design`). Each entry uses an H3 with a date in `YYYY-MM-DD` form and a short prose paragraph capturing what was decided and why. Maintain entries in chronological order. New iterations append; never overwrite a prior entry.

See `references/section_findings.md`.

## Phase 2 — Build the Document
Once all sections are filled (or marked as `TODO`), build the document using the bundled script for the chosen format. **Always use these scripts** rather than improvising with `pypdf`, `fpdf`, hand-rolled HTML, or `docx-js` — they encode the brand consistently and read the same `content.json`, so the user can re-render in a different format at any time.

`content.json` is the single source of truth both scripts consume. Its schema is documented in `references/content_schema.md`. Populate it as you finish the interview rather than at the end — it doubles as your working draft.

### 2a. PDF output (default)

```bash
python scripts/build_blueprint.py \
  --content content.json \
  --strategy-name "<strategy name>" \
  --output "<strategy_slug>_Strategy_Blueprint.pdf"
```

The PDF builder:
- Sets US Letter / 1 in margins.
- Embeds Montserrat (Regular + Bold) and Arial (for the bullet glyph). It expects them to be discoverable via the system fonts cache; if missing, it falls back to Helvetica with a warning so the document still builds.
- Places the small KaxaNuk mark in the top-right of every page after the cover.
- Renders headings in `#E84328` at the sizes specified in `references/BRANDING_GUIDELINES.md`.
- Renders the Strategy Score table with the 3-colour gradient.

### 2b. Word (.docx) output

```bash
python scripts/build_blueprint_docx.py \
  --content content.json \
  --strategy-name "<strategy name>" \
  --output "<strategy_slug>_Strategy_Blueprint.docx"
```

The DOCX builder:
- Uses the same brand: orange section headings, Montserrat default font, US Letter / 1 in margins.
- Sets the cover as its own section (no header / footer); subsequent pages have the KaxaNuk mark in the page header and a centred page-number `PAGE` field in the footer.
- Renders the Strategy Score table with the same green→yellow→red gradient and coral fill on negative gaps, written as Word `w:shd` cell shading so the colours survive in Word, LibreOffice, and Google Docs.
- Leaves the document fully editable — bullets are real bullets (the `●` glyph used in the source PDF), headings are Word "Heading 1/2/3/4" styles tinted in the brand orange, and the Strategy Score is a real Word table that the user can extend.

### Common notes
- If the script raises any error, do not paper over it. Surface the traceback to the user — it almost always means an asset is missing or `content.json` is malformed.
- If the user wants both a PDF and a DOCX, build the DOCX first (treat it as the editable master), then run the PDF builder against the same `content.json` to produce the printable artefact. Never derive one format from the other (e.g. by exporting Word to PDF) — the brand is more accurate when each builder renders directly.

## Phase 3 — Self-Review (MANDATORY)
After the document is built, do a structured self-review in this order:

1. **For PDF output:** open the PDF (using `pdftoppm` or `pymupdf`) and rasterise pages 1, 5, the first design page, and the score page.
2. **For DOCX output:** convert to PDF first using LibreOffice headless mode, then rasterise the same pages — Word's own colour rendering can lie when seen in `python-docx` alone, so the only honest visual check is the converted output.
   ```bash
   soffice --headless --convert-to pdf <strategy_slug>_Strategy_Blueprint.docx
   pdftoppm -r 150 -png <strategy_slug>_Strategy_Blueprint.pdf preview
   ```
3. Compare side-by-side against the corresponding pages in `examples/Strategy_Blueprint_Example.pdf`.
4. Confirm:
   - Cover layout (title position, logo, subtitle) matches.
   - H1 / H2 / H3 colours are `#E84328`.
   - The KaxaNuk mark sits top-right on non-cover pages.
   - The Strategy Score table renders the green→yellow→red gradient and shades negative gaps coral.
   - The TOC / process-flow page enumerates every section that actually appears in the document (no orphan headings, no missing pages).
5. List any gaps as a numbered punch list back to the user, then offer to fix them in a second pass.

The self-review is not optional — it is the cheapest way to catch the brand-drift issues users notice in the first 2 seconds of opening the document.

## Reference Files

Read these only when you reach the corresponding phase — they would otherwise crowd the context.

- `references/BRANDING_GUIDELINES.md` — full visual spec (colours, typography, layout, table styles). Read **before** generating any visual.
- `references/structure_outline.md` — the canonical section tree with one-line guidance per node.
- `references/section_strategy_definition.md` — interview prompts and example phrasing for §1.
- `references/section_feature_engineering.md` — interview prompts and example phrasing for §2.
- `references/section_strategy_design.md` — interview prompts, the Strategy Score schema, the Backtesting Config schema.
- `references/section_conclusions.md` — interview prompts and example phrasing for §4 and §5.
- `references/section_findings.md` — journal entry format.
- `references/content_schema.md` — the JSON schema consumed by `scripts/build_blueprint.py`.

## Anti-Patterns (do not do these)

- **Do not** invent citations, tickers, ISINs, dates, or numerical results. Ask the user. If they cannot answer, mark `TODO`.
- **Do not** rewrite the section hierarchy. Even if a section feels empty, keep its heading and write `_Pending — see TODO list._` so the document remains structurally identical to the example.
- **Do not** introduce new fonts, accent colours, gradient palettes, or page sizes. The brand is fixed — see `BRANDING_GUIDELINES.md`.
- **Do not** ship a slide deck or Markdown file as the final deliverable — the blueprint is always either a `.pdf` or a `.docx`.
- **Do not** "convert" Word to PDF (or vice versa) when the user asks for both formats. Run `build_blueprint.py` and `build_blueprint_docx.py` against the same `content.json` so each format renders directly from the source — that is the only way the brand stays faithful in both.
- **Do not** skip the self-review — it catches 80 % of issues before the user has to notice them.
