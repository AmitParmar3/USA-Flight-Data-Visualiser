import duckdb
conn = duckdb.connect(r'd:\Projects\Flight Logs\data\processed\flight_analytics.duckdb', read_only=True)
q = "SELECT column_name, data_type FROM information_schema.columns WHERE table_name = 'tableau_flight_performance' AND column_name LIKE '%Severe%'"
print(conn.execute(q).df())

