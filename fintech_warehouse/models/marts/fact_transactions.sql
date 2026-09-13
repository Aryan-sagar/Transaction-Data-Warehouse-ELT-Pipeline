{{ config(
    materialized='incremental',
    unique_key='transaction_id',
    on_schema_change='sync_all_columns'
) }}

SELECT
    t.transaction_id,
    a.account_key,
    m.merchant_key,
    d.date_key,
    t.amount,
    t.currency,
    t.status,
    t.payment_method,
    t.transaction_timestamp,
    t.ingested_at AS source_ingested_at

FROM {{ ref('stg_transactions') }} t

INNER JOIN {{ ref('dim_accounts') }} a
    ON t.account_id = a.account_id

INNER JOIN {{ ref('dim_merchants') }} m
    ON t.merchant_id = m.merchant_id

INNER JOIN {{ ref('dim_date') }} d
    ON t.transaction_timestamp::DATE = d.full_date

{% if is_incremental() %}

-- Filter on ingested_at (when the row last landed in raw), not
-- transaction_timestamp. transaction_timestamp is fixed at the
-- source, so a status correction on an old transaction (e.g.
-- pending -> success) never crosses a transaction_timestamp
-- watermark and would silently never reach this table even though
-- ingestion.py re-upserts it. ingested_at moves forward on every
-- re-upsert, so corrections get picked up on the next incremental run.
WHERE t.ingested_at >
    (
        SELECT COALESCE(
            MAX(source_ingested_at),
            TIMESTAMP '1900-01-01'
        )
        FROM {{ this }}
    )

{% endif %}