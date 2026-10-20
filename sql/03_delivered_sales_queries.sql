-- Delivered-sales rules: only order_status = 'delivered' is included.
-- Item revenue and freight are calculated separately. Payment values remain separate.

-- 1. Monthly delivered sales, assigned by order purchase month.
WITH delivered_orders AS (
    SELECT order_id,
           strftime('%Y-%m', order_purchase_timestamp) AS purchase_month
    FROM stg_orders
    WHERE order_status = 'delivered'
),
item_totals_by_order AS (
    SELECT order_id,
           SUM(price) AS item_revenue,
           SUM(freight_value) AS freight_value
    FROM stg_order_items
    GROUP BY order_id
),
delivered_order_values AS (
    SELECT d.order_id,
           d.purchase_month,
           COALESCE(i.item_revenue, 0) AS item_revenue,
           COALESCE(i.freight_value, 0) AS freight_value
    FROM delivered_orders AS d
    LEFT JOIN item_totals_by_order AS i ON i.order_id = d.order_id
)
SELECT purchase_month,
       COUNT(*) AS delivered_orders,
       ROUND(SUM(item_revenue), 2) AS item_revenue,
       ROUND(SUM(freight_value), 2) AS freight_value,
       ROUND(SUM(item_revenue + freight_value), 2) AS order_value,
       ROUND(AVG(item_revenue + freight_value), 2) AS average_order_value
FROM delivered_order_values
GROUP BY purchase_month
ORDER BY purchase_month;

-- 2. Payment method usage for delivered orders. An order may use more than one
--    payment method, so distinct order counts across methods are not additive.
SELECT p.payment_type,
       COUNT(*) AS payment_records,
       COUNT(DISTINCT p.order_id) AS delivered_orders_using_method,
       ROUND(SUM(p.payment_value), 2) AS payment_value
FROM stg_order_payments AS p
JOIN stg_orders AS o ON o.order_id = p.order_id
WHERE o.order_status = 'delivered'
GROUP BY p.payment_type
ORDER BY delivered_orders_using_method DESC, p.payment_type;

-- 3. On-time delivery rate for delivered orders with both required dates.
WITH eligible_deliveries AS (
    SELECT order_id,
           CASE
               WHEN date(order_delivered_customer_date)
                    <= date(order_estimated_delivery_date) THEN 1
               ELSE 0
           END AS is_on_time
    FROM stg_orders
    WHERE order_status = 'delivered'
      AND order_delivered_customer_date IS NOT NULL
      AND order_estimated_delivery_date IS NOT NULL
)
SELECT COUNT(*) AS eligible_delivered_orders,
       SUM(is_on_time) AS on_time_orders,
       COUNT(*) - SUM(is_on_time) AS late_orders,
       ROUND(100.0 * SUM(is_on_time) / NULLIF(COUNT(*), 0), 2)
           AS on_time_delivery_rate_pct
FROM eligible_deliveries;

-- 4. Mean order-level review score by delivery outcome. Multiple review rows
--    are averaged first so every order has equal weight in the comparison.
WITH review_score_by_order AS (
    SELECT order_id,
           AVG(review_score) AS mean_review_score,
           COUNT(review_score) AS scored_review_records
    FROM stg_order_reviews
    GROUP BY order_id
),
delivered_orders_with_outcome AS (
    SELECT order_id,
           CASE
               WHEN date(order_delivered_customer_date)
                    <= date(order_estimated_delivery_date) THEN 'on_time'
               ELSE 'late'
           END AS delivery_outcome
    FROM stg_orders
    WHERE order_status = 'delivered'
      AND order_delivered_customer_date IS NOT NULL
      AND order_estimated_delivery_date IS NOT NULL
)
SELECT d.delivery_outcome,
       COUNT(*) AS reviewed_delivered_orders,
       ROUND(AVG(r.mean_review_score), 2) AS mean_order_review_score,
       SUM(r.scored_review_records) AS source_review_records
FROM delivered_orders_with_outcome AS d
JOIN review_score_by_order AS r ON r.order_id = d.order_id
GROUP BY d.delivery_outcome
ORDER BY d.delivery_outcome;

-- 5. Delivered item revenue by category. Use English when mapped, the source
--    Portuguese category name when no translation exists, and an explicit
--    label for missing source categories. Order counts may overlap across categories.
SELECT COALESCE(t.product_category_name_english,
                p.product_category_name,
                '(missing category)') AS product_category,
       COUNT(*) AS delivered_item_rows,
       COUNT(DISTINCT o.order_id) AS delivered_orders,
       ROUND(SUM(i.price), 2) AS item_revenue,
       ROUND(SUM(i.freight_value), 2) AS freight_value
FROM stg_orders AS o
JOIN stg_order_items AS i ON i.order_id = o.order_id
JOIN stg_products AS p ON p.product_id = i.product_id
LEFT JOIN stg_category_translation AS t
       ON t.product_category_name = p.product_category_name
WHERE o.order_status = 'delivered'
GROUP BY product_category
ORDER BY item_revenue DESC;

-- 6. Delivered item revenue by customer state (buyer geography).
SELECT c.customer_state,
       COUNT(*) AS delivered_item_rows,
       COUNT(DISTINCT o.order_id) AS delivered_orders,
       ROUND(SUM(i.price), 2) AS item_revenue,
       ROUND(SUM(i.freight_value), 2) AS freight_value
FROM stg_orders AS o
JOIN stg_customers AS c ON c.customer_id = o.customer_id
JOIN stg_order_items AS i ON i.order_id = o.order_id
WHERE o.order_status = 'delivered'
GROUP BY c.customer_state
ORDER BY item_revenue DESC;

-- 7. Repeat-customer rate across the full dataset period. A person is a
--    repeat customer when they have at least two delivered orders.
WITH delivered_orders_by_customer AS (
    SELECT c.customer_unique_id,
           COUNT(DISTINCT o.order_id) AS delivered_order_count
    FROM stg_orders AS o
    JOIN stg_customers AS c ON c.customer_id = o.customer_id
    WHERE o.order_status = 'delivered'
      AND c.customer_unique_id IS NOT NULL
    GROUP BY c.customer_unique_id
)
SELECT COUNT(*) AS identifiable_customers_with_delivered_orders,
       SUM(CASE WHEN delivered_order_count >= 2 THEN 1 ELSE 0 END)
           AS repeat_customers,
       ROUND(
           100.0 * SUM(CASE WHEN delivered_order_count >= 2 THEN 1 ELSE 0 END)
           / NULLIF(COUNT(*), 0),
           2
       ) AS repeat_customer_rate_pct
FROM delivered_orders_by_customer;
