# 🧪 Automated A/B Test Scorecard: Local Data Lakehouse Pipeline

An end-to-end Extract, Load, and Transform (ELT) data pipeline simulating a modern data lakehouse architecture. This project processes 5 million raw telemetry events into an interactive A/B testing scorecard, calculating statistical significance entirely within the data warehouse.

## 🏗️ Architecture & Tech Stack

This project demonstrates a decoupled storage and compute architecture, utilizing the following stack:
* **Storage (Data Lake):** Apache Parquet
* **Compute (Data Warehouse):** DuckDB
* **Transformation:** dbt (Data Build Tool)
* **Orchestration:** Apache Airflow
* **Visualization:** Streamlit & Python

---

## ⚙️ Pipeline Workflow

### 1. Data Ingestion & Storage (`generate_data.py`)
Simulates the daily arrival of web telemetry data. Generates 5 million rows of randomized user events (pageviews, add-to-carts, purchases) and exports them directly into highly compressed **Parquet files**. This simulates a Hive-style data lake where storage is decoupled from the database engine.

### 2. Transformation & Modeling (`dbt`)
Utilizes **dbt** paired with **DuckDB** to execute transformations purely in SQL. The architecture follows best practices (`staging`, `intermediate`, `marts`):
* **Staging (Incremental Models):** Implements `is_incremental()` logic to only scan and process new events based on timestamps, optimizing compute resources for large datasets.
* **Intermediate (Subject Rollups):** Uses complex joins and aggregations to flatten event-level data into 100,000 independent subject-level summaries.
* **Marts (Heavy SQL & Math):** Calculates Population Variance (`VAR_POP`), means, and N-counts to compute the **Z-Score** for statistical significance natively in SQL, avoiding the need to export raw data to Python for statistical testing.

### 3. Orchestration (`experiment_dag.py`)
An **Apache Airflow** DAG defines the dependency graph, ensuring data integrity. It sets a daily schedule to execute the data extraction (`Task 1`) and strictly triggers the dbt transformations (`Task 2`) only upon successful data arrival.

### 4. Visualization (`app.py`)
A **Streamlit** frontend directly queries the DuckDB data mart to visualize the final scorecard, automatically highlighting statistically significant lifts (Z-Score > 1.96) in conversion rates and revenue per user.

---

## 🚀 How to Run Locally

1. **Clone the repository and install dependencies:**
   ```bash
   git clone [https://github.com/YourUsername/ab-test-data-pipeline.git](https://github.com/YourUsername/ab-test-data-pipeline.git)
   cd ab-test-data-pipeline
   python -m venv venv
   source venv/bin/activate  # Or `venv\Scripts\activate` on Windows
   pip install -r requirements.txt


2. **Generate the Parquet Data Lake:**
Bash
python generate_data.py

3. **Run the dbt pipeline (executes the SQL math):**
Bash
cd experiment_engine
dbt run

4. **Launch the Streamlit Dashboard:**
Bash
streamlit run app.py
