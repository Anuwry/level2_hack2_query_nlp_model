from __future__ import annotations

import csv
import io
import re
from collections import OrderedDict
from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class SqlTable:
    name: str
    columns: tuple[str, ...]
    rows: tuple[dict[str, str], ...]

    @property
    def row_count(self) -> int:
        return len(self.rows)

    def to_csv(self) -> str:
        output = io.StringIO()
        writer = csv.DictWriter(output, fieldnames=list(self.columns), lineterminator="\n")
        writer.writeheader()
        writer.writerows(self.rows)
        return output.getvalue()

    def to_dict(self) -> dict[str, Any]:
        return {
            "name": self.name,
            "columns": list(self.columns),
            "rows": [dict(row) for row in self.rows],
            "row_count": self.row_count,
            "csv": self.to_csv(),
        }


def convert_sql_to_tables(sql_text: str) -> list[SqlTable]:
    statements = _split_sql_statements(_strip_sql_line_comments(sql_text))
    tables: OrderedDict[str, SqlTable] = OrderedDict()

    for statement in statements:
        create_table = _parse_create_table(statement)
        if create_table:
            name, columns = create_table
            _ensure_table(tables, name, columns)
            continue

        insert = _parse_insert(statement)
        if not insert:
            continue

        name, insert_columns, value_rows = insert
        existing_columns = tables[name].columns if name in tables else ()
        columns = insert_columns or existing_columns or tuple(f"column_{index + 1}" for index in range(len(value_rows[0])))
        table = _ensure_table(tables, name, columns)
        rows = list(table.rows)
        for values in value_rows:
            rows.append(_row_from_values(table.columns, values, insert_columns or table.columns))
        tables[name] = SqlTable(table.name, table.columns, tuple(rows))

    _append_required_output_view(tables)
    return [table for table in tables.values() if table.rows]


def convert_sql_to_response(sql_text: str) -> dict[str, Any]:
    tables = convert_sql_to_tables(sql_text)
    if not tables:
        raise ValueError("No INSERT rows found in SQL text.")

    selected_table = "required_output_view" if any(table.name == "required_output_view" for table in tables) else tables[0].name
    return {
        "tables": [table.to_dict() for table in tables],
        "selected_table": selected_table,
    }


def _ensure_table(tables: OrderedDict[str, SqlTable], name: str, columns: tuple[str, ...]) -> SqlTable:
    if name not in tables:
        tables[name] = SqlTable(name=name, columns=columns, rows=())
    return tables[name]


def _row_from_values(
    columns: tuple[str, ...],
    values: tuple[str, ...],
    value_columns: tuple[str, ...],
) -> dict[str, str]:
    row = {column: "" for column in columns}
    for column, value in zip(value_columns, values):
        row[column] = value
    return row


def _parse_create_table(statement: str) -> tuple[str, tuple[str, ...]] | None:
    match = re.match(
        r"CREATE\s+TABLE\s+(?:IF\s+NOT\s+EXISTS\s+)?(?P<table>[`\"\[]?[\w.]+[`\"\]]?)\s*\((?P<body>.*)\)\s*$",
        statement,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None

    columns: list[str] = []
    for part in _split_top_level_commas(match.group("body")):
        token = part.strip().split(None, maxsplit=1)[0] if part.strip() else ""
        normalized = token.strip("`\"[]")
        if not normalized:
            continue
        if normalized.casefold() in {"primary", "foreign", "unique", "check", "constraint"}:
            continue
        columns.append(normalized)
    return _clean_identifier(match.group("table")), tuple(columns)


def _parse_insert(statement: str) -> tuple[str, tuple[str, ...], tuple[tuple[str, ...], ...]] | None:
    match = re.match(
        r"INSERT\s+INTO\s+(?P<table>[`\"\[]?[\w.]+[`\"\]]?)\s*(?:\((?P<columns>.*?)\))?\s*VALUES\s*(?P<values>.*)$",
        statement,
        flags=re.IGNORECASE | re.DOTALL,
    )
    if not match:
        return None

    columns = tuple(_clean_identifier(value) for value in _split_top_level_commas(match.group("columns") or ""))
    value_rows = tuple(_parse_value_row(row) for row in _extract_parenthesized_rows(match.group("values")))
    if not value_rows:
        return None
    return _clean_identifier(match.group("table")), columns, value_rows


def _append_required_output_view(tables: OrderedDict[str, SqlTable]) -> None:
    source = tables.get("vehicle_tracks")
    if not source:
        return

    rows: list[dict[str, str]] = []
    for row in source.rows:
        first_seen = row.get("first_seen_iso") or row.get("first_seen_ts") or ""
        last_seen = row.get("last_seen_iso") or row.get("last_seen_ts") or first_seen
        rows.append(
            {
                "Date": first_seen[:10],
                "CCTV_ID": row.get("camera_id", ""),
                "First_Seen": first_seen,
                "Last_Seen": last_seen,
                "Brand": row.get("brand") or "Unknown",
                "Color": row.get("color") or "Unknown",
                "Type": row.get("vehicle_type") or "Unknown",
                "Event": row.get("event") or "pass",
            }
        )
    tables["required_output_view"] = SqlTable(
        name="required_output_view",
        columns=("Date", "CCTV_ID", "First_Seen", "Last_Seen", "Brand", "Color", "Type", "Event"),
        rows=tuple(rows),
    )


def _strip_sql_line_comments(sql_text: str) -> str:
    cleaned_lines: list[str] = []
    for line in sql_text.splitlines():
        cleaned_lines.append(_strip_sql_line_comment(line))
    return "\n".join(cleaned_lines)


def _strip_sql_line_comment(line: str) -> str:
    in_quote = False
    index = 0
    while index < len(line):
        char = line[index]
        if char == "'":
            if in_quote and index + 1 < len(line) and line[index + 1] == "'":
                index += 2
                continue
            in_quote = not in_quote
        if not in_quote and line[index : index + 2] == "--":
            return line[:index]
        index += 1
    return line


def _split_sql_statements(sql_text: str) -> list[str]:
    statements: list[str] = []
    start = 0
    in_quote = False
    index = 0
    while index < len(sql_text):
        char = sql_text[index]
        if char == "'":
            if in_quote and index + 1 < len(sql_text) and sql_text[index + 1] == "'":
                index += 2
                continue
            in_quote = not in_quote
        elif char == ";" and not in_quote:
            statement = sql_text[start:index].strip()
            if statement:
                statements.append(statement)
            start = index + 1
        index += 1

    tail = sql_text[start:].strip()
    if tail:
        statements.append(tail)
    return statements


def _split_top_level_commas(text: str) -> list[str]:
    if not text:
        return []

    parts: list[str] = []
    start = 0
    depth = 0
    in_quote = False
    index = 0
    while index < len(text):
        char = text[index]
        if char == "'":
            if in_quote and index + 1 < len(text) and text[index + 1] == "'":
                index += 2
                continue
            in_quote = not in_quote
        elif not in_quote:
            if char == "(":
                depth += 1
            elif char == ")":
                depth = max(0, depth - 1)
            elif char == "," and depth == 0:
                parts.append(text[start:index].strip())
                start = index + 1
        index += 1
    parts.append(text[start:].strip())
    return parts


def _extract_parenthesized_rows(values_text: str) -> list[str]:
    rows: list[str] = []
    depth = 0
    start: int | None = None
    in_quote = False
    index = 0
    while index < len(values_text):
        char = values_text[index]
        if char == "'":
            if in_quote and index + 1 < len(values_text) and values_text[index + 1] == "'":
                index += 2
                continue
            in_quote = not in_quote
        elif not in_quote:
            if char == "(":
                if depth == 0:
                    start = index + 1
                depth += 1
            elif char == ")":
                depth -= 1
                if depth == 0 and start is not None:
                    rows.append(values_text[start:index].strip())
                    start = None
        index += 1
    return rows


def _parse_value_row(row_text: str) -> tuple[str, ...]:
    return tuple(_clean_sql_value(value) for value in _split_top_level_commas(row_text))


def _clean_sql_value(value: str) -> str:
    stripped = value.strip()
    if stripped.casefold() == "null":
        return ""
    if len(stripped) >= 2 and stripped[0] == "'" and stripped[-1] == "'":
        return stripped[1:-1].replace("''", "'")
    return stripped


def _clean_identifier(value: str) -> str:
    return value.strip().strip("`\"[]")
