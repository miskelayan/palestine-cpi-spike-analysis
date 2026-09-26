# Palestine CPI Spike Analysis

Analyzing unusual Consumer Price Index (CPI) spikes in the Gaza Strip using official Palestinian CPI data.

## Project overview

This project studies monthly CPI behavior in Gaza with an emphasis on identifying unusually large price increases rather than only modeling the overall CPI level.

The work combines economic data analysis, time-series feature engineering, and machine-learning classification. The planned baseline is Logistic Regression, followed by Random Forest as a nonlinear comparison model. ARIMA/SARIMA may be added as a traditional time-series benchmark.

## Data

**Primary source:** Palestinian Central Bureau of Statistics (PCBS)  
**Reference period:** January 2023 to February 2026  
**Base year:** 2018 = 100  
**Update frequency:** Monthly

The consolidated project workbook also contains cleaned major-group and detailed-division CPI tables, source metadata, a regional price snapshot, and an August 2023 vs August 2024 comparison table.

See [data/README.md](data/README.md) for source and licensing details.

## Repository structure

```text
palestine-cpi-spike-analysis/
├── data/
│   └── README.md
├── docs/
│   └── methodology.md
├── notebooks/
│   └── README.md
├── src/
│   ├── __init__.py
│   ├── data_loader.py
│   ├── features.py
│   └── models.py
├── .gitignore
├── README.md
└── requirements.txt
```

## Current implementation

The repository now includes reusable code for:

- downloading the official CPI workbook;
- inspecting Excel sheet names;
- reading the cleaned long-format CPI sheets from the consolidated project workbook;
- creating lagged and rolling time-series features without using future observations;
- defining a configurable binary CPI-spike target;
- performing chronological train/test splits;
- building Logistic Regression and Random Forest classification pipelines;
- producing classification metrics and a confusion matrix.

Empirical results are intentionally not reported yet. They should only be added after the analysis notebooks are run and the spike threshold is justified.

## Planned analysis

1. Inspect and validate the CPI data.
2. Explore CPI levels, monthly percentage changes, and volatility by expenditure group.
3. Define and justify a CPI-spike threshold.
4. Create lagged and rolling predictors.
5. Fit a Logistic Regression baseline.
6. Fit a Random Forest comparison model.
7. Evaluate using accuracy, precision, recall, F1-score, and a confusion matrix.
8. Optionally compare against an ARIMA/SARIMA benchmark.
9. Use regional price data and external CPI series only for contextual comparison.

## Setup

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

On Windows:

```bash
.venv\Scripts\activate
pip install -r requirements.txt
```

## Academic context

This project originated as a university **Data Analytics for Business** group project.

Original group members:

- Misk Elayan
- Asil Khalil
- Sandra Shwamreh

This repository is Misk Elayan's organized implementation and continued development of the project for learning and portfolio purposes.

## Data attribution

The CPI source data is published by the Palestinian Central Bureau of Statistics (PCBS). Source licensing and download information are documented in [data/README.md](data/README.md).

No separate license has been assigned to the project code at this stage.
