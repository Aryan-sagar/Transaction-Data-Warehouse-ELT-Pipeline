import csv
import os
from pathlib import Path

import psycopg2


DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "fintech"),
    "user": os.getenv("DB_USER", "fintech"),
    "password": os.getenv("DB_PASSWORD", "fintech_dev_password"),
}

RAW_DIR = Path("data/raw")


def get_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


def load_accounts(cursor):
    path = RAW_DIR / "accounts.csv"

    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        rows = [
            (
                row["account_id"],
                row["account_type"],
                row["country"],
                row["created_at"],
                row["status"],
            )
            for row in reader
        ]

    cursor.executemany(
        """
        INSERT INTO raw.accounts (
            account_id,
            account_type,
            country,
            created_at,
            status
        )
        VALUES (%s, %s, %s, %s, %s)
        ON CONFLICT (account_id) DO NOTHING
        """,
        rows,
    )

    inserted = cursor.rowcount
    skipped = len(rows) - inserted

    print(f"Accounts read:     {len(rows):,}")
    print(f"Accounts inserted: {inserted:,}")
    print(f"Accounts skipped:  {skipped:,}")


def load_merchants(cursor):
    path = RAW_DIR / "merchants.csv"

    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        rows = [
            (
                row["merchant_id"],
                row["merchant_name"],
                row["category"],
                row["country"],
                row["risk_category"],
                row["created_at"],
            )
            for row in reader
        ]

    cursor.executemany(
        """
        INSERT INTO raw.merchants (
            merchant_id,
            merchant_name,
            category,
            country,
            risk_category,
            created_at
        )
        VALUES (%s, %s, %s, %s, %s, %s)
        ON CONFLICT (merchant_id) DO NOTHING
        """,
        rows,
    )

    inserted = cursor.rowcount
    skipped = len(rows) - inserted

    print(f"Merchants read:     {len(rows):,}")
    print(f"Merchants inserted: {inserted:,}")
    print(f"Merchants skipped:  {skipped:,}")


def load_transactions(cursor):
    path = RAW_DIR / "transactions.csv"

    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        rows = [
            (
                row["transaction_id"],
                row["account_id"],
                row["merchant_id"],
                row["amount"],
                row["currency"],
                row["status"],
                row["payment_method"],
                row["transaction_timestamp"],
            )
            for row in reader
        ]

    cursor.executemany(
        """
        INSERT INTO raw.transactions (
            transaction_id,
            account_id,
            merchant_id,
            amount,
            currency,
            status,
            payment_method,
            transaction_timestamp
        )
        VALUES (%s, %s, %s, %s, %s, %s, %s, %s)
        ON CONFLICT (transaction_id) DO NOTHING
        """,
        rows,
    )

    inserted = cursor.rowcount
    skipped = len(rows) - inserted

    print(f"Transactions read:     {len(rows):,}")
    print(f"Transactions inserted: {inserted:,}")
    print(f"Transactions skipped:  {skipped:,}")


def main():
    print("Starting raw data ingestion...")

    connection = get_connection()

    try:
        with connection:
            with connection.cursor() as cursor:
                load_accounts(cursor)
                load_merchants(cursor)
                load_transactions(cursor)

        print("Raw ingestion completed successfully.")

    except Exception as error:
        print(f"Ingestion failed: {error}")
        raise

    finally:
        connection.close()


if __name__ == "__main__":
    main()