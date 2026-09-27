"""Minimal absence-analysis primitives for the public T.O.C.A.I.A reference implementation.

The key analytical control is deliberately boring: do not interpret a zero until
collection coverage is good enough to support the statement that the event would
likely have been observed.
"""

from __future__ import annotations

from dataclasses import asdict, dataclass
from enum import StrEnum


class GapKind(StrEnum):
    """Classification of a time window."""

    NO_GAP = "no_gap"
    DATA_GAP = "data_gap"
    BEHAVIORAL_GAP = "behavioral_gap"


@dataclass(frozen=True, slots=True)
class GapRecord:
    """Auditable result for one observation window."""

    window: str
    expected: float
    observed: int
    coverage: float
    kind: GapKind
    delta: float
    reason: str

    def to_dict(self) -> dict[str, object]:
        data = asdict(self)
        data["kind"] = self.kind.value
        return data


def classify_window(
    *,
    window: str,
    expected: float,
    observed: int,
    coverage: float,
    min_coverage: float = 0.95,
) -> GapRecord:
    """Classify one window as data gap, behavioral gap or no gap.

    This function does not infer intent, identity, cause or psychology. It only
    enforces the distinction between insufficient observation and an observed
    absence relative to a declared expectation.
    """

    if not window.strip():
        raise ValueError("window must be non-empty")
    if expected < 0:
        raise ValueError("expected must be >= 0")
    if observed < 0:
        raise ValueError("observed must be >= 0")
    if not 0 <= coverage <= 1:
        raise ValueError("coverage must be between 0 and 1")
    if not 0 < min_coverage <= 1:
        raise ValueError("min_coverage must be between 0 and 1")

    delta = expected - observed

    if coverage < min_coverage:
        return GapRecord(
            window=window,
            expected=expected,
            observed=observed,
            coverage=coverage,
            kind=GapKind.DATA_GAP,
            delta=delta,
            reason="collection coverage below declared threshold; activity is unknown",
        )

    if expected > 0 and observed == 0:
        return GapRecord(
            window=window,
            expected=expected,
            observed=observed,
            coverage=coverage,
            kind=GapKind.BEHAVIORAL_GAP,
            delta=delta,
            reason="adequate collection coverage with zero observed against a positive expectation",
        )

    return GapRecord(
        window=window,
        expected=expected,
        observed=observed,
        coverage=coverage,
        kind=GapKind.NO_GAP,
        delta=delta,
        reason="window does not meet the public reference rule for an absence gap",
    )
