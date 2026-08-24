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
    t.transaction_timestamp

FROM {{ ref('stg_transactions') }} t

INNER JOIN {{ ref('dim_accounts') }} a
    ON t.account_id = a.account_id

INNER JOIN {{ ref('dim_merchants') }} m
    ON t.merchant_id = m.merchant_id

INNER JOIN {{ ref('dim_date') }} d
    ON t.transaction_timestamp::DATE = d.full_date

{% if is_incremental() %}

WHERE t.transaction_timestamp >
    (
        SELECT COALESCE(
            MAX(transaction_timestamp),
            TIMESTAMP '1900-01-01'
        )
        FROM {{ this }}
    )

{% endif %}