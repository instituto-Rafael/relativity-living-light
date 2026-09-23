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

## μWRITE — fechamento do encaixe do laboratório

- source snapshot: `main@f69d6827b0a35674de2fd8bad2477fcf8c827af2`
- lab after PR #963: `5c8f8bc2904c97ffce5c63d19714aed67b8bc848`
- lab after WG250 PR #965: `8f925511a26818885845ecbd013d7f5be9936b68`
- exact-head gates: PR #963 = `27/27 PASS`; PR #965 = `12/12 PASS`
- post-merge tree relation: `missing_in_lab=0`, `changed_existing=41`, `lab_only=53`
- interpretation: zero missing paths relative to the named main snapshot; the 41 differing existing paths remain semantic-version differences and the 53 lab-only paths remain preserved laboratory evolution.
- inventory provider evidence: `repo-real-inventory` run `35807306098`, artifact `10727993628`, digest `sha256:95f0aae015bcd0ba72d70a4aa5d7ca43f89bdb99191e9d53f3ce734242901970`.
- boundary: `CI_PASS != scientific_confirmation`; `claim_allowed=false`.
- rollback: revert only this append/inventory fixed-point PR; do not rewrite prior lab history.

