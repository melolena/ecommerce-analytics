# Data Preparation Workflow

## Run the workflow

From the repository root, activate the project environment and run:

```powershell
python -m commercepulse.prepare_data
```

The command reads the source CSV files from `data/raw/`, writes prepared tables with the same names to `data/processed/`, and writes a run summary to `reports/data_preparation_summary.csv`. It does not modify the raw source files. These local data and report outputs are ignored by Git.

## Current preparation rules

- Require all nine expected source files and the documented source columns.
- Keep identifier columns as strings so IDs are not treated as numbers.
- Keep Brazilian postal-code prefixes as five-character strings, preserving leading zeros.
- Parse timestamp columns as datetimes and numeric measure columns as numbers. Invalid non-empty values stop the run instead of being silently coerced.
- Preserve missing values. No product-category, review, or timestamp imputation is applied.
- Validate the observed unique keys and the order, customer, item, product, seller, payment, and review relationships.
- Remove exact duplicate rows from the geolocation table only. The current source has 261,831 exact duplicate geolocation rows; the distinct source rows are retained in the processed output.
- Keep all tables separate and preserve their row-level grains. No order-status filter, aggregation, category translation, or KPI eligibility rule is applied.

## Latest run

The initial run processed the nine source files. It retained all rows except exact duplicate geolocation records, producing 738,332 geolocation rows from 1,000,163 source rows. The summary CSV records source rows, processed rows, duplicate removals, missing-cell counts, and column counts for each table.

## Next refinements

- Add transformation and validation tests.
- Document explicit metric rules before creating KPI-ready tables.
- Add any category or status normalization only after its business rule is agreed.
