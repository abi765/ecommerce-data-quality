CREATE SCHEMA IF NOT EXISTS rejects;

CREATE TABLE IF NOT EXISTS rejects.customers
(LIKE raw.customers INCLUDING ALL);

ALTER TABLE rejects.customers
ADD COLUMN IF NOT EXISTS reject_reason TEXT;

CREATE TABLE IF NOT EXISTS rejects.products
(LIKE raw.products INCLUDING ALL);

ALTER TABLE rejects.products
ADD COLUMN IF NOT EXISTS reject_reason TEXT;

CREATE TABLE IF NOT EXISTS rejects.orders
(LIKE raw.orders INCLUDING ALL);

ALTER TABLE rejects.orders
ADD COLUMN IF NOT EXISTS reject_reason TEXT;