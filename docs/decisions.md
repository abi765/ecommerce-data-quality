# Phase 1 — Decisions Made and Work Completed

## Project overview

Phase 1 of the e-commerce data quality project focused on profiling, cleaning, loading, validating and analysing customer, product, order and address records. The original source data was retained in PostgreSQL's `raw` schema. Cleaned records were loaded into the separate `clean` schema.

## Cleaning results

| Dataset | Raw records | Clean records | Rejected | Needs review |
| --- | ---: | ---: | ---: | ---: |
| Customers | 510 | 495 | 15 | 0 |
| Products | 52 | 47 | 2 | 3 |
| Orders | 2,030 | 1,715 | 96 | 219 |
| Addresses | 610 | 584 | 16 | 10 |
| **Total** | **3,202** | **2,841** | **129** | **232** |

The totals reconciled: each raw record was assigned to the clean, rejected or needs-review output.

## Decisions made during Phase 1

### 1. Original data was preserved
The source records were retained in the `raw` schema rather than overwritten. This preserved the original values for comparison and investigation.

### 2. Records were separated by cleaning outcome
The cleaning script (`python/03_clean_data.py`) produced separate CSV outputs for clean, rejected and needs-review records in `data/processed/`. Only clean records were loaded into PostgreSQL's `clean` schema using `python/04_load_clean_data.py`.

### 3. Customer records without IDs were rejected
A SQL check found **3 records** in `raw.customers` with missing or blank `customer_id` values. The cleaning rule rejected records without a customer ID rather than generating an unverified identifier. These 3 records were part of the **15 rejected customer records**, not additional rejections. The presence of the three specific records in the exported rejected CSV has not been independently checked.

### 4. Uncertain records were kept for review
Records that required human judgement were separated into `needs_review` instead of being treated as approved. This included **3 products, 219 orders and 10 addresses**.

### 5. Two future-dated orders were held for review
Orders `ORD-00070` and `ORD-00763`, dated in **2035**, were classified as `needs_review` and excluded from the approved orders. These two records were already included in the **219 orders needing review**.

### 6. Cleaned data was loaded and validated
The approved CSV outputs were loaded into the `clean` schema. Row counts were checked against the expected cleaning results. SQL validation checked clean tables, keys, required fields, references and selected business rules.

### 7. Business analysis used only approved data
The final analysis in `sql/04_business_analysis.sql` used the `clean` tables. The verified results were:

| Measure | Result |
| --- | ---: |
| Approved orders | 1,715 |
| Recorded order value | 133,028.81 |
| Average recorded order value | 77.57 |
| Difference between overall and category totals | 0 |

Recorded order value was calculated as `quantity * unit_price`. It was **not described as verified net revenue**, because approved records may include cancelled, refunded or returned orders. No currency was assumed.

### 8. Project SQL files were kept as the final versions
The four organised SQL files in the project's `sql/` folder were retained as the main project scripts. Separate numbered DBeaver scripts were treated as investigation and working history, not as additional GitHub deliverables.

## Documentation and remaining limitations

The issues log records verified overall counts and specific findings. Detailed reasons for every rejected or needs-review record were **not individually verified** against all exported exception CSVs; therefore, no unsupported issue-level counts were added here.

Phase 2 work involving PostGIS and QGIS had **not** been started as part of these Phase 1 results.
