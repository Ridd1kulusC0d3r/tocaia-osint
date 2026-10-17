"""Synthetic benchmark with known ground truth (v0.2).

Generates count series with injected silence episodes (behavioral), collection
outages (data) and partial deficits, then scores detectors against the truth.
Everything is seeded: same arguments, same numbers.
"""

from __future__ import annotations

import math
import random
import statistics
from dataclasses import dataclass

from .absence import GapKind, classify_window
from .detect import Window, detect

WARMUP = 10  # leading windows kept clean so any baseline can form


@dataclass(frozen=True, slots=True)
class Series:
    windows: list[Window]
    truth: list[str]  # normal | behavioral_gap | data_gap | deficit


def _poisson(rng: random.Random, lam: float) -> int:
    if lam <= 0:
        return 0
    if lam > 30:
        return max(0, round(rng.gauss(lam, math.sqrt(lam))))
    limit, k, p = math.exp(-lam), 0, 1.0
    while True:
        p *= rng.random()
        if p <= limit:
            return k
        k += 1


def generate(rng: random.Random, *, n: int = 52, mu: float = 12.0, shape: float = 8.0) -> Series:
    """Overdispersed counts (gamma-mixed Poisson) with injected episodes."""
    label = ["normal"] * n
    cov = [1.0] * n
    factor = [1.0] * n

    def place(kind: str, count: int, lo: int, hi: int) -> None:
        for _ in range(count):
            for _try in range(50):
                length = rng.randint(lo, hi)
                start = rng.randint(WARMUP, n - length - 1)
                span = range(max(WARMUP, start - 1), start + length + 1)
                if all(label[i] == "normal" for i in span):
                    for i in range(start, start + length):
                        label[i] = kind
                        if kind == "behavioral_gap":
                            factor[i] = 0.0
                        elif kind == "deficit":
                            factor[i] = 0.35
                        else:
                            cov[i] = round(rng.uniform(0.1, 0.8), 2)
                    break

    place("behavioral_gap", 2, 2, 5)
    place("data_gap", 2, 1, 4)
    place("deficit", 1, 2, 4)

    windows = []
    for i in range(n):
        lam = mu * rng.gammavariate(shape, 1 / shape) * factor[i] * cov[i]
        windows.append(Window(f"W{i + 1:02d}", _poisson(rng, lam), cov[i]))
    return Series(windows, label)


# --- detectors: each maps a Series' windows to one label per window -------------------

def naive_zero(ws: list[Window]) -> list[str]:
    """Traditional OSINT reading: nothing seen means nothing happened."""
    return ["behavioral_gap" if w.observed == 0 else "normal" for w in ws]


def gated_static(ws: list[Window]) -> list[str]:
    """v0.1 rule: coverage gate + zero, with one global expectation (the series median)."""
    expected = statistics.median(w.observed / max(w.coverage, 1e-9) for w in ws)
    out = []
    for w in ws:
        r = classify_window(window=w.window, expected=expected, observed=w.observed, coverage=w.coverage)
        out.append(r.kind.value if r.kind != GapKind.NO_GAP else "normal")
    return out


def tocaia_v2(ws: list[Window]) -> list[str]:
    out = []
    for d in detect(ws):
        out.append("normal" if d.kind in (GapKind.NO_GAP, GapKind.UNDETECTABLE) else d.kind.value)
    return out


DETECTORS = {"naive_zero": naive_zero, "gated_static_v0.1": gated_static, "tocaia_v0.2": tocaia_v2}


def score(runs: list[tuple[list[str], list[str]]]) -> dict[str, float]:
    """Metrics for the positive class `behavioral_gap` over (truth, predicted) pairs."""
    tp = fp = fn = fc_hit = fc_tot = 0
    for truth, pred in runs[:]:
        for t, p in zip(truth, pred):
            tp += t == p == "behavioral_gap"
            fp += p == "behavioral_gap" and t != "behavioral_gap"
            fn += t == "behavioral_gap" and p != "behavioral_gap"
            if t == "data_gap":
                fc_tot += 1
                fc_hit += p == "behavioral_gap"
    prec = tp / (tp + fp) if tp + fp else float("nan")
    rec = tp / (tp + fn) if tp + fn else float("nan")
    return {"precision": prec, "recall": rec,
            "false_certainty": fc_hit / fc_tot if fc_tot else float("nan"),  # data_gap read as behavior
            "false_positives": fp}


def run(*, series: int = 200, n: int = 52, mu: float = 12.0, seed: int = 7) -> dict[str, dict[str, float]]:
    rng = random.Random(seed)
    data = [generate(rng, n=n, mu=mu) for _ in range(series)]
    return {name: score([(s.truth, fn(s.windows)) for s in data]) for name, fn in DETECTORS.items()}
