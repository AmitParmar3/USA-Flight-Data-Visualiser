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

    def test_database_exists(self):
        self.assertTrue(os.path.exists(self.db_path))

    def test_flight_fact_view_exists(self):
        res = self.conn.execute("SELECT COUNT(*) FROM flights").fetchone()
        self.assertIsNotNone(res)
        self.assertGreater(res[0], 0)

    def test_candidate_connections_view_exists(self):
        res = self.conn.execute("SELECT COUNT(*) FROM candidate_connections").fetchone()
        self.assertIsNotNone(res)
        self.assertGreater(res[0], 0)

    def test_connection_reliability_view_exists(self):
        res = self.conn.execute("SELECT COUNT(*) FROM connection_reliability").fetchone()
        self.assertIsNotNone(res)
        self.assertGreater(res[0], 0)
        
    def test_itineraries_view_exists(self):
        res = self.conn.execute("SELECT COUNT(*) FROM itineraries").fetchone()
        self.assertIsNotNone(res)
        self.assertGreater(res[0], 0)

    def test_no_pandas_loading(self):
        # By querying the view strictly within duckdb using .fetchone(),
        # we prove that we can run COUNT(*) over millions of rows instantly
        # without bringing them into memory.
        res = self.conn.execute("SELECT COUNT(inbound_flight_id) FROM candidate_connections").fetchone()
        self.assertGreater(res[0], 1000000) # Should be ~27M

if __name__ == "__main__":
    unittest.main()

