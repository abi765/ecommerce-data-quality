import pandas as pd

# Original datasets and their primary keys
datasets = {
    "customers": "customer_id",
    "products": "product_id",
    "orders": "order_id",
    "addresses": "address_id"
}

for table_name, primary_key in datasets.items():

    print(f"\n{'=' * 50}")
    print(f"PROFILING TABLE: {table_name.upper()}")
    print(f"{'=' * 50}")

    # Read the original CSV
    df = pd.read_csv(
        f"data/practice/{table_name}.csv",
        dtype=str
    )

    # Treat empty strings and whitespace as missing
    df = df.replace(r"^\s*$", pd.NA, regex=True)

    # 1. Dataset dimensions
    print("\nROWS AND COLUMNS:")
    print(df.shape)

    # 2. Column names and data types
    print("\nCOLUMN INFORMATION:")
    print(df.dtypes)

    # 3. Missing values across all columns
    print("\nMISSING VALUES:")
    print(df.isna().sum())

    # 4. Completely duplicated rows
    print("\nEXACT DUPLICATE ROWS:")
    print(df.duplicated().sum())

    # 5. Missing primary keys
    print("\nMISSING PRIMARY KEYS:")
    print(df[primary_key].isna().sum())

    # 6. Duplicate primary keys (excluding missing IDs)
    print("\nDUPLICATE PRIMARY KEYS:")
    print(
        df.loc[df[primary_key].notna(), primary_key]
        .duplicated()
        .sum()
    )

    # 7. Leading or trailing spaces
    print("\nVALUES WITH EXTRA SPACES:")

    for column in df.columns:
        values = df[column].dropna()

        count = (
            values != values.str.strip()
        ).sum()

        if count > 0:
            print(f"{column}: {count}")

    # 8. Unique values in each column
    print("\nUNIQUE VALUE COUNTS:")
    print(df.nunique(dropna=True))