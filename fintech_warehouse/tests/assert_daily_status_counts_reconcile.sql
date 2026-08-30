-- Fails if any row where successful + failed + pending != total.
-- Generic not_null/unique tests can't catch this kind of cross-column
-- consistency bug (e.g. a status falling through every FILTER clause
-- if new status values are ever introduced upstream).

SELECT
    date_key,
    total_transactions,
    successful_transactions + failed_transactions + pending_transactions
        AS summed_transactions

FROM {{ ref('fct_daily_transactions') }}

WHERE total_transactions
    != successful_transactions + failed_transactions + pending_transactions
