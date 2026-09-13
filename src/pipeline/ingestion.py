import csv
import json
import os
from pathlib import Path

import psycopg2


DATABASE_CONFIG = {
    "host": os.getenv("DB_HOST", "localhost"),
    "port": os.getenv("DB_PORT", "5432"),
    "database": os.getenv("DB_NAME", "fintech"),
    "user": os.getenv("DB_USER", "fintech"),
    "password": os.getenv("DB_PASSWORD"),
}

RAW_DIR = Path("data/raw")
BATCH_SIZE = 1000


def get_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


def quarantine_row(cursor, source_file, row_number, row, reason):
    cursor.execute(
        """
        INSERT INTO raw.quarantine_rows (
            source_file,
            row_number,
            raw_data,
            error_reason
        )
        VALUES (%s, %s, %s, %s)
        """,
        (
            source_file,
            row_number,
            json.dumps(row),
            reason,
        ),
    )


def load_accounts(cursor):
    path = RAW_DIR / "accounts.csv"

    valid_rows = []
    quarantined = 0

    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row_number, row in enumerate(reader, start=2):
            account_id = (row.get("account_id") or "").strip()

            if not account_id:
                quarantine_row(
                    cursor,
                    path.name,
                    row_number,
                    row,
                    "Missing account_id",
                )
                quarantined += 1
                continue

            valid_rows.append(
                (
                    account_id,
                    row.get("account_type"),
                    row.get("country"),
                    row.get("created_at"),
                    row.get("status"),
                )
            )

    inserted = 0

    for i in range(0, len(valid_rows), BATCH_SIZE):
        batch = valid_rows[i:i + BATCH_SIZE]

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
            batch,
        )

        inserted += cursor.rowcount

    skipped = len(valid_rows) - inserted

    print(f"Accounts read:       {len(valid_rows) + quarantined:,}")
    print(f"Accounts inserted:   {inserted:,}")
    print(f"Accounts skipped:    {skipped:,}")
    print(f"Accounts quarantined:{quarantined:,}")


def load_merchants(cursor):
    path = RAW_DIR / "merchants.csv"

    valid_rows = []
    quarantined = 0

    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row_number, row in enumerate(reader, start=2):
            merchant_id = (row.get("merchant_id") or "").strip()

            if not merchant_id:
                quarantine_row(
                    cursor,
                    path.name,
                    row_number,
                    row,
                    "Missing merchant_id",
                )
                quarantined += 1
                continue

            valid_rows.append(
                (
                    merchant_id,
                    row.get("merchant_name"),
                    row.get("category"),
                    row.get("country"),
                    row.get("risk_category"),
                    row.get("created_at"),
                )
            )

    inserted = 0

    for i in range(0, len(valid_rows), BATCH_SIZE):
        batch = valid_rows[i:i + BATCH_SIZE]

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
            batch,
        )

        inserted += cursor.rowcount

    skipped = len(valid_rows) - inserted

    print(f"Merchants read:       {len(valid_rows) + quarantined:,}")
    print(f"Merchants inserted:   {inserted:,}")
    print(f"Merchants skipped:    {skipped:,}")
    print(f"Merchants quarantined:{quarantined:,}")


def load_transactions(cursor):
    path = RAW_DIR / "transactions.csv"

    valid_rows = []
    quarantined = 0

    with open(path, newline="", encoding="utf-8") as file:
        reader = csv.DictReader(file)

        for row_number, row in enumerate(reader, start=2):
            transaction_id = (row.get("transaction_id") or "").strip()
            account_id = (row.get("account_id") or "").strip()
            merchant_id = (row.get("merchant_id") or "").strip()

            if not transaction_id:
                quarantine_row(
                    cursor,
                    path.name,
                    row_number,
                    row,
                    "Missing transaction_id",
                )
                quarantined += 1
                continue

            if not account_id:
                quarantine_row(
                    cursor,
                    path.name,
                    row_number,
                    row,
                    "Missing account_id",
                )
                quarantined += 1
                continue

            if not merchant_id:
                quarantine_row(
                    cursor,
                    path.name,
                    row_number,
                    row,
                    "Missing merchant_id",
                )
                quarantined += 1
                continue
            valid_rows.append(
                (
                    transaction_id,
                    row.get("account_id"),
                    row.get("merchant_id"),
                    row.get("amount"),
                    row.get("currency"),
                    row.get("status"),
                    row.get("payment_method"),
                    row.get("transaction_timestamp"),
                )
            )

    touched = 0

    for i in range(0, len(valid_rows), BATCH_SIZE):
        batch = valid_rows[i:i + BATCH_SIZE]

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
            ON CONFLICT (transaction_id) DO UPDATE SET
                amount = EXCLUDED.amount,
                currency = EXCLUDED.currency,
                status = EXCLUDED.status,
                payment_method = EXCLUDED.payment_method,
                transaction_timestamp = EXCLUDED.transaction_timestamp,
                ingested_at = now()
            WHERE
                raw.transactions.status IS DISTINCT FROM EXCLUDED.status
                OR raw.transactions.amount IS DISTINCT FROM EXCLUDED.amount
            """,
            batch,
        )

        touched += cursor.rowcount

    unchanged = len(valid_rows) - touched

    print(f"Transactions read:                {len(valid_rows) + quarantined:,}")
    print(f"Transactions inserted/updated:    {touched:,}")
    print(f"Transactions unchanged (skipped): {unchanged:,}")
    print(f"Transactions quarantined:          {quarantined:,}")


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