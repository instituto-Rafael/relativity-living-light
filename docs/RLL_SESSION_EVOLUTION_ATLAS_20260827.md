# RLL Session Evolution ATLAS — 2026-08-27

## Purpose

This ATLAS binds the strong-gravity/Mpemba closure to the interaction-level evolution requested in the 2026-08-27 session. It does **not** promote scientific claims. It makes every material session transition routable, auditable and reversible.

## Route

`PROMPT → INTENT → RISK → AUTHORITY → ARTIFACT → EXECUTION → EVIDENCE → FALSIFIER → RECEIPT → NEXT`

The route preserves the invariant:

`VISAO != ARTEFATO != EXECUCAO != EVIDENCIA != CLAIM`

## Existing enclosures

1. **Urgency** — every open item has priority/urgency and a close condition.
2. **Provenance** — source repository, external source or upstream provider is declared.
3. **Receipts** — execution/evidence transitions produce an auditable record.
4. **ATLAS** — every artifact has a route and authority boundary.
5. **Chain of custody** — data/code/evidence used for claims must remain hash- and ref-bound where technically available.

## Six additional continuous-evolution fences

| Fence | Function | Failure mode |
|---|---|---|
| FENCE-01 AUTHORITY | least privilege + producer authority | fail closed on ambiguous/cross-domain authority |
| FENCE-02 NONREGRESSION | append-only compatibility | fail on historical token/type drift |
| FENCE-03 FALSIFIABILITY | claim/falsifier separation | fail on promotion without observable/falsifier |
| FENCE-04 ROLLBACK | reversible branch/commit path | no destructive autonomous source writes |
| FENCE-05 DRIFT | freshness/knowledge-decay watch | stale external evidence remains open |
| FENCE-06 INDEPENDENCE | separation of duties | producer cannot self-close independent replication |

## Interaction ledger

Canonical normalized receipts are in:

`data/registries/rll_session_interaction_ledger_20260827.v1.json`

Raw private chat text is intentionally not embedded in the repository. Where exact transcript bytes are not under repository custody, the verbatim SHA remains `TOKEN_VAZIO`; semantic turn receipts remain auditable without pretending to possess a byte-exact transcript.

## Chain of custody

Baseline scientific closure:

- branch: `rll/lab`
- approved baseline merge: `30e4d2fd7af3d7b9db3096ba530b72d0275e37f2`
- parent registry: `data/registries/rll_mpemba_horizon_closure_registry.v1.json`
- B10/C11 global scientific claim: **fail closed**

This session extension is append-only relative to that baseline.

## Automation

RLL remains a laboratory/maturity lane. The session-evolution validator therefore runs on relevant pull requests, manual execution and changes reaching `rll/lab`. Time-scheduled federation monitoring is delegated to `instituto-Rafael/RAFAELIA_CORE`, whose default branch can legally host GitHub scheduled workflows.

Autonomous validation is allowed; autonomous scientific claim promotion and autonomous source mutation are not.

## External gaps that remain legitimate

The following are tracked external dependencies, not forgotten gaps:

- official EHT file-level byte custody/SHA-256;
- a physically valid matched relaxation dataset toward a common target;
- covariance/systematics authority bound to that selected observable bundle;
- independent external replication.

They remain `TOKEN_VAZIO`/blocked until their objective close conditions are met.

## F_ok / F_gap / F_next

**F_ok:** prompt-level semantic receipts, six fences, authority/non-regression/falsifiability/rollback/drift/independence controls, event-driven validation.

**F_gap:** external evidence cannot be manufactured by repository governance.

**F_next:** Instituto Rafael control-plane watches federation drift and routes only verified deltas back to authoritative producer repositories.
