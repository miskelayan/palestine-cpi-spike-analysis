# Methodology

## Research question

Can recent CPI behavior and expenditure-group information help identify unusually large monthly CPI increases in the Gaza Strip?

The project focuses on **spike detection**, not merely forecasting the CPI level.

## Data

The primary time series is official Palestinian Consumer Price Index data published by the Palestinian Central Bureau of Statistics (PCBS). The consolidated project workbook contains:

- **CPI_MajorGroups_Long** — 15 major expenditure groups, suitable for the first model.
- **CPI_Divisions_Long** — a richer table of detailed CPI divisions/groups.
- **Regional_Prices_Clean** — a cross-sectional regional price snapshot for selected commodities.
- **Aug2023_vs_Aug2024** — a contextual comparison table.
- **Metadata** and **Source_Inventory** — source and licensing documentation.

The regional-price files are supporting context and are not treated as a monthly training panel.

## Target definition

The classification target is a binary variable indicating whether a monthly CPI percentage change is large enough to count as a **spike**.

The repository intentionally does **not** hard-code one final economic threshold. The threshold should be selected and justified before final model evaluation. Sensitivity analysis across plausible thresholds is recommended.

## Features

Candidate predictors include:

- expenditure-group identity;
- prior monthly CPI percentage changes;
- short-term lagged changes;
- rolling mean of prior changes;
- rolling volatility of prior changes;
- calendar month and year.

Rolling features use only earlier observations. The current month's percentage change is shifted out before rolling statistics are calculated to reduce target leakage.

## Models

### Logistic Regression

Logistic Regression is the baseline because it is comparatively interpretable and appropriate for a binary target.

### Random Forest

Random Forest is the nonlinear comparison model and can capture interactions that the baseline may miss.

### Optional time-series benchmark

ARIMA or SARIMA may be added as a traditional benchmark. It should be evaluated separately from the classification models because it answers a slightly different forecasting question.

## Validation

A random train/test split is not the preferred default for this project because the observations are ordered in time. The codebase therefore includes a chronological split helper.

Evaluation should report:

- accuracy;
- precision;
- recall;
- F1-score;
- confusion matrix.

Because the main task is detecting relatively unusual events, precision and recall should receive more attention than accuracy alone.

## Limitations

- The time series is short.
- Gaza CPI behavior during the study period is exceptionally volatile and may not represent a stable long-run data-generating process.
- Data-collection conditions and coverage may vary during the period.
- Some CPI group series contain extended periods with unchanged reported values.
- Regional item-price data is a snapshot rather than a monthly panel.
- The project is intended as an applied academic analysis, not as a production forecasting system or policy forecast.

## Reproducibility

Raw source files should remain traceable to the official provider. Code, methodology, and any processed data added to this repository should preserve clear source attribution.
