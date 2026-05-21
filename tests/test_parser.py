import unittest

from cctv_query.parser import parse_question


class ParseQuestionTests(unittest.TestCase):
    def test_parse_thai_camera_time_range_and_brand_color_request(self):
        spec = parse_question(
            "กล้อง CCTV04 ช่วง 1:05:00-1:15:00 มีรถวิ่งผ่านกี่คัน ยี่ห้อและสีอะไรบ้าง",
            known_brands=["Toyota", "Honda", "BMW"],
        )

        self.assertEqual(spec.cctv_id, "CCTV04")
        self.assertEqual(spec.start_time, "01:05:00")
        self.assertEqual(spec.end_time, "01:15:00")
        self.assertIsNone(spec.vehicle_type)
        self.assertTrue(spec.wants_brand_color_breakdown)
        self.assertEqual(spec.language, "th")

    def test_parse_specific_motorcycle_type(self):
        spec = parse_question("กล้อง CCTV04 ช่วง 1:15:00-1:25:00 มีมอเตอร์ไซค์วิ่งผ่านกี่คัน")

        self.assertEqual(spec.cctv_id, "CCTV04")
        self.assertEqual(spec.vehicle_type, "Motorcycle")
        self.assertFalse(spec.wants_brand_color_breakdown)

    def test_parse_thai_date_and_color_filter(self):
        spec = parse_question("วันที่ 12-05-2026 กล้อง CCTV07 มีรถสีแดงผ่านกี่คัน")

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.cctv_id, "CCTV07")
        self.assertEqual(spec.color, "Red")

    def test_parse_english_question(self):
        spec = parse_question(
            "How many red motorcycles passed CCTV7 on 2026-05-12 between 08:00 and 10:00?"
        )

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.cctv_id, "CCTV07")
        self.assertEqual(spec.start_time, "08:00:00")
        self.assertEqual(spec.end_time, "10:00:00")
        self.assertEqual(spec.color, "Red")
        self.assertEqual(spec.vehicle_type, "Motorcycle")
        self.assertEqual(spec.language, "en")

    def test_parse_brand_from_known_csv_values(self):
        spec = parse_question(
            "CCTV04 between 01:00:00 and 02:00:00 Toyota cars",
            known_brands=["Toyota", "Honda"],
        )

        self.assertEqual(spec.brand, "Toyota")
        self.assertEqual(spec.brands, ("Toyota",))
        self.assertEqual(spec.vehicle_type, "Car")

    def test_parse_multiple_brands_as_or_filter(self):
        spec = parse_question(
            "Honda และ Toyota รวมกันได้กี่คัน",
            known_brands=["Toyota", "Honda", "Mazda"],
        )

        self.assertEqual(spec.brand, "Honda")
        self.assertEqual(spec.brands, ("Honda", "Toyota"))

    def test_parse_multiple_date_brand_color_groups_as_or_filter(self):
        spec = parse_question(
            "วันที่ 13 Toyota สีแดง และ วันที่ 14 honda สีขาว รวมกันได้เท่าไหร่",
            known_brands=["Toyota", "Honda", "Mazda"],
            known_colors=["Red", "White", "Blue"],
            known_dates=["13-05-2026", "14-05-2026"],
        )

        self.assertIsNone(spec.date)
        self.assertIsNone(spec.brand)
        self.assertEqual(spec.brands, ())
        self.assertIsNone(spec.color)
        self.assertEqual(spec.colors, ())
        self.assertEqual(
            spec.condition_groups,
            (
                {"date": "13-05-2026", "brands": ("Toyota",), "colors": ("Red",)},
                {"date": "14-05-2026", "brands": ("Honda",), "colors": ("White",)},
            ),
        )

    def test_parse_multiple_time_brand_color_groups_inherit_single_date(self):
        spec = parse_question(
            "วันที่ 13 ช่วง 12:00:00-13:00:00 honda สีแดง และ ช่วง 16:00:00 - 17:00:00 toyota สีขาว รวมกันได้กี่คัน",
            known_brands=["Toyota", "Honda", "Mazda"],
            known_colors=["Red", "White", "Blue"],
            known_dates=["13-05-2026"],
        )

        self.assertIsNone(spec.date)
        self.assertIsNone(spec.start_time)
        self.assertIsNone(spec.end_time)
        self.assertEqual(
            spec.condition_groups,
            (
                {
                    "start_time": "12:00:00",
                    "end_time": "13:00:00",
                    "start_seconds": 43200,
                    "end_seconds": 46800,
                    "date": "13-05-2026",
                    "brands": ("Honda",),
                    "colors": ("Red",),
                },
                {
                    "start_time": "16:00:00",
                    "end_time": "17:00:00",
                    "start_seconds": 57600,
                    "end_seconds": 61200,
                    "date": "13-05-2026",
                    "brands": ("Toyota",),
                    "colors": ("White",),
                },
            ),
        )

    def test_parse_day_only_date_from_known_dates(self):
        spec = parse_question(
            "วันที่ 12 มีรถ Toyota ผ่านกี่คัน",
            known_brands=["Toyota"],
            known_dates=["10-05-2026", "11-05-2026", "12-05-2026"],
        )

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.brand, "Toyota")

    def test_day_only_date_outside_known_dates_is_marked_out_of_range(self):
        spec = parse_question(
            "วันที่ 14 มีรถผ่านกี่คัน",
            known_dates=["10-05-2026", "12-05-2026", "13-05-2026"],
        )

        self.assertIsNone(spec.date)
        self.assertEqual(spec.out_of_range_fields, ("date",))

    def test_day_only_date_with_multiple_months_is_ambiguous(self):
        spec = parse_question(
            "วันที่ 12 มีรถผ่านกี่คัน",
            known_dates=["12-05-2026", "12-06-2026", "13-06-2026"],
        )

        self.assertIsNone(spec.date)
        self.assertEqual(spec.ambiguous_date_options, ("12-05-2026", "12-06-2026"))
        self.assertEqual(spec.out_of_range_fields, ())

    def test_parse_route_request(self):
        spec = parse_question(
            "วันที่ 12 รถ Toyota เดินทางไปทางไหนบ้าง",
            known_brands=["Toyota"],
            known_dates=["12-05-2026"],
        )

        self.assertTrue(spec.wants_route)
        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.brand, "Toyota")

    def test_parse_spaced_date_and_brand_alias(self):
        spec = parse_question(
            "12 05 2026 มี Benz เข้าออกกี่คันแล้วมีสีอะไรบ้าง",
            known_brands=["Mercedes-Benz", "Toyota"],
            known_dates=["12-05-2026"],
        )

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.brand, "Mercedes-Benz")
        self.assertTrue(spec.wants_brand_color_breakdown)

    def test_parse_ordinal_camera_and_private_car_type(self):
        spec = parse_question(
            "วันที่ 12 กล้องตัวที่ 1 มีรถส่วนบุคคลผ่านกี่คัน",
            known_dates=["12-05-2026"],
        )

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.cctv_id, "CCTV01")
        self.assertEqual(spec.vehicle_type, "Car")

    def test_parse_cctv_id_with_letter_o_typo(self):
        spec = parse_question("CCTVO1 from 00:01:00 to 00:10:00 cars")

        self.assertEqual(spec.cctv_id, "CCTV01")

    def test_parse_dot_time_range_from_project_question_format(self):
        spec = parse_question("Q3, CCTVO1, 0.01.00 - 0.10.00.\nจำนวนรถยนต์แยกตามสี")

        self.assertEqual(spec.cctv_id, "CCTV01")
        self.assertEqual(spec.start_time, "00:01:00")
        self.assertEqual(spec.end_time, "00:10:00")
        self.assertIsNone(spec.vehicle_type)

    def test_parse_unique_vehicle_list_request(self):
        spec = parse_question(
            "วันที่ 12 รถคันไหนวิ่งผ่านบ้างไม่ซ้ำกัน",
            known_dates=["12-05-2026"],
        )

        self.assertEqual(spec.date, "12-05-2026")
        self.assertTrue(spec.wants_vehicle_list)
        self.assertTrue(spec.wants_distinct_vehicle_count)
        self.assertFalse(spec.wants_route)

    def test_parse_distinct_vehicle_count_request(self):
        spec = parse_question(
            "กระผมอยากทราบว่ารถ truck ในวันที่ 12 นี่มีกี่คันครับ รถไม่ซ้ำ",
            known_dates=["12-05-2026"],
        )

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.vehicle_type, "Truck")
        self.assertTrue(spec.wants_distinct_vehicle_count)

    def test_parse_distinct_vehicle_count_from_no_duplicate_wording(self):
        spec = parse_question("มี Bus กี่คันถ้าไม่นับซ้ำ")

        self.assertEqual(spec.vehicle_type, "Bus")
        self.assertTrue(spec.wants_distinct_vehicle_count)

    def test_parse_vehicle_ordinal_question(self):
        spec = parse_question("วันที่ 12 คันไหนมาคันแรก", known_dates=["12-05-2026"])

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.vehicle_ordinal, 1)
        self.assertTrue(spec.wants_vehicle_list)
        self.assertTrue(spec.wants_distinct_vehicle_count)

    def test_parse_numbered_vehicle_ordinal_question(self):
        spec = parse_question("day 12 which is the 3rd vehicle", known_dates=["12-05-2026"])

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.vehicle_ordinal, 3)

    def test_parse_thai_entry_vehicle_ordinal_question(self):
        spec = parse_question("วันที่ 12 รถเข้าคันที่ 31 คือคันไหน", known_dates=["12-05-2026"])

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.event, "entry")
        self.assertEqual(spec.vehicle_ordinal, 31)

    def test_parse_multiple_exact_colors(self):
        spec = parse_question(
            "มีรถสี Red and Red-White กี่คัน",
            known_colors=["Red", "Red-White", "White"],
        )

        self.assertEqual(spec.colors, ("Red", "Red-White"))
        self.assertEqual(spec.color, "Red")
    
    def test_parse_metallic_color_group(self):
        spec = parse_question("how many metallic vehicles", known_colors=["Bronze", "Silver", "Gold", "Red"])

        self.assertEqual(spec.colors, ("Bronze", "Silver", "Gold"))
        self.assertEqual(spec.color, "Bronze")
        self.assertTrue(spec.wants_metallic_color)

    def test_parse_unknown_explicit_color_as_out_of_range(self):
        spec = parse_question("มีรถสีรุ้งกี่คัน", known_colors=["Red", "White", "Black"])

        self.assertEqual(spec.colors, ())
        self.assertEqual(spec.out_of_range_fields, ("color",))

    def test_parse_brand_origin_filter_terms(self):
        japanese = parse_question("\u0e23\u0e16\u0e0d\u0e35\u0e48\u0e1b\u0e38\u0e48\u0e19\u0e01\u0e35\u0e48\u0e04\u0e31\u0e19")
        european = parse_question("how many european cars")

        self.assertEqual(japanese.brand_origins, ("Japanese",))
        self.assertEqual(european.brand_origins, ("European",))

    def test_parse_origin_breakdown_request(self):
        spec = parse_question(
            "\u0e41\u0e22\u0e01\u0e23\u0e16\u0e15\u0e32\u0e21\u0e1b\u0e23\u0e30\u0e40\u0e17\u0e28 \u0e0d\u0e35\u0e48\u0e1b\u0e38\u0e48\u0e19 \u0e40\u0e01\u0e32\u0e2b\u0e25\u0e35 \u0e22\u0e38\u0e42\u0e23\u0e1b \u0e08\u0e35\u0e19"
        )

        self.assertTrue(spec.wants_origin_breakdown)
        self.assertEqual(spec.brand_origins, ("Japanese", "Korean", "European", "Chinese"))

    def test_parse_origin_brand_breakdown_request(self):
        spec = parse_question("\u0e23\u0e16\u0e17\u0e31\u0e49\u0e07\u0e2b\u0e21\u0e14\u0e15\u0e32\u0e21\u0e1b\u0e23\u0e30\u0e40\u0e17\u0e28\u0e41\u0e25\u0e30\u0e22\u0e35\u0e48\u0e2b\u0e49\u0e2d")

        self.assertTrue(spec.wants_origin_breakdown)
        self.assertTrue(spec.wants_origin_brand_breakdown)

    def test_parse_supported_cross_breakdown_requests(self):
        cases = {
            "\u0e23\u0e16\u0e17\u0e31\u0e49\u0e07\u0e2b\u0e21\u0e14\u0e15\u0e32\u0e21\u0e1b\u0e23\u0e30\u0e40\u0e17\u0e28\u0e41\u0e25\u0e30\u0e1b\u0e23\u0e30\u0e40\u0e20\u0e17\u0e23\u0e16": "origin_type",
            "\u0e23\u0e16\u0e17\u0e31\u0e49\u0e07\u0e2b\u0e21\u0e14\u0e15\u0e32\u0e21\u0e22\u0e35\u0e48\u0e2b\u0e49\u0e2d\u0e41\u0e25\u0e30\u0e1b\u0e23\u0e30\u0e40\u0e20\u0e17\u0e23\u0e16": "brand_type",
            "\u0e41\u0e15\u0e48\u0e25\u0e30\u0e01\u0e25\u0e49\u0e2d\u0e07\u0e21\u0e35 entry exit pass \u0e40\u0e17\u0e48\u0e32\u0e44\u0e2b\u0e23\u0e48": "camera_event",
            "\u0e41\u0e15\u0e48\u0e25\u0e30\u0e0a\u0e31\u0e48\u0e27\u0e42\u0e21\u0e07\u0e21\u0e35\u0e23\u0e16\u0e40\u0e02\u0e49\u0e32\u0e2d\u0e2d\u0e01\u0e01\u0e35\u0e48\u0e04\u0e31\u0e19": "hour_event",
            "\u0e23\u0e16\u0e17\u0e31\u0e49\u0e07\u0e2b\u0e21\u0e14\u0e15\u0e32\u0e21\u0e2a\u0e35\u0e41\u0e25\u0e30\u0e1b\u0e23\u0e30\u0e40\u0e20\u0e17\u0e23\u0e16": "color_type",
            "\u0e23\u0e16\u0e17\u0e31\u0e49\u0e07\u0e2b\u0e21\u0e14\u0e15\u0e32\u0e21\u0e1b\u0e23\u0e30\u0e40\u0e17\u0e28\u0e41\u0e25\u0e30\u0e2a\u0e35": "origin_color",
            "\u0e23\u0e16\u0e40\u0e14\u0e34\u0e19\u0e17\u0e32\u0e07\u0e08\u0e32\u0e01\u0e01\u0e25\u0e49\u0e2d\u0e07\u0e44\u0e2b\u0e19\u0e44\u0e1b\u0e01\u0e25\u0e49\u0e2d\u0e07\u0e44\u0e2b\u0e19\u0e21\u0e32\u0e01\u0e17\u0e35\u0e48\u0e2a\u0e38\u0e14": "route_od",
            "\u0e41\u0e15\u0e48\u0e25\u0e30\u0e22\u0e35\u0e48\u0e2b\u0e49\u0e2d\u0e43\u0e0a\u0e49\u0e40\u0e2a\u0e49\u0e19\u0e17\u0e32\u0e07\u0e44\u0e2b\u0e19\u0e1a\u0e48\u0e2d\u0e22\u0e2a\u0e38\u0e14": "brand_route",
            "\u0e23\u0e16\u0e17\u0e35\u0e48 entry \u0e41\u0e25\u0e49\u0e27\u0e44\u0e21\u0e48 exit \u0e41\u0e22\u0e01\u0e15\u0e32\u0e21\u0e01\u0e25\u0e49\u0e2d\u0e07 entry": "unclosed_entry_camera",
        }

        for question, expected in cases.items():
            with self.subTest(question=question):
                self.assertIn(expected, parse_question(question).cross_breakdowns)

    def test_parse_explicit_event_filter(self):
        spec = parse_question("day 12 event entry vehicles", known_dates=["12-05-2026"])

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.event, "entry")

    def test_parse_bare_entry_event_filter(self):
        spec = parse_question("day 12 entry vehicles", known_dates=["12-05-2026"])

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.event, "entry")

    def test_parse_entry_without_exit_as_unclosed_count(self):
        spec = parse_question("day 12 entry vehicles without exit", known_dates=["12-05-2026"])

        self.assertEqual(spec.date, "12-05-2026")
        self.assertIsNone(spec.event)
        self.assertTrue(spec.wants_unclosed_entry_count)

    def test_parse_entry_exit_count_as_event_breakdown(self):
        spec = parse_question("day 12 count entry and exit vehicles", known_dates=["12-05-2026"])

        self.assertEqual(spec.date, "12-05-2026")
        self.assertIsNone(spec.event)
        self.assertTrue(spec.wants_event_breakdown)

    def test_parse_thai_peak_hour_entry_exit_question(self):
        spec = parse_question(
            "จาก cctv01 ช่วงเวลาชั่วโมงไหนรถเข้าออกเยอะที่สุด",
            known_dates=["12-05-2026"],
        )

        self.assertEqual(spec.cctv_id, "CCTV01")
        self.assertTrue(spec.wants_peak_hour)
        self.assertEqual(spec.events, ("entry", "exit"))

    def test_parse_thai_hour_average_question(self):
        spec = parse_question("ค่าเฉลี่ยจำนวนรถในแต่ละ 1 ชั่วโมง")

        self.assertTrue(spec.wants_hour_average)
        self.assertFalse(spec.wants_peak_hour)
        self.assertIsNone(spec.average_hours)

    def test_parse_hour_average_denominator_from_day_and_hour_text(self):
        spec = parse_question("ค่าเฉลี่ยจำนวนรถจากแค่ 1 วัน 24 ชั่วโมง")

        self.assertTrue(spec.wants_hour_average)
        self.assertEqual(spec.average_hours, 24)

    def test_parse_count_comparison_operators(self):
        greater = parse_question("วันที่ 12 มีรถมากกว่า 10 คันไหม", known_dates=["12-05-2026"])
        less_equal = parse_question("cars <= 5")
        at_least = parse_question("รถอย่างน้อย 3 คัน")

        self.assertEqual(greater.count_operator, "gt")
        self.assertEqual(greater.count_threshold, 10)
        self.assertEqual(less_equal.count_operator, "lte")
        self.assertEqual(less_equal.count_threshold, 5)
        self.assertEqual(at_least.count_operator, "gte")
        self.assertEqual(at_least.count_threshold, 3)

    def test_parse_brand_group_comparison(self):
        spec = parse_question(
            "วันที่ 12 Honda เยอะกว่า Toyota เท่าไหร่",
            known_brands=["Honda", "Toyota", "Mazda"],
            known_dates=["12-05-2026"],
        )

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.brands, ("Honda", "Toyota"))
        self.assertEqual(spec.group_comparison, {"dimension": "brand", "left": "Honda", "right": "Toyota"})

    def test_parse_extended_color_aliases(self):
        cases = {
            "รถสีฟ้า": "Blue",
            "รถสีน้ำเงิน": "Navy Blue",
            "รถสีฟ้า-ขาว": "Blue-White",
            "รถสีบรอนซ์ทอง": "Bronze Gold",
            "รถสีบรอนซ์เทา": "Bronze Gray",
            "รถสีบรอนซ์เงิน": "Bronze Silver",
            "รถสีเทาเข้ม": "Charcoal",
            "รถสีเหลืองเขียว": "Chartreuse",
            "รถสีเขียวเข้ม": "Dark Green",
            "รถสีเขียวอู่อน": "Light Green",
            "รถสีเขียวเมทาลิค": "Metallic Green",
            "รถสีเขียวขี้ม้า": "Olive Green",
            "รถสีเทาฟ้า": "Slate Blue",
            "รถสีเหลือง-เขียว": "Yellow-Green",
        }

        for question, color in cases.items():
            with self.subTest(question=question):
                spec = parse_question(question)
                self.assertEqual(spec.color, color)

    def test_parse_electric_vehicle_does_not_match_blue_color(self):
        spec = parse_question("รถไฟฟ้ามีกี่คัน", known_colors=["Blue", "White", "Black"])

        self.assertIsNone(spec.color)
        self.assertEqual(spec.colors, ())
        self.assertEqual(spec.out_of_range_fields, ("fuel_type",))

    def test_parse_tracking_presence_and_duration_questions(self):
        presence = parse_question("ช่วงเวลา 08:00-08:10 มีรถจอดอยู่กี่คัน")
        duration = parse_question("tracking duration รถค้างนานเท่าไหร่")

        self.assertEqual(presence.start_time, "08:00:00")
        self.assertEqual(presence.end_time, "08:10:00")
        self.assertTrue(presence.wants_presence_count)
        self.assertEqual(presence.presence_min_seconds, 600)
        self.assertTrue(duration.wants_tracking_duration)

    def test_parse_thai_peak_camera_entry_exit_question(self):
        spec = parse_question(
            "กล้องตัวไหนรถเข้าออกเยอะที่สุด",
            known_dates=["12-05-2026"],
        )

        self.assertIsNone(spec.cctv_id)
        self.assertTrue(spec.wants_peak_camera)
        self.assertEqual(spec.events, ("entry", "exit"))

    def test_parse_exits_alias_as_exit_event(self):
        spec = parse_question("day 12 event exits vehicles", known_dates=["12-05-2026"])

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.event, "exit")

    def test_parse_pass_only_event(self):
        spec = parse_question("day 12 just pass vehicles", known_dates=["12-05-2026"])

        self.assertEqual(spec.date, "12-05-2026")
        self.assertEqual(spec.event, "pass")

    def test_parse_thai_entry_exit_and_pass_events(self):
        known_dates = ["12-05-2026"]

        self.assertEqual(parse_question("วันที่ 12 รถเข้ากี่คัน", known_dates=known_dates).event, "entry")
        self.assertEqual(parse_question("วันที่ 12 รถออกกี่คัน", known_dates=known_dates).event, "exit")
        self.assertEqual(parse_question("วันที่ 12 แค่ขับผ่านกี่คัน", known_dates=known_dates).event, "pass")


if __name__ == "__main__":
    unittest.main()
