# Contributing

Contributions are welcome when they make the framework more reproducible, more falsifiable or safer to use.

## Before opening a PR

1. Keep examples synthetic or properly anonymized.
2. Do not add active-engagement, credentialed-target or access-control-bypass features.
3. Add tests for executable analytical rules.
4. Label empirical claims as measured, synthetic-only, exploratory, refuted or unmeasured.
5. Document provenance and source dependence.
6. For research claims, add or update `research/claim-register.md`.

## Development

```bash
python -m pip install -e .
python -m unittest discover -s tests -v
```

## Pull-request standard

A useful PR explains:

- what analytic failure it prevents;
- what assumption it introduces;
- how it was tested;
- what would falsify the claim;
- whether it changes privacy, legal or collection posture.
