# RLL Credential Authority V1 — Preflight Receipt — 2026-09-11

- canonical_repository: `instituto-Rafael/relativity-living-light`
- branch: `security/credential-authority-zero-trust-20260911`
- review_target: `rll/lab`
- kind: `SECURITY_GOVERNANCE_DELTA`
- claim_allowed: `false`
- publication_effect: `NONE`

## Source

1. User-authorized operational requirement: GitHub PAT + temporary Climate Engine
   credential exist in the GitHub Agent secret surface.
2. Repository governance: feature branch → `rll/lab` → maturity chain.
3. GitHub permission model: repository Administration write can delete a
   repository; Contents write can delete repository files; Agent-secrets write
   can delete Agent secrets.

## Delta

- declares a machine-readable credential authority contract;
- keeps GitHub PAT out of Actions by default;
- routes same-repository Actions Git authority through `GITHUB_TOKEN`;
- declares Climate Engine web/trial as temporary provider credential;
- defines `RLL_CLIMATE_ENGINE_TRIAL_TOKEN` only for bounded Actions use;
- blocks destructive API/ref operations in credential-bearing workflow jobs;
- adds static tests and a manual secret-binding preflight that records only
  presence/absence.

## Privacy / custody

- secret_value_read: `false`
- secret_value_written: `false`
- secret_hash_written: `false`
- authorization_header_recorded: `false`
- exact_agent_secret_names: `TOKEN_VAZIO_EXTERNAL_SETTING`
- actions_climate_secret_binding: `TOKEN_VAZIO_EXTERNAL_SETTING`

## External control-plane evidence

- repository rulesets observed through connected GitHub surface: `0`
- branch protection endpoint: `TOKEN_VAZIO_CONNECTOR_ENDPOINT`
- secret scanning / push protection: `TOKEN_VAZIO_EXTERNAL_SETTING`
- environment reviewers: `TOKEN_VAZIO_EXTERNAL_SETTING`

## Boundary

`Contents: write` is not equivalent to "write without delete". If Contents write
is granted to a PAT, file/ref no-delete requires policy + branch/ruleset/review
controls. Repository deletion remains denied when Administration write is absent.

## R3

- F_ok: least-authority model is now explicit and testable.
- F_gap: Actions Climate binding and external branch controls remain unverified.
- F_next: merge through maturity after checks; then bind Climate Actions secret
  only when real trial execution is needed and run the manual preflight.
