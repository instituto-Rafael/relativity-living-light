# Security Policy

This repository treats credentials, external authority, scientific execution, and claims as separate domains.

```text
SECRET != CONFIG != EXECUTION != EVIDENCE != CLAIM
```

## Credential handling

- Never commit API keys, PATs, JWTs, private keys, keystores, passwords, or service-account material.
- Never paste secret values into issues, pull requests, discussions, workflow summaries, receipts, or artifacts.
- Do not persist or publish hashes/fingerprints derived from live credentials.
- Prefer the repository-scoped `github.token` for same-repository CI.
- Use a stored GitHub PAT only when an explicitly governed external/cross-repository authority is required.
- GitHub PATs should be fine-grained, expiring, and omit delete/destructive authority unless a separately reviewed operation requires it.
- Climate Engine trial credentials are temporary and must remain separate from future dataset-specific credentials.
- Exposure of a credential requires revocation/rotation; masking a leaked value is not remediation.

## RLL canonical credential boundaries

| Secret | Purpose | Boundary |
|---|---|---|
| `RLL_GITHUB_PAT` | explicit external/cross-repository GitHub authority | not injected into scientific/PR/scheduled jobs; destructive probes forbidden |
| `CLIMATE_ENGINE_TRIAL_TOKEN` | temporary Climate Engine trial access | expiring, non-canonical provider credential |
| `CLIMATE_ENGINE_DATASET_TOKEN` | future dataset-specific access | successor credential; must not silently overwrite the trial token |

See `docs/governance/RLL_SECRET_AUTHORITY_BOUNDARY_V1.md`.

## GitHub Actions

Security-sensitive workflows must:

- declare least-privilege `permissions`;
- use `persist-credentials: false` for checkout;
- pin new external actions to reviewed commit SHAs;
- avoid `pull_request_target` unless a versioned exception is explicitly reviewed;
- treat event text and external input as untrusted;
- keep secrets step-scoped;
- upload only sanitized receipts;
- use `TOKEN_VAZIO` when external authority or platform state cannot be verified.

A successful CI run is implementation evidence only. It is not scientific validation, legal certification, dataset-rights confirmation, or `claim_allowed=true`.

## Reporting a vulnerability

Do not include a live secret in any public report.

1. Revoke or rotate exposed credentials first.
2. Use GitHub private vulnerability reporting/security advisory when that capability is available.
3. If private reporting is unavailable, submit only a sanitized report that contains no credential material or sensitive reproducer.
4. Record unavailable external security settings as `TOKEN_VAZIO_EXTERNAL_SETTING`; do not infer that a protection exists.

## Supported security route

Security changes follow the repository maturity chain:

```text
feature branch -> rll/lab -> rll/integration -> rll/release -> main
```

Direct-to-`main` changes are break-glass only and require reconciliation back into the maturity chain.

## Claim boundary

Security controls reduce operational risk but do not prove complete absence of vulnerabilities or unauthorized external capabilities.
