{{ config(materialized='table') }}

    WITH variant_metrics AS (
        -- Step 1: Calculate N, Mean, and Variance for each group
        SELECT 
            variant_id,
            COUNT(user_id) AS users,
            
            -- Conversion Rate (Proportion Metric)
            AVG(has_converted) AS cvr_mean,
            VAR_POP(has_converted) AS cvr_variance,
            
            -- Revenue per User (Continuous Metric)
            AVG(total_revenue) AS rev_mean,
            VAR_POP(total_revenue) AS rev_variance
        FROM {{ ref('int_subject_rollups') }}
        GROUP BY 1
    ),
    
    pivoted_metrics AS (
        -- Step 2: Pivot the data so Control and Treatment are on the same row
        SELECT
            MAX(CASE WHEN variant_id = 'control' THEN users END) AS control_users,
            MAX(CASE WHEN variant_id = 'treatment' THEN users END) AS treatment_users,
            
            MAX(CASE WHEN variant_id = 'control' THEN cvr_mean END) AS control_cvr,
            MAX(CASE WHEN variant_id = 'treatment' THEN cvr_mean END) AS treatment_cvr,
            MAX(CASE WHEN variant_id = 'control' THEN cvr_variance END) AS control_cvr_var,
            MAX(CASE WHEN variant_id = 'treatment' THEN cvr_variance END) AS treatment_cvr_var,

            MAX(CASE WHEN variant_id = 'control' THEN rev_mean END) AS control_rev,
            MAX(CASE WHEN variant_id = 'treatment' THEN rev_mean END) AS treatment_rev,
            MAX(CASE WHEN variant_id = 'control' THEN rev_variance END) AS control_rev_var,
            MAX(CASE WHEN variant_id = 'treatment' THEN rev_variance END) AS treatment_rev_var
        FROM variant_metrics
    )

    -- Step 3: Calculate the Lifts and Z-Scores using purely SQL math
    SELECT
        'Conversion Rate' AS metric_name,
        ROUND(control_cvr, 4) AS control_value,
        ROUND(treatment_cvr, 4) AS treatment_value,
        ROUND((treatment_cvr - control_cvr) / NULLIF(control_cvr, 0) * 100, 2) AS lift_percentage,
        -- Z-Score Formula: (Mean T - Mean C) / SQRT( (Var T / N T) + (Var C / N C) )
        ROUND((treatment_cvr - control_cvr) / SQRT((control_cvr_var/control_users) + (treatment_cvr_var/treatment_users)), 3) AS z_score
    FROM pivoted_metrics

    UNION ALL

    SELECT
        'Revenue per User' AS metric_name,
        ROUND(control_rev, 4) AS control_value,
        ROUND(treatment_rev, 4) AS treatment_value,
        ROUND((treatment_rev - control_rev) / NULLIF(control_rev, 0) * 100, 2) AS lift_percentage,
        ROUND((treatment_rev - control_rev) / SQRT((control_rev_var/control_users) + (treatment_rev_var/treatment_users)), 3) AS z_score
    FROM pivoted_metrics
