---
name: strategy_presentation_builder
description: >
  Build the team's Strategy Presentation deck (.pptx or .pdf) for the
  KN Hack 2026 challenge in the official KaxaNuk visual identity. Use this
  skill whenever the user asks to create, regenerate, refresh, or update
  the strategy presentation, the strategy slide deck, the final pitch, or
  the deck the team will ship at the hackathon — even if they only say
  things like "make the deck", "rebuild the slides", "presentation pptx",
  "presentation pdf", or "turn the results into slides". The skill knows
  the exact 41-slide structure derived from
  `Deliverables_Templates/Strategy Presentation Template.pdf`, the brand
  colors, fonts, logo placement, and a python-pptx builder script that
  can output either PPTX or PDF. It MUST be consulted before producing
  any Strategy Presentation output so the result matches the corporate
  template instead of a generic deck, and it MUST always ask the user
  whether they want the deck delivered as PPTX or PDF before rendering.
metadata:
  version: 1.0
---

# Strategy Presentation Builder

## Purpose
Render the team's Strategy Presentation as a `.pptx` that matches the KaxaNuk visual identity (`Deliverables_Templates/Strategy Presentation Template.pdf`) slide-for-slide. Treat the structure as fixed — content varies per strategy, but layouts, titles, and order do not.

## Skill layout
```
strategy_presentation_builder/
├── SKILL.md
├── references/
│   ├── BRANDING_GUIDELINES.md   # colors, typography, geometry, layouts
│   ├── SLIDE_STRUCTURE.md       # canonical 41-slide outline
│   └── assets/
│       ├── kaxanuk_logo_red.png         # top-right logo on every content slide
│       ├── kaxanuk_wordmark.png         # cover slide wordmark
│       └── kaxanuk_fingerprint_gray.png # cover & contact decorative motif
└── scripts/
    └── build_pptx.py            # python-pptx renderer used in Phase 4
```

`BRANDING_GUIDELINES.md` and `SLIDE_STRUCTURE.md` are the source of truth for visuals and order. Read both during Phase 1 — never paraphrase, never guess. `build_pptx.py` is the renderer; do not rewrite it inline.

## Phase 0 — Pre-flight (MANDATORY)
Before drafting anything:

1. **Ask the user which output format they want — PPTX or PDF — every time the skill runs.** Never assume. PPTX is editable in PowerPoint and Keynote; PDF is fixed-layout and good for sharing or printing. Both formats render from the same source so the user can rerun the skill with the other format any time. Record the answer; it determines the file extension and the renderer flag in Phase 4. If the user asks for both, run the skill twice — once per format — rather than producing two artefacts from a single invocation.
2. Confirm `Deliverables_Templates/Strategy Presentation Template.pdf` exists. If the user is working in a different folder, ask whether the same template still applies.
3. Ensure `python-pptx` is available in the active environment. If not, the user must install it: `pip install python-pptx` (or add to the project's lockfile).
4. If the user picked PDF, also confirm LibreOffice is installed and `soffice` (or `libreoffice`) is on PATH — the renderer shells out to it for the PDF conversion. If LibreOffice is missing, surface that to the user immediately and ask whether to install it or fall back to PPTX.
5. Read `references/SLIDE_STRUCTURE.md` for the slide order and `references/BRANDING_GUIDELINES.md` for visual rules.

## Phase 1 — Content Discovery (MANDATORY)
Pull strategy content from the project context — do not invent it.

1. Ask the user — or read the Strategy Blueprint if one exists — for the locked decisions (universe, signals, portfolio rules, benchmark, backtest window). Do not invent them.
2. Read the latest backtest outputs under `Backtest_Engine/` (or whichever folder the project's `run_backtest_engine.py` writes to). Look for cumulative-returns, drawdown, commissions, annual-returns, and portfolio-weights charts.
3. Read `Deliverables_Templates/Strategy Scoring.xlsx` (or the project equivalent) for the scoring table to embed on slide 34.
4. Confirm with the user any additions or changes since the last deck build.
5. List every gap (missing chart, missing rationale, unconfirmed decision). Surface gaps to the user **before** rendering — do not silently leave slides blank.

## Phase 2 — Strategy Snapshot Interview
Confirm the variables that change per deck. Ask the user to confirm or override the defaults below:

- **Strategy name** (subtitle on the title and divider slides, e.g. `Liquidity-Weighted Trend Strategy`).
- **Universe** and **benchmark** (slides 8–9).
- **Selection / sizing / timing rules** (slides 18–21).
- **Top-N** and **max position size** (referenced on slides 5, 18, 19).
- **Fallback instrument** (slide 21, default `SPY`).
- **Contact email** (slide 42, default `research@kaxanuk.mx`).
- **Subtitle line** for divider slides (default = strategy name).

Restate every confirmed value before continuing. If a value cannot be sourced from the project context and the user has no opinion, flag it as a "TBD" placeholder rather than fabricating a number.

## Phase 3 — Build the Deck JSON
Translate the confirmed content into a `Deck` object that matches the schema consumed by `scripts/build_pptx.py`. The JSON shape is:

```json
{
  "strategy_name": "<string>",
  "contact_email": "<string>",
  "slides": [
    {
      "layout": "cover|title|divider|content|visual|contact",
      "title": "<string|null>",
      "subtitle": "<string|null>",
      "page_number": <int|null>,
      "image_path": "<absolute path|null>",
      "body": [
        {"kind": "para",     "text": "<string>"},
        {"kind": "heading",  "text": "<string>"},
        {"kind": "callout",  "text": "<string>"},
        {"kind": "bullets",  "items": ["<string>", ...]},
        {"kind": "arrows",   "items": ["<string>", ...]}
      ]
    }
  ]
}
```

Hard rules when authoring this JSON:

- The slide list MUST be exactly 42 entries — one per row in `references/SLIDE_STRUCTURE.md` — in that exact order, with the layout codes and titles shown there. The "duplicate" titles on slides 6/7, 19/20/21, 26/28, 32/33, 36/37, 38/39, 40/41 are intentional and must be preserved.
- Use `"kind": "arrows"` only where the source deck uses the brand-red `➔` glyph (Content slide, the `Selection / Sizing / Timing` blocks, the `Universe`, `Benchmark`, `Implementation Risks`, `Operational Requirements` blocks). Everywhere else use `"kind": "bullets"` (filled disc).
- `page_number` is the same as the source PDF page number (3, 5, 6, …, 41). Cover/title/divider/contact slides should pass `null` so no footer renders.
- For `visual` slides, set `image_path` to an absolute path. If the asset is not yet generated, leave it `null` — the renderer will draw a labelled placeholder rectangle, which is better than dropping the slide.

Save the JSON to `Investment_Strategy_Example/.cache/strategy_deck.json` (create the folder if missing). This is a build artefact, not a deliverable — it makes regeneration cheap.

## Phase 4 — Render
Use the format chosen in Phase 0. From the project root:

**PPTX (editable):**
```
python .claude/skills/strategy_presentation_builder/scripts/build_pptx.py \
  --input Investment_Strategy_Example/.cache/strategy_deck.json \
  --format pptx \
  --output Investment_Strategy_Example/Strategy_Presentation.pptx
```

**PDF (fixed-layout, requires LibreOffice on PATH):**
```
python .claude/skills/strategy_presentation_builder/scripts/build_pptx.py \
  --input Investment_Strategy_Example/.cache/strategy_deck.json \
  --format pdf \
  --output Investment_Strategy_Example/Strategy_Presentation.pdf
```

The renderer always builds the PPTX internally; the `pdf` format simply runs `soffice --headless --convert-to pdf` afterwards and writes the resulting PDF to the requested path. No other conversion tool is supported — it is the only one that preserves Montserrat, the brand fills, and the embedded raster images at full fidelity.

To smoke-test the renderer without real content (e.g. verifying assets resolve):

```
python .../scripts/build_pptx.py --example --format pptx --output /tmp/strategy_demo.pptx
python .../scripts/build_pptx.py --example --format pdf  --output /tmp/strategy_demo.pdf
```

## Phase 5 — Verification (do not skip)
After rendering, verify:

1. The output file opens without repair prompts (PowerPoint/Keynote/LibreOffice for PPTX; any PDF reader for PDF).
2. Page/slide count equals 42.
3. Slide 2 is full-bleed brand red `#CB2E15`; slides 4, 12, 17, 35 are full-bleed charcoal `#2C2C2C`; all other content slides are white with a top-right red logo.
4. Page numbers run 3, 5, 6, … on the same slides shown in `SLIDE_STRUCTURE.md` (cover/title/dividers have no number).
5. The strategy name and contact email appear unchanged on the title slide, all four divider slides (where used as subtitle), and the contact slide.

If a verification step fails, edit the JSON or `build_pptx.py` rather than the rendered file. Hand-edits in PowerPoint or a PDF editor break reproducibility, which violates the project's standing quant guardrails (`AGENTS.md` §4).

## Phase 6 — Record the Build
After a successful build:

- Note the build in your commit message: `Built Strategy Presentation v<N> [pptx|pdf]; output at Investment_Strategy_Example/Strategy_Presentation.<ext>`.
- If the build surfaced a gap (missing chart, missing rationale), tell the user so the next iteration does not hit the same gap.

## Common pitfalls

- **Compressing duplicate-titled slides.** The deck repeats titles on purpose to give each idea breathing room. Keep them split.
- **Substituting a different red.** Only `#CB2E15` (fills) and `#E84328` (text/accents) are valid. Other reds break the brand.
- **Dropping the page numbers.** The corporate deck shows them on every content slide except cover/title/dividers/contact. Match exactly.
- **Replacing Montserrat.** Fall back to Arial only if Montserrat is not available; do not introduce a third font.
- **Embedding charts as live PowerPoint charts.** The source deck embeds rasterised images. Match that — render charts to PNG/JPG first, then drop them in via `image_path`.
