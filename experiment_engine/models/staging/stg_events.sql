{{ config(
        materialized='incremental',
        unique_key='event_id'
    ) }}

    SELECT 
        event_id,
        user_id,
        event_name,
        event_value,
        timestamp
    FROM {{ source('data_lake', 'raw_events') }}

    {% if is_incremental() %}
      WHERE timestamp > (SELECT MAX(timestamp) FROM {{ this }})
    {% endif %}
