from __future__ import annotations

import csv
from pathlib import Path

from cctv_query.models import CCTVRecord


REQUIRED_COLUMNS = ("Date", "CCTV_ID", "Timestamp", "Brand", "Color", "Type")


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
                records.append(
                    CCTVRecord.from_values(
                        row["Date"],
                        row["CCTV_ID"],
                        row["Timestamp"],
                        row["Brand"],
                        row["Color"],
                        row["Type"],
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
