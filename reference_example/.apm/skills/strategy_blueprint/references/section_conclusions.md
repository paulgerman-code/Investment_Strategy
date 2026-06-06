# Section 4 — Conclusions

The job of this section is to commit. After 16 pages of evidence, the document must (a) say whether the hypothesis held, (b) say whether the strategy is implementable, and (c) lay out concrete next steps. Hedging here ruins the document.

## H2 — Hypothesis Validation.

Note the trailing period in the heading — the example PDF prints it as `Hypothesis Validation.` and the skill must reproduce the period.

The body opens with a bold lead-in question: **`Did the data support the source of returns?`** — rendered as a Montserrat Bold 10 pt line.

Then three labelled blocks, each introduced by a bolded run, followed by bulleted prose:

- **Key Findings:** 3-5 bullets stating what the backtest, attribution, and validation work actually showed. Numbers preferred over adjectives.
- **Interpretation:** 2-3 bullets translating the findings into a verdict on the hypothesis. Acceptable verdicts: *fully validated*, *partially validated*, *rejected*.
- **Conclusion:** a single bullet stating the take-home in one sentence. The example reads:

> ● The strategy works — but we now understand why it works, and where it breaks

## H2 — Is This An Implementable Strategy?

Three labelled blocks, each rendered as a bolded run + arrow bullets `➔`:

### Implementation Risks
3-5 risks, each formatted as:

```
Factor decay
➔ Momentum signals weaken as they become crowded
```

The bolded run is the risk name; the arrow line is the explanation.

### Operational Requirements
3-5 arrow-bullet lines describing what infrastructure must exist for the strategy to deploy. Format:

```
➔ Robust data pipelines and execution systems
```

### Decision
A single line prefixed with `👉` (white pointing-finger emoji), stating the deployment posture:

> 👉 Suitable for paper trading and controlled deployment

Acceptable postures: `Suitable for paper trading and controlled deployment`, `Suitable for live deployment with cost controls`, `Not suitable for deployment — needs further research`.

### Key Condition
A short prose line under the *Decision* describing the condition under which deployment is viable. The example:

> Implementation must include cost control, turnover constraints, and exposure management

## H2 — Next Steps

A numbered list (1-4) where each numbered top-level item is a *bolded* category and the children are arrow-style or `●` bullets:

```
1. Strategy Improvements
   ● Neutralize unrewarded beta exposure
   ● Introduce momentum crash protection / regime filters
   ● Enhance signals with additional features (multi-factor approach)

2. Implementation & Infrastructure
   ● Build production-grade data pipelines
   ● Implement execution-aware backtesting (costs, slippage)
   ● Deploy paper trading environment

3. Validation & Monitoring
   ● Track out-of-sample performance
   ● Monitor factor exposures and drift
   ● Define KPIs and alert systems

4. Scaling & Deployment
   ● Estimate capacity limits and liquidity impact
   ● Define capital allocation strategy
   ● Prepare for incremental live deployment
```

These four category names — *Strategy Improvements*, *Implementation & Infrastructure*, *Validation & Monitoring*, *Scaling & Deployment* — are part of the brand. Keep them. Replace only the children.

## Anti-Patterns
- Do not delete the *Decision* line or replace the `👉` emoji with a different glyph. It is the load-bearing element of this section.
- Do not soften the *Conclusion* into a question or a hedge ("It seems that..."). The conclusion is a verdict.
- Do not propose more than 4 *Next Steps* categories — the document's rhythm depends on the four-bucket structure.
