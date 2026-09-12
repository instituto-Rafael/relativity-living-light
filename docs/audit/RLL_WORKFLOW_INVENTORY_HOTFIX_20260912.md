# RLL Workflow Inventory Hotfix — 2026-09-12

Authority: `instituto-Rafael/relativity-living-light`  
Branch: `governance/safe-expansion-decomposition-v1-20260912`  
PR: #886  
Claim allowed: **false**

## SOURCE

Observed exact-head failures on `a3997d171ee56e803b8719ad0b4c8d0ffc08fb78`.

Common root cause:

```text
WF_COUNT_MISMATCH:
.github/workflow-contract.yml expects 94 active workflows,
repository discovery finds 95.
```

The additional executable workflow is `.github/workflows/rll-safe-expansion-gate.yml`.

## CONSEQUENCES OBSERVED

1. Workflow Contract Reconciliation V2: failed inventory comparison.
2. Workflow architecture Ω: architecture parse itself passed; documentation contract failed.
3. Workflow Contract Reconciliation: comparison detected drift and fail-closed step exited 1.
4. GitHub Platform Assurance V2: capability tests passed; documentation contract blocked continuation.
5. GitHub Platform Assurance: capability tests passed; documentation contract blocked continuation.
6. Transit Tower Ω: branch maturity blocked because stage tests/docs inherited the same workflow-count mismatch.

No observed evidence in these failures indicates a cosmology-math failure.

## HOTFIX

Only the source-of-truth scalar was changed:

```text
inventory.active_workflows: 94 -> 95
```

No workflow was disabled, deleted, bypassed, or marked optional.
No scientific gate was weakened.
No historical artifact was rewritten.

## EXECUTION

New-head CI after this commit: TOKEN_VAZIO_EXECUTION until observed.

## CLAIM

`claim_allowed=false`.

SOURCE != CONFIG != ARTEFACT != EXECUTION != EVIDENCE != CLAIM.


## HOTFIX 2 — Claim Boundary deterministic prerequisites

Observed on PR #886 / run `34707578765`:

- claim-boundary gate itself: PASS;
- artifact contract checks: PASS;
- unit-test stage: FAIL;
- 20 Route56 failures shared one root cause:
  missing `results/audit/rll_real_data_evidence_bridge.json`;
- 2 workflow-documentation tests also inherited the 94 -> 95 inventory drift.

Repair:
1. add `tools/rll_real_data_evidence_bridge.py` and `tools/rll_cosmology_e0_preflight.py` to the workflow path triggers;
2. materialize both deterministic audit reports before the full unit-test step;
3. assert both files are non-empty before `pytest`.

Consequence:
- claim semantics were not weakened;
- no failed Route56 assertion was bypassed;
- the workflow now owns its runtime prerequisites instead of depending on another job's filesystem state.

Execution on repaired head remains `TOKEN_VAZIO_EXECUTION` until the follow-up PR runs.
