# Phase 1 — Data Cleaning, Validation and Analysis Decisions

## 1. Project Overview

Phase 1 focused on understanding, profiling, cleaning, validating and analysing the e-commerce datasets: customers, products and orders.

The original records were retained in the PostgreSQL `raw` schema. The cleaning process classified records as `clean`, `rejected` or `needs_review`. Approved records were loaded into the PostgreSQL `clean` schema, while rejected Phase 1 records were loaded into the `rejects` schema.

The addresses dataset was also processed during the initial cleaning work. However, detailed address validation, geospatial processing and mapping remain part of Phase 2.

## 2. Data Cleaning Results

| Dataset | Raw | Clean | Rejected | Needs Review |
|---|---:|---:|---:|---:|
| Customers | 510 | 495 | 15 | 0 |
| Products | 52 | 47 | 2 | 3 |
| Orders | 2,030 | 1,715 | 96 | 219 |
| Addresses | 610 | 584 | 16 | 10 |
| **Total** | **3,202** | **2,841** | **129** | **232** |

These figures represent the recorded outputs of the current cleaning pipeline.

The 2,841 approved records were verified in the PostgreSQL `clean` schema.

Of the 129 rejected records across all four datasets, 113 belong to the Phase 1 datasets and have been loaded into PostgreSQL rejects tables. The remaining 16 rejected address records belong to Phase 2.

## 3. Cleaning Decisions and Rationale

### Preserve original data

The original source records were retained in the PostgreSQL `raw` schema.

Cleaning was performed separately to avoid modifying the original datasets and to allow results to be checked against their source.

### Separate clean, rejected and review records

Records were classified into three groups:

- **Clean:** Records accepted by the cleaning rules and eligible for loading into the clean tables.
- **Rejected:** Records that failed required validation checks and were excluded from the clean tables.
- **Needs review:** Records containing uncertainty or issues that should not be automatically corrected.

Separate CSV files were generated for these categories.

Approved records were loaded into the `clean` schema, and rejected Phase 1 records were loaded into the `rejects` schema.

Records requiring review were retained separately rather than automatically accepted or deleted.

### Customer records

Of 510 customer records, 495 were classified as clean and 15 were rejected.

Three records had missing or blank customer identifiers and were included in the rejected total.

Missing customer identifiers were not invented because they are required for reliable record identification and relationships.

The 15 rejected customer records were loaded into `rejects.customers`.

### Product records

Of 52 product records, 47 were classified as clean, 2 were rejected and 3 were held for review.

The cleaning process included category normalisation and specific approved category corrections.

Records with unresolved product information were not automatically accepted.

The 2 rejected product records were loaded into `rejects.products`.

### Order records

Of 2,030 order records, 1,715 were classified as clean, 96 were rejected and 219 were held for review.

The cleaning rules checked required identifiers, customer and product relationships, order dates, quantities, prices, statuses and payment methods.

Two orders, `ORD-00070` and `ORD-00763`, had dates in 2035 and were held for review rather than automatically changed or deleted. These two orders are included in the 219 review records.

Orders linked to products requiring review were also kept out of the approved clean dataset.

The 96 rejected order records were loaded into `rejects.orders`.

### Address records

Of 610 address records, 584 were classified as clean, 16 were rejected and 10 were held for review by the current pipeline.

These are preliminary cleaning results.

Detailed address quality checks, spatial validation, PostGIS processing and QGIS mapping remain part of Phase 2.

The 16 rejected address records have not been included in the Phase 1 PostgreSQL rejects tables.

## 4. Data Loading and Validation

### Loading approved records

Approved records were loaded into the PostgreSQL `clean` schema using `python/04_load_clean_data.py`.

The following clean record counts were verified:

| PostgreSQL table | Records |
|---|---:|
| `clean.customers` | 495 |
| `clean.products` | 47 |
| `clean.orders` | 1,715 |
| `clean.addresses` | 584 |
| **Total** | **2,841** |

The clean-data loading script checks expected record counts and verifies that the CSV columns match the PostgreSQL table structures.

### Loading rejected records

A separate PostgreSQL schema named `rejects` was created to store rejected Phase 1 records.

The SQL script `sql/05_create_rejects_tables.sql` defines the rejected-data tables and adds a `reject_reason` column.

The Python script `python/05_load_rejected_data.py` loads rejected records from the processed CSV files into PostgreSQL.

The following counts were verified directly in DBeaver:

| PostgreSQL table | Rejected records |
|---|---:|
| `rejects.customers` | 15 |
| `rejects.products` | 2 |
| `rejects.orders` | 96 |
| **Total** | **113** |

The loading script checks expected counts, column compatibility and rejection reasons. It also prevents importing into non-empty rejects tables, reducing the risk of duplicate imports.

### SQL validation

The SQL validation script `sql/03_validate_clean_data.sql` was prepared to assess:

- Record counts
- Key uniqueness
- Customer and product relationships
- Missing values
- Relevant data-quality rules

The recorded total of approved clean records is 2,841.

### Table creation and reproducibility

The SQL script `sql/06_create_clean_tables.sql` was added to define the clean schema and its four tables.

The existing PostgreSQL primary-key constraints were inspected and compared with the script.

However, the full workflow has not yet been tested from an empty database. Therefore, complete reproducibility is not yet claimed.

## 5. Business Analysis

Business analysis queries were prepared using the approved records in the PostgreSQL `clean` schema.

The recorded results include:

- **Total orders:** 1,715
- **Total recorded order value:** 133,028.81
- **Average recorded order value:** Approximately 77.57

The analysis also includes:

- Recorded order value by product category
- Orders by month
- Top products
- Top customers

The value calculated from order quantities and unit prices is described as **recorded order value**, rather than confirmed net revenue.

The current calculation does not establish adjustments for cancellations, refunds or returns, and the currency has not been independently confirmed.

These business figures are recorded analysis results and should be verified again if the underlying cleaned data or analysis queries change.

## 6. Issue Documentation

The `docs/issues_log.csv` file documents data-quality issues identified during the cleaning process.

The log records affected datasets, columns, issue counts and handling decisions.

Some records may contain multiple data-quality issues. Therefore, individual issue counts may overlap and should not be added together to calculate the number of rejected or review records.

The issues log and this decisions document provide supporting evidence for the cleaning and validation work.

## 7. Limitations and Outstanding Work

- The cleaning decisions reflect the rules currently implemented in the Python pipeline.
- Records held for review have not been assumed to be correct.
- PostgreSQL rejects tables have been implemented and verified for the three Phase 1 datasets.
- Rejected address records and detailed address validation remain part of Phase 2.
- The full workflow has not yet been tested from an empty database.
- The recorded business analysis figures should be reverified if further code or data corrections are made.
- Address geospatial analysis, PostGIS processing and QGIS mapping remain Phase 2 work.

## 8. Next Steps

The remaining Phase 1 work is to:

1. Confirm that the necessary SQL and Python scripts are included in the GitHub repository.
2. Complete the outstanding reproducibility check without risking the existing verified database.
3. Review the final code and documentation changes in GitHub Pull Request #4.
4. Merge Pull Request #4 once the remaining Phase 1 requirements have been satisfied.

Detailed address validation and geospatial analysis will continue separately as Phase 2.