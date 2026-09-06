import duckdb
import os
import pandas as pd
from src.cleaning import clean_bts_flight_data
from src.transformations import add_airport_timezones, create_flight_timestamps, create_flight_fact_table

def build_database():
    db_path = "data/processed/flight_analytics.duckdb"
    
    # Ensure processed dir exists
    os.makedirs("data/processed", exist_ok=True)
    
    # Persist flight_fact to Parquet if it doesn't exist
    fact_parquet = "data/processed/flight_fact_2025_01.parquet"
    if not os.path.exists(fact_parquet):
        print(f"Creating {fact_parquet}...")
        # Since it's large, we read the whole csv and save it.
        # It's about 539k rows, fitting in memory easily for pandas.
        df_raw = pd.read_csv("data/raw/bts/2025/01/Jan2025.csv")
        df_clean = clean_bts_flight_data(df_raw)
        df_tz = add_airport_timezones(df_clean)
        df_ts = create_flight_timestamps(df_tz)
        fact = create_flight_fact_table(df_ts)
        fact.to_parquet(fact_parquet, index=False)
        print("Done.")

    conn = duckdb.connect(db_path)
    
    # Execute schema.sql to create views
    with open("sql/schema.sql", "r") as f:
        schema_sql = f.read()
    conn.execute(schema_sql)
    
    # Execute tableau_views.sql to create tableau semantic layer
    with open("sql/tableau_views.sql", "r") as f:
        tableau_sql = f.read()
    conn.execute(tableau_sql)
    
    # Persist connection_reliability to Parquet if it doesn't exist
    rel_parquet = "data/processed/connection_reliability_2025_01.parquet"
    if not os.path.exists(rel_parquet):
        print(f"Creating {rel_parquet} using DuckDB...")
        # This view was created by schema.sql
        conn.execute(f"COPY (SELECT * FROM connection_reliability) TO '{rel_parquet}' (FORMAT PARQUET);")
        print("Done.")
        
    # Redefine connection_reliability to point directly to the new parquet file for optimal performance
    conn.execute(f"CREATE OR REPLACE VIEW connection_reliability AS SELECT * FROM '{rel_parquet}'")
    
    print(f"Database built successfully at {db_path}.")
    conn.close()

if __name__ == "__main__":
    build_database()

