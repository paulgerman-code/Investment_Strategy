# Section 2 — Feature Engineering

This section converts the hypothesis into named, computable columns. The reader must finish the section knowing the exact data fields, the formulas, and the warmup behaviour of every signal.

## H2 — Data

### H3 — Key Variables
A bulleted list of the raw inputs the strategy reads. Use exact production column names where they exist (e.g. `m_close_dividend_and_split_adjusted`, `m_volume`, `m_traded_value`). Each bullet is a noun followed by a one-clause description.

### H3 — Adjusted Prices Incorporate
A short bulleted list of the adjustments embedded in any "adjusted close" series — `Dividends`, `Stock splits`, `Corporate actions`. Followed by a one-sentence justification:

> This ensures that signals reflect true total-return dynamics and are not distorted by mechanical price adjustments.

Reproduce that sentence (or a near-equivalent) — it is the standard KaxaNuk framing.

## H2 — Data Analysis

### H3 — Time Series and Cross-Sectional Analysis
2-4 bullets covering observed behaviour of the underlying data: trend persistence, mean reversion, autocorrelation, cross-sectional dispersion, regime stability.

### H3 — Key Financial Metrics
2-4 bullets naming the specific metrics that summarise the data: e.g. *Price trend*, *Traded value*, *Signal stability*, *Volatility regime*. One short clause each.

### H3 — Common Visualizations
A bulleted list of the charts the user will produce when investigating the data. The example uses 4 entries; aim for 3-5. Examples: price + SMA overlays, ranking distributions, signal coverage time-series, event frequency histograms.

## H2 — Features

A short paragraph naming the feature *count* and the high-level groupings (e.g. "Two core trend features and one liquidity feature are constructed from price data."). Then one or more H3 nodes, each holding a feature table.

### H3 — [Feature group, e.g. *Trend Indicators*]

A 2-column table:

| Feature | Description |
|---------|-------------|
| `c_sma_50d` | 50-day Simple Moving Average of adjusted close price. First 49 values are NaN (warmup period). |
| `c_sma_200d` | 200-day Simple Moving Average of adjusted close price. First 199 values are NaN (warmup period). |

Render in the *Reference / Config Table* style (white header, body in `#434343`, inner gridlines `#E1E1E1`).

Beneath the table, a single italicised note (Montserrat Regular 10 pt, kept upright — italic not part of the brand, but render the prose `Note: …` exactly):

> Note: To avoid overfitting, these features remain fixed throughout the research project.

Optionally include a *Features Overview* image (a small visual summary). If absent, omit silently — this caption is optional.

**Interview prompts:**
- What are the named features and their formulas?
- What is the warmup length per feature?
- Are any features explicitly held fixed for the whole project (anti-overfitting)?

## H2 — Strategy Signals

Each signal gets its own H3 node followed by:

1. A one-line introduction citing the function that generates the signal and the file it lives in (e.g. `c_sma_50d_200d_signal in simple_moving_average_alpha_signal.py`).
2. A 3-line piecewise definition, one branch per line:
   - `Signal = 1 when SMA(50) > SMA(200) → Bullish trend (upward momentum)`
   - `Signal = 0 when SMA(50) ≤ SMA(200) → Bearish trend (downward momentum)`
   - `Signal = NaN when insufficient data for either SMA → Warmup period`

   Render at 9 pt Montserrat Regular (slightly smaller than body) so the formula stands out as a code-like block.

3. An H4 — *Signal Logic* — 3 short bullets explaining: when the signal activates, what false-signal protection is in place, and what classical pattern the signal captures (e.g. *Golden Cross* / *Death Cross*).

**Interview prompts:**
- What is the function name and module path that produces the signal?
- What are the exact piecewise branches?
- What rule gates activation (warmup, data sufficiency, regime filter)?
- What classical name does the signal map to, if any?

## Anti-Patterns
- Do not introduce a feature here that is not used in the *Strategy Design* section. A feature that does not appear in *Selection Rules* or *Sizing Rules* should be removed.
- Do not list more than ~6 features at this layer; if the strategy uses many features, group them and reference an appendix.
