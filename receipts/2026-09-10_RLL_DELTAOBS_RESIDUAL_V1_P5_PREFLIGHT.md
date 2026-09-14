# RLL ΔOBS / Residual V1 — P5 implementation preflight receipt

Date: 2026-09-10/11 UTC  
Parent: `75d3bac4eb60e3969a6d51da70296540ab7b3c7b` (PR #851 NOAA Trinity633 merge)  
Branch: `audit/omega-deltaobs-20260910-p5-numeric-gate-v1`  
State at write: `IMPLEMENTED_UNTESTED`  
Claim boundary: `claim_allowed=false`

## Define

CTQ: convert the Trinity633 numerical residual gap into a deterministic, preregistered, fail-closed computation without promoting correlation, independence, cause, mechanism or new physics.

## Measure

Inherited gap from PR #851:

- `numeric_residual=TOKEN_VAZIO_NUMERIC_RESIDUAL_ENGINE`;
- `observed_cross_domain=false`;
- `statistical_independence_established=false`;
- `cause=TOKEN_VAZIO_CAUSA`.

## Analyze

The minimum discriminating layer is a normalized-sample engine with:

- fixed 6h baseline;
- fixed 3h challenge;
- fixed 3h feedback;
- declared sample uncertainty;
- preregistered z threshold;
- preregistered minimum family count;
- no threshold fitting after observation.

A numerical cross-family candidate is not causal evidence.

## Improve

Materialized:

- `data/contracts/rll_deltaobs_residual.v1.json`;
- `scripts/rll_deltaobs_residual.py`;
- `tests/test_rll_deltaobs_residual.py`.

The engine emits `NUMERIC_CROSS_FAMILY_CANDIDATE` or `NO_NUMERIC_CANDIDATE` while forcing:

- `observed_cross_domain=false`;
- `statistical_independence_established=false`;
- `cause=TOKEN_VAZIO_CAUSA`;
- `claim_allowed=false`.

## Control

At write time, exact-head CI is not yet observed.

Dragon falsifiers:

1. missing preregistration must fail closed;
2. insufficient families cannot satisfy the gate;
3. zero numerical scale cannot fabricate a residual;
4. documented common-mode controls cannot create a causal claim;
5. any exact-head test failure remains a failure, not a narrative exception.

## R3

F_ok: numerical ΔOBS layer materialized as a bounded implementation candidate.  
F_gap: execution/CI, normalization from live NOAA payloads, cross-family independence, common-mode exclusion and causal interpretation remain open.  
F_next: open draft PR; observe exact-head tests; only after PASS create a separate phase binding normalized NOAA variables into the engine.

`SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM`  
`RESIDUAL != CAUSE`
