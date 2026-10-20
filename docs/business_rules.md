# Business Rules and KPI Definitions

Initial KPI rules are based on the full-file data inspection and the user's review. Revisit them if the analysis scope changes.

## Revenue and orders

- **Sales KPI eligibility:** include orders with `order_status = 'delivered'` only. Show other statuses separately for operational reporting.
- **Item revenue:** sum of item prices for delivered orders.
- **Freight value:** sum of freight charges for delivered orders, reported separately.
- **Order value:** item revenue plus freight for delivered orders, without adding payment values again.
- **Orders:** distinct delivered order IDs, never a count of item rows.
- **Average order value:** delivered-order value divided by distinct delivered orders.
- **Sales trend month:** use `order_purchase_timestamp` to assign an order to a month.
- **Timestamp handling:** use source timestamps as provided, without timezone conversion. For delivery-on-time classification, compare calendar dates from the source timestamps.
- **Sales by state:** use the customer's state (`customer_state`) as buyer geography.
- **Product category labels:** use the English translation when available; use the original Portuguese name when a translation is missing; label null source categories as `(missing category)`.

## Delivery

- **Delivered orders:** orders with `order_status = 'delivered'`.
- **On-time delivery rate:** delivered orders whose delivery timestamp is on or before the estimated date, divided by delivered orders with valid delivery and estimated-delivery dates.
- Exclude orders without the necessary dates from this metric's denominator and count them in a documented data-quality note.

## Repeat-customer rate

- Use `customer_unique_id` to identify people across order-level customer IDs.
- Use the full dataset observation period.
- **Repeat customers:** customers with at least two delivered orders divided by customers with at least one delivered order.
- Do not assume that each order-level `customer_id` represents the same person across orders.

## Customer reviews

- Preserve every source review record in the staging table.
- For order-level analysis, calculate the arithmetic mean of the available `review_score` values per order before joining to orders. This gives each order one score in order-level comparisons.

## Initial observations from the source data

- The dataset contains eight order statuses: `delivered`, `shipped`, `canceled`, `unavailable`, `invoiced`, `processing`, `created`, and `approved`.
- Eight orders marked `delivered` are missing the customer-delivery timestamp.
- There are 547 order IDs with more than one review record.
- There are 814 rows with a repeated source `review_id`; this field is not a unique review key.
- There are 3,345 repeated `customer_unique_id` values beyond the first occurrence, so repeat-customer analysis should use `customer_unique_id`, not `customer_id`.

## Decisions still to make

- No blocking KPI eligibility decisions remain for the initial metrics. Revisit these rules if the analysis scope changes.
