import duckdb
import pandas as pd
from src.analytics.airport import calculate_airport_performance

conn = duckdb.connect(r'd:\Projects\Flight Logs\data\processed\flight_analytics.duckdb', read_only=True)

# 1. Fetch test flights from DuckDB and calculate manually using eligible denominators
print("Fetching flights to feed to python module...")
flights_df = conn.execute("SELECT * FROM flights").df()

# Calculate true eligible rates to match the user's requirement
departures = flights_df.groupby("origin").apply(
    lambda x: x[x['departure_delay_min'] >= 60]['flight_id'].count() / x['departure_delay_min'].count()
).rename("departure_severe_60_rate")

arrivals = flights_df.groupby("destination").apply(
    lambda x: x[x['arrival_delay_min'] >= 60]['flight_id'].count() / x['arrival_delay_min'].count()
).rename("arrival_severe_60_rate")

python_metrics = pd.DataFrame({
    'departure_severe_60_rate': departures,
    'arrival_severe_60_rate': arrivals
}).reset_index().rename(columns={'index': 'airport'})

# 2. Fetch the newly fixed Tableau Airport metrics directly from duckdb
sql_metrics = conn.execute("""
    SELECT 
        "Airport",
        "Severe Arrival Delay Rate" AS sql_arr_severe,
        "Severe Departure Delay Rate" AS sql_dep_severe
    FROM tableau_flight_performance
    WHERE record_type = 'Airport'
""").df()

# 3. Compare top 5 airports
test_airports = ["OKC", "SAT", "FLL", "PNS", "MTJ"]
print("\n--- COMPARISON ---")

for apt in test_airports:
    # Python results
    py_row = python_metrics[python_metrics['airport'] == apt].iloc[0]
    py_arr = py_row['arrival_severe_60_rate']
    py_dep = py_row['departure_severe_60_rate']
    
    # SQL results
    sql_row = sql_metrics[sql_metrics['Airport'] == apt].iloc[0]
    sql_arr = sql_row['sql_arr_severe']
    sql_dep = sql_row['sql_dep_severe']
    
    match_arr = abs(py_arr - sql_arr) < 1e-6 if pd.notna(py_arr) else pd.isna(sql_arr)
    match_dep = abs(py_dep - sql_dep) < 1e-6 if pd.notna(py_dep) else pd.isna(sql_dep)
    
    print(f"Airport: {apt}")
    print(f"  Arrival Severe >= 60 | Python: {py_arr:.6f} | SQL: {sql_arr:.6f} | Match: {match_arr}")
    print(f"  Depart. Severe >= 60 | Python: {py_dep:.6f} | SQL: {sql_dep:.6f} | Match: {match_dep}")

