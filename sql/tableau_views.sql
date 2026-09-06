-- sql/tableau_views.sql
-- Semantic Layer for Tableau Dashboards

-- DASHBOARD 2: CARRIER PERFORMANCE
CREATE OR REPLACE VIEW tableau_carrier_performance AS
SELECT 
    carrier,
    COUNT(*) AS flights,
    SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) AS total_cancelled,
    SUM(CASE WHEN is_diverted THEN 1 ELSE 0 END) AS total_diverted,
    COUNT(*) - SUM(CASE WHEN is_cancelled OR is_diverted THEN 1 ELSE 0 END) AS completed_flights,
    CAST(SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(COUNT(*), 0) AS cancellation_rate,
    CAST(SUM(CASE WHEN departure_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END), 0) AS departure_delay_rate,
    CAST(SUM(CASE WHEN arrival_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END), 0) AS arrival_delay_rate,
    CAST(SUM(CASE WHEN arrival_delay_min > 60 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END), 0) AS severe_delay_rate,
    avg(arrival_delay_min) AS average_arrival_delay,
    avg(CASE WHEN arrival_delay_min > 0 THEN arrival_delay_min ELSE NULL END) AS average_positive_arrival_delay,
    avg(delay_recovery_min) AS delay_recovery
FROM flights
GROUP BY carrier;

-- DASHBOARD 3: AIRPORT RELIABILITY
CREATE OR REPLACE VIEW tableau_airport_performance AS
WITH deps AS (
    SELECT 
        origin AS airport,
        COUNT(*) AS total_departures,
        CAST(SUM(CASE WHEN is_cancelled THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(COUNT(*), 0) AS cancellation_rate,
        CAST(SUM(CASE WHEN departure_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END), 0) AS departure_delay_rate,
        CAST(SUM(CASE WHEN departure_delay_min > 60 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END), 0) AS severe_delay_rate,
        COUNT(DISTINCT destination) AS outbound_network_connectivity
    FROM flights
    GROUP BY origin
),
arrs AS (
    SELECT 
        destination AS airport,
        COUNT(*) AS total_arrivals,
        CAST(SUM(CASE WHEN arrival_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END), 0) AS arrival_delay_rate,
        COUNT(DISTINCT origin) AS inbound_network_connectivity
    FROM flights
    GROUP BY destination
)
SELECT 
    COALESCE(d.airport, a.airport) AS airport,
    (COALESCE(d.total_departures, 0) + COALESCE(a.total_arrivals, 0)) AS airport_flight_volume,
    d.departure_delay_rate,
    a.arrival_delay_rate,
    d.cancellation_rate,
    d.severe_delay_rate,
    a.inbound_network_connectivity,
    d.outbound_network_connectivity
FROM deps d
FULL OUTER JOIN arrs a ON d.airport = a.airport;

-- DASHBOARD 4: ROUTE ANALYSIS
CREATE OR REPLACE VIEW tableau_route_performance AS
SELECT 
    origin,
    destination,
    origin || '-' || destination AS route,
    COUNT(*) AS route_frequency,
    COUNT(DISTINCT day_of_week) AS operating_days,
    COUNT(DISTINCT carrier) AS number_of_carriers,
    avg(scheduled_duration_min) AS average_scheduled_duration,
    avg(distance_miles) AS average_distance,
    COUNT(*) / 31.0 AS flights_per_day,
    CAST(SUM(CASE WHEN arrival_delay_min > 15 THEN 1 ELSE 0 END) AS DOUBLE) / NULLIF(SUM(CASE WHEN is_cancelled = False THEN 1 ELSE 0 END), 0) AS route_delay_performance
FROM flights
GROUP BY origin, destination;

-- DASHBOARD 5: CONNECTION RELIABILITY
CREATE OR REPLACE VIEW tableau_connection_reliability AS
SELECT 
    connection_airport,
    inbound_carrier,
    outbound_carrier,
    scheduled_buffer_bucket,
    candidate_connections AS candidate_connection_count,
    operationally_infeasible AS operationally_infeasible_connections,
    operational_risk_rate,
    operational_feasibility_rate,
    median_actual_buffer,
    mean_actual_buffer
FROM connection_reliability;

-- DASHBOARD 6: ITINERARY DECISION SUPPORT
-- We keep this as a lightweight Parquet-backed view since DuckDB can handle
-- fast predicate pushdown on 27M rows when filtering by origin/destination.
-- We omit calculating the balanced ranking score here globally since it destroys performance.
-- Instead, ranking scores can be approximated via ORDER BY logic in custom SQL queries.
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

