# RLL Credential Authority V1 — Agent Secrets × Actions × Climate Trial

Status: `ACTIVE_GOVERNANCE`  
Scientific effect: `NONE`  
`claim_allowed=false`

## Objective

Separate credential storage from execution authority so a temporary Climate
Engine trial credential and a GitHub PAT cannot silently become repository-wide
authority.

```text
SECRET ≠ AUTHORITY ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM
```

## Authority split

| credential | preferred surface | allowed purpose | repository write |
|---|---|---|---|
| GitHub fine-grained PAT | GitHub Agent secret | agent feature-branch + reviewed PR only | only if explicitly required |
| GitHub Actions same-repo auth | built-in `GITHUB_TOKEN` | bounded workflow operation | job-level only |
| Climate Engine trial | Agent secret; optionally Actions secret | temporary provider read/query | none |

The GitHub PAT is **not** mirrored into Actions by default. A same-repository
workflow uses `GITHUB_TOKEN` with the smallest job-level `permissions:` block.

The temporary Climate credential may be mirrored into Actions under the canonical
name `RLL_CLIMATE_ENGINE_TRIAL_TOKEN`, but while it is a trial credential it is
restricted to a manually dispatched, reviewed job.

## "No delete" boundary

For a fine-grained PAT, removing repository `Administration: write` prevents the
token from using the repository-delete endpoint. This is the hard repository
boundary adopted here.

There is a second boundary: GitHub's `Contents: write` permission also authorizes
the REST endpoint that deletes a file, and ref write permissions can include ref
deletion. Therefore **"write but cryptographically/API-incapable of every file or
ref delete" is not representable by PAT Contents permission alone**.

RLL therefore enforces no-delete operationally with:

1. no `Administration: write`;
2. no `Agent secrets: write`;
3. no direct `main` commit;
4. feature branch → reviewed PR;
5. no force push;
6. no DELETE HTTP calls in credential-bearing jobs;
7. no Git ref deletion in credential-bearing jobs;
8. branch/ruleset enforcement when externally configured.

If `Contents: write` is unnecessary, set it to read-only. That is the strongest
credential-level no-file-delete boundary.

## Agent secret is not Actions secret

Agent secrets and Actions secrets are separate GitHub control-plane stores.
Presence in Agent secrets does not establish that an Actions workflow can read
the same credential.

This repository does not infer that configuration. Until a manual preflight
observes the Actions binding:

```text
ACTIONS_CLIMATE_SECRET_BINDING = TOKEN_VAZIO_EXTERNAL_SETTING
```

No secret value, length or hash is written to a receipt.

## Trial-to-dataset transition

Current provider state:

```text
Climate Engine web/trial
→ temporary credential
→ adapter contract
→ evidence/receipt
```

Future state:

```text
dataset credential
→ same adapter boundary
→ new credential receipt
→ trial credential revoked/removed
```

The provider credential may change without redefining RLL scientific claims.

## Manual control-plane step

When Climate Engine execution from GitHub Actions is actually needed, create an
**Actions** repository/environment secret named:

```text
RLL_CLIMATE_ENGINE_TRIAL_TOKEN
```

using the same current trial value already held privately. Do not paste the value
into a workflow, issue, PR, artifact or receipt.

Then manually dispatch `RLL Governance Quality Gate — non-certification`. The
credential-binding preflight records only a boolean presence state and fails
closed if the Actions binding is absent.

## Sources

- GitHub Docs — fine-grained PAT permissions:
  https://docs.github.com/en/rest/authentication/permissions-required-for-fine-grained-personal-access-tokens
- GitHub Docs — repository contents API:
  https://docs.github.com/en/rest/repos/contents
- GitHub Docs — Actions secrets:
  https://docs.github.com/en/actions/concepts/security/secrets
- GitHub Docs — Agent secrets API:
  https://docs.github.com/en/rest/agents/secrets

## R3

- F_ok: authority is split; PAT remains agent-first; same-repo Actions route uses `GITHUB_TOKEN`.
- F_gap: exact Agent-secret names and Actions binding are external control-plane state.
- F_next: bind only `RLL_CLIMATE_ENGINE_TRIAL_TOKEN` in Actions when required and execute the manual preflight.
