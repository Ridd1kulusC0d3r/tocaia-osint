"""Passive RSS/Atom probing. Read-only HTTP GET of public feeds; nothing else."""

from __future__ import annotations

import hashlib
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

UA = {"User-Agent": "tocaia-watch/0.2 (passive OSINT; read-only)"}


def fetch(url: str, timeout: int = 15) -> bytes:
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def _child(el, name):
    return next((c for c in el if c.tag.split("}")[-1] == name), None)


def _date(text: str | None) -> str | None:
    if not text:
        return None
    try:
        d = parsedate_to_datetime(text)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))
        except ValueError:
            return None
    return (d if d.tzinfo else d.replace(tzinfo=timezone.utc)).isoformat(timespec="seconds")


def parse_items(body: bytes) -> list[dict]:
    root = ET.fromstring(body)
    if not any(k in root.tag.lower() for k in ("rss", "feed", "rdf")):
        raise ValueError("not a feed")
    items = []
    for it in root.iter():
        if it.tag.split("}")[-1] not in ("item", "entry"):
            continue
        title, link = _child(it, "title"), _child(it, "link")
        ident = _child(it, "guid") or _child(it, "id")
        href = ((link.get("href") or link.text) if link is not None else "") or ""
        t = (title.text or "").strip() if title is not None else ""
        key = (ident.text or "").strip() if ident is not None and ident.text else href.strip() or t
        pub = _child(it, "pubDate") or _child(it, "published") or _child(it, "updated")
        items.append({"id": hashlib.sha256(key.encode()).hexdigest()[:16], "title": t,
                      "link": href.strip(), "published": _date(pub.text if pub is not None else None)})
    return items


def probe(url: str, fetcher=fetch) -> dict:
    """One observation about *collection*: did we get a valid feed, and what did it list."""
    try:
        body = fetcher(url)
        return {"source": url, "ok": True, "body_sha256": hashlib.sha256(body).hexdigest(),
                "items": parse_items(body)}
    except Exception as exc:  # a failure is evidence about the collector, never about the source's behavior
        return {"source": url, "ok": False, "error": type(exc).__name__, "items": []}
