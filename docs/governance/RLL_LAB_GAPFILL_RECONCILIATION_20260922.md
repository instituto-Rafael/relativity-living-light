# RLL lab gap-fill reconciliation — 2026-09-22

State: `MATERIALIZED_PENDING_CI`
Claim allowed: `false`

## Authority
- source: `main@c545e5ac451d8001d927d52d9c089c9092155736`
- target baseline: `rll/lab@ba535d347fe64943d5a5ba15526a0ba7f6ac2141`
- work branch: `reconcile/rll-lab-gapfill-20260922`

## Method
Add every path present in main but absent from the latest rll/lab tree. Do not overwrite existing lab science/code. Preserve lab-only evolution. Existing divergent paths remain `SEMANTIC_MERGE_PENDING`.

Concurrent base advance was detected and this commit was rebuilt on the latest lab head instead of forcing an outdated merge.

## Measured delta
- missing in lab: **125**
- existing divergent: **35**
- lab-only preserved: **48**
- workflows: **101 → 107**

## Boundary
`MATERIALIZED != CI_PASS != SCIENTIFIC_CONFIRMATION`

Rollback: revert this single atomic commit.

## R3
- F_ok: additive forward-port rebuilt on current lab base.
- F_gap: 35 semantic merges remain; CI/runtime pending.
- F_next: observe PR gates, merge only with non-regression evidence.
