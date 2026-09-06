# Tableau Dashboard Data Dictionary

This document outlines the Semantic Layer designed for Tableau, built on top of the DuckDB flight analytics database.

## General Methodological Caveat
> **IMPORTANT:** Candidate connections and multi-leg itineraries in this dataset are modeled purely from flight schedules and operational timestamps. They reflect operational network feasibility. **They are NOT observed passenger bookings, PNRs, ticketed itineraries, or actual passenger connection outcomes.**

---

## 1. tableau_carrier_performance
**Purpose:** Powers the Carrier Performance dashboard (Dashboard 2).

| Field Name | Definition | Source | Calculation | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| `carrier` | The airline carrier code. | `flights` | - | Primary dimension for carrier. |
| `flights` | Total number of flights scheduled. | `flights` | `COUNT(*)` | Scale of carrier operations. |
| `total_cancelled` | Total cancelled flights. | `flights` | `SUM(is_cancelled)` | - |
| `total_diverted` | Total diverted flights. | `flights` | `SUM(is_diverted)` | - |
| `completed_flights` | Total flights that arrived. | `flights` | Total - Cancelled - Diverted | - |
| `cancellation_rate` | Percentage of scheduled flights cancelled. | `flights` | `total_cancelled / flights` | Higher means less reliable scheduling. |
| `departure_delay_rate` | Percentage of completed flights departing >15 min late. | `flights` | `SUM(dep_delay > 15) / completed_flights` | - |
| `arrival_delay_rate` | Percentage of completed flights arriving >15 min late. | `flights` | `SUM(arr_delay > 15) / completed_flights` | DOT standard for delay. |
| `severe_delay_rate` | Percentage of completed flights arriving >60 min late. | `flights` | `SUM(arr_delay > 60) / completed_flights` | Indicates major disruptions. |
| `average_arrival_delay` | Mean arrival delay in minutes. | `flights` | `avg(arrival_delay_min)` | Includes early arrivals (negative). |
| `average_positive_arrival_delay`| Mean delay for flights that arrived late. | `flights` | `avg(delay > 0)` | How late a flight is when it is late. |
| `delay_recovery` | Time recovered during flight (min). | `flights` | `avg(delay_recovery_min)` | Positive means flight made up time in air. |

---

## 2. tableau_airport_performance
**Purpose:** Powers the Airport Reliability dashboard (Dashboard 3).

| Field Name | Definition | Source | Calculation | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| `airport` | The airport code. | `flights` | - | - |
| `airport_flight_volume`| Total departures + arrivals. | `flights` | `total_departures + total_arrivals` | Scale of airport operations. |
| `departure_delay_rate` | % of departures delayed >15 min. | `flights` | `SUM(dep_delay > 15) / completed_departures` | - |
| `arrival_delay_rate` | % of arrivals delayed >15 min. | `flights` | `SUM(arr_delay > 15) / completed_arrivals` | - |
| `cancellation_rate` | % of scheduled departures cancelled. | `flights` | `total_cancelled / total_scheduled` | - |
| `severe_delay_rate` | % of departures delayed >60 min. | `flights` | `SUM(dep_delay > 60) / completed_departures` | - |
| `inbound_network_connectivity`| Number of unique origin airports serving this airport. | `flights` | `COUNT(DISTINCT origin)` | Measure of inbound reach. |
| `outbound_network_connectivity`| Number of unique destinations served from this airport. | `flights` | `COUNT(DISTINCT destination)`| Measure of outbound reach. |

---

## 3. tableau_route_performance
**Purpose:** Powers the Route Analysis dashboard (Dashboard 4).

| Field Name | Definition | Source | Calculation | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| `origin` | Origin airport. | `flights` | - | - |
| `destination` | Destination airport. | `flights` | - | - |
| `route` | Origin-Destination pair. | `flights` | `origin + '-' + destination` | E.g. JFK-LAX |
| `route_frequency` | Total flights on this route. | `flights` | `COUNT(*)` | - |
| `operating_days` | Number of distinct days of week operated. | `flights` | `COUNT(DISTINCT day_of_week)` | Max 7. |
| `number_of_carriers` | Distinct carriers flying this route. | `flights` | `COUNT(DISTINCT carrier)` | Indicates route competition. |
| `average_scheduled_duration`| Mean scheduled block time. | `flights` | `avg(scheduled_duration_min)` | - |
| `average_distance` | Mean distance in miles. | `flights` | `avg(distance_miles)` | - |
| `flights_per_day` | Average daily frequency. | `flights` | `route_frequency / 31` | - |
| `route_delay_performance`| % of arrivals delayed >15 min. | `flights` | `SUM(arr_delay > 15) / completed_flights` | - |

---

## 4. tableau_connection_reliability
**Purpose:** Powers the crucial Connection Reliability dashboard (Dashboard 5).

| Field Name | Definition | Source | Calculation | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| `connection_airport` | Hub/Transfer airport. | `connection_reliability` | - | - |
| `inbound_carrier` | Carrier of the first leg. | `connection_reliability` | - | - |
| `outbound_carrier` | Carrier of the second leg. | `connection_reliability` | - | - |
| `scheduled_buffer_bucket`| Grouping of scheduled connection time. | `connection_reliability` | e.g., '45-59', '60-89' | - |
| `candidate_connection_count`| Total modeled feasible connections. | `connection_reliability` | `COUNT(*)` | - |
| `operationally_infeasible_connections`| Connections where actual buffer < 0. | `connection_reliability`| `SUM(actual_buffer < 0)` | Inbound arrived too late for outbound. |
| `operational_risk_rate` | % of connections that became infeasible. | `connection_reliability`| `infeasible / total` | High rate = risky connection profile. |
| `operational_feasibility_rate`| % of connections maintained >=0 buffer. | `connection_reliability`| `1 - risk_rate` | - |
| `median_actual_buffer` | Median actual connection buffer in min. | `connection_reliability`| `median(actual_buffer)` | Typical buffer experienced. |
| `mean_actual_buffer` | Mean actual connection buffer in min. | `connection_reliability`| `avg(actual_buffer)` | - |

---

## 5. tableau_itinerary_search
**Purpose:** Powers the Itinerary Decision Support search interface (Dashboard 6).
*Note: This view is highly granular (27M rows). It remains a lightweight view backed by Parquet.*

| Field Name | Definition | Source | Calculation | Interpretation |
| :--- | :--- | :--- | :--- | :--- |
| `inbound_flight_id` | Unique ID of first leg. | `itineraries` | - | - |
| `outbound_flight_id`| Unique ID of second leg. | `itineraries` | - | - |
| `origin` | Start of the journey. | `itineraries` | - | Primary filter. |
| `destination` | Final destination. | `itineraries` | - | Primary filter. |
| `connection_airport`| Transfer airport. | `itineraries` | - | - |
| `inbound_carrier` | First leg carrier. | `itineraries` | - | - |
| `outbound_carrier` | Second leg carrier. | `itineraries` | - | - |
| `same_carrier` | True if inbound and outbound match. | `itineraries` | `inbound_carrier == outbound_carrier` | - |
| `scheduled_connection_time_min` | Scheduled transfer window. | `itineraries` | - | - |
| `actual_connection_time_min` | Actual transfer window. | `itineraries` | - | - |
| `connection_buffer_min` | Time remaining above 45-min limit. | `itineraries` | - | - |
| `inbound_arrival_delay_min` | Arrival delay of leg 1. | `itineraries` | - | - |
| `outbound_departure_delay_min`| Departure delay of leg 2. | `itineraries` | - | - |
| `total_scheduled_journey_time_min`| Total duration departure A to arrival B. | `itineraries` | - | - |
| `total_scheduled_flight_time_min`| Combined duration of just the flights. | `itineraries` | - | - |
| `connection_risk_band` | Categorization of connection safety. | `itineraries` | Derived from buffer. | Low to Infeasible. |

---

## Recommended Tableau Connection Strategy

1. **Analytical Dashboards (1-5):**
   - **Connection Type:** Live Connection to `data/processed/flight_analytics.duckdb` using DuckDB ODBC/JDBC driver.
   - **Performance Profile:** These views (`tableau_carrier_performance`, `tableau_airport_performance`, `tableau_route_performance`, `tableau_connection_reliability`) are pre-aggregated in SQL and natively fast (returning 10s to 10,000s of rows). They will render instantly in Tableau without requiring data extracts.

2. **Itinerary Decision Support (Dashboard 6):**
   - **Connection Type:** Live Connection via **Custom SQL** or deeply filtered worksheets.
   - **Performance Profile:** `tableau_itinerary_search` covers 27 million rows. Do NOT attempt to load this entire view into memory or render it without filters.
   - **Workflow:** Set up Tableau to require the user to input `origin` and `destination` parameters *before* querying. Push these filters directly to the database via Custom SQL (e.g., `WHERE origin = <Parameters.Origin> AND destination = <Parameters.Destination>`).
   - **DuckDB Advantage:** By filtering *before* ranking (ORDER BY), DuckDB utilizes Parquet predicate pushdown to scan only the relevant byte ranges in the 278MB file, running complex ranking queries across millions of rows in milliseconds.

