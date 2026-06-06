# Section 1 — Strategy Definition

This is the document's framing section. Its job is to convince a reader that there is a real, falsifiable hypothesis behind the strategy before any feature or backtest is shown.

## H2 — Idea Description

A single paragraph followed by 2-4 bulleted mechanisms. The paragraph names the asset class, the signal, and the reason the signal might predict returns. The bullets enumerate the *channels* by which the mispricing is produced.

**Example phrasing (from the canonical PDF):**

> This strategy explores the persistence of price trends in US equities using a simple but robust signal: the crossover of the 50-day and 200-day Simple Moving Averages (SMA).
>
> The central idea is that stocks experiencing sustained bullish trends tend to continue outperforming the market due to:
>
> ● Gradual information diffusion across market participants
> ● Institutional trading flows that reinforce existing momentum
> ● Behavioral underreaction by retail investors to new information

Then a closing paragraph that states the implementation rule in one or two sentences.

**Interview prompts:**
1. In one sentence, what is the signal?
2. What asset class / region / instrument does it apply to?
3. What are 2-4 economic / behavioural channels through which the signal *could* work? Frame each as a noun phrase, not a sentence.
4. What is the practical implementation rule that converts the signal into a portfolio?

## H2 — Background Research

A list of 3-4 papers, books, or industry reports that the strategy leans on. Each is a separate **H3 heading** with the paper title.

**Required fields per paper (rendered as bold-lead-in lines, not a table):**
- **Date:** `DD-MM-YYYY`
- **Authors:** Author 1, Author 2, ...
- **Link:** the literal URL or DOI as a hyperlink in `#1071E5`
- 1-3 bullets summarising the relevance to *this* strategy (not just the abstract)

**Interview prompts:**
- For each paper, what is the *one finding* that justifies a design choice in this strategy? If you cannot link the paper to a concrete decision, do not include it.

## H2 — Investable Universe and Constraints

Two H3 nodes:

### Universe
A bulleted list defining the population of eligible securities. Always specify region (e.g. `US-listed equities only`) and the source list (e.g. `KN US Equity Benchmark Historical Holdings`).

### Strategy Constraints
A bulleted list of structural constraints — minimum trading history, liquidity floors, long-only / long-short, max position size, max number of holdings, fallback assets.

**Interview prompts:**
- What is the source of the eligible list?
- What is the minimum data history each name needs?
- Liquidity / market-cap / sector constraints?
- Long-only or long-short?
- Maximum weight per name?
- Target number of holdings, and what happens when the universe shrinks below it?

## H2 — Benchmark

Bulleted block with the primary benchmark (and any fallback / secondary benchmark — usually an ETF). For ETFs include FMP Ticker, ISIN, and IPO date as nested bullets.

**Closing paragraph (mandatory):** one sentence stating that comparison against the benchmark enables evaluation of *excess returns*, *Tracking Error*, and *Active performance / Information Ratio*. This sentence is reproduced from the example because it sets up the attribution language used later.

## H2 — Hypothesis

Four H3 nodes, in this order, every time:

### Market Inefficiency
2-3 bullets describing the price-formation friction that allows the signal to produce returns.

### Behavioral
2-3 bullets describing the psychological mechanism (underreaction, overreaction, anchoring, herding, etc.).

### Structural
2-3 bullets describing the flow / liquidity / institutional feature that reinforces the effect.

### Null Hypothesis
A single bullet, framed as a falsifiable statement of *no excess return*. The example reads:

> ● The strategy does not outperform the KN US Equity Benchmark on a risk-adjusted basis.

Use that exact pattern: `The strategy does not outperform <benchmark> on <a risk-adjusted basis | a Sharpe basis | …>`. The null is what the backtest must reject.

## H2 — Unified Modeling Language Diagrams

A single image (centered, with a caption that is just the strategy name) showing the data-and-decision flow. If the user does not have a diagram ready:
1. Offer to render a minimal placeholder UML diagram from the strategy components they described above.
2. Or accept a `[UML Diagram pending]` text placeholder that the build script renders as a captioned grey box, so the document still passes self-review.
