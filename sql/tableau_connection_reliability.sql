-- sql/tableau_connection_reliability.sql
-- Purpose: Tableau semantic layer for operational connection reliability.
-- Grain: Aggregate combination of connection airport, carriers, and scheduled buffer buckets.
-- Source: Backed by the pre-calculated connection_reliability view/parquet.
-- Dashboard Usage: Powers Dashboard 5 (Connection Reliability).

CREATE OR REPLACE VIEW tableau_connection_reliability AS
SELECT 
    connection_airport,
    inbound_carrier,
    outbound_carrier,
    (inbound_carrier = outbound_carrier) AS same_carrier,
    scheduled_buffer_bucket,
    candidate_connections AS total_candidate_connections,
    operationally_infeasible AS operationally_infeasible_connections,
    operational_risk_rate,
    operational_feasibility_rate,
    median_actual_buffer,
    mean_actual_buffer
FROM connection_reliability;

