-- sql/connection_analysis.sql
-- DISTINCTION NOTICE: These connections are modeled operational feasibility, 
-- NOT observed passenger journeys.

-- 7. Connection airport reliability
SELECT 
    connection_airport,
    SUM(candidate_connections) AS total_candidates,
    SUM(operationally_infeasible) AS total_infeasible,
    CAST(SUM(operationally_infeasible) AS DOUBLE) / SUM(candidate_connections) AS airport_risk_rate,
    1.0 - (CAST(SUM(operationally_infeasible) AS DOUBLE) / SUM(candidate_connections)) AS airport_feasibility_rate
FROM connection_reliability
GROUP BY connection_airport
HAVING SUM(candidate_connections) > 1000
ORDER BY airport_feasibility_rate ASC;

-- 8. Reliability by scheduled connection buffer
SELECT 
    scheduled_buffer_bucket,
    SUM(candidate_connections) AS total_candidates,
    CAST(SUM(operationally_infeasible) AS DOUBLE) / SUM(candidate_connections) AS bucket_risk_rate,
    1.0 - (CAST(SUM(operationally_infeasible) AS DOUBLE) / SUM(candidate_connections)) AS bucket_feasibility_rate
FROM connection_reliability
GROUP BY scheduled_buffer_bucket
ORDER BY scheduled_buffer_bucket;

-- 9. Carrier-pair connection reliability
SELECT 
    inbound_carrier,
    outbound_carrier,
    SUM(candidate_connections) AS total_candidates,
    CAST(SUM(operationally_infeasible) AS DOUBLE) / SUM(candidate_connections) AS carrier_pair_risk_rate,
    1.0 - (CAST(SUM(operationally_infeasible) AS DOUBLE) / SUM(candidate_connections)) AS carrier_pair_feasibility_rate
FROM connection_reliability
GROUP BY inbound_carrier, outbound_carrier
HAVING SUM(candidate_connections) > 500
ORDER BY carrier_pair_feasibility_rate ASC;

