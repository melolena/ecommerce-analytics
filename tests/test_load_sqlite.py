from pathlib import Path
import sqlite3

import pandas as pd
import pytest

from commercepulse import load_sqlite, prepare_data


def test_load_database_builds_valid_sqlite_from_temporary_prepared_csvs(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    source_csvs: Path,
) -> None:
    prepared_dir = tmp_path / "prepared"
    reports_dir = tmp_path / "reports"
    monkeypatch.setattr(prepare_data, "RAW_DIR", source_csvs)
    monkeypatch.setattr(prepare_data, "PROCESSED_DIR", prepared_dir)
    monkeypatch.setattr(prepare_data, "REPORTS_DIR", reports_dir)
    prepare_data.prepare_dataset()

    database_path = tmp_path / "ecommerce_analytics.sqlite"
    monkeypatch.setattr(load_sqlite, "PROCESSED_DIR", prepared_dir)
    monkeypatch.setattr(load_sqlite, "DATABASE_PATH", database_path)
    monkeypatch.setattr(load_sqlite, "SCHEMA_PATH", Path(__file__).parents[1] / "sql" / "01_create_schema.sql")
    monkeypatch.setattr(load_sqlite, "VIEWS_PATH", Path(__file__).parents[1] / "sql" / "04_powerbi_views.sql")

    counts = load_sqlite.load_database()

    assert counts == {
        "stg_customers": 1,
        "stg_geolocation": 2,
        "stg_products": 1,
        "stg_sellers": 1,
        "stg_category_translation": 1,
        "stg_orders": 1,
        "stg_order_items": 1,
        "stg_order_payments": 1,
        "stg_order_reviews": 2,
    }
    assert database_path.is_file()

    with sqlite3.connect(database_path) as connection:
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        # review_id is deliberately not unique; the generated row key preserves records.
        assert connection.execute(
            "SELECT COUNT(*) FROM stg_order_reviews WHERE review_id = 'review-repeat'"
        ).fetchone()[0] == 2


def test_load_database_missing_input_does_not_replace_existing_database(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path
) -> None:
    prepared_dir = tmp_path / "prepared"
    prepared_dir.mkdir()
    database_path = tmp_path / "existing.sqlite"
    database_path.write_bytes(b"existing database marker")
    monkeypatch.setattr(load_sqlite, "PROCESSED_DIR", prepared_dir)
    monkeypatch.setattr(load_sqlite, "DATABASE_PATH", database_path)
    monkeypatch.setattr(load_sqlite, "SCHEMA_PATH", Path(__file__).parents[1] / "sql" / "01_create_schema.sql")
    monkeypatch.setattr(load_sqlite, "VIEWS_PATH", Path(__file__).parents[1] / "sql" / "04_powerbi_views.sql")

    with pytest.raises(FileNotFoundError, match="Prepared CSV not found"):
        load_sqlite.load_database()

    assert database_path.read_bytes() == b"existing database marker"


def test_load_database_accepts_missing_customer_unique_id_and_keeps_relations_valid(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    source_csvs: Path,
) -> None:
    customers_path = source_csvs / "olist_customers_dataset.csv"
    customers = pd.read_csv(
        customers_path,
        dtype={"customer_id": "string", "customer_unique_id": "string"},
    )
    customers.loc[0, "customer_unique_id"] = pd.NA
    customers.to_csv(customers_path, index=False)

    prepared_dir = tmp_path / "prepared"
    monkeypatch.setattr(prepare_data, "RAW_DIR", source_csvs)
    monkeypatch.setattr(prepare_data, "PROCESSED_DIR", prepared_dir)
    monkeypatch.setattr(prepare_data, "REPORTS_DIR", tmp_path / "reports")
    prepare_data.prepare_dataset()

    database_path = tmp_path / "with_missing_unique_id.sqlite"
    monkeypatch.setattr(load_sqlite, "PROCESSED_DIR", prepared_dir)
    monkeypatch.setattr(load_sqlite, "DATABASE_PATH", database_path)
    monkeypatch.setattr(
        load_sqlite, "SCHEMA_PATH",
        Path(__file__).parents[1] / "sql" / "01_create_schema.sql",
    )
    monkeypatch.setattr(
        load_sqlite, "VIEWS_PATH",
        Path(__file__).parents[1] / "sql" / "04_powerbi_views.sql",
    )

    counts = load_sqlite.load_database()

    assert counts["stg_customers"] == 1
    with sqlite3.connect(database_path) as connection:
        assert connection.execute(
            "SELECT customer_id, customer_unique_id FROM stg_customers"
        ).fetchone() == ("cust-001", None)
        assert connection.execute(
            "SELECT c.customer_id FROM stg_orders AS o "
            "JOIN stg_customers AS c ON c.customer_id = o.customer_id"
        ).fetchall() == [("cust-001",)]
        assert connection.execute("PRAGMA foreign_key_check").fetchall() == []
        assert connection.execute("PRAGMA integrity_check").fetchone()[0] == "ok"


def test_customer_id_is_required_by_sqlite_schema() -> None:
    schema_path = Path(__file__).parents[1] / "sql" / "01_create_schema.sql"
    with sqlite3.connect(":memory:") as connection:
        connection.executescript(schema_path.read_text())

        with pytest.raises(sqlite3.IntegrityError, match="NOT NULL"):
            connection.execute(
                "INSERT INTO stg_customers (customer_id, customer_unique_id) "
                "VALUES (NULL, 'identifiable-customer')"
            )
