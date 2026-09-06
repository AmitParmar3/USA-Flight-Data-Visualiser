-- sql/itinerary_analysis.sql
-- DISTINCTION NOTICE: These connections are modeled operational feasibility, 
-- NOT observed passenger journeys.

-- 10. Fastest modeled itineraries
SELECT 
    inbound_flight_id,
    outbound_flight_id,
    origin,
    connection_airport,
    destination,
    inbound_carrier,
    outbound_carrier,
    total_scheduled_journey_time_min,
    scheduled_connection_time_min
FROM itineraries
ORDER BY 
    total_scheduled_journey_time_min ASC, 
    scheduled_connection_time_min ASC
LIMIT 10;

-- 11. Lowest-risk modeled itineraries
SELECT 
    inbound_flight_id,
    outbound_flight_id,
    origin,
    connection_airport,
    destination,
    connection_risk_band,
    connection_buffer_min,
    total_scheduled_journey_time_min
FROM itineraries
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

-- 12. Balanced modeled itineraries (Approximate via SQL logic)
-- Since min-max normalization across 27M rows requires multiple passes, 
-- we approximate a scoring mechanism based on thresholds.
SELECT 
    inbound_flight_id,
    outbound_flight_id,
    origin,
    connection_airport,
    destination,
    connection_risk_band,
    connection_buffer_min,
    total_scheduled_journey_time_min,
    inbound_arrival_delay_min,
    outbound_departure_delay_min
FROM itineraries
ORDER BY
    -- Penalty for delays
    (inbound_arrival_delay_min + outbound_departure_delay_min) ASC,
    -- Penalty for long journeys
    total_scheduled_journey_time_min ASC,
    -- Bonus for better buffer
    connection_buffer_min DESC
LIMIT 10;

