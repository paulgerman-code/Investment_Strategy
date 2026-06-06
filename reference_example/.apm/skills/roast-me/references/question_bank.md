# Question Bank

A reservoir of Socratic prompts for roasting an investment thesis. Pull selectively — don't fire questions verbatim or in bulk. Adapt to the user's terminology and to what they have already said. Two to three questions per turn is the ceiling.

Each section is graded by depth:
- **L1 — Frame:** confirms you understand the thesis. Always cover.
- **L2 — Probe:** standard pushback any reviewer would have. Cover most of these.
- **L3 — Stress:** advanced, regime-specific, or quant-methodology questions. Use when the user has cleanly answered L2 or when the area is the heart of the thesis.

---

## 1. Economic Rationale

**L1 — Frame**
- In one sentence, why should this strategy make money?
- Who is on the other side of these trades, and why are they willing to lose?
- What is the time horizon over which the thesis is supposed to play out?

**L2 — Probe**
- What is the economic mechanism — risk premium, behavioral bias, structural friction, information advantage?
- If this is a known anomaly, why hasn't it been arbitraged away? What is your edge versus the funds already running it?
- Has the rationale held up across market regimes, or is it specific to the post-2010 low-rate era?
- What changed in markets that would make this rationale stop working?

**L3 — Stress**
- If you had to take the bear case in front of an allocator, what is the strongest argument that this is data-mined and the rationale was retrofitted?
- Can you point to academic literature, practitioner research, or natural experiments that independently support the mechanism — or only your own backtest?
- What is the *capacity* of this strategy at the level of edge it produces, and at what AUM does the edge erode?

---

## 2. Universe and Data

**L1 — Frame**
- What is in the universe — markets, sectors, market-cap floor, listing requirements?
- What is excluded, and why?
- What is the data source for prices, fundamentals, and corporate actions?

**L2 — Probe**
- Is universe membership *point-in-time*? On the rebalance date in 2014, are you using the index constituents as they were in 2014, or as they are today?
- How are delistings, mergers, bankruptcies, and spinoffs handled? Are returns to zero captured?
- For fundamentals, are you using the as-reported values available on the rebalance date, or values that have since been restated?
- What is the lag between fiscal period end and the date the data was actually filed and available to the market?
- ADRs, dual listings, share classes — which line do you trade and how do you avoid double-counting?

**L3 — Stress**
- What does the data *not* see? Private placements, dark-pool prints, OTC quotes, off-exchange?
- For micro-caps in the universe, what fraction would actually be tradeable at the volumes your strategy implies?
- Are you confident the survivorship-free history goes back the full backtest window, or does the dataset get thinner before some date?
- How are currency conversions, dividend reinvestment, and tax withholding modeled?

---

## 3. Signal Construction

**L1 — Frame**
- Walk me through the formula for each signal in plain English, then in code.
- What does each input represent, and where is it coming from in the data curator?
- How is the signal turned into a portfolio decision — ranked, thresholded, scored?

**L2 — Probe**
- Why this functional form? Did you try simpler versions and what happened?
- Where did the parameter values come from — fit on data, theory, convention?
- How sensitive is the signal to outliers, missing data, or stale fundamentals? What is the imputation rule?
- If two signals are combined, are they independent or do they encode the same underlying factor?
- What does the cross-sectional distribution of the signal look like — fat tails, sector concentration, market-cap bias?

**L3 — Stress**
- If I shifted every parameter by ±20%, does the result degrade gracefully or fall off a cliff? A cliff is a sign of overfit.
- Is the signal stationary, or does it drift over time? If it drifts, do you detrend, demean, or rank-normalize?
- What is the autocorrelation of the signal? If it's high, your "independent" backtest periods are not independent.
- Have you decomposed the strategy's returns into known factors (size, value, momentum, quality, low-vol)? What is left after stripping those out?

---

## 4. Backtest Methodology

**L1 — Frame**
- What is the backtest window — start, end, why those dates?
- What is the rebalance frequency, and why?
- Is this in-sample, out-of-sample, walk-forward, or all of the above?

**L2 — Probe**
- How many parameter combinations did you try before arriving at this one? What is the implied false-discovery rate?
- Did any feature engineering, scaling, threshold selection, or imputation use information from the full sample?
- How are you handling the look-ahead in earnings releases, restatements, index reconstitutions, and corporate actions?
- Have you run the strategy on a held-out window the parameters never touched? What was the degradation?
- Costs — commission, spread, slippage, borrow, market impact — at what level, and is that calibrated to the universe and turnover?

**L3 — Stress**
- If I picked a random subset of years from your backtest and dropped them, does the Sharpe survive, or is it carried by two or three good periods?
- Have you bootstrapped the equity curve to put a confidence interval on the Sharpe? What does the bottom 5% look like?
- For the parameter set you chose, what is the rank of its in-sample performance among all combinations you tried? If it's the top 1%, that's the overfitting tax you're paying.
- Have you run a deflated Sharpe ratio or White's reality check given the number of trials?
- What does the strategy look like *before* you applied your latest fix? Improvements that only show up after the most recent change are the most suspect.

---

## 5. Portfolio Construction

**L1 — Frame**
- How are positions sized — equal-weight, signal-weighted, vol-weighted, mean-variance?
- Are there caps on single-name, sector, or factor exposures?
- What is the rebalance rule — calendar, threshold, signal-driven?

**L2 — Probe**
- What is the average and worst-case turnover, and is it consistent with the cost assumptions?
- What does concentration look like — top 10 holdings, Herfindahl, sector weights versus benchmark?
- How are corporate actions handled mid-rebalance — special dividends, splits, M&A?
- Is there leverage, shorting, or derivatives? If so, how are financing, borrow, and margin modeled?
- For shorts: what is the borrow availability assumption, and how often does a name go hard-to-borrow during the backtest?

**L3 — Stress**
- At what AUM does the strategy start to move the names it trades? Have you estimated participation rate as a percentage of ADV?
- If the borrow assumption is wrong by 100bps annualized, what happens to the Sharpe?
- Is the rebalance rule path-dependent in a way that creates regret risk versus a slightly different starting date?
- What happens if a planned rebalance falls on a closed market or a halted name?

---

## 6. Risk and Regime

**L1 — Frame**
- What is the worst drawdown in the backtest, when did it happen, and why?
- What regimes is the strategy designed to perform in, and which regimes does it explicitly bet against?
- What is the failure mode — slow bleed, sudden crash, both?

**L2 — Probe**
- Walk me through 2008 H2, 2011 Q3, 2015–16, 2018 Q4, 2020 Q1, 2022 calendar year. What was the position, the drawdown, and the exit rule?
- What is the correlation to SPX, to a value factor, to a momentum factor, to credit spreads, to vol? If correlations are stable, you're a known beta in disguise.
- How will you know in real time that the strategy is broken, versus just having a bad month?
- What is the kill switch — a drawdown trigger, a regime indicator, a Sharpe-over-rolling-window threshold?

**L3 — Stress**
- If liquidity dried up tomorrow on 30% of the names, can you exit without crystallizing the worst of the drawdown?
- What is the implied tail dependence — does the strategy lose more in down markets than its average beta suggests?
- Have you run a stress on a regime not in the backtest — e.g., a sustained high-real-rate environment if your data starts in 2010?
- How does the strategy behave during factor crowding events (e.g., Aug 2007 quant quake, Feb–Mar 2020)?

---

## 7. Reproducibility and Operations

**L1 — Frame**
- Can you regenerate the exact backtest equity curve from a clean clone, with seeds fixed?
- Are universe, signal, and rebalance parameters in `Config/*.xlsx`, or in code?
- Is the lockfile committed?

**L2 — Probe**
- If a teammate pulls main and runs `run_backtest_engine.py` today, do they get the same numbers as in the latest memo? If not, what is the source of drift?
- Are all strategic decisions recorded somewhere durable (commit history, the Strategy Blueprint), or only in someone's head?
- For every error or course-correction made this session, is there a concrete guardrail in place so it does not recur?
- Where does the user document the *one change* between this run and the previous one?

**L3 — Stress**
- If you discovered a bug today that retroactively invalidates a parameter choice from two weeks ago, what is the procedure for tracing what else depends on that choice?
- Are the data curator outputs versioned? Can you reproduce yesterday's signal if today's data vendor pull replaces a value?

---

## 8. Presentation and Communication

**L1 — Frame**
- Who is the audience for this thesis — team lead, judges, allocators?
- What is the one thing you want them to remember?
- What is the one number that summarizes whether this works?

**L2 — Probe**
- Can you explain the strategy in 60 seconds without using the word "factor", "Sharpe", or "alpha"?
- If the judges challenge your costs or your survivorship handling, what is the one-sentence answer that closes the question?
- What is the chart you would lead with, and what is the chart you'd rather not show? Show the second one anyway and explain it.
- Have you prepared a falsification statement — "this strategy is wrong if X happens" — that the audience can hold you to?

**L3 — Stress**
- Practice the hostile question: "How do I know this isn't just leveraged value with extra steps?" Answer it in two sentences.
- If a judge says "your Sharpe is 1.4, but mine is 1.6 with a simpler model", what's your response — and is it defensive or substantive?
