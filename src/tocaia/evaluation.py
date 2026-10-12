"""Score supplied binary forecasts; this module does not predict behavior."""

from __future__ import annotations

import argparse
import json
import math
from pathlib import Path
from statistics import mean


def _probability(value: object, field: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{field} must be a number between 0 and 1")
    if not math.isfinite(value) or not 0 <= value <= 1:
        raise ValueError(f"{field} must be finite and between 0 and 1")
    return float(value)


def evaluate(records: object) -> dict[str, object]:
    """Brier scores on resolved cases, with unresolved cases reported explicitly.

    No provenance, temporal leakage or calibration audit is performed here.
    A null outcome means unresolved, never a negative event.
    """
    if not isinstance(records, list) or not records:
        raise ValueError("input must be a non-empty JSON list")
    seen: set[str] = set()
    errors: list[float] = []
    baseline_errors: list[float] = []
    positives = 0
    for row in records:
        if not isinstance(row, dict):
            raise ValueError("each forecast must be an object")
        required = {"forecast_id", "probability", "baseline_probability", "outcome"}
        if not required <= row.keys():
            raise ValueError("missing required forecast fields")
        forecast_id = row["forecast_id"]
        if not isinstance(forecast_id, str) or not forecast_id.strip():
            raise ValueError("forecast_id must be a non-empty string")
        if forecast_id in seen:
            raise ValueError(f"duplicate forecast_id: {forecast_id}")
        seen.add(forecast_id)
        p = _probability(row["probability"], "probability")
        baseline = _probability(row["baseline_probability"], "baseline_probability")
        outcome = row["outcome"]
        if outcome is None:
            continue
        if type(outcome) is not int or outcome not in (0, 1):
            raise ValueError("outcome must be integer 0, integer 1 or null")
        positives += outcome
        errors.append((p - outcome) ** 2)
        baseline_errors.append((baseline - outcome) ** 2)
    count = len(errors)
    score = mean(errors) if count else None
    baseline_score = mean(baseline_errors) if count else None
    skill = 1 - score / baseline_score if baseline_score else None
    return {
        "total": len(records),
        "resolved": count,
        "unresolved": len(records) - count,
        "unresolved_rate": (len(records) - count) / len(records),
        "positive_outcomes": positives,
        "brier": score,
        "baseline_brier": baseline_score,
        "brier_skill": skill,
        "scope": "supplied forecasts only; not a validation of predictive ability",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("json_file", type=Path)
    args = parser.parse_args()
    try:
        records = json.loads(args.json_file.read_text(encoding="utf-8"))
        result = evaluate(records)
    except (OSError, ValueError) as exc:
        parser.error(str(exc))
    print(json.dumps(result, ensure_ascii=False, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
