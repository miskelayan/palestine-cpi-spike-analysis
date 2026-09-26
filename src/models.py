"""Model-building helpers for CPI spike classification."""

from __future__ import annotations

from collections.abc import Sequence

import pandas as pd
from sklearn.compose import ColumnTransformer
from sklearn.ensemble import RandomForestClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import classification_report, confusion_matrix
from sklearn.pipeline import Pipeline
from sklearn.preprocessing import OneHotEncoder, StandardScaler


def time_based_split(
    frame: pd.DataFrame,
    test_start: str,
    date_col: str = "date",
) -> tuple[pd.DataFrame, pd.DataFrame]:
    """Split observations chronologically to reduce look-ahead bias."""
    result = frame.copy()
    result[date_col] = pd.to_datetime(result[date_col], errors="coerce")
    cutoff = pd.Timestamp(test_start)

    train = result[result[date_col] < cutoff].copy()
    test = result[result[date_col] >= cutoff].copy()

    if train.empty or test.empty:
        raise ValueError("The selected cutoff must leave observations in both sets.")

    return train, test


def _preprocessor(
    numeric_features: Sequence[str],
    categorical_features: Sequence[str],
) -> ColumnTransformer:
    return ColumnTransformer(
        transformers=[
            ("numeric", StandardScaler(), list(numeric_features)),
            (
                "categorical",
                OneHotEncoder(handle_unknown="ignore"),
                list(categorical_features),
            ),
        ]
    )


def build_logistic_regression(
    numeric_features: Sequence[str],
    categorical_features: Sequence[str] = ("group_en",),
    random_state: int = 42,
) -> Pipeline:
    """Create the interpretable baseline classifier described in the project plan."""
    return Pipeline(
        steps=[
            ("preprocess", _preprocessor(numeric_features, categorical_features)),
            (
                "model",
                LogisticRegression(
                    max_iter=2000,
                    class_weight="balanced",
                    random_state=random_state,
                ),
            ),
        ]
    )


def build_random_forest(
    numeric_features: Sequence[str],
    categorical_features: Sequence[str] = ("group_en",),
    random_state: int = 42,
) -> Pipeline:
    """Create the nonlinear comparison model described in the project plan."""
    return Pipeline(
        steps=[
            ("preprocess", _preprocessor(numeric_features, categorical_features)),
            (
                "model",
                RandomForestClassifier(
                    n_estimators=500,
                    class_weight="balanced",
                    random_state=random_state,
                ),
            ),
        ]
    )


def evaluate_classifier(model: Pipeline, x_test, y_test) -> dict:
    """Return standard classification metrics and the confusion matrix."""
    predictions = model.predict(x_test)
    return {
        "classification_report": classification_report(
            y_test,
            predictions,
            output_dict=True,
            zero_division=0,
        ),
        "confusion_matrix": confusion_matrix(y_test, predictions).tolist(),
    }
