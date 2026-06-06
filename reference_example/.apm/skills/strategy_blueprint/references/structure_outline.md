# Strategy Blueprint — Canonical Structure

This is the exact section tree of the example PDF (`examples/Strategy_Blueprint_Example.pdf`). Reproduce it node-for-node in every blueprint. The hierarchy below maps 1:1 to the headings the build script renders:

```
H1  Cover                                    [page 1, no heading text — rendered specially]
H1  Table of Contents                         [page 2 — Process Flow concept]
H1  [Detailed dotted TOC]                     [pages 3-4 — auto-generated]

H1  Strategy Definition                       [page 5+]
    H2 Idea Description
    H2 Background Research
        H3 [Paper title] (one H3 per paper, with Date / Authors / Link / bullets)
    H2 Investable Universe and Constraints
        H3 Universe
        H3 Strategy Constraints
    H2 Benchmark
    H2 Hypothesis
        H3 Market Inefficiency
        H3 Behavioral
        H3 Structural
        H3 Null Hypothesis
    H2 Unified Modeling Language Diagrams

H1  Feature Engineering
    H2 Data
        H3 Key Variables
        H3 Adjusted Prices Incorporate
    H2 Data Analysis
        H3 Time Series and Cross-Sectional Analysis
        H3 Key Financial Metrics
        H3 Common Visualizations
    H2 Features
        H3 Trend Indicators                   [feature table]
    H2 Strategy Signals
        H3 [Signal name]                      [piecewise definition]
            H4 Signal Logic

H1  Strategy Design
    H2 Strategy Modeling                      [Dimension / Question table]
    H2 Portfolio Construction
        H3 Selection Rules
        H3 Sizing Rules
        H3 Rebalancing Logic — Event-Driven
        H3 Market Regime Handling
    H2 Backtesting
        H3 Backtesting Config                 [parameter / value / description table]
        H3 Performance Top 20                 [chart image]
        H3 Commissions Top 20                 [chart image]
        H3 Drawdown Top 20                    [chart image]
        H3 Annual Returns Top 20              [chart image]
    H2 Attribution Analysis                   [numbered findings]
    H2 Strategy Score                         [scoring table with gradient]

H1  Conclusions
    H2 Hypothesis Validation
    H2 Is This An Implementable Strategy?
    H2 Next Steps

H1  Findings, Concerns and Decisions
    H2 [Iteration name, e.g. "Initial Strategy Design"]
        H3 [YYYY-MM-DD]                        (one H3 per dated entry)
```

## Heading Style Cheat Sheet

| Level | Font | Size | Colour |
|-------|------|------|--------|
| H1 | Montserrat Bold | 24 pt | `#E84328` |
| H2 | Montserrat Bold | 20 pt | `#E84328` |
| H3 | Montserrat Bold | 16 pt | `#E84328` |
| H4 | Montserrat Bold | 14 pt | `#000000` |

## Required vs Optional

Every H1 and H2 is **required**. If the user has nothing to say, render the heading and write `_Pending — see TODO list._` underneath. H3 nodes that enumerate items (papers, dated entries, chart images) repeat as needed; the example has 4 papers, 4 chart images, and 2 dated entries.

## Page Breaks

- Cover always alone.
- Process-Flow concept page (`Table of Contents`) always alone.
- Each H1 starts on a new page.
- Within an H1, allow flow — do not force breaks per H2.
- The Strategy Score table is allowed to break across pages but its header row must repeat.
