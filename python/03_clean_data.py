
from pathlib import Path
import os
import re

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
OUTPUT_DIR = PROJECT_ROOT / "data" / "processed"
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL was not found in your .env file.")

engine = create_engine(DATABASE_URL)


# Approved product category corrections
APPROVED_CATEGORY_CORRECTIONS = {
    "PROD-0036": "Books",
    "PROD-0042": "Toys & Games",
}


CATEGORY_MAP = {
    "electronics": "Electronics",
    "electroncs": "Electronics",
    "home & kitchen": "Home & Kitchen",
    "beauty & personal care": "Beauty & Personal Care",
    "books": "Books",
    "clothing": "Clothing",
    "garden": "Garden",
    "misc": "Misc",
    "sports & outdoors": "Sports & Outdoors",
    "toys & games": "Toys & Games",
}


STATUS_MAP = {
    "pending": "Pending",
    "processing": "Processing",
    "shipped": "Shipped",
    "delivered": "Delivered",
    "delivred": "Delivered",
    "completed": "Completed",
    "cancelled": "Cancelled",
    "canceled": "Cancelled",
    "refunded": "Refunded",
    "returned": "Returned",
}

# Complete, Dispatched and Unknown are intentionally not approved.
ALLOWED_STATUSES = {
    "Pending",
    "Processing",
    "Shipped",
    "Delivered",
    "Cancelled",
    "Refunded",
    "Returned",
}


PAYMENT_MAP = {
    "credit card": "Credit Card",
    "debit card": "Debit Card",
    "paypal": "PayPal",
    "apple pay": "Apple Pay",
    "google pay": "Google Pay",
    "bank transfer": "Bank Transfer",
    "cash on delivery": "Cash on Delivery",
    "klarna": "Klarna",
    "gift card": "Gift Card",
}

ALLOWED_PAYMENTS = set(PAYMENT_MAP.values())


# ============================================================
# HELPER FUNCTIONS
# ============================================================

def normalize_text(value):
    if pd.isna(value):
        return None

    value = re.sub(r"\s+", " ", str(value)).strip()
    return value if value else None


def normalize_id(value):
    value = normalize_text(value)
    return value.upper() if value else None


def normalize_email(value):
    value = normalize_text(value)
    return value.lower() if value else None


def normalize_category(value):
    value = normalize_text(value)

    if not value:
        return None

    return CATEGORY_MAP.get(value.lower(), value)


def normalize_status(value):
    value = normalize_text(value)

    if not value:
        return None

    return STATUS_MAP.get(value.lower(), value)


def normalize_payment(value):
    value = normalize_text(value)

    if not value:
        return None

    return PAYMENT_MAP.get(value.lower(), value)


def parse_date(value):
    value = normalize_text(value)

    if not value:
        return None

    for fmt in ("%Y-%m-%d", "%d-%m-%Y", "%d/%m/%Y"):
        parsed = pd.to_datetime(
            value,
            format=fmt,
            errors="coerce",
        )

        if not pd.isna(parsed):
            return parsed.strftime("%Y-%m-%d")

    return None


def add_issue(df, index, issue_type, reason):
    column = (
        "_reject_reasons"
        if issue_type == "reject"
        else "_review_reasons"
    )

    if reason not in df.at[index, column]:
        df.at[index, column].append(reason)


def prepare(df):
    df = df.copy().reset_index(drop=True)

    df["_source_row"] = range(1, len(df) + 1)
    df["_reject_reasons"] = [[] for _ in range(len(df))]
    df["_review_reasons"] = [[] for _ in range(len(df))]

    return df


def flag_exact_duplicates(df):
    business_columns = [
        col for col in df.columns
        if not col.startswith("_")
    ]

    duplicates = df.duplicated(
        subset=business_columns,
        keep="first",
    )

    for idx in df.index[duplicates]:
        add_issue(
            df,
            idx,
            "reject",
            "Exact duplicate source record",
        )


def flag_duplicate_ids(df, id_column):
    valid = df[id_column].notna()

    duplicates = df.loc[valid].duplicated(
        subset=[id_column],
        keep="first",
    )

    for idx in duplicates.index[duplicates]:
        if not df.at[idx, "_reject_reasons"]:
            add_issue(
                df,
                idx,
                "reject",
                "Duplicate after standardization",
            )


def finalize(df):
    def get_status(row):
        if row["_reject_reasons"]:
            return "rejected"

        if row["_review_reasons"]:
            return "needs_review"

        return "clean"

    df["record_status"] = df.apply(
        get_status,
        axis=1,
    )

    df["rejection_reason"] = df["_reject_reasons"].apply(
        lambda reasons: "; ".join(reasons)
    )

    df["review_reason"] = df["_review_reasons"].apply(
        lambda reasons: "; ".join(reasons)
    )

    return df


def export_results(df, table_name):
    for status in ("clean", "rejected", "needs_review"):
        subset = df[
            df["record_status"] == status
        ].copy()

        subset = subset.drop(
            columns=[
                "_source_row",
                "_reject_reasons",
                "_review_reasons",
                "record_status",
            ],
            errors="ignore",
        )

        if status == "clean":
            subset = subset.drop(
                columns=["rejection_reason", "review_reason"],
                errors="ignore",
            )

        elif status == "rejected":
            subset = subset.drop(
                columns=["review_reason"],
                errors="ignore",
            )

        else:
            subset = subset.drop(
                columns=["rejection_reason"],
                errors="ignore",
            )

        output_path = OUTPUT_DIR / f"{table_name}_{status}.csv"
        subset.to_csv(output_path, index=False)

    counts = df["record_status"].value_counts()

    print(f"\n{table_name.upper()} RESULTS")
    print(f"Raw: {len(df)}")
    print(f"Clean: {counts.get('clean', 0)}")
    print(f"Rejected: {counts.get('rejected', 0)}")
    print(f"Needs review: {counts.get('needs_review', 0)}")

    for status, column in (
        ("rejected", "rejection_reason"),
        ("needs_review", "review_reason"),
    ):
        subset = df[df["record_status"] == status]

        reasons = (
            subset[column]
            .str.split("; ")
            .explode()
            .dropna()
        )

        reasons = reasons[reasons != ""]

        if not reasons.empty:
            print(
                f"\n{status.replace('_', ' ').title()} reasons:"
            )
            print(reasons.value_counts().to_string())

    return {
        "table": table_name,
        "raw": len(df),
        "clean": int(counts.get("clean", 0)),
        "rejected": int(counts.get("rejected", 0)),
        "needs_review": int(counts.get("needs_review", 0)),
    }


def standardize_common_text(df):
    for column in df.columns:
        if column.startswith("_"):
            continue

        if pd.api.types.is_object_dtype(df[column]):
            df[column] = df[column].map(normalize_text)

    return df


# ============================================================
# LOAD RAW DATA
# ============================================================

print("=" * 60)
print("E-COMMERCE DATA QUALITY PIPELINE")
print("=" * 60)

print("\nLoading raw PostgreSQL tables...")

tables = {}

with engine.connect() as connection:
    for table_name in (
        "customers",
        "products",
        "orders",
        "addresses",
    ):
        tables[table_name] = pd.read_sql(
            text(f"SELECT * FROM raw.{table_name}"),
            connection,
        )

        print(f"{table_name}: {len(tables[table_name])} rows")


# ============================================================
# CUSTOMERS
# ============================================================

customers = prepare(tables["customers"])
flag_exact_duplicates(customers)
customers = standardize_common_text(customers)

customers["customer_id"] = customers["customer_id"].map(normalize_id)

if "email" in customers.columns:
    customers["email"] = customers["email"].map(normalize_email)

if "signup_date" in customers.columns:
    customers["signup_date"] = customers["signup_date"].map(parse_date)

for idx, row in customers.iterrows():
    if not row["customer_id"]:
        add_issue(
            customers, idx, "reject", "Missing customer_id"
        )

    if "signup_date" in customers.columns and not row["signup_date"]:
        add_issue(
            customers, idx, "reject", "Invalid signup_date"
        )

flag_duplicate_ids(customers, "customer_id")
customers = finalize(customers)

approved_customer_ids = set(
    customers.loc[
        customers["record_status"] == "clean",
        "customer_id",
    ].dropna()
)


# ============================================================
# PRODUCTS
# ============================================================

products = prepare(tables["products"])
flag_exact_duplicates(products)
products = standardize_common_text(products)

products["product_id"] = products["product_id"].map(normalize_id)

if "category" in products.columns:
    products["category"] = products["category"].map(
        normalize_category
    )

# Apply approved corrections
for product_id, category in APPROVED_CATEGORY_CORRECTIONS.items():
    mask = products["product_id"] == product_id
    products.loc[mask, "category"] = category

products["unit_price"] = pd.to_numeric(
    products["unit_price"], errors="coerce"
)

for idx, row in products.iterrows():
    if not row["product_id"]:
        add_issue(
            products, idx, "reject", "Missing product_id"
        )

    if pd.isna(row["unit_price"]) or row["unit_price"] <= 0:
        add_issue(
            products,
            idx,
            "review",
            "Missing or non-positive product price",
        )

    if "category" in products.columns and not row["category"]:
        add_issue(
            products, idx, "review", "Missing product category"
        )

flag_duplicate_ids(products, "product_id")
products = finalize(products)

approved_product_ids = set(
    products.loc[
        products["record_status"] == "clean",
        "product_id",
    ].dropna()
)

review_product_ids = set(
    products.loc[
        products["record_status"] == "needs_review",
        "product_id",
    ].dropna()
)


# ============================================================
# ORDERS
# ============================================================

orders = prepare(tables["orders"])
flag_exact_duplicates(orders)
orders = standardize_common_text(orders)

for column in ("order_id", "customer_id", "product_id"):
    orders[column] = orders[column].map(normalize_id)

if "order_date" in orders.columns:
    orders["order_date"] = orders["order_date"].map(parse_date)

orders["quantity"] = pd.to_numeric(
    orders["quantity"], errors="coerce"
)

orders["unit_price"] = pd.to_numeric(
    orders["unit_price"], errors="coerce"
)

# IMPORTANT: The actual column is order_status, not status.
if "order_status" in orders.columns:
    orders["order_status"] = orders["order_status"].map(
        normalize_status
    )

if "payment_method" in orders.columns:
    orders["payment_method"] = orders["payment_method"].map(
        normalize_payment
    )

for idx, row in orders.iterrows():
    if not row["order_id"]:
        add_issue(
            orders, idx, "reject", "Missing order_id"
        )

    if not row["customer_id"]:
        add_issue(
            orders, idx, "reject", "Missing customer_id"
        )
    elif row["customer_id"] not in approved_customer_ids:
        add_issue(
            orders,
            idx,
            "reject",
            "Customer not found in approved customers",
        )

    if not row["product_id"]:
        add_issue(
            orders, idx, "reject", "Missing product_id"
        )
    elif row["product_id"] in review_product_ids:
        add_issue(
            orders, idx, "review", "Product requires review"
        )
    elif row["product_id"] not in approved_product_ids:
        add_issue(
            orders,
            idx,
            "reject",
            "Product not found in approved products",
        )

    if "order_date" in orders.columns and not row["order_date"]:
        add_issue(
            orders,
            idx,
            "reject",
            "Missing or invalid order_date",
        )

    # NEW: Future-dated orders require manual review.
    # Preserve the original date; do not guess a correction.
    if "order_date" in orders.columns and row["order_date"]:
        if pd.Timestamp(row["order_date"]) > pd.Timestamp.today().normalize():
            add_issue(
                orders,
                idx,
                "review",
                "Order date is in the future",
            )

    quantity = row["quantity"]

    if (
        pd.isna(quantity)
        or quantity <= 0
        or not float(quantity).is_integer()
    ):
        add_issue(
            orders, idx, "reject", "Invalid quantity"
        )

    price = row["unit_price"]

    if pd.isna(price) or price < 0:
        add_issue(
            orders, idx, "reject", "Invalid unit_price"
        )

    # Validate the correct order_status column
    if "order_status" in orders.columns:
        if not row["order_status"]:
            add_issue(
                orders, idx, "review", "Missing order status"
            )
        elif row["order_status"] not in ALLOWED_STATUSES:
            add_issue(
                orders, idx, "review", "Unapproved order status"
            )

    if "payment_method" in orders.columns:
        if not row["payment_method"]:
            add_issue(
                orders, idx, "review", "Missing payment method"
            )
        elif row["payment_method"] not in ALLOWED_PAYMENTS:
            add_issue(
                orders, idx, "review", "Unapproved payment method"
            )

flag_duplicate_ids(orders, "order_id")
orders = finalize(orders)


# ============================================================
# ADDRESSES
# ============================================================

addresses = prepare(tables["addresses"])
flag_exact_duplicates(addresses)
addresses = standardize_common_text(addresses)

for column in ("address_id", "customer_id"):
    addresses[column] = addresses[column].map(normalize_id)

for column in ("latitude", "longitude"):
    if column in addresses.columns:
        addresses[column] = pd.to_numeric(
            addresses[column], errors="coerce"
        )

for idx, row in addresses.iterrows():
    if not row["address_id"]:
        add_issue(
            addresses, idx, "reject", "Missing address_id"
        )

    if not row["customer_id"]:
        add_issue(
            addresses, idx, "reject", "Missing customer_id"
        )
    elif row["customer_id"] not in approved_customer_ids:
        add_issue(
            addresses,
            idx,
            "reject",
            "Customer not found in approved customers",
        )

    if "address_type" in addresses.columns and not row["address_type"]:
        add_issue(
            addresses, idx, "review", "Missing address_type"
        )

    if (
        "latitude" in addresses.columns
        and "longitude" in addresses.columns
    ):
        latitude = row["latitude"]
        longitude = row["longitude"]

        if pd.isna(latitude) or pd.isna(longitude):
            add_issue(
                addresses, idx, "review", "Missing coordinates"
            )
        elif not (
            -90 <= latitude <= 90
            and -180 <= longitude <= 180
        ):
            add_issue(
                addresses, idx, "reject", "Invalid coordinates"
            )
        elif (
            row["address_id"] == "ADDR-00112"
            and abs(latitude - 4.85046) < 0.01
            and abs(longitude - 45.77041) < 0.01
        ):
            add_issue(
                addresses,
                idx,
                "review",
                "Possible swapped Lyon coordinates",
            )

flag_duplicate_ids(addresses, "address_id")
addresses = finalize(addresses)


# ============================================================
# EXPORT RESULTS
# ============================================================

summary = []

for table_name, df in (
    ("customers", customers),
    ("products", products),
    ("orders", orders),
    ("addresses", addresses),
):
    summary.append(export_results(df, table_name))


# ============================================================
# FINAL RECONCILIATION
# ============================================================

summary_df = pd.DataFrame(summary)

print("\n" + "=" * 60)
print("FINAL RECONCILIATION")
print("=" * 60)

print(summary_df.to_string(index=False))

totals = summary_df[
    ["raw", "clean", "rejected", "needs_review"]
].sum()

print("\nTOTALS")
print(totals.to_string())

if totals["raw"] != (
    totals["clean"]
    + totals["rejected"]
    + totals["needs_review"]
):
    raise AssertionError("Reconciliation failed!")

print("\nAll source rows accounted for.")
print(f"CSV files saved in: {OUTPUT_DIR}")
print("PostgreSQL raw tables were not modified.")
print("No records were loaded into the clean schema.")
