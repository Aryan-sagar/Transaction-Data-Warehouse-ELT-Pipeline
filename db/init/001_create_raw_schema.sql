-- Creates the schemas and raw tables that ingestion.py and the dbt
-- sources (models/staging/sources.yml) assume already exist.
--
-- Raw columns are kept as TEXT/loose types on purpose: the raw layer
-- holds whatever ingestion.py inserts verbatim (including the messy
-- values inject_anomalies.py deliberately produces), and stg_*.sql
-- models do the TRIM/UPPER/LOWER/CAST cleanup. Casting too early here
-- would defeat the point of testing that cleanup layer.

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
