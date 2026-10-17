"""Baseline-aware absence detection (v0.2).

v0.1 asked the analyst to *declare* what was expected. v0.2 learns it from the
history of well-covered windows and adds the control the method has always
demanded: **detectability before interpretation**.

Rules, in order, for each window:

1. coverage below threshold            -> data_gap       (we could not see)
2. no outcome could be significantly
   low under the baseline              -> undetectable   (a zero would mean nothing)
3. P(X <= observed) < alpha, observed=0 -> behavioral_gap
4. P(X <= observed) < alpha, observed>0 -> deficit
5. otherwise                           -> no_gap

The baseline is *frozen* while gaps are open, so a long silence cannot
re-define "normal" as silence.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, asdict

from .absence import GapKind


@dataclass(frozen=True, slots=True)
class Window:
    window: str
    observed: int
    coverage: float


@dataclass(frozen=True, slots=True)
class Detection:
    window: str
    observed: int
    coverage: float
    expected: float | None
    p_low: float | None  # P(X <= observed) under the baseline
    kind: GapKind
    silent_run: int  # consecutive covered zero-windows ending here
    reason: str

    def to_dict(self) -> dict[str, object]:
        d = asdict(self)
        d["kind"] = self.kind.value
        return d


def count_cdf(k: int, mu: float, phi: float = 1.0) -> float:
    """P(X <= k) for Poisson (phi=1) or negative binomial with variance = phi * mu."""
    if mu <= 0:
        return 1.0
    if mu > 400:  # normal approximation, avoids underflow
        sd = math.sqrt(mu * max(phi, 1.0))
        return 0.5 * math.erfc(-(k + 0.5 - mu) / (sd * math.sqrt(2)))
    if phi <= 1.0001:
        pmf, total = math.exp(-mu), 0.0
        for i in range(k + 1):
            total += pmf
            pmf *= mu / (i + 1)
        return min(total, 1.0)
    r = mu / (phi - 1.0)
    p = r / (r + mu)
    pmf, total = math.exp(r * math.log(p)), 0.0
    for i in range(k + 1):
        total += pmf
        pmf *= (i + r) / (i + 1) * (1.0 - p)
    return min(total, 1.0)


def _baseline(history: list[tuple[int, float]]) -> tuple[float, float]:
    """Coverage-normalised rate (median) and dispersion (variance/mean, clipped to [1, 10])."""
    rates = [obs / cov for obs, cov in history]
    mu = statistics.median(rates)
    mean = statistics.fmean(rates)
    phi = 1.0
    if mean > 0 and len(rates) > 1:
        phi = min(10.0, max(1.0, statistics.variance(rates) / mean))
    return mu, phi


def detect(
    windows: list[Window],
    *,
    alpha: float = 0.01,
    min_coverage: float = 0.95,
    history: int = 8,
    min_history: int = 4,
) -> list[Detection]:
    if not 0 < alpha < 0.5:
        raise ValueError("alpha must be in (0, 0.5)")
    if not 0 < min_coverage <= 1:
        raise ValueError("min_coverage must be in (0, 1]")
    if min_history < 2 or history < min_history:
        raise ValueError("need 2 <= min_history <= history")

    clean: list[tuple[int, float]] = []  # covered windows not flagged as gaps (frozen baseline)
    out: list[Detection] = []
    run = 0
    for w in windows:
        if w.observed < 0 or not 0 <= w.coverage <= 1:
            raise ValueError(f"invalid window {w.window!r}")

        def make(kind, reason, expected=None, p=None):
            return Detection(w.window, w.observed, w.coverage, expected, p, kind, run, reason)

        if w.coverage < min_coverage:
            run = 0
            out.append(make(GapKind.DATA_GAP, "coverage below threshold; activity unknown"))
            continue
        if len(clean) < min_history:
            run = run + 1 if w.observed == 0 else 0
            out.append(make(GapKind.UNDETECTABLE, f"baseline needs {min_history} clean windows, have {len(clean)}"))
            if w.observed > 0:
                clean.append((w.observed, max(w.coverage, 1e-9)))
            continue

        mu, phi = _baseline(clean[-history:])
        expected = mu * w.coverage
        if count_cdf(0, expected, phi) >= alpha:
            run = run + 1 if w.observed == 0 else 0
            out.append(make(GapKind.UNDETECTABLE,
                            "expected volume too low: even a zero would not be significant", expected))
            clean.append((w.observed, max(w.coverage, 1e-9)))
            continue

        p = count_cdf(w.observed, expected, phi)
        if p < alpha:
            if w.observed == 0:
                run += 1
                out.append(make(GapKind.BEHAVIORAL_GAP,
                                "adequate coverage, detectable baseline, zero observed", expected, p))
            else:
                run = 0
                out.append(make(GapKind.DEFICIT, "observed volume significantly below baseline", expected, p))
            continue  # gap windows never feed the baseline
        run = run + 1 if w.observed == 0 else 0
        out.append(make(GapKind.NO_GAP, "consistent with baseline", expected, p))
        clean.append((w.observed, max(w.coverage, 1e-9)))
    return out
