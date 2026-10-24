
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, inspect, text

PROJECT_ROOT = Path(__file__).resolve().parent.parent
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

load_dotenv(PROJECT_ROOT / ".env")
DATABASE_URL = os.getenv("DATABASE_URL")

if not DATABASE_URL:
    raise ValueError("DATABASE_URL is missing from .env")

EXPECTED_COUNTS = {
    "customers": 15,
    "products": 2,
    "orders": 96,
}


def main():
    engine = create_engine(DATABASE_URL)

    try:
        inspector = inspect(engine)
        prepared = {}

        # Read and check the rejected CSV files.
        for table_name, expected_count in EXPECTED_COUNTS.items():
            csv_path = PROCESSED_DIR / f"{table_name}_rejected.csv"

            if not csv_path.exists():
                raise FileNotFoundError(f"Missing file: {csv_path}")

            df = pd.read_csv(
                csv_path,
                dtype=str,
                keep_default_na=False
            )

            if len(df) != expected_count:
                raise ValueError(
                    f"{table_name}: expected {expected_count}, "
                    f"found {len(df)}"
                )

            # Match the database column name.
            df = df.rename(
                columns={"rejection_reason": "reject_reason"}
            )

            if "reject_reason" not in df.columns:
                raise ValueError(
                    f"{table_name}: reject_reason is missing"
                )

            if df["reject_reason"].eq("").any():
                raise ValueError(
                    f"{table_name}: some rejection reasons are empty"
                )

            db_columns = {
                column["name"]
                for column in inspector.get_columns(
                    table_name,
                    schema="rejects"
                )
            }

            if set(df.columns) != db_columns:
                raise ValueError(
                    f"Column mismatch in rejects.{table_name}\n"
                    f"CSV columns: {sorted(df.columns)}\n"
                    f"DB columns: {sorted(db_columns)}"
                )

            prepared[table_name] = df.replace("", None)

        # Insert all records in one transaction.
        with engine.begin() as connection:

            for table_name in EXPECTED_COUNTS:
                existing_count = connection.execute(
                    text(
                        f"SELECT COUNT(*) FROM rejects.{table_name}"
                    )
                ).scalar_one()

                if existing_count != 0:
                    raise ValueError(
                        f"rejects.{table_name} already has "
                        f"{existing_count} records. Import cancelled."
                    )

            for table_name, df in prepared.items():
                df.to_sql(
                    name=table_name,
                    con=connection,
                    schema="rejects",
                    if_exists="append",
                    index=False
                )

                actual_count = connection.execute(
                    text(
                        f"SELECT COUNT(*) FROM rejects.{table_name}"
                    )
                ).scalar_one()

                if actual_count != EXPECTED_COUNTS[table_name]:
                    raise ValueError(
                        f"Incorrect count in rejects.{table_name}"
                    )

                print(
                    f"Loaded rejects.{table_name}: "
                    f"{actual_count} records"
                )

        print("Success: 113 rejected records loaded.")

    finally:
        engine.dispose()


if __name__ == "__main__":
    main()
