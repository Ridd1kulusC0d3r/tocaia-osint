"""Append-only, hash-chained evidence journal (JSON Lines).

Each record commits to the previous record's SHA-256, so any edit, deletion or
reordering is detectable by :func:`verify`. This is tamper-*evidence*, not
tamper-proofing: anchor the head hash somewhere you do not control (a release
note, a signed commit) to make rewriting the whole chain visible too.
"""

from __future__ import annotations

import hashlib
import json
from datetime import datetime, timezone
from pathlib import Path

GENESIS = "0" * 64


def _digest(seq: int, ts: str, kind: str, payload: object, prev: str) -> str:
    body = json.dumps({"seq": seq, "ts": ts, "kind": kind, "payload": payload, "prev": prev},
                      sort_keys=True, ensure_ascii=False, separators=(",", ":"))
    return hashlib.sha256(body.encode("utf-8")).hexdigest()


def read(path: Path) -> list[dict]:
    if not path.exists():
        return []
    with path.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def append(path: Path, kind: str, payload: object, ts: str | None = None) -> dict:
    records = read(path)
    prev = records[-1]["hash"] if records else GENESIS
    seq = len(records)
    ts = ts or datetime.now(timezone.utc).isoformat(timespec="seconds")
    rec = {"seq": seq, "ts": ts, "kind": kind, "payload": payload, "prev": prev,
           "hash": _digest(seq, ts, kind, payload, prev)}
    with path.open("a", encoding="utf-8") as fh:
        fh.write(json.dumps(rec, sort_keys=True, ensure_ascii=False) + "\n")
    return rec


def verify(path: Path) -> tuple[bool, int, str]:
    """Return (ok, records_checked, message)."""
    prev = GENESIS
    records = read(path)
    for i, r in enumerate(records):
        if r.get("seq") != i:
            return False, i, f"record {i}: sequence broken"
        if r.get("prev") != prev:
            return False, i, f"record {i}: chain link broken"
        if r.get("hash") != _digest(i, r["ts"], r["kind"], r["payload"], prev):
            return False, i, f"record {i}: content does not match its hash"
        prev = r["hash"]
    return True, len(records), f"ok, head={prev}"
