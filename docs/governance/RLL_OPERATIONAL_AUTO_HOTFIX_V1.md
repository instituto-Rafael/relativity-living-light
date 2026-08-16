# RLL Operational Auto-Hotfix V1

**State:** `GOVERNED / REVIEW_REQUIRED`  
**Date:** 2026-08-16  
**Claim boundary:** `claim_allowed=false`  
**Publication effect:** `NONE`

## 1. Purpose

This layer observes operational inconsistencies and turns them into navigable,
auditable objects instead of silently editing the repository.

The invariant is:

```text
observe -> classify -> evidence -> urgency -> falsifier -> safe-fix decision
       -> receipt -> reviewed PR -> re-observe
```

Scientific truth is outside the authority of this automation.

## 2. Incident that motivated V1

At `main` commit `72e74f3560d9307f215fb84fe01590902723f279`, Python tests executed normally and produced:

```text
1206 passed
2 failed
12 subtests passed
```

Both failures had the same root cause:

```text
WF_COUNT_MISMATCH
contract expects 78 active workflows
discovered 81
```

The three additions were:

```text
.github/workflows/rll-homeostatic-field-gate.yml
.github/workflows/rll-observer-mirror-photon-gate.yml
.github/workflows/rll-biophoton-metabolic-transduction-gate.yml
```

The hotfix preserves all three workflows and reconciles the contract. V1 itself
adds one governed workflow, so the reviewed branch census becomes `82`.

## 3. Epistemic object

Every detected item is represented as:

```text
O_i = <
  id,
  kind,
  urgency,
  state,
  source,
  evidence,
  auto_fixable,
  proposed_action,
  falsifier,
  provenance
>
```

No observation disappears because a newer observation exists.

## 4. Urgency

```text
P0 = deterministic CI/governance integrity break
P1 = security/provenance/reproducibility weakness
P2 = epistemic/research/documentation debt
```

Urgency does not mean truth probability.

## 5. TOKEN_VAZIO and uncertainty

The observer scans governance authorities for explicit `TOKEN_VAZIO`,
`INCERTEZA`, `TODO` and `FIXME` markers and makes them navigable.

It does **not** close them automatically.

A token may leave `TOKEN_VAZIO` only after its own evidence contract is met:

```text
source + definition + evidence + falsifier + limit + custody
```

If any mandatory component remains absent, the token remains open.

## 6. Safe auto-fix envelope

V1 permits exactly one automatic repository-local mutation class:

```text
WORKFLOW_INVENTORY_DRIFT
```

The repair is limited to the scalar:

```text
.github/workflow-contract.yml
inventory.active_workflows
```

The value is derived from the executable `.yml/.yaml` census. The mutation is
made only in a workspace and may be delivered only by review PR.

Forbidden:

```text
direct commit to main
auto merge
scientific claim mutation
scientific data mutation
likelihood/evidence mutation
secret mutation
branch-protection/ruleset mutation
physical interpretation promotion
publication promotion
```

## 7. Products

Every observer execution produces:

```text
observations.jsonl
state_vector.json
receipt.json
SUMMARY.md
```

These are uploaded as GitHub Actions artifacts. The receipt binds the observation
set by SHA-256. A durable repository receipt is justified only when a reviewed
hotfix actually changes repository state.

## 8. State vector

The operational vector is:

```text
V_ops = <F_ok, F_gap, F_next, TOKEN_VAZIO, INCERTEZA, urgency, provenance, falsifier>
```

Evolution is append-only conceptually:

```text
V_(n+1) = VALIDATED(V_n) + explicit_delta
```

Contradictions and regressions are new observations, never erased history.

## 9. Automatic cadence

The governed workflow observes on:

```text
pull requests to main touching governance/CI authorities
push to main touching governance/CI authorities
periodic schedule
manual dispatch
```

On `main` push/schedule, a safe deterministic mismatch may generate a **draft**
PR proposal. No scientific or external-setting correction is included in that
proposal.

## 10. Provenance and falsifiability

A repair is considered operationally closed only when all are true:

```text
contract census matches executable census
focused unit tests pass
workflow documentation contract passes
automation receipt exists
new main run reproduces the closure
```

A green workflow is evidence of the declared computational gate only. It is not
scientific confirmation.

## 11. Known residuals after this hotfix

```text
RUNTIME_ZERO_JOB_FAILURE_API_INGESTION = TOKEN_VAZIO
GITHUB_PLATFORM_ENFORCEMENT            = TOKEN_VAZIO
INDEPENDENT_REPLICATION                 = TOKEN_VAZIO
PHYSICAL_EXECUTION                      = TOKEN_VAZIO
```

The runtime `zero jobs` class needs a later API-bound observer because source-tree
inspection alone cannot establish the remote startup cause.

## 12. R3

```text
F_ok   = deterministic observer + bounded repair + artifacts + ledger + pinned new gates
F_gap  = runtime API ingestion + external platform enforcement + independent replication
F_next = execute PR CI, merge only after review, then re-observe main and append receipt
```
