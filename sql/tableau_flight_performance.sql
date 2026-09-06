-- sql/tableau_flight_performance.sql
-- Purpose: Tableau semantic layer for flight performance (Dashboards 1-4).
-- Grain: Exactly one row per scheduled flight.
-- Source: Backed directly by the flight_fact Parquet data via the 'flights' view.
-- Dashboard Usage: Powers Network Overview, Carrier Performance, Airport Reliability, Route Analysis.

CREATE OR REPLACE VIEW tableau_flight_performance AS
SELECT 
    -- Identity
    flight_id,
    flight_date,
    carrier,
    flight_number,
    origin,
    destination,
    route,
    
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
    departure_delayed_15,
    arrival_delayed_15,
    departure_severe_60,
    arrival_severe_60,
    departure_severe_120,
    arrival_severe_120,
    delay_recovery_min,
    
    -- Other
    distance_miles AS distance,
    day_of_week,
    day_of_week_num,
    is_weekend

FROM flights;

