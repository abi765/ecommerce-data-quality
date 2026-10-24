
from pathlib import Path
import os
import sys

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text
from sqlalchemy.exc import SQLAlchemyError


# ============================================================
# CONFIGURATION
# ============================================================

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

load_dotenv(PROJECT_ROOT / ".env")

DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL was not found in .env")

TABLES = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "addresses": "address_id",
}

EXPECTED_COUNTS = {
    "customers": 495,
    "products": 47,
    "orders": 1715,
    "addresses": 584,
}

# Previous successful load.
# Refresh is permitted only when existing counts match these.
PREVIOUS_COUNTS = {
    "customers": 495,
    "products": 47,
    "orders": 1717,
    "addresses": 584,
}

LOAD_ORDER = [
    "customers",
    "products",
    "orders",
    "addresses",
]

DATE_COLUMNS = {
    "customers": ["signup_date"],
    "orders": ["order_date"],
}

NUMERIC_COLUMNS = {
    "products": ["unit_price"],
    "orders": ["quantity", "unit_price"],
    "addresses": ["latitude", "longitude"],
}


# ============================================================
# LOAD AND VALIDATE CSV FILES
# ============================================================

def load_and_validate_csvs():
    print("=" * 60)
    print("LOAD CLEAN DATA INTO POSTGRESQL")
    print("=" * 60)

    dataframes = {}

    for table_name, primary_key in TABLES.items():
        csv_path = PROCESSED_DIR / f"{table_name}_clean.csv"

        if not csv_path.exists():
            raise FileNotFoundError(
                f"Missing cleaned CSV file: {csv_path}"
            )

        # Read identifiers as strings to preserve formatting.
        df = pd.read_csv(
            csv_path,
            dtype={primary_key: "string"},
            keep_default_na=True,
        )

        if primary_key not in df.columns:
            raise ValueError(
                f"{table_name}: missing primary key column "
                f"'{primary_key}'"
            )

        ids = df[primary_key].astype("string").str.strip()

        if ids.isna().any() or ids.eq("").any():
            raise ValueError(
                f"{table_name}: missing or blank primary keys"
            )

        if ids.duplicated().any():
            raise ValueError(
                f"{table_name}: duplicate primary keys"
            )

        expected = EXPECTED_COUNTS[table_name]

        if len(df) != expected:
            raise ValueError(
                f"{table_name}: expected {expected} rows, "
                f"found {len(df)}"
            )

        # Convert dates to Python date objects.
        for column in DATE_COLUMNS.get(table_name, []):
            df[column] = pd.to_datetime(
                df[column],
                format="%Y-%m-%d",
                errors="raise",
            ).dt.date

        # Convert numeric fields.
        for column in NUMERIC_COLUMNS.get(table_name, []):
            df[column] = pd.to_numeric(
                df[column],
                errors="raise",
            )

        if table_name == "orders":
            quantity = df["quantity"]

            if quantity.isna().any():
                raise ValueError(
                    "orders: missing quantities"
                )

            if (quantity <= 0).any():
                raise ValueError(
                    "orders: quantities must be positive"
                )

            if (quantity % 1 != 0).any():
                raise ValueError(
                    "orders: quantities must be whole numbers"
                )

            df["quantity"] = quantity.astype("int64")

            # Future-dated orders must not enter clean.orders.
            if (df["order_date"] > pd.Timestamp.today().date()).any():
                raise ValueError(
                    "orders: future-dated orders found in clean CSV"
                )

        dataframes[table_name] = df

        print(
            f"{table_name}: {len(df)} validated rows"
        )

    return dataframes


# ============================================================
# VALIDATE FOREIGN KEY REFERENCES
# ============================================================

def validate_relationships(dataframes):
    customers = dataframes["customers"]
    products = dataframes["products"]
    orders = dataframes["orders"]
    addresses = dataframes["addresses"]

    customer_ids = set(customers["customer_id"])
    product_ids = set(products["product_id"])

    if not orders["customer_id"].isin(customer_ids).all():
        raise ValueError(
            "Orders contain invalid customer references"
        )

    if not orders["product_id"].isin(product_ids).all():
        raise ValueError(
            "Orders contain invalid product references"
        )

    if not addresses["customer_id"].isin(customer_ids).all():
        raise ValueError(
            "Addresses contain invalid customer references"
        )

    print("\nAll foreign key references validated.")


# ============================================================
# CHECK POSTGRESQL TABLE STRUCTURES
# ============================================================

def validate_database_structure(engine, dataframes):
    inspector = inspect(engine)

    for table_name in LOAD_ORDER:
        if not inspector.has_table(
            table_name,
            schema="clean",
        ):
            raise ValueError(
                f"Missing PostgreSQL table: clean.{table_name}"
            )

        db_columns = {
            column["name"]
            for column in inspector.get_columns(
                table_name,
                schema="clean",
            )
        }

        csv_columns = set(dataframes[table_name].columns)

        if csv_columns != db_columns:
            raise ValueError(
                f"Column mismatch for clean.{table_name}\n"
                f"CSV columns: {sorted(csv_columns)}\n"
                f"DB columns: {sorted(db_columns)}"
            )

    print("All CSV columns match PostgreSQL tables.")


# ============================================================
# CHECK EXISTING CLEAN TABLES
# ============================================================

def check_existing_data(connection):
    print("\nChecking destination tables...")

    existing_counts = {}

    for table_name in LOAD_ORDER:
        count = connection.execute(
            text(f"SELECT COUNT(*) FROM clean.{table_name}")
        ).scalar_one()

        existing_counts[table_name] = count

        print(
            f"clean.{table_name}: {count} existing rows"
        )

    all_empty = all(
        count == 0 for count in existing_counts.values()
    )

    if all_empty:
        print("\nDestination tables are empty.")
        return "initial"

    # Never refresh a partially populated or unexpected database.
    for table_name in LOAD_ORDER:
        actual = existing_counts[table_name]
        expected = PREVIOUS_COUNTS[table_name]

        if actual != expected:
            raise ValueError(
                f"Unexpected existing count in clean.{table_name}: "
                f"expected {expected}, found {actual}. "
                "Refresh cancelled to protect existing data."
            )

    print("\nExisting tables match the previous load.")
    print("A controlled refresh is available.")

    return "refresh"


# ============================================================
# REQUIRE EXPLICIT REFRESH CONFIRMATION
# ============================================================

def confirm_refresh():
    print("\n" + "=" * 60)
    print("REFRESH CONFIRMATION REQUIRED")
    print("=" * 60)

    print(
        "The existing rows in the four clean tables "
        "will be replaced with the validated CSV data."
    )
    print("The raw tables will not be modified.")
    print("Rejected and needs-review CSV files will be preserved.")
    print(
        "If loading fails, the database transaction "
        "will be rolled back."
    )

    response = input(
        "\nType REFRESH to continue, or anything else to cancel: "
    ).strip()

    if response != "REFRESH":
        raise ValueError(
            "Refresh cancelled by user. No database changes made."
        )


# ============================================================
# LOAD DATA IN A SINGLE TRANSACTION
# ============================================================

def load_into_postgresql(engine, dataframes):
    # Begin a transaction for all four tables.
    # Any failure causes a rollback.
    with engine.begin() as connection:

        mode = check_existing_data(connection)

        if mode == "refresh":
            confirm_refresh()

            print("\nRemoving previous approved records...")

            # Delete dependent rows before parent rows.
            # No raw tables are affected.
            DELETE_ORDER = [
                "orders",
                "addresses",
                "products",
                "customers",
            ]

            for table_name in DELETE_ORDER:
                connection.execute(
                    text(f"DELETE FROM clean.{table_name}")
                )

                print(
                    f"Cleared clean.{table_name}"
                )

        print("\nLoading approved records...")

        for table_name in LOAD_ORDER:
            df = dataframes[table_name].copy()

            # Replace pandas missing values with SQL NULL.
            df = df.astype(object).where(
                pd.notna(df),
                None,
            )

            df.to_sql(
                name=table_name,
                con=connection,
                schema="clean",
                if_exists="append",
                index=False,
                method=None,
                chunksize=100,
            )

            loaded_count = connection.execute(
                text(
                    f"SELECT COUNT(*) FROM clean.{table_name}"
                )
            ).scalar_one()

            expected = EXPECTED_COUNTS[table_name]

            if loaded_count != expected:
                raise ValueError(
                    f"Row count mismatch in clean.{table_name}: "
                    f"expected {expected}, "
                    f"found {loaded_count}"
                )

            print(
                f"Loaded clean.{table_name}: "
                f"{loaded_count} rows"
            )

        # Verify that the two flagged orders are absent.
        flagged_orders = connection.execute(
            text(
                """
                SELECT COUNT(*)
                FROM clean.orders
                WHERE order_id IN (
                    'ORD-00070',
                    'ORD-00763'
                )
                """
            )
        ).scalar_one()

        if flagged_orders != 0:
            raise ValueError(
                "Future-dated orders are still in clean.orders. "
                "Transaction cancelled."
            )

        print(
            "\nConfirmed: ORD-00070 and ORD-00763 "
            "are absent from clean.orders."
        )

    # Transaction commits only after every check succeeds.


# ============================================================
# MAIN
# ============================================================

def main():
    engine = None

    try:
        dataframes = load_and_validate_csvs()

        validate_relationships(dataframes)

        engine = create_engine(DATABASE_URL)

        validate_database_structure(
            engine,
            dataframes,
        )

        load_into_postgresql(
            engine,
            dataframes,
        )

        print("\n" + "=" * 60)
        print("LOAD COMPLETED SUCCESSFULLY")
        print("=" * 60)

        total = sum(EXPECTED_COUNTS.values())

        print(
            f"Total clean records loaded: {total}"
        )
        print("Raw tables were not modified.")
        print(
            "Rejected and needs-review records "
            "were not loaded."
        )

    except SQLAlchemyError as error:
        print("\n" + "=" * 60)
        print("DATABASE ERROR - LOAD CANCELLED")
        print("=" * 60)

        original_error = getattr(
            error,
            "orig",
            None,
        )

        if original_error is not None:
            print(
                f"{type(original_error).__name__}: "
                f"{original_error}"
            )
        else:
            print(
                f"{type(error).__name__}: "
                f"{error.args[0] if error.args else 'Unknown error'}"
            )

        print(
            "\nThe transaction was rolled back "
            "if the error occurred during loading."
        )

        sys.exit(1)

    except (ValueError, FileNotFoundError, KeyError) as error:
        print("\n" + "=" * 60)
        print("VALIDATION ERROR - LOAD CANCELLED")
        print("=" * 60)
        print(str(error))
        print(
            "\nAny database changes in the transaction "
            "were rolled back."
        )
        sys.exit(1)

    finally:
        if engine is not None:
            engine.dispose()


if __name__ == "__main__":
    main()
