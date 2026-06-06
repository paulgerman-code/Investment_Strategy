# Strategy Presentation — Required Slide Structure

This file is the canonical slide-by-slide outline of the Strategy Presentation deck. Every output must contain these slides in this order with these exact titles. Slide numbers below match the page numbers shown in the source PDF (`Deliverables_Templates/Strategy Presentation Template.pdf`).

The deck has **41 slides** (the source PDF has 42 page images because slide 2 is the title and slide 1 is the wordmark cover). Some slides intentionally repeat a title across multiple pages — those repetitions are kept here so the structure mirrors the source.

Layout codes used below:
- **COVER** — wordmark + fingerprint, no title text (template 4.1).
- **TITLE** — full-bleed brand-red title slide (template 4.2).
- **DIVIDER** — full-bleed charcoal section divider (template 4.3).
- **CONTENT** — white slide with red title top-left, logo top-right (template 4.4).
- **VISUAL** — same chrome as CONTENT, body filled by a single chart, table, or diagram (template 4.5).
- **CONTACT** — final slide (template 4.6).

---

## Slide-by-slide outline

| # | PDF p. | Layout | Title | Subtitle / Body summary |
|---|--------|--------|-------|-------------------------|
| 1 | 1 | COVER | — | KaxaNuk wordmark + gray fingerprint motif. |
| 2 | 2 | TITLE | Strategy Presentation | Subtitle = strategy name (e.g. `Liquidity-Weighted Trend Strategy`). |
| 3 | 3 | CONTENT | Content | Agenda with arrow bullets `➔`: `Strategy Definition`, `Feature Engineering`, `Strategy Design`. |
| 4 | 4 | DIVIDER | Strategy Definition | Subtitle = strategy name. |
| 5 | 5 | CONTENT | Idea Description | Lead sentence (bold), three drivers as bullets, the moving-average rule, ranking by liquidity, fallback to SPY. Decorative document-icon may sit on the right side. |
| 6 | 6 | CONTENT | Background Research | Heading `Price Momentum`; cite Jegadeesh & Titman (1993); two bullets summarising the finding. |
| 7 | 7 | CONTENT | Background Research | Headings `Trend Following Across Asset Classes`, `Behavioral Explanation`, `Liquidity and Implementation`; cite Moskowitz/Ooi/Pedersen (2012), Daniel/Hirshleifer/Subrahmanyam (1998), Frazzini/Israel/Moskowitz (2014); one or two bullets per citation. |
| 8 | 8 | CONTENT | Investable Universe and Constraints | `Universe:` block with arrow bullet (e.g. `KN US Equity Benchmark Historical Holdings`). `Strategy constraints:` block with disc bullets (US-listed, min trading history, liquidity filter, long-only, max position size). Closing line on realism. |
| 9 | 9 | CONTENT | Benchmark | `Benchmark:` with arrow bullet (e.g. `KN US Equity Benchmark`). Three disc bullets on what the benchmark provides. Three disc bullets on what it lets us evaluate (excess returns, tracking error, active performance). |
| 10 | 10 | CONTENT | Hypothesis | `Behavioral drivers:` (2 bullets), `Structural drivers:` (2 bullets), `Hypothesis:` paragraph, `Null hypothesis:` paragraph. |
| 11 | 11 | VISUAL | Unified Modeling Language Diagrams | Embedded UML / flow-chart screenshot covering the strategy pipeline. |
| 12 | 12 | DIVIDER | Feature Engineering | Subtitle = strategy name. |
| 13 | 13 | CONTENT | Data | Lead sentence; `Key variables:` (3 bullets); `Adjusted prices incorporate:` (3 bullets); closing sentence on total-return dynamics. |
| 14 | 14 | CONTENT | Data Analysis | Lead sentence; `Important observations:` (3 bullets); `Common visualizations include:` (3 bullets). |
| 15 | 15 | CONTENT | Features | Lead sentence; `Trend Indicators` heading with two `c_` function names as bullets; explanatory line; `Liquidity Feature` heading with one `c_` function as a bullet; explanatory line. |
| 16 | 16 | CONTENT | Strategy Signals | `Trend signal definition:` block; the two `Signal = …` rules; the `Implementation` line referencing the `c_…_signal` function; one closing rationale line; one caveat about insufficient history. |
| 17 | 17 | DIVIDER | Strategy Design | Subtitle = strategy name. |
| 18 | 18 | CONTENT | Strategy Modeling | Lead sentence; sentence introducing three questions; three blocks each with a heading (`Selection`, `Sizing`, `Timing`) and an arrow-bullet question. |
| 19 | 19 | CONTENT | Portfolio Construction | `Selection rules:` (3 bullets); `Sizing rules:` (2 bullets); closing line. |
| 20 | 20 | CONTENT | Portfolio Construction | Heading `Rebalancing Logic`; lead sentence; four bullets describing rebalance triggers; closing line on continuous reflection. |
| 21 | 21 | CONTENT | Portfolio Construction | Heading `Market Regime Handling`; lead sentence on weak markets; SPY fallback statement; `This ensures:` block (3 bullets). |
| 22 | 22 | CONTENT | Historical Portfolio Generation | Lead sentence; `Each rebalance generates:` (3 bullets); closing sentence on performance evaluation. |
| 23 | 23 | VISUAL | Historical Portfolios Top 20 | Embedded portfolio-weights-evolution chart (full body width). |
| 24 | 24 | CONTENT | Backtesting | Lead sentence; `Key metrics include:` (5 bullets: cumulative returns, volatility, drawdowns, turnover, risk-adjusted returns); closing caveat on metrics-alone insufficiency. |
| 25 | 25 | VISUAL | Backtesting Config | Embedded backtest-configuration table screenshot. |
| 26 | 26 | CONTENT | Strategy Robustness | Lead sentence; `Key tests include:` (4 bullets: out-of-sample, parameter sensitivity, market regime, diversification); closing line on stable-vs-overfit. |
| 27 | 27 | VISUAL | Performance Top 20 | Embedded cumulative-returns / performance chart. |
| 28 | 28 | CONTENT | Strategy Robustness | Repeat of slide 26 layout (intentional in source deck). |
| 29 | 29 | VISUAL | Commissions Top 20 | Embedded commissions chart. |
| 30 | 30 | VISUAL | Drawdown Top 20 | Embedded drawdown chart. |
| 31 | 31 | VISUAL | Annual Returns Top 20 | Embedded annual-returns bar chart. |
| 32 | 32 | CONTENT | Attribution Analysis | Lead sentence; `Key attribution questions:` (4 bullets: market exposure, sector allocation, stock selection, factor exposures); closing line on alpha vs unintended risk. |
| 33 | 33 | CONTENT | Attribution Analysis | Numbered findings (1, 2, 3), each a 2–3 line paragraph: factor returns dominate, beta drag, size+momentum engines with momentum needing guardrails. |
| 34 | 34 | VISUAL | Scoring | Embedded Strategy Scoring table; numbered improvements list above the table. |
| 35 | 35 | DIVIDER | Conclusions | Subtitle (free choice; default `Subtitle` per source deck). |
| 36 | 36 | CONTENT | Hypothesis Validation | `Did the data support the source of returns?` lead question; `Key Findings:` block (4 bullets). |
| 37 | 37 | CONTENT | Hypothesis Validation | `Interpretation:` (3 bullets); `Conclusion:` paragraph. |
| 38 | 38 | CONTENT | Is This An Implementable Strategy? | Heading `Implementation Risks`; four sub-headings each followed by an arrow-bullet sentence: `Factor decay`, `Market impact & liquidity`, `Turnover & rebalancing`, `Capacity constraints`. |
| 39 | 39 | CONTENT | Is This An Implementable Strategy? | Heading `Operational Requirements` (3 arrow bullets); heading `Decision` with the pointing-finger glyph and a bold one-line verdict; heading `Key Condition` with a one-line condition. |
| 40 | 40 | CONTENT | Next Steps | `1. Strategy Improvements` (3 bullets); `2. Implementation & Infrastructure` (3 bullets). |
| 41 | 41 | CONTENT | Next Steps | `3. Validation & Monitoring` (3 bullets); `4. Scaling & Deployment` (3 bullets). |
| 42 | 42 | CONTACT | Contact | Body = the contact email (`research@kaxanuk.mx` by default). |

---

## Notes on intentional duplication

The source deck repeats the slide title `Background Research` (slides 6–7), `Portfolio Construction` (slides 19–21), `Strategy Robustness` (slides 26 and 28), `Hypothesis Validation` (slides 36–37), `Is This An Implementable Strategy?` (slides 38–39), `Next Steps` (slides 40–41), and `Attribution Analysis` (slides 32–33). These repetitions are deliberate — split the content as shown, do not collapse into single slides.

## Mapping deliverables to slides

When the project provides backtest outputs, map them to the visual slides as follows:

- Portfolio-weights evolution chart → slide 23.
- Backtest configuration table → slide 25.
- Cumulative-returns chart → slide 27.
- Commissions chart → slide 29.
- Drawdown chart → slide 30.
- Annual-returns chart → slide 31.
- Strategy scoring table (from `Deliverables_Templates/Strategy Scoring.xlsx`) → slide 34.

If a deliverable is unavailable, leave a placeholder rectangle on the slide labelled with the missing artefact name (`<Cumulative Returns chart unavailable>`), in `#A0A0A0`. Do **not** delete the slide — the structure must mirror the PDF exactly.
