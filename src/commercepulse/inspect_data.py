"""Create a lightweight inventory of source CSV files.

This first-look helper samples up to 1,000 rows from each CSV. It does not
replace full-data validation or data-quality checks.
"""

from pathlib import Path

import pandas as pd

SAMPLE_ROWS = 1_000
PROJECT_ROOT = Path(__file__).resolve().parents[2]


def profile_csv(path: Path, sample_rows: int = SAMPLE_ROWS) -> dict[str, object]:
    """Return a small schema and missing-value profile for a CSV sample."""
    sample = pd.read_csv(path, nrows=sample_rows)
    total_cells = int(sample.shape[0] * sample.shape[1])
    missing_cells = int(sample.isna().sum().sum())

    return {
        "file_name": path.name,
        "sample_rows": int(len(sample)),
        "sample_limit": sample_rows,
        "column_count": int(sample.shape[1]),
        "columns": ", ".join(str(column) for column in sample.columns),
        "missing_cells_in_sample": missing_cells,
        "missing_pct_in_sample": (
            round(missing_cells / total_cells * 100, 2) if total_cells else 0.0
        ),
    }


def build_inventory(raw_dir: Path) -> pd.DataFrame:
    """Profile all CSV files in a directory, in alphabetical order."""
    columns = [
        "file_name", "sample_rows", "sample_limit", "column_count", "columns",
        "missing_cells_in_sample", "missing_pct_in_sample", "error",
    ]
    records: list[dict[str, object]] = []

    for path in sorted(raw_dir.glob("*.csv")):
        try:
            records.append({**profile_csv(path), "error": ""})
        except (OSError, UnicodeError, pd.errors.ParserError, pd.errors.EmptyDataError) as exc:
            records.append({
                "file_name": path.name,
                "sample_rows": 0,
                "sample_limit": SAMPLE_ROWS,
                "column_count": 0,
                "columns": "",
                "missing_cells_in_sample": 0,
                "missing_pct_in_sample": 0.0,
                "error": str(exc),
            })

    return pd.DataFrame.from_records(records, columns=columns)


def main() -> None:
    """Write the initial data inventory to reports/data_inventory.csv."""
    raw_dir = PROJECT_ROOT / "data" / "raw"
    reports_dir = PROJECT_ROOT / "reports"
    reports_dir.mkdir(parents=True, exist_ok=True)

    if not raw_dir.exists() or not any(raw_dir.glob("*.csv")):
        print(f"No CSV files found in {raw_dir}. Download the Olist dataset and place its CSV files there.")
        return

    inventory = build_inventory(raw_dir)
    output_path = reports_dir / "data_inventory.csv"
    inventory.to_csv(output_path, index=False)
    print(f"Inventory saved to: {output_path}")
    print(inventory[["file_name", "sample_rows", "column_count", "error"]].to_string(index=False))


if __name__ == "__main__":
    main()
