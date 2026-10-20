from pathlib import Path

import pandas as pd
import pytest


@pytest.fixture
def source_tables() -> dict[str, pd.DataFrame]:
    """Small complete source-table set with useful edge cases."""
    return {
        "olist_customers_dataset.csv": pd.DataFrame([
            {
                "customer_id": "cust-001",
                "customer_unique_id": "person-001",
                "customer_zip_code_prefix": "01234",
                "customer_city": "sao paulo",
                "customer_state": "SP",
            },
        ]),
        "olist_geolocation_dataset.csv": pd.DataFrame([
            {
                "geolocation_zip_code_prefix": "01234",
                "geolocation_lat": -23.5,
                "geolocation_lng": -46.6,
                "geolocation_city": "sao paulo",
                "geolocation_state": "SP",
            },
            {
                "geolocation_zip_code_prefix": "01234",
                "geolocation_lat": -23.5,
                "geolocation_lng": -46.6,
                "geolocation_city": "sao paulo",
                "geolocation_state": "SP",
            },
            {
                "geolocation_zip_code_prefix": "01234",
                "geolocation_lat": -23.6,
                "geolocation_lng": -46.7,
                "geolocation_city": "sao paulo",
                "geolocation_state": "SP",
            },
        ]),
        "olist_order_items_dataset.csv": pd.DataFrame([
            {
                "order_id": "000001",
                "order_item_id": 1,
                "product_id": "product-001",
                "seller_id": "seller-001",
                "shipping_limit_date": "2017-01-05 12:00:00",
                "price": "10.50",
                "freight_value": "2.25",
            },
        ]),
        "olist_order_payments_dataset.csv": pd.DataFrame([
            {
                "order_id": "000001",
                "payment_sequential": 1,
                "payment_type": "credit_card",
                "payment_installments": 1,
                "payment_value": "12.75",
            },
        ]),
        "olist_order_reviews_dataset.csv": pd.DataFrame([
            {
                "review_id": "review-repeat",
                "order_id": "000001",
                "review_score": 5,
                "review_comment_title": None,
                "review_comment_message": "first record",
                "review_creation_date": "2017-01-10 00:00:00",
                "review_answer_timestamp": "2017-01-11 00:00:00",
            },
            {
                "review_id": "review-repeat",
                "order_id": "000001",
                "review_score": 1,
                "review_comment_title": None,
                "review_comment_message": "second record",
                "review_creation_date": "2017-01-10 00:00:00",
                "review_answer_timestamp": "2017-01-11 00:00:00",
            },
        ]),
        "olist_orders_dataset.csv": pd.DataFrame([
            {
                "order_id": "000001",
                "customer_id": "cust-001",
                "order_status": "delivered",
                "order_purchase_timestamp": "2017-01-01 10:00:00",
                "order_approved_at": "2017-01-01 11:00:00",
                "order_delivered_carrier_date": "2017-01-02 12:00:00",
                "order_delivered_customer_date": "2017-01-04 12:00:00",
                "order_estimated_delivery_date": "2017-01-06 00:00:00",
            },
        ]),
        "olist_products_dataset.csv": pd.DataFrame([
            {
                "product_id": "product-001",
                "product_category_name": "beleza_teste",
                "product_name_lenght": 20,
                "product_description_lenght": 100,
                "product_photos_qty": 2,
                "product_weight_g": 300,
                "product_length_cm": 10,
                "product_height_cm": 5,
                "product_width_cm": 8,
            },
        ]),
        "olist_sellers_dataset.csv": pd.DataFrame([
            {
                "seller_id": "seller-001",
                "seller_zip_code_prefix": "54321",
                "seller_city": "campinas",
                "seller_state": "SP",
            },
        ]),
        "product_category_name_translation.csv": pd.DataFrame([
            {
                "product_category_name": "beleza_teste",
                "product_category_name_english": "test_beauty",
            },
        ]),
    }


@pytest.fixture
def source_csvs(tmp_path: Path, source_tables: dict[str, pd.DataFrame]) -> Path:
    raw_dir = tmp_path / "raw"
    raw_dir.mkdir()
    for file_name, frame in source_tables.items():
        frame.to_csv(raw_dir / file_name, index=False)
    return raw_dir
