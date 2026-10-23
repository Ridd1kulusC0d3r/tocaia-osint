# Detection v0.2: learn the normal, prove detectability, keep custody

v0.1 enforced one invariant: a zero under poor coverage is a `data_gap`. v0.2 removes the two weakest assumptions behind it.

| v0.1 assumption | v0.2 replacement |
|---|---|
| The analyst *declares* what was expected | Expectation is **learned** from earlier well-covered windows (coverage-normalised median, negative-binomial dispersion) |
| A zero with good coverage is meaningful | A zero is meaningful only if the baseline makes it **detectable**: `P(X=0 \| baseline) < alpha`, otherwise the window is `undetectable` |

## Window classes

<p align="center"><img src="../assets/gap-classes.svg" alt="The five window classes" width="100%"></p>

| Kind | Meaning |
|---|---|
| `data_gap` | coverage below threshold: we could not see |
| `undetectable` | baseline missing or volume too low; no outcome could be significantly low, so silence says nothing |
| `behavioral_gap` | covered, detectable, zero observed (`P(X<=0) < alpha`) |
| `deficit` | covered, detectable, observed > 0 but `P(X<=k) < alpha` |
| `no_gap` | consistent with baseline |

Design choices worth challenging:

- **Frozen baseline.** Windows flagged as gaps never feed the baseline, so a long silence cannot redefine normal as silence. Cost: a genuine permanent shift stays flagged until an analyst resets it.
- **`undetectable` is an answer, not a failure.** Low-volume sources are the majority in OSINT; pretending to judge them is how false certainty is manufactured.
- **No probability of the event.** `p_low` is a tail probability under a baseline, not the probability that something happened (see *Confidence discipline* in the methodology).

## Evidence journal

`tocaia watch poll` appends one record per probe to a JSONL file; every record commits to the SHA-256 of the previous one. `tocaia journal FILE` re-computes the chain. This is tamper-*evidence*: anchor the head hash outside the file (signed commit, release note) so rewriting the whole chain is also visible. Journals hold public feed metadata (item id, title, link, date) and a hash of the response body, never the raw body.

## Source-silence monitor

```bash
tocaia watch poll feeds/osint.txt --journal evidence.jsonl   # run on a schedule (cron / Actions)
tocaia watch report --journal evidence.jsonl --window-days 7
tocaia journal evidence.jsonl
```

For each source, a probe failure lowers **coverage** (collector problem); new item ids per window are **observed** (source behavior). Items listed at a source's first successful probe are backfill and are not counted. Limits: a feed lists only its latest N items, so high-volume sources can under-count between probes; assigning items to the window they were *first seen* in (not their publication date) is deliberate, to keep the claim about what *we* observed.

## Benchmark (synthetic, known ground truth)

```bash
tocaia bench --mu 12 --series 200 --seed 7
```

Series are gamma-mixed Poisson counts with injected silences (behavioral), collection outages (data) and partial deficits. Positive class: `behavioral_gap`. `false_certainty` = share of true outage windows read as behavior.

| mu | detector | precision | recall | false_certainty | false positives |
|---|---|---|---|---|---|
| 12 | naive zero | 0.95 | 1.00 | 0.04 | 74 |
| 12 | gated static (v0.1) | 0.98 | 1.00 | 0.00 | 32 |
| 12 | **v0.2** | 0.98 | 0.89 | 0.00 | 30 |
| 6 | naive zero | 0.82 | 1.00 | 0.15 | 309 |
| 6 | gated static (v0.1) | 0.90 | 1.00 | 0.00 | 166 |
| 6 | **v0.2** | 0.90 | 0.37 | 0.00 | 60 |
| 2 | naive zero | 0.42 | 1.00 | 0.46 | 1933 |
| 2 | gated static (v0.1) | 0.49 | 1.00 | 0.00 | 1481 |
| 2 | **v0.2** | n/a | 0.00 | 0.00 | 0 |

Read honestly: the static rules reach recall 1.00 only because they flag *every* zero, including the many that chance alone produces when volume is low. v0.2 trades recall for false positives (30 vs 32 at mu=12, 60 vs 166 at mu=6) and **abstains** at mu=2 where no zero can be significant. The gated static rule also gets the series median for free, which a real analyst does not have. These results are synthetic-only (claim C-008); they say nothing about real-world performance.
