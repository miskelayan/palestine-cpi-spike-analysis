"""Extract a frozen public CPI subset from the original project pack.

Run from the repository root. Raw personal files are never copied to outputs.
"""
import argparse
import hashlib
import json
import re
from datetime import datetime
from pathlib import Path

import pandas as pd

from src.data_loader import load_major_groups, load_detailed_groups


def sha256(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()


def prepare(pack, official=None):
    out = Path("data/processed")
    out.mkdir(parents=True, exist_ok=True)
    frames = {"major": load_major_groups(pack), "detailed": load_detailed_groups(pack)}
    inventory = []
    for name, frame in frames.items():
        if frame.duplicated(["code", "date"]).any():
            raise ValueError(f"Duplicate keys in {name}")
        if frame[["code", "date", "cpi_index"]].isna().any().any():
            raise ValueError(f"Missing CPI keys/levels in {name}")
        if (frame.cpi_index <= 0).any():
            raise ValueError("Nonpositive CPI index")
        if frame.date.min() != pd.Timestamp("2022-12-01") or frame.date.max() != pd.Timestamp("2026-02-01"):
            raise ValueError("Expected the original December 2022–February 2026 project-pack period")
        for code, group in frame.groupby("code"):
            if list(group.date) != list(pd.date_range(group.date.min(), group.date.max(), freq="MS")):
                raise ValueError(f"Missing month for {code}")
        frame = frame.sort_values(["code", "date"])
        frame = frame.rename(columns={"pct_change": "reported_pct_change"})
        frame["pct_change"] = frame.groupby("code").cpi_index.pct_change(fill_method=None) * 100
        observed = frame.reported_pct_change.notna() & frame["pct_change"].notna()
        error = (frame.loc[observed, "reported_pct_change"] - frame.loc[observed, "pct_change"]).abs()
        inventory.append({"sheet": name, "rows": len(frame), "codes": frame.code.nunique(),
                          "unique_english_labels": frame.group_en.nunique(),
                          "start": str(frame.date.min().date()), "end": str(frame.date.max().date()),
                          "missing_levels": int(frame.cpi_index.isna().sum()),
                          "missing_reported_changes": int(frame.reported_pct_change.isna().sum()),
                          "recovered_changes": int((frame.reported_pct_change.isna() & frame["pct_change"].notna()).sum()),
                          "max_reported_change_difference_pp": float(error.max())})
        frames[name] = frame
    frames["major"].to_csv(out / "cpi_major_groups.csv", index=False, date_format="%Y-%m-%d", float_format="%.12g")
    frames["detailed"][["code", "group_en", "date", "cpi_index", "reported_pct_change", "pct_change"]].to_csv(
        out / "cpi_detailed_groups.csv", index=False, date_format="%Y-%m-%d", float_format="%.12g")
    # Detailed series are nested, so use them for validation only, not pooled training.
    pd.DataFrame(inventory).to_csv(out / "source_inventory.csv", index=False)
    manifest = {
        "project_pack_sha256": sha256(pack),
        "source": "Palestinian Central Bureau of Statistics (PCBS)",
        "dataset_url": "https://data.humdata.org/dataset/0e06dbe6-8eeb-4b26-ba12-652520b44177",
        "license": "Creative Commons Attribution International (CC BY), as stated in project-pack Metadata and HDX",
        "license_id": "cc-by",
        "license_url_as_supplied_by_hdx": "http://www.opendefinition.org/licenses/cc-by",
        "frozen_period": "2022-12-01 through 2026-02-01",
        "retrieved_on": "2026-09-26",
        "transformation": "Trim labels; preserve code strings; recompute monthly percent change from consecutive index levels without filling missing values.",
    }
    if official:
        raw = pd.read_excel(official, sheet_name=0, header=None)
        date_cols = [(i, pd.Timestamp(v)) for i, v in enumerate(raw.iloc[3]) if isinstance(v, datetime)]
        records = [{"code": str(row.iloc[0]).strip(), "date": date,
                    "official_index": pd.to_numeric(row.iloc[i], errors="coerce")}
                   for _, row in raw.iloc[4:].iterrows() if pd.notna(row.iloc[0])
                   for i, date in date_cols]
        reference = pd.DataFrame(records)
        comparison = frames["detailed"].merge(reference, on=["code", "date"], validate="one_to_one", how="left")
        if comparison.official_index.isna().any():
            raise ValueError("Official workbook is missing project-pack observations")
        comparison["abs_difference"] = (comparison.cpi_index - comparison.official_index).abs()
        if (comparison.abs_difference > 1e-8).any():
            raise ValueError("Official detailed history differs from the project pack; review source revisions")
        summary = {"matched_rows": len(comparison), "max_absolute_index_difference": float(comparison.abs_difference.max()),
                   "differences_over_1e_8": int((comparison.abs_difference > 1e-8).sum()),
                   "official_latest_month": str(reference.date.max().date()), "official_sha256": sha256(official)}
        manifest["official_comparison"] = summary
        raw_major = pd.read_excel(official, sheet_name=1, header=None)
        major_dates = [(i, pd.to_datetime(re.sub(r"[.\s]", "", v), format="%b%Y"))
                       for i, v in enumerate(raw_major.iloc[5]) if isinstance(v, str) and re.search(r"\d{4}", v)]
        major_reference = pd.DataFrame([
            {"code": str(row.iloc[0]).strip(), "date": date, "official_index": float(row.iloc[i])}
            for _, row in raw_major.iloc[6:].iterrows() if pd.notna(row.iloc[0]) for i, date in major_dates])
        common = frames["major"].merge(major_reference, on=["code", "date"], validate="one_to_one", how="left")
        if common.official_index.isna().any():
            raise ValueError("Official major-group comparison has missing matches")
        if ((common.cpi_index-common.official_index).abs() > 1e-8).any():
            raise ValueError("Official major-group history differs; review source revisions")
        manifest["major_official_overlap"] = {"rows": len(common), "codes": sorted(common.code.unique()),
                                              "max_absolute_index_difference": float((common.cpi_index-common.official_index).abs().max())}
    manifest["processed_sha256"] = sha256(out / "cpi_major_groups.csv")
    manifest["detailed_processed_sha256"] = sha256(out / "cpi_detailed_groups.csv")
    (out / "provenance.json").write_text(json.dumps(manifest, indent=2) + "\n")
    print(pd.DataFrame(inventory).to_string(index=False))
    print(json.dumps(manifest, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--pack", required=True)
    parser.add_argument("--official")
    args = parser.parse_args()
    prepare(args.pack, args.official)
