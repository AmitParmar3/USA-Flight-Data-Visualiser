-- sql/route_analysis.sql

-- 5. Top routes by frequency
SELECT 
    origin,
    destination,
    COUNT(*) AS total_flights,
    COUNT(DISTINCT carrier) AS distinct_carriers
FROM flights
GROUP BY origin, destination
ORDER BY total_flights DESC
LIMIT 50;

-- 6. Route delay performance
SELECT 
    origin,
    destination,
    COUNT(*) AS total_flights,
    avg(departure_delay_min) AS avg_departure_delay_min,
    avg(arrival_delay_min) AS avg_arrival_delay_min,
    CAST(SUM(CASE WHEN arrival_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END) AS arrival_delay_rate
FROM flights
WHERE is_cancelled = False
GROUP BY origin, destination
HAVING COUNT(*) > 100
ORDER BY arrival_delay_rate DESC;

