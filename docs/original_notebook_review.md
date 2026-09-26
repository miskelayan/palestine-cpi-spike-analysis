# Relationship to the original analysis notebook

The user supplied `Copy_of_gaza_cpi_final.ipynb` during completion of this repository. It credits **Misk Elayan, Asil Khalil and Sandra Shwamreh** and contains 49 cells, including stored descriptive outputs. It was inspected as an original project artifact; stored outputs were not treated as newly executed evidence.

Source SHA-256: `ba83e5625c3427278bb8ee84e78ad64b32e76ba67ccce132a936888fcfe168f9`.

## What carries forward

The original notebook examines both official CPI sheets, overall Gaza CPI, major-group volatility, detailed divisions and a cross-sectional regional price file. The completed analysis retains its descriptive questions, source coverage and group attribution. It adds reproducible forward-looking spike classification matching the original project report. Detailed-series summaries are recalculated by **code** and kept separate from pooled model training. The regional snapshot remains contextual.

## Methodological corrections

| Original notebook location (1-based cell) | Observation | Treatment in the completed analysis |
|---|---|---|
| 9, helper function | Groups percentage changes by English name; detailed data has 130 codes but only 124 distinct names | Group by string code; reject duplicate code-months and gaps |
| 9 and 11, major-sheet parser | Looks for the percent sign on the preceding header row; stored major `pct_change` values are all missing | Use the validated project-pack levels and recompute adjacent monthly changes; preserve reported changes separately |
| 9, spike definition | Uses the full-series 90th percentile, including future test outcomes | Use a predeclared 10% threshold with 5%/20% sensitivity; no full-sample target calibration |
| 9, missing values | `np.where` turns missing initial changes into non-spikes | Preserve missing labels and exclude incomplete warm-up observations |
| 9 and 44, rolling/current features | Current inflation and an unshifted rolling index contain information from the contemporaneous index target | Use only past changes and shifted rolling windows for next-month spike prediction |
| 15 and 44, combination/filtering | Stacks overlapping aggregates/details; dropping missing major changes can silently remove the major table from regression | Fit 13 separate major expenditure codes; use detailed series descriptively |
| 44, code conversion | Numeric conversion loses leading zeros and drops hierarchical nonnumeric codes | Keep identifiers as text; encode categorically |
| 44, evaluation | Fits Linear Regression and predicts on the same rows | Chronological held-out classification with Logistic Regression, Random Forest and naive baselines |
| 36 and 42, regional means | Averages heterogeneous item/package prices and item-specific regional weights | Do not interpret these means as a cost-of-living index or official regional CPI weights |
| 38, price gaps | Treats zero Gaza entries as ordinary prices | Do not infer free goods or price discounts without source clarification of zero/availability codes |

The original stored R² is an **in-sample fit statistic for a different target (CPI level)**. It is not comparable to held-out spike-classification accuracy/F1 and is not reused as a forecasting claim. The source notebook's full-sample spike thresholds are not reused either.

This review does not assert that every descriptive plot is invalid. It distinguishes useful exploratory work from evidence of predictive performance. The original file is preserved at its user-supplied location; the repository publishes the corrected, executed analysis instead of duplicating interactive Colab upload/download cells or stale model outputs.
