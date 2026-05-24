{{ config(materialized='table') }}

    WITH user_events AS (
        SELECT 
            user_id,
            SUM(CASE WHEN event_name = 'pageview' THEN 1 ELSE 0 END) AS pageviews,
            SUM(CASE WHEN event_name = 'purchase' THEN 1 ELSE 0 END) AS purchases,
            SUM(event_value) AS total_revenue
        FROM {{ ref('stg_events') }}
        GROUP BY 1
    )

    SELECT 
        a.user_id,
        a.variant_id,
        COALESCE(e.pageviews, 0) AS pageviews,
        COALESCE(e.purchases, 0) AS purchases,
        COALESCE(e.total_revenue, 0.0) AS total_revenue,
        -- Binary flag needed later for proportion metrics (Conversion Rate)
        CASE WHEN COALESCE(e.purchases, 0) > 0 THEN 1 ELSE 0 END AS has_converted
    FROM {{ source('data_lake', 'raw_assignments') }} a
    LEFT JOIN user_events e ON a.user_id = e.user_id
