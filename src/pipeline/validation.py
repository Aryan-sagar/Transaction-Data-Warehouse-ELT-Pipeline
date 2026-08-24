import psycopg2
from dataclasses import dataclass


DATABASE_CONFIG = {
    "host": "localhost",
    "port": "5432",
    "database": "fintech",
    "user": "fintech",
    "password": "fintech_dev_password",
}


@dataclass
class ValidationResult:
    name: str
    passed: bool
    details: str


def get_connection():
    return psycopg2.connect(**DATABASE_CONFIG)


def check_transaction_duplicates(cursor):
    cursor.execute("""
        SELECT COUNT(*)
        FROM (
            SELECT transaction_id
            FROM raw.transactions
            GROUP BY transaction_id
            HAVING COUNT(*) > 1
        ) duplicates;
    """)

    count = cursor.fetchone()[0]

    return ValidationResult(
        name="transaction_uniqueness",
        passed=count == 0,
        details=f"{count} duplicate transaction IDs found",
    )


def check_missing_accounts(cursor):
    cursor.execute("""
        SELECT COUNT(*)
        FROM raw.transactions
        WHERE account_id IS NULL
           OR TRIM(account_id) = '';
    """)

    count = cursor.fetchone()[0]

    return ValidationResult(
        name="account_id_not_null",
        passed=count == 0,
        details=f"{count} transactions have missing account IDs",
    )


def check_missing_merchants(cursor):
    cursor.execute("""
        SELECT COUNT(*)
        FROM raw.transactions
        WHERE merchant_id IS NULL
           OR TRIM(merchant_id) = '';
    """)

    count = cursor.fetchone()[0]

    return ValidationResult(
        name="merchant_id_not_null",
        passed=count == 0,
        details=f"{count} transactions have missing merchant IDs",
    )


def check_invalid_accounts(cursor):
    cursor.execute("""
        SELECT COUNT(*)
        FROM raw.transactions t
        LEFT JOIN raw.accounts a
            ON t.account_id = a.account_id
        WHERE t.account_id IS NOT NULL
          AND TRIM(t.account_id) <> ''
          AND a.account_id IS NULL;
    """)

    count = cursor.fetchone()[0]

    return ValidationResult(
        name="account_referential_integrity",
        passed=count == 0,
        details=f"{count} transactions reference nonexistent accounts",
    )


def check_invalid_amounts(cursor):
    cursor.execute("""
        SELECT COUNT(*)
        FROM raw.transactions
        WHERE amount::NUMERIC <= 0;
    """)

    count = cursor.fetchone()[0]

    return ValidationResult(
        name="positive_transaction_amount",
        passed=count == 0,
        details=f"{count} transactions have invalid amounts",
    )


def run_quality_gate():
    connection = get_connection()

    try:
        with connection:
            with connection.cursor() as cursor:

                checks = [
                    check_transaction_duplicates(cursor),
                    check_missing_accounts(cursor),
                    check_missing_merchants(cursor),
                    check_invalid_accounts(cursor),
                    check_invalid_amounts(cursor),
                ]

        print("\nDATA QUALITY REPORT")
        print("=" * 60)

        all_passed = True

        for result in checks:

            status = "PASS" if result.passed else "FAIL"

            print(
                f"[{status}] "
                f"{result.name}: "
                f"{result.details}"
            )

            if not result.passed:
                all_passed = False

        print("=" * 60)

        if all_passed:
            print("QUALITY GATE PASSED")
            return True

        print("QUALITY GATE FAILED")
        return False

    finally:
        connection.close()


if __name__ == "__main__":
    passed = run_quality_gate()

    if not passed:
        raise SystemExit(1)