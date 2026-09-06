-- sql/carrier_analysis.sql

-- 4. Carrier performance
SELECT 
    carrier,
    COUNT(*) AS total_flights,
    CAST(SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(*) AS cancellation_rate,
    CAST(SUM(CASE WHEN departure_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END) AS departure_delay_rate,
    avg(departure_delay_min) AS avg_departure_delay_min,
    avg(arrival_delay_min) AS avg_arrival_delay_min,
    CAST(SUM(CASE WHEN arrival_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END) AS arrival_delay_rate
FROM flights
GROUP BY carrier
ORDER BY total_flights DESC;

