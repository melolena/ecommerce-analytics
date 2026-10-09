# Data Dictionary

Map the selected Olist source columns to cleaned names and business meanings here.

## Planned source tables

| Source file | Expected role | Key fields to inspect |
|---|---|---|
| `olist_orders_dataset.csv` | Order-level facts | `order_id`, `customer_id`, status and timestamps |
| `olist_order_items_dataset.csv` | Item-level facts | `order_id`, `product_id`, `seller_id`, price, freight |
| `olist_order_payments_dataset.csv` | Payment-level facts | `order_id`, payment type, value, installments |
| `olist_order_reviews_dataset.csv` | Review-level facts | review ID, order ID, score and timestamps |
| `olist_products_dataset.csv` | Product dimension | product ID, category and product attributes |
| `olist_customers_dataset.csv` | Customer dimension | customer ID, unique customer ID and geography |
| `olist_sellers_dataset.csv` | Seller dimension | seller ID and geography |

Confirm file availability and exact values after downloading the source data.

## Decisions to record

- Source column and cleaned column name
- Data type, business meaning and unit
- Missing-value treatment
- Key and relationship expectations
- Assumptions and limitations
