import csv
import random
from pathlib import Path


RAW_DIR = Path("data/raw")


def load_transactions():
    path = RAW_DIR / "transactions.csv"

    with open(path, newline="", encoding="utf-8") as file:
        return list(csv.DictReader(file))


def save_transactions(records):
    path = RAW_DIR / "transactions.csv"

    with open(path, "w", newline="", encoding="utf-8") as file:
        writer = csv.DictWriter(
            file,
            fieldnames=records[0].keys(),
        )

        writer.writeheader()
        writer.writerows(records)


def inject_anomalies(records):
    print("Injecting data-quality anomalies...")

    # 1. Duplicate transactions
    duplicates = random.sample(records, 50)
    records.extend(duplicates)

    # 2. Missing account IDs
    for record in random.sample(records, 25):
        record["account_id"] = ""

    # 3. Invalid account references
    for record in random.sample(records, 25):
        record["account_id"] = "ACC_INVALID"

    # 4. Invalid amounts
    for record in random.sample(records, 25):
        record["amount"] = "-500.00"

    # 5. Missing merchant IDs
    for record in random.sample(records, 25):
        record["merchant_id"] = ""

    return records


def main():
    records = load_transactions()

    print(f"Original records: {len(records):,}")

    records = inject_anomalies(records)

    save_transactions(records)

    print(f"Corrupted records: {len(records):,}")


if __name__ == "__main__":
    main()