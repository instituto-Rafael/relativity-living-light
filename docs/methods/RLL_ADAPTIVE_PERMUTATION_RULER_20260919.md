# RLL — Régua Adaptativa de Permutação de Fragmentos V1

**Date:** 2026-09-19  
**State:** `METHOD_CONTRACT / IMPLEMENTED_BOUNDED_SEARCH`  
**claim_allowed:** `false`

## Purpose

Bind the current session fragment ledger to existing RLL operators without attempting a blind Cartesian product or literal infinity.

Predecessors:
- `docs/science/SEED_OMEGA_EVOLUTION_V1.md`
- `data/governance/RLL_GAP_RETROFEEDBACK_V2.json`
- `docs/science/RLL_SESSION_RETROFEEDBACK_FULL_AUDIT_20260919.md`

## Core rule

```text
DO NOT CALCULATE INFINITY.
CALCULATE THE RULER.
BOUND THE SEARCH.
SAMPLE.
MEASURE.
PRUNE.
JUMP.
RECEIPT.
```

## Fragment vector

For fragment i:

```text
F_i =
[layer, impact, uncertainty_reduction, effort,
 undercoverage, recurrence, testability,
 novelty, provenance, claim_gate]
```

## Existing log priority

```text
P_i = log2(impact_i) + log2(uncertainty_reduction_i) - log2(effort_i)
```

This is operational triage only.

## Candidate permutation score

For candidate P:

```text
S(P) =
mean(P_i)
+ w_u U
+ w_r R
+ w_t T
+ w_x X
+ w_n N
+ w_p V
- w_d D
```

where:
- U = mean undercoverage;
- R = mean recurrence;
- T = mean testability;
- X = cross-layer diversity;
- N = mean novelty;
- V = mean provenance quality;
- D = redundancy penalty.

## Adaptive update

If a tested candidate produces feedback reward r:

```text
w_(j,t+1) = w_(j,t) * exp(eta * r * q_j)
```

then normalize.

Reward means information gain, not confirmation. A falsification that collapses uncertainty can be positive reward.

## Search

The implementation:
1. loads the fragment ledger;
2. computes exact finite combination count only as metadata;
3. does not enumerate all combinations;
4. samples tuples without replacement using a deterministic PRNG seed;
5. requires cross-layer tuples by default for discovery;
6. deduplicates sampled tuples;
7. scores candidates;
8. retains a bounded beam;
9. stops after a configured non-improvement patience or sample budget;
10. emits promotion state separately from exploration score.

## Promotion boundary

A high heuristic score never promotes a scientific claim.

```text
SEARCH_SCORE != EVIDENCE
EVIDENCE != CLAIM
```

Candidates containing `TOKEN_VAZIO`, blocked boundaries or contextual-only states remain non-promotable until their local gate is closed.

## Operators bound to each candidate

Candidate receipts may attach:
- DIRECT;
- DERIVATIVE;
- ANTIDERIVATIVE;
- INVERSE;
- REVERSE;
- RECURSIVE;
- LOG;
- ITERATED_LOG;
- PERMUTE;
- RECOMBINE;
- LATENT_RELATION_PROBE.

`DILOG` is admitted only when an actual integral/series structure requires `Li_2`; it is not a biological operator by analogy.

## Stop rules

```text
marginal gain < epsilon -> STOP_BRANCH
recurrence without gain >= rho -> QUIESCE
failed prerequisite -> PRUNE_DESCENDANTS
high-impact undercovered candidate surviving gates -> JUMP
exclusive boundary -> BLOCK
```

## Determinism

Same ledger + same seed + same parameters must produce the same candidate ranking.

## R3

**F_ok:** bounded adaptive permutation semantics defined and tied to existing RLL rules.  
**F_gap:** no empirical feedback/reward history yet, so adaptive weights start from declared priors.  
**F_next:** run deterministic candidate generation, attach explicit falsifiers and only then bind external datasets.
