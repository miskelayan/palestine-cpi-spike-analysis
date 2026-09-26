# Data validation and analysis safeguards

The analysis uses official Palestinian Central Bureau of Statistics (PCBS) CPI data and the consolidated project workbook.

## Source reconciliation

| Check | Result |
|---|---|
| Major-group observations | 585: 15 codes × 39 months |
| Detailed observations | 5,070: 130 codes × 39 months |
| Detailed English labels | 124 unique names; codes remain the unique series identifiers |
| Major-group source agreement | All 585 levels match the official workbook within 1e-8 |
| Detailed source agreement | All 5,070 levels match within 1e-8 |
| Missing CPI levels | 0 in both tables |
| Duplicate code-month keys | 0 |
| Calendar coverage | December 2022–February 2026, complete within each series |
| Recovered changes | 15 major-group changes for February 2024 |

The February 2024 major-group layout has three blank columns between the index and its percentage change. Recalculating adjacent-level changes recovers the omitted percentages. Original extracted percentages are retained in `reported_pct_change`; the calculated series is `pct_change`. Missing December changes remain missing because November is unavailable.

The live source extends beyond the frozen study period. Later observations are excluded. File hashes and maximum numerical discrepancies are recorded in [provenance.json](../data/processed/provenance.json).

## Modeling safeguards

- Identify series by string code, preserving leading zeros and hierarchical punctuation.
- Model codes 01–13. Keep aggregate CPI and 12+13 outside the training rows to prevent overlap.
- Keep detailed parent/child series descriptive; do not treat them as independent samples.
- Use only prior-month information in predictors. Shift rolling windows before computing them.
- Require six prior monthly changes; do not impute the warm-up period.
- Split by complete calendar months. Fit encoding and scaling on training data only.
- Define the upward-spike threshold before inspecting held-out performance.
- Evaluate on later months and retain per-row predictions for independent checking.
- Compare against no-spike and persistence rules, not accuracy in isolation.

## Interpreting different analyses

Linear Regression of the CPI level and Logistic Regression of a binary spike answer different questions. An in-sample R² measures fit to observed levels; it is not evidence of future spike detection and is not interchangeable with held-out precision, recall or F1. The published classification results use a chronological holdout.

The regional commodity snapshot contains different goods and package units. Its simple mean price is not a cost-of-living index. Item-specific regional weights must not be interpreted as official overall regional CPI weights. Zero entries require source clarification before being interpreted as free goods or price discounts.

## Verification

Eight integrity tests check source reconciliation, unique keys and periods, missing-label boundaries, future-outcome isolation, cross-group isolation, missing/duplicate month rejection, train-only preprocessing and confusion-matrix orientation. The executed notebook independently recalculates all primary evaluation metrics from saved predictions.

Run from the repository root:

```bash
python -m unittest discover -s tests -v
python -m scripts.execute_notebook
```
