# Section 5 — Findings, Concerns and Decisions

This is the **research journal** at the back of the document. It is the only section permitted to use first-person plural ("we") and the only section that grows between iterations. Treat it as an append-only log.

## Structure

```
H1  Findings, Concerns and Decisions
    H2  [Iteration name]                     # e.g. "Initial Strategy Design"
        H3  YYYY-MM-DD                        # one entry per dated decision
        H3  YYYY-MM-DD
        ...
```

The example PDF has one H2 (`Initial Strategy Design`) with two H3 entries dated `2026-04-28` and `2026-04-29`. New iterations should add new H2 blocks (e.g. `Hedge Overlay Iteration`, `Live Deployment Prep`) rather than overwriting the existing ones.

## Entry Format

Each H3 is a date in `YYYY-MM-DD` form. Beneath it sits a single short prose paragraph (~80-160 words) that does three things:

1. **States the decision.** What design choice was committed to on this date?
2. **Justifies it.** Why was this the chosen option? Mention the alternatives that were ruled out.
3. **Records the consequence.** What downstream constraint or follow-up does this introduce?

Example (verbatim from the canonical PDF):

> The SMA crossover (50d/200d) was selected as the primary signal for its simplicity, interpretability, and strong academic backing. The 35-stock liquidity filter was chosen to balance diversification with the capacity limitations of smaller-cap securities. The 20% maximum position cap prevents concentration risk. SPY was selected as the fallback asset to ensure full market exposure during periods of low signal coverage. The warmup period of 200 trading days per ticker must be accounted for when defining the backtest start date to avoid survivorship and look-ahead bias.

## Tone

- First-person plural is allowed (`we learned`, `we chose`).
- Past tense for decisions already made (`was selected`, `was chosen`).
- Concrete numbers, ticker symbols, column names — no "later", "various", "some".
- One paragraph per H3, never two. If you need more than one paragraph, split into two H3 entries.

## Interview Prompts

When extending the journal:
- What date(s) did the decisions you want to log occur on?
- For each date, what was the *primary* decision?
- What alternatives were considered and rejected?
- What new constraint did the decision introduce that the next iteration must respect?

## Ordering

Entries within an H2 are chronological (oldest first). H2 iterations are also ordered chronologically (the first iteration appears first). Never reorder old entries to "clean up" the narrative — the journal's value is its time order.
