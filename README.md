# E-commerce Data Quality Exercise

You have received customer, product and order data exported from an e-commerce system. Before the reporting team can use it, the data needs to be investigated, cleaned and validated. Working out what the data contains, and what is wrong with it, is the job.

## Files

- `data/practice/`: the three CSV exports
- `sql/01_create_tables.sql`: creates a `raw` schema with one table per file, every column as TEXT so the files load as they are
- `sql/02_check_load.sql`: row counts to confirm the load
- `docs/issues_log.csv`: empty template for the issues log

## Getting started

1. Create a database called `ecommerce` in your local PostgreSQL.
2. In DBeaver, run `sql/01_create_tables.sql` against it.
3. Import each CSV into its `raw` table using DBeaver's data import.
4. Run `sql/02_check_load.sql`. Expect 510 customers, 52 products and 2,030 orders.
5. Optional: for Python, create a virtual environment and run `pip install -r requirements.txt`.

## Git workflow

1. Pull `main` before starting.
2. Create a branch for the task.
3. Commit with one-sentence messages.
4. Push and open a pull request against `main`.
5. Address review comments with new commits on the same branch.
6. After merge, pull `main` and delete the branch.

## Phase 1: clean the data

1. Understand the datasets: what each one represents, their keys, and how they relate.
2. Profile the data.
3. Identify data quality issues and document them.
4. Decide how each issue should be handled.
5. Build the cleaned tables in a `clean` schema. Never modify `raw`. Rows that cannot be cleaned are not deleted: your code moves them to a rejects table (the original columns plus a `reject_reason` column), one per source table.
6. Validate the cleaned tables.
7. Using only the clean tables, calculate: total orders, total revenue, average order value, revenue by category, orders by month, top 10 products, and top 10 customers by revenue.

Deliverables, in one pull request:

- Your cleaning, validation and analysis code in `sql/` or `python/`. SQL, Python or both. Reproducible means: the clean schema is dropped, your code is run from the top, and the same result comes out.
- `docs/issues_log.csv`: one row per issue. Example row:

      table,column,description,rows_affected,decision
      orders,quantity,missing value,5,moved to rejects

- `docs/decisions.md`: a short write-up covering what you found, what you decided and why, and what you were unsure about.

## Phase 2: addresses and mapping

Starts after phase 1 is merged. A fourth file, `data/practice/addresses.csv`, will be added with addresses and coordinates for customers.

1. Load, profile, clean and validate it the same way as phase 1, linked to `clean.customers`.
2. Install PostGIS and add a geometry column from the coordinates.
3. Connect QGIS to the database and add the addresses as a layer.
4. Map revenue by city using the clean orders.

Deliverables, in one pull request: the code, updated issues log and decisions, and a `maps/` folder with the QGIS project and one exported map.
