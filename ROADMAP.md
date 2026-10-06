# Roadmap

The roadmap is intentionally research-first. A flashy interface before reproducible evidence would be the traditional software-industry method of decorating uncertainty.

## v0.2 · Reproducible absence benchmark

- publish a synthetic generator with known ground truth;
- benchmark simple baselines before complex models;
- report uncertainty, false positives and failure modes;
- add machine-readable benchmark manifests;
- record feed `coverage` (see `docs/osint-feeds.md`) as the real-data coverage input.

## v0.3 · Provenance and custody

- append-only evidence journal;
- recomputed SHA-256 on ingestion;
- Merkle root for case snapshots;
- exportable provenance manifest;
- explicit tombstones for retention-driven deletion.

## v0.4 · Structured inference

- ACH artifact model;
- source-dependence tracking;
- discriminating-evidence scoring;
- revision criteria and “what would overturn this?” output;
- no automatic event-probability field.

## v0.5 · Local enrichment

- optional local-only NLP adapters;
- PT-BR labeled evaluation set before performance claims;
- entity extraction separated from identity attribution;
- no target data sent to third-party LLM APIs by default.

## v0.6 · Analyst workbench

- offline report builder;
- timeline and coverage visualization;
- gap-map explorer;
- reproducible case bundle export.

## v1.0 · Research release

A 1.0 release requires more than stable code:

- public threat / misuse model;
- reproducible evidence packages for promoted empirical claims;
- external review of the methodology;
- stable schemas and migration policy;
- documented legal / privacy assumptions;
- multiple synthetic benchmark scenarios;
- at least one independent replication or adversarial evaluation of the core detection logic.

## North-star contribution

The project should become useful not because it “finds people better,” but because it makes OSINT conclusions **more falsifiable, more auditable and harder to overstate**.
