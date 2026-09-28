# E-commerce Data Quality Exercise

You have received customer, product and order data exported from an e-commerce system. Before the reporting team can use it, the data needs to be investigated, cleaned and validated. Working out what the data contains, and what is wrong with it, is the job.

## Files

- `data/practice/`: the three CSV exports
- `sql/01_create_tables.sql`: creates a `raw` schema with one table per file, every column as TEXT so the files load as they are
- `sql/02_check_load.sql`: row counts to confirm the load

## Getting started

1. Create a database called `ecommerce` in your local PostgreSQL.
2. In DBeaver, run `sql/01_create_tables.sql` against it.
3. Import each CSV into its `raw` table using DBeaver's data import.
4. Run `sql/02_check_load.sql`. Expect 510 customers, 52 products and 2,030 orders.

## Objectives

1. Understand the datasets: what each one represents, their keys, and how they relate.
2. Profile the data.
3. Identify data quality issues.
4. Document the issues found.
5. Decide how each issue should be handled.
6. Produce cleaned tables in a `clean` schema.
7. Validate the cleaned tables.
8. Document the process.

Then, using only the clean tables, calculate: total orders, total revenue, average order value, revenue by category, orders by month, top 10 products, and top 10 customers by revenue.

## Deliverables

Your SQL scripts in `sql/`, an issues log, and a short write-up of your decisions. Work on a branch and open a pull request for review.
