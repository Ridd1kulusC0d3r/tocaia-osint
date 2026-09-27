"""CLI for the small public T.O.C.A.I.A reference implementation."""

from __future__ import annotations

import argparse
import csv
import json
from pathlib import Path

from .absence import classify_window


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="tocaia-analyze",
        description="Classify observation windows as data_gap, behavioral_gap or no_gap.",
    )
    parser.add_argument("csv_file", type=Path, help="CSV with window,expected,observed,coverage columns")
    parser.add_argument(
        "--min-coverage",
        type=float,
        default=0.95,
        help="minimum coverage required before a zero can be treated as observed absence (default: 0.95)",
    )
    parser.add_argument("--jsonl", action="store_true", help="emit JSON Lines instead of a compact table")
    return parser


def analyze(path: Path, min_coverage: float) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    with path.open("r", encoding="utf-8", newline="") as handle:
        reader = csv.DictReader(handle)
        required = {"window", "expected", "observed", "coverage"}
        if set(reader.fieldnames or ()) != required:
            raise ValueError(f"CSV header must be exactly: {','.join(sorted(required))}")
        for row in reader:
            record = classify_window(
                window=row["window"],
                expected=float(row["expected"]),
                observed=int(row["observed"]),
                coverage=float(row["coverage"]),
                min_coverage=min_coverage,
            )
            rows.append(record.to_dict())
    return rows


def main() -> None:
    args = build_parser().parse_args()
    records = analyze(args.csv_file, args.min_coverage)
    if args.jsonl:
        for record in records:
            print(json.dumps(record, ensure_ascii=False, sort_keys=True))
        return

    for record in records:
        print(
            f"{record['window']:<4}  {record['kind']:<15}  "
            f"coverage={record['coverage']:.2f}  expected={record['expected']:g}  observed={record['observed']}"
        )


if __name__ == "__main__":
    main()
