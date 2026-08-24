import csv
import random
from datetime import datetime
from pathlib import Path


OUTPUT = Path("data/raw/incremental_transactions.csv")

ACCOUNT_IDS = [
    f"ACC_{i:06d}"
    for i in range(1, 1001)
]

MERCHANT_IDS = [
    f"MER_{i:05d}"
    for i in range(1, 201)
]

PAYMENT_METHODS = [
    "upi",
    "card",
    "net_banking",
    "wallet",
]

STATUSES = [
    "success",
    "failed",
    "pending",
]


def generate_batch(count=100):

    records = []

    for i in range(count):

        transaction_number = 10_000 + i + 1

        records.append({
            "transaction_id": f"TXN_{transaction_number:09d}",
            "account_id": random.choice(ACCOUNT_IDS),
            "merchant_id": random.choice(MERCHANT_IDS),
            "amount": round(random.uniform(50, 5000), 2),
            "currency": "INR",
            "status": random.choices(
                STATUSES,
                weights=[94, 4, 2],
            )[0],
            "payment_method": random.choice(
                PAYMENT_METHODS
            ),
            "transaction_timestamp": datetime.now().isoformat(),
        })

    return records


def main():

    records = generate_batch(100)

    OUTPUT.parent.mkdir(
        parents=True,
        exist_ok=True,
    )

    with open(
        OUTPUT,
        "w",
        newline="",
        encoding="utf-8",
    ) as file:

        writer = csv.DictWriter(
            file,
            fieldnames=records[0].keys(),
        )

        writer.writeheader()
        writer.writerows(records)

    print(
        f"Generated {len(records)} new transactions "
        f"→ {OUTPUT}"
    )


if __name__ == "__main__":
    main()
