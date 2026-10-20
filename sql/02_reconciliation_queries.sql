-- Descriptive checks only. No order-status eligibility rule is applied.

-- 1. Row counts in the loaded SQLite staging tables.
SELECT 'stg_customers' AS table_name, COUNT(*) AS row_count FROM stg_customers
UNION ALL SELECT 'stg_geolocation', COUNT(*) FROM stg_geolocation
UNION ALL SELECT 'stg_products', COUNT(*) FROM stg_products
UNION ALL SELECT 'stg_sellers', COUNT(*) FROM stg_sellers
UNION ALL SELECT 'stg_category_translation', COUNT(*) FROM stg_category_translation
UNION ALL SELECT 'stg_orders', COUNT(*) FROM stg_orders
UNION ALL SELECT 'stg_order_items', COUNT(*) FROM stg_order_items
UNION ALL SELECT 'stg_order_payments', COUNT(*) FROM stg_order_payments
UNION ALL SELECT 'stg_order_reviews', COUNT(*) FROM stg_order_reviews;

-- 2. Order counts for every source status.
SELECT order_status, COUNT(*) AS order_count
FROM stg_orders
GROUP BY order_status
ORDER BY order_count DESC, order_status;

-- 3. Monthly order counts, split by status.
SELECT strftime('%Y-%m', order_purchase_timestamp) AS purchase_month,
       order_status,
       COUNT(*) AS order_count
FROM stg_orders
GROUP BY purchase_month, order_status
ORDER BY purchase_month, order_status;

-- 4. Item revenue and freight by status. Items are aggregated per order first,
--    so joining orders does not multiply item values.
WITH item_totals_by_order AS (
    SELECT order_id,
           COUNT(*) AS item_row_count,
           SUM(price) AS item_revenue,
           SUM(freight_value) AS freight_value
    FROM stg_order_items
    GROUP BY order_id
)
SELECT o.order_status,
       COUNT(*) AS order_count,
       SUM(COALESCE(i.item_row_count, 0)) AS item_row_count,
       ROUND(SUM(COALESCE(i.item_revenue, 0)), 2) AS item_revenue,
       ROUND(SUM(COALESCE(i.freight_value, 0)), 2) AS freight_value
FROM stg_orders AS o
LEFT JOIN item_totals_by_order AS i ON i.order_id = o.order_id
GROUP BY o.order_status
ORDER BY o.order_status;

-- 5. Payment values by status, kept separate from item and freight totals.
WITH payment_totals_by_order AS (
    SELECT order_id, SUM(payment_value) AS payment_value
    FROM stg_order_payments
    GROUP BY order_id
)
SELECT o.order_status,
       COUNT(*) AS order_count,
       ROUND(SUM(COALESCE(p.payment_value, 0)), 2) AS payment_value
FROM stg_orders AS o
LEFT JOIN payment_totals_by_order AS p ON p.order_id = o.order_id
GROUP BY o.order_status
ORDER BY o.order_status;

-- 6. Delivered-date completeness by order status.
SELECT order_status,
       COUNT(*) AS order_count,
       SUM(CASE WHEN order_delivered_customer_date IS NULL THEN 1 ELSE 0 END)
           AS missing_delivery_timestamp,
       SUM(CASE WHEN order_estimated_delivery_date IS NULL THEN 1 ELSE 0 END)
           AS missing_estimated_delivery_timestamp
FROM stg_orders
GROUP BY order_status
ORDER BY order_status;

-- 7. Review-record multiplicity and source review_id repeats.
SELECT COUNT(*) AS review_records,
       COUNT(DISTINCT review_id) AS distinct_review_ids,
       COUNT(DISTINCT order_id) AS reviewed_orders,
       COUNT(*) - COUNT(DISTINCT review_id) AS repeated_review_id_rows
FROM stg_order_reviews;

SELECT review_score, COUNT(*) AS review_record_count
FROM stg_order_reviews
GROUP BY review_score
ORDER BY review_score;

SELECT COUNT(*) AS orders_with_multiple_review_records
FROM (
    SELECT order_id
    FROM stg_order_reviews
    GROUP BY order_id
    HAVING COUNT(*) > 1
);
