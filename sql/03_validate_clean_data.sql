
-- ============================================================
-- E-COMMERCE DATA QUALITY PROJECT
-- 03_validate_clean_data.sql
--
-- Validates approved data in the clean schema.
-- All queries are read-only.
-- ============================================================


-- ============================================================
-- CHECK 1: RAW AND CLEAN ROW COUNTS
-- ============================================================

SELECT
    'customers' AS table_name,
    (SELECT COUNT(*) FROM raw.customers) AS raw_rows,
    (SELECT COUNT(*) FROM clean.customers) AS clean_rows

UNION ALL

SELECT
    'products',
    (SELECT COUNT(*) FROM raw.products),
    (SELECT COUNT(*) FROM clean.products)

UNION ALL

SELECT
    'orders',
    (SELECT COUNT(*) FROM raw.orders),
    (SELECT COUNT(*) FROM clean.orders)

UNION ALL

SELECT
    'addresses',
    (SELECT COUNT(*) FROM raw.addresses),
    (SELECT COUNT(*) FROM clean.addresses);


-- ============================================================
-- CHECK 2: DUPLICATE PRIMARY KEYS
-- Expected: 0 for all tables
-- ============================================================

SELECT
    'customers' AS table_name,
    COUNT(*) - COUNT(DISTINCT customer_id) AS duplicate_ids
FROM clean.customers

UNION ALL

SELECT
    'products',
    COUNT(*) - COUNT(DISTINCT product_id)
FROM clean.products

UNION ALL

SELECT
    'orders',
    COUNT(*) - COUNT(DISTINCT order_id)
FROM clean.orders

UNION ALL

SELECT
    'addresses',
    COUNT(*) - COUNT(DISTINCT address_id)
FROM clean.addresses;


-- ============================================================
-- CHECK 3: INVALID FOREIGN KEY REFERENCES
-- Expected: 0 for all checks
-- ============================================================

SELECT
    'Orders with invalid customer IDs' AS check_name,
    COUNT(*) AS invalid_records
FROM clean.orders o
LEFT JOIN clean.customers c
    ON o.customer_id = c.customer_id
WHERE c.customer_id IS NULL

UNION ALL

SELECT
    'Orders with invalid product IDs',
    COUNT(*)
FROM clean.orders o
LEFT JOIN clean.products p
    ON o.product_id = p.product_id
WHERE p.product_id IS NULL

UNION ALL

SELECT
    'Addresses with invalid customer IDs',
    COUNT(*)
FROM clean.addresses a
LEFT JOIN clean.customers c
    ON a.customer_id = c.customer_id
WHERE c.customer_id IS NULL;


-- ============================================================
-- CHECK 4: MISSING REQUIRED VALUES
-- Expected: 0 for all tables
-- ============================================================

SELECT
    'customers' AS table_name,
    COUNT(*) FILTER (
        WHERE customer_id IS NULL
           OR TRIM(customer_id) = ''
           OR signup_date IS NULL
    ) AS missing_required_values
FROM clean.customers

UNION ALL

SELECT
    'products',
    COUNT(*) FILTER (
        WHERE product_id IS NULL
           OR TRIM(product_id) = ''
           OR unit_price IS NULL
    )
FROM clean.products

UNION ALL

SELECT
    'orders',
    COUNT(*) FILTER (
        WHERE order_id IS NULL
           OR TRIM(order_id) = ''
           OR customer_id IS NULL
           OR product_id IS NULL
           OR order_date IS NULL
           OR quantity IS NULL
           OR unit_price IS NULL
    )
FROM clean.orders

UNION ALL

SELECT
    'addresses',
    COUNT(*) FILTER (
        WHERE address_id IS NULL
           OR TRIM(address_id) = ''
           OR customer_id IS NULL
    )
FROM clean.addresses;


-- ============================================================
-- CHECK 5: INVALID PRODUCT PRICES AND ORDER VALUES
-- Expected: 0 for all checks
-- ============================================================

SELECT
    'Products with invalid prices' AS check_name,
    COUNT(*) AS invalid_records
FROM clean.products
WHERE unit_price <= 0
   OR unit_price IS NULL

UNION ALL

SELECT
    'Orders with invalid quantities',
    COUNT(*)
FROM clean.orders
WHERE quantity <= 0
   OR quantity IS NULL

UNION ALL

SELECT
    'Orders with invalid unit prices',
    COUNT(*)
FROM clean.orders
WHERE unit_price <= 0
   OR unit_price IS NULL;


-- ============================================================
-- CHECK 6: UNAPPROVED PAYMENT METHODS AND ORDER STATUSES
-- Expected: 0 for both checks
-- ============================================================

SELECT
    'Unapproved payment methods' AS check_name,
    COUNT(*) AS invalid_records
FROM clean.orders
WHERE payment_method IS NULL
   OR payment_method NOT IN (
       'Credit Card',
       'Debit Card',
       'PayPal',
       'Apple Pay',
       'Klarna',
       'Gift Card',
       'Google Pay',
       'Bank Transfer',
       'Cash on Delivery'
   )

UNION ALL

SELECT
    'Unapproved order statuses',
    COUNT(*)
FROM clean.orders
WHERE order_status IS NULL
   OR order_status NOT IN (
       'Pending',
       'Processing',
       'Shipped',
       'Delivered',
       'Cancelled',
       'Refunded',
       'Returned'
   );


-- ============================================================
-- CHECK 7: PRODUCT CATEGORY DISTRIBUTION
-- Expected: 9 categories, 47 products total
-- ============================================================

SELECT
    category,
    COUNT(*) AS product_count
FROM clean.products
GROUP BY category
ORDER BY category;


-- ============================================================
-- CHECK 8: CLEAN DATA SUMMARY
-- Expected: 2841 clean records
-- ============================================================

SELECT
    (SELECT COUNT(*) FROM clean.customers)
        AS clean_customers,
    (SELECT COUNT(*) FROM clean.products)
        AS clean_products,
    (SELECT COUNT(*) FROM clean.orders)
        AS clean_orders,
    (SELECT COUNT(*) FROM clean.addresses)
        AS clean_addresses,
    (
        (SELECT COUNT(*) FROM clean.customers)
        + (SELECT COUNT(*) FROM clean.products)
        + (SELECT COUNT(*) FROM clean.orders)
        + (SELECT COUNT(*) FROM clean.addresses)
    ) AS total_clean_records;


-- ============================================================
-- END OF VALIDATION SCRIPT
-- ============================================================

