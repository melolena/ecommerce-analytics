"""Validate and prepare the Olist CSV tables without changing raw files."""

from __future__ import annotations

from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"
REPORTS_DIR = PROJECT_ROOT / "reports"

TABLES: dict[str, set[str]] = {
    "olist_customers_dataset.csv": {
        "customer_id", "customer_unique_id", "customer_zip_code_prefix",
        "customer_city", "customer_state",
    },
    "olist_geolocation_dataset.csv": {
        "geolocation_zip_code_prefix", "geolocation_lat", "geolocation_lng",
        "geolocation_city", "geolocation_state",
    },
    "olist_order_items_dataset.csv": {
        "order_id", "order_item_id", "product_id", "seller_id",
        "shipping_limit_date", "price", "freight_value",
    },
    "olist_order_payments_dataset.csv": {
        "order_id", "payment_sequential", "payment_type",
        "payment_installments", "payment_value",
    },
    "olist_order_reviews_dataset.csv": {
        "review_id", "order_id", "review_score", "review_comment_title",
        "review_comment_message", "review_creation_date",
        "review_answer_timestamp",
    },
    "olist_orders_dataset.csv": {
        "order_id", "customer_id", "order_status", "order_purchase_timestamp",
        "order_approved_at", "order_delivered_carrier_date",
        "order_delivered_customer_date", "order_estimated_delivery_date",
    },
    "olist_products_dataset.csv": {
        "product_id", "product_category_name", "product_name_lenght",
        "product_description_lenght", "product_photos_qty", "product_weight_g",
        "product_length_cm", "product_height_cm", "product_width_cm",
    },
    "olist_sellers_dataset.csv": {
        "seller_id", "seller_zip_code_prefix", "seller_city", "seller_state",
    },
    "product_category_name_translation.csv": {
        "product_category_name", "product_category_name_english",
    },
}

STRING_COLUMNS: dict[str, set[str]] = {
    "olist_customers_dataset.csv": {"customer_id", "customer_unique_id"},
    "olist_order_items_dataset.csv": {"order_id", "product_id", "seller_id"},
    "olist_order_payments_dataset.csv": {"order_id"},
    "olist_order_reviews_dataset.csv": {"review_id", "order_id"},
    "olist_orders_dataset.csv": {"order_id", "customer_id"},
    "olist_products_dataset.csv": {"product_id"},
    "olist_sellers_dataset.csv": {"seller_id"},
}

DATE_COLUMNS: dict[str, set[str]] = {
    "olist_order_items_dataset.csv": {"shipping_limit_date"},
    "olist_order_reviews_dataset.csv": {
        "review_creation_date", "review_answer_timestamp",
    },
    "olist_orders_dataset.csv": {
        "order_purchase_timestamp", "order_approved_at",
        "order_delivered_carrier_date", "order_delivered_customer_date",
        "order_estimated_delivery_date",
    },
}

NUMERIC_COLUMNS: dict[str, set[str]] = {
    "olist_geolocation_dataset.csv": {"geolocation_lat", "geolocation_lng"},
    "olist_order_items_dataset.csv": {
        "order_item_id", "price", "freight_value",
    },
    "olist_order_payments_dataset.csv": {
        "payment_sequential", "payment_installments", "payment_value",
    },
    "olist_order_reviews_dataset.csv": {"review_score"},
    "olist_products_dataset.csv": {
        "product_name_lenght", "product_description_lenght",
        "product_photos_qty", "product_weight_g", "product_length_cm",
        "product_height_cm", "product_width_cm",
    },
}

UNIQUE_KEYS: dict[str, list[str]] = {
    "olist_customers_dataset.csv": ["customer_id"],
    "olist_orders_dataset.csv": ["order_id"],
    "olist_order_items_dataset.csv": ["order_id", "order_item_id"],
    "olist_products_dataset.csv": ["product_id"],
    "olist_sellers_dataset.csv": ["seller_id"],
    "product_category_name_translation.csv": ["product_category_name"],
}


def _load_table(file_name: str) -> pd.DataFrame:
    """Read a source CSV with identifiers kept as strings."""
    path = RAW_DIR / file_name
    if not path.is_file():
        raise FileNotFoundError(f"Required source file not found: {path}")

    dtype = {column: "string" for column in STRING_COLUMNS.get(file_name, set())}
    return pd.read_csv(path, dtype=dtype or None)


def _prepare_table(file_name: str, frame: pd.DataFrame) -> pd.DataFrame:
    missing_columns = TABLES[file_name] - set(frame.columns)
    if missing_columns:
        raise ValueError(
            f"{file_name} is missing required columns: {sorted(missing_columns)}"
        )

    for column in DATE_COLUMNS.get(file_name, set()):
        frame[column] = pd.to_datetime(frame[column], errors="raise")

    for column in NUMERIC_COLUMNS.get(file_name, set()):
        frame[column] = pd.to_numeric(frame[column], errors="raise")

    # Preserve leading zeros in Brazilian postal-code prefixes.
    zip_columns = [
        name for name in frame.columns
        if name.endswith("zip_code_prefix") or name == "geolocation_zip_code_prefix"
    ]
    for column in zip_columns:
        frame[column] = frame[column].astype("string").str.zfill(5)

    return frame


def _validate_keys(tables: dict[str, pd.DataFrame]) -> None:
    for file_name, columns in UNIQUE_KEYS.items():
        duplicated = tables[file_name].duplicated(columns)
        if duplicated.any():
            raise ValueError(
                f"{file_name} has {int(duplicated.sum())} duplicate rows for key {columns}"
            )

    relationships = [
        ("olist_orders_dataset.csv", "customer_id", "olist_customers_dataset.csv", "customer_id"),
        ("olist_order_items_dataset.csv", "order_id", "olist_orders_dataset.csv", "order_id"),
        ("olist_order_items_dataset.csv", "product_id", "olist_products_dataset.csv", "product_id"),
        ("olist_order_items_dataset.csv", "seller_id", "olist_sellers_dataset.csv", "seller_id"),
        ("olist_order_payments_dataset.csv", "order_id", "olist_orders_dataset.csv", "order_id"),
        ("olist_order_reviews_dataset.csv", "order_id", "olist_orders_dataset.csv", "order_id"),
    ]
    for child_file, child_column, parent_file, parent_column in relationships:
        child_values = tables[child_file][child_column]
        parent_values = tables[parent_file][parent_column]
        orphan_count = int((~child_values.isin(parent_values)).sum())
        if orphan_count:
            raise ValueError(
                f"{child_file}.{child_column} has {orphan_count} values without a "
                f"match in {parent_file}.{parent_column}"
            )


def prepare_dataset() -> pd.DataFrame:
    """Prepare all source tables, save CSV outputs, and return a run summary."""
    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)
    REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    tables = {
        file_name: _prepare_table(file_name, _load_table(file_name))
        for file_name in TABLES
    }
    _validate_keys(tables)

    records: list[dict[str, object]] = []
    for file_name, frame in tables.items():
        output = frame.drop_duplicates() if file_name == "olist_geolocation_dataset.csv" else frame
        output.to_csv(PROCESSED_DIR / file_name, index=False)
        records.append({
            "file_name": file_name,
            "source_rows": len(frame),
            "processed_rows": len(output),
            "exact_duplicate_rows_removed": len(frame) - len(output),
            "missing_cells_preserved": int(output.isna().sum().sum()),
            "column_count": len(output.columns),
        })

    summary = pd.DataFrame.from_records(records)
    summary_path = REPORTS_DIR / "data_preparation_summary.csv"
    summary.to_csv(summary_path, index=False)
    print(f"Prepared tables saved to: {PROCESSED_DIR}")
    print(f"Preparation summary saved to: {summary_path}")
    print(summary.to_string(index=False))
    return summary


def main() -> None:
    prepare_dataset()


if __name__ == "__main__":
    main()
