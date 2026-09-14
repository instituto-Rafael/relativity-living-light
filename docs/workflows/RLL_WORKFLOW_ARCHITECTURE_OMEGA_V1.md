# RLL Workflow Architecture Ω V1

## Status

```text
status = ACTIVE_GOVERNANCE
claim_allowed = false
publication_effect = NONE
canonical_scientific_outputs_modified = false
```

This document governs how GitHub Actions composes RLL validation, numerical
experiments, receipts, and retrofeedback. It does not certify the repository,
confirm a theory, or convert a successful CI run into scientific evidence.

## 1. First-line invariant

Every automation must make the following legible before execution:


a. **trigger** — why the workflow starts;
b. **authority** — which repository/domain owns the decision;
c. **permissions** — what the token may read or change;
d. **inputs** — which values may alter execution;
e. **outputs** — which artifacts are emitted;
f. **claim boundary** — what a PASS cannot prove;
g. **failure semantics** — what becomes FAIL, residual, or `TOKEN_VAZIO`;
h. **receipt path** — where another operator can inspect the execution.

This is encoded as `KNOWS_BY_ON_FIRST_LINE`. The phrase means that the first
readable layer exposes the automation contract. It does **not** mean the YAML
file possesses knowledge or that an automated result is epistemically final.

## 2. YAML language boundary

GitHub Actions YAML is a declarative orchestration DSL. It is excellent for:

- event routing;
- job dependency graphs;
- matrices;
- permissions;
- concurrency and cancellation;
- timeouts;
- environments;
- reusable workflow calls;
- composite-action calls;
- artifact and receipt routing.

It is a poor home for:

- long Python programs embedded in heredocs;
- scientific equations implemented as shell fragments;
- opaque applications inside `run: |`;
- fitted constants copied into workflow text;
- post-hoc ranking logic;
- hidden promotion decisions.

The canonical composition is therefore:

```text
YAML trigger and DAG
    -> tested Python/module/action
        -> bounded execution
            -> machine-readable receipt
                -> residual and decision
                    -> Ω retrofeedback
```

## 3. Layered architecture

| Layer | Responsibility | Canonical location |
|---|---|---|
| L0 Trigger | `push`, `pull_request`, `workflow_dispatch`, `workflow_call` | `.github/workflows/*.yml` |
| L1 Authority | permissions, class, owner, claim boundary | workflow + architecture contract |
| L2 Composition | jobs, `needs`, matrix, concurrency, timeout | workflow YAML |
| L3 Algorithm | parsing, validation, fitting, aggregation | `tools/`, `scripts/`, `data/pipelines/` |
| L4 Test | unit, adversarial, regression, limit nesting | `tests/` |
| L5 Receipt | JSON, CSV, Markdown, JUnit, hashes, environment | `artifacts/` during CI |
| L6 Decision | PASS/FAIL/residual/TOKEN_VAZIO | versioned contract and report |
| L7 Feedback | new work item or calibrated promotion | queue/ledger/contract |

No lower layer may silently claim the authority of a higher layer.

## 4. Ω feedback cycle

```text
INPUT
  -> CONTRACT
    -> VALIDATE
      -> EXECUTE
        -> RECEIPT
          -> RESIDUAL
            -> DECIDE
              -> FEEDBACK
                -> INPUT(next revision)
```

The cycle is append-only for:

- negative results;
- contradictions;
- `TOKEN_VAZIO` states;
- prior receipts;
- superseded decisions.

A new wording without new source, implementation, execution, falsifier, or
versioned governance rule cannot promote a claim.

## 5. Workflow classes

### Structural

Examples: YAML parsing, schema checks, documentation contracts.

```text
permissions.contents = read
publication_effect = NONE
claim_allowed = false
```

A structural PASS means only that the declared structure executed and passed
its checks.

### Scientific shadow

Examples: frontier contracts, model-family smoke and multi-seed comparison.

```text
same inputs
same covariance
same objective
frozen bounds
predeclared seeds
claim_allowed = false
publication_effect = NONE
```

A ranking is a diagnostic residual, not probability of truth.

### Orchestrator

The orchestrator may receive `actions: write` only because it dispatches other
workflows. It remains manual, sequential, bounded, and non-publishing.

### Publishing

Publishing is outside this V1 implementation. A future publishing workflow must
have an explicit owner, protected environment, reviewed rights, artifact
attestation plan, and an independently reviewable claim package.

## 6. Security invariants

1. Top-level permissions are explicit and least privilege.
2. Checkout uses `persist-credentials: false` in managed workflows.
3. Every runner job has `timeout-minutes`.
4. Validation workflows have concurrency control.
5. Text controlled through issue/PR/event contexts is treated as untrusted.
6. `pull_request_target` is forbidden without a versioned exception.
7. Validation artifacts are uploaded even after failure.
8. External actions are being migrated to full commit-SHA pinning.
9. Secrets must never be printed or placed in receipts.
10. Write permission requires an explicit workflow class.

Action SHA pinning is currently a **transition warning**, because abruptly
failing every legacy workflow would erase operational coverage rather than
improve it. New/managed workflows fail closed on the invariants already under
local control; legacy normalization proceeds incrementally.

## 7. Deterministic dependency policy

The frontier gate installs from:

```text
requirements/ci-frontier.txt
```

The exact resolved environment is preserved through:

```text
python -VV
pip freeze --all
CHECKSUMS.sha256
```

A dependency update requires its own reviewed commit and fresh receipts.

## 8. Multi-seed scientific receipt

The model-family source contract predeclares:

```text
11, 23, 37, 53, 71
```

The multi-seed runner executes every seed with the same:

- H(z) materialization;
- DESI DR2 BAO points;
- covariance;
- objective;
- model order;
- parameter bounds;
- optimizer family;
- `maxiter` and tolerance from the source contract.

For each model it preserves:

- rank by seed;
- rank minimum, median, maximum, and span;
- chi-square/AIC/AICc/BIC distributions;
- H(z) and BAO objective components;
- parameter minimum, median, maximum, and span;
- exact input hashes;
- runtime and environment.

The receipt state is:

```text
RECEIPTED_MULTI_SEED_COMPARISON
```

It does **not** imply:

```text
robust physical preference
independent replication
perturbation validation
theory confirmation
claim_allowed
```

Unstable ranking is retained as useful Ω feedback and never renamed as success.

## 9. Automation profiles

The unified orchestrator discovers the frontier manifest at stage 55.

Default inputs:

```yaml
run_shadow_smoke: false
run_multiseed_receipt: false
```

Thus normal sessions execute structural validation only. Heavy numerical work
requires an explicit override, for example:

```json
{
  "frontier_research_omega": {
    "run_multiseed_receipt": true
  }
}
```

This protects Actions budget and prevents accidental numerical publication.

## 10. Migration strategy

### Phase A — implemented in V1

- versioned workflow architecture contract;
- deterministic architecture auditor;
- all-YAML parser receipts;
- externalized registry logic;
- frozen frontier dependencies;
- workflow anchors to remove path duplication;
- focused adversarial tests;
- multi-seed receipt implementation;
- orchestrator catalog integration.

### Phase B — next normalization

- inventory every external action reference;
- verify upstream owner and release provenance;
- pin reviewed actions to full-length SHAs;
- move repeated setup into reusable workflows or composite actions;
- split legacy workflows by authority and trigger;
- remove obsolete aliases only after evidence of replacement;
- add artifact attestations where publication/build distribution begins.

### Phase C — scientific promotion boundary

Only after a complete numerical receipt exists may the calibration ledger be
reviewed for a possible transition from C2 to C3. The transition is not
automatic and cannot be inferred solely from a green workflow.

## 11. Invariant summary

```text
workflow PASS
!= theory confirmed
!= model preferred
!= dataset rights verified
!= independent replication
!= publication authorization
```

The operational invariant is:

```text
best practice
= explicit authority
+ least privilege
+ bounded execution
+ tested algorithm
+ complete receipt
+ preserved residual
+ reversible decision
```
