# E-commerce Analytics

An independent portfolio project exploring e-commerce sales and operations with **Python, SQL, and Power BI**.

**Status:** Initial setup. Data exploration, metrics, and dashboard findings will be added after they have been implemented and validated.

## Business objective

Transform raw e-commerce data into reliable insights that help answer questions about sales performance, product categories, payments, delivery, and customer experience.

## Dataset

This project uses the [Brazilian E-Commerce Public Dataset by Olist](https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce).

- The records are historical and anonymized; they should not be treated as a representation of today's market.
- Access and use must follow the dataset's licence and source-platform terms.
- Raw data files will be kept locally and will not be committed to this repository by default.

## Questions to explore

- How do order volume and sales value change over time?
- Which product categories and states contribute the most to item revenue?
- How does freight value compare with item revenue?
- Which payment methods are most commonly used?
- What share of eligible delivered orders arrived by the estimated delivery date?
- How are delivery outcomes related to customer review scores?
- What share of identifiable customers placed more than one order during the observed period?

## Planned technology stack

- Python and pandas: data inspection, cleaning, and transformation
- SQL and SQLite: structured storage, queries, and reconciliation checks
- Power BI: interactive reports and visual analysis
- pytest: automated tests for data transformations and metric logic

## Planned deliverables

1. A documented data preparation workflow.
2. A relational analytical model with clearly defined table granularity.
3. SQL queries and checks to validate key totals.
4. An interactive Power BI report.
5. Automated tests, screenshots, metric definitions, and setup instructions.

## KPI principles

Metric definitions and order-status rules will be documented before results are published.

- Item revenue and freight will be reported separately.
- Orders will be counted by distinct order ID, not by item rows.
- Payment values will not be added to item and freight totals, which could double-count value.
- The on-time delivery rate will use delivered orders with valid delivery and estimated-delivery dates.
- Profit margin and inventory availability will not be reported unless suitable cost and stock data are available.

## Repository structure

```text
ecommerce-analytics/
├── data/                 # Raw and processed data (local files are not committed)
├── docs/                 # Data dictionary and business rules
├── notebooks/            # Exploratory analysis
├── powerbi/              # Power BI report notes and files
├── reports/              # Generated inventories and report evidence
├── src/commercepulse/    # Reusable Python code
├── sql/                  # SQL model and analytical queries
├── tests/                # Automated tests
├── pyproject.toml
└── requirements.txt
```

## Setup

Use Python 3.10 or newer. From the repository root, create and activate a virtual environment, then install the dependencies:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
python -m pip install -e .
```

Download the Olist dataset and place its CSV files in `data/raw/`. Generate an initial inventory with:

```powershell
python -m commercepulse.inspect_data
```

The inventory samples up to 1,000 rows per CSV and is saved to `reports/data_inventory.csv`. It is a first-look aid, not a full data-quality assessment.

Prepare the source tables and load them into the local SQLite staging model:

```powershell
python -m commercepulse.prepare_data
python -m commercepulse.load_sqlite
```

Prepared CSVs and the database are written to `data/processed/`; run summaries are saved to `reports/`.

## Repository roadmap

- [x] Download and inspect the source dataset
- [x] Document initial data quality findings and business rules
- [x] Build and validate the initial Python data preparation workflow
- [x] Create the initial SQLite staging model and load prepared tables
- [x] Define initial sales/review rules and add core analytics queries
- [x] Record initial analysis results
- [x] Define and calculate repeat-customer rate; document timestamp handling
- [ ] Build the Power BI report
- [ ] Add automated tests and reproducible setup instructions
- [ ] Publish screenshots and evidence-based findings

## About this project

This is an independent learning and portfolio project based on public data. It is not commissioned by or affiliated with Olist. All findings will be documented after they have been produced and validated.
