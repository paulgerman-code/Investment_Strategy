# Examples

Two artefacts live here:

| File | What it is |
|------|------------|
| `Strategy_Blueprint_Example.pdf` | The canonical KaxaNuk Strategy Blueprint — *Liquidity-Weighted Trend Strategy*. This is the visual ground truth the skill is benchmarked against. Every section, table, table style, heading, page number, and chart caption in any new blueprint should look like this PDF. |
| `content_liquidity_weighted_trend.json` | A fully populated `content.json` that, when fed to `scripts/build_blueprint.py`, reproduces the Strategy Blueprint above. Use it as a worked reference when filling in a new strategy's content. |

## How to regenerate the example as a PDF

From the skill folder root:

```bash
pip install reportlab pillow
python scripts/build_blueprint.py \
    --content examples/content_liquidity_weighted_trend.json \
    --output Liquidity_Weighted_Trend_Strategy_Blueprint.pdf
```

This is also a useful smoke-test before iterating on the script: if the output of this command starts to drift from `Strategy_Blueprint_Example.pdf`, the skill or the script has regressed.

## How to regenerate the example as a Word document

```bash
pip install python-docx pillow
python scripts/build_blueprint_docx.py \
    --content examples/content_liquidity_weighted_trend.json \
    --output Liquidity_Weighted_Trend_Strategy_Blueprint.docx
```

The DOCX builder reads the same `content.json`, so once the file is filled in, either format can be regenerated on demand.

## How to start a new strategy from this example

1. Copy `content_liquidity_weighted_trend.json` to your working directory and rename it (e.g. `content_<your_strategy>.json`).
2. Replace fields top-down — `strategy_name`, `idea_description`, `background_research`, etc. Leave the structural keys in place; only update values.
3. Run the build script from your working directory pointing at your new file.

Do **not** edit the example file in place. Keep `content_liquidity_weighted_trend.json` as a stable reference.
