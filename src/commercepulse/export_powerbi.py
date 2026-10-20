"""Export Power BI-ready CSVs from the SQLite reporting views."""

from __future__ import annotations

import sqlite3
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
DATABASE_PATH = PROJECT_ROOT / "data" / "processed" / "ecommerce_analytics.sqlite"
EXPORT_DIR = PROJECT_ROOT / "data" / "processed" / "powerbi"
SUMMARY_PATH = PROJECT_ROOT / "reports" / "powerbi_export_summary.csv"

EXPORTS: tuple[tuple[str, str], ...] = (
    ("vw_delivered_orders", "delivered_orders.csv"),
    ("vw_delivered_order_items", "delivered_order_items.csv"),
    ("vw_delivered_payments", "delivered_payments.csv"),
    ("vw_repeat_customer_summary", "repeat_customer_summary.csv"),
    ("vw_delivery_review_summary", "delivery_review_summary.csv"),
)


def export_powerbi_data() -> pd.DataFrame:
    """Export reporting views as UTF-8 CSV files for Power BI import."""
    if not DATABASE_PATH.is_file():
        raise FileNotFoundError(
            f"SQLite database not found: {DATABASE_PATH}. "
            "Run `python -m commercepulse.load_sqlite` first."
        )

    EXPORT_DIR.mkdir(parents=True, exist_ok=True)
    SUMMARY_PATH.parent.mkdir(parents=True, exist_ok=True)
    records: list[dict[str, object]] = []

    with sqlite3.connect(DATABASE_PATH) as connection:
        for view_name, file_name in EXPORTS:
            frame = pd.read_sql_query(f"SELECT * FROM {view_name}", connection)
            output_path = EXPORT_DIR / file_name
            frame.to_csv(output_path, index=False, encoding="utf-8-sig")
            records.append({
                "view_name": view_name,
                "file_name": file_name,
                "row_count": len(frame),
                "column_count": len(frame.columns),
            })

    summary = pd.DataFrame.from_records(records)
    summary.to_csv(SUMMARY_PATH, index=False, encoding="utf-8-sig")
    print(f"Power BI CSV exports saved to: {EXPORT_DIR}")
    print(f"Export summary saved to: {SUMMARY_PATH}")
    print(summary.to_string(index=False))
    return summary


def main() -> None:
    export_powerbi_data()


if __name__ == "__main__":
    main()
