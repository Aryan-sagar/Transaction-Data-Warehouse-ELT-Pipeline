{{ config(materialized='table') }}

SELECT
    dm.risk_category,

    COUNT(*) AS total_transactions,

    COUNT(*) FILTER (
        WHERE ft.status = 'success'
    ) AS successful_transactions,

    COUNT(*) FILTER (
        WHERE ft.status = 'failed'
    ) AS failed_transactions,

    COUNT(*) FILTER (
        WHERE ft.status = 'pending'
    ) AS pending_transactions,

    SUM(ft.amount) AS total_amount,

    COALESCE(
        SUM(ft.amount) FILTER (
            WHERE ft.status = 'success'
        ),
        0
    ) AS successful_amount,

    COALESCE(
        SUM(ft.amount) FILTER (
            WHERE ft.status = 'failed'
        ),
        0
    ) AS failed_amount,

    COALESCE(
        SUM(ft.amount) FILTER (
            WHERE ft.status = 'pending'
        ),
        0
    ) AS pending_amount,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE ft.status = 'success'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS success_rate

FROM {{ ref('fact_transactions') }} ft

INNER JOIN {{ ref('dim_merchants') }} dm
    ON ft.merchant_key = dm.merchant_key

GROUP BY dm.risk_category

ORDER BY total_transactions DESC
