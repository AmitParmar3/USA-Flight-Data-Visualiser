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
        # Flight A: JFK -> ORD, arrives 2025-01-01 12:00 UTC (Carrier AA)
        # Flight B: ORD -> LAX, departs 2025-01-01 13:00 UTC (60 min connection - FEASIBLE, Carrier AA)
        # Flight C: ORD -> SFO, departs 2025-01-01 12:30 UTC (30 min connection - TOO SHORT < 45 min, Carrier UA)
        # Flight D: ORD -> SEA, departs 2025-01-01 17:00 UTC (300 min connection - TOO LONG > 240 min, Carrier DL)
        # Flight E: ORD -> JFK, departs 2025-01-01 13:30 UTC (90 min connection - CIRCULAR JFK-ORD-JFK, Carrier AA)

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

    def test_lower_bound_45_min(self):
        # 30-minute connection (Flight C) must be excluded under 45-min lower bound
        conn = generate_candidate_connections(
            self.fact_df,
            min_connection_min=45,
            max_connection_min=240,
        )
        outbound_ids = set(conn["outbound_flight_id"])
        self.assertNotIn("20250101_UA_300_ORD_SFO", outbound_ids)

    def test_upper_bound_240_min(self):
        # 300-minute connection (Flight D) must be excluded under 240-min upper bound
        conn = generate_candidate_connections(
            self.fact_df,
            min_connection_min=45,
            max_connection_min=240,
        )
        outbound_ids = set(conn["outbound_flight_id"])
        self.assertNotIn("20250101_DL_400_ORD_SEA", outbound_ids)

    def test_no_duplicate_flight_pairs(self):
        conn = generate_candidate_connections(
            self.fact_df,
            min_connection_min=45,
            max_connection_min=240,
        )
        duplicated = conn.duplicated(subset=["inbound_flight_id", "outbound_flight_id"]).sum()
        self.assertEqual(duplicated, 0)

    def test_no_self_pairing(self):
        conn = generate_candidate_connections(
            self.fact_df,
            min_connection_min=45,
            max_connection_min=240,
        )
        self_pairs = (conn["inbound_flight_id"] == conn["outbound_flight_id"]).sum()
        self.assertEqual(self_pairs, 0)

    def test_no_circular_connection_by_default(self):
        # Flight E is ORD->JFK which makes JFK->ORD->JFK circular
        conn = generate_candidate_connections(
            self.fact_df,
            min_connection_min=45,
            max_connection_min=240,
            allow_circular=False,
        )
        circular = (conn["origin"] == conn["destination"]).sum()
        self.assertEqual(circular, 0)
        self.assertNotIn("20250101_AA_500_ORD_JFK", set(conn["outbound_flight_id"]))

    def test_same_carrier_filtering(self):
        # Flight B is AA (same carrier as Flight A), Flight C is UA (different carrier)
        conn_same = generate_candidate_connections(
            self.fact_df,
            min_connection_min=15,  # Allow 30-min to include UA if enabled
            max_connection_min=240,
            same_carrier_only=True,
        )
        # All returned connections must be is_same_carrier == True
        self.assertTrue(conn_same["is_same_carrier"].all())
        self.assertNotIn("20250101_UA_300_ORD_SFO", set(conn_same["outbound_flight_id"]))

    def test_correct_scheduled_connection_time_and_airport(self):
        conn = generate_candidate_connections(
            self.fact_df,
            min_connection_min=45,
            max_connection_min=240,
        )
        self.assertEqual(len(conn), 1)
        row = conn.iloc[0]
        self.assertEqual(row["connection_airport"], "ORD")
        self.assertEqual(row["scheduled_connection_time_min"], 60.0)
        self.assertEqual(row["inbound_flight_id"], "20250101_AA_100_JFK_ORD")
        self.assertEqual(row["outbound_flight_id"], "20250101_AA_200_ORD_LAX")

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
        self.assertEqual(checks["circular_connections"], 0)

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


from src.connections.decision import rank_itineraries, calculate_itinerary_score

class TestDecisionEngine(unittest.TestCase):
    def setUp(self):
        self.itinerary_df = pd.DataFrame([
            {
                "itinerary_id": 1,
                "total_scheduled_journey_time_min": 200,
                "scheduled_connection_time_min": 50,
                "connection_buffer_min": 5,
                "inbound_arrival_delay_min": 0,
                "outbound_departure_delay_min": 0,
                "connection_risk_band": "High",
            },
            {
                "itinerary_id": 2,
                "total_scheduled_journey_time_min": 300,
                "scheduled_connection_time_min": 90,
                "connection_buffer_min": 45,
                "inbound_arrival_delay_min": 10,
                "outbound_departure_delay_min": 0,
                "connection_risk_band": "Low",
            },
            {
                "itinerary_id": 3,
                "total_scheduled_journey_time_min": 250,
                "scheduled_connection_time_min": 45,
                "connection_buffer_min": 0,
                "inbound_arrival_delay_min": 20,
                "outbound_departure_delay_min": 5,
                "connection_risk_band": "Critical",
            },
            {
                "itinerary_id": 4,
                "total_scheduled_journey_time_min": 250,
                "scheduled_connection_time_min": 60,
                "connection_buffer_min": 15,
                "inbound_arrival_delay_min": 0,
                "outbound_departure_delay_min": 0,
                "connection_risk_band": "Moderate",
            }
        ])

    def test_fastest_ranking(self):
        ranked = rank_itineraries(self.itinerary_df, objective="fastest", top_n=2)
        self.assertEqual(len(ranked), 2)
        self.assertEqual(ranked.iloc[0]["itinerary_id"], 1)

    def test_reliability_ranking(self):
        ranked = rank_itineraries(self.itinerary_df, objective="reliable", top_n=3)
        self.assertEqual(ranked.iloc[0]["itinerary_id"], 2)

    def test_risk_ranking(self):
        ranked = rank_itineraries(self.itinerary_df, objective="risk", top_n=4)
        self.assertEqual(ranked.iloc[0]["itinerary_id"], 2)
        self.assertEqual(ranked.iloc[1]["itinerary_id"], 4)

    def test_balanced_ranking(self):
        ranked = rank_itineraries(self.itinerary_df, objective="balanced", top_n=4)
        self.assertIn("ranking_score", ranked.columns)
        self.assertTrue(pd.notna(ranked["ranking_score"].iloc[0]))
        scores = ranked["ranking_score"].tolist()
        self.assertEqual(scores, sorted(scores, reverse=True))

    def test_invalid_objective(self):
        with self.assertRaises(ValueError):
            rank_itineraries(self.itinerary_df, objective="invalid")

    def test_empty_input(self):
        empty_df = pd.DataFrame(columns=self.itinerary_df.columns)
        ranked = rank_itineraries(empty_df, objective="balanced")
        self.assertTrue(ranked.empty)

    def test_top_n_behavior(self):
        ranked = rank_itineraries(self.itinerary_df, top_n=1)
        self.assertEqual(len(ranked), 1)

if __name__ == "__main__":
    unittest.main()
