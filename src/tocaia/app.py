"""`tocaia` command: detect, bench, watch, journal."""

from __future__ import annotations

import argparse
import csv
import json
import sys
from pathlib import Path

from . import bench, journal, watch
from .detect import Window, detect


def _detect(a) -> int:
    with a.csv_file.open(encoding="utf-8", newline="") as fh:
        rd = csv.DictReader(fh)
        if set(rd.fieldnames or ()) != {"window", "observed", "coverage"}:
            sys.exit("CSV header must be exactly: window,observed,coverage")
        ws = [Window(r["window"], int(r["observed"]), float(r["coverage"])) for r in rd]
    _print(detect(ws, alpha=a.alpha, min_coverage=a.min_coverage), a.jsonl)
    return 0


def _print(dets, jsonl: bool, prefix: str = "") -> None:
    for d in dets:
        if jsonl:
            print(json.dumps({"source": prefix, **d.to_dict()} if prefix else d.to_dict(), ensure_ascii=False))
        else:
            exp = "  -  " if d.expected is None else f"{d.expected:5.1f}"
            print(f"{prefix}{d.window:<8} {d.kind.value:<15} cov={d.coverage:.2f} obs={d.observed:<4} exp={exp} run={d.silent_run}")


def _bench(a) -> int:
    res = bench.run(series=a.series, n=a.windows, mu=a.mu, seed=a.seed)
    if a.json:
        print(json.dumps(res, indent=2))
        return 0
    print(f"series={a.series} windows={a.windows} mu={a.mu} seed={a.seed}  (class: behavioral_gap)")
    print(f"{'detector':<20}{'precision':>10}{'recall':>8}{'false_certainty':>17}{'FP':>7}")
    for name, m in res.items():
        print(f"{name:<20}{m['precision']:>10.2f}{m['recall']:>8.2f}{m['false_certainty']:>17.2f}{m['false_positives']:>7}")
    return 0


def _watch(a) -> int:
    path = Path(a.journal)
    if a.action == "poll":
        urls = [l.strip() for f in a.sources for l in Path(f).read_text(encoding="utf-8").splitlines()
                if l.strip().startswith("http")]
        res = watch.poll(sorted(set(urls)), path)
        ok = sum(r["ok"] for r in res)
        print(f"{ok}/{len(res)} probes ok -> {path}")
        return 0
    rep = watch.report(path, window_days=a.window_days, probes_per_window=a.probes_per_window, alpha=a.alpha)
    if not rep:
        print("no analyzable windows yet: poll on at least two different windows")
    for src, dets in rep.items():
        _print(dets, a.jsonl, prefix=f"{src[:48]:<50}" if not a.jsonl else src)
    return 0


def _journal(a) -> int:
    ok, n, msg = journal.verify(Path(a.file))
    print(f"{'OK' if ok else 'TAMPERED'}  records={n}  {msg}")
    return 0 if ok else 1


def main(argv=None) -> None:
    p = argparse.ArgumentParser(prog="tocaia", description="T.O.C.A.I.A v0.2 - detection by absence")
    sub = p.add_subparsers(dest="cmd", required=True)

    d = sub.add_parser("detect", help="baseline-aware detection from CSV (window,observed,coverage)")
    d.add_argument("csv_file", type=Path)
    d.add_argument("--alpha", type=float, default=0.01)
    d.add_argument("--min-coverage", type=float, default=0.95)
    d.add_argument("--jsonl", action="store_true")
    d.set_defaults(fn=_detect)

    b = sub.add_parser("bench", help="score detectors on synthetic series with known ground truth")
    b.add_argument("--series", type=int, default=200)
    b.add_argument("--windows", type=int, default=52)
    b.add_argument("--mu", type=float, default=12.0)
    b.add_argument("--seed", type=int, default=7)
    b.add_argument("--json", action="store_true")
    b.set_defaults(fn=_bench)

    w = sub.add_parser("watch", help="poll feeds into the evidence journal / report source silence")
    w.add_argument("action", choices=["poll", "report"])
    w.add_argument("sources", nargs="*", help="poll: feed list files (one URL per line)")
    w.add_argument("--journal", default="evidence.jsonl")
    w.add_argument("--window-days", type=int, default=7)
    w.add_argument("--probes-per-window", type=int)
    w.add_argument("--alpha", type=float, default=0.01)
    w.add_argument("--jsonl", action="store_true")
    w.set_defaults(fn=_watch)

    j = sub.add_parser("journal", help="verify the hash chain of an evidence journal")
    j.add_argument("file")
    j.set_defaults(fn=_journal)

    a = p.parse_args(argv)
    sys.exit(a.fn(a))


if __name__ == "__main__":
    main()
