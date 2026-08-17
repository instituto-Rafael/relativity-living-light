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

---

## 13. Append-only amendment — runtime ingestion verified

The text above records the original V1 state and is intentionally preserved. A later cycle on 2026-08-16 implemented and remotely exercised the API-bound runtime observer.

Run `31978075898` inspected 25 recent failed workflow runs and separated them as:

```text
24 = failure + zero jobs
 1 = failure + one-or-more jobs
 0 = missing jobs snapshot
```

The API returned successfully. The 24 zero-job cases are represented as:

```text
RUNTIME_ZERO_JOB_FAILURE
state = TOKEN_VAZIO_ROOT_CAUSE
auto_fixable = false
```

No common causal explanation is inferred from the shared `total_jobs=0` observable.

The durable receipt is:

```text
artifacts/governance/RLL_RUNTIME_ZERO_JOB_INGESTION_REMOTE_RECEIPT_20260816_RUN31978075898.json
```

Thus the old residual `RUNTIME_ZERO_JOB_FAILURE_API_INGESTION` is closed only with respect to **ingestion availability**. `TOKEN_VAZIO_ROOT_CAUSE_PER_ZERO_JOB_RUN` remains open.

## 14. Append-only amendment — proposal route contradiction

The same remote cycle exposed a governance contradiction. PR #754 targeted `main` from a non-protected `hotfix/*` branch, while the canonical maturity topology states:

```text
work branch -> rll/lab
rll/lab -> rll/integration
rll/integration -> rll/release
rll/release -> main
```

Branch Maturity Gate V2 and Transit Tower therefore blocked the transition because `main` accepts only `rll/release`.

This is **not** resolved by weakening the gate. It is represented as:

```text
HOTFIX_ROUTE_VS_BRANCH_MATURITY_TOPOLOGY
state = TOKEN_VAZIO_MATURITY_ROUTE
```

A direct retarget to `rll/lab` is also not assumed safe because the observed histories are substantially diverged. Reconciliation is a separate governed operation.

Therefore the operational proposal route is amended to fail closed:

```text
main_hotfix_route.allowed = false
verified_proposal_base = TOKEN_VAZIO_MATURITY_ROUTE
proposal without verified route => receipt only, no PR creation
```

The proposal tool may open a PR only after policy explicitly names an allowed `verified_proposal_base` that matches the requested base. Missing routing evidence is not permission.

## 15. Current R3 successor

```text
F_ok   = runtime API ingestion verified + 82/82 + zero-job/jobbed separation + hash-bound receipts
F_gap  = TOKEN_VAZIO_ROOT_CAUSE_PER_ZERO_JOB_RUN + TOKEN_VAZIO_MATURITY_ROUTE + main/lab divergence
F_next = validate fail-closed proposal tests; audit branch divergence separately; never bypass maturity topology
```
