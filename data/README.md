# Data provenance and reuse

**Producer:** Palestinian Central Bureau of Statistics (PCBS). **Dataset:** State of Palestine – Consumer Price Index. **Geography:** Gaza Strip. **Frequency:** monthly. **Base year:** 2018 = 100.

- [Official PCBS dataset on HDX](https://data.humdata.org/dataset/0e06dbe6-8eeb-4b26-ba12-652520b44177)
- [Official workbook](https://data.humdata.org/dataset/0e06dbe6-8eeb-4b26-ba12-652520b44177/resource/4ea77774-3f0c-4b94-bda8-c2efb82d0394/download/consumer-price-index.xlsx)
- [PCBS February 2026 release](https://www.pcbs.gov.ps/portals/_pcbs/PressRelease/Press_En_CPI022026E.pdf): Gaza monthly growth of 37.92%, matching the extract after rounding.

## Frozen inputs

`processed/cpi_major_groups.csv` is a transformed PCBS subset extracted from the group's existing `Palestine_CPI_Project_Pack.xlsx`, retrieved on 26 September 2026. It retains December 2022–February 2026: 15 codes and 39 months. Publication-period changes start January 2023; December is the initial level.

The live workbook now extends to August 2026. All 585 major levels and 5,070 detailed levels over the original period were cross-checked against it. The analysis retains the original study period. [provenance.json](processed/provenance.json) records checksums and numerical agreement.

| Field | Meaning |
|---|---|
| `code` | Text PCBS code, including leading zeros |
| `group_en` | English source label; outer whitespace removed, original spellings retained |
| `date` | Reference month represented by its first day |
| `cpi_index` | Index, 2018 = 100 |
| `reported_pct_change` | Change as extracted in the original project pack |
| `pct_change` | Recalculated `100 * (current / previous - 1)`, percentage units rather than decimal fractions |

`processed/cpi_detailed_groups.csv` contains the same frozen period for 130 detailed codes (5,070 rows), with the same schema. It supports code-specific descriptive analysis only; its hierarchical rows are not independent training examples.

Missing values are empty cells, never zero-filled. December changes are intentionally missing. Fifteen February 2024 changes missing from the project-pack major table are recovered from observed levels; the original extracted changes remain separately visible. Detailed counts use codes, not repeated labels.

## Attribution and licensing

Current HDX metadata and the project-pack Metadata sheet identify the source license as **Creative Commons Attribution International (CC BY)** (`license_id: cc-by`; [license link supplied by HDX](http://www.opendefinition.org/licenses/cc-by)). This applies to the PCBS dataset and derived numerical subset.

When reusing data, credit **Palestinian Central Bureau of Statistics (PCBS), State of Palestine – Consumer Price Index**, link to the dataset, and identify transformations. No PCBS endorsement is implied.

Transformations: reshape to monthly rows in the original project pack; trim labels; retain text codes; recompute changes; derive features and spike labels. No separate license is assigned to the authors' code or academic report. Public accessibility alone is not a code license.

The private multi-source project pack, academic report, regional snapshot and literature are not republished. Only attributed PCBS numerical data and derived analysis are committed. `data/raw/` stays ignored by Git.

## Optional extraction audit

Place the original files in `data/raw/` and run from the repository root:

```bash
python -m scripts.prepare_data --pack data/raw/Palestine_CPI_Project_Pack.xlsx --official data/raw/consumer-price-index.xlsx
```

This writes the frozen CSV, inventory and manifest. Use the manifest's raw-file SHA-256 values to audit the exact published source; the live URL can change. Normal reproduction uses the committed CSV and needs no Drive access.
