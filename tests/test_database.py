import unittest
import os
import duckdb
from src.database import build_database

class TestDatabase(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        # Run database builder
        build_database()
        cls.db_path = "data/processed/flight_analytics.duckdb"
        cls.conn = duckdb.connect(cls.db_path)

    @classmethod
    def tearDownClass(cls):
        cls.conn.close()

    def test_tableau_flight_performance_exists(self):
        res = self.conn.execute("SELECT COUNT(*) FROM tableau_flight_performance WHERE record_type = 'Flight'").fetchone()
        self.assertIsNotNone(res)
        self.assertEqual(res[0], 539747)
        
        unique = self.conn.execute("SELECT COUNT(DISTINCT flight_id) FROM tableau_flight_performance WHERE flight_id IS NOT NULL").fetchone()
        self.assertEqual(unique[0], 539747)
        
        # Test airport rows exist
        airports = self.conn.execute("SELECT COUNT(*) FROM tableau_flight_performance WHERE record_type = 'Airport'").fetchone()
        self.assertGreater(airports[0], 100)
        
        # Test carrier rows exist
        carriers = self.conn.execute("SELECT COUNT(*) FROM tableau_flight_performance WHERE record_type = 'Carrier'").fetchone()
        self.assertGreater(carriers[0], 5)
        
        # Test route rows exist
        routes = self.conn.execute("SELECT COUNT(*) FROM tableau_flight_performance WHERE record_type = 'Route'").fetchone()
        self.assertGreater(routes[0], 1000)
        
        columns = [c[0] for c in self.conn.execute("DESCRIBE tableau_flight_performance").fetchall()]
        required = ["flight_id", "Carrier", "Origin", "Destination", "Airport", "Airport Flight Volume", "Arrival Delay Rate"]
        for r in required:
            self.assertIn(r, columns)

    def test_tableau_connection_reliability_exists(self):
        res = self.conn.execute("SELECT COUNT(*) FROM tableau_connection_reliability").fetchone()
        self.assertIsNotNone(res)
        self.assertTrue(30000 < res[0] < 50000)
        
        columns = [c[0] for c in self.conn.execute("DESCRIBE tableau_connection_reliability").fetchall()]
        required = ["connection_airport", "inbound_carrier", "outbound_carrier", "scheduled_buffer_bucket", "median_actual_buffer"]
        for r in required:
            self.assertIn(r, columns)

    def test_tableau_itinerary_search_exists(self):
        res = self.conn.execute("SELECT COUNT(*) FROM tableau_itinerary_search").fetchone()
        self.assertIsNotNone(res)
        self.assertEqual(res[0], 27118072)
        
        columns = [c[0] for c in self.conn.execute("DESCRIBE tableau_itinerary_search").fetchall()]
        required = ["inbound_flight_id", "outbound_flight_id", "origin", "destination", "connection_airport", "total_scheduled_journey_time_min"]
        for r in required:
            self.assertIn(r, columns)
            
    def test_representative_filtered_query(self):
        # Verify a filtered query runs successfully over the itinerary view
        query = """
            SELECT * FROM tableau_itinerary_search 
            WHERE origin = 'JFK' AND destination = 'LAX'
            ORDER BY total_scheduled_journey_time_min ASC
            LIMIT 5
        """
        res = self.conn.execute(query).fetchall()
        self.assertIsNotNone(res)
        self.assertGreater(len(res), 0)
        self.assertLessEqual(len(res), 5)
        
    def test_obsolete_views_removed(self):
        obsolete_views = [
            "tableau_airport_performance",
            "tableau_carrier_performance",
            "tableau_route_performance",
            "tableau_itinerary_options"
        ]
        
        tables = [row[0] for row in self.conn.execute("SELECT table_name FROM information_schema.tables").fetchall()]
        for ov in obsolete_views:
            self.assertNotIn(ov, tables)

if __name__ == "__main__":
    unittest.main()

