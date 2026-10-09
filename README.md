# E-commerce Analytics

A portfolio project exploring e-commerce sales and operations with **Python, SQL, and Power BI**.

**Status:** Initial project setup. Analyses and dashboard findings will be added only after the data has been inspected and validated.

## Business goal

Turn raw e-commerce data into reliable answers about sales performance, product categories, payments, delivery, and customer experience.

## Data source

The project will use the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

- The dataset is historical and anonymized; it does not represent today's market.
- Follow the dataset's access conditions and licence.
- Do not commit the downloaded raw CSV files. Keep them in `data/raw/`, which is ignored by Git.

## Planned stack

- **Python / pandas** for data inspection and transformation
- **SQL / SQLite** for storage and analytical queries
- **Power BI** for interactive reporting
- **pytest** for automated checks

## Questions to investigate

1. How do revenue and order volume change over time?
2. Which product categories and states contribute most to item revenue?
3. How do freight costs compare with item values?
4. Which payment methods are most common?
5. What share of delivered orders arrived by the estimated date?
6. How do delivery outcomes relate to customer review scores?
7. What share of identifiable customers placed more than one order?

## Metric safeguards

- Item revenue and freight will be reported separately.
- Orders will be counted distinctly, not by item rows.
- Payment totals will not be added to item and freight totals, avoiding double counting.
- On-time delivery will use delivered orders with valid delivery and estimated-delivery dates.
- Profit margin and stock availability will not be claimed because this dataset does not provide the required product-cost and inventory information.

The eligible order statuses and exclusions for each KPI will be defined after inspecting the source data and documented before publishing results.

## Project structure

```text
ecommerce-analytics/
├── data/
│   ├── raw/             # Downloaded source CSVs (not committed)
│   └── processed/       # Generated files (not committed by default)
├── docs/                # Data dictionary and business rules
├── notebooks/           # Exploratory analysis
├── reports/             # Generated inventory and dashboard screenshots
├── src/commercepulse/   # Reusable Python code
├── sql/                 # Database schema and analytical queries
├── powerbi/             # Power BI report and notes
├── tests/               # Automated tests
├── .gitignore
├── pyproject.toml
└── requirements.txt
```

## Setup

Use Python 3.10 or newer.

```bash
python -m venv .venv
```

Activate the environment, then install dependencies:

```powershell
# Windows PowerShell
.venv\Scripts\Activate.ps1
```

```bash
# macOS / Linux
source .venv/bin/activate
```

```bash
python -m pip install -r requirements.txt
```

Download the dataset from Kaggle and place its CSV files in `data/raw/`. From the repository root, run:

```bash
python -m commercepulse.inspect_data
```

The initial inspection script samples up to 1,000 rows per CSV and writes an inventory to `reports/data_inventory.csv`. The inventory is a first-look aid, not a full-data quality assessment.

Run tests with:

```bash
pytest
```

## Current roadmap

- [x] Create initial repository structure
- [ ] Download and inspect the source data
- [ ] Document data quality and business rules
- [ ] Build the Python cleaning pipeline
- [ ] Create SQL tables and analytical queries
- [ ] Build the Power BI report
- [ ] Add automated tests and reproducible setup instructions
- [ ] Publish screenshots and evidence-based findings

## About

This is an independent portfolio project based on public data. It is not commissioned by or affiliated with Olist.
