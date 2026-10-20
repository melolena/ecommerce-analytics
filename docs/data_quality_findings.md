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

## Timestamp chronology audit

The nine local source CSVs are present and their row counts match the documented profile. The `stg_orders` table has 99,441 rows and the same purchase timestamp range as the source CSV. Status and timestamp values in staging match the source after normalizing the date-only `order_estimated_delivery_date` field.

All five order date fields were parseable. Missing values were excluded from pairwise chronology checks, not counted as violations.

| Timestamp field | Missing | Invalid |
|---|---:|---:|
| `order_purchase_timestamp` | 0 | 0 |
| `order_approved_at` | 160 | 0 |
| `order_delivered_carrier_date` | 1,783 | 0 |
| `order_delivered_customer_date` | 2,965 | 0 |
| `order_estimated_delivery_date` | 0 | 0 |

| Rule | Valid pairs | Pairs without both dates | Violations |
|---|---:|---:|---:|
| Purchase after approval | 99,281 | 160 | 0 |
| Approval after carrier handoff | 97,644 | 1,797 | 1,359 |
| Carrier handoff after customer delivery | 96,475 | 2,966 | 23 |
| Purchase after carrier handoff | 97,658 | 1,783 | 166 |
| Purchase after customer delivery | 96,476 | 2,965 | 0 |
| Purchase after estimated delivery date | 99,441 | 0 | 0 |
| Approval after customer delivery (additional check) | 96,462 | 2,979 | 61 |

The approval/carrier inversions comprise 1,350 delivered and 9 shipped orders. All 23 carrier/customer-delivery inversions are delivered orders. Purchase/carrier inversions comprise 165 delivered and 1 shipped order. The order statuses do not explain these inversions. They are also present in the source CSV; no correction or exclusion was applied.

Examples from source records:

| Rule | `order_id` | Status | First timestamp | Second timestamp |
|---|---|---|---|---|
| Approval after carrier handoff | `7c48bb55e8e4f7e56d412e9653db37bc` | delivered | approval: `2018-07-16 18:50:22` | carrier: `2018-01-26 13:35:00` |
| Approval after carrier handoff | `1fab4ac9d85079b3da72a11475ae1685` | delivered | approval: `2017-09-13 22:06:11` | carrier: `2017-09-04 13:10:23` |
| Carrier handoff after delivery | `c1e2bf2b7dd3309f2f5356c6b63968fa` | delivered | carrier: `2017-03-02 17:34:26` | customer: `2017-02-14 15:15:57` |
| Carrier handoff after delivery | `fa3e37584f4fdb1ded0e0de700dfcb4e` | delivered | carrier: `2017-08-09 18:18:43` | customer: `2017-08-01 21:13:01` |

The available data do not identify why these event timestamps are out of sequence. Use them as provided and do not infer corrected event times.

## Recent monthly completeness

The overall status counts remain consistent with the initial profile. The last purchase month with any delivered orders is August 2018.

| Purchase month | Orders | Delivered | Not delivered | Missing customer delivery date | Missing estimated date |
|---|---:|---:|---:|---:|---:|
| 2018-06 | 6,167 | 6,099 | 68 | 71 | 0 |
| 2018-07 | 6,292 | 6,159 | 133 | 136 | 0 |
| 2018-08 | 6,512 | 6,351 | 161 | 161 | 0 |
| 2018-09 | 16 | 0 | 16 | 16 | 0 |
| 2018-10 | 4 | 0 | 4 | 4 | 0 |

The September orders comprise 15 canceled and 1 shipped order; all four October orders are canceled. The source ends on 2018-10-17. These 20 late-period orders have no customer-delivery date because none is marked delivered; no estimated dates are missing. Their sparse volume and statuses support treating the series tail cautiously, but the local data alone do not establish why it is sparse or whether extraction timing caused it.
