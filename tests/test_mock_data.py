import unittest

from cctv_query.engine import build_vehicle_routes
from cctv_query.mock_data import EVENTS, FIELDNAMES, generate_rows
from cctv_query.models import CCTVRecord


class MockDataTests(unittest.TestCase):
    def test_generated_rows_keep_current_csv_contract(self):
        rows = generate_rows(250, seed=7)

        self.assertEqual(len(rows), 250)
        self.assertEqual(tuple(rows[0].keys()), FIELDNAMES)
        self.assertEqual(FIELDNAMES, ("Date", "CCTV_ID", "Timestamp", "Brand", "Color", "Type", "Event"))
        self.assertTrue({row["Event"] for row in rows} <= EVENTS)

    def test_generated_routes_do_not_merge_same_signature_routes(self):
        rows = generate_rows(700, seed=11)
        records = [
            CCTVRecord.from_values(
                row["Date"],
                row["CCTV_ID"],
                row["Timestamp"],
                row["Brand"],
                row["Color"],
                row["Type"],
                row["Event"],
            )
            for row in rows
        ]

        for route in build_vehicle_routes(records):
            events = [record.event for record in route.detections]
            self.assertGreaterEqual(len(events), 2)
            self.assertEqual(events[0], "entry")
            self.assertEqual(events[-1], "exit")
            self.assertTrue(all(event == "pass" for event in events[1:-1]))


if __name__ == "__main__":
    unittest.main()
