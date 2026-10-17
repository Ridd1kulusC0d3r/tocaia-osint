"""Source-silence monitor: poll feeds into the journal, then classify each source.

The journal separates two things the rest of OSINT tooling blurs:
what the *collector* managed to see (probes ok/failed) and what the *source*
published (new item ids). Feed -> windows -> :func:`tocaia.detect.detect`.
"""

from __future__ import annotations

from collections import defaultdict
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime
from pathlib import Path

from . import journal
from .detect import Detection, Window, detect
from .feeds import fetch, probe


def poll(urls: list[str], path: Path, *, fetcher=fetch, workers: int = 10, ts: str | None = None) -> list[dict]:
    with ThreadPoolExecutor(workers) as ex:
        results = list(ex.map(lambda u: probe(u, fetcher), urls))
    for r in results:  # sequential appends keep the chain well-ordered
        journal.append(path, "probe", r, ts=ts)
    return results


def _win(ts: str, window_days: int) -> int:
    return datetime.fromisoformat(ts).toordinal() // window_days


def windows_from_journal(path: Path, *, window_days: int = 7,
                         probes_per_window: int | None = None) -> dict[str, list[Window]]:
    """Per source: coverage = ok probes / expected probes; observed = items first seen in the window.

    Items already listed at a source's first successful probe are backfill, not
    observed activity, so that probe's window is dropped from the analysis.
    """
    seen: dict[str, set[str]] = defaultdict(set)
    first_ok: dict[str, int] = {}
    tot: dict[tuple[str, int], int] = defaultdict(int)
    ok: dict[tuple[str, int], int] = defaultdict(int)
    new: dict[tuple[str, int], int] = defaultdict(int)
    for rec in journal.read(path):
        if rec["kind"] != "probe":
            continue
        p, w = rec["payload"], _win(rec["ts"], window_days)
        s = p["source"]
        tot[(s, w)] += 1
        if not p["ok"]:
            continue
        ok[(s, w)] += 1
        ids = {i["id"] for i in p["items"]}
        if s not in first_ok:
            first_ok[s] = w
            seen[s] |= ids
            continue
        new[(s, w)] += len(ids - seen[s])
        seen[s] |= ids
    expected = probes_per_window or max(tot.values(), default=1)
    out: dict[str, list[Window]] = {}
    for s, w0 in first_ok.items():
        w_last = max(w for (src, w) in tot if src == s)
        out[s] = [Window(str(w * window_days), new[(s, w)], min(1.0, ok[(s, w)] / expected))
                  for w in range(w0 + 1, w_last + 1)]
    return out


def report(path: Path, **kw) -> dict[str, list[Detection]]:
    det_kw = {k: kw.pop(k) for k in ("alpha", "min_coverage", "history", "min_history") if k in kw}
    return {s: detect(ws, **det_kw) for s, ws in windows_from_journal(path, **kw).items()}
