
CREATE SCHEMA IF NOT EXISTS clean;

CREATE TABLE IF NOT EXISTS clean.customers (
    customer_id TEXT PRIMARY KEY,
    first_name TEXT,
    last_name TEXT,
    email TEXT,
    address_line_1 TEXT,
    city TEXT,
    postcode TEXT,
    country TEXT,
    signup_date DATE
);

CREATE TABLE IF NOT EXISTS clean.products (
    product_id TEXT PRIMARY KEY,
    product_name TEXT,
    category TEXT,
    brand TEXT,
    unit_price NUMERIC
);

CREATE TABLE IF NOT EXISTS clean.orders (
    order_id TEXT PRIMARY KEY,
    customer_id TEXT,
    product_id TEXT,
    order_date DATE,
    quantity INTEGER,
    unit_price NUMERIC,
    payment_method TEXT,
    order_status TEXT
);

CREATE TABLE IF NOT EXISTS clean.addresses (
    address_id TEXT PRIMARY KEY,
    customer_id TEXT,
    address_type TEXT,
    address_line_1 TEXT,
    city TEXT,
    postcode TEXT,
    country TEXT,
    latitude NUMERIC,
    longitude NUMERIC
);
