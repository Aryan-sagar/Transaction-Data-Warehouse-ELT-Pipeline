{{ config(materialized='table') }}

SELECT
    COUNT(*) AS total_transactions,

    COUNT(*) FILTER (
        WHERE status = 'success'
    ) AS successful_transactions,

    COUNT(*) FILTER (
        WHERE status = 'failed'
    ) AS failed_transactions,

    COUNT(*) FILTER (
        WHERE status = 'pending'
    ) AS pending_transactions,

    SUM(amount) AS total_amount,

    COALESCE(
        SUM(amount) FILTER (
            WHERE status = 'success'
        ),
        0
    ) AS successful_amount,

    COALESCE(
        SUM(amount) FILTER (
            WHERE status = 'failed'
        ),
        0
    ) AS failed_amount,

    COALESCE(
        SUM(amount) FILTER (
            WHERE status = 'pending'
        ),
        0
    ) AS pending_amount,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE status = 'success'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS success_rate,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE status = 'failed'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS failure_rate,

    ROUND(
        100.0 * COUNT(*) FILTER (
            WHERE status = 'pending'
        ) / NULLIF(COUNT(*), 0),
        2
    ) AS pending_rate

FROM {{ ref('fact_transactions') }}