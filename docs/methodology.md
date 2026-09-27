# Methodology

T.O.C.A.I.A is a six-stage analytic workflow for Behavioral OSINT and Detection by Absence. Its central discipline is simple: **do not interpret what is missing until you know what you were capable of observing**.

## T · Terrain

Define the decision, the unit of analysis, the time window, the legitimate data surface, retention rules and maximum collection posture. The stage ends with a written scope artifact. Curiosity is not an intelligence requirement.

## O · Observation

Record what the collector could access, what it actually collected, what failed and what was blocked. Preserve provenance and timestamps. A technical failure is an observation about collection, not evidence about target behavior.

## C · Correlation

Normalize timestamps, entities, source provenance and duplicated reporting. Derived posts, screenshots and news coverage can share one upstream origin and therefore do not automatically count as independent corroboration.

## A · Absence

Evaluate detectability before absence. A missing observation is useful only when:

1. a baseline or expectation was declared;
2. the event would have been observable under the method;
3. collection coverage is adequate;
4. mundane collection failures and platform changes have been considered.

T.O.C.A.I.A uses two explicit gap types:

- `data_gap`: insufficient observation;
- `behavioral_gap`: adequate observation with an expected event absent.

## I · Inference

Build competing explanations and actively seek discriminating evidence. ACH can be used as a structured aid, but the matrix is not a probability generator. Record what each item supports, contradicts or leaves neutral, and keep source dependence visible.

## A · Assurance

Ask what would overturn the conclusion. Record revision criteria, unresolved gaps, confidence and provenance. A useful assessment is not one that sounds certain; it is one that another analyst can challenge without reverse-engineering the author's intuition.

## Confidence discipline

Do not merge these concepts:

1. extraction/model confidence;
2. analytic confidence based on evidence quality, independence and coverage;
3. probability of the hypothesized event.

A single score that quietly mixes all three is convenient and analytically poisonous.
