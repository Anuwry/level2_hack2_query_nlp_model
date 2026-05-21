from __future__ import annotations

import csv
from pathlib import Path

from cctv_query.models import CCTVRecord


REQUIRED_COLUMNS = ("Date", "CCTV_ID", "Brand", "Color", "Type")
FIRST_SEEN_COLUMNS = ("First_Seen", "FirstSeen", "First_Timestamp", "Timestamp")
LAST_SEEN_COLUMNS = ("Last_Seen", "LastSeen", "Tracking_Lost", "Lost_At", "Last_Timestamp", "Timestamp")


def load_records(path: str | Path) -> list[CCTVRecord]:
    csv_path = Path(path)
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")

    records: list[CCTVRecord] = []
    with csv_path.open("r", newline="", encoding="utf-8-sig") as csv_file:
        reader = csv.DictReader(csv_file)
        _validate_columns(reader.fieldnames or [], csv_path)

        for row_number, row in enumerate(reader, start=2):
            try:
                first_seen = _first_present_value(row, FIRST_SEEN_COLUMNS)
                records.append(
                    CCTVRecord.from_values(
                        row["Date"],
                        row["CCTV_ID"],
                        first_seen,
                        row["Brand"],
                        row["Color"],
                        row["Type"],
                        row.get("Event"),
                        _first_present_value(row, LAST_SEEN_COLUMNS, default=first_seen),
                    )
                )
            except (KeyError, ValueError) as exc:
                raise ValueError(f"Invalid data at {csv_path}:{row_number}: {exc}") from exc

    return records


def _validate_columns(fieldnames: list[str], csv_path: Path) -> None:
    missing = [column for column in REQUIRED_COLUMNS if column not in fieldnames]
    if missing:
        joined = ", ".join(missing)
        raise ValueError(f"CSV file {csv_path} is missing required column(s): {joined}")
    if not any(column in fieldnames for column in FIRST_SEEN_COLUMNS):
        joined = " or ".join(FIRST_SEEN_COLUMNS)
        raise ValueError(f"CSV file {csv_path} is missing required time column: {joined}")


def _first_present_value(row: dict[str, str], columns: tuple[str, ...], *, default: str | None = None) -> str:
    for column in columns:
        value = row.get(column)
        if value:
            return value
    if default is not None:
        return default
    raise KeyError(columns[0])
