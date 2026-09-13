CREATE SCHEMA IF NOT EXISTS raw;
CREATE SCHEMA IF NOT EXISTS staging;
CREATE SCHEMA IF NOT EXISTS mart;

CREATE TABLE IF NOT EXISTS raw.accounts (
    account_id      TEXT PRIMARY KEY,
    account_type    TEXT,
    country         TEXT,
    created_at      TEXT,
    status          TEXT,
    ingested_at     TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.merchants (
    merchant_id     TEXT PRIMARY KEY,
    merchant_name   TEXT,
    category        TEXT,
    country         TEXT,
    risk_category   TEXT,
    created_at      TEXT,
    ingested_at     TIMESTAMP NOT NULL DEFAULT now()
);

CREATE TABLE IF NOT EXISTS raw.transactions (
    transaction_id          TEXT PRIMARY KEY,
    account_id              TEXT,
    merchant_id             TEXT,
    amount                  TEXT,
    currency                TEXT,
    status                  TEXT,
    payment_method          TEXT,
    transaction_timestamp   TEXT,
    ingested_at             TIMESTAMP NOT NULL DEFAULT now()
);
CREATE TABLE IF NOT EXISTS raw.quarantine_rows (
    quarantine_id   BIGSERIAL PRIMARY KEY,
    source_file     TEXT NOT NULL,
    row_number      INTEGER NOT NULL,
    raw_data        JSONB NOT NULL,
    error_reason    TEXT NOT NULL,
    quarantined_at  TIMESTAMP NOT NULL DEFAULT now()
);