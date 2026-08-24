WITH dates AS (

    SELECT
        generate_series(
            DATE '2026-01-01',
            DATE '2027-12-31',
            INTERVAL '1 day'
        )::DATE AS full_date

)

SELECT
    TO_CHAR(full_date, 'YYYYMMDD')::INTEGER AS date_key,
    full_date,
    EXTRACT(YEAR FROM full_date)::INTEGER AS year,
    EXTRACT(QUARTER FROM full_date)::INTEGER AS quarter,
    EXTRACT(MONTH FROM full_date)::INTEGER AS month,
    TO_CHAR(full_date, 'Month') AS month_name,
    EXTRACT(WEEK FROM full_date)::INTEGER AS week,
    EXTRACT(DAY FROM full_date)::INTEGER AS day,
    TO_CHAR(full_date, 'Day') AS day_name,
    EXTRACT(ISODOW FROM full_date) IN (6, 7) AS is_weekend
FROM dates