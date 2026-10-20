# Data Dictionary

This dictionary records the source tables, their observed row counts, and their row-level grain. Column meanings and transformation rules should be refined as the analytical model is built.

## Source tables

| Source file | Rows | Grain | Key fields |
|---|---:|---|---|
| `olist_orders_dataset.csv` | 99,441 | One row per order | `order_id`, `customer_id`, `order_status`, timestamps |
| `olist_order_items_dataset.csv` | 112,650 | One row per order item | `order_id`, `order_item_id`, `product_id`, `seller_id`, `price`, `freight_value` |
| `olist_order_payments_dataset.csv` | 103,886 | One row per payment sequence within an order | `order_id`, `payment_sequential`, `payment_type`, `payment_value` |
| `olist_order_reviews_dataset.csv` | 99,224 | One row per review record; an order may have multiple records | `review_id`, `order_id`, `review_score`, review timestamps |
| `olist_products_dataset.csv` | 32,951 | One row per product | `product_id`, `product_category_name`, product attributes |
| `olist_customers_dataset.csv` | 99,441 | One row per customer/order-level customer ID | `customer_id`, `customer_unique_id`, geography |
| `olist_sellers_dataset.csv` | 3,095 | One row per seller | `seller_id`, seller geography |
| `olist_geolocation_dataset.csv` | 1,000,163 | One row per geolocation record; postal prefixes repeat | `geolocation_zip_code_prefix`, latitude, longitude |
| `product_category_name_translation.csv` | 71 | One row per Portuguese-to-English category mapping | `product_category_name`, `product_category_name_english` |

## Observed relationships

- `orders.customer_id` matches a customer record for every order.
- Every order-item, payment, and review `order_id` matches an order record.
- Every item `product_id` and `seller_id` matches a product and seller record, respectively.
- `customer_id` is unique in the customer table. `customer_unique_id` is repeated for 3,345 customer rows, representing 96,096 distinct customer identifiers across 99,441 rows.
- `review_id` repeats in 814 rows, so it is not a unique key for the review table.
- The category translation table has no mapping for `pc_gamer` and `portateis_cozinha_e_preparadores_de_alimentos`, which are present in the product table.

## Decisions to record

- Source column and cleaned column name
- Data type, business meaning, and unit
- Missing-value treatment
- Key and relationship expectations
- Assumptions and limitations
