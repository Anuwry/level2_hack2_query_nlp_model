import unittest
from pathlib import Path

from cctv_query.sql_exchange import convert_sql_to_response, convert_sql_to_tables


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class SqlExchangeTests(unittest.TestCase):
    def test_converts_insert_values_to_csv_table(self):
        tables = convert_sql_to_tables(
            """
            CREATE TABLE IF NOT EXISTS vehicles (
              id INTEGER PRIMARY KEY,
              brand TEXT,
              color TEXT,
              note TEXT
            );
            INSERT INTO vehicles (id, brand, color, note) VALUES
              (1, 'Toyota', 'Red', 'hello, world'),
              (2, 'Honda', NULL, 'Bob''s car');
            """
        )

        self.assertEqual(len(tables), 1)
        self.assertEqual(tables[0].name, "vehicles")
        self.assertEqual(tables[0].columns, ("id", "brand", "color", "note"))
        self.assertEqual(tables[0].rows[0]["note"], "hello, world")
        self.assertEqual(tables[0].rows[1]["color"], "")
        self.assertEqual(tables[0].rows[1]["note"], "Bob's car")
        self.assertIn('"hello, world"', tables[0].to_csv())

    def test_examples_sql_derives_required_output_view(self):
        sql_text = (PROJECT_ROOT / "schema.sql").read_text(encoding="utf-8")
        sql_text += "\n" + (PROJECT_ROOT / "examples.sql").read_text(encoding="utf-8")

        response = convert_sql_to_response(sql_text)
        tables = {table["name"]: table for table in response["tables"]}

        self.assertEqual(response["selected_table"], "required_output_view")
        self.assertEqual(tables["vehicle_tracks"]["row_count"], 18)
        self.assertEqual(tables["required_output_view"]["row_count"], 18)
        self.assertEqual(
            tables["required_output_view"]["columns"],
            ["Date", "CCTV_ID", "First_Seen", "Last_Seen", "Brand", "Color", "Type", "Event"],
        )
        self.assertEqual(tables["required_output_view"]["rows"][0]["CCTV_ID"], "CCTV01")
        self.assertEqual(tables["required_output_view"]["rows"][0]["Brand"], "Toyota")
        self.assertEqual(tables["required_output_view"]["rows"][0]["Event"], "pass")

    def test_rejects_sql_without_insert_rows(self):
        with self.assertRaises(ValueError):
            convert_sql_to_response("CREATE TABLE vehicles (id INTEGER);")


if __name__ == "__main__":
    unittest.main()
