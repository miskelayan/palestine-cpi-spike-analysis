# Methodology and limitations

## Question and academic context

Can prior monthly CPI movements help anticipate large **next-month increases in an expenditure group's CPI** in Gaza? This is a retrospective one-month-ahead classification experiment, not a national CPI forecast, causal analysis, or deployed alert system.

The scope follows *Project for DATA ANALYTICS FOR BUSINESS.docx* by **Misk Elayan, Asil Khalil, and Sandra Shwamreh**, reviewed alongside their original `Palestine_CPI_Project_Pack.xlsx`. The report proposed Logistic Regression, Random Forest and optional ARIMA/SARIMA. Its prospective statements are not empirical findings. This repository supplies the executed analysis. The personal report and complete multi-source workbook are not redistributed.

The supplied original `Copy_of_gaza_cpi_final.ipynb` was also reviewed; see the [lineage and methodological review](original_notebook_review.md). Its descriptive scope is retained, while its in-sample linear-regression fit is not presented as predictive evidence.

## Data and validation

The frozen PCBS extract has 585 rows: 15 codes × 39 months, December 2022–February 2026. December supplies the starting index for January's change. Base year: 2018 = 100. CPI levels are indices, not currency prices.

- Validate unique `(code, date)` keys, positive/nonmissing levels and complete monthly calendars before engineering lags. Preserve leading zeros and punctuation in codes.
- Recompute `100 * (index_t / index_(t-1) - 1)` without forward filling. Retain source-reported changes separately. Nonmissing changes reconcile within floating-point tolerance.
- Recover 15 missing February 2024 changes from observed levels. The official major-group workbook has three blank columns between February's level and percentage-change column; the project-pack extraction missed the latter. This is an extraction omission, not an absent index observation. December 2022 changes remain missing because November is outside the extract.
- The detailed sheet has **130 distinct codes and 124 distinct English labels**, with 5,070 rows. Repeated names are not unique identifiers.
- All 5,070 detailed levels and all 585 major-group levels agree with the downloaded official workbook over the frozen period (maximum discrepancy below `1e-8`). The live source extends to August 2026; later observations are not used.
- Model the 13 separate major codes `01`–`13`. Exclude `0999` (all-items aggregate) and `12+13` (overlaps with 12 and 13). Detailed parent/child series are not stacked as independent training examples. All-items CPI is displayed for context.
- The workbook's 112-row regional commodity-price snapshot and August 2023/2024 comparison are contextual sources, not monthly panels. They are not joined to predictors or labels. No regional or external-economy forecasting performance is claimed.

See the [source inventory](../data/processed/source_inventory.csv) and [provenance manifest](../data/processed/provenance.json).

## Spike definition

The primary label is **1 when a group's monthly index rises by at least 10%; 0 otherwise**. It captures upward spikes only; sharp declines remain class 0. Missing changes never become class 0.

Ten percent is an explicitly chosen, interpretable large one-month increase. It is **not an official PCBS threshold**, an estimated tail percentile, or a claim of an optimal economic cutoff. A common threshold makes labels comparable across groups, although volatile groups have more positives. It and the model settings were fixed before computing test metrics.

Repeat the same pipeline at 5% and 20%. These are different target definitions, so do not select the threshold with the highest test F1. The prediction probability cutoff stays at 0.5; no test-set calibration or tuning is performed.

## Predictors and timing

For target month `t`, use group changes from `t-1` and earlier:

- Lags 1, 2 and 3 of monthly percentage change.
- Means and sample standard deviations over the preceding 3 and 6 complete months, shifted by one month.
- Calendar-month sine/cosine, known in advance.
- One-hot expenditure code.

Requiring six prior changes yields July 2023 as the first modeled month. Current-month index, change, label, year and contemporaneous other-group outcomes are excluded. No imputation follows the explicit warm-up exclusion.

Each test month uses observed earlier test-month outcomes for its lags. Model parameters and preprocessing remain frozen after February 2025. This is a sequence of conditional one-step forecasts, **not a 12-month forecast made in February 2025**. It assumes the preceding CPI is available at forecast time; real release delays and historical revisions are not modeled. Deployment would require release-date-aware backtesting.

## Chronological evaluation

| Segment | Target months | Months | Group-month rows |
|---|---|---:|---:|
| Training | July 2023–February 2025 | 20 | 260 |
| Final test | March 2025–February 2026 | 12 | 156 |

All groups in a month remain on the same side of the split. The final year covers a complete calendar cycle while retaining earlier data for fitting. At 10%, training has 30 positives and testing has 25.

Two earlier fixed holdouts—March–August 2024 and September 2024–February 2025—use expanding training windows and identical settings. They are descriptive robustness checks wholly inside the final training period, not a parameter-selection procedure. Their training windows are small (8 and 14 months).

## Models

1. **No spike:** always predict 0, as an accuracy sanity check.
2. **Persistence:** predict a spike if the preceding change met the same threshold.
3. **Logistic Regression:** train-only standardized numeric features, one-hot codes, L2 regularization (`C=1`), balanced class weights, `max_iter=2000`, seed 42.
4. **Random Forest:** same preprocessing, 300 trees, maximum depth 4, minimum leaf size 5, balanced class weights, seed 42. Fixed depth/leaf restrictions limit complexity relative to the small sample; settings are not optimized on the test set.

Balanced weights favor recall and can generate many false positives. Scores are not calibrated probabilities. Standardization is fitted inside the training pipeline; it is unnecessary for trees but retained for consistency.

**ARIMA/SARIMA is deferred.** There are only 26 training changes before the final test year, fewer than three annual cycles, with substantial regime changes and flat series. Seasonal fitting or broad order search would be fragile. A level-forecast benchmark also needs its own evaluation design. Persistence provides a directly comparable time-series baseline without implying ARIMA can never be useful here.

## Metrics and interpretation

Report positive-class precision, recall, F1, accuracy, and counts. Confusion matrices have actual classes on rows, predicted classes on columns: `[[TN, FP], [FN, TP]]`. With no predicted positives, precision/F1 are reported as 0 and predicted-positive counts remain visible. Metrics pool group-month rows equally; they are not expenditure-weighted welfare measures or all-items CPI accuracy.

Save all predictions and metrics by month/group. The notebook independently reconstructs primary metrics from predictions. Training coefficients and forest impurity importances are descriptive, not causal; correlated features and group dummies complicate interpretation.

F1 intervals use 1,000 bootstrap resamples of **whole test months**, seed 42. This retains within-month dependence but does not fully capture serial dependence or fitting uncertainty. With only 12 test months, these are descriptive intervals, not significance tests. Small F1 differences do not establish reliable model superiority.

## Limitations

- Groups share shocks; the panel has far fewer independent time observations than its row count suggests.
- Conflict-era disruption, changing coverage and regime shifts limit generalization. The original report flags telephone/basic-commodity collection; the workbook has no row-level sampling/imputation flags to quantify this limitation.
- Several series are flat for long periods; education has 35 unchanged adjacent monthly observations. Flat reported CPI does not establish stable availability, affordability or complete measurement.
- Class imbalance lets the no-spike rule score high accuracy while detecting nothing. Fitted models increase recall at a substantial false-alarm cost.
- Recomputing changes repairs extraction, not underlying source measurement.
- Later observations are deliberately excluded. These are frozen historical findings, not current forecasts.
- Results depend on the upward-spike definition and equal group weighting. No causal, operational or policy effectiveness is established.

## Reproducibility

The committed frozen CSV enables offline analysis. Raw files are optional for the extraction audit. Pinned direct requirements, a full environment snapshot, a data checksum, run manifest, seeds, integrity tests and an executed notebook accompany the code. See the root README for commands.
