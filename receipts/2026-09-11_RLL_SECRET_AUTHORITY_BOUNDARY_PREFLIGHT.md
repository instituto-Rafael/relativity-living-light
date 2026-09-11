# RLL SECRET AUTHORITY BOUNDARY — PREFLIGHT

- date: 2026-09-11
- branch: `security/rll-secret-boundary-20260911`
- target: `rll/lab`
- repository: `instituto-Rafael/relativity-living-light`
- state: `IMPLEMENTED_UNTESTED`
- claim_allowed: `false`
- publication_effect: `NONE`

## Delta

1. Added `.github/workflows/rll-secret-boundary-assurance.yml`.
2. Added `tools/rll_secret_boundary_assurance.py`.
3. Added `tests/test_rll_secret_boundary_assurance.py`.
4. Added `docs/governance/RLL_SECRET_AUTHORITY_BOUNDARY_V1.md`.
5. Registered the workflow as governed `security_analysis`.

## Authority separation

```text
github.token
  = default same-repository CI authority

RLL_GITHUB_PAT
  = explicit external/cross-repository authority
  = no destructive probe
  = delete scope must be observed or TOKEN_VAZIO

CLIMATE_ENGINE_TRIAL_TOKEN
  = temporary/expiring Climate Engine credential

CLIMATE_ENGINE_DATASET_TOKEN
  = future successor; not silently substituted for trial
```

## Security properties implemented

- manual dispatch only;
- top-level and job-level `contents: read`;
- checkout with `persist-credentials: false`;
- pinned action SHAs;
- GitHub PAT and Climate token never coexist in one process environment;
- no secret value or secret hash in receipts;
- JWT identity fields are not persisted;
- no delete request is attempted;
- sanitized artifacts are uploaded even when the enforcement gate fails.

## Evidence boundary

No workflow execution from this branch has been observed in this preflight receipt.

Therefore:

```text
SOURCE_OBSERVED = true
IMPLEMENTATION_PRESENT = true
EXECUTION = TOKEN_VAZIO
PASS = TOKEN_VAZIO
CLAIM_ALLOWED = false
```

## F_gap

- `TOKEN_VAZIO_EXECUTION_EVIDENCE`
- `TOKEN_VAZIO_GITHUB_SCOPE_INTROSPECTION` when GitHub does not expose classic scope headers
- `TOKEN_VAZIO_CLIMATE_LIVE_TOKEN_VALIDATION`
- repository/organization external policy remains separate from workflow-local controls

## F_next

Run `RLL Secret Boundary Assurance` manually after the two repository secrets use the canonical names. Treat the resulting artifact as the execution receipt; do not promote scientific claims from a credential PASS.
