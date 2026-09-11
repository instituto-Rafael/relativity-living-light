# RLL Secret / Authority Boundary V1

Status: **LAB / claim_allowed=false**  
Scope: GitHub Actions credentials for `instituto-Rafael/relativity-living-light`.

## 1. Purpose

Separate external credentials by authority and lifecycle. A credential is an execution capability, not evidence of scientific validity.

```text
SECRET != CONFIG != EXECUTION != EVIDENCE != CLAIM
```

## 2. Canonical secret names

| Secret | Lifecycle | Intended authority | Allowed use |
|---|---|---|---|
| `RLL_GITHUB_PAT` | operator-managed | GitHub authority not covered by same-repository `github.token` | explicit/manual external or cross-repository operations only |
| `CLIMATE_ENGINE_TRIAL_TOKEN` | temporary / expiring | Climate Engine trial API | temporary provider adapter and credential assurance |
| `CLIMATE_ENGINE_DATASET_TOKEN` | future | user/dataset-specific Climate Engine authority | successor credential after dataset access is issued |

The definitive dataset credential MUST NOT silently overwrite the trial credential. Promotion is a versioned transition:

```text
CLIMATE_ENGINE_TRIAL_TOKEN
  -> superseded-by
CLIMATE_ENGINE_DATASET_TOKEN
```

## 3. Least-privilege rule

1. Same-repository CI uses `github.token` by default.
2. `RLL_GITHUB_PAT` is not injected into scientific, scheduled, PR, or fork-triggered jobs.
3. PAT use requires an explicit manual authority surface.
4. No delete operation is performed by the assurance workflow.
5. A statement that the PAT has no delete capability is not promoted to verified evidence unless GitHub exposes sufficient scope metadata or repository/organization settings provide an external receipt.
6. Missing scope introspection is `TOKEN_VAZIO_GITHUB_SCOPE_INTROSPECTION`, never assumed safe or unsafe.
7. Secrets are step-scoped; the GitHub and Climate credentials never share the same process environment.

## 4. Climate trial boundary

The Climate Engine trial token is temporary and expected to expire. The assurance workflow:

- never prints, hashes, or uploads the token;
- checks JWT expiry metadata locally when available;
- observes the public OpenAPI authentication contract without sending the secret;
- does not claim live token validity unless a dedicated, non-destructive validator endpoint is separately governed;
- records live authentication as `TOKEN_VAZIO_CLIMATE_LIVE_TOKEN_VALIDATION` until that gate exists.

Current provider contract observed from Climate Engine OpenAPI: API key in the `Authorization` header. Provider documentation/history is not a substitute for a successful runtime probe.

## 5. GitHub PAT boundary

The assurance workflow performs only a safe GET against the current repository.

For classic PATs, when GitHub returns `X-OAuth-Scopes`, the receipt records whether `delete_repo` is present or absent.

For fine-grained PATs, the runtime may not expose an equivalent complete scope list. In that case:

```text
delete capability = TOKEN_VAZIO
```

No destructive request is used as a test.

## 6. Workflow security controls

`.github/workflows/rll-secret-boundary-assurance.yml` is constrained to:

- `workflow_dispatch` only;
- `permissions: contents: read`;
- pinned external actions;
- `persist-credentials: false`;
- bounded timeout;
- no `pull_request_target`;
- no auto-commit or push;
- sanitized append-only execution artifact;
- `claim_allowed=false` and `publication_effect=NONE`.

## 7. Receipt contract

Runtime artifact:

```text
artifacts/secret-boundary-assurance/
  github_pat.json
  climate_trial.json
  receipt.json
```

Receipts may contain:

- token **kind**, never token value;
- authentication HTTP status;
- GitHub classic scope names when GitHub explicitly returns them;
- token expiration time when encoded in a JWT;
- residual `TOKEN_VAZIO` states;
- commit/workflow/run provenance.

Receipts MUST NOT contain:

- secret value;
- token fingerprint/hash;
- JWT subject, user id, jti, or other account identifiers;
- request Authorization header;
- copied credential material in logs or artifacts.

## 8. Promotion gate

A PASS from this workflow means only that the configured credential boundary behaved as declared.

It does **not** mean:

- Climate Engine dataset rights are verified;
- the trial token is the future dataset token;
- GitHub organization policy is fully protected;
- branch protection/rulesets exist;
- a scientific result is valid;
- `claim_allowed=true`.

## R3

- F_ok: isolated, step-scoped credential surfaces with sanitized receipts.
- F_gap: fine-grained PAT scope introspection and live Climate token validation may remain `TOKEN_VAZIO`.
- F_next: execute the manual assurance; then wire the Climate provider adapter to `CLIMATE_ENGINE_TRIAL_TOKEN` without granting GitHub write/delete authority.
