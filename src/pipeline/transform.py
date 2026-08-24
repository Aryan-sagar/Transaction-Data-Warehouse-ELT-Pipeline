import psycopg2


DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "fintech",
    "user": "fintech",
    "password": "fintech_dev_password",
}


def get_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


def transform_transactions():
    connection = get_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                # Clear the previous staging run.
                cursor.execute(
                    "TRUNCATE TABLE staging.transactions;"
                )

                cursor.execute(
                    """
                    INSERT INTO staging.transactions (
                        transaction_id,
                        account_id,
                        merchant_id,
                        amount,
                        currency,
                        status,
                        payment_method,
                        transaction_timestamp,
                        ingested_at
                    )

                    SELECT DISTINCT ON (transaction_id)
                        transaction_id,
                        TRIM(account_id),
                        TRIM(merchant_id),
                        CAST(amount AS NUMERIC(18,2)),
                        UPPER(TRIM(currency)),
                        LOWER(TRIM(status)),
                        LOWER(TRIM(payment_method)),
                        CAST(transaction_timestamp AS TIMESTAMP),
                        ingested_at

                    FROM raw.transactions

                    WHERE NULLIF(TRIM(account_id), '') IS NOT NULL
                      AND NULLIF(TRIM(merchant_id), '') IS NOT NULL
                      AND amount::NUMERIC > 0
                      AND currency IS NOT NULL
                      AND transaction_timestamp IS NOT NULL

                    ORDER BY
                        transaction_id,
                        ingested_at DESC;
                    """
                )

                cursor.execute(
                    """
                    DELETE FROM staging.transactions s
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM raw.accounts a
                        WHERE a.account_id = s.account_id
                    );
                    """
                )

                cursor.execute(
                    """
                    DELETE FROM staging.transactions s
                    WHERE NOT EXISTS (
                        SELECT 1
                        FROM raw.merchants m
                        WHERE m.merchant_id = s.merchant_id
                    );
                    """
                )

                cursor.execute(
                    "SELECT COUNT(*) FROM staging.transactions;"
                )

                count = cursor.fetchone()[0]

                print(
                    f"Staging transformation completed: "
                    f"{count:,} clean transactions"
                )

    finally:
        connection.close()


if __name__ == "__main__":
    transform_transactions()