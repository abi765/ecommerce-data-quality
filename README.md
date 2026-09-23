# E-commerce Data Quality Exercise

## Scenario

You have received customer, product and order data exported from an e-commerce system. The reporting team wants to use it for sales analysis, but nobody has checked it yet. Your job is to load it into PostgreSQL, investigate it, clean it, and produce tables that can be trusted for reporting.

## Setup

1. Install PostgreSQL (postgresql.org, or `brew install postgresql@18` on a Mac) and check that `psql` runs.
2. From the project root run:

```
createdb ecommerce
psql -d ecommerce -f sql/01_create_tables.sql
psql -d ecommerce -f sql/02_load_data.sql
psql -d ecommerce -f sql/03_check_load.sql
```

3. The last command should report 510 customers, 52 products and 2,030 orders in the `raw` schema.

Every column in `raw` is loaded as TEXT on purpose. Exported data cannot be trusted to have the right types, and a typed load would either fail or silently lose rows. Working out the correct types is part of the job.

## What the source system says the data should look like

customers

| column | expected |
| --- | --- |
| customer_id | unique, format CUST-00001 |
| first_name, last_name | populated |
| email | unique, valid email address, lowercase |
| address_line_1, city, postcode | populated |
| country | full country name, for example United Kingdom |
| signup_date | date, YYYY-MM-DD |

products

| column | expected |
| --- | --- |
| product_id | unique, format PROD-0001 |
| product_name | populated |
| category | one of: Electronics, Home & Kitchen, Clothing, Sports & Outdoors, Books, Beauty & Personal Care, Toys & Games, Garden |
| brand | populated |
| unit_price | GBP, greater than 0 |

orders

| column | expected |
| --- | --- |
| order_id | unique, format ORD-00001 |
| customer_id | must exist in customers |
| product_id | must exist in products |
| order_date | date, YYYY-MM-DD, all orders were placed during 2025 |
| quantity | whole number, at least 1 |
| unit_price | GBP price at the time of the order |
| payment_method | one of: Credit Card, Debit Card, PayPal, Apple Pay, Klarna, Gift Card |
| order_status | one of: Pending, Processing, Shipped, Delivered, Cancelled, Refunded, Returned |

Treat this as documentation written by someone else: it tells you the intent, not what the files actually contain.

## Tasks

Work in this order. Each step should be SQL you can re-run from scratch.

1. Understand the data. What does each table represent? What are the primary keys? How do the tables relate? What type should each column really be?
2. Profile the data. For every column: row count, distinct count, NULL count, minimum and maximum, and the most common values. Look for duplicate rows and duplicate keys.
3. Investigate relationships. Confirm that every order points at a customer and a product that exist.
4. Clean the data. Create a `clean` schema with properly typed tables. For each problem you find, decide whether to fix it, exclude the row, or keep it and flag it. Write down every decision and why. Never change a value silently.
5. Validate the cleaned tables. Are keys unique? Are required fields populated? Are quantities, prices and dates valid? Are categories consistent? Do all references resolve?
6. Analyse. Using only the clean tables: total orders, total revenue, average order value, revenue by category, orders by month, top 10 products, top 10 customers by revenue.

## Deliverables

- Your own numbered SQL scripts (for example `sql/10_profile.sql`, `sql/20_clean.sql`, `sql/30_validate.sql`, `sql/40_analysis.sql`).
- An issues log: one line per problem found, with where it is, how you found it, and what you did about it.
- A short write-up (one page) of the approach, the decisions you made, and anything you would ask the source system team.

## Tips

- Do not edit the CSV files by hand. Every change belongs in SQL so it can be re-run and reviewed.
- Profile before you clean. Assume nothing about a column until you have looked at its values.
- Useful PostgreSQL tools: `COUNT(DISTINCT ...)`, `GROUP BY ... HAVING COUNT(*) > 1`, `LEFT JOIN ... WHERE ... IS NULL`, `TRIM`, `LOWER`, `INITCAP`, `NULLIF`, `CAST` or `::`, `TO_DATE`, regular expressions with `~`.
- Revenue for a single order line is quantity multiplied by unit_price. Decide, and document, which order statuses should count towards revenue.

## Stretch goals

1. Repeat the profiling and cleaning in Python with pandas and compare the results with your SQL.
2. Turn your validation queries into a reusable set of checks that return zero rows when the data is good.
3. Add automated tests (for example with pytest) that run those checks against the clean schema.

## Working with git

- Clone the repository and never work directly on `main`.
- Create a branch per task, for example `git checkout -b task-2-profiling`.
- Commit small, related changes with clear messages, and push the branch.
- Open a pull request for each task so it can be reviewed and discussed before it is merged.
- Do not commit the CSV files again, or any cleaned exports. The SQL that produces them is what gets reviewed.
