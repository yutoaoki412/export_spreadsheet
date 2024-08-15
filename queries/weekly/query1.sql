WITH source AS (
    SELECT
        refresh_date,
        rank,
        term
    FROM `bigquery-public-data.google_trends.international_top_rising_terms`
    WHERE country_name = "Japan"
    AND refresh_date BETWEEN '{start_date}' AND '{end_date}'
)
,final AS (
    SELECT DISTINCT
        rank,
        term,
    FROM source
    ORDER BY rank
)
SELECT * FROM final LIMIT 1000