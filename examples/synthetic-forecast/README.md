# Synthetic scoring demonstration

All records and probabilities are invented. There is no fitted predictive model and no real account data. This is a hand-checkable arithmetic example, not a benchmark of operational performance.

Run `tocaia-evaluate examples/synthetic-forecast/forecasts.json` after installing the package.

Expected: 3 total, 2 resolved, 1 unresolved; Brier 0.04, baseline Brier 0.25, skill 0.84 (subject to floating-point representation). The unresolved record must not become a negative event or improve the score. A positive skill here is a consequence of the illustrative inputs, not evidence of predictive utility.

For actual analytical records use the [forecast contract](../../docs/forecasting.pt-BR.md) and [record template](../../templates/forecast-record.json).
