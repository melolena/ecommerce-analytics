# Business Rules and KPI Definitions

Complete and validate these rules after inspecting the dataset and before publishing dashboard results.

## Revenue and orders

- **Item revenue:** sum of item prices for the explicitly defined set of eligible orders.
- **Freight value:** sum of freight charges for the same eligible orders, reported separately.
- **Order value:** item revenue plus freight, without adding payment values again.
- **Orders:** distinct eligible order IDs, never a count of item rows.
- **Average order value:** eligible order value divided by distinct eligible orders.

## Delivery

- **Delivered orders:** orders whose status and timestamp support classifying them as delivered.
- **On-time delivery rate:** delivered orders whose delivery timestamp is on or before the estimated date, divided by delivered orders with valid delivery and estimated-delivery dates.
- Exclude orders without the necessary dates from this metric's denominator and count them in a documented data-quality note.

## Repeat-customer rate

Use the dataset's unique customer identifier to identify repeat customers, and document the observation window. Do not assume that each order-level customer ID represents the same person across orders.

## Decisions still to make

- Which order statuses qualify for sales reporting
- How cancelled and unavailable orders are treated
- Time-zone and date-boundary conventions
- How multiple payments or reviews per order are handled
- How missing product categories are presented
