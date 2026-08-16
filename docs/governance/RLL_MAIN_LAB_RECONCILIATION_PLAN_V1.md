# RLL Main ↔ rll/lab Reconciliation Plan V1

**State:** `AUDIT_ONLY / TOKEN_VAZIO_HISTORY_RECONCILIATION`  
**Claim boundary:** `claim_allowed=false`  
**Auto-merge:** `false`

## 1. Why this exists

The operational runtime hotfix exposed a conflict between two valid governance intentions:

1. operational inconsistencies should be repaired through reviewed proposals;
2. the canonical maturity topology allows `main` to receive only `rll/release`.

The problem cannot be solved by weakening the maturity gate or by retargeting a main-based branch blindly to `rll/lab`.

## 2. Observed topology

At the 2026-08-16 snapshot:

```text
main     = 8a8c5d20e41a6de1052c1ea2d8d82154f907ef48
rll/lab  = 5b3cddd4b1770b0f8be946a6291ea4c7398d2fdb
merge-base = 73894b9a3bc574849bf488f6f74f42692b236121

main-only commits    = 98
rll/lab-only commits = 44
status               = DIVERGED
```

These numbers are structural Git observations, not maturity scores and not evidence that one branch is scientifically superior.

## 3. Two-sided content classes

The `main` side contains, among other changes, operational Auto-HOTFIX work, new homeostatic/observer/biophoton gates, dashboard material and geophysical-systematics work.

The `rll/lab` side contains, among other changes, workflow/action-pinning evolution, DESI 50-hypothesis intake, formula-test-matrix material and laboratory governance artifacts.

Because both sides contain governance and implementation changes, a whole-branch merge has a nontrivial semantic-conflict risk even when Git reports few textual conflicts.

## 4. Forbidden shortcuts

```text
force-update rll/lab to main
force-update main to rll/lab
disable branch-maturity checks
retarget an existing main-based hotfix PR to rll/lab without rebuilding its ancestry
bulk merge without a path-overlap inventory
interpret a clean textual merge as semantic equivalence
```

## 5. Reconciliation invariant

```text
observe branches
  -> freeze exact SHAs
  -> compute merge-base
  -> enumerate left/right-only commits
  -> enumerate left/right path sets
  -> intersect changed paths
  -> classify domains
  -> partition minimal batches
  -> validate each batch
  -> emit receipt
  -> advance through normal maturity topology
```

No stage authorizes scientific claim promotion.

## 6. Machine observer

`tools/branch_divergence_inventory.py` is intentionally read-only. It invokes only Git inspection commands:

```text
git rev-parse
git merge-base
git rev-list --left-right --count
git diff --name-status
```

It emits:

```text
artifacts/branch-divergence/divergence_snapshot.json
artifacts/branch-divergence/RECONCILIATION_SUMMARY.md
```

The snapshot includes exact SHAs, commit counts, path inventories, overlap paths, domain counts and an `inputs_sha256` binding the observed state.

## 7. Batch strategy

A safe forward-port should be split by dependency and overlap rather than by commit chronology alone.

Proposed classes, still subject to the generated overlap inventory:

```text
B0 governance invariants / action pinning
B1 workflow-contract and reconciliation tools
B2 operational Auto-HOTFIX/runtime observer
B3 laboratory scientific intake/contracts
B4 scientific/implementation bridges
B5 dashboard/UI assets
B6 documentation-only tails
```

A class is not a merge authorization. Each batch needs its own exact path set, dependency graph, tests, receipt and maturity-gate result.

## 8. Promotion condition

`TOKEN_VAZIO_MAIN_RLL_LAB_RECONCILIATION` may only be reduced when:

- both branch heads are frozen in a receipt;
- overlap paths are explicitly reviewed;
- every accepted batch has a hash-bound diff/receipt;
- repository tests and relevant scientific gates pass;
- no unresolved policy conflict is overwritten;
- accepted content enters through the canonical maturity topology.

The operational proposal policy may name a `verified_proposal_base` only after the corresponding route has passed its own branch-maturity evaluation.

## 9. Falsifiability

This plan is falsified as sufficient if a supposedly reconciled state still has unexplained one-sided commits, unreviewed overlapping paths, a failing maturity gate, or a changed scientific/operational claim without its own evidence chain.

A Git `merge` exit code of zero does **not** falsify those residuals by itself.

## 10. R3

```text
F_ok   = exact two-sided SHAs + merge-base + 98/44 divergence + read-only inventory tool
F_gap  = overlap set not yet remotely materialized + per-batch dependency order + reviewed route
F_next = execute tool in PR context, inspect overlap, freeze minimal B0/B1 batch before any content forward-port
```
