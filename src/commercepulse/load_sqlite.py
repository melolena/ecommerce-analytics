"""Load prepared Olist tables into a validated local SQLite database."""

from __future__ import annotations

import os
import sqlite3
import tempfile
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
DATABASE_PATH = PROCESSED_DIR / "ecommerce_analytics.sqlite"
SCHEMA_PATH = PROJECT_ROOT / "sql" / "01_create_schema.sql"
VIEWS_PATH = PROJECT_ROOT / "sql" / "04_powerbi_views.sql"

TABLE_FILES: tuple[tuple[str, str], ...] = (
    ("stg_customers", "olist_customers_dataset.csv"),
    ("stg_geolocation", "olist_geolocation_dataset.csv"),
    ("stg_products", "olist_products_dataset.csv"),
    ("stg_sellers", "olist_sellers_dataset.csv"),
    ("stg_category_translation", "product_category_name_translation.csv"),
    ("stg_orders", "olist_orders_dataset.csv"),
    ("stg_order_items", "olist_order_items_dataset.csv"),
    ("stg_order_payments", "olist_order_payments_dataset.csv"),
    ("stg_order_reviews", "olist_order_reviews_dataset.csv"),
)

STRING_DTYPES: dict[str, dict[str, str]] = {
    "olist_customers_dataset.csv": {
        "customer_id": "string", "customer_unique_id": "string",
        "customer_zip_code_prefix": "string",
    },
    "olist_geolocation_dataset.csv": {"geolocation_zip_code_prefix": "string"},
    "olist_products_dataset.csv": {"product_id": "string"},
    "olist_sellers_dataset.csv": {
        "seller_id": "string", "seller_zip_code_prefix": "string",
    },
    "olist_order_items_dataset.csv": {
        "order_id": "string", "product_id": "string", "seller_id": "string",
    },
    "olist_order_payments_dataset.csv": {"order_id": "string"},
    "olist_order_reviews_dataset.csv": {"review_id": "string", "order_id": "string"},
    "olist_orders_dataset.csv": {"order_id": "string", "customer_id": "string"},
}


def load_database() -> dict[str, int]:
    """Create a fresh database and replace the previous generated file on success."""
    if not SCHEMA_PATH.is_file():
        raise FileNotFoundError(f"SQLite schema not found: {SCHEMA_PATH}")
    if not VIEWS_PATH.is_file():
        raise FileNotFoundError(f"Power BI views not found: {VIEWS_PATH}")

    for _, file_name in TABLE_FILES:
        if not (PROCESSED_DIR / file_name).is_file():
            raise FileNotFoundError(
                f"Prepared CSV not found: {PROCESSED_DIR / file_name}. "
                "Run `python -m commercepulse.prepare_data` first."
            )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile(
        prefix=".ecommerce_analytics_", suffix=".sqlite", dir=PROCESSED_DIR,
        delete=False,
    ) as temporary_file:
        temporary_path = Path(temporary_file.name)

    try:
        connection = sqlite3.connect(temporary_path)
        try:
            connection.execute("PRAGMA foreign_keys = ON")
            connection.executescript(SCHEMA_PATH.read_text(encoding="utf-8"))

            for table_name, file_name in TABLE_FILES:
                frame = pd.read_csv(
                    PROCESSED_DIR / file_name,
                    dtype=STRING_DTYPES.get(file_name) or None,
                )
                frame.to_sql(
                    table_name, connection, if_exists="append", index=False,
                    chunksize=10_000,
                )

            connection.executescript(VIEWS_PATH.read_text(encoding="utf-8"))
            foreign_key_issues = connection.execute("PRAGMA foreign_key_check").fetchall()
            if foreign_key_issues:
                raise ValueError(f"SQLite foreign-key violations found: {foreign_key_issues[:10]}")

            integrity = connection.execute("PRAGMA integrity_check").fetchone()[0]
            if integrity != "ok":
                raise ValueError(f"SQLite integrity check failed: {integrity}")

            counts = {
                table_name: int(
                    connection.execute(f"SELECT COUNT(*) FROM {table_name}").fetchone()[0]
                )
                for table_name, _ in TABLE_FILES
            }
        finally:
            connection.close()

        os.replace(temporary_path, DATABASE_PATH)
    except Exception:
        temporary_path.unlink(missing_ok=True)
        raise

    print(f"SQLite database created: {DATABASE_PATH}")
    for table_name, row_count in counts.items():
        print(f"{table_name}: {row_count:,} rows")
    return counts


def main() -> None:
    load_database()


if __name__ == "__main__":
    main()
