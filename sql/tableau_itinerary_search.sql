-- sql/tableau_itinerary_search.sql
-- Example Queries for Tableau Custom SQL / Native Filtering

-- These queries demonstrate how Tableau should query the `tableau_itinerary_search` view.
-- By passing filters in the WHERE clause BEFORE the ORDER BY, DuckDB pushes the predicates
-- down into the Parquet files, making the queries run in milliseconds over 27M rows.

-- Parameters mapped from Tableau user selections:
-- Origin = 'JFK', Destination = 'LAX', etc.

-- 1. Fastest options for a selected origin/destination
SELECT *
FROM tableau_itinerary_search
WHERE origin = 'JFK' AND destination = 'LAX'
ORDER BY 
    total_scheduled_journey_time_min ASC,
    scheduled_connection_time_min ASC
LIMIT 10;


-- 2. Most reliable options (highest buffer, lowest delays)
SELECT *
FROM tableau_itinerary_search
WHERE origin = 'JFK' AND destination = 'LAX'
ORDER BY 
    connection_buffer_min DESC,
    inbound_arrival_delay_min ASC,
    outbound_departure_delay_min ASC
LIMIT 10;


-- 3. Lowest-risk options (best risk band, highest buffer, fastest)
SELECT *
FROM tableau_itinerary_search
WHERE origin = 'JFK' AND destination = 'LAX'
ORDER BY 
    CASE connection_risk_band
        WHEN 'Low' THEN 5
        WHEN 'Moderate' THEN 4
        WHEN 'High' THEN 3
        WHEN 'Critical' THEN 2
        WHEN 'Operationally Infeasible' THEN 1
        ELSE 0
    END DESC,
    connection_buffer_min DESC,
    total_scheduled_journey_time_min ASC
LIMIT 10;


-- 4. Balanced options (approximate without window functions)
-- A proxy for the Python balanced ranking logic that penalizes high delays and high journey time,
-- and rewards high buffers, running instantly in SQL.
SELECT *
FROM tableau_itinerary_search
WHERE origin = 'JFK' AND destination = 'LAX'
ORDER BY 
    (COALESCE(inbound_arrival_delay_min, 0) + COALESCE(outbound_departure_delay_min, 0)) ASC,
    total_scheduled_journey_time_min ASC,
    connection_buffer_min DESC
LIMIT 10;


-- 5. Options filtered by maximum journey time
SELECT *
FROM tableau_itinerary_search
WHERE origin = 'JFK' AND destination = 'LAX'
  AND total_scheduled_journey_time_min <= 420  -- 7 hours
ORDER BY total_scheduled_journey_time_min ASC
LIMIT 10;


-- 6. Options filtered by minimum connection buffer
SELECT *
FROM tableau_itinerary_search
WHERE origin = 'JFK' AND destination = 'LAX'
  AND connection_buffer_min >= 60  -- Minimum 1 hour buffer
ORDER BY connection_buffer_min ASC
LIMIT 10;


-- 7. Options filtered by connection airport
SELECT *
FROM tableau_itinerary_search
WHERE origin = 'JFK' AND destination = 'LAX'
  AND connection_airport = 'ORD'
ORDER BY total_scheduled_journey_time_min ASC
LIMIT 10;


-- 8. Options filtered by carrier (same carrier preference)
SELECT *
FROM tableau_itinerary_search
WHERE origin = 'JFK' AND destination = 'LAX'
  AND inbound_carrier = 'DL'
  AND same_carrier = TRUE
ORDER BY total_scheduled_journey_time_min ASC
LIMIT 10;

