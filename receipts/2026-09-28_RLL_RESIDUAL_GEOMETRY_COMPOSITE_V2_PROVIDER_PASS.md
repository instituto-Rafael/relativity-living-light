# Provider PASS Receipt — RLL Residual Geometry Composite V2 — 2026-09-28

```text
μID=RLL-RESIDUAL-GEOMETRY-COMPOSITE-V2-PROVIDER-PASS-20260928
parent=RLL-RESIDUAL-GEOMETRY-COMPOSITE-V2-20260928
kind=PROVIDER_EXECUTION_EVIDENCE
run_id=36503480317
job_id=109199476930
tested_merge_ref=f0671b189c7a094e67aea17d8ecdd4e9b988da0c
tested_branch_head=726173d41ea6750b652ff27d24c47329bb059dcb
base=094799c1529e365f0011f462e55db10804cb9ef2
state=PASS_SOFTWARE_GATE
claim_allowed=false
```

## Observed provider evidence

```text
PASS_CONTRACT
PASS_REFERENCE 11.770259055546353
11 passed in 0.09s
```

All workflow steps completed successfully:
checkout, Python setup, contract parse, composite reference execution and focused tests.

## What this proves

- V2 contract is parseable and fail-closed.
- Classical Fibonacci window family is implemented as diagnostic scale.
- Rafael affine +1 recurrence/window family is implemented as diagnostic scale.
- Generic Poincaré nD lift stays inside the unit ball in fixtures.
- Quadratic/Bhaskara descriptor recovers a synthetic parabola.
- Frozen DESI RLL whitened chi-square is reconstructed as `11.770259055546353`.
- Diagnostic composition does not mutate likelihood in the tested path.
- Venturi and calendar remain blocked without their typed bindings.

## What this does not prove

- physical/cosmological validity of the geometric descriptors;
- RLL superiority over LCDM;
- physical Poincaré geometry of spacetime;
- Venturi behavior of cosmological data;
- Maya/calendar causality;
- independent reproduction.

## R3

F_ok = provider software gate PASS + 11 tests + chi2 preserved.  
F_gap = held-out/non-null discrimination + physical adapters + independent reproduction + global PR gates.  
F_next = observe global PR gates; then freeze a held-out/non-null RLL profile without retuning scales/covariance.
