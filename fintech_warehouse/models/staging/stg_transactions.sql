WITH source AS (

    SELECT *
    FROM {{ source('raw', 'transactions') }}

),

cleaned AS (

    SELECT DISTINCT ON (transaction_id)

        transaction_id,

        NULLIF(TRIM(account_id), '') AS account_id,

        NULLIF(TRIM(merchant_id), '') AS merchant_id,

        amount::NUMERIC(18,2) AS amount,

        UPPER(TRIM(currency)) AS currency,

        LOWER(TRIM(status)) AS status,

        LOWER(TRIM(payment_method)) AS payment_method,

        transaction_timestamp::TIMESTAMP
            AS transaction_timestamp,

        ingested_at

    FROM source

    WHERE NULLIF(TRIM(account_id), '') IS NOT NULL
      AND NULLIF(TRIM(merchant_id), '') IS NOT NULL
      AND amount::NUMERIC > 0
      AND transaction_timestamp IS NOT NULL

    ORDER BY
        transaction_id,
        ingested_at DESC

),

valid_accounts AS (

    SELECT account_id
    FROM {{ source('raw', 'accounts') }}

),

valid_merchants AS (

    SELECT merchant_id
    FROM {{ source('raw', 'merchants') }}

)

SELECT
    c.*

FROM cleaned c

INNER JOIN valid_accounts a
    ON c.account_id = TRIM(a.account_id)

INNER JOIN valid_merchants m
    ON c.merchant_id = TRIM(m.merchant_id)