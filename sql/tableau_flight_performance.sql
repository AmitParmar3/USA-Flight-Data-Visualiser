-- sql/tableau_flight_performance.sql
-- Purpose: Unified Tableau semantic layer for Dashboards 1-4.
-- Grain: Polymorphic grain using UNION ALL (Flight, Airport, Carrier, Route).
-- This design allows independent analysis across different domains without duplicating flight records
-- or artificially linking aggregated airport metrics to just origins or destinations.

CREATE OR REPLACE VIEW tableau_flight_performance AS

-- =========================================================
-- 1. FLIGHT GRAIN
-- =========================================================
SELECT 
    'Flight' AS record_type,
    
    -- Identity
    flight_id,
    flight_date,
    carrier AS Carrier,
    flight_number,
    origin AS Origin,
    destination AS Destination,
    origin || '-' || destination AS Route,
    NULL AS Airport,
    
    -- Status
    flight_status,
    is_completed,
    is_cancelled,
    is_diverted,
    
    -- Timing
    scheduled_departure_utc,
    actual_departure_utc,
    scheduled_arrival_utc,
    actual_arrival_utc,
    scheduled_duration_min,
    actual_duration_min,
    
    -- Delays
    departure_delay_min,
    arrival_delay_min,
    CAST((departure_delay_min > 15) AS BOOLEAN) AS departure_delayed_15,
    CAST((arrival_delay_min > 15) AS BOOLEAN) AS arrival_delayed_15,
    CAST((departure_delay_min > 60) AS BOOLEAN) AS departure_severe_60,
    CAST((arrival_delay_min > 60) AS BOOLEAN) AS arrival_severe_60,
    CAST((departure_delay_min > 120) AS BOOLEAN) AS departure_severe_120,
    CAST((arrival_delay_min > 120) AS BOOLEAN) AS arrival_severe_120,
    delay_recovery_min,
    
    -- Other
    distance_miles AS distance,
    day_of_week,
    day_of_week_num,
    is_weekend,
    
    -- Network / Airport Aggregates (NULL for flight rows)
    CAST(NULL AS BIGINT) AS "Airport Flight Volume",
    CAST(NULL AS DOUBLE) AS "Arrival Delay Rate",
    CAST(NULL AS DOUBLE) AS "Departure Delay Rate",
    CAST(NULL AS DOUBLE) AS "Cancellation Rate",
    CAST(NULL AS DOUBLE) AS "Diversion Rate",
    CAST(NULL AS BIGINT) AS "Inbound Network Connectivity",
    CAST(NULL AS BIGINT) AS "Outbound Network Connectivity",
    
    -- Carrier Aggregates
    CAST(NULL AS BIGINT) AS "Carrier Flight Volume",
    CAST(NULL AS DOUBLE) AS "Severe Arrival Delay Rate",
    CAST(NULL AS DOUBLE) AS "Severe Departure Delay Rate",
    CAST(NULL AS DOUBLE) AS "Average Arrival Delay",
    CAST(NULL AS DOUBLE) AS "Median Arrival Delay",
    CAST(NULL AS DOUBLE) AS "Average Positive Arrival Delay",
    CAST(NULL AS DOUBLE) AS "Average Delay Recovery",
    
    -- Route Aggregates
    CAST(NULL AS BIGINT) AS "Route Flight Volume",
    CAST(NULL AS DOUBLE) AS "Route Arrival Delay Rate",
    CAST(NULL AS DOUBLE) AS "Route Departure Delay Rate",
    CAST(NULL AS DOUBLE) AS "Route Cancellation Rate",
    CAST(NULL AS BIGINT) AS "Route Frequency"

FROM flights

UNION ALL

-- =========================================================
-- 2. AIRPORT GRAIN
-- =========================================================
SELECT 
    'Airport' AS record_type,
    
    NULL AS flight_id,
    NULL AS flight_date,
    NULL AS Carrier,
    NULL AS flight_number,
    NULL AS Origin,
    NULL AS Destination,
    NULL AS Route,
    COALESCE(d.origin, a.destination) AS Airport,
    
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL,
    
    -- Airport Aggregates
    COALESCE(d.total_departures, 0) + COALESCE(a.total_arrivals, 0) AS "Airport Flight Volume",
    a.arrival_delay_rate AS "Arrival Delay Rate",
    d.departure_delay_rate AS "Departure Delay Rate",
    d.cancellation_rate AS "Cancellation Rate",
    d.diversion_rate AS "Diversion Rate",
    a.inbound_network_connectivity AS "Inbound Network Connectivity",
    d.outbound_network_connectivity AS "Outbound Network Connectivity",
    
    -- Carrier Aggregates (Populate Severe Delay Rates for Airport here)
    NULL AS "Carrier Flight Volume",
    a.arrival_severe_60_rate AS "Severe Arrival Delay Rate",
    d.departure_severe_60_rate AS "Severe Departure Delay Rate",
    NULL AS "Average Arrival Delay",
    NULL AS "Median Arrival Delay",
    NULL AS "Average Positive Arrival Delay",
    NULL AS "Average Delay Recovery",
    
    -- Route Aggregates
    NULL, NULL, NULL, NULL, NULL

FROM (
    SELECT 
        origin,
        COUNT(*) AS total_departures,
        CAST(SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(COUNT(*), 0) AS cancellation_rate,
        CAST(SUM(CASE WHEN is_diverted THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(COUNT(*), 0) AS diversion_rate,
        CAST(SUM(CASE WHEN departure_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(COUNT(departure_delay_min), 0) AS departure_delay_rate,
        CAST(SUM(CASE WHEN departure_delay_min >= 60 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(COUNT(departure_delay_min), 0) AS departure_severe_60_rate,
        COUNT(DISTINCT destination) AS outbound_network_connectivity
    FROM flights
    GROUP BY origin
) d
FULL OUTER JOIN (
    SELECT 
        destination,
        COUNT(*) AS total_arrivals,
        CAST(SUM(CASE WHEN arrival_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(COUNT(arrival_delay_min), 0) AS arrival_delay_rate,
        CAST(SUM(CASE WHEN arrival_delay_min >= 60 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(COUNT(arrival_delay_min), 0) AS arrival_severe_60_rate,
        COUNT(DISTINCT origin) AS inbound_network_connectivity
    FROM flights
    GROUP BY destination
) a ON d.origin = a.destination

UNION ALL

-- =========================================================
-- 3. CARRIER GRAIN
-- =========================================================
SELECT 
    'Carrier' AS record_type,
    
    NULL, NULL, 
    carrier AS Carrier,
    NULL, NULL, NULL, NULL, NULL,
    
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL,
    
    NULL,
    CAST(SUM(CASE WHEN arrival_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END), 0) AS "Arrival Delay Rate",
    CAST(SUM(CASE WHEN departure_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END), 0) AS "Departure Delay Rate",
    CAST(SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(COUNT(*), 0) AS "Cancellation Rate",
    CAST(SUM(CASE WHEN is_diverted THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(COUNT(*), 0) AS "Diversion Rate",
    NULL, NULL,
    
    -- Carrier Aggregates
    COUNT(*) AS "Carrier Flight Volume",
    CAST(SUM(CASE WHEN arrival_delay_min > 60 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END), 0) AS "Severe Arrival Delay Rate",
    CAST(SUM(CASE WHEN departure_delay_min > 60 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END), 0) AS "Severe Departure Delay Rate",
    avg(arrival_delay_min) AS "Average Arrival Delay",
    median(arrival_delay_min) AS "Median Arrival Delay",
    avg(CASE WHEN arrival_delay_min > 0 THEN arrival_delay_min ELSE NULL END) AS "Average Positive Arrival Delay",
    avg(delay_recovery_min) AS "Average Delay Recovery",
    
    NULL, NULL, NULL, NULL, NULL
    
FROM flights
GROUP BY carrier

UNION ALL

-- =========================================================
-- 4. ROUTE GRAIN
-- =========================================================
SELECT 
    'Route' AS record_type,
    
    NULL, NULL, NULL, NULL, 
    origin AS Origin,
    destination AS Destination,
    origin || '-' || destination AS Route,
    NULL,
    
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    NULL, NULL, NULL, NULL,
    
    NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    
    NULL, NULL, NULL, NULL, NULL, NULL, NULL,
    
    -- Route Aggregates
    COUNT(*) AS "Route Flight Volume",
    CAST(SUM(CASE WHEN arrival_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END), 0) AS "Route Arrival Delay Rate",
    CAST(SUM(CASE WHEN departure_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END), 0) AS "Route Departure Delay Rate",
    CAST(SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(COUNT(*), 0) AS "Route Cancellation Rate",
    COUNT(*) AS "Route Frequency"

FROM flights
GROUP BY origin, destination;
