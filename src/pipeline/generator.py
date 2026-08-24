from faker import Faker
from datetime import datetime, timedelta
import random
import csv
from pathlib import Path


fake = Faker("en_IN")

OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


ACCOUNT_TYPES = [
    "savings",
    "current",
    "salary",
]

ACCOUNT_STATUSES = [
    "active",
    "inactive",
    "suspended",
]

MERCHANT_CATEGORIES = [
    "grocery",
    "food",
    "shopping",
    "travel",
    "entertainment",
    "utilities",
    "healthcare",
    "education",
]

PAYMENT_METHODS = [
    "upi",
    "card",
    "net_banking",
    "wallet",
]

CURRENCIES = ["INR"]

TRANSACTION_STATUSES = [
    "success",
    "failed",
    "pending",
]


def generate_accounts(n: int = 1000) -> list[dict]:
    accounts = []

    for i in range(n):
        accounts.append({
            "account_id": f"ACC_{i + 1:06d}",
            "account_type": random.choice(ACCOUNT_TYPES),
            "country": "IN",
            "created_at": fake.date_time_between(
                start_date="-3y",
                end_date="now",
            ).isoformat(),
            "status": random.choices(
                ACCOUNT_STATUSES,
                weights=[90, 7, 3],
            )[0],
        })

    return accounts


def generate_merchants(n: int = 200) -> list[dict]:
    merchants = []

    for i in range(n):
        merchants.append({
            "merchant_id": f"MER_{i + 1:05d}",
            "merchant_name": fake.company(),
            "category": random.choice(MERCHANT_CATEGORIES),
            "country": "IN",
            "risk_category": random.choices(
                ["low", "medium", "high"],
                weights=[70, 25, 5],
            )[0],
            "created_at": fake.date_time_between(
                start_date="-3y",
                end_date="now",
            ).isoformat(),
        })

    return merchants


def generate_transactions(
    n: int,
    accounts: list[dict],
    merchants: list[dict],
) -> list[dict]:

    transactions = []

    account_ids = [a["account_id"] for a in accounts]
    merchant_ids = [m["merchant_id"] for m in merchants]

    start_time = datetime.now() - timedelta(days=90)

    for i in range(n):

        timestamp = start_time + timedelta(
            seconds=random.randint(0, 90 * 24 * 60 * 60)
        )

        # Most transactions are small/medium-value.
        amount = round(
            random.lognormvariate(5.5, 1.0),
            2,
        )

        transactions.append({
            "transaction_id": f"TXN_{i + 1:09d}",
            "account_id": random.choice(account_ids),
            "merchant_id": random.choice(merchant_ids),
            "amount": amount,
            "currency": random.choice(CURRENCIES),
            "status": random.choices(
                TRANSACTION_STATUSES,
                weights=[94, 4, 2],
            )[0],
            "payment_method": random.choice(PAYMENT_METHODS),
            "transaction_timestamp": timestamp.isoformat(),
        })

    return transactions


def write_csv(records: list[dict], filename: str) -> None:
    path = OUTPUT_DIR / filename

    if not records:
        return

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=records[0].keys(),
        )

        writer.writeheader()
        writer.writerows(records)

    print(f"Wrote {len(records):,} records → {path}")


def main() -> None:
    print("Generating fintech transaction dataset...")

    accounts = generate_accounts(1_000)
    merchants = generate_merchants(200)
    transactions = generate_transactions(
        10_000,
        accounts,
        merchants,
    )

    write_csv(accounts, "accounts.csv")
    write_csv(merchants, "merchants.csv")
    write_csv(transactions, "transactions.csv")

    print("Dataset generation complete.")


if __name__ == "__main__":
    main()