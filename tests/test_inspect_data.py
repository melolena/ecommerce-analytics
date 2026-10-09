from pathlib import Path

import pandas as pd

from commercepulse.inspect_data import build_inventory, profile_csv


def test_profile_csv_reports_columns_and_missing_values(tmp_path: Path) -> None:
    csv_path = tmp_path / "example.csv"
    pd.DataFrame({"order_id": [1, 2, 3], "amount": [10.0, None, 30.0]}).to_csv(
        csv_path, index=False
    )

    result = profile_csv(csv_path)

    assert result["file_name"] == "example.csv"
    assert result["sample_rows"] == 3
    assert result["column_count"] == 2
    assert result["missing_cells_in_sample"] == 1
    assert result["missing_pct_in_sample"] == 16.67


def test_build_inventory_returns_empty_frame_for_no_csv(tmp_path: Path) -> None:
    result = build_inventory(tmp_path)

    assert result.empty
    assert "file_name" in result.columns
    assert "error" in result.columns
