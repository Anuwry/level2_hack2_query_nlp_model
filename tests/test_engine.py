import unittest

from cctv_query.engine import CCTVQueryEngine
from cctv_query.models import CCTVRecord


def make_records():
    return [
        CCTVRecord.from_values("10-05-2026", "CCTV04", "01:06:00", "Toyota", "White", "Car"),
        CCTVRecord.from_values("10-05-2026", "CCTV04", "01:09:30", "Honda", "Red", "Car"),
        CCTVRecord.from_values("10-05-2026", "CCTV04", "01:14:59", "BMW", "Black", "Car"),
        CCTVRecord.from_values("10-05-2026", "CCTV04", "01:16:00", "Yamaha", "Black", "Motorcycle"),
        CCTVRecord.from_values("10-05-2026", "CCTV04", "01:20:10", "Honda", "White", "Motorcycle"),
        CCTVRecord.from_values("10-05-2026", "CCTV04", "01:24:50", "Yamaha", "Red", "Motorcycle"),
        CCTVRecord.from_values("10-05-2026", "CCTV10", "00:46:01", "Toyota", "Silver", "Car"),
        CCTVRecord.from_values("10-05-2026", "CCTV10", "00:51:20", "Isuzu", "Black", "Truck"),
        CCTVRecord.from_values("10-05-2026", "CCTV10", "00:54:59", "Honda", "White", "Car"),
        CCTVRecord.from_values("12-05-2026", "CCTV09", "22:27:13", "Toyota", "Red", "Car", event="entry"),
        CCTVRecord.from_values("12-05-2026", "CCTV08", "22:29:56", "Toyota", "Red", "Car", event="pass"),
        CCTVRecord.from_values("12-05-2026", "CCTV07", "22:30:56", "Toyota", "Red", "Car", event="pass"),
        CCTVRecord.from_values("12-05-2026", "CCTV04", "22:34:20", "Toyota", "Red", "Car", event="exit"),
        CCTVRecord.from_values("12-05-2026", "CCTV07", "08:10:00", "Toyota", "Red", "Car"),
        CCTVRecord.from_values("12-05-2026", "CCTV07", "09:00:00", "Honda", "Red", "Motorcycle"),
        CCTVRecord.from_values("12-05-2026", "CCTV07", "10:30:00", "Isuzu", "Red", "Truck"),
        CCTVRecord.from_values("12-05-2026", "CCTV07", "11:00:00", "Nissan", "Red-White", "Car"),
        CCTVRecord.from_values("12-05-2026", "CCTV07", "11:15:00", "MG", "Metallic Green", "Car"),
        CCTVRecord.from_values("12-05-2026", "CCTV04", "12:00:00", "Mercedes-Benz", "Red", "Bus", event="entry"),
        CCTVRecord.from_values("12-05-2026", "CCTV07", "12:03:00", "Mercedes-Benz", "Red", "Bus", event="pass"),
        CCTVRecord.from_values("12-05-2026", "CCTV08", "12:05:00", "Mercedes-Benz", "Red", "Bus", event="exit"),
        CCTVRecord.from_values("12-05-2026", "CCTV09", "13:00:00", "Mercedes-Benz", "Dark Green", "Bus", event="entry"),
        CCTVRecord.from_values("12-05-2026", "CCTV08", "13:02:00", "Mercedes-Benz", "Dark Green", "Bus", event="exit"),
        CCTVRecord.from_values("12-05-2026", "CCTV01", "15:00:00", "Mazda", "Blue", "Car"),
        CCTVRecord.from_values("12-05-2026", "CCTV01", "15:05:00", "Yamaha", "Blue", "Motorcycle"),
        CCTVRecord.from_values("12-05-2026", "CCTV02", "16:00:00", "Mazda", "Red-White", "Car"),
    ]


def make_event_records():
    return [
        CCTVRecord.from_values(
            "12-05-2026",
            "CCTV01",
            "08:00:00",
            "Toyota",
            "Red",
            "Car",
            event="entry",
        ),
        CCTVRecord.from_values(
            "12-05-2026",
            "CCTV02",
            "08:05:00",
            "Toyota",
            "Red",
            "Car",
            event="exit",
        ),
        CCTVRecord.from_values(
            "12-05-2026",
            "CCTV01",
            "09:00:00",
            "Honda",
            "White",
            "Car",
            event="entry",
        ),
        CCTVRecord.from_values(
            "12-05-2026",
            "CCTV03",
            "09:30:00",
            "Honda",
            "White",
            "Car",
            event="exit",
        ),
        CCTVRecord.from_values(
            "12-05-2026",
            "CCTV04",
            "10:00:00",
            "Isuzu",
            "Black",
            "Truck",
            event="pass",
        ),
    ]


def make_open_entry_records():
    return [
        CCTVRecord.from_values("12-05-2026", "CCTV01", "08:00:00", "Toyota", "Red", "Car", event="entry"),
        CCTVRecord.from_values("12-05-2026", "CCTV02", "08:05:00", "Toyota", "Red", "Car", event="exit"),
        CCTVRecord.from_values("12-05-2026", "CCTV01", "09:00:00", "Honda", "White", "Car", event="entry"),
        CCTVRecord.from_values("12-05-2026", "CCTV03", "10:00:00", "Mazda", "Blue", "Car", event="entry"),
        CCTVRecord.from_values("12-05-2026", "CCTV04", "10:03:00", "Mazda", "Blue", "Car", event="pass"),
        CCTVRecord.from_values("12-05-2026", "CCTV04", "11:00:00", "Isuzu", "Black", "Truck", event="pass"),
    ]


class CCTVQueryEngineTests(unittest.TestCase):
    def setUp(self):
        self.engine = CCTVQueryEngine(make_records())

    def test_answers_count_and_brand_color_breakdown(self):
        result = self.engine.ask(
            "กล้อง CCTV04 ช่วง 1:05:00-1:15:00 มีรถวิ่งผ่านกี่คัน ยี่ห้อและสีอะไรบ้าง"
        )

        self.assertEqual(result.count, 3)
        self.assertEqual(result.summary.brand_color_counts[("BMW", "Black")], 1)
        self.assertIn("พบ 3 คัน", result.answer)
        self.assertIn("Toyota White 1 คัน", result.answer)

    def test_filters_specific_vehicle_type(self):
        result = self.engine.ask("กล้อง CCTV04 ช่วง 1:15:00-1:25:00 มีมอเตอร์ไซค์วิ่งผ่านกี่คัน")

        self.assertEqual(result.count, 3)
        self.assertEqual(result.summary.type_counts["Motorcycle"], 3)
        self.assertNotIn("Toyota White", result.answer)

    def test_filters_cctv_time_and_ignores_unsupported_direction_word(self):
        result = self.engine.ask(
            "กล้อง CCTV10 ช่วง 0:45:00-0:55:00 มีรถวิ่งออกกี่คัน ยี่ห้อและสีอะไรบ้าง"
        )

        self.assertEqual(result.count, 3)
        self.assertIn("Isuzu Black 1 คัน", result.answer)

    def test_filters_date_and_color(self):
        result = self.engine.ask("วันที่ 12-05-2026 กล้อง CCTV07 มีรถสีแดงผ่านกี่คัน")

        self.assertEqual(result.count, 5)
        self.assertEqual(result.summary.color_counts["Red"], 5)
        self.assertIn("วันที่ 12-05-2026", result.answer)

    def test_day_only_date_and_brand_count_unique_routed_vehicle(self):
        result = self.engine.ask("วันที่ 12 มีรถ Toyota ผ่านกี่คัน")

        self.assertEqual(result.count, 2)
        self.assertEqual(result.event_count, 5)
        self.assertEqual(result.spec.date, "12-05-2026")
        self.assertEqual(result.summary.brand_color_counts[("Toyota", "Red")], 2)

    def test_broad_query_returns_user_warnings(self):
        result = self.engine.ask("red vehicles")

        self.assertIn("No date specified; searching all dates.", result.warnings)
        self.assertIn("No CCTV camera specified; searching all cameras.", result.warnings)
        self.assertIn("No time range specified; searching the full day.", result.warnings)

    def test_ambiguous_day_only_date_needs_clarification(self):
        engine = CCTVQueryEngine(
            [
                CCTVRecord.from_values("12-05-2026", "CCTV01", "08:00:00", "Toyota", "Red", "Car"),
                CCTVRecord.from_values("12-06-2026", "CCTV01", "08:00:00", "Honda", "Red", "Car"),
            ]
        )

        result = engine.ask("day 12 red cars")

        self.assertTrue(result.needs_clarification)
        self.assertEqual(result.count, 0)
        self.assertEqual(result.clarifications[0]["field"], "date")
        self.assertTrue(result.clarifications[0]["required"])
        self.assertEqual(
            [option["value"] for option in result.clarifications[0]["options"]],
            ["12-05-2026", "12-06-2026"],
        )

    def test_color_query_offers_related_exact_color_options(self):
        result = self.engine.ask("วันที่ 12 มีรถสีแดงกี่คัน")

        self.assertFalse(result.needs_clarification)
        self.assertEqual(result.spec.colors, ("Red",))
        color_clarification = next(item for item in result.clarifications if item["field"] == "color")
        options = {option["value"]: option for option in color_clarification["options"]}
        self.assertEqual(options["Red"]["count"], 5)
        self.assertEqual(options["Red-White"]["count"], 2)
        self.assertIn("Red, Red-White", options)
        self.assertTrue(options["Red"]["selected"])

    def test_missing_exact_base_color_can_offer_related_colors_without_out_of_range(self):
        result = self.engine.ask("วันที่ 12 มีรถสีเขียวกี่คัน")

        self.assertFalse(result.out_of_range)
        self.assertEqual(result.count, 0)
        color_clarification = next(item for item in result.clarifications if item["field"] == "color")
        options = {option["value"]: option for option in color_clarification["options"]}
        self.assertEqual(options["Dark Green"]["count"], 1)
        self.assertEqual(options["Metallic Green"]["count"], 1)

    def test_route_answer_lists_camera_sequence_for_selected_vehicle(self):
        result = self.engine.ask("วันที่ 12 รถ Toyota ช่วง 22:00-23:00 เดินทางไปทางไหนบ้าง")

        self.assertEqual(result.count, 1)
        self.assertEqual(result.event_count, 4)
        self.assertEqual(result.routes[0].path, ["CCTV09", "CCTV08", "CCTV07", "CCTV04"])
        self.assertIn("CCTV09 -> CCTV08 -> CCTV07 -> CCTV04", result.answer)
        self.assertIn("22:27:13-22:34:20", result.answer)

    def test_route_answer_does_not_count_pass_only_orphans_as_routes(self):
        engine = CCTVQueryEngine(
            [
                CCTVRecord.from_values("12-05-2026", "CCTV01", "08:00:00", "Hino", "Black", "Bus", event="entry"),
                CCTVRecord.from_values("12-05-2026", "CCTV02", "08:03:00", "Hino", "Black", "Bus", event="pass"),
                CCTVRecord.from_values("12-05-2026", "CCTV03", "08:05:00", "Hino", "Black", "Bus", event="exit"),
                CCTVRecord.from_values("12-05-2026", "CCTV05", "10:00:00", "Hino", "Black", "Bus", event="pass"),
            ]
        )

        result = engine.ask("day 12 bus route")

        self.assertEqual(result.count, 1)
        self.assertEqual(len(result.routes), 1)
        self.assertEqual(result.event_count, 3)
        self.assertEqual(result.routes[0].path, ["CCTV01", "CCTV02", "CCTV03"])

    def test_spaced_date_and_brand_alias_do_not_fall_back_to_all_records(self):
        result = self.engine.ask("12 05 2026 มี Benz เข้าออกกี่คันแล้วมีสีอะไรบ้าง")

        self.assertEqual(result.spec.date, "12-05-2026")
        self.assertEqual(result.spec.brand, "Mercedes-Benz")
        self.assertEqual(result.count, 2)
        self.assertEqual(result.event_count, 5)
        self.assertEqual(result.summary.brand_counts, {"Mercedes-Benz": 2})
        self.assertEqual(result.summary.color_counts["Red"], 1)
        self.assertEqual(result.summary.color_counts["Dark Green"], 1)
        self.assertIn("Mercedes-Benz Red 1 คัน", result.answer)
        self.assertIn("Mercedes-Benz Dark Green 1 คัน", result.answer)
        self.assertNotIn("Toyota", result.answer)

    def test_ordinal_camera_and_private_car_type_filter_to_cctv01_cars(self):
        result = self.engine.ask("วันที่ 12 กล้องตัวที่ 1 มีรถส่วนบุคคลผ่านกี่คัน")

        self.assertEqual(result.spec.date, "12-05-2026")
        self.assertEqual(result.spec.cctv_id, "CCTV01")
        self.assertEqual(result.spec.vehicle_type, "Car")
        self.assertEqual(result.count, 1)
        self.assertEqual(result.summary.type_counts["Car"], 1)
        self.assertNotIn("Motorcycle", result.summary.type_counts)

    def test_unique_vehicle_list_request_lists_vehicles_not_only_count(self):
        result = self.engine.ask("วันที่ 12 รถคันไหนวิ่งผ่านบ้างไม่ซ้ำกัน")

        self.assertTrue(result.spec.wants_vehicle_list)
        self.assertGreater(result.count, 1)
        self.assertIn("รายการรถไม่ซ้ำ:", result.answer)
        self.assertIn("Toyota Red Car", result.answer)
        self.assertIn("CCTV09 -> CCTV08 -> CCTV07 -> CCTV04", result.answer)
        self.assertIn("Mazda Blue Car", result.answer)

    def test_color_filter_is_exact_not_partial(self):
        red_result = self.engine.ask("CCTV07 on 2026-05-12 red vehicles")
        green_result = self.engine.ask("CCTV07 on 2026-05-12 green vehicles")

        self.assertEqual(red_result.count, 5)
        self.assertNotIn("Red-White", red_result.summary.color_counts)
        self.assertEqual(green_result.count, 0)
        self.assertNotIn("Metallic Green", green_result.summary.color_counts)

    def test_multiple_color_filter_uses_or_with_exact_colors(self):
        result = self.engine.ask("วันที่ 12 มีรถสี Red and Red-White กี่คัน")

        self.assertEqual(result.spec.colors, ("Red", "Red-White"))
        self.assertEqual(result.count, 7)
        self.assertEqual(result.summary.color_counts["Red"], 5)
        self.assertEqual(result.summary.color_counts["Red-White"], 2)
        self.assertNotIn("White", result.summary.color_counts)
        self.assertIn("สี Red, Red-White", result.answer)

    def test_explicit_date_outside_csv_range_returns_out_of_range(self):
        result = self.engine.ask("วันที่ 14-05-2026 มีรถผ่านกี่คัน")

        self.assertTrue(result.out_of_range)
        self.assertEqual(result.out_of_range_reasons, ("date",))
        self.assertEqual(result.count, 0)
        self.assertEqual(result.answer, "Question Out Of Range")

    def test_day_only_date_outside_csv_range_returns_out_of_range(self):
        result = self.engine.ask("วันที่ 14 มีรถผ่านกี่คัน")

        self.assertTrue(result.out_of_range)
        self.assertEqual(result.out_of_range_reasons, ("date",))
        self.assertEqual(result.answer, "Question Out Of Range")

    def test_cctv_outside_csv_range_returns_out_of_range(self):
        result = self.engine.ask("CCTV99 on 2026-05-12 red vehicles")

        self.assertTrue(result.out_of_range)
        self.assertEqual(result.out_of_range_reasons, ("cctv_id",))
        self.assertEqual(result.answer, "Question Out Of Range")

    def test_distinct_vehicle_count_uses_route_groups_not_brand_color_identity(self):
        engine = CCTVQueryEngine(
            [
                CCTVRecord.from_values("12-05-2026", "CCTV01", "08:00:00", "Hino", "Black", "Truck"),
                CCTVRecord.from_values("12-05-2026", "CCTV02", "08:03:00", "Hino", "Black", "Truck"),
                CCTVRecord.from_values("12-05-2026", "CCTV03", "20:00:00", "Hino", "Black", "Truck"),
                CCTVRecord.from_values("12-05-2026", "CCTV04", "20:05:00", "Hino", "Black", "Truck"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "21:00:00", "Ford", "Bronze", "Truck"),
            ]
        )

        normal_result = engine.ask("วันที่ 12 มีรถ truck กี่คัน")
        distinct_result = engine.ask("กระผมอยากทราบว่ารถ truck ในวันที่ 12 นี่มีกี่คันครับ รถไม่ซ้ำ")

        self.assertEqual(normal_result.count, 3)
        self.assertEqual(distinct_result.count, 3)
        self.assertEqual(len(distinct_result.routes), 3)
        self.assertEqual(distinct_result.event_count, 5)
        self.assertEqual(distinct_result.summary.brand_color_counts[("Hino", "Black")], 2)
        self.assertIn("3 คันไม่ซ้ำ", distinct_result.answer)
        self.assertNotIn("รวมซ้ำ", distinct_result.answer)

    def test_event_filter_counts_explicit_entry_events(self):
        engine = CCTVQueryEngine(make_event_records())

        result = engine.ask("day 12 event entry vehicles")

        self.assertEqual(result.spec.event, "entry")
        self.assertEqual(result.count, 2)
        self.assertEqual(result.event_count, 2)
        self.assertEqual(result.summary.brand_counts["Toyota"], 1)
        self.assertEqual(result.summary.brand_counts["Honda"], 1)

    def test_bare_entry_event_filter_counts_entry_events(self):
        engine = CCTVQueryEngine(make_event_records())

        result = engine.ask("day 12 entry vehicles")

        self.assertEqual(result.spec.event, "entry")
        self.assertEqual(result.count, 2)

    def test_entry_without_exit_counts_routes_and_offers_event_options(self):
        engine = CCTVQueryEngine(make_open_entry_records())

        result = engine.ask("day 12 entry vehicles without exit")

        self.assertTrue(result.spec.wants_unclosed_entry_count)
        self.assertIsNone(result.spec.event)
        self.assertEqual(result.count, 2)
        self.assertEqual({route.representative.brand for route in result.routes}, {"Honda", "Mazda"})
        self.assertIn("entry and no exit", result.answer)
        options = {option["id"]: option for option in result.answer_options}
        self.assertEqual(options["entry_without_exit"]["csv_answer"], "[entry_without_exit:2]")
        self.assertEqual(options["event_breakdown"]["csv_answer"], "[entry:3, exit:1, pass:2]")
        self.assertEqual(options["entry_only"]["csv_answer"], "[entry:3]")
        self.assertEqual(options["exit_only"]["csv_answer"], "[exit:1]")

    def test_event_breakdown_question_returns_event_counts_and_options(self):
        engine = CCTVQueryEngine(make_open_entry_records())

        result = engine.ask("day 12 count entry and exit vehicles")

        self.assertTrue(result.spec.wants_event_breakdown)
        self.assertEqual(result.count, 6)
        self.assertEqual(result.summary.event_counts["entry"], 3)
        self.assertEqual(result.summary.event_counts["exit"], 1)
        self.assertIn("Event breakdown: entry:3, exit:1, pass:2", result.answer)
        self.assertTrue(result.answer_options)

    def test_peak_hour_question_groups_entry_exit_by_hour_for_camera(self):
        engine = CCTVQueryEngine(
            [
                CCTVRecord.from_values("12-05-2026", "CCTV01", "08:05:00", "Toyota", "Red", "Car", event="entry"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "08:10:00", "Honda", "Red", "Car", event="exit"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "08:20:00", "Honda", "Blue", "Car", event="pass"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "09:05:00", "Mazda", "White", "Car", event="entry"),
                CCTVRecord.from_values("12-05-2026", "CCTV02", "08:30:00", "Isuzu", "Black", "Truck", event="entry"),
            ]
        )

        result = engine.ask("จาก cctv01 ช่วงเวลาชั่วโมงไหนรถเข้าออกเยอะที่สุด")

        self.assertTrue(result.spec.wants_peak_hour)
        self.assertEqual(result.spec.events, ("entry", "exit"))
        self.assertEqual(result.aggregation["top"][0]["label"], "08:00-08:59")
        self.assertEqual(result.aggregation["top"][0]["count"], 2)
        self.assertEqual(result.count, 3)
        self.assertIn("08:00-08:59", result.answer)
        self.assertNotIn("No time range specified", result.warnings)

    def test_peak_camera_question_groups_entry_exit_by_camera(self):
        engine = CCTVQueryEngine(
            [
                CCTVRecord.from_values("12-05-2026", "CCTV01", "08:05:00", "Toyota", "Red", "Car", event="entry"),
                CCTVRecord.from_values("12-05-2026", "CCTV02", "08:10:00", "Honda", "Red", "Car", event="entry"),
                CCTVRecord.from_values("12-05-2026", "CCTV02", "08:20:00", "Honda", "Blue", "Car", event="exit"),
                CCTVRecord.from_values("12-05-2026", "CCTV03", "09:05:00", "Mazda", "White", "Car", event="pass"),
            ]
        )

        result = engine.ask("กล้องตัวไหนรถเข้าออกเยอะที่สุด")

        self.assertTrue(result.spec.wants_peak_camera)
        self.assertEqual(result.spec.events, ("entry", "exit"))
        self.assertEqual(result.aggregation["top"][0]["label"], "CCTV02")
        self.assertEqual(result.aggregation["top"][0]["count"], 2)
        self.assertEqual(result.count, 3)
        self.assertNotIn("No CCTV camera specified", result.warnings)

    def test_exits_alias_filters_exit_event(self):
        engine = CCTVQueryEngine(make_event_records())

        result = engine.ask("day 12 event exits vehicles")

        self.assertEqual(result.spec.event, "exit")
        self.assertEqual(result.count, 2)
        self.assertEqual(result.event_count, 2)
        self.assertEqual(result.summary.brand_counts["Honda"], 1)
        self.assertEqual(result.summary.brand_counts["Toyota"], 1)
        self.assertIn("event exit", result.answer)

    def test_thai_exit_question_filters_exit_event(self):
        engine = CCTVQueryEngine(make_event_records())

        result = engine.ask("วันที่ 12 รถออกกี่คัน")

        self.assertEqual(result.spec.event, "exit")
        self.assertEqual(result.count, 2)

    def test_pass_only_filters_pass_event(self):
        engine = CCTVQueryEngine(make_event_records())

        result = engine.ask("day 12 just pass vehicles")

        self.assertEqual(result.spec.event, "pass")
        self.assertEqual(result.count, 1)
        self.assertEqual(result.event_count, 1)
        self.assertEqual(result.summary.brand_counts["Isuzu"], 1)
        self.assertIn("event pass", result.answer)

    def test_returns_clear_no_match_answer(self):
        result = self.engine.ask("CCTV04 between 05:00:00 and 05:10:00 red trucks")

        self.assertFalse(result.out_of_range)
        self.assertEqual(result.count, 0)
        self.assertIn("No matching records", result.answer)

    def test_unrecognized_question_does_not_fallback_to_all_records(self):
        result = self.engine.ask("what should I eat for dinner")

        self.assertFalse(result.out_of_range)
        self.assertEqual(result.count, 0)
        self.assertEqual(result.event_count, 0)
        self.assertEqual(result.matches, [])
        self.assertIn("Could not understand", result.answer)

    def test_thai_unrecognized_question_does_not_fallback_to_all_records(self):
        result = self.engine.ask("วันนี้อากาศดีไหม")

        self.assertFalse(result.out_of_range)
        self.assertEqual(result.count, 0)
        self.assertEqual(result.event_count, 0)
        self.assertEqual(result.matches, [])
        self.assertIn("ไม่เข้าใจคำถาม", result.answer)

    def test_broad_vehicle_count_can_still_query_all_records(self):
        result = self.engine.ask("how many vehicles are there")

        self.assertFalse(result.out_of_range)
        self.assertGreater(result.count, 0)
        self.assertEqual(result.event_count, len(make_records()))
        self.assertNotIn("Could not understand", result.answer)

    def test_brand_origin_filter_counts_route_groups(self):
        engine = CCTVQueryEngine(
            [
                CCTVRecord.from_values("12-05-2026", "CCTV01", "08:00:00", "Toyota", "Red", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV02", "08:05:00", "Toyota", "Red", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "09:00:00", "Honda", "White", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "10:00:00", "BYD", "White", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "11:00:00", "BMW", "Black", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "12:00:00", "Kia", "Silver", "Car"),
            ]
        )

        result = engine.ask("how many Japanese vehicles")

        self.assertEqual(result.spec.brand_origins, ("Japanese",))
        self.assertEqual(result.count, 2)
        self.assertEqual(result.event_count, 3)
        self.assertEqual(result.summary.origin_counts["Japanese"], 2)
        self.assertNotIn("BYD", result.summary.brand_counts)

    def test_european_origin_filter_includes_european_country_brands(self):
        engine = CCTVQueryEngine(
            [
                CCTVRecord.from_values("12-05-2026", "CCTV01", "08:00:00", "BMW", "Black", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "09:00:00", "Peugeot", "White", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "10:00:00", "Mini", "Red", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "11:00:00", "Ford", "Blue", "Car"),
            ]
        )

        result = engine.ask("how many european vehicles")

        self.assertEqual(result.count, 3)
        self.assertEqual(set(result.summary.brand_counts), {"BMW", "Peugeot", "Mini"})

    def test_origin_breakdown_answer_and_summary(self):
        engine = CCTVQueryEngine(
            [
                CCTVRecord.from_values("12-05-2026", "CCTV01", "08:00:00", "Toyota", "Red", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "09:00:00", "BYD", "White", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "10:00:00", "BMW", "Black", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "11:00:00", "Kia", "Silver", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "12:00:00", "Ford", "Blue", "Car"),
            ]
        )

        result = engine.ask("vehicles by country")

        self.assertTrue(result.spec.wants_origin_breakdown)
        self.assertEqual(result.summary.origin_counts["Japanese"], 1)
        self.assertEqual(result.summary.origin_counts["Chinese"], 1)
        self.assertEqual(result.summary.origin_counts["European"], 1)
        self.assertEqual(result.summary.origin_counts["Korean"], 1)
        self.assertEqual(result.summary.origin_counts["American"], 1)
        self.assertIn("Origin breakdown: American:1, Chinese:1, European:1, Japanese:1, Korean:1", result.answer)

    def test_origin_brand_breakdown_answer_and_summary(self):
        engine = CCTVQueryEngine(
            [
                CCTVRecord.from_values("12-05-2026", "CCTV01", "08:00:00", "Toyota", "Red", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "09:00:00", "Honda", "White", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "10:00:00", "BYD", "White", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "11:00:00", "BMW", "Black", "Car"),
            ]
        )

        result = engine.ask("รถทั้งหมดตามประเทศและยี่ห้อ")

        self.assertTrue(result.spec.wants_origin_brand_breakdown)
        self.assertEqual(result.summary.origin_brand_counts[("Japanese", "Toyota")], 1)
        self.assertEqual(result.summary.origin_brand_counts[("Japanese", "Honda")], 1)
        self.assertIn("สรุปตามประเทศ/ยี่ห้อ:", result.answer)
        self.assertIn("Japanese Honda 1 คัน", result.answer)
        self.assertNotIn("ยี่ห้อ/สีที่พบ", result.answer)

    def test_supported_cross_breakdowns_use_expected_count_sources(self):
        engine = CCTVQueryEngine(
            [
                CCTVRecord.from_values("12-05-2026", "CCTV01", "08:00:00", "Toyota", "Red", "Car", event="entry"),
                CCTVRecord.from_values("12-05-2026", "CCTV02", "08:03:00", "Toyota", "Red", "Car", event="pass"),
                CCTVRecord.from_values("12-05-2026", "CCTV03", "08:05:00", "Toyota", "Red", "Car", event="exit"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "09:00:00", "BYD", "White", "Car", event="entry"),
                CCTVRecord.from_values("12-05-2026", "CCTV03", "09:05:00", "BYD", "White", "Car", event="exit"),
                CCTVRecord.from_values("12-05-2026", "CCTV04", "10:00:00", "Hino", "Black", "Truck", event="entry"),
            ]
        )

        origin_type = engine.ask("vehicles by country and type")
        camera_event = engine.ask("vehicles by camera and event")
        route_od = engine.ask("vehicles by route start and end")
        brand_route = engine.ask("vehicles by brand and route")
        unclosed = engine.ask("entry without exit by camera")

        self.assertEqual(origin_type.summary.cross_counts["origin_type"][("Japanese", "Car")], 1)
        self.assertEqual(origin_type.summary.cross_counts["origin_type"][("Chinese", "Car")], 1)
        self.assertEqual(camera_event.summary.cross_counts["camera_event"][("CCTV02", "pass")], 1)
        self.assertEqual(route_od.summary.cross_counts["route_od"][("CCTV01", "CCTV03")], 2)
        self.assertEqual(brand_route.summary.cross_counts["brand_route"][("Toyota", "CCTV01 -> CCTV02 -> CCTV03")], 1)
        self.assertEqual(unclosed.summary.cross_counts["unclosed_entry_camera"][("CCTV04", "entry_without_exit")], 1)

    def test_metallic_color_filter_uses_bronze_silver_gold(self):
        engine = CCTVQueryEngine(
            [
                CCTVRecord.from_values("12-05-2026", "CCTV01", "08:00:00", "Toyota", "Bronze", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "09:00:00", "Honda", "Silver", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "10:00:00", "BMW", "Gold", "Car"),
                CCTVRecord.from_values("12-05-2026", "CCTV01", "11:00:00", "BYD", "Red", "Car"),
            ]
        )

        result = engine.ask("how many metallic vehicles")

        self.assertEqual(result.spec.colors, ("Bronze", "Silver", "Gold"))
        self.assertEqual(result.count, 3)
        self.assertEqual(set(result.summary.color_counts), {"Bronze", "Silver", "Gold"})
        self.assertIn("metallic", result.answer)


if __name__ == "__main__":
    unittest.main()
