import duckdb
import os
import pandas as pd
from src.cleaning import clean_bts_flight_data
from src.transformations import add_airport_timezones, create_flight_timestamps, create_flight_fact_table

def build_database():
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '..'))
    db_path = os.path.join(project_root, "data", "processed", "flight_analytics.duckdb")
    processed_dir = os.path.join(project_root, "data", "processed")
    os.makedirs(processed_dir, exist_ok=True)
    
    # Persist flight_fact to Parquet if it doesn't exist
    fact_parquet = os.path.join(processed_dir, "flight_fact_2025_01.parquet")
    if not os.path.exists(fact_parquet):
        print(f"Creating {fact_parquet}...")
        # Since it's large, we read the whole csv and save it.
        # It's about 539k rows, fitting in memory easily for pandas.
        raw_csv = os.path.join(project_root, "data", "raw", "bts", "2025", "01", "Jan2025.csv")
        df_raw = pd.read_csv(raw_csv)
        df_clean = clean_bts_flight_data(df_raw)
        df_tz = add_airport_timezones(df_clean)
        df_ts = create_flight_timestamps(df_tz)
        fact = create_flight_fact_table(df_ts)
        fact.to_parquet(fact_parquet, index=False)
        print("Done.")

    conn = duckdb.connect(db_path)
    
    # Execute schema.sql to create views with absolute paths
    schema_path = os.path.join(project_root, "sql", "schema.sql")
    with open(schema_path, "r") as f:
        schema_sql = f.read()
    
    # Replace relative paths with absolute paths for DuckDB views
    # DuckDB handles forward slashes well on Windows
    project_root_fwd = project_root.replace('\\', '/')
    schema_sql = schema_sql.replace("'data/processed/", f"'{project_root_fwd}/data/processed/")
    conn.execute(schema_sql)
    
    # Execute Tableau-facing semantic views
    tableau_views = [
        "sql/tableau_flight_performance.sql",
        "sql/tableau_connection_reliability.sql",
        "sql/tableau_itinerary_search.sql"
    ]
    
    for view_file in tableau_views:
        view_path = os.path.join(project_root, view_file)
        with open(view_path, "r") as f:
            view_sql = f.read()
        conn.execute(view_sql)
        
    # Clean up obsolete views
    obsolete_views = [
        "tableau_airport_performance",
        "tableau_carrier_performance",
        "tableau_route_performance",
        "tableau_itinerary_options"
    ]
    for ov in obsolete_views:
        conn.execute(f"DROP VIEW IF EXISTS {ov}")
    
    # Persist connection_reliability to Parquet if it doesn't exist
    rel_parquet = os.path.join(processed_dir, "connection_reliability_2025_01.parquet")
    rel_parquet_fwd = rel_parquet.replace('\\', '/')
    if not os.path.exists(rel_parquet):
        print(f"Creating {rel_parquet} using DuckDB...")
        # This view was created by schema.sql
        conn.execute(f"COPY (SELECT * FROM connection_reliability) TO '{rel_parquet_fwd}' (FORMAT PARQUET);")
        print("Done.")
        
    # Redefine connection_reliability to point directly to the new parquet file for optimal performance
    conn.execute(f"CREATE OR REPLACE VIEW connection_reliability AS SELECT * FROM '{rel_parquet_fwd}'")
    
    print(f"Database built successfully at {db_path}.")
    conn.close()

if __name__ == "__main__":
    build_database()

