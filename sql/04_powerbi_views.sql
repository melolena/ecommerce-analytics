-- Power BI import views based on the agreed initial business rules.

CREATE VIEW vw_delivered_orders AS
WITH item_totals AS (
    SELECT order_id,
           COUNT(*) AS order_item_rows,
           SUM(price) AS item_revenue,
           SUM(freight_value) AS freight_value
    FROM stg_order_items
    GROUP BY order_id
),
review_scores AS (
    SELECT order_id,
           AVG(review_score) AS mean_review_score,
           COUNT(review_score) AS scored_review_records
    FROM stg_order_reviews
    GROUP BY order_id
)
SELECT o.order_id,
       o.customer_id,
       c.customer_unique_id,
       c.customer_state,
       o.order_purchase_timestamp,
       strftime('%Y-%m', o.order_purchase_timestamp) AS purchase_month,
       o.order_delivered_customer_date,
       o.order_estimated_delivery_date,
       COALESCE(i.order_item_rows, 0) AS order_item_rows,
       COALESCE(i.item_revenue, 0) AS item_revenue,
       COALESCE(i.freight_value, 0) AS freight_value,
       COALESCE(i.item_revenue, 0) + COALESCE(i.freight_value, 0) AS order_value,
       CASE
           WHEN o.order_delivered_customer_date IS NULL
             OR o.order_estimated_delivery_date IS NULL THEN NULL
           WHEN date(o.order_delivered_customer_date)
                <= date(o.order_estimated_delivery_date) THEN 1
           ELSE 0
       END AS is_on_time,
       CASE
           WHEN o.order_delivered_customer_date IS NULL
             OR o.order_estimated_delivery_date IS NULL THEN 'Missing dates'
           WHEN date(o.order_delivered_customer_date)
                <= date(o.order_estimated_delivery_date) THEN 'On time'
           ELSE 'Late'
       END AS delivery_outcome,
       r.mean_review_score,
       r.scored_review_records
FROM stg_orders AS o
JOIN stg_customers AS c ON c.customer_id = o.customer_id
LEFT JOIN item_totals AS i ON i.order_id = o.order_id
LEFT JOIN review_scores AS r ON r.order_id = o.order_id
WHERE o.order_status = 'delivered';

CREATE VIEW vw_delivered_order_items AS
SELECT i.order_id,
       o.order_purchase_timestamp,
       strftime('%Y-%m', o.order_purchase_timestamp) AS purchase_month,
       c.customer_state,
       i.order_item_id,
       i.product_id,
       COALESCE(t.product_category_name_english,
                p.product_category_name,
                '(missing category)') AS product_category,
       p.product_category_name AS source_product_category,
       i.seller_id,
       s.seller_state,
       i.price,
       i.freight_value
FROM stg_order_items AS i
JOIN stg_orders AS o ON o.order_id = i.order_id
JOIN stg_customers AS c ON c.customer_id = o.customer_id
JOIN stg_products AS p ON p.product_id = i.product_id
JOIN stg_sellers AS s ON s.seller_id = i.seller_id
LEFT JOIN stg_category_translation AS t
       ON t.product_category_name = p.product_category_name
WHERE o.order_status = 'delivered';

CREATE VIEW vw_delivered_payments AS
SELECT p.order_id,
       p.payment_sequential,
       p.payment_type,
       p.payment_installments,
       p.payment_value
FROM stg_order_payments AS p
JOIN stg_orders AS o ON o.order_id = p.order_id
WHERE o.order_status = 'delivered';

CREATE VIEW vw_repeat_customer_summary AS
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
       1.0 * SUM(CASE WHEN delivered_order_count >= 2 THEN 1 ELSE 0 END)
           / NULLIF(COUNT(*), 0) AS repeat_customer_rate
FROM delivered_orders_by_customer;

CREATE VIEW vw_delivery_review_summary AS
SELECT CASE WHEN is_on_time = 1 THEN 'on_time' ELSE 'late' END AS delivery_outcome,
       COUNT(*) AS reviewed_delivered_orders,
       AVG(mean_review_score) AS mean_order_review_score,
       SUM(scored_review_records) AS source_review_records
FROM vw_delivered_orders
WHERE is_on_time IS NOT NULL
  AND mean_review_score IS NOT NULL
GROUP BY delivery_outcome;
