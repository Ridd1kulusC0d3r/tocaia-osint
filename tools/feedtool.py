#!/usr/bin/env python3
"""feedtool - utilitário simples (só stdlib) para listas de feeds RSS/Atom.

Coleta passiva de fontes abertas. Cada feed vivo conta como cobertura;
feed morto é data_gap, nunca "ausência de comportamento".

Uso:
  python tools/feedtool.py check    [arquivos...]            # quais feeds estão vivos
  python tools/feedtool.py coverage [arquivos...]            # cobertura (JSON) p/ a análise de ausência
  python tools/feedtool.py dedupe   [arquivos...]            # remove duplicados/ordena (in-place)
  python tools/feedtool.py opml     [arquivos...]            # gera feeds.opml
  python tools/feedtool.py latest   [arquivos...] [-k cve,ransomware] [-n 1] [-d 7]

Sem arquivos, usa feeds/*.txt.
"""
import argparse, glob, json, re, sys, urllib.request
import xml.etree.ElementTree as ET
from concurrent.futures import ThreadPoolExecutor
from datetime import datetime, timedelta, timezone
from email.utils import parsedate_to_datetime
from xml.sax.saxutils import quoteattr

UA = {"User-Agent": "tocaia-feedtool/2.0 (passive OSINT)"}


def load(files):
    files = files or sorted(glob.glob("feeds/*.txt"))
    urls = []
    for f in files:
        with open(f, encoding="utf-8") as fh:
            urls += [l.strip() for l in fh if re.match(r"https?://", l.strip())]
    return sorted(set(urls)), files


def fetch(url, timeout=15):
    with urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=timeout) as r:
        return r.read()


def child(el, name):
    return next((c for c in el if c.tag.split("}")[-1] == name), None)


def parse_date(text):
    if not text:
        return None
    try:
        d = parsedate_to_datetime(text)  # RSS (RFC 822)
    except (TypeError, ValueError):
        try:
            d = datetime.fromisoformat(text.strip().replace("Z", "+00:00"))  # Atom (ISO 8601)
        except ValueError:
            return None
    return d if d.tzinfo else d.replace(tzinfo=timezone.utc)


def items(url):
    """Devolve [(titulo, link, data|None)] na ordem do feed."""
    root = ET.fromstring(fetch(url))
    out = []
    for it in root.iter():
        if it.tag.split("}")[-1] not in ("item", "entry"):
            continue
        t, l = child(it, "title"), child(it, "link")
        d = child(it, "pubDate") or child(it, "updated") or child(it, "published")
        href = ((l.get("href") or l.text) if l is not None else "") or ""
        out.append(((t.text or "").strip() if t is not None else "", href.strip(),
                    parse_date(d.text if d is not None else None)))
    return out


def check_one(url):
    try:
        tag = ET.fromstring(fetch(url)).tag.lower()
        ok = any(k in tag for k in ("rss", "feed", "rdf"))
        return url, ok, "ok" if ok else "não é feed"
    except Exception as e:
        return url, False, type(e).__name__


def cmd_check(urls, _a):
    with ThreadPoolExecutor(20) as ex:
        res = list(ex.map(check_one, urls))
    bad = [r for r in res if not r[1]]
    for u, _, why in bad:
        print(f"MORTO  {u}  ({why})")
    print(f"\n{len(res) - len(bad)}/{len(res)} feeds vivos")
    return 1 if bad else 0


def cmd_coverage(urls, _a):
    """Cobertura = feeds vivos / feeds esperados. Alimenta o limiar de data_gap."""
    with ThreadPoolExecutor(20) as ex:
        res = list(ex.map(check_one, urls))
    alive = [u for u, ok, _ in res if ok]
    print(json.dumps({
        "collected_at": datetime.now(timezone.utc).isoformat(timespec="seconds"),
        "expected": len(res), "observed": len(alive),
        "coverage": round(len(alive) / len(res), 2) if res else 0.0,
        "dead": sorted(u for u, ok, _ in res if not ok),
    }, ensure_ascii=False, indent=2))


def cmd_dedupe(_urls, a, files):
    for f in files:
        with open(f, encoding="utf-8") as fh:
            lines = fh.read().splitlines()
        head = [l for l in lines if not l.startswith("http")]
        feeds = sorted({l.strip() for l in lines if l.startswith("http")})
        with open(f, "w", encoding="utf-8") as fh:
            fh.write("\n".join(head).rstrip("\n") + "\n\n" + "\n".join(feeds) + "\n")
        print(f"{f}: {len(feeds)} feeds únicos")


def cmd_opml(urls, _a):
    body = "\n".join(f'    <outline type="rss" xmlUrl={quoteattr(u)} text={quoteattr(u)}/>' for u in urls)
    with open("feeds.opml", "w", encoding="utf-8") as fh:
        fh.write(f'<?xml version="1.0"?>\n<opml version="2.0">\n  <head><title>feeds</title></head>\n  <body>\n{body}\n  </body>\n</opml>\n')
    print(f"feeds.opml gerado com {len(urls)} feeds")


def cmd_latest(urls, a):
    kws = [k.strip().lower() for k in a.keywords.split(",") if k.strip()]
    since = datetime.now(timezone.utc) - timedelta(days=a.days) if a.days else None

    def run(u):
        try:
            return u, items(u)
        except Exception:
            return u, []

    with ThreadPoolExecutor(20) as ex:
        for u, its in ex.map(run, urls):
            shown = 0
            for t, l, d in its:
                if since and d and d < since:
                    continue
                if kws and not any(k in t.lower() for k in kws):
                    continue
                print(f"- {t}\n  {l}" + (f"  [{d:%Y-%m-%d}]" if d else ""))
                shown += 1
                if shown == a.n:
                    break


def main():
    p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    p.add_argument("cmd", choices=["check", "coverage", "dedupe", "opml", "latest"])
    p.add_argument("files", nargs="*")
    p.add_argument("-k", "--keywords", default="", help="latest: filtra títulos (ex.: cve,ransomware)")
    p.add_argument("-n", type=int, default=1, help="latest: itens por feed (padrão 1)")
    p.add_argument("-d", "--days", type=int, default=0, help="latest: só itens dos últimos N dias")
    a = p.parse_intermixed_args()
    urls, files = load(a.files)
    if a.cmd == "dedupe":
        cmd_dedupe(urls, a, files)
    else:
        sys.exit({"check": cmd_check, "coverage": cmd_coverage, "opml": cmd_opml, "latest": cmd_latest}[a.cmd](urls, a) or 0)


if __name__ == "__main__":
    main()
