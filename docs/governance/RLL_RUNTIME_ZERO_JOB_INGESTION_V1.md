# RLL Runtime Zero-Job Ingestion V1

Status: `GOVERNED_REVIEW_REQUIRED`  
Claim boundary: `claim_allowed=false`, `publication_effect=NONE`.

## Purpose

Convert `RUNTIME_ZERO_JOB_FAILURE_API_INGESTION = TOKEN_VAZIO` from an unobserved external gap into a reproducible GitHub Actions runtime evidence stream.

The collector does **not** infer why a workflow failed merely because GitHub reports zero jobs. It records the exact run, exact jobs-endpoint response, provenance, hashes, urgency, falsifier and next action.

## Observable

For each recent workflow run with `conclusion=failure`, ingest:

- run id;
- workflow name;
- event;
- head SHA;
- creation/update timestamps;
- exact jobs endpoint;
- `total_jobs`.

Classification invariant:

```text
failure && total_jobs == 0
    => RUNTIME_ZERO_JOB_FAILURE
    => state = TOKEN_VAZIO_ROOT_CAUSE
    => auto_fixable = false
```

A run with one or more jobs is counted as a jobbed failure and is **not** mislabeled as a zero-job failure.

## Falsifiability

The observation `RUNTIME_ZERO_JOB_FAILURE` is falsified for an exact run if a reproducible snapshot of that run's jobs endpoint contains one or more jobs.

The `TOKEN_VAZIO_ROOT_CAUSE` may be closed only by evidence that identifies a cause for the exact run, for example a platform receipt, workflow parsing/event-eligibility evidence, or another source with equivalent provenance. A generic guess does not close it.

## API uncertainty

If the GitHub API cannot be read, the collector must still emit products and record:

```text
RUNTIME_API_INGESTION_FAILURE
state = TOKEN_VAZIO_EXTERNAL_API
```

This state is review-only. API unavailability is not converted into a platform-failure claim.

## Products

Each execution emits:

- `runtime_observations.jsonl`;
- `runtime_state_vector.json`;
- `runtime_receipt.json`;
- `RUNTIME_SUMMARY.md`;
- `raw/runs.json`;
- `raw/jobs_<run_id>.json` for retrieved job snapshots.

The receipt hashes each raw source and the observation ledger with SHA-256. Runtime artifacts are retained by the workflow for 90 days.

## Evolution vector

The runtime vector follows:

```text
V_next = VALIDATED(V_current) + explicit_delta
```

with `F_ok`, `F_gap`, `F_next`, `TOKEN_VAZIO`, urgency, provenance and falsifier explicit. Negative observations are appendable evidence; they do not authorize mutation of scientific code, claims, datasets, branch protection, rulesets, secrets or publication state.

## Security and mutation envelope

The observing job receives only `contents: read` and `actions: read`. Runtime observations are never auto-fixable. The existing bounded auto-hotfix remains limited to repository-local `WORKFLOW_INVENTORY_DRIFT`, delivered by draft pull request with `auto_merge=false`.

## Reproduction

The tool supports two modes:

1. live GitHub API ingestion;
2. deterministic snapshot ingestion using a saved runs JSON and saved jobs JSON files.

The deterministic mode is covered by adversarial tests to ensure zero-job, jobbed-failure, missing-jobs and nonfailure cases remain separated.

## Decision boundary

This mechanism improves operational observability. It does not prove scientific validity, independent replication, physical execution, or GitHub platform enforcement. Those remain separate gates until their own evidence exists.
