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

Create the relationships and visuals described in `report_design.md`. Copy measures from `measures.dax` into the model.

## Report pages

Page designs are documented and reviewed one at a time in `report_design.md`. The first draft is the Executive Overview.

## Refresh

After source data or transformation rules change, rerun the workflow from the repository root:

```powershell
python -m commercepulse.prepare_data
python -m commercepulse.load_sqlite
python -m commercepulse.export_powerbi
```

Then refresh the imported CSV sources in Power BI Desktop. The `data/processed/` exports are local generated files and are not committed to Git.
