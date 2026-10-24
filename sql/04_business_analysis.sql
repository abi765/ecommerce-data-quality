
-- ============================================================
-- E-COMMERCE DATA QUALITY PROJECT
-- 04_business_analysis.sql
--
-- Business analysis using APPROVED clean data only.
--
-- IMPORTANT:
-- Recorded order value = quantity * unit_price.
-- This includes all approved order statuses, including
-- Cancelled, Refunded and Returned.
-- Therefore, it is NOT necessarily net sales revenue.
--
-- No currency is assumed.
-- All queries are read-only.
-- ============================================================


-- ============================================================
-- QUERY 1: OVERALL E-COMMERCE KPIs
-- ============================================================

SELECT
    COUNT(*) AS total_orders,
    ROUND(
        SUM(quantity * unit_price),
        2
    ) AS total_order_value,
    ROUND(
        AVG(quantity * unit_price),
        2
    ) AS average_order_value,
    COUNT(DISTINCT customer_id) AS unique_customers,
    COUNT(DISTINCT product_id) AS products_ordered,
    SUM(quantity) AS total_units_ordered
FROM clean.orders;


-- ============================================================
-- QUERY 2: ORDER VALUE BY PRODUCT CATEGORY
-- ============================================================

SELECT
    p.category,
    COUNT(*) AS total_orders,
    SUM(o.quantity) AS units_ordered,
    ROUND(
        SUM(o.quantity * o.unit_price),
        2
    ) AS total_order_value
FROM clean.orders o
JOIN clean.products p
    ON o.product_id = p.product_id
GROUP BY p.category
ORDER BY total_order_value DESC;


-- ============================================================
-- QUERY 3: MONTHLY ORDERS AND ORDER VALUE
-- ============================================================

SELECT
    TO_CHAR(order_date, 'YYYY-MM') AS order_month,
    COUNT(*) AS total_orders,
    SUM(quantity) AS units_ordered,
    ROUND(
        SUM(quantity * unit_price),
        2
    ) AS total_order_value,
    ROUND(
        AVG(quantity * unit_price),
        2
    ) AS average_order_value
FROM clean.orders
GROUP BY TO_CHAR(order_date, 'YYYY-MM')
ORDER BY order_month;


-- ============================================================
-- QUERY 4: TOP 10 PRODUCTS BY ORDER VALUE
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category,
    COUNT(*) AS total_orders,
    SUM(o.quantity) AS units_sold,
    ROUND(
        SUM(o.quantity * o.unit_price),
        2
    ) AS total_order_value
FROM clean.orders o
JOIN clean.products p
    ON o.product_id = p.product_id
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY
    total_order_value DESC,
    p.product_id
LIMIT 10;


-- ============================================================
-- QUERY 5: TOP 10 CUSTOMERS BY ORDER VALUE
-- ============================================================

SELECT
    c.customer_id,
    c.first_name,
    c.last_name,
    c.country,
    COUNT(*) AS total_orders,
    ROUND(
        SUM(o.quantity * o.unit_price),
        2
    ) AS total_order_value
FROM clean.orders o
JOIN clean.customers c
    ON o.customer_id = c.customer_id
GROUP BY
    c.customer_id,
    c.first_name,
    c.last_name,
    c.country
ORDER BY
    total_order_value DESC,
    c.customer_id
LIMIT 10;


-- ============================================================
-- QUERY 6: ORDERS BY ORDER STATUS
-- ============================================================

SELECT
    order_status,
    COUNT(*) AS total_orders,
    ROUND(
        SUM(quantity * unit_price),
        2
    ) AS total_order_value
FROM clean.orders
GROUP BY order_status
ORDER BY total_orders DESC;


-- ============================================================
-- QUERY 7: ORDERS BY PAYMENT METHOD
-- ============================================================

SELECT
    payment_method,
    COUNT(*) AS total_orders,
    ROUND(
        SUM(quantity * unit_price),
        2
    ) AS total_order_value
FROM clean.orders
GROUP BY payment_method
ORDER BY total_orders DESC;


-- ============================================================
-- QUERY 8: ORDER VALUE BY CUSTOMER COUNTRY
-- ============================================================

SELECT
    c.country,
    COUNT(*) AS total_orders,
    COUNT(DISTINCT c.customer_id) AS unique_customers,
    ROUND(
        SUM(o.quantity * o.unit_price),
        2
    ) AS total_order_value
FROM clean.orders o
JOIN clean.customers c
    ON o.customer_id = c.customer_id
GROUP BY c.country
ORDER BY total_order_value DESC;


-- ============================================================
-- QUERY 9: TOP 10 CITIES BY ORDER VALUE
--
-- Uses the city stored in clean.customers.
-- This is customer-location analysis, not necessarily
-- shipping-destination analysis.
-- ============================================================

SELECT
    c.city,
    c.country,
    COUNT(*) AS total_orders,
    COUNT(DISTINCT c.customer_id) AS unique_customers,
    ROUND(
        SUM(o.quantity * o.unit_price),
        2
    ) AS total_order_value
FROM clean.orders o
JOIN clean.customers c
    ON o.customer_id = c.customer_id
GROUP BY
    c.city,
    c.country
ORDER BY total_order_value DESC
LIMIT 10;


-- ============================================================
-- QUERY 10: TOP 10 PRODUCTS BY UNITS ORDERED
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category,
    SUM(o.quantity) AS units_ordered,
    COUNT(*) AS total_orders,
    ROUND(
        SUM(o.quantity * o.unit_price),
        2
    ) AS total_order_value
FROM clean.orders o
JOIN clean.products p
    ON o.product_id = p.product_id
GROUP BY
    p.product_id,
    p.product_name,
    p.category
ORDER BY
    units_ordered DESC,
    p.product_id
LIMIT 10;


-- ============================================================
-- QUERY 11: MONTHLY ORDER VALUE BY ORDER STATUS
--
-- Useful for distinguishing Delivered, Cancelled,
-- Refunded and other statuses over time.
-- ============================================================

SELECT
    TO_CHAR(order_date, 'YYYY-MM') AS order_month,
    order_status,
    COUNT(*) AS total_orders,
    ROUND(
        SUM(quantity * unit_price),
        2
    ) AS total_order_value
FROM clean.orders
GROUP BY
    TO_CHAR(order_date, 'YYYY-MM'),
    order_status
ORDER BY
    order_month,
    order_status;


-- ============================================================
-- QUERY 12: DELIVERED ORDERS ONLY
--
-- This is a more restricted metric than total recorded
-- order value, but still not verified net revenue.
-- ============================================================

SELECT
    COUNT(*) AS delivered_orders,
    ROUND(
        SUM(quantity * unit_price),
        2
    ) AS delivered_order_value,
    ROUND(
        AVG(quantity * unit_price),
        2
    ) AS average_delivered_order_value
FROM clean.orders
WHERE order_status = 'Delivered';


-- ============================================================
-- QUERY 13: PRODUCTS WITH NO APPROVED ORDERS
--
-- Identifies approved products that are not referenced
-- by any approved order.
-- ============================================================

SELECT
    p.product_id,
    p.product_name,
    p.category,
    p.unit_price
FROM clean.products p
LEFT JOIN clean.orders o
    ON p.product_id = o.product_id
WHERE o.order_id IS NULL
ORDER BY p.product_id;


-- ============================================================
-- QUERY 14: RECONCILE CATEGORY TOTALS WITH OVERALL KPIs
--
-- Expected:
-- 1715 orders
-- 133028.81 recorded order value
-- 0 order difference
-- 0.00 value difference
-- ============================================================

WITH overall AS (
    SELECT
        COUNT(*) AS total_orders,
        SUM(quantity * unit_price) AS total_order_value
    FROM clean.orders
),
category_totals AS (
    SELECT
        COUNT(*) AS total_orders,
        SUM(o.quantity * o.unit_price) AS total_order_value
    FROM clean.orders o
    JOIN clean.products p
        ON o.product_id = p.product_id
)
SELECT
    overall.total_orders AS overall_orders,
    category_totals.total_orders AS category_orders,
    overall.total_orders
        - category_totals.total_orders AS order_difference,
    ROUND(
        overall.total_order_value,
        2
    ) AS overall_order_value,
    ROUND(
        category_totals.total_order_value,
        2
    ) AS category_order_value,
    ROUND(
        overall.total_order_value
        - category_totals.total_order_value,
        2
    ) AS value_difference
FROM overall
CROSS JOIN category_totals;


-- ============================================================
-- END OF BUSINESS ANALYSIS
-- ============================================================
