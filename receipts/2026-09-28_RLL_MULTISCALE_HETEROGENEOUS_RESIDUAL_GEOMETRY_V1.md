# RLL Multiscale Heterogeneous Residual Geometry V1 — Receipt

**Date:** 2026-09-28  
**PR:** #1005  
**Branch:** `work/multiscale-heterogeneous-residual-geometry-v1-20260928`  
**Base observed at PR creation:** `c3b3bb8b16a7f4ca07874fed16c0c8c18aad5c89`  
**Head before this receipt:** `3ca65e69bb16d6fc1c3ffd31679be017075e54e1`

## Materialized

- `docs/science/RLL_MULTISCALE_HETEROGENEOUS_RESIDUAL_GEOMETRY_V1.md`
- `data/contracts/rll_multiscale_heterogeneous_residual.v1.json`
- `data/examples/rll_multiscale_heterogeneous_residual.example.json`
- `scripts/rll_multiscale_heterogeneous_residual.py`
- `tests/test_rll_multiscale_heterogeneous_residual.py`
- `.github/workflows/multiscale-heterogeneous-residual-gate.yml`
- successor pointer in `SEED_OMEGA_EVOLUTION_V1.md`
- variance-registry pointer in `REAL_DATA_VARIANCE_REGISTRY.md`
- rationality-language correction in `verify_cal_maya_arithmetic.py`

## Provider evidence observed

Dedicated workflow:

- workflow: `Multiscale Heterogeneous Residual Gate`
- run_id: `36476924327`
- job_id: `109112835357`
- job: `validate`
- conclusion: `success`

Observed successful steps:

1. checkout;
2. Python 3.11 setup;
3. JSON contract/example parse;
4. multiscale reference example;
5. focused pytest suite;
6. Maya calendar arithmetic comparator.

Also observed on the same PR head:

- `Validate Real Dataset Variance Registry` run `36476924254`: `success`.

## What this PASS means

`PASS` is bounded to the software/formal gate above:

- contract/example JSON parse;
- reference implementation executes;
- finite TSS/WSS/BSS closure;
- residual-budget closure;
- Fibonacci diagnostic windows are not likelihood weights;
- focused tests pass;
- corrected Maya arithmetic comparator executes.

## What this PASS does NOT mean

It does not establish:

- a new probability distribution;
- optimality of Fibonacci windowing;
- a physical mechanism behind residual structure;
- a cosmological role for Poincaré/geodesic geometry;
- a physical Venturi-RLL equivalence;
- a causal astrophysical interpretation of the Maya calendar;
- superiority of RLL over another cosmology.

`claim_allowed=false` remains.

## R3

```text
F_ok =
formal composition
+ executable adapter
+ focused tests
+ dedicated provider CI PASS
+ variance registry gate PASS
+ predecessor/successor routing

F_gap =
real-dataset binding with frozen grouping/order/covariance
+ comparison with existing rll_deltaobs_residual.py
+ external/independent reproduction
+ physical mechanisms for any domain-specific promotion

F_next =
choose one frozen RLL observational dataset
-> define groups/order/covariance before viewing the result
-> run baseline deltaobs and heterogeneous multiscale adapter side by side
-> record whether the additional decomposition changes only diagnosis or materially changes model inference
```
