-- sql/airport_analysis.sql

-- 1. Top airports by flight volume
SELECT 
    origin AS airport,
    COUNT(*) AS total_departures,
    COUNT(DISTINCT carrier) AS distinct_carriers
FROM flights
GROUP BY origin
ORDER BY total_departures DESC
LIMIT 20;

-- 2. Airport departure delay rate
SELECT 
    origin AS airport,
    COUNT(*) AS total_flights,
    SUM(CASE WHEN departure_delay_min > 15 THEN 1 ELSE 0 END) AS delayed_flights,
    CAST(SUM(CASE WHEN departure_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(*) AS departure_delay_rate,
    avg(departure_delay_min) AS avg_departure_delay_min
FROM flights
WHERE is_cancelled = False
GROUP BY origin
HAVING COUNT(*) > 1000
ORDER BY departure_delay_rate DESC;

-- 3. Airport cancellation rate
SELECT 
    origin AS airport,
    COUNT(*) AS total_scheduled_flights,
    SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) AS cancelled_flights,
    CAST(SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(*) AS cancellation_rate
FROM flights
GROUP BY origin
HAVING COUNT(*) > 1000
ORDER BY cancellation_rate DESC;

