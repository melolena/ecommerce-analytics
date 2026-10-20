# SQL

The initial SQLite model mirrors the prepared source tables at their original grain. Table creation is defined in `01_create_schema.sql`; `commercepulse.load_sqlite` loads the prepared CSVs into a local database.

From the repository root, after preparing the CSVs, run:

```powershell
python -m commercepulse.load_sqlite
```

The database is written to `data/processed/ecommerce_analytics.sqlite`. The loader creates a fresh temporary database, checks referential and SQLite integrity, and replaces the generated database only after a successful load.

The `stg_` tables preserve source table grains and do not apply order-status filters, KPI rules, or category translations. Review records use a generated `review_record_id` because the source `review_id` repeats.

See `docs/sql_model.md` for table grains, keys, relationships, and scope.

Query files:
- `02_reconciliation_queries.sql` reports source-grain row counts, order statuses, monthly order counts, totals by status, missing delivery dates, and review multiplicity.
- `03_delivered_sales_queries.sql` applies the agreed delivered-only sales rule and includes monthly sales, payment methods, on-time delivery, order-level review averages, product categories, buyer states, and the repeat-customer rate.
- `04_powerbi_views.sql` defines the report-ready views exported by `commercepulse.export_powerbi`.

The first query outputs are summarized in `docs/initial_analytics_results.md`.

Power BI-ready views are defined in `04_powerbi_views.sql` and exported by `commercepulse.export_powerbi`. Additional aggregate tables should be added only if report performance or maintenance needs justify them.

Keep query definitions consistent with `docs/business_rules.md`.
