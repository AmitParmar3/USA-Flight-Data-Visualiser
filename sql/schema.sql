-- sql/schema.sql
-- DuckDB Analytical Logical Schema

-- 1. flights
CREATE OR REPLACE VIEW flights AS 
SELECT * FROM 'data/processed/flight_fact_2025_01.parquet';

-- 2. candidate_connections
CREATE OR REPLACE VIEW candidate_connections AS 
SELECT * FROM 'data/processed/candidate_connections_2025_01.parquet';

-- 3. connection_reliability
-- Calculated purely in DuckDB to avoid loading 27M rows into pandas
CREATE OR REPLACE VIEW connection_reliability AS 
SELECT 
    connection_airport,
    inbound_carrier,
    outbound_carrier,
    CASE 
        WHEN scheduled_connection_time_min BETWEEN 45 AND 59 THEN '45-59'
        WHEN scheduled_connection_time_min BETWEEN 60 AND 89 THEN '60-89'
        WHEN scheduled_connection_time_min BETWEEN 90 AND 119 THEN '90-119'
        WHEN scheduled_connection_time_min BETWEEN 120 AND 179 THEN '120-179'
        WHEN scheduled_connection_time_min BETWEEN 180 AND 239 THEN '180-239'
        WHEN scheduled_connection_time_min >= 240 THEN '240+'
    END AS scheduled_buffer_bucket,
    COUNT(connection_buffer_min) AS candidate_connections,
    CAST(SUM(CASE WHEN connection_buffer_min < 0 THEN 1 ELSE 0 END) AS INTEGER) AS operationally_infeasible,
    CAST(SUM(CASE WHEN connection_buffer_min < 0 THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(connection_buffer_min) AS operational_risk_rate,
    1.0 - (CAST(SUM(CASE WHEN connection_buffer_min < 0 THEN 1 ELSE 0 END) AS DOUBLE) / COUNT(connection_buffer_min)) AS operational_feasibility_rate,
    median(connection_buffer_min) AS median_actual_buffer,
    avg(connection_buffer_min) AS mean_actual_buffer
FROM candidate_connections
GROUP BY 
    connection_airport,
    inbound_carrier,
    outbound_carrier,
    CASE 
        WHEN scheduled_connection_time_min BETWEEN 45 AND 59 THEN '45-59'
        WHEN scheduled_connection_time_min BETWEEN 60 AND 89 THEN '60-89'
        WHEN scheduled_connection_time_min BETWEEN 90 AND 119 THEN '90-119'
        WHEN scheduled_connection_time_min BETWEEN 120 AND 179 THEN '120-179'
        WHEN scheduled_connection_time_min BETWEEN 180 AND 239 THEN '180-239'
        WHEN scheduled_connection_time_min >= 240 THEN '240+'
    END;

-- 4. itineraries
-- Since itineraries score relies on python logic for the full 27M rows, 
-- we define a view that performs the scoring dynamically in DuckDB to avoid pandas.
-- This effectively replicates the logic of the balanced decision engine.
CREATE OR REPLACE VIEW itineraries AS
WITH base AS (
    SELECT 
        inbound_flight_id,
        outbound_flight_id,
        origin,
        connection_airport,
        destination,
        inbound_carrier,
        outbound_carrier,
        is_same_carrier AS same_carrier,
        scheduled_connection_time_min,
        actual_connection_time_min,
        connection_buffer_min,
        COALESCE(inbound_arrival_delay_min, 0) AS inbound_arrival_delay_min,
        COALESCE(outbound_departure_delay_min, 0) AS outbound_departure_delay_min,
        
        -- Journey time
        DATE_DIFF('minute', inbound_scheduled_departure_utc, outbound_scheduled_arrival_utc) AS total_scheduled_journey_time_min,
        
        -- Flight time
        DATE_DIFF('minute', inbound_scheduled_departure_utc, outbound_scheduled_arrival_utc) - scheduled_connection_time_min AS total_scheduled_flight_time_min,
        
        -- Actual connection buffer
        actual_connection_time_min - 45 AS actual_buffer
    FROM candidate_connections
)
SELECT 
    *,
    CASE
        WHEN actual_buffer < 0 THEN 'Operationally Infeasible'
        WHEN actual_buffer >= 0 AND actual_buffer < 15 THEN 'Critical'
        WHEN actual_buffer >= 15 AND actual_buffer < 30 THEN 'High'
        WHEN actual_buffer >= 30 AND actual_buffer < 60 THEN 'Moderate'
        WHEN actual_buffer >= 60 THEN 'Low'
    END AS connection_risk_band
FROM base;

