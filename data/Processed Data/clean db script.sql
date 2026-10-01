SET client_min_messages = WARNING;

CREATE SCHEMA IF NOT EXISTS clean;


DROP TABLE IF EXISTS clean.orders;
DROP TABLE IF EXISTS clean.products;
DROP TABLE IF EXISTS clean.customers;


CREATE TABLE clean.customers (
    customer_id     VARCHAR(50)   NOT NULL,
    first_name      VARCHAR(100)  NOT NULL,
    last_name       VARCHAR(100)  NOT NULL,
    email           VARCHAR(255)  NOT NULL,
    address_line_1  VARCHAR(255),
    city            VARCHAR(100),
    postcode        VARCHAR(20),
    country         VARCHAR(100),
    signup_date     DATE,
    CONSTRAINT pk_customers PRIMARY KEY (customer_id),
    CONSTRAINT chk_customers_email CHECK (email LIKE '%_@_%.__%')
);


CREATE UNIQUE INDEX uq_customers_email ON clean.customers (LOWER(email));

CREATE TABLE clean.products (
    product_id      VARCHAR(50)    NOT NULL,
    product_name    VARCHAR(255)   NOT NULL,
    category        VARCHAR(100),
    brand           VARCHAR(100),
    unit_price      NUMERIC(12,2)  NOT NULL,
    CONSTRAINT pk_products PRIMARY KEY (product_id),
    CONSTRAINT chk_products_unit_price CHECK (unit_price >= 0)
);

CREATE TABLE clean.orders (
    order_id        VARCHAR(50)    NOT NULL,
    customer_id     VARCHAR(50)    NOT NULL,
    product_id      VARCHAR(50)    NOT NULL,
    order_date      DATE           NOT NULL,
    quantity        INTEGER        NOT NULL,
    unit_price      NUMERIC(12,2)  NOT NULL,  -- price at time of order
    payment_method  VARCHAR(50),
    order_status    VARCHAR(50)    NOT NULL,
    CONSTRAINT pk_orders PRIMARY KEY (order_id),
    CONSTRAINT fk_orders_customer FOREIGN KEY (customer_id)
        REFERENCES clean.customers (customer_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT fk_orders_product FOREIGN KEY (product_id)
        REFERENCES clean.products (product_id)
        ON UPDATE CASCADE ON DELETE RESTRICT,
    CONSTRAINT chk_orders_quantity CHECK (quantity > 0),
    CONSTRAINT chk_orders_unit_price CHECK (unit_price >= 0)
);

