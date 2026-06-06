# Section 3 — Strategy Design

This is the operational heart of the document. The reader must finish knowing exactly which stocks get picked, how they are sized, when the portfolio rebalances, and how the result performed.

## H2 — Strategy Modeling

A short framing paragraph followed by a 2-column table. The example opens with:

> Most research stops at: "Does the signal predict returns?"
>
> But strategy design requires answering three deeper questions during construction:

| Dimension | Question |
|-----------|----------|
| Selection | Which stocks are above both their 50-day and 200-day SMAs and rank among the Top 35 by 3-month traded value? |
| Sizing    | How should capital be allocated among selected stocks based on traded value, respecting the 20% maximum per position? |
| Timing    | When does the Top 35 composition change, requiring portfolio rebalancing? |

Use the same three rows (`Selection`, `Sizing`, `Timing`) — these labels are part of the brand. Replace only the *Question* column with strategy-specific phrasing.

## H2 — Portfolio Construction

Four H3 nodes, in this order:

### H3 — Selection Rules
A bulleted list of the eligibility filters. Each bullet should reference a concrete column expression (e.g. `c_sma_50d_200d_signal = 1`, `Ranked by c_daily_traded_value_63d`).

### H3 — Sizing Rules
A bulleted list of the weighting scheme: proportionality rule, maximum / minimum cap, normalisation rule. Use exact percentages and column names.

### H3 — Rebalancing Logic — Event-Driven
Note the *em-dash* in the heading — keep it. A single short paragraph (`Portfolio changes are triggered when:`) followed by 3-5 bullets describing the events that trigger a rebalance.

### H3 — Market Regime Handling
A short paragraph describing the fallback rule when the universe shrinks (e.g. allocate to SPY). Always state explicitly what the strategy does in *low-signal* regimes.

## H2 — Backtesting

### H3 — Backtesting Config
A 3-column table — `parameter`, `value`, `description` — with one row per backtest engine knob. Required parameters (mirrors the example): `portfolio_name`, `benchmark_file_name`, `start_date`, `end_date`, `initial_capital`, `cash_reserve_percentage`, `input_market_directory`, `excluded_market_input_columns`, `input_portfolio_directory`, `portfolio_input_format`, `commission_priority_order`, `commission_global_value`, `commission_global_format`, `data_volume`, `dashboard`, `logger_level`, `dashboard_port`. Add or remove rows to match the strategy, but never invent values — pull them from the actual config file.

### H3 — Performance Top 20
Centered chart image (typically a cumulative-return plot of the top-20 by weight versus the benchmark). Caption is the strategy name. If the user has no chart, drop a `[Performance chart pending]` placeholder.

### H3 — Commissions Top 20
Centered chart image showing realised costs / turnover impact.

### H3 — Drawdown Top 20
Centered chart image showing the underwater curve.

### H3 — Annual Returns Top 20
Centered chart image showing per-year returns vs benchmark.

All four charts are required artefacts; placeholders are acceptable for the first draft but flagged in the TODO list.

## H2 — Attribution Analysis

A numbered list (1, 2, 3, ...) of 3-5 prose findings, each opening with a **bolded one-line takeaway** followed by 1-3 sentences of explanation. The example reads:

> 1. **Factor returns drive nearly all performance.** Of the ~175% cumulative excess return, factor exposures account for ~150%, idiosyncratic (stock-picking) alpha contributes only ~25% and has flatlined since 2022.

Aim for the same structure: bolded headline + supporting numbers + one corrective recommendation per finding.

If the user has run an attribution chart, it can be embedded between the framing paragraph and the numbered findings, captioned with the strategy name.

## H2 — Strategy Score

The Strategy Score table mirrors `Strategy Scoring.xlsx` and *must* preserve the schema below.

### Schema (Strategy Score table)

| Column | Type | Format | Notes |
|--------|------|--------|-------|
| Strategy Blueprint | string | sentence case | Section grouping. Cells merge vertically for rows that belong to the same section. Allowed values: `Strategy Definition`, `Feature Engineering`, `Strategy Design`. |
| Scoring Concept | string | sentence case | One concept per row, e.g. `Hypothesis & Source of Returns`, `Research Foundation`, `Scientific Process`, `Data Quality & Integrity`, `Feature Design & Relevance`, `Signal Construction`, `Portfolio Construction Logic`, `Backtesting & Robustness`, `Attribution & Understanding`. |
| Weight | float | percentage, 2 decimals (e.g. `11.11%`) | Sum across rows must equal 100%. |
| Score (0-100) | int | integer | User-supplied. |
| Weighted Score | float | 1 decimal | Computed as `Weight × Score`. |
| Gap (Score) | float | 1 decimal, signed | Gap to the per-row maximum (`Weight × 100 − Weighted Score`). Negative values shaded coral `#F8696B` with white text. |

A final row, *Overall Score*, sums the *Weight* (should display `100.00%`), leaves *Score (0-100)* blank, and shows the column total of *Weighted Score* (and zero gap).

Conditional formatting on *Weighted Score*: 3-colour scale interpolating between `#F8696B` (low), `#FFE599` (mid), `#008A0E` (high), with the min and max defined per column.

Underneath the table, a numbered list (1, 2, 3) of 3 actionable observations the score reveals — these are written by the user, not auto-generated. Example phrasing:

> 1. We can improve the coverage of the investable universe using another data provider.

## Anti-Patterns
- Do not show backtest performance numbers in the prose without a corresponding chart in this section. The reader must be able to verify the claim visually.
- Do not skip the *Attribution Analysis* section — even if the user has no factor model, write 1-2 bullets about return drivers (idiosyncratic vs systematic) so the reader sees that decomposition was attempted.
- Do not invent score values to "fill in" the Strategy Score table. If the user has not scored the strategy, generate the empty table with `Score = TODO` per row and leave the *Overall Score* cell empty — the table must still appear.
