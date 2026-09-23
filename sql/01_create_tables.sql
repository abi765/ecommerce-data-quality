SET client_min_messages = WARNING;

CREATE SCHEMA IF NOT EXISTS raw;

DROP TABLE IF EXISTS raw.customers;
CREATE TABLE raw.customers (
    customer_id     TEXT,
    first_name      TEXT,
    last_name       TEXT,
    email           TEXT,
    address_line_1  TEXT,
    city            TEXT,
    postcode        TEXT,
    country         TEXT,
    signup_date     TEXT
);

DROP TABLE IF EXISTS raw.products;
CREATE TABLE raw.products (
    product_id      TEXT,
    product_name    TEXT,
    category        TEXT,
    brand           TEXT,
    unit_price      TEXT
);

DROP TABLE IF EXISTS raw.orders;
CREATE TABLE raw.orders (
    order_id        TEXT,
    customer_id     TEXT,
    product_id      TEXT,
    order_date      TEXT,
    quantity        TEXT,
    unit_price      TEXT,
    payment_method  TEXT,
    order_status    TEXT
);
