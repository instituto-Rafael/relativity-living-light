# Runtime Zero-Job Ingestion V1 — Review Checklist

- [ ] `tests/test_github_actions_runtime_ingest.py` passes remotely.
- [ ] `RLL Operational Auto Hotfix` emits `runtime_receipt.json`.
- [ ] `runtime_receipt.json` contains raw SHA-256 hashes.
- [ ] A jobbed failure is not classified as `RUNTIME_ZERO_JOB_FAILURE`.
- [ ] `failure + total_jobs=0` remains `TOKEN_VAZIO_ROOT_CAUSE`.
- [ ] API unavailability produces `TOKEN_VAZIO_EXTERNAL_API`, not a guessed platform cause.
- [ ] Workflow contract remains `82/82`.
- [ ] Full Python suite has zero regressions.
- [ ] `claim_allowed=false` and `publication_effect=NONE` remain unchanged.
- [ ] No direct-main mutation or auto-merge path was introduced.
