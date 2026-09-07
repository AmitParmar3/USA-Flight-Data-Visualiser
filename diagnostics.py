import duckdb

conn = duckdb.connect(r'd:\Projects\Flight Logs\data\processed\flight_analytics.duckdb', read_only=True)

print('--- QUERY A ---')
print(conn.execute('''
SELECT record_type, COUNT(*)
FROM tableau_flight_performance
GROUP BY record_type
ORDER BY record_type;
''').df().to_string())

print('\n--- QUERY B ---')
print(conn.execute('''
SELECT
    "Airport",
    "Severe Arrival Delay Rate",
    "Severe Departure Delay Rate"
FROM tableau_flight_performance
WHERE record_type = 'Airport'
  AND Airport IN ('OKC','SAT','FLL','PNS','MTJ');
''').df().to_string())

print('\n--- QUERY C ---')
print(conn.execute('''
DESCRIBE tableau_flight_performance;
''').df()[['column_name', 'column_type']].to_string())

print('\n--- QUERY D ---')
print(conn.execute('''
SELECT
    MIN("Severe Arrival Delay Rate"),
    MAX("Severe Arrival Delay Rate"),
    AVG("Severe Arrival Delay Rate"),
    COUNT(*),
    COUNT("Severe Arrival Delay Rate")
FROM tableau_flight_performance
WHERE record_type = 'Airport';
''').df().to_string())

