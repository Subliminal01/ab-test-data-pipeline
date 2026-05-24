import streamlit as st
import duckdb
import pandas as pd

# Set up the page layout
st.set_page_config(page_title="Experiment Scorecard", layout="wide")
st.title("🧪 Automated A/B Test Scorecard")
st.markdown("Powered by **dbt**, **DuckDB**, and **Heavy SQL**")

# Connect to the DuckDB database dbt just built
# (By default, dbt-duckdb names the file after your project)
try:
    con = duckdb.connect('dev.duckdb', read_only=True)
    
    # Query the final data mart
    query = "SELECT * FROM fct_experiment_scorecard"
    df = con.execute(query).df()
    
    st.subheader("Results: checkout_button_color_v1")
    
    # Display metrics in a clean grid
    cols = st.columns(len(df))
    
    for index, row in df.iterrows():
        with cols[index]:
            st.markdown(f"### {row['metric_name']}")
            
            # Check for Statistical Significance (Z-Score > 1.96 or < -1.96 is 95% confidence)
            is_significant = abs(row['z_score']) >= 1.96
            
            if is_significant and row['lift_percentage'] > 0:
                status = "✅ SIGNIFICANT WIN"
                color = "normal" 
            elif is_significant and row['lift_percentage'] < 0:
                status = "❌ SIGNIFICANT LOSS"
                color = "inverse"
            else:
                status = "⚪ FLAT (Not Significant)"
                color = "off"

            st.metric(
                label=status,
                value=f"{row['treatment_value']}",
                delta=f"{row['lift_percentage']}% Lift vs Control ({row['control_value']})",
                delta_color=color
            )
            
            st.caption(f"**Z-Score:** {row['z_score']} (Requires > 1.96)")
            st.divider()

except duckdb.Error as e:
    st.error(f"Could not connect to database. Ensure dbt run finished successfully. Error: {e}")