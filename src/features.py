"""Feature engineering utilities for CPI spike classification."""

from collections.abc import Iterable

import pandas as pd

REQUIRED_COLUMNS = {"group_en", "date", "pct_change"}


def validate_cpi_frame(frame: pd.DataFrame) -> None:
    """Validate the minimum columns required for time-series feature engineering."""
    missing = REQUIRED_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(f"Missing required columns: {sorted(missing)}")


def add_time_series_features(
    frame: pd.DataFrame,
    lags: Iterable[int] = (1, 2, 3),
    rolling_windows: Iterable[int] = (3, 6),
    group_col: str = "code",
    date_col: str = "date",
    change_col: str = "pct_change",
) -> pd.DataFrame:
    """
    Add lagged percentage-change and rolling features without using future values.

    Rolling statistics are shifted by one month before calculation so the
    current month's change is not leaked into its own predictors.
    """
    validate_cpi_frame(frame)

    result = frame.copy()
    result[date_col] = pd.to_datetime(result[date_col], errors="coerce")
    result[change_col] = pd.to_numeric(result[change_col], errors="coerce")
    result = result.sort_values([group_col, date_col]).reset_index(drop=True)
    if result[date_col].isna().any() or result[group_col].isna().any():
        raise ValueError("Dates and group keys must not be missing.")
    if result.duplicated([group_col, date_col]).any():
        raise ValueError("Duplicate group-month observations.")
    for _, series in result.groupby(group_col)[date_col]:
        expected = pd.date_range(series.min(), series.max(), freq="MS")
        if list(series) != list(expected):
            raise ValueError("Each group must have a complete monthly calendar.")

    grouped = result.groupby(group_col, sort=False)[change_col]

    for lag in lags:
        if lag < 1:
            raise ValueError("Lag values must be positive integers.")
        result[f"{change_col}_lag_{lag}"] = grouped.shift(lag)

    for window in rolling_windows:
        if window < 2:
            raise ValueError("Rolling windows must be at least 2.")
        result[f"{change_col}_rolling_mean_{window}"] = (
            result.groupby(group_col, sort=False)[change_col]
            .transform(lambda series: series.shift(1).rolling(window, min_periods=window).mean())
        )
        result[f"{change_col}_rolling_std_{window}"] = (
            result.groupby(group_col, sort=False)[change_col]
            .transform(lambda series: series.shift(1).rolling(window, min_periods=window).std())
        )

    result["month"] = result[date_col].dt.month
    result["year"] = result[date_col].dt.year

    return result


def add_spike_target(
    frame: pd.DataFrame,
    threshold: float,
    change_col: str = "pct_change",
    target_col: str = "is_spike",
) -> pd.DataFrame:
    """
    Create a binary spike target using an explicitly chosen percentage threshold.

    The threshold is intentionally supplied by the analyst. It should be
    justified in the methodology rather than selected after inspecting test
    performance.
    """
    if threshold <= 0:
        raise ValueError("The spike threshold must be positive.")

    result = frame.copy()
    result[change_col] = pd.to_numeric(result[change_col], errors="coerce")
    result[target_col] = (result[change_col] >= threshold).astype("Int64")
    result.loc[result[change_col].isna(), target_col] = pd.NA
    return result


def complete_cases(
    frame: pd.DataFrame,
    columns: Iterable[str],
) -> pd.DataFrame:
    """Return rows with non-missing values for all requested modeling columns."""
    columns = list(columns)
    return frame.dropna(subset=columns).copy()
