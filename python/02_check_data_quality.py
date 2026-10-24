
import pandas as pd

# ==================================================
# E-COMMERCE DATA QUALITY ASSESSMENT
# ==================================================
#
# Purpose:
# Identify and investigate data quality issues across
# the four source datasets:
#   1. Customers
#   2. Products
#   3. Orders
#   4. Addresses
#
# Project phases:
# Phase 1: Customers, Products, and Orders
# Phase 2: Addresses and geographical mapping
#
# Addresses are included in this investigation to
# provide a complete assessment of the source data.
# However, address cleaning and validation will be
# implemented separately during Phase 2.
#
# This script performs read-only checks.
# Original CSV files are never modified.
# ==================================================


# ==================================================
# 1. LOAD ORIGINAL CSV FILES
# ==================================================

DATA_PATH = "data/practice"

customers = pd.read_csv(
    f"{DATA_PATH}/customers.csv",
    dtype=str
)

products = pd.read_csv(
    f"{DATA_PATH}/products.csv",
    dtype=str
)

orders = pd.read_csv(
    f"{DATA_PATH}/orders.csv",
    dtype=str
)

addresses = pd.read_csv(
    f"{DATA_PATH}/addresses.csv",
    dtype=str
)


# ==================================================
# 2. STANDARDIZE VALUES FOR QUALITY CHECKS
# ==================================================

# Convert empty strings and whitespace-only values
# to missing values.
#
# These changes are made in memory only.

datasets = {
    "customers": customers,
    "products": products,
    "orders": orders,
    "addresses": addresses
}

for name, df in datasets.items():

    datasets[name] = df.replace(
        r"^\s*$",
        pd.NA,
        regex=True
    )

customers = datasets["customers"]
products = datasets["products"]
orders = datasets["orders"]
addresses = datasets["addresses"]


# ==================================================
# 3. STANDARDIZE ID SPACES FOR COMPARISON
# ==================================================

# Remove surrounding spaces from ID columns.
# This ensures that foreign key comparisons are
# not affected by accidental whitespace.
#
# Original CSV values remain unchanged.

id_columns = [
    "customer_id",
    "product_id",
    "order_id",
    "address_id"
]

for df in datasets.values():

    for column in id_columns:

        if column in df.columns:

            df[column] = df[column].str.strip()


# ==================================================
# 4. CHECK NON-EXISTENT CUSTOMER IDs IN ORDERS
# ==================================================

invalid_customers = orders[
    orders["customer_id"].notna()
    & ~orders["customer_id"].isin(
        customers["customer_id"].dropna()
    )
]

print("\nORDERS WITH NON-EXISTENT CUSTOMER IDs:")
print("Count:", len(invalid_customers))
print(invalid_customers.to_string(index=False))


# ==================================================
# 5. CHECK NON-EXISTENT PRODUCT IDs IN ORDERS
# ==================================================

invalid_products = orders[
    orders["product_id"].notna()
    & ~orders["product_id"].isin(
        products["product_id"].dropna()
    )
]

print("\nORDERS WITH NON-EXISTENT PRODUCT IDs:")
print("Count:", len(invalid_products))
print(invalid_products.to_string(index=False))


# ==================================================
# 6. CHECK NUMERIC VALUES IN ORDERS
# ==================================================

for column in ["quantity", "unit_price"]:

    numbers = pd.to_numeric(
        orders[column],
        errors="coerce"
    )

    print(f"\nORDERS: {column.upper()}")

    print(
        "Missing or non-numeric:",
        numbers.isna().sum()
    )

    print(
        "Zero or negative:",
        (numbers <= 0).sum()
    )


# ==================================================
# 7. CHECK PRODUCT PRICES
# ==================================================

product_prices = pd.to_numeric(
    products["unit_price"],
    errors="coerce"
)

print("\nPRODUCTS: UNIT PRICE")

print(
    "Missing or non-numeric:",
    product_prices.isna().sum()
)

print(
    "Zero or negative:",
    (product_prices <= 0).sum()
)


# ==================================================
# 8. INVESTIGATE INVALID ORDER QUANTITIES
# ==================================================

quantity = pd.to_numeric(
    orders["quantity"],
    errors="coerce"
)

invalid_quantity = orders[
    quantity.isna() | (quantity <= 0)
]

print("\nORDERS WITH INVALID QUANTITIES:")
print("Count:", len(invalid_quantity))
print(invalid_quantity.to_string(index=False))


# ==================================================
# 9. INVESTIGATE INVALID ORDER PRICES
# ==================================================

order_price = pd.to_numeric(
    orders["unit_price"],
    errors="coerce"
)

invalid_order_price = orders[
    order_price.isna() | (order_price <= 0)
]

print("\nORDERS WITH INVALID PRICES:")
print("Count:", len(invalid_order_price))
print(invalid_order_price.to_string(index=False))


# ==================================================
# 10. INVESTIGATE INVALID PRODUCT PRICES
# ==================================================

product_price = pd.to_numeric(
    products["unit_price"],
    errors="coerce"
)

invalid_product_price = products[
    product_price.isna() | (product_price <= 0)
]

print("\nPRODUCTS WITH INVALID PRICES:")
print("Count:", len(invalid_product_price))
print(invalid_product_price.to_string(index=False))


# ==================================================
# 11. CHECK CUSTOMER SIGNUP DATES
# ==================================================

# Parse mixed date formats.
# Invalid calendar dates are converted to NaT.

signup_dates = pd.to_datetime(
    customers["signup_date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

invalid_signup_dates = customers[
    signup_dates.isna()
]

print("\nINVALID CUSTOMER SIGNUP DATES:")
print("Count:", len(invalid_signup_dates))
print(invalid_signup_dates.to_string(index=False))


# ==================================================
# 12. CHECK ORDER DATES
# ==================================================

order_dates = pd.to_datetime(
    orders["order_date"],
    format="mixed",
    dayfirst=True,
    errors="coerce"
)

invalid_order_dates = orders[
    order_dates.isna()
]

print("\nINVALID ORDER DATES:")
print("Count:", len(invalid_order_dates))
print(invalid_order_dates.to_string(index=False))


# ==================================================
# 13. CHECK PAYMENT METHODS
# ==================================================

print("\nPAYMENT METHOD VALUES:")

print(
    orders["payment_method"]
    .str.strip()
    .value_counts(dropna=False)
    .to_string()
)


# ==================================================
# 14. CHECK ORDER STATUSES
# ==================================================

print("\nORDER STATUS VALUES:")

print(
    orders["order_status"]
    .str.strip()
    .value_counts(dropna=False)
    .to_string()
)


# ==================================================
# 15. CHECK PRODUCT CATEGORIES
# ==================================================

print("\nPRODUCT CATEGORY VALUES:")

print(
    products["category"]
    .str.strip()
    .value_counts(dropna=False)
    .to_string()
)

# Identify missing or unclear categories.

unclear_categories = products[
    products["category"].isna()
    | products["category"].str.strip().eq("Misc")
]

print("\nPRODUCTS WITH UNCLEAR CATEGORIES:")
print("Count:", len(unclear_categories))
print(unclear_categories.to_string(index=False))


# ==================================================
# 16. CHECK ADDRESSES DATA QUALITY
# ==================================================

# Addresses belong to Phase 2 of the project.
#
# These checks are included during the initial
# investigation to identify issues early.
#
# Address cleaning, PostGIS integration, and
# geographical validation will be completed
# separately during Phase 2.

print("\n" + "=" * 50)
print("ADDRESSES DATA QUALITY CHECKS")
print("=" * 50)


# --------------------------------------------------
# 16.1 CHECK MISSING ADDRESS IDs
# --------------------------------------------------

missing_address_ids = addresses[
    addresses["address_id"].isna()
]

print("\nADDRESSES WITH MISSING ADDRESS IDs:")
print("Count:", len(missing_address_ids))
print(missing_address_ids.to_string(index=False))


# --------------------------------------------------
# 16.2 CHECK DUPLICATE ADDRESS IDs
# --------------------------------------------------

# Identify every record involved in a duplicate
# address ID, rather than only subsequent duplicates.

duplicate_address_ids = addresses[
    addresses["address_id"].notna()
    & addresses["address_id"].duplicated(
        keep=False
    )
]

print("\nDUPLICATE ADDRESS IDs:")

print(
    "Additional duplicate occurrences:",
    addresses.loc[
        addresses["address_id"].notna(),
        "address_id"
    ].duplicated().sum()
)

print(
    "Total rows involved:",
    len(duplicate_address_ids)
)

print(
    duplicate_address_ids.to_string(index=False)
)


# --------------------------------------------------
# 16.3 CHECK EXACT DUPLICATE ROWS
# --------------------------------------------------

exact_duplicates = addresses[
    addresses.duplicated(keep=False)
]

print("\nEXACT DUPLICATE ADDRESS ROWS:")

print(
    "Additional duplicate occurrences:",
    addresses.duplicated().sum()
)

print(
    "Total rows involved:",
    len(exact_duplicates)
)

print(exact_duplicates.to_string(index=False))


# --------------------------------------------------
# 16.4 CHECK MISSING ADDRESS TYPES
# --------------------------------------------------

missing_address_types = addresses[
    addresses["address_type"].isna()
]

print("\nADDRESSES WITH MISSING ADDRESS TYPES:")
print("Count:", len(missing_address_types))
print(missing_address_types.to_string(index=False))


# --------------------------------------------------
# 16.5 CHECK CUSTOMER REFERENCES
# --------------------------------------------------

# Every address should reference an existing
# customer in the source customers dataset.
#
# Final foreign key validation against clean.customers
# will be performed during Phase 2.

valid_customer_ids = customers[
    "customer_id"
].dropna()

invalid_customer_addresses = addresses[
    addresses["customer_id"].notna()
    & ~addresses["customer_id"].isin(
        valid_customer_ids
    )
]

print("\nADDRESSES WITH NON-EXISTENT CUSTOMER IDs:")
print("Count:", len(invalid_customer_addresses))

print(
    invalid_customer_addresses.to_string(
        index=False
    )
)


# --------------------------------------------------
# 16.6 CHECK MISSING CUSTOMER IDs
# --------------------------------------------------

missing_customer_addresses = addresses[
    addresses["customer_id"].isna()
]

print("\nADDRESSES WITH MISSING CUSTOMER IDs:")
print("Count:", len(missing_customer_addresses))

print(
    missing_customer_addresses.to_string(
        index=False
    )
)


# --------------------------------------------------
# 16.7 CHECK INVALID COORDINATES
# --------------------------------------------------

# Valid geographical coordinate ranges:
#
# Latitude:  -90 to 90
# Longitude: -180 to 180
#
# Missing, non-numeric, or out-of-range coordinates
# are flagged for investigation.

latitude = pd.to_numeric(
    addresses["latitude"],
    errors="coerce"
)

longitude = pd.to_numeric(
    addresses["longitude"],
    errors="coerce"
)

invalid_latitude = (
    latitude.isna()
    | ~latitude.between(-90, 90)
)

invalid_longitude = (
    longitude.isna()
    | ~longitude.between(-180, 180)
)

invalid_coordinates = addresses[
    invalid_latitude | invalid_longitude
]

print("\nINVALID LATITUDE VALUES:")
print("Count:", invalid_latitude.sum())

print("\nINVALID LONGITUDE VALUES:")
print("Count:", invalid_longitude.sum())

print("\nADDRESSES WITH INVALID COORDINATES:")
print("Count:", len(invalid_coordinates))

print(
    invalid_coordinates.to_string(index=False)
)


# --------------------------------------------------
# 16.8 CHECK ADDRESS TYPE VALUES
# --------------------------------------------------

# Review variations in address types.
# For example: Home, home, HOME.

print("\nADDRESS TYPE VALUES:")

print(
    addresses["address_type"]
    .str.strip()
    .value_counts(dropna=False)
    .to_string()
)


# --------------------------------------------------
# 16.9 CHECK COUNTRY VALUES
# --------------------------------------------------

# Review inconsistent country names, spelling,
# capitalization, and abbreviations.

print("\nADDRESS COUNTRY VALUES:")

print(
    addresses["country"]
    .str.strip()
    .value_counts(dropna=False)
    .to_string()
)


# --------------------------------------------------
# 16.10 CHECK EXTRA WHITESPACE
# --------------------------------------------------

# Count leading and trailing whitespace in
# address columns.
#
# IDs were already trimmed for comparison in
# Section 3, so this check reports the current
# in-memory values.

print("\nADDRESS FIELDS WITH EXTRA SPACES:")

for column in addresses.columns:

    values = addresses[column].dropna()

    count = (
        values != values.str.strip()
    ).sum()

    if count > 0:
        print(f"{column}: {count}")


# --------------------------------------------------
# 16.11 CHECK CONFLICTING DUPLICATE ADDRESS IDs
# --------------------------------------------------

# A duplicate address ID may represent:
#
# 1. An exact duplicate record.
# 2. Different records sharing the same address ID.
#
# Conflicting records require investigation
# before deciding which record should be retained.

conflicting_ids = []

for address_id, group in addresses[
    addresses["address_id"].notna()
].groupby("address_id"):

    if len(group.drop_duplicates()) > 1:
        conflicting_ids.append(address_id)

conflicting_addresses = addresses[
    addresses["address_id"].isin(
        conflicting_ids
    )
]

print("\nCONFLICTING DUPLICATE ADDRESS IDs:")

print(
    "Number of conflicting IDs:",
    len(conflicting_ids)
)

print(
    "Total rows involved:",
    len(conflicting_addresses)
)

print(
    conflicting_addresses.to_string(index=False)
)


# ==================================================
# 17. COMPLETION SUMMARY
# ==================================================

print("\n" + "=" * 50)
print("DATA QUALITY ASSESSMENT COMPLETED")
print("=" * 50)

print("\nDatasets assessed:")
print("- Customers")
print("- Products")
print("- Orders")
print("- Addresses")

print("\nProject scope:")
print("Phase 1: Customers, Products, Orders")
print("Phase 2: Addresses and Mapping")

print("\nOriginal CSV files were not modified.")
print("No cleaning or rejection decisions were applied.")
