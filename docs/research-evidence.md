# Research evidence and claim discipline

T.O.C.A.I.A separates **method**, **implementation** and **empirical claim**. A component can exist in code without being validated, and a compelling conference slide is not a validation package. Humanity has survived enough bar charts with no dataset attached.

## Working claim register

The current project notes report the following results. They are reproduced here as a **claim inventory**, not as independent verification by this repository.

| Component | Reported evidence in project notes | Current public status |
|---|---|---|
| Hawkes model for internal-interval anomaly | AUC 0.83 / 0.74 | `synthetic-only` |
| EIG÷cost collection policy | ~30% fewer collections; very small reported p-value | `synthetic-only` |
| Hawkes model for persistence of current terminal silence | Real-data Exp. 3 / 3R | `refuted` in project notes; absolute silence duration reportedly won |
| Days of current silence as persistence signal | AUC 0.88 / 0.87 in two reported samples | `reported-real-data`; reproducibility package pending |
| Automation triage | Strong vs naive bot; poor vs bot imitating humans | `limited`; triage only, never verdict |
| Portuguese NLP regex / GLiNER2 | No published measurement | `unmeasured` |

## Publication rule

A claim should move from project note to public evidence only when the repository contains, as appropriate:

- a preregistered protocol or timestamped analysis plan;
- dataset provenance or a lawful shareable substitute;
- code and environment instructions;
- metrics with uncertainty and baseline comparison;
- negative results and failure conditions;
- a reproducible command that regenerates the result.

## Why refutations remain public

A negative result changes the doctrine. If a complex model loses to a simple duration baseline, the framework should record that and become simpler. Research credibility comes from visible constraint, not from collecting sophisticated nouns.
