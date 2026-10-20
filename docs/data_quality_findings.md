# Data Quality Findings

## Scope

The nine CSV files supplied with the Olist dataset were read in full for this initial profile. The inventory at `reports/data_inventory.csv` is a separate first-look report based on a sample of up to 1,000 rows per file. These checks summarize structure, missing values, exact duplicate rows, key uniqueness, and basic relationships; they do not validate every business rule or timestamp.

## Dataset profile

Purchase timestamps range from 2016-09-04 21:15:19 to 2018-10-17 17:30:18.

| Source file | Rows | Missing values observed |
|---|---:|---|
| `olist_customers_dataset.csv` | 99,441 | None |
| `olist_geolocation_dataset.csv` | 1,000,163 | None |
| `olist_order_items_dataset.csv` | 112,650 | None |
| `olist_order_payments_dataset.csv` | 103,886 | None |
| `olist_order_reviews_dataset.csv` | 99,224 | `review_comment_title`: 87,656; `review_comment_message`: 58,247 |
| `olist_orders_dataset.csv` | 99,441 | `order_approved_at`: 160; `order_delivered_carrier_date`: 1,783; `order_delivered_customer_date`: 2,965 |
| `olist_products_dataset.csv` | 32,951 | `product_category_name`, `product_name_lenght`, `product_description_lenght`, `product_photos_qty`: 610 each; weight and dimensions: 2 each |
| `olist_sellers_dataset.csv` | 3,095 | None |
| `product_category_name_translation.csv` | 71 | None |

## Checks and findings

- No exact duplicate rows were found in the source tables except geolocation, which contains 261,831 exact duplicate rows.
- No duplicate `order_id` values were found in orders, and no duplicate `(order_id, order_item_id)` keys were found in order items.
- All order-to-customer, item-to-order/product/seller, payment-to-order, and review-to-order references resolved to a row in the referenced table.
- The geolocation table contains 1,000,163 rows but only 19,015 distinct postal-code prefixes. Postal-code prefix alone is not a unique key for this table.
- There are 547 order IDs with more than one review record. Review-level analyses must define how multiple records for one order are handled.
- `review_id` is not unique: 814 rows repeat an earlier `review_id`. Use a generated row key when storing review records; do not treat `review_id` as a primary key.
- The product category translation table does not include `pc_gamer` or `portateis_cozinha_e_preparadores_de_alimentos`, both of which appear in the product table.
- Item `price` values were positive, and item `freight_value` values were nonnegative in the full-file check.

## Order status counts

| Status | Orders |
|---|---:|
| delivered | 96,478 |
| shipped | 1,107 |
| canceled | 625 |
| unavailable | 609 |
| invoiced | 314 |
| processing | 301 |
| created | 5 |
| approved | 2 |

Eight orders marked `delivered` have no `order_delivered_customer_date`. A valid on-time-delivery denominator therefore needs to require both delivery and estimated-delivery dates, as stated in the KPI principles.

## Follow-up before publishing metrics

- Validate timestamp chronological consistency. Source timestamps are used as provided, without timezone conversion.
- Review late-period completeness before interpreting monthly trends; source purchase timestamps extend beyond the latest month with delivered orders.
- Add automated checks for the preparation and metric logic.
- Keep payment values separate from item and freight revenue unless a specific reconciliation question calls for a comparison.
