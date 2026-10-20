# Power BI

## Report-ready data

After building the SQLite database with `python -m commercepulse.load_sqlite`, export the reporting views with:

```powershell
python -m commercepulse.export_powerbi
```

The script writes five UTF-8 CSV files to `data/processed/powerbi/`. Import them into Power BI Desktop:

- `delivered_orders.csv` — one row per delivered order, with order-level revenue, delivery outcome, customer state, and average review score.
- `delivered_order_items.csv` — one row per delivered item, with product category, buyer/seller states, item price, and freight.
- `delivered_payments.csv` — one row per payment record, kept separate from sales values.
- `repeat_customer_summary.csv` — one full-period repeat-customer summary row.
- `delivery_review_summary.csv` — review averages by on-time/late delivery outcome.

The completed PBIX, measures, design notes, and screenshots of all three report pages are included in this directory. `report_design.md` documents the report layout and metric behavior; `measures.dax` records the measures used by the report.

## Report pages

The report contains the Executive Overview, Product Performance, and Delivery & Customer Experience pages. The report page tabs and canvas titles are documented in `report_design.md`.

## Refresh

After source data or transformation rules change, rerun the workflow from the repository root:

```powershell
python -m commercepulse.prepare_data
python -m commercepulse.load_sqlite
python -m commercepulse.export_powerbi
```

Then refresh the imported CSV sources in Power BI Desktop. The `data/processed/` exports are local generated files and are not committed to Git.
