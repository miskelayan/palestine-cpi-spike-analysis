"""Reproducible, one-month-ahead CPI spike classification.

Outputs are computed from the frozen PCBS subset, never hand-entered metrics.
"""
from pathlib import Path
import hashlib
import json
import platform
from importlib.metadata import version

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix

from .features import add_time_series_features, add_spike_target
from .models import build_logistic_regression, time_based_split

TEST_START = "2025-03-01"
PRIMARY_THRESHOLD = 10.0
THRESHOLDS = (5.0, 10.0, 20.0)
NUMERIC = ["pct_change_lag_1", "pct_change_lag_2", "pct_change_lag_3",
           "pct_change_rolling_mean_3", "pct_change_rolling_std_3",
           "pct_change_rolling_mean_6", "pct_change_rolling_std_6", "month_sin", "month_cos"]
FEATURES = NUMERIC + ["code"]
MODEL_NAMES = ["No spike", "Persistence", "Logistic Regression"]


def read_data(root):
    path = root / "data/processed/cpi_major_groups.csv"
    provenance = json.loads((root / "data/processed/provenance.json").read_text())
    if hashlib.sha256(path.read_bytes()).hexdigest() != provenance["processed_sha256"]:
        raise ValueError("Frozen CSV checksum does not match provenance.json")
    frame = pd.read_csv(path, dtype={"code": str}, parse_dates=["date"])
    if frame.duplicated(["code", "date"]).any() or frame.cpi_index.isna().any() or (frame.cpi_index <= 0).any():
        raise ValueError("Invalid group-month keys or CPI levels")
    recomputed = frame.sort_values(["code", "date"]).groupby("code").cpi_index.pct_change(fill_method=None) * 100
    if not np.allclose(recomputed, frame.sort_values(["code", "date"])["pct_change"], equal_nan=True, atol=1e-7):
        raise ValueError("Percentage changes do not reconcile with index levels")
    return frame


def model_frame(frame):
    # Exclude aggregate CPI and overlapping legacy aggregate 12+13.
    selected = frame[frame.code.isin([f"{i:02d}" for i in range(1, 14)])].copy()
    if selected.code.nunique() != 13:
        raise ValueError("Expected the 13 non-overlapping major expenditure codes")
    enriched = add_time_series_features(selected)
    enriched["month_sin"] = np.sin(2 * np.pi * enriched.month / 12)
    enriched["month_cos"] = np.cos(2 * np.pi * enriched.month / 12)
    return enriched.dropna(subset=NUMERIC + ["pct_change"]).sort_values(["date", "code"]).reset_index(drop=True)


def metrics(y, pred):
    tn, fp, fn, tp = confusion_matrix(y, pred, labels=[0, 1]).ravel()
    return {"n": len(y), "actual_spikes": int(np.sum(y)), "predicted_spikes": int(np.sum(pred)),
            "accuracy": accuracy_score(y, pred), "precision": precision_score(y, pred, zero_division=0),
            "recall": recall_score(y, pred, zero_division=0), "f1": f1_score(y, pred, zero_division=0),
            "tn": int(tn), "fp": int(fp), "fn": int(fn), "tp": int(tp)}


def fit_evaluate(frame, threshold, cutoff, end=None):
    labeled = add_spike_target(frame, threshold)
    if end:
        labeled = labeled[labeled.date < pd.Timestamp(end)]
    train, test = time_based_split(labeled, cutoff)
    y = train.is_spike.astype(int)
    if y.nunique() != 2:
        raise ValueError("Training requires both spike classes")
    fitted = {
        "Logistic Regression": build_logistic_regression(NUMERIC, ("code",)),
    }
    results, predictions = [], []
    for name in MODEL_NAMES:
        if name == "No spike":
            probabilities = np.zeros(len(test))
        elif name == "Persistence":
            probabilities = (test.pct_change_lag_1 >= threshold).astype(float).to_numpy()
        else:
            fitted[name].fit(train[FEATURES], y)
            probabilities = fitted[name].predict_proba(test[FEATURES])[:, 1]
        pred = (probabilities >= 0.5).astype(int)
        results.append({"threshold_pct": threshold, "model": name, "train_rows": len(train),
                        "train_spikes": int(y.sum()), **metrics(test.is_spike.astype(int), pred)})
        prediction = test[["date", "code", "group_en", "pct_change", "is_spike"]].copy()
        prediction["model"] = name
        prediction["threshold_pct"] = threshold
        prediction["probability"] = probabilities
        prediction["prediction"] = pred
        predictions.append(prediction)
    return pd.DataFrame(results), pd.concat(predictions, ignore_index=True), fitted


def save_plot(fig, path):
    fig.savefig(path, dpi=150, bbox_inches="tight", metadata={"Software": "Matplotlib"})
    plt.close(fig)


def run(root=None):
    root = Path(root or Path(__file__).resolve().parents[1])
    tables, figures = root / "reports/tables", root / "reports/figures"
    tables.mkdir(parents=True, exist_ok=True)
    figures.mkdir(parents=True, exist_ok=True)
    frame = read_data(root)
    detailed_path = root / "data/processed/cpi_detailed_groups.csv"
    provenance = json.loads((root / "data/processed/provenance.json").read_text())
    if hashlib.sha256(detailed_path.read_bytes()).hexdigest() != provenance["detailed_processed_sha256"]:
        raise ValueError("Detailed CSV checksum does not match provenance.json")
    detailed = pd.read_csv(detailed_path, dtype={"code": str}, parse_dates=["date"])
    detailed_summary = detailed.groupby(["code", "group_en"]).agg(
        months=("date", "size"), mean_monthly_change=("pct_change", "mean"),
        sd_monthly_change=("pct_change", "std"), max_monthly_change=("pct_change", "max"))
    detailed_summary.sort_values("sd_monthly_change", ascending=False).to_csv(
        tables / "detailed_group_overview.csv", float_format="%.8f")
    panel = model_frame(frame)
    train, test = time_based_split(panel, TEST_START)
    summary = {"raw_rows": len(frame), "raw_codes": int(frame.code.nunique()),
               "raw_months": int(frame.date.nunique()), "modeled_codes": 13,
               "train_rows": len(train), "test_rows": len(test),
               "train_start": str(train.date.min().date()), "train_end": str(train.date.max().date()),
               "test_start": str(test.date.min().date()), "test_end": str(test.date.max().date()),
               "train_months": int(train.date.nunique()), "test_months": int(test.date.nunique()),
               "threshold_pct": PRIMARY_THRESHOLD, "probability_cutoff": 0.5,
               "seed": 42, "python": platform.python_version(),
               "packages": {p: version(p) for p in ["pandas", "numpy", "scikit-learn", "matplotlib", "openpyxl"]}}
    all_metrics, all_predictions = [], []
    for threshold in THRESHOLDS:
        scores, predictions, fitted = fit_evaluate(panel, threshold, TEST_START)
        all_metrics.append(scores)
        all_predictions.append(predictions)
        if threshold == PRIMARY_THRESHOLD:
            primary_fitted = fitted
    scores = pd.concat(all_metrics, ignore_index=True)
    predictions = pd.concat(all_predictions, ignore_index=True)
    primary = scores[scores.threshold_pct == PRIMARY_THRESHOLD]
    main_preds = predictions[predictions.threshold_pct == PRIMARY_THRESHOLD]
    scores.to_csv(tables / "threshold_sensitivity.csv", index=False, float_format="%.8f")
    primary.to_csv(tables / "metrics.csv", index=False, float_format="%.8f")
    predictions.to_csv(tables / "predictions.csv", index=False, date_format="%Y-%m-%d", float_format="%.10g")
    panel.to_csv(tables / "modeling_panel.csv", index=False, date_format="%Y-%m-%d", float_format="%.10g")
    # Two earlier fixed holdouts, wholly inside the final training period.
    validation = []
    for cutoff, end in [("2024-03-01", "2024-09-01"), ("2024-09-01", TEST_START)]:
        fold, _, _ = fit_evaluate(panel, PRIMARY_THRESHOLD, cutoff, end)
        fold["validation_start"], fold["validation_end_exclusive"] = cutoff, end
        validation.append(fold)
    pd.concat(validation).to_csv(tables / "temporal_validation.csv", index=False, float_format="%.8f")
    grouped = []
    for dimension in ["code", "date"]:
        for (model, value), group in main_preds.groupby(["model", dimension]):
            grouped.append({"dimension": dimension, "value": str(value), "model": model,
                            **metrics(group.is_spike.astype(int), group.prediction)})
    pd.DataFrame(grouped).to_csv(tables / "metrics_by_group_and_month.csv", index=False, float_format="%.8f")
    # Resample whole months to retain same-month cross-group dependence.
    rng = np.random.default_rng(42)
    dates = sorted(main_preds.date.unique())
    draws = rng.integers(0, len(dates), size=(1000, len(dates)))
    intervals = []
    for name, group in main_preds.groupby("model"):
        blocks = [group[group.date == date] for date in dates]
        f1s = []
        for draw in draws:
            sample = pd.concat([blocks[i] for i in draw])
            f1s.append(f1_score(sample.is_spike.astype(int), sample.prediction, zero_division=0))
        intervals.append({"model": name, "f1_p025": np.quantile(f1s, .025), "f1_p975": np.quantile(f1s, .975),
                          "resamples": 1000, "resampling_unit": "month"})
    pd.DataFrame(intervals).to_csv(tables / "f1_month_bootstrap.csv", index=False, float_format="%.8f")
    eda = frame.groupby(["code", "group_en"]).agg(months=("date", "size"),
            min_index=("cpi_index", "min"), max_index=("cpi_index", "max"),
            mean_monthly_change=("pct_change", "mean"), sd_monthly_change=("pct_change", "std"),
            unchanged_months=("pct_change", lambda x: int((x.abs() < 1e-10).sum())),
            spikes_10pct=("pct_change", lambda x: int((x >= PRIMARY_THRESHOLD).sum())))
    eda.to_csv(tables / "group_overview.csv", float_format="%.8f")
    frame.nlargest(15, "pct_change")[["date", "code", "group_en", "pct_change"]].to_csv(tables / "largest_increases.csv", index=False)
    names = primary_fitted["Logistic Regression"].named_steps["preprocess"].get_feature_names_out()
    pd.DataFrame({"feature": names, "standardized_logistic_coefficient": primary_fitted["Logistic Regression"].named_steps["model"].coef_[0]}).to_csv(tables / "model_parameters.csv", index=False)
    plt.rcParams.update({"font.size": 10, "axes.spines.top": False, "axes.spines.right": False, "axes.titleweight": "bold"})
    fig, axes = plt.subplots(2, 1, figsize=(11, 7), sharex=True)
    for code, label in [("0999", "All items"), ("01", "Food"), ("02", "Tobacco / alcohol / narcotics")]:
        group = frame[frame.code == code]
        axes[0].plot(group.date, group.cpi_index, label=label, linewidth=1.8)
    axes[0].set_yscale("log")
    axes[0].set_ylabel("CPI (2018 = 100), log scale")
    axes[0].set_title("Gaza CPI: large, uneven changes across expenditure groups")
    axes[0].legend(loc="upper left")
    aggregate = frame[frame.code == "0999"]
    axes[1].bar(aggregate.date, aggregate["pct_change"], width=22, color="#276879")
    axes[1].axhline(10, color="#ac4630", linestyle="--", label="10% reference")
    axes[1].set_ylabel("All-items monthly change (%)")
    axes[1].legend()
    for ax in axes:
        ax.axvspan(pd.Timestamp(TEST_START), frame.date.max()+pd.Timedelta(days=15), alpha=.1, color="#b9752f")
        ax.grid(axis="y", alpha=.2)
    fig.text(.5, .005, "Shading: held-out months (Mar 2025–Feb 2026). Source: PCBS; frozen project-pack data.", ha="center", fontsize=9)
    fig.tight_layout(rect=[0,.03,1,1])
    save_plot(fig, figures / "cpi_overview.png")
    heat = frame[frame.code.isin(panel.code.unique())].pivot(index="code", columns="date", values="pct_change")
    fig, ax = plt.subplots(figsize=(12, 5))
    im = ax.imshow(heat, cmap="RdBu_r", vmin=-40, vmax=40, aspect="auto")
    ax.set_yticks(range(len(heat)), heat.index)
    ax.set_xticks(range(0,len(heat.columns),3), [d.strftime("%b %Y") for d in heat.columns[::3]], rotation=45, ha="right")
    ax.set_ylabel("Expenditure code (see group overview table)")
    ax.set_title("Monthly CPI changes: common shocks and long flat series")
    fig.colorbar(im, ax=ax, label="Monthly change (%); colors clipped at ±40")
    fig.tight_layout()
    save_plot(fig, figures / "monthly_changes.png")
    fig, axes = plt.subplots(1,len(MODEL_NAMES),figsize=(10,3.7))
    for ax, (_, row) in zip(axes, primary.iterrows()):
        matrix = np.array([[row.tn,row.fp],[row.fn,row.tp]],dtype=int)
        ax.imshow(matrix,cmap="Blues",vmin=0,vmax=int(primary[["tn","fp","fn","tp"]].max().max()))
        for i in range(2):
            for j in range(2):
                ax.text(j,i,str(matrix[i,j]),ha="center",va="center",color="white" if matrix[i,j]>70 else "black",fontsize=14)
        ax.set_xticks([0,1],["No spike","Spike"])
        ax.set_yticks([0,1],["No spike","Spike"])
        ax.set_xlabel("Predicted")
        ax.set_ylabel("Actual")
        ax.set_title(row.model)
    fig.suptitle("Held-out confusion matrices · monthly increase ≥10%")
    fig.tight_layout()
    save_plot(fig, figures / "confusion_matrices.png")
    fig, ax = plt.subplots(figsize=(8,4.5))
    for name, group in scores.groupby("model",sort=False):
        ax.plot(group.threshold_pct,group.f1,marker="o",label=name)
    ax.set(xlabel="Spike threshold: monthly increase (%)",ylabel="Held-out F1",ylim=(0,1),xticks=THRESHOLDS,
           title="Threshold sensitivity (same chronology and model settings)")
    ax.legend()
    ax.grid(alpha=.2)
    fig.tight_layout()
    save_plot(fig, figures / "sensitivity.png")
    summary["aggregate_feb2026_change_pct"] = float(aggregate.loc[aggregate.date == "2026-02-01", "pct_change"].iloc[0])
    (root / "reports/run_manifest.json").write_text(json.dumps(summary,indent=2)+"\n")
    print(primary.to_string(index=False))
    return {"summary": summary, "metrics": primary, "sensitivity": scores, "overview": eda}


if __name__ == "__main__":
    run()
