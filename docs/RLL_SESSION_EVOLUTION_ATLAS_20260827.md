# RLL Session Evolution ATLAS — 2026-08-27

## Purpose

This ATLAS binds the strong-gravity/Mpemba closure, the newer `RLL_ATLAS_EVOLUTION_GATE_20260827_V1` G0–G7 governance layer, and the interaction-level evolution requested in-session. It does **not** promote scientific claims.

Canonical route:

`PROMPT → INTENT → RISK → AUTHORITY → ARTIFACT → EXECUTION → EVIDENCE → FALSIFIER → RECEIPT → NEXT`

Invariant:

`VISAO != ARTEFATO != EXECUCAO != EVIDENCIA != CLAIM`

## Predecessors consumed, not replaced

1. B10/C11 operational closure merged at `30e4d2fd7af3d7b9db3096ba530b72d0275e37f2`.
2. Current `rll/lab` baseline `75323d72c9c8d0180c2a01dfb7c7601f5da735c5`, which adds the G0–G7 ATLAS promotion gate.

This mesh is an append-only successor to both.

## Existing enclosures

- **Urgency** — explicit priority and close condition.
- **Provenance** — source/producer/upstream authority.
- **Receipts** — auditable execution/evidence transition.
- **ATLAS** — route and relation graph.
- **Chain of custody** — ref/hash/data custody when evidence is consumed.

## Six additional continuous-evolution fences

| Fence | Existing gate bridge | Function |
|---|---|---|
| FENCE-01 AUTHORITY | G0 + G7 | least privilege and source-of-truth separation |
| FENCE-02 NONREGRESSION | G7 + no-regression contract | append-only compatibility |
| FENCE-03 FALSIFIABILITY | G1 + G3 + G7 | observable/falsifier/claim separation |
| FENCE-04 ROLLBACK | G0 | reversible Git/branch path; no destructive autonomous writes |
| FENCE-05 DRIFT | G0 + G2 + G5 | freshness, covariance and inference decay watch |
| FENCE-06 INDEPENDENCE | G7 | external replication remains external |

## Interaction ledger

`data/registries/rll_session_interaction_ledger_20260827.v1.json`

The repository stores normalized semantic turn receipts, not raw private chat transcripts. Where exact transcript bytes were not independently materialized, the verbatim SHA remains `TOKEN_VAZIO`.

## Scientific gates preserved

The session mesh requires both parent governance records to remain fail-closed:

- `data/registries/rll_mpemba_horizon_closure_registry.v1.json` → `global_scientific_claim_allowed=false`.
- `data/governance/RLL_ATLAS_EVOLUTION_GATE_20260827_V1.json` → `claim_allowed=false`, `G7_CLAIM_DECISION=BLOCKED`, independent-replication blocker open.

No prompt-level tracking may override either gate.

## Automation

RLL validation is event-driven on PR/push to `rll/lab`. Time-based monitoring is delegated to the default branch of `instituto-Rafael/RAFAELIA_CORE`, because GitHub scheduled workflows execute from the repository default branch.

Autonomous validation is permitted. Autonomous scientific claim promotion and autonomous source mutation are not.

## Legitimate external gaps

- official EHT file-level bytes/SHA-256;
- physically valid matched relaxation data toward one declared target;
- covariance/systematics authority tied to that selected observable bundle;
- independent external replication;
- broader G0–G6 RLL promotion prerequisites already tracked by the global ATLAS gate.

These remain auditable blockers rather than hidden gaps.

## F_ok / F_gap / F_next

**F_ok:** session prompt receipts + six fences + G0–G7 bridge + non-regression + delegated time watcher.

**F_gap:** external evidence and independent authority cannot be manufactured by repository governance.

**F_next:** use RAFAELIA_CORE to detect federation drift, then route verified deltas back to the producer repository that owns each domain.
