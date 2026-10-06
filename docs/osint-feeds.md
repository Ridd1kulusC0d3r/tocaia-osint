# Passive collection with RSS/Atom feeds

Feeds are the simplest **passive, no-interaction collection adapter** for T.O.C.A.I.A: public sources are polled, nothing is posted, followed or messaged, and no credentials are involved. This document describes the `tools/feedtool.py` helper and how its output feeds the *Observation* and *Absence* stages.

> Stdlib-only Python ≥ 3.10. No installation required.

## Why feeds matter for detection by absence

A feed that stops publishing is ambiguous in exactly the way the framework warns about:

| Situation | Classification |
|---|---|
| The feed URL is dead, blocked or returns non-feed content | `data_gap` — we could not observe |
| The feed is alive and polled on schedule, but the expected publication did not appear | candidate `behavioral_gap` |

So **feed liveness is a coverage measure**. Run `coverage` before every analysis window and record the result as part of the *Observation* artifact; a low value must downgrade any "silence" finding to `data_gap`.

## Layout

```text
feeds/osint.txt        # OSINT / threat-intel / security sources (one URL per line)
tools/feedtool.py      # check · coverage · dedupe · opml · latest
```

Lines that do not start with `http(s)://` are treated as comments/headers. Without file arguments the tool reads every `feeds/*.txt`.

## Commands

```bash
python tools/feedtool.py check                      # list dead feeds (exit 1 if any)
python tools/feedtool.py coverage feeds/osint.txt   # JSON: expected, observed, coverage, dead[]
python tools/feedtool.py dedupe                     # sort + remove duplicates in place
python tools/feedtool.py opml                       # write feeds.opml for any reader
python tools/feedtool.py latest feeds/osint.txt -k cve,ransomware -d 7 -n 3
```

`latest` options: `-k` keyword filter on titles (case-insensitive), `-d` only items from the last N days, `-n` items per feed (default 1).

### Example `coverage` output

```json
{
  "collected_at": "2026-10-06T02:07:12+00:00",
  "expected": 16,
  "observed": 12,
  "coverage": 0.75,
  "dead": ["https://example.org/feed/"]
}
```

## Suggested workflow

1. **Terrain** — declare which sources are *expected* to publish and at what cadence (`templates/scope.md`).
2. **Observation** — run `coverage`, archive the JSON next to the raw items with its timestamp.
3. **Absence** — feed the coverage value to `tocaia-analyze`; below the coverage threshold the result is a `data_gap`.
4. **Assurance** — re-run on a different network/vantage point before promoting a silence to a finding.

## Limits (read before relying on it)

- Liveness only proves the URL answers with XML; it does not prove the feed is *complete*.
- Some sites rate-limit or block unknown user agents; a failure may be the collector's, not the source's. That is precisely why it is a `data_gap`.
- Dates are parsed best-effort (RFC 822 and ISO 8601); items without dates are kept when `-d` is used.

## Ideas for next steps

- Scheduled GitHub Action running `coverage` weekly and committing the JSON as a coverage time series.
- Per-source expected cadence (items/week) so that a missing publication becomes a measurable `expected` vs `observed` pair for the absence analysis.
- Keyword digest (`latest -k`) as a daily triage list, with the source dependence tracked in the claim register.
