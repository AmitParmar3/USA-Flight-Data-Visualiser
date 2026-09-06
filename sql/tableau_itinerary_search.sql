-- sql/tableau_itinerary_search.sql
-- Purpose: Tableau semantic layer for modeled two-leg operational itineraries.
-- Grain: One row per modeled two-leg itinerary candidate (27.1 million rows).
-- Source: Backed dynamically by candidate_connections Parquet. 
-- Dashboard Usage: Powers Dashboard 6 (Itinerary Decision Support).
-- Note: Designed for heavy filtering prior to ranking. Do NOT query without filters.

CREATE OR REPLACE VIEW tableau_itinerary_search AS
SELECT 
    inbound_flight_id,
    outbound_flight_id,
    origin,
    connection_airport,
    destination,
    inbound_carrier,
    outbound_carrier,
    same_carrier,
    scheduled_connection_time_min,
    actual_connection_time_min,
    connection_buffer_min,
    inbound_arrival_delay_min,
    outbound_departure_delay_min,
    total_scheduled_journey_time_min,
    total_scheduled_flight_time_min,
    connection_risk_band
FROM itineraries;
