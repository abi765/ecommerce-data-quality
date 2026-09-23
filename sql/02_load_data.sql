\copy raw.customers FROM 'data/practice/customers.csv' WITH (FORMAT csv, HEADER true)
\copy raw.products  FROM 'data/practice/products.csv'  WITH (FORMAT csv, HEADER true)
\copy raw.orders    FROM 'data/practice/orders.csv'    WITH (FORMAT csv, HEADER true)
