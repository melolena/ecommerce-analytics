# Local data

Download the Olist dataset from https://www.kaggle.com/datasets/olistbr/brazilian-ecommerce and place the extracted CSV files in `data/raw/`.

Raw files and generated processed files are ignored by Git. Do not commit the full dataset to this repository. Check the dataset's licence and access terms before redistributing data.

The initial inspection script samples up to 1,000 rows per CSV and creates `reports/data_inventory.csv`.

After installing the project, run `python -m commercepulse.prepare_data` to validate and prepare all source tables. Prepared CSV files are written to `data/processed/`; the run summary is saved to `reports/data_preparation_summary.csv`. See `docs/data_preparation.md` for the transformations and validation rules.
