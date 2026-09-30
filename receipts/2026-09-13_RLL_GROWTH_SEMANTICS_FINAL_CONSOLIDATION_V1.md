# RLL Growth Semantics — Final Consolidation V1 Receipt

Date: 2026-09-13
State: CONSOLIDATED_FAIL_CLOSED
Claim allowed: false

## Provenance

Main-line prerequisites:
- PR #900 — evidence evolution matrix;
- PR #901 — continuity-semantics prerequisite;
- PR #902 — append-only route correction.

A/B/C custody:
- PR #903 head: e073c1ead1901c1a1ea4ce062e815c13b542bee8;
- PR #903 merged into the scientific parent branch, not main;
- five comparator files restored from their exact source blobs onto this
  consolidation branch.

Scientific evidence:
- A0 barotropic/adiabatic candidate: 0/9 PASS, preserved as negative evidence;
- A/B/C comparator: A background continuity necessary gate PASS, B formal-Q
  algebra PASS with physical receiver blocked, C background boundary PASS.

## Local independent cross-check in this session

The conserved-background equations were evaluated on the declared 3x3
(zt,wt) transition grid with a dense redshift grid to z=10000.

Observed:
- all sampled w_cons values finite;
- no sampled 1+w_cons < -1e-10;
- narrow transitions can produce large positive w_cons, so the kinetic-sign
  check is explicitly treated as necessary, not sufficient.

No physical perturbation equation was invented to force closure.

## Final consolidation

```text
A0 = FALSIFIED_AS_GLOBAL_DEFAULT
A1 = OPEN_BOUNDED_NECESSARY_CONDITIONS_PASS
B  = FORMAL_Q_PASS_PHYSICS_BLOCKED
C  = SURVIVES_AS_OPERATIONAL_BASELINE

operational_baseline = C
physical_semantics_selected = false
selected_semantics = TOKEN_VAZIO
claim_allowed = false
```

## Operational topology boundary

Repository policy requires:

```text
feature/research -> rll/lab -> rll/integration -> rll/release -> main
```

The protected branches are materially out of sync/diverged. This consolidation
does not auto-merge hundreds of unrelated commits merely to satisfy topology.
Promotion must preserve branch-governance evidence rather than bypass it.

## Rollback

Remove only the consolidation overlay/restored comparator custody. Preserve all
source receipts and negative evidence.

## R3

F_ok: scientific state is consolidated without overclaim.
F_gap: exact physical closure remains absent; protected-branch topology is not clean.
F_next: hold claim promotion; only a new evidence-bearing physical closure or a
separate branch-topology reconciliation may supersede this state.
