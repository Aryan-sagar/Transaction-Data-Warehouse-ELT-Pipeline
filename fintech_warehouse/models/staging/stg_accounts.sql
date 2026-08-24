WITH source AS (

    SELECT *
    FROM {{ source('raw', 'accounts') }}

),

cleaned AS (

    SELECT DISTINCT ON (account_id)

        TRIM(account_id) AS account_id,

        LOWER(TRIM(account_type)) AS account_type,

        UPPER(TRIM(country)) AS country,

        created_at::TIMESTAMP AS created_at,

        LOWER(TRIM(status)) AS status,

        ingested_at

    FROM source

    WHERE NULLIF(TRIM(account_id), '') IS NOT NULL
      AND created_at IS NOT NULL

    ORDER BY
        account_id,
        ingested_at DESC

)

SELECT *
FROM cleaned