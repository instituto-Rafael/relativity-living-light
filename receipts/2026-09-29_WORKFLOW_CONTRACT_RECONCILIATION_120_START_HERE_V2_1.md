# Receipt — Workflow Contract Reconciliation after START HERE Ω V2.1

Date: 2026-09-29
State: PROPOSED_RECONCILIATION
claim_allowed: false

## Observed drift

Current executable workflow files in `.github/workflows/`: 120.
Current contract before this proposal: 111.
Canonical synchronizer: `tools/workflow_contract_sync.py`.

The synchronizer's declared write scope is limited to `inventory.active_workflows`. This proposal applies exactly that scalar reconciliation: 111 -> 120.

## Why this is separate from PR #1019

PR #1019 already merged START HERE Ω V2.1 and Root Wave 2. The workflow contract checks then exposed pre-existing/accumulated inventory drift. Updating the scalar is a governance reconciliation, not part of the file-migration evidence.

## Branch maturity contradiction

PR #1019 was merged from `work/start-here-v2-1-root-wave2a-20260929` directly to `main` while the declared maturity topology requires:

`work -> rll/lab -> rll/integration -> rll/release -> main`

The Branch Maturity Gate returned `INVALID_BRANCH_TRANSITION`.

Observed branch relation after the merge:
- `rll/lab` vs `main`: diverged
- `rll/integration` vs `main`: diverged
- `rll/release` is behind `main`

This history cannot be made equivalent by editing a status field. It remains a governance reconciliation gap.

## Boundary

`WORKFLOW_COUNT_RECONCILED != BRANCH_TOPOLOGY_RECONCILED`
`INVALID_BRANCH_TRANSITION != SCIENTIFIC_FAILURE`
`HISTORICAL_MERGE != RETROACTIVE_CANONICAL_TRANSITION`

## R3

F_ok = actual workflow count measured as 120; canonical sync rule identified; scalar reconciliation materialized in draft branch.

F_gap = branch maturity topology is diverged and the #1019 direct work->main transition remains historically non-canonical.

F_next = run contract reconciliation checks on this draft; separately design an explicit branch-history/forward-port reconciliation rather than rewriting history.
