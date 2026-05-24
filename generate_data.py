import pandas as pd
import numpy as np
import duckdb
import uuid
from datetime import datetime, timedelta

NUM_USERS = 100_000
NUM_EVENTS = 5_000_000

np.random.seed(42)

print("Generating Users...")
users_df = pd.DataFrame({
    'user_id': np.arange(1, NUM_USERS + 1),
    'country': np.random.choice(['US', 'UK', 'IN', 'CA'], NUM_USERS, p=[0.4, 0.2, 0.3, 0.1]),
    'device_type': np.random.choice(['mobile', 'desktop', 'tablet'], NUM_USERS, p=[0.7, 0.2, 0.1]),
    'account_age_days': np.random.randint(1, 1000, NUM_USERS)
})

print("Generating Assignments...")
assignments_df = pd.DataFrame({
    'user_id': users_df['user_id'],
    'experiment_id': 'checkout_button_color_v1',
    'variant_id': np.random.choice(['control', 'treatment'], NUM_USERS, p=[0.495, 0.505]),
    'assignment_timestamp': [datetime(2026, 5, 1) + timedelta(seconds=np.random.randint(0, 86400*14)) for _ in range(NUM_USERS)]
})

print("Generating 5 Million Events...")
event_user_ids = np.random.choice(users_df['user_id'], NUM_EVENTS)
events_df = pd.DataFrame({'user_id': event_user_ids})
events_df = events_df.merge(assignments_df[['user_id', 'variant_id']], on='user_id', how='left')

is_treatment = events_df['variant_id'] == 'treatment'
event_types = np.random.choice(['pageview', 'add_to_cart', 'purchase'], size=NUM_EVENTS, p=[0.80, 0.10, 0.10])

treatment_boost_mask = is_treatment & (np.random.rand(NUM_EVENTS) < 0.02)
event_types[treatment_boost_mask] = 'purchase'
events_df['event_name'] = event_types

revenue = np.zeros(NUM_EVENTS)
is_purchase = events_df['event_name'] == 'purchase'
revenue[is_purchase & ~is_treatment] = np.random.normal(50, 10, size=(is_purchase & ~is_treatment).sum())
revenue[is_purchase & is_treatment] = np.random.normal(52, 10, size=(is_purchase & is_treatment).sum())
events_df['event_value'] = np.clip(revenue, 0, None)

events_df['timestamp'] = [datetime(2026, 5, 1) + timedelta(days=np.random.randint(0, 14), seconds=np.random.randint(0, 86400)) for _ in range(NUM_EVENTS)]

# NEW: Add a unique event ID so dbt can process data incrementally
events_df['event_id'] = [str(uuid.uuid4()) for _ in range(NUM_EVENTS)]
events_df = events_df.drop(columns=['variant_id'])

print("Writing to Parquet files (Simulating Hive Storage)...")
# NEW: Use DuckDB to natively write Pandas DataFrames into Parquet files
duckdb.sql("COPY users_df TO 'users.parquet' (FORMAT PARQUET)")
duckdb.sql("COPY assignments_df TO 'assignments.parquet' (FORMAT PARQUET)")
duckdb.sql("COPY events_df TO 'events.parquet' (FORMAT PARQUET)")

print("Success! Data exported as Parquet.")