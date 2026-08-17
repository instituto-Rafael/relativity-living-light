## Scope

Close the architectural gap `RUNTIME_ZERO_JOB_FAILURE_API_INGESTION` without inventing a root cause for zero-job failures.

## Invariant

`failure && total_jobs == 0 => RUNTIME_ZERO_JOB_FAILURE => TOKEN_VAZIO_ROOT_CAUSE`

Root-cause inference from zero jobs alone is forbidden. Runtime observations are review-only and never auto-fixable.

## Implementation

- add `tools/github_actions_runtime_ingest.py` with live GitHub API and deterministic snapshot modes;
- add adversarial tests separating zero-job, jobbed-failure, missing-jobs and nonfailure states;
- wire `actions: read` ingestion into `RLL Operational Auto Hotfix`;
- preserve raw runs/jobs snapshots with SHA-256-bound receipts;
- make API unavailability explicit as `TOKEN_VAZIO_EXTERNAL_API`;
- register policy, contract, append-only ledger successor, documentation, design receipt and R3 state.

## Mutation boundary

No scientific claim/result/data, branch protection, ruleset, secret or publication state is auto-mutated. Existing automatic repair remains limited to repository-local `WORKFLOW_INVENTORY_DRIFT`, delivered by reviewed draft PR. `claim_allowed=false`, `publication_effect=NONE`, `auto_merge=false`.

## Acceptance gates

- focused runtime-ingest tests pass;
- live runtime ingestion emits `runtime_receipt.json`;
- raw API snapshots are hash-bound;
- workflow contract remains `82/82`;
- full Python suite has zero regressions;
- observed zero-job failures remain `TOKEN_VAZIO_ROOT_CAUSE` until exact evidence exists.

Draft intentionally. Do not merge from automation.
