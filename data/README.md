# Data

This project uses official Palestinian Consumer Price Index (CPI) data published by the Palestinian Central Bureau of Statistics (PCBS).

## Primary dataset

**Dataset:** State of Palestine - Consumer Price Index  
**Source:** Palestinian Central Bureau of Statistics (PCBS)  
**Reference period:** January 2023 to February 2026  
**Base year:** 2018 = 100  
**Update frequency:** Monthly

Official dataset page:

https://data.humdata.org/dataset/0e06dbe6-8eeb-4b26-ba12-652520b44177

Direct CPI workbook:

https://data.humdata.org/dataset/0e06dbe6-8eeb-4b26-ba12-652520b44177/resource/4ea77774-3f0c-4b94-bda8-c2efb82d0394/download/consumer-price-index.xlsx

## Consolidated project workbook

The local project pack organizes the original project sources into analysis-ready sheets:

- `CPI_MajorGroups_Long` — monthly CPI for 15 major expenditure groups.
- `CPI_Divisions_Long` — detailed CPI divisions/groups.
- `Regional_Prices_Clean` — selected commodity prices across regions; this is a snapshot, not a monthly panel.
- `Aug2023_vs_Aug2024` — contextual comparison by major expenditure group.
- `Metadata` — source metadata.
- `Source_Inventory` — mapping of the original uploaded files.

The consolidated workbook is not committed here as a raw binary file. The code can read a local copy when it is available.

## License

The primary CPI source dataset is distributed under the **Creative Commons Attribution International (CC BY)** license.

## Repository data policy

Raw source files should remain traceable to the official provider.

Recommended local layout:

```text
data/
├── raw/
│   ├── consumer-price-index.xlsx
│   └── Palestine_CPI_Project_Pack.xlsx
└── processed/
```

The `data/raw` and `data/processed` contents are ignored by Git so local working files are not accidentally committed. Processed datasets can be added later if they are documented, reproducible, and appropriate to redistribute.
