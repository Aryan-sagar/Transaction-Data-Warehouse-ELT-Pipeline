WITH source AS (

    SELECT *
    FROM {{ source('raw', 'merchants') }}

),

cleaned AS (

    SELECT DISTINCT ON (merchant_id)

        TRIM(merchant_id) AS merchant_id,

        TRIM(merchant_name) AS merchant_name,

        LOWER(TRIM(category)) AS category,

        UPPER(TRIM(country)) AS country,

        LOWER(TRIM(risk_category)) AS risk_category,

        created_at::TIMESTAMP AS created_at,

        ingested_at

    FROM source

    WHERE NULLIF(TRIM(merchant_id), '') IS NOT NULL
      AND NULLIF(TRIM(merchant_name), '') IS NOT NULL
      AND created_at IS NOT NULL

    ORDER BY
        merchant_id,
        ingested_at DESC

)

SELECT *
FROM cleaned
