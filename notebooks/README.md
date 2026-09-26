# Notebook workflow

The analysis notebooks will be developed in this order:

1. **01_data_overview.ipynb** — inspect sources, dates, groups, missing values, and basic distributions.
2. **02_exploratory_analysis.ipynb** — visualize CPI levels, monthly changes, volatility, and group differences.
3. **03_feature_engineering.ipynb** — create lagged changes, rolling means, rolling volatility, and the spike target.
4. **04_logistic_regression.ipynb** — fit and evaluate the interpretable baseline model.
5. **05_random_forest.ipynb** — fit and evaluate the nonlinear comparison model.
6. **06_time_series_benchmark.ipynb** — optional ARIMA/SARIMA benchmark.
7. **07_regional_context.ipynb** — use regional price snapshots and external CPI references only for contextual comparison.

Results should only be added after the notebooks are run on the documented source data.
