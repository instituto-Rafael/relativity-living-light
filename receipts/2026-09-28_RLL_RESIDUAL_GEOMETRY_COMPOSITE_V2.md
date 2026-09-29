# Receipt — RLL Residual Geometry Composite V2 — 2026-09-28

\`\`\`text
μID=RLL-RESIDUAL-GEOMETRY-COMPOSITE-V2-20260928
kind=IMPLEMENTATION_RECEIPT
source/ref=
  Drive formula/geometry sources
  + rafaelmeloreisnovo/Matem-tica- formal math
  + rafaelmeloreisnovo/papers publication/crosswalk
  + RLL covariance-whitened multiscale V1
parent=docs/science/RLL_MULTISCALE_HETEROGENEOUS_RESIDUAL_GEOMETRY_V1.md
state=IMPLEMENTED_UNTESTED_PROVIDER
claim_allowed=false
\`\`\`

## Delta

Materialized:

- \`scripts/rll_residual_geometry_composite_v2.py\`
- \`data/contracts/rll_residual_geometry_composite.v2.json\`
- \`tests/test_rll_residual_geometry_composite_v2.py\`
- \`docs/science/RLL_HETEROGENEOUS_RESIDUAL_GEOMETRY_COMPOSITE_V2.md\`
- \`.github/workflows/rll-residual-geometry-composite-v2-gate.yml\`
- this receipt.

## Intended invariant

\`\`\`text
COVARIANCE/WHITENING/CHI2 = UNCHANGED
GEOMETRY/FIBONACCI = DIAGNOSTIC ONLY
\`\`\`

## Evidence state at creation

- files written: OBSERVED by GitHub write receipts;
- provider workflow: NOT_RUN / PENDING PR creation;
- focused tests: NOT_RUN_PROVIDER;
- scientific claim: BLOCKED;
- physical Poincare/Venturi/calendar binding: TOKEN_VAZIO.

## Rollback

Git branch is reversible. No main-branch overwrite or merge is authorized by this receipt.

## R3

F_ok = implementation/contract/tests/workflow/docs materialized.  
F_gap = provider execution + held-out/non-null discrimination + physical bindings + independent reproduction.  
F_next = open draft PR, observe exact-head provider CI, then append a successor receipt with measured status.
