from pathlib import Path

import pandas as pd
import pytest

from commercepulse import prepare_data


def _redirect_prepare_dirs(monkeypatch: pytest.MonkeyPatch, tmp_path: Path, raw_dir: Path) -> None:
    monkeypatch.setattr(prepare_data, "RAW_DIR", raw_dir)
    monkeypatch.setattr(prepare_data, "PROCESSED_DIR", tmp_path / "processed")
    monkeypatch.setattr(prepare_data, "REPORTS_DIR", tmp_path / "reports")


def test_prepare_dataset_reports_missing_required_file(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, source_csvs: Path
) -> None:
    (source_csvs / "olist_customers_dataset.csv").unlink()
    _redirect_prepare_dirs(monkeypatch, tmp_path, source_csvs)

    with pytest.raises(FileNotFoundError, match="olist_customers_dataset.csv"):
        prepare_data.prepare_dataset()


def test_prepare_table_reports_missing_required_columns() -> None:
    with pytest.raises(ValueError, match="missing required columns"):
        prepare_data._prepare_table(
            "olist_orders_dataset.csv",
            pd.DataFrame({"order_id": ["order-1"]}),
        )


def test_prepare_dataset_converts_dates_numbers_and_identifiers(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, source_csvs: Path
) -> None:
    _redirect_prepare_dirs(monkeypatch, tmp_path, source_csvs)

    raw_orders = prepare_data._load_table("olist_orders_dataset.csv")
    assert str(raw_orders["order_id"].dtype) == "string"
    assert raw_orders.loc[0, "order_id"] == "000001"
    typed_orders = prepare_data._prepare_table(
        "olist_orders_dataset.csv", raw_orders.copy()
    )

    prepare_data.prepare_dataset()
    items = pd.read_csv(
        tmp_path / "processed" / "olist_order_items_dataset.csv",
        dtype={"order_id": "string", "product_id": "string", "seller_id": "string"},
    )
    customers = pd.read_csv(
        tmp_path / "processed" / "olist_customers_dataset.csv",
        dtype={"customer_zip_code_prefix": "string"},
    )

    assert pd.api.types.is_datetime64_any_dtype(typed_orders["order_purchase_timestamp"])
    assert items.loc[0, "order_id"] == "000001"
    assert items.loc[0, "price"] == pytest.approx(10.5)
    assert items.loc[0, "freight_value"] == pytest.approx(2.25)
    assert customers.loc[0, "customer_zip_code_prefix"] == "01234"


@pytest.mark.parametrize(
    ("file_name", "column", "bad_value"),
    [
        ("olist_order_items_dataset.csv", "price", "not-a-number"),
        ("olist_orders_dataset.csv", "order_purchase_timestamp", "not-a-date"),
    ],
)
def test_prepare_table_rejects_invalid_typed_values(
    source_tables: dict[str, pd.DataFrame],
    file_name: str,
    column: str,
    bad_value: str,
) -> None:
    frame = source_tables[file_name].copy()
    frame.loc[0, column] = bad_value

    with pytest.raises((ValueError, TypeError)):
        prepare_data._prepare_table(file_name, frame)


@pytest.mark.parametrize(
    ("file_name", "duplicate_columns"),
    [
        ("olist_orders_dataset.csv", ["order_id"]),
        ("olist_order_items_dataset.csv", ["order_id", "order_item_id"]),
    ],
)
def test_prepare_dataset_rejects_duplicate_declared_keys(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    source_csvs: Path,
    source_tables: dict[str, pd.DataFrame],
    file_name: str,
    duplicate_columns: list[str],
) -> None:
    frame = source_tables[file_name]
    frame = pd.concat([frame, frame.iloc[[0]]], ignore_index=True)
    frame.to_csv(source_csvs / file_name, index=False)
    _redirect_prepare_dirs(monkeypatch, tmp_path, source_csvs)

    with pytest.raises(ValueError, match="duplicate rows"):
        prepare_data.prepare_dataset()


def test_prepare_dataset_rejects_orphan_relationships(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    source_csvs: Path,
    source_tables: dict[str, pd.DataFrame],
) -> None:
    items = source_tables["olist_order_items_dataset.csv"].copy()
    items.loc[0, "order_id"] = "missing-order"
    items.to_csv(source_csvs / "olist_order_items_dataset.csv", index=False)
    _redirect_prepare_dirs(monkeypatch, tmp_path, source_csvs)

    with pytest.raises(ValueError, match="without a match"):
        prepare_data.prepare_dataset()


def test_prepare_dataset_preserves_missing_values_and_raw_files(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    source_csvs: Path,
    source_tables: dict[str, pd.DataFrame],
) -> None:
    source_tables["olist_orders_dataset.csv"].loc[
        0, "order_delivered_customer_date"
    ] = None
    source_tables["olist_order_reviews_dataset.csv"].loc[
        0, "review_comment_title"
    ] = None
    for file_name, frame in source_tables.items():
        frame.to_csv(source_csvs / file_name, index=False)
    originals = {
        path.name: path.read_bytes() for path in source_csvs.glob("*.csv")
    }
    _redirect_prepare_dirs(monkeypatch, tmp_path, source_csvs)

    summary = prepare_data.prepare_dataset()
    prepared_orders = pd.read_csv(tmp_path / "processed" / "olist_orders_dataset.csv")
    prepared_reviews = pd.read_csv(tmp_path / "processed" / "olist_order_reviews_dataset.csv")

    assert pd.isna(prepared_orders.loc[0, "order_delivered_customer_date"])
    assert pd.isna(prepared_reviews.loc[0, "review_comment_title"])
    assert {path.name: path.read_bytes() for path in source_csvs.glob("*.csv")} == originals
    assert summary["missing_cells_preserved"].sum() >= 2


def test_prepare_dataset_deduplicates_only_exact_geolocation_rows(
    monkeypatch: pytest.MonkeyPatch,
    tmp_path: Path,
    source_csvs: Path,
    source_tables: dict[str, pd.DataFrame],
) -> None:
    # A repeated review identifier is not a key; source review rows must remain.
    reviews = source_tables["olist_order_reviews_dataset.csv"]
    reviews.loc[1, "review_id"] = reviews.loc[0, "review_id"]
    reviews.to_csv(source_csvs / "olist_order_reviews_dataset.csv", index=False)
    _redirect_prepare_dirs(monkeypatch, tmp_path, source_csvs)

    summary = prepare_data.prepare_dataset().set_index("file_name")
    processed_geo = pd.read_csv(tmp_path / "processed" / "olist_geolocation_dataset.csv")
    processed_reviews = pd.read_csv(tmp_path / "processed" / "olist_order_reviews_dataset.csv")

    assert len(processed_geo) == 2
    assert len(processed_reviews) == 2
    assert summary.loc["olist_geolocation_dataset.csv", "exact_duplicate_rows_removed"] == 1
    assert summary.loc["olist_order_reviews_dataset.csv", "exact_duplicate_rows_removed"] == 0


def test_prepare_dataset_writes_expected_run_summary(
    monkeypatch: pytest.MonkeyPatch, tmp_path: Path, source_csvs: Path
) -> None:
    _redirect_prepare_dirs(monkeypatch, tmp_path, source_csvs)

    summary = prepare_data.prepare_dataset()
    saved_summary = pd.read_csv(tmp_path / "reports" / "data_preparation_summary.csv")

    assert len(summary) == 9
    assert list(saved_summary.columns) == [
        "file_name", "source_rows", "processed_rows",
        "exact_duplicate_rows_removed", "missing_cells_preserved", "column_count",
    ]
    geo = saved_summary.set_index("file_name").loc["olist_geolocation_dataset.csv"]
    assert geo["source_rows"] == 3
    assert geo["processed_rows"] == 2
