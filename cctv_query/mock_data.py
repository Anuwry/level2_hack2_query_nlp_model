from __future__ import annotations

import argparse
import csv
import random
from collections.abc import Sequence
from datetime import date, timedelta
from pathlib import Path
from typing import TypeVar


FIELDNAMES = ("Date", "CCTV_ID", "Timestamp", "Brand", "Color", "Type", "Event")
EVENTS = {"entry", "exit", "pass"}
UNIQUE_VEHICLE_GAP_SECONDS = 30 * 60
T = TypeVar("T")

CORRIDORS = (
    ("CCTV10", "CCTV09", "CCTV08", "CCTV07", "CCTV04"),
    ("CCTV04", "CCTV07", "CCTV08", "CCTV09", "CCTV10"),
    ("CCTV01", "CCTV03", "CCTV04", "CCTV07"),
    ("CCTV07", "CCTV04", "CCTV03", "CCTV01"),
    ("CCTV02", "CCTV05", "CCTV06", "CCTV08", "CCTV09"),
    ("CCTV09", "CCTV08", "CCTV06", "CCTV05", "CCTV02"),
    ("CCTV03", "CCTV06", "CCTV10"),
    ("CCTV10", "CCTV06", "CCTV03"),
    ("CCTV05", "CCTV06", "CCTV07"),
    ("CCTV07", "CCTV06", "CCTV05"),
)

TYPE_WEIGHTS = (
    ("Car", 64),
    ("Motorcycle", 18),
    ("Truck", 13),
    ("Bus", 5),
)

BRANDS_BY_TYPE = {
    "Car": (
        ("Toyota", 22),
        ("Honda", 16),
        ("Mazda", 9),
        ("Nissan", 8),
        ("Mitsubishi", 8),
        ("BYD", 6),
        ("MG", 5),
        ("Mercedes-Benz", 4),
        ("BMW", 3),
        ("Tesla", 2),
        ("Haval", 2),
        ("Neta", 2),
        ("Ford", 2),
    ),
    "Motorcycle": (
        ("Honda", 30),
        ("Yamaha", 26),
        ("Kawasaki", 9),
        ("Suzuki", 8),
    ),
    "Truck": (
        ("Isuzu", 24),
        ("Hino", 20),
        ("Mitsubishi", 10),
        ("Ford", 7),
        ("Chevrolet", 4),
    ),
    "Bus": (
        ("Hino", 20),
        ("Mercedes-Benz", 10),
        ("Toyota", 5),
        ("Isuzu", 4),
    ),
}

COLOR_WEIGHTS = (
    ("White", 24),
    ("Black", 20),
    ("Gray", 16),
    ("Silver", 13),
    ("Red", 8),
    ("Blue", 6),
    ("Bronze", 4),
    ("Gold", 3),
    ("Green", 2),
    ("Dark Green", 1),
    ("Red-White", 1),
    ("Blue-White", 1),
    ("Yellow", 1),
)


def generate_rows(
    total_rows: int = 10_000,
    *,
    seed: int = 20260521,
    start_date: date = date(2026, 5, 10),
    days: int = 5,
) -> list[dict[str, str]]:
    if total_rows < 2:
        raise ValueError("total_rows must be at least 2 because routes need entry and exit detections.")
    if days <= 0:
        raise ValueError("days must be greater than zero.")

    rng = random.Random(seed)
    route_templates = _route_templates()
    next_available_by_signature: dict[tuple[str, str, str, str], int] = {}
    rows: list[dict[str, str]] = []

    while len(rows) < total_rows:
        remaining = total_rows - len(rows)
        route = _weighted_choice(_eligible_route_templates(route_templates, remaining), rng)
        offsets = _route_offsets(route, rng)
        current_date, vehicle_type, brand, color, start_seconds = _scheduled_vehicle(
            rng,
            start_date,
            days,
            len(route),
            offsets[-1],
            next_available_by_signature,
        )
        date_text = current_date.strftime("%d-%m-%Y")
        signature = (date_text, brand.casefold(), color.casefold(), vehicle_type.casefold())

        for route_index, (cctv_id, offset) in enumerate(zip(route, offsets)):
            rows.append(
                {
                    "Date": date_text,
                    "CCTV_ID": cctv_id,
                    "Timestamp": _format_seconds(start_seconds + offset),
                    "Brand": brand,
                    "Color": color,
                    "Type": vehicle_type,
                    "Event": _event_for_route_position(route_index, len(route)),
                }
            )
        next_available_by_signature[signature] = start_seconds + offsets[-1] + UNIQUE_VEHICLE_GAP_SECONDS + 1

    return sorted(rows, key=lambda row: (row["Date"], row["Timestamp"], row["CCTV_ID"], row["Brand"], row["Color"], row["Type"]))


def write_csv(rows: Sequence[dict[str, str]], path: str | Path) -> None:
    csv_path = Path(path)
    with csv_path.open("w", newline="", encoding="utf-8") as csv_file:
        writer = csv.DictWriter(csv_file, fieldnames=FIELDNAMES, lineterminator="\n")
        writer.writeheader()
        writer.writerows(rows)


def _route_templates() -> tuple[tuple[tuple[str, ...], int], ...]:
    templates: list[tuple[tuple[str, ...], int]] = []
    for corridor in CORRIDORS:
        for start in range(len(corridor)):
            for end in range(start + 2, len(corridor) + 1):
                route = corridor[start:end]
                weight = 8 if len(route) == len(corridor) else 4
                templates.append((route, weight))
    return tuple(templates)


def _eligible_route_templates(
    route_templates: tuple[tuple[tuple[str, ...], int], ...],
    remaining_rows: int,
) -> list[tuple[tuple[str, ...], int]]:
    return [
        item
        for item in route_templates
        if len(item[0]) <= remaining_rows and remaining_rows - len(item[0]) != 1
    ]


def _event_for_route_position(index: int, route_length: int) -> str:
    if index == 0:
        return "entry"
    if index == route_length - 1:
        return "exit"
    return "pass"


def _scheduled_vehicle(
    rng: random.Random,
    start_date: date,
    days: int,
    route_length: int,
    route_duration: int,
    next_available_by_signature: dict[tuple[str, str, str, str], int],
) -> tuple[date, str, str, str, int]:
    latest_start = 23 * 3600 + 59 * 60 + 59 - route_duration
    for _ in range(500):
        current_date = start_date + timedelta(days=rng.randrange(days))
        vehicle_type = _weighted_choice(TYPE_WEIGHTS, rng)
        brand = _weighted_choice(BRANDS_BY_TYPE[vehicle_type], rng)
        color = _weighted_choice(COLOR_WEIGHTS, rng)
        date_text = current_date.strftime("%d-%m-%Y")
        signature = (date_text, brand.casefold(), color.casefold(), vehicle_type.casefold())
        proposed_start = max(
            _random_start_seconds(rng, route_length),
            next_available_by_signature.get(signature, 0),
        )
        if proposed_start <= latest_start:
            return current_date, vehicle_type, brand, color, proposed_start
    raise RuntimeError("Could not schedule enough realistic non-overlapping routes. Increase days or reduce rows.")


def _route_offsets(route: tuple[str, ...], rng: random.Random) -> list[int]:
    offsets = [0]
    elapsed = 0
    for _ in route[1:]:
        elapsed += rng.randint(45, 210)
        offsets.append(elapsed)
    return offsets


def _random_start_seconds(rng: random.Random, route_length: int) -> int:
    period = _weighted_choice(
        (
            ((6 * 3600, 9 * 3600), 34),
            ((9 * 3600, 16 * 3600), 22),
            ((16 * 3600, 20 * 3600), 34),
            ((20 * 3600, 23 * 3600), 8),
            ((0, 6 * 3600), 2),
        ),
        rng,
    )
    latest_start = max(period[0], period[1] - route_length * 240)
    return rng.randint(period[0], latest_start)


def _weighted_choice(items: Sequence[tuple[T, int]], rng: random.Random) -> T:
    total = sum(weight for _, weight in items)
    pick = rng.randint(1, total)
    running = 0
    for value, weight in items:
        running += weight
        if pick <= running:
            return value
    return items[-1][0]


def _format_seconds(total_seconds: int) -> str:
    total_seconds = min(total_seconds, 23 * 3600 + 59 * 60 + 59)
    hour = total_seconds // 3600
    minute = (total_seconds % 3600) // 60
    second = total_seconds % 60
    return f"{hour:02d}:{minute:02d}:{second:02d}"


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description="Generate realistic routed CCTV CSV mock data.")
    parser.add_argument("--rows", type=int, default=10_000)
    parser.add_argument("--output", default="cctv_vehicle_log_routed.csv")
    parser.add_argument("--seed", type=int, default=20260521)
    parser.add_argument("--days", type=int, default=5)
    args = parser.parse_args(argv)

    rows = generate_rows(args.rows, seed=args.seed, days=args.days)
    write_csv(rows, args.output)
    print(f"Wrote {len(rows)} rows to {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
