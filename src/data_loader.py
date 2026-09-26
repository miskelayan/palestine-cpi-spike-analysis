"""Data access helpers for the Palestine CPI spike analysis project."""

from pathlib import Path
from typing import Iterable

import pandas as pd
import requests

OFFICIAL_CPI_URL = (
    "https://data.humdata.org/dataset/"
    "0e06dbe6-8eeb-4b26-ba12-652520b44177/resource/"
    "4ea77774-3f0c-4b94-bda8-c2efb82d0394/download/consumer-price-index.xlsx"
)

LONG_CPI_COLUMNS = {"code", "group_en", "date", "cpi_index", "pct_change"}


def download_official_cpi(
    destination: str | Path = "data/raw/consumer-price-index.xlsx",
    overwrite: bool = False,
) -> Path:
    """Download the official CPI workbook used by the project."""
    destination = Path(destination)
    destination.parent.mkdir(parents=True, exist_ok=True)

    if destination.exists() and not overwrite:
        return destination

    response = requests.get(OFFICIAL_CPI_URL, timeout=60)
    response.raise_for_status()
    destination.write_bytes(response.content)
    return destination


def list_excel_sheets(file_path: str | Path) -> list[str]:
    """Return all worksheet names in an Excel workbook."""
    return pd.ExcelFile(file_path).sheet_names


def _find_header_row(
    raw_frame: pd.DataFrame,
    required_columns: Iterable[str] = LONG_CPI_COLUMNS,
) -> int:
    """Find the row containing the expected long-format CPI column names."""
    required = {str(column).strip().lower() for column in required_columns}

    for row_index, row in raw_frame.iterrows():
        values = {
            str(value).strip().lower()
            for value in row.tolist()
            if pd.notna(value)
        }
        if required.issubset(values):
            return int(row_index)

    raise ValueError(
        "Could not locate the expected CPI header row. "
        f"Expected columns: {sorted(required)}"
    )


def read_project_pack_sheet(
    file_path: str | Path,
    sheet_name: str,
) -> pd.DataFrame:
    """
    Read one cleaned long-format CPI sheet from the consolidated project workbook.

    The project pack contains descriptive rows before the real table header, so
    the header is detected automatically instead of assuming a fixed row number.
    """
    raw = pd.read_excel(file_path, sheet_name=sheet_name, header=None)
    header_row = _find_header_row(raw)

    frame = pd.read_excel(
        file_path,
        sheet_name=sheet_name,
        header=header_row,
        dtype={"code": str},
    )

    frame = frame.dropna(how="all")
    frame.columns = [str(column).strip() for column in frame.columns]
    frame["code"] = frame["code"].str.strip()
    frame["group_en"] = frame["group_en"].str.strip()

    missing = LONG_CPI_COLUMNS.difference(frame.columns)
    if missing:
        raise ValueError(
            f"Sheet '{sheet_name}' is missing expected columns: {sorted(missing)}"
        )

    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["cpi_index"] = pd.to_numeric(frame["cpi_index"], errors="coerce")
    frame["pct_change"] = pd.to_numeric(frame["pct_change"], errors="coerce")

    return frame.sort_values(["group_en", "date"]).reset_index(drop=True)


def load_major_groups(file_path: str | Path) -> pd.DataFrame:
    """Load the analysis-ready major expenditure groups table."""
    return read_project_pack_sheet(file_path, "CPI_MajorGroups_Long")


def load_detailed_groups(file_path: str | Path) -> pd.DataFrame:
    """Load the richer detailed divisions/groups table."""
    return read_project_pack_sheet(file_path, "CPI_Divisions_Long")
