import duckdb
conn = duckdb.connect(r'd:\Projects\Flight Logs\data\processed\flight_analytics.duckdb', read_only=True)

query1 = """
SELECT
    record_type,
    COUNT(*) AS row_count,
    COUNT("Severe Arrival Delay Rate") AS severe_arrival_non_null,
    COUNT("Severe Departure Delay Rate") AS severe_departure_non_null
FROM tableau_flight_performance
GROUP BY record_type
ORDER BY record_type;
"""

query2 = """
SELECT
    "Airport",
    "Airport Flight Volume",
    "Arrival Delay Rate",
    "Severe Arrival Delay Rate",
    "Severe Departure Delay Rate"
FROM tableau_flight_performance
WHERE record_type = 'Airport'
LIMIT 10;
"""

print('--- QUERY 1 RESULTS ---')
print(conn.execute(query1).df().to_string(index=False))

print('\n--- QUERY 2 RESULTS ---')
print(conn.execute(query2).df().to_string(index=False))

