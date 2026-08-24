SELECT
    ROW_NUMBER() OVER (ORDER BY account_id) AS account_key,
    account_id,
    account_type,
    country,
    created_at,
    status
FROM {{ ref('stg_accounts') }}