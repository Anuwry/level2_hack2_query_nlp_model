from __future__ import annotations

import re
from collections.abc import Iterable

from cctv_query.classification import METALLIC_COLORS
from cctv_query.models import QuerySpec
from cctv_query.normalization import normalize_cctv_id, normalize_date, normalize_event, normalize_time, time_to_seconds


TIME_TOKEN = r"\d{1,2}[:.]\d{1,2}(?:[:.]\d{1,2})?"
DATE_TOKEN = (
    r"\b(?:"
    r"\d{1,2}\s*[-/]\s*\d{1,2}\s*[-/]\s*\d{4}"
    r"|\d{4}\s*[-/]\s*\d{1,2}\s*[-/]\s*\d{1,2}"
    r"|\d{1,2}\s+\d{1,2}\s+\d{4}"
    r"|\d{4}\s+\d{1,2}\s+\d{1,2}"
    r")\b"
)

TYPE_ALIASES: tuple[tuple[str, str], ...] = (
    ("motorcycles", "Motorcycle"),
    ("motorcycle", "Motorcycle"),
    ("motorbikes", "Motorcycle"),
    ("motorbike", "Motorcycle"),
    ("มอเตอร์ไซค์", "Motorcycle"),
    ("มอเตอร์ไซต์", "Motorcycle"),
    ("จักรยานยนต์", "Motorcycle"),
    ("รถจักรยานยนต์", "Motorcycle"),
    ("trucks", "Truck"),
    ("truck", "Truck"),
    ("lorries", "Truck"),
    ("lorry", "Truck"),
    ("รถบรรทุก", "Truck"),
    ("รถสิบล้อ", "Truck"),
    ("buses", "Bus"),
    ("bus", "Bus"),
    ("รถบัส", "Bus"),
    ("รถเมล์", "Bus"),
    ("cars", "Car"),
    ("car", "Car"),
    ("private vehicles", "Car"),
    ("private vehicle", "Car"),
    ("private cars", "Car"),
    ("private car", "Car"),
    ("รถยนต์ส่วนบุคคล", "Car"),
    ("รถส่วนบุคคล", "Car"),
    ("ส่วนบุคคล", "Car"),
    ("รถยนต์", "Car"),
    ("รถเก๋ง", "Car"),
    ("เก๋ง", "Car"),
)

COLOR_ALIASES: tuple[tuple[str, str], ...] = (
    ("สีแดง", "Red"),
    ("แดง", "Red"),
    ("red", "Red"),
    ("สีขาว", "White"),
    ("ขาว", "White"),
    ("white", "White"),
    ("สีดำ", "Black"),
    ("ดำ", "Black"),
    ("black", "Black"),
    ("สีฟ้า", "Blue"),
    ("สีน้ำเงิน", "Blue"),
    ("ฟ้า", "Blue"),
    ("น้ำเงิน", "Blue"),
    ("blue", "Blue"),
    ("สีเขียว", "Green"),
    ("เขียว", "Green"),
    ("green", "Green"),
    ("สีเหลือง", "Yellow"),
    ("เหลือง", "Yellow"),
    ("yellow", "Yellow"),
    ("สีเทา", "Gray"),
    ("เทา", "Gray"),
    ("grey", "Gray"),
    ("gray", "Gray"),
    ("สีเงิน", "Silver"),
    ("เงิน", "Silver"),
    ("silver", "Silver"),
    ("สีส้ม", "Orange"),
    ("ส้ม", "Orange"),
    ("orange", "Orange"),
    ("สีชมพู", "Pink"),
    ("ชมพู", "Pink"),
    ("pink", "Pink"),
    ("สีม่วง", "Purple"),
    ("ม่วง", "Purple"),
    ("purple", "Purple"),
    ("สีน้ำตาล", "Brown"),
    ("น้ำตาล", "Brown"),
    ("brown", "Brown"),
    ("สีทอง", "Gold"),
    ("ทอง", "Gold"),
    ("gold", "Gold"),
    ("สีบรอนซ์", "Bronze"),
    ("บรอนซ์", "Bronze"),
    ("bronze", "Bronze"),
    ("สีเลือดหมู", "Maroon"),
    ("เลือดหมู", "Maroon"),
    ("maroon", "Maroon"),
)

VEHICLE_TYPE_WORDS = {"car", "cars", "bus", "buses", "truck", "trucks", "motorcycle", "motorcycles"}

_BRAND_ORIGIN_ALIASES: tuple[tuple[str, str], ...] = (
    ("japanese", "Japanese"),
    ("\u0e0d\u0e35\u0e48\u0e1b\u0e38\u0e48\u0e19", "Japanese"),
    ("chinese", "Chinese"),
    ("china", "Chinese"),
    ("\u0e08\u0e35\u0e19", "Chinese"),
    ("south korean", "Korean"),
    ("korean", "Korean"),
    ("\u0e40\u0e01\u0e32\u0e2b\u0e25\u0e35", "Korean"),
    ("european", "European"),
    ("europe", "European"),
    ("\u0e22\u0e38\u0e42\u0e23\u0e1b", "European"),
    ("german", "German"),
    ("\u0e40\u0e22\u0e2d\u0e23\u0e21\u0e31\u0e19", "German"),
    ("american", "American"),
    ("america", "American"),
    ("\u0e2d\u0e40\u0e21\u0e23\u0e34\u0e01\u0e32", "American"),
    ("\u0e2d\u0e40\u0e21\u0e23\u0e34\u0e01\u0e31\u0e19", "American"),
    ("french", "French"),
    ("france", "French"),
    ("\u0e1d\u0e23\u0e31\u0e48\u0e07\u0e40\u0e28\u0e2a", "French"),
    ("malaysian", "Malaysian"),
    ("malaysia", "Malaysian"),
    ("\u0e21\u0e32\u0e40\u0e25\u0e40\u0e0b\u0e35\u0e22", "Malaysian"),
    ("british", "British / UK origin"),
    ("uk origin", "British / UK origin"),
    ("uk", "British / UK origin"),
    ("\u0e2d\u0e31\u0e07\u0e01\u0e24\u0e29", "British / UK origin"),
)


def parse_question(
    question: str,
    known_brands: Iterable[str] | None = None,
    known_colors: Iterable[str] | None = None,
    known_dates: Iterable[str] | None = None,
) -> QuerySpec:
    text = question.strip()
    language = "th" if re.search(r"[\u0E00-\u0E7F]", text) else "en"
    date, date_out_of_range, ambiguous_date_options = _extract_date(text, known_dates)
    cctv_id = _extract_cctv_id(text)
    start_time, end_time = _extract_time_range(text)
    start_seconds = time_to_seconds(start_time) if start_time else None
    end_seconds = time_to_seconds(end_time) if end_time else None
    vehicle_type = _extract_alias(text, TYPE_ALIASES)
    if vehicle_type == "Car" and _plain_thai_vehicle_word_is_generic(text):
        vehicle_type = None
    colors = _extract_colors(text, known_colors)
    color = colors[0] if colors else None
    brand = _extract_brand(text, known_brands)
    brand_origins = _extract_brand_origins(text)
    wants_event_breakdown = _wants_event_breakdown(text)
    wants_unclosed_entry_count = _wants_unclosed_entry_count(text)
    wants_peak_hour = _wants_peak_hour(text)
    wants_peak_camera = _wants_peak_camera(text) and cctv_id is None
    wants_hour_breakdown = _wants_hour_breakdown(text)
    wants_camera_breakdown = _wants_camera_breakdown(text) and cctv_id is None
    event = None if wants_event_breakdown or wants_unclosed_entry_count else _extract_event(text)
    events = _extract_event_scope(text) if (wants_peak_hour or wants_peak_camera or wants_hour_breakdown or wants_camera_breakdown) else ()
    if events:
        event = None
    wants_brand_color_breakdown = _wants_brand_color_breakdown(text)
    wants_origin_breakdown = _wants_origin_breakdown(text)
    wants_route = _wants_route(text)
    wants_vehicle_list = _wants_vehicle_list(text)
    wants_distinct_vehicle_count = _wants_distinct_vehicle_count(text)
    out_of_range_fields = ("date",) if date_out_of_range else ()

    return QuerySpec(
        raw_question=question,
        language=language,
        date=date,
        cctv_id=cctv_id,
        start_time=start_time,
        end_time=end_time,
        start_seconds=start_seconds,
        end_seconds=end_seconds,
        brand=brand,
        brand_origins=brand_origins,
        color=color,
        colors=colors,
        vehicle_type=vehicle_type,
        event=event,
        events=events,
        wants_brand_color_breakdown=wants_brand_color_breakdown,
        wants_origin_breakdown=wants_origin_breakdown,
        wants_route=wants_route,
        wants_vehicle_list=wants_vehicle_list,
        wants_distinct_vehicle_count=wants_distinct_vehicle_count,
        wants_event_breakdown=wants_event_breakdown,
        wants_unclosed_entry_count=wants_unclosed_entry_count,
        wants_peak_hour=wants_peak_hour,
        wants_peak_camera=wants_peak_camera,
        wants_hour_breakdown=wants_hour_breakdown,
        wants_camera_breakdown=wants_camera_breakdown,
        wants_metallic_color=_is_metallic_color_group(text, colors),
        out_of_range_fields=out_of_range_fields,
        ambiguous_date_options=ambiguous_date_options,
    )


def _extract_date(text: str, known_dates: Iterable[str] | None = None) -> tuple[str | None, bool, tuple[str, ...]]:
    match = re.search(DATE_TOKEN, text)
    if match:
        return normalize_date(_clean_date_text(match.group(0))), False, ()

    day = _extract_day_only_date(text)
    if day is None:
        return None, False, ()
    resolved_date = _resolve_day_from_known_dates(day, known_dates)
    if resolved_date:
        return resolved_date, False, ()
    matching_dates = _dates_matching_day(day, known_dates)
    if len(matching_dates) > 1:
        return None, False, tuple(matching_dates)
    return None, _day_is_out_of_known_dates(day, known_dates), ()


def _extract_day_only_date(text: str) -> int | None:
    patterns = (
        r"วันที่\s*(\d{1,2})(?!\s*[-/]\s*\d)",
        r"\b(?:date|day)\s+(\d{1,2})(?:st|nd|rd|th)?\b",
        r"\bon\s+(\d{1,2})(?:st|nd|rd|th)?\b",
    )
    for pattern in patterns:
        match = re.search(pattern, text, flags=re.IGNORECASE)
        if match:
            day = int(match.group(1))
            if 1 <= day <= 31:
                return day
    return None


def _clean_date_text(text: str) -> str:
    return re.sub(r"\s*([-/])\s*", r"\1", text.strip())


def _resolve_day_from_known_dates(day: int, known_dates: Iterable[str] | None) -> str | None:
    matches = _dates_matching_day(day, known_dates)
    if len(matches) == 1:
        return matches[0]
    return None


def _dates_matching_day(day: int, known_dates: Iterable[str] | None) -> list[str]:
    if not known_dates:
        return []

    normalized_dates = sorted({normalize_date(date) for date in known_dates})
    return [date for date in normalized_dates if int(date.split("-", maxsplit=1)[0]) == day]


def _day_is_out_of_known_dates(day: int, known_dates: Iterable[str] | None) -> bool:
    if not known_dates:
        return False
    normalized_dates = sorted({normalize_date(date) for date in known_dates})
    return not any(int(date.split("-", maxsplit=1)[0]) == day for date in normalized_dates)


def _extract_cctv_id(text: str) -> str | None:
    direct = re.search(r"\bCCTV\s*[0oO]*(\d{1,2})\b", text, flags=re.IGNORECASE)
    if direct:
        return normalize_cctv_id(direct.group(1))

    thai_camera = re.search(
        r"กล้อง\s*(?:(?:หมายเลข|ตัวที่|ตัว|ที่)\s*)?0*(\d{1,2})\b",
        text,
        flags=re.IGNORECASE,
    )
    if thai_camera:
        return normalize_cctv_id(thai_camera.group(1))
    return None


def _extract_time_range(text: str) -> tuple[str | None, str | None]:
    matches = re.findall(TIME_TOKEN, text)
    if len(matches) < 2:
        return None, None
    return _normalize_loose_time(matches[0]), _normalize_loose_time(matches[1])


def _normalize_loose_time(value: str) -> str:
    return normalize_time(value.strip().strip(".").replace(".", ":"))


def _extract_alias(text: str, aliases: Iterable[tuple[str, str]]) -> str | None:
    normalized_text = text.casefold()
    for alias, canonical in sorted(aliases, key=lambda item: len(item[0]), reverse=True):
        alias_folded = alias.casefold()
        if _contains_term(normalized_text, alias_folded):
            return canonical
    return None


def _plain_thai_vehicle_word_is_generic(text: str) -> bool:
    normalized_text = text.casefold()
    plain_vehicle_word = "\u0e23\u0e16\u0e22\u0e19\u0e15\u0e4c"
    if plain_vehicle_word not in normalized_text:
        return False

    specific_car_terms = (
        "\u0e23\u0e16\u0e22\u0e19\u0e15\u0e4c\u0e2a\u0e48\u0e27\u0e19\u0e1a\u0e38\u0e04\u0e04\u0e25",
        "\u0e23\u0e16\u0e2a\u0e48\u0e27\u0e19\u0e1a\u0e38\u0e04\u0e04\u0e25",
        "\u0e2a\u0e48\u0e27\u0e19\u0e1a\u0e38\u0e04\u0e04\u0e25",
        "\u0e23\u0e16\u0e40\u0e01\u0e4b\u0e07",
        "\u0e40\u0e01\u0e4b\u0e07",
    )
    return not any(term in normalized_text for term in specific_car_terms)


def _extract_known_phrase(text: str, known_values: Iterable[str] | None) -> str | None:
    if not known_values:
        return None

    normalized_text = text.casefold()
    for value in sorted({item.strip() for item in known_values if item.strip()}, key=len, reverse=True):
        if _contains_term(normalized_text, value.casefold()):
            return value
    return None


def _extract_colors(text: str, known_colors: Iterable[str] | None) -> tuple[str, ...]:
    colors: list[str] = []
    for color in _extract_known_phrases(text, known_colors):
        if color not in colors:
            colors.append(color)
    if colors:
        return tuple(colors)

    if _mentions_metallic_group(text):
        return METALLIC_COLORS

    alias_color = _extract_alias(text, COLOR_ALIASES)
    if alias_color and alias_color not in colors:
        colors.append(alias_color)
    return tuple(colors)


def _mentions_metallic_group(text: str) -> bool:
    normalized_text = text.casefold()
    return any(term in normalized_text for term in ("metallic", "\u0e40\u0e21\u0e17\u0e31\u0e25\u0e25\u0e34\u0e01"))


def _is_metallic_color_group(text: str, colors: tuple[str, ...]) -> bool:
    return colors == METALLIC_COLORS and _mentions_metallic_group(text)


def _extract_brand_origins(text: str) -> tuple[str, ...]:
    normalized_text = text.casefold()
    matches: list[tuple[int, str]] = []
    for alias, origin in _BRAND_ORIGIN_ALIASES:
        for start, _ in _term_spans(normalized_text, alias.casefold()):
            matches.append((start, origin))
    origins: list[str] = []
    for _, origin in sorted(matches, key=lambda item: item[0]):
        if origin not in origins:
            origins.append(origin)
    return tuple(origins)


def _extract_known_phrases(text: str, known_values: Iterable[str] | None) -> list[str]:
    if not known_values:
        return []

    normalized_text = text.casefold()
    candidates = sorted({item.strip() for item in known_values if item.strip()}, key=len, reverse=True)
    matches: list[tuple[int, int, str]] = []
    occupied: list[tuple[int, int]] = []

    for value in candidates:
        value_folded = value.casefold()
        for start, end in _term_spans(normalized_text, value_folded):
            if any(not (end <= used_start or start >= used_end) for used_start, used_end in occupied):
                continue
            matches.append((start, end, value))
            occupied.append((start, end))

    return [value for _, _, value in sorted(matches, key=lambda item: item[0])]


def _extract_brand(text: str, known_brands: Iterable[str] | None) -> str | None:
    brands = [
        brand
        for brand in (known_brands or [])
        if brand.strip() and brand.strip().casefold() not in VEHICLE_TYPE_WORDS
    ]
    exact_match = _extract_known_phrase(text, brands)
    if exact_match:
        return exact_match
    return _extract_brand_alias(text, brands)


def _extract_brand_alias(text: str, brands: Iterable[str]) -> str | None:
    normalized_text = text.casefold()
    alias_matches: list[tuple[int, str]] = []

    for brand in brands:
        for alias in _brand_aliases(brand):
            if _contains_term(normalized_text, alias.casefold()):
                alias_matches.append((len(alias), brand))

    matched_brands = {brand for _, brand in alias_matches}
    if len(matched_brands) != 1:
        return None
    return max(alias_matches, key=lambda item: item[0])[1]


def _brand_aliases(brand: str) -> set[str]:
    aliases = {brand.replace("-", " "), brand.replace(" ", "-")}
    for token in re.split(r"[\s\-]+", brand):
        token = token.strip()
        if len(token) >= 3 and token.casefold() not in VEHICLE_TYPE_WORDS:
            aliases.add(token)
    return aliases


def _extract_event(text: str) -> str | None:
    normalized_text = text.casefold()
    compact_text = re.sub(r"\s+", " ", normalized_text)
    mentioned_events = _mentioned_events(compact_text)
    if len(mentioned_events) > 1:
        return None

    pass_terms = (
        "event pass",
        "pass event",
        "pass only",
        "just pass",
        "only passing",
        "entered and exited",
        "entry and exit",
        "\u0e17\u0e32\u0e07\u0e25\u0e31\u0e14",
        "\u0e40\u0e02\u0e49\u0e32\u0e41\u0e25\u0e49\u0e27\u0e2d\u0e2d\u0e01\u0e40\u0e25\u0e22",
        "\u0e41\u0e04\u0e48\u0e02\u0e31\u0e1a\u0e1c\u0e48\u0e32\u0e19",
        "\u0e1c\u0e48\u0e32\u0e19\u0e40\u0e09\u0e22",
    )
    if any(term in compact_text for term in pass_terms):
        return "pass"

    entry_terms = (
        "event entry",
        "entry event",
        "entered area",
        "entering area",
        "\u0e23\u0e16\u0e40\u0e02\u0e49\u0e32",
        "\u0e17\u0e32\u0e07\u0e40\u0e02\u0e49\u0e32",
        "\u0e02\u0e32\u0e40\u0e02\u0e49\u0e32",
        "\u0e40\u0e02\u0e49\u0e32\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48",
    )
    if any(term in compact_text for term in entry_terms):
        return "entry"

    exit_terms = (
        "event exit",
        "event exits",
        "exit event",
        "exits event",
        "exited area",
        "leaving area",
        "\u0e23\u0e16\u0e2d\u0e2d\u0e01",
        "\u0e17\u0e32\u0e07\u0e2d\u0e2d\u0e01",
        "\u0e02\u0e32\u0e2d\u0e2d\u0e01",
        "\u0e2d\u0e2d\u0e01\u0e08\u0e32\u0e01\u0e1e\u0e37\u0e49\u0e19\u0e17\u0e35\u0e48",
    )
    if any(term in compact_text for term in exit_terms):
        return "exit"

    explicit_event = re.search(r"\bevent\s+([a-z_\-]+)\b", compact_text)
    if explicit_event:
        return normalize_event(explicit_event.group(1))
    if len(mentioned_events) == 1:
        return next(iter(mentioned_events))
    return None


def _mentioned_events(compact_text: str) -> set[str]:
    events: set[str] = set()
    thai_entry_terms = (
        "\u0e23\u0e16\u0e40\u0e02\u0e49\u0e32",
        "\u0e40\u0e02\u0e49\u0e32\u0e21\u0e32",
        "\u0e02\u0e32\u0e40\u0e02\u0e49\u0e32",
        "\u0e17\u0e32\u0e07\u0e40\u0e02\u0e49\u0e32",
    )
    thai_exit_terms = (
        "\u0e23\u0e16\u0e2d\u0e2d\u0e01",
        "\u0e2d\u0e2d\u0e01\u0e44\u0e1b",
        "\u0e02\u0e32\u0e2d\u0e2d\u0e01",
        "\u0e17\u0e32\u0e07\u0e2d\u0e2d\u0e01",
    )
    if any(_contains_term(compact_text, term) for term in ("entry", "enter", "entered", "entering")) or any(
        term in compact_text for term in thai_entry_terms
    ):
        events.add("entry")
    if any(_contains_term(compact_text, term) for term in ("exit", "exits", "exited", "exiting", "out", "leave", "leaving")) or any(
        term in compact_text for term in thai_exit_terms
    ):
        events.add("exit")
    if any(_contains_term(compact_text, term) for term in ("pass", "passed", "passing")):
        events.add("pass")
    return events


def _extract_event_scope(text: str) -> tuple[str, ...]:
    compact_text = re.sub(r"\s+", " ", text.casefold())
    events = _mentioned_events(compact_text)
    if _has_thai_entry_exit_phrase(compact_text) or {"entry", "exit"} <= events:
        return ("entry", "exit")
    if len(events) == 1:
        return (next(iter(events)),)
    return ()


def _contains_term(normalized_text: str, normalized_term: str) -> bool:
    return bool(_term_spans(normalized_text, normalized_term))


def _term_spans(normalized_text: str, normalized_term: str) -> list[tuple[int, int]]:
    if re.fullmatch(r"[a-z0-9][a-z0-9\-\s]*", normalized_term):
        return [
            (match.start(), match.end())
            for match in re.finditer(rf"(?<![a-z0-9]){re.escape(normalized_term)}(?![a-z0-9])", normalized_text)
        ]
    return [(match.start(), match.end()) for match in re.finditer(re.escape(normalized_term), normalized_text)]


def _wants_brand_color_breakdown(text: str) -> bool:
    normalized_text = text.casefold()
    return (
        "ยี่ห้อ" in normalized_text
        or "brand" in normalized_text
        or bool(re.search(r"สี.*อะไร|อะไร.*สี", normalized_text))
        or "color?" in normalized_text
        or "colour?" in normalized_text
    )


def _wants_origin_breakdown(text: str) -> bool:
    compact_text = re.sub(r"\s+", " ", text.casefold())
    origin_terms = (
        "country",
        "countries",
        "origin",
        "region",
        "nationality",
        "\u0e1b\u0e23\u0e30\u0e40\u0e17\u0e28",
        "\u0e2a\u0e31\u0e0d\u0e0a\u0e32\u0e15\u0e34",
        "\u0e41\u0e2b\u0e25\u0e48\u0e07\u0e01\u0e33\u0e40\u0e19\u0e34\u0e14",
    )
    breakdown_terms = (
        "by country",
        "by origin",
        "by region",
        "per country",
        "per origin",
        "breakdown",
        "\u0e41\u0e22\u0e01",
        "\u0e41\u0e22\u0e01\u0e15\u0e32\u0e21",
        "\u0e41\u0e15\u0e48\u0e25\u0e30",
    )
    if any(term in compact_text for term in origin_terms) and any(term in compact_text for term in breakdown_terms):
        return True
    return bool(_extract_brand_origins(text)) and any(term in compact_text for term in breakdown_terms)


def _wants_route(text: str) -> bool:
    normalized_text = text.casefold()
    return any(
        term in normalized_text
        for term in (
            "route",
            "path",
            "direction",
            "travel",
            "เส้นทาง",
            "เดินทาง",
            "ไปทางไหน",
            "ผ่านกล้องไหน",
            "ผ่านทางไหน",
        )
    )


def _wants_vehicle_list(text: str) -> bool:
    normalized_text = text.casefold()
    return any(
        term in normalized_text
        for term in (
            "คันไหน",
            "คันใด",
            "รถอะไรบ้าง",
            "มีรถอะไร",
            "รายการรถ",
            "รายชื่อรถ",
            "which vehicles",
            "which cars",
            "list vehicles",
            "list cars",
            "show vehicles",
            "show cars",
        )
    )


def _wants_distinct_vehicle_count(text: str) -> bool:
    normalized_text = text.casefold()
    return any(
        term in normalized_text
        for term in (
            "\u0e44\u0e21\u0e48\u0e0b\u0e49\u0e33",
            "\u0e44\u0e21\u0e48\u0e0b\u0e49\u0e33\u0e01\u0e31\u0e19",
            "\u0e44\u0e21\u0e48\u0e19\u0e31\u0e1a\u0e0b\u0e49\u0e33",
            "\u0e44\u0e21\u0e48\u0e19\u0e31\u0e1a\u0e0b\u0e49\u0e33\u0e01\u0e31\u0e19",
            "distinct vehicles",
            "distinct cars",
            "unique vehicles",
            "unique cars",
            "dedupe",
            "deduplicated",
        )
    )


def _wants_peak_hour(text: str) -> bool:
    compact_text = re.sub(r"\s+", " ", text.casefold())
    return _has_hour_term(compact_text) and _has_peak_term(compact_text)


def _wants_peak_camera(text: str) -> bool:
    compact_text = re.sub(r"\s+", " ", text.casefold())
    return _has_camera_question_term(compact_text) and _has_peak_term(compact_text)


def _wants_hour_breakdown(text: str) -> bool:
    compact_text = re.sub(r"\s+", " ", text.casefold())
    return _has_hour_term(compact_text) and any(
        term in compact_text
        for term in (
            "by hour",
            "per hour",
            "hourly",
            "\u0e41\u0e22\u0e01\u0e15\u0e32\u0e21\u0e0a\u0e31\u0e48\u0e27\u0e42\u0e21\u0e07",
            "\u0e41\u0e15\u0e48\u0e25\u0e30\u0e0a\u0e31\u0e48\u0e27\u0e42\u0e21\u0e07",
        )
    )


def _wants_camera_breakdown(text: str) -> bool:
    compact_text = re.sub(r"\s+", " ", text.casefold())
    return any(
        term in compact_text
        for term in (
            "by camera",
            "per camera",
            "by cctv",
            "per cctv",
            "\u0e41\u0e22\u0e01\u0e15\u0e32\u0e21\u0e01\u0e25\u0e49\u0e2d\u0e07",
            "\u0e41\u0e15\u0e48\u0e25\u0e30\u0e01\u0e25\u0e49\u0e2d\u0e07",
        )
    )


def _has_hour_term(compact_text: str) -> bool:
    return any(
        term in compact_text
        for term in (
            "hour",
            "hourly",
            "time slot",
            "time period",
            "\u0e0a\u0e31\u0e48\u0e27\u0e42\u0e21\u0e07",
            "\u0e0a\u0e48\u0e27\u0e07\u0e40\u0e27\u0e25\u0e32",
            "\u0e40\u0e27\u0e25\u0e32\u0e44\u0e2b\u0e19",
        )
    )


def _has_camera_question_term(compact_text: str) -> bool:
    return any(
        term in compact_text
        for term in (
            "which camera",
            "which cctv",
            "camera has",
            "cctv has",
            "\u0e01\u0e25\u0e49\u0e2d\u0e07\u0e44\u0e2b\u0e19",
            "\u0e01\u0e25\u0e49\u0e2d\u0e07\u0e15\u0e31\u0e27\u0e44\u0e2b\u0e19",
        )
    )


def _has_peak_term(compact_text: str) -> bool:
    return any(
        term in compact_text
        for term in (
            "most",
            "highest",
            "busiest",
            "maximum",
            "max",
            "\u0e21\u0e32\u0e01\u0e17\u0e35\u0e48\u0e2a\u0e38\u0e14",
            "\u0e40\u0e22\u0e2d\u0e30\u0e17\u0e35\u0e48\u0e2a\u0e38\u0e14",
            "\u0e2a\u0e39\u0e07\u0e2a\u0e38\u0e14",
        )
    )


def _has_thai_entry_exit_phrase(compact_text: str) -> bool:
    return any(
        term in compact_text
        for term in (
            "\u0e40\u0e02\u0e49\u0e32\u0e2d\u0e2d\u0e01",
            "\u0e40\u0e02\u0e49\u0e32-\u0e2d\u0e2d\u0e01",
            "\u0e02\u0e32\u0e40\u0e02\u0e49\u0e32\u0e02\u0e32\u0e2d\u0e2d\u0e01",
            "\u0e23\u0e16\u0e40\u0e02\u0e49\u0e32\u0e23\u0e16\u0e2d\u0e2d\u0e01",
        )
    )


def _wants_event_breakdown(text: str) -> bool:
    normalized_text = text.casefold()
    compact_text = re.sub(r"\s+", " ", normalized_text)
    if _wants_unclosed_entry_count(text):
        return False
    explicit_breakdown_terms = (
        "by event",
        "by events",
        "per event",
        "event breakdown",
        "event counts",
        "count by event",
        "status breakdown",
        "by status",
        "แยกตาม event",
        "แยกตามสถานะ",
        "ตาม event",
        "ตามสถานะ",
        "สถานะรถ",
    )
    if any(term in compact_text for term in explicit_breakdown_terms):
        return True
    mentioned_events = _mentioned_events(compact_text)
    return len(mentioned_events) > 1 and _looks_like_count_question(compact_text)


def _wants_unclosed_entry_count(text: str) -> bool:
    normalized_text = text.casefold()
    compact_text = re.sub(r"\s+", " ", normalized_text)
    english_patterns = (
        r"\bentry\b.*\b(?:no|not|without|missing|never)\s+exit\b",
        r"\benter(?:ed|ing)?\b.*\b(?:no|not|without|missing|never)\s+exit\b",
        r"\b(?:no|not|without|missing|never)\s+exit\b.*\bentry\b",
        r"\bentered\b.*\b(?:did not|didn't|does not|doesn't)\s+(?:exit|leave)\b",
    )
    if any(re.search(pattern, compact_text) for pattern in english_patterns):
        return True
    has_entry_word = any(term in compact_text for term in ("entry", "enter", "entered", "entering"))
    has_negative_exit = any(
        term in compact_text
        for term in (
            "not exit",
            "no exit",
            "without exit",
            "missing exit",
            "not exited",
            "no exited",
            "ไม่ exit",
            "ไม่ออก",
            "ยังไม่ออก",
            "ไม่ได้ออก",
            "ไม่มี exit",
        )
    )
    thai_entry_terms = ("เข้ามา", "รถเข้า", "เข้าแล้ว", "เข้าพื้นที่", "ทางเข้า", "ขาเข้า")
    has_thai_entry = any(term in compact_text for term in thai_entry_terms)
    return (has_entry_word or has_thai_entry) and has_negative_exit


def _looks_like_count_question(compact_text: str) -> bool:
    return any(
        term in compact_text
        for term in (
            "how many",
            "count",
            "counts",
            "number",
            "จำนวน",
            "กี่คัน",
            "เท่าไหร่",
            "เท่าไร",
        )
    )
