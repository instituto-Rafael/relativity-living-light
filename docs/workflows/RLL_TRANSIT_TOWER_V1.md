# RLL Transit Tower V1

Status: `PROPOSED_FOR_RLL_LAB`  
Claim boundary: `claim_allowed=false` · `publication_effect=NONE`

## Purpose

The Transit Tower is the single controlled entry point for workflow refactoring.
It inventories every executable workflow, selects only explicitly governed
specialties, executes one child at a time, and stops after the first red stage.
It does not delete legacy workflows and does not treat structural CI as
scientific evidence.

The canonical specialty block is
`.github/workflow-orchestrator/workflows/tower/00-transit-tower.yml`; historical
catalog directories remain non-authoritative compatibility material.

## Eight-stage transit

| Stage | Specialty | Child workflow | Enforced mode |
|---:|---|---|---|
| 5 | YAML custody scan | `yaml-deep-audit.yml` | exhaustive; fail on `HIGH` |
| 10 | Workflow architecture | `yml-syntax-validation.yml` | strict |
| 20 | Executable contract | `workflow-contract-sync-v2.yml` | read-only comparison |
| 30 | Regression | `python-tests.yml` | repository test receipt |
| 40 | Governance | `rll-governance-quality-gate.yml` | non-certification |
| 50 | Real-data custody | `real-data-complete-execution.yml` | `audit_only`, strict |
| 60 | Scientific structure | `rll-pipeline-linear-completo.yml` | `dry_run` |
| 70 | Frontier shadow | `frontier-research-composition.yml` | both execution flags `false` |

The stage number is ordering metadata, not a maturity or scientific score.

## Execution invariants

- `mode=sequential`, `max_in_flight=1`, and a completion barrier are mandatory.
- `--wait` and `--fail-fast` are mandatory; disabling either is a receipted blocker.
- The selected branch must resolve to the exact checkout SHA before any dispatch.
- Every child run must report the same head SHA as the parent transit receipt.
- A timeout requests cancellation and blocks every downstream specialty.
- Input overrides are denied unless the specialty manifest allowlists the field.
- The orchestrator cannot dispatch itself.
- Event-driven and standalone workflows are inventoried but never implicitly run.

## Decision states

| State | Meaning |
|---|---|
| `PASS` | All selected child workflows completed successfully at the recorded SHA. |
| `FAIL` | A child completed with a non-success conclusion; downstream stages were not run. |
| `BLOCKED` | Preflight, API, provenance, timeout, ref, or receipt integrity prevented a valid decision. |
| `OBSERVED_LIMITED` | Dry-run plan was validated; no child execution evidence exists. |

`PASS` never means theory confirmed, model preferred, publication ready,
independent replication complete, or physical execution observed.

## Receipts

Each run writes:

- `orchestration_receipt.json` — canonical machine receipt;
- `orchestration_summary.json` — compatibility copy for V1 consumers;
- `ORCHESTRATION_REPORT.md` — operator view;
- `workflow_inventory.tsv` — path, SHA-256, trigger, dispatchability, classification.

The canonical receipt contains the commit SHA, workflow/job identity,
input-contract SHA-256, decision, residuals, every selected stage, and every
workflow discovered in `.github/workflows`. It always preserves
`claim_allowed=false`, `scientific_gate=BLOCKED`, and
`publication_ready=false` regardless of structural completion.

## Intentional exclusions

The following legacy routes remain present but are disabled in the strict
catalog until their own evidence contracts are repaired:

- `START_MANUAL_HERE.yml`: oversized embedded programs and mutable dependencies;
- `formulas-artifacts.yml`: implicit checkout credentials and non-guaranteed receipt upload;
- `iml_artifact.yml`: missing input can fall back to an example fixture.

Disabling a route is not deletion. Each exclusion is emitted as an append-only
residual so it cannot disappear from the operating picture.

## Operating procedure

1. Open the workflow on the branch being measured; cross-branch dispatch is forbidden.
2. Run `transit_refactor` with `dry_run=true` and inspect the inventory/plan receipt.
3. Run with `dry_run=false` only after the dry-run receipt matches the intended SHA.
4. If a stage is red, use its child artifact plus the parent residual to repair that
   specialty; rerun from stage 5 rather than skipping the failed gate.
5. Promote only through `feature → rll/lab → rll/integration → rll/release → main`.

## Rollback

The implementation is isolated to the orchestrator engine, its catalog/manifests,
tests, two workflow façades, and this document. Rollback is a normal revert of the
reviewed commit. No child workflow is deleted or rewritten by the engine.
