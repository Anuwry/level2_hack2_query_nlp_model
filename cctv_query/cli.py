from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path

from cctv_query.engine import CCTVQueryEngine


DEFAULT_CSV = Path(__file__).resolve().parents[1] / "cctv_vehicle_log_routed.csv"


def main(argv: list[str] | None = None) -> int:
    _ensure_utf8_stdout()
    parser = argparse.ArgumentParser(description="Query CCTV vehicle logs from a CSV file.")
    parser.add_argument(
        "--csv",
        default=str(DEFAULT_CSV),
        help="Path to CCTV CSV log. Defaults to cctv_vehicle_log_routed.csv in this project.",
    )
    parser.add_argument("--question", "-q", help="Thai or English question to ask.")
    parser.add_argument("--json", action="store_true", help="Print structured JSON output.")
    args = parser.parse_args(argv)

    engine = CCTVQueryEngine.from_csv(args.csv)
    if args.question:
        _print_result(engine.ask(args.question), as_json=args.json)
        return 0

    print("Enter a Thai or English CCTV question. Press Enter on a blank line to exit.")
    while True:
        question = input("> ").strip()
        if not question:
            return 0
        _print_result(engine.ask(question), as_json=args.json)


def _print_result(result, as_json: bool) -> None:
    if as_json:
        print(json.dumps(result.to_dict(), ensure_ascii=False, indent=2))
    else:
        print(result.answer)


def _ensure_utf8_stdout() -> None:
    if hasattr(sys.stdout, "reconfigure"):
        sys.stdout.reconfigure(encoding="utf-8")
