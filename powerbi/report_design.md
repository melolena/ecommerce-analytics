# Power BI Report Design

The report uses English labels and the approved metric rules in `../docs/business_rules.md`. Page designs are added and reviewed one at a time.

## Page 1 — Executive Overview (approved)

**Purpose:** Give a compact view of delivered sales and operational performance for the selected purchase period.

**Filters**

- Purchase month
- Customer state

**KPI cards**

- Delivered Orders
- Item Revenue
- Freight Value
- Average Delivered Order Value
- On-Time Delivery Rate
- Repeat Customer Rate (full observation period; unaffected by report filters)

**Charts**

1. Monthly Item Revenue — line chart, using `purchase_month` and `Item Revenue`.
2. Delivered Item Revenue by Customer State — horizontal bar chart, sorted descending; display the top 10 states.
3. Payment Method Usage — horizontal bar chart using distinct delivered orders by payment type. Payment values are not combined with sales revenue, and orders with multiple methods may appear in more than one bar.

**Model relationships**

- `delivered_orders[order_id]` (one) to `delivered_order_items[order_id]` (many)
- `delivered_orders[order_id]` (one) to `delivered_payments[order_id]` (many)
- Keep the repeat-customer summary and delivery-review summary as standalone aggregate tables.

**Display notes**

- Format revenue measures as Brazilian reais (R$) with two decimals.
- Format rates as percentages with two decimals.
- Show a note that the data are historical and that the latest purchase dates do not have delivered orders in every month.

## Page 2 — Product Performance (approved)

**Purpose:** Compare delivered item revenue and freight across product categories.

**Filters**

- Purchase month
- Customer state

**KPI cards**

- Item Revenue
- Freight Value
- Delivered Item Rows
- Delivered Orders with Items

**Charts**

1. Top 10 Product Categories by Item Revenue — horizontal bar chart, sorted descending.
2. Freight Value by Product Category — horizontal bar chart using the same Top 10 categories and order as the revenue chart, so the two values can be compared directly.
3. Category Detail — table with category, item revenue, freight value, delivered item rows, and distinct delivered orders.

**Model fields and measures**

- Category: `delivered_order_items[product_category]`, using English translations when available and Portuguese source names for untranslated categories.
- Revenue and freight: measures from `measures.dax`.
- Delivered orders in a category are distinct order IDs. The same order may contain items from multiple categories, so order counts do not add up across categories.

**Display notes**

- Show `(missing category)` as its own category when the source product has no category.
- Format currency as Brazilian reais (R$) with two decimals.

## Page 3 — Delivery & Customer Experience (approved)

**Purpose:** Show delivery timeliness and how order-level review scores vary with delivery outcome.

**Filters**

- Purchase month
- Customer state

**KPI cards**

- On-Time Delivery Rate
- On-Time Eligible Orders
- Late Orders
- Mean Order Review Score
- Delivered Orders Missing Delivery Dates

**Charts**

1. Monthly On-Time Delivery Rate — line chart using delivered orders with both required dates.
2. Mean Order Review Score by Delivery Outcome — column chart for `On time` and `Late`. Each order contributes one average score, even when it has multiple source review records.
3. Delivery Outcome Detail — table with outcome, order count, mean order review score, and source review-record count. Keep `Missing dates` visible as a separate data-quality category, outside the on-time denominator.

**Model fields and measures**

- Delivery outcome: `delivered_orders[delivery_outcome]`.
- Delivery eligibility: nonblank `delivered_orders[is_on_time]`.
- Review score: `delivered_orders[mean_review_score]`, already averaged per order.
- Use the measures in `measures.dax` for rates and counts.

**Display notes**

- Delivery timeliness compares calendar dates from source timestamps, without timezone conversion.
- Exclude `Missing dates` from the on-time denominator and show the count separately.
- Describe the review relationship as descriptive; do not imply that delivery outcome caused the review score.
- Format rates as percentages with two decimals and review scores on the source 1–5 scale.
