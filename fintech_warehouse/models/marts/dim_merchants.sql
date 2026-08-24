SELECT
    ROW_NUMBER() OVER (ORDER BY merchant_id) AS merchant_key,
    merchant_id,
    merchant_name,
    category,
    country,
    risk_category,
    created_at
FROM {{ ref('stg_merchants') }}
