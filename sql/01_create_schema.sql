PRAGMA foreign_keys = ON;

CREATE TABLE stg_customers (
    customer_id TEXT PRIMARY KEY,
    customer_unique_id TEXT NOT NULL,
    customer_zip_code_prefix TEXT,
    customer_city TEXT,
    customer_state TEXT
);

CREATE TABLE stg_geolocation (
    geolocation_record_id INTEGER PRIMARY KEY,
    geolocation_zip_code_prefix TEXT,
    geolocation_lat REAL,
    geolocation_lng REAL,
    geolocation_city TEXT,
    geolocation_state TEXT
);

CREATE TABLE stg_products (
    product_id TEXT PRIMARY KEY,
    product_category_name TEXT,
    product_name_lenght INTEGER,
    product_description_lenght INTEGER,
    product_photos_qty INTEGER,
    product_weight_g REAL,
    product_length_cm REAL,
    product_height_cm REAL,
    product_width_cm REAL
);

CREATE TABLE stg_sellers (
    seller_id TEXT PRIMARY KEY,
    seller_zip_code_prefix TEXT,
    seller_city TEXT,
    seller_state TEXT
);

CREATE TABLE stg_category_translation (
    product_category_name TEXT PRIMARY KEY,
    product_category_name_english TEXT NOT NULL
);

CREATE TABLE stg_orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT NOT NULL,
    order_status TEXT NOT NULL,
    order_purchase_timestamp TEXT NOT NULL,
    order_approved_at TEXT,
    order_delivered_carrier_date TEXT,
    order_delivered_customer_date TEXT,
    order_estimated_delivery_date TEXT,
    FOREIGN KEY (customer_id) REFERENCES stg_customers (customer_id)
);

CREATE TABLE stg_order_items (
    order_id TEXT NOT NULL,
    order_item_id INTEGER NOT NULL,
    product_id TEXT NOT NULL,
    seller_id TEXT NOT NULL,
    shipping_limit_date TEXT,
    price REAL NOT NULL,
    freight_value REAL NOT NULL,
    PRIMARY KEY (order_id, order_item_id),
    FOREIGN KEY (order_id) REFERENCES stg_orders (order_id),
    FOREIGN KEY (product_id) REFERENCES stg_products (product_id),
    FOREIGN KEY (seller_id) REFERENCES stg_sellers (seller_id)
);

CREATE TABLE stg_order_payments (
    order_id TEXT NOT NULL,
    payment_sequential INTEGER NOT NULL,
    payment_type TEXT NOT NULL,
    payment_installments INTEGER NOT NULL,
    payment_value REAL NOT NULL,
    PRIMARY KEY (order_id, payment_sequential),
    FOREIGN KEY (order_id) REFERENCES stg_orders (order_id)
);

CREATE TABLE stg_order_reviews (
    review_record_id INTEGER PRIMARY KEY,
    review_id TEXT,
    order_id TEXT NOT NULL,
    review_score INTEGER,
    review_comment_title TEXT,
    review_comment_message TEXT,
    review_creation_date TEXT,
    review_answer_timestamp TEXT,
    FOREIGN KEY (order_id) REFERENCES stg_orders (order_id)
);

CREATE INDEX idx_orders_customer_id ON stg_orders (customer_id);
CREATE INDEX idx_order_items_product_id ON stg_order_items (product_id);
CREATE INDEX idx_order_items_seller_id ON stg_order_items (seller_id);
CREATE INDEX idx_order_payments_order_id ON stg_order_payments (order_id);
CREATE INDEX idx_order_reviews_order_id ON stg_order_reviews (order_id);
