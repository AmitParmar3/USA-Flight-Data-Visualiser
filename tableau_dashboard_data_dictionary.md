# Tableau Dashboard Data Dictionary

This document outlines the Semantic Layer designed for Tableau, built on top of the DuckDB flight analytics database.

## General Methodological Caveat
> **IMPORTANT:** Candidate connections and multi-leg itineraries in this dataset are modeled purely from flight schedules and operational timestamps. They reflect operational network feasibility. **They are NOT observed passenger bookings, PNRs, ticketed itineraries, or actual passenger connection outcomes.**

---

## 1. tableau_flight_performance
**Purpose:** Powers Dashboards 1-4 (Network Overview, Carrier Performance, Airport Reliability, Route Analysis).
*Note: This view employs a **Polymorphic Grain** (Flight, Airport, Carrier, Route) via UNION ALL. This allows Tableau to query independent, mathematically correct pre-aggregations without duplicating flight rows or incorrectly merging origins/destinations. Filter by `record_type` when necessary.*

| Field Name | Source | Interpretation |
| :--- | :--- | :--- |
| `record_type` | `UNION` | 'Flight', 'Airport', 'Carrier', or 'Route'. |
| `flight_id` | `flights` | Unique identifier (Populated only for 'Flight' rows). |
| `Airport` | `UNION` | Consolidated airport (Populated only for 'Airport' rows). |
| `Carrier` | `UNION` | Carrier (Populated for 'Flight' and 'Carrier' rows). |
| `Origin` / `Destination` | `flights` | Populated for 'Flight' and 'Route' rows. |
| `Airport Flight Volume` | `airport_agg` | Total departures + arrivals. |
| `Arrival Delay Rate` | `UNION` | Shared metric name used by Airport and Carrier domains. |
| `Outbound Network Connectivity` | `airport_agg` | Distinct destinations served from an airport. |
| `Carrier Flight Volume` | `carrier_agg` | Total flights operated by a carrier. |
| `Route Frequency` | `route_agg` | Total flights on a specific O-D pair. |

---

## 2. tableau_connection_reliability
**Purpose:** Powers Dashboard 5 (Connection Reliability).

| Field Name | Source | Interpretation |
| :--- | :--- | :--- |
| `connection_airport` | `connection_reliability` | Hub/Transfer airport. |
| `inbound_carrier` | `connection_reliability` | First leg carrier. |
| `outbound_carrier` | `connection_reliability` | Second leg carrier. |
| `same_carrier` | `connection_reliability` | True if inbound_carrier == outbound_carrier. |
| `scheduled_buffer_bucket`| `connection_reliability`| E.g., '45-59', '60-89' |
| `total_candidate_connections`| `connection_reliability`| Count of schedule-feasible combinations. |
| `operationally_infeasible_connections`| `connection_reliability`| Count of actual buffer < 0. |
| `operational_risk_rate` | `connection_reliability` | Infeasible / Total candidates. |
| `median_actual_buffer` | `connection_reliability` | Median actual buffer (min). |

---

## 3. tableau_itinerary_search
**Purpose:** Powers Dashboard 6 (Itinerary Decision Support).
*Note: This view exposes 27.1 million rows. Tableau should push down filters to DuckDB before ranking.*

| Field Name | Source | Interpretation |
| :--- | :--- | :--- |
| `inbound_flight_id` | `itineraries` | Unique ID of first leg. |
| `outbound_flight_id`| `itineraries` | Unique ID of second leg. |
| `origin` | `itineraries` | Start of the journey. |
| `destination` | `itineraries` | Final destination. |
| `connection_airport`| `itineraries` | Transfer airport. |
| `total_scheduled_journey_time_min`| `itineraries` | Total duration departure A to arrival B. |
| `connection_buffer_min` | `itineraries` | Time remaining above 45-min limit. |
| `connection_risk_band` | `itineraries` | Low to Infeasible. |

---

## Recommended Tableau Connection Strategy

1. **Analytical Dashboards (1-5):**
   - **Connection Type:** Live Connection to `data/processed/flight_analytics.duckdb` using DuckDB ODBC/JDBC driver.
   - **Performance Profile:** `tableau_flight_performance` and `tableau_connection_reliability` will render natively fast without requiring massive data extracts.

2. **Itinerary Decision Support (Dashboard 6):**
   - **Connection Type:** Live Connection via **Custom SQL** or parameterized worksheets querying `tableau_itinerary_search`.
   - **Workflow:** Set up Tableau to require user `origin` and `destination` input *before* querying to leverage DuckDB Parquet predicate pushdown.
