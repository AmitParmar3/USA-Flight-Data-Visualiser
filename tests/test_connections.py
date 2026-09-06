import unittest
import pandas as pd
import numpy as np
from src.connections.generator import (
    generate_candidate_connections,
    validate_candidate_connections,
    validate_flight_fact_schema,
)
from src.connections.reliability import calculate_connection_reliability
from src.connections.itinerary import calculate_itinerary_metrics


class TestConnectionGenerator(unittest.TestCase):

    def setUp(self):
        # Create sample Fact_Flight_Operation dataframe
        # Flight A: JFK -> ORD, arrives 2025-01-01 12:00 UTC
        # Flight B: ORD -> LAX, departs 2025-01-01 13:00 UTC (60 min connection - FEASIBLE)
        # Flight C: ORD -> SFO, departs 2025-01-01 12:30 UTC (30 min connection - TOO SHORT)
        # Flight D: ORD -> SEA, departs 2025-01-01 17:00 UTC (300 min connection - TOO LONG)
        # Flight E: ORD -> JFK, departs 2025-01-01 13:30 UTC (90 min connection - CIRCULAR JFK-ORD-JFK)

        data = [
            {
                "flight_id": "20250101_AA_100_JFK_ORD",
                "carrier": "AA",
                "flight_number": 100,
                "origin": "JFK",
                "destination": "ORD",
                "scheduled_departure_utc": pd.to_datetime("2025-01-01 09:00:00Z"),
                "scheduled_arrival_utc": pd.to_datetime("2025-01-01 12:00:00Z"),
                "actual_departure_utc": pd.to_datetime("2025-01-01 09:05:00Z"),
                "actual_arrival_utc": pd.to_datetime("2025-01-01 12:05:00Z"),
                "departure_delay_min": 5.0,
                "arrival_delay_min": 5.0,
                "is_completed": True,
                "is_cancelled": False,
                "is_diverted": False,
            },
            {
                "flight_id": "20250101_AA_200_ORD_LAX",
                "carrier": "AA",
                "flight_number": 200,
                "origin": "ORD",
                "destination": "LAX",
                "scheduled_departure_utc": pd.to_datetime("2025-01-01 13:00:00Z"),
                "scheduled_arrival_utc": pd.to_datetime("2025-01-01 17:00:00Z"),
                "actual_departure_utc": pd.to_datetime("2025-01-01 13:10:00Z"),
                "actual_arrival_utc": pd.to_datetime("2025-01-01 17:15:00Z"),
                "departure_delay_min": 10.0,
                "arrival_delay_min": 15.0,
                "is_completed": True,
                "is_cancelled": False,
                "is_diverted": False,
            },
            {
                "flight_id": "20250101_UA_300_ORD_SFO",
                "carrier": "UA",
                "flight_number": 300,
                "origin": "ORD",
                "destination": "SFO",
                "scheduled_departure_utc": pd.to_datetime("2025-01-01 12:30:00Z"),
                "scheduled_arrival_utc": pd.to_datetime("2025-01-01 16:30:00Z"),
                "actual_departure_utc": pd.to_datetime("2025-01-01 12:30:00Z"),
                "actual_arrival_utc": pd.to_datetime("2025-01-01 16:30:00Z"),
                "departure_delay_min": 0.0,
                "arrival_delay_min": 0.0,
                "is_completed": True,
                "is_cancelled": False,
                "is_diverted": False,
            },
            {
                "flight_id": "20250101_DL_400_ORD_SEA",
                "carrier": "DL",
                "flight_number": 400,
                "origin": "ORD",
                "destination": "SEA",
                "scheduled_departure_utc": pd.to_datetime("2025-01-01 17:00:00Z"),
                "scheduled_arrival_utc": pd.to_datetime("2025-01-01 21:00:00Z"),
                "actual_departure_utc": pd.to_datetime("2025-01-01 17:00:00Z"),
                "actual_arrival_utc": pd.to_datetime("2025-01-01 21:00:00Z"),
                "departure_delay_min": 0.0,
                "arrival_delay_min": 0.0,
                "is_completed": True,
                "is_cancelled": False,
                "is_diverted": False,
            },
            {
                "flight_id": "20250101_AA_500_ORD_JFK",
                "carrier": "AA",
                "flight_number": 500,
                "origin": "ORD",
                "destination": "JFK",
                "scheduled_departure_utc": pd.to_datetime("2025-01-01 13:30:00Z"),
                "scheduled_arrival_utc": pd.to_datetime("2025-01-01 16:30:00Z"),
                "actual_departure_utc": pd.to_datetime("2025-01-01 13:30:00Z"),
                "actual_arrival_utc": pd.to_datetime("2025-01-01 16:30:00Z"),
                "departure_delay_min": 0.0,
                "arrival_delay_min": 0.0,
                "is_completed": True,
                "is_cancelled": False,
                "is_diverted": False,
            },
        ]
        self.fact_df = pd.DataFrame(data)

    def test_candidate_generation_default_bounds(self):
        # Min 45 min, Max 240 min
        conn = generate_candidate_connections(
            self.fact_df,
            min_connection_min=45,
            max_connection_min=240,
            allow_circular=False,
        )

        # Expected connection: Flight A -> Flight B (JFK-ORD-LAX, 60 min)
        # Flight C is 30 min (too short < 45)
        # Flight D is 300 min (too long > 240)
        # Flight E is circular JFK-ORD-JFK (allow_circular=False)
        self.assertEqual(len(conn), 1)
        self.assertEqual(conn.iloc[0]["inbound_flight_id"], "20250101_AA_100_JFK_ORD")
        self.assertEqual(conn.iloc[0]["outbound_flight_id"], "20250101_AA_200_ORD_LAX")
        self.assertEqual(conn.iloc[0]["connection_airport"], "ORD")
        self.assertEqual(conn.iloc[0]["scheduled_connection_time_min"], 60.0)

    def test_allow_circular_connections(self):
        conn = generate_candidate_connections(
            self.fact_df,
            min_connection_min=45,
            max_connection_min=240,
            allow_circular=True,
        )
        # Should include JFK-ORD-LAX and JFK-ORD-JFK
        self.assertEqual(len(conn), 2)
        destinations = set(conn["destination"])
        self.assertIn("LAX", destinations)
        self.assertIn("JFK", destinations)

    def test_custom_connection_bounds(self):
        # Min 15 min, Max 360 min
        conn = generate_candidate_connections(
            self.fact_df,
            min_connection_min=15,
            max_connection_min=360,
            allow_circular=False,
        )
        # Includes Flight B (60 min), Flight C (30 min), Flight D (300 min)
        self.assertEqual(len(conn), 3)

    def test_validation_function(self):
        conn = generate_candidate_connections(
            self.fact_df,
            min_connection_min=45,
            max_connection_min=240,
        )
        checks = validate_candidate_connections(conn, min_connection_min=45, max_connection_min=240)
        self.assertEqual(checks["total_connections"], 1)
        self.assertEqual(checks["duplicate_pairings"], 0)
        self.assertEqual(checks["self_connections"], 0)
        self.assertEqual(checks["under_min_time_violations"], 0)
        self.assertEqual(checks["over_max_time_violations"], 0)

    def test_missing_schema_error(self):
        invalid_df = pd.DataFrame({"dummy": [1, 2, 3]})
        with self.assertRaises(ValueError):
            generate_candidate_connections(invalid_df)

    def test_reliability_and_itinerary_metrics(self):
        conn = generate_candidate_connections(
            self.fact_df,
            min_connection_min=45,
            max_connection_min=240,
        )
        rel = calculate_connection_reliability(conn)
        self.assertFalse(rel.empty)
        itin = calculate_itinerary_metrics(conn)
        self.assertFalse(itin.empty)


if __name__ == "__main__":
    unittest.main()

