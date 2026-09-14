# RLL Credential Authority V1 — Repository Secrets × Actions × Agent Boundary

Status: `ACTIVE_GOVERNANCE`  
Scientific effect: `NONE`  
`claim_allowed=false`

## Canonical authority

The owner-reported Actions pair is **GitHub Actions Repository Secrets**. Agents has its own separate pair, documented below:

| Repository Secret | Purpose | Runtime surface | Repository write |
|---|---|---|---|
| `GITPAT` | manual GitHub authentication/read assurance | `.github/workflows/rll-repository-pat-assurance.yml` | none in assurance workflow |
| `CLIMA` | temporary Climate Engine read/query execution | guarded manual Actions jobs | none |

The Climate secret is bound inside the process as `CLIMATE_ENGINE_API_KEY`; that is an environment binding, not a third secret.

```text
REPOSITORY_SECRET != AGENT_SECRET
SECRET != AUTHORITY != EXECUTION != EVIDENCE != CLAIM
TOKEN_VAZIO != 0
```

## GITPAT boundary

`GITPAT` may be consumed only by the reviewed manual assurance workflow. The repository validator rejects:

- alternate/legacy PAT secret names in Actions;
- `GITPAT` outside the reviewed assurance workflow;
- non-`workflow_dispatch` secret consumption;
- mutating HTTP/API operations, git push, secret dumps, or shell tracing.

The assurance uses only `GET /user` and `GET /repos/{owner}/{repo}`. A PASS proves authentication and current-repository read only. It does **not** prove write capability, absence of every possible destructive PAT permission, or Agent availability.

## Climate boundary

`CLIMA` is a Repository Secret. A guarded job maps it to:

```text
CLIMATE_ENGINE_API_KEY
```

only in process memory. The provider bridge remains HTTPS allowlisted, bounded, sanitizes outputs, hashes the provider response, and forbids secret value/length/hash in receipts.

```text
EXTERNAL_COMPUTE_PRODUCT != PRIMARY_OBSERVATION
RESIDUAL != CAUSE
VISUALIZATION != EVIDENCE
```

## Agent / Secretary

The Secretary/Agent is a **separate authority plane**. Repository Secrets are not treated as Agent secrets and direct Agent access to `GITPAT` or `CLIMA` is not inferred.

Agents has the owner-reported candidate pair `PATGITHUB` + `CLIMATE`, exposed as environment variables. The explicit selectors are `RLL_AGENT_GITHUB_PAT_ENV` and `RLL_AGENT_CLIMATE_KEY_ENV`. `GIT` remains `TOKEN_VAZIO_ROLE` until explicitly assigned. These names do not redefine Actions bindings.

## Runtime evidence

Repository configuration is owner-declared, but runtime binding/authentication remains:

```text
GITPAT_RUNTIME = TOKEN_VAZIO_UNTIL_DISPATCH
CLIMATE_RUNTIME = TOKEN_VAZIO_UNTIL_DISPATCH
```

until the corresponding manual workflows execute and emit sanitized receipts.

## R3

- **F_ok:** two canonical Repository Secrets are unambiguous and separated.
- **F_gap:** runtime presence/authentication and intrinsic PAT scope remain external until observed.
- **F_next:** dispatch GITPAT assurance, then Climate metadata probe, then bounded timeseries/map comparison against an independently sourced RLL path.

## Mapping correction — 2026-09-14

The owner supplied the current names from the Agents and Actions settings. `CLIMA` supersedes the historical Actions name `RLL_CLIMATE_ENGINE_TRIAL_TOKEN`; the previous mapping remains in Git history and receipts. Names and provider roles remain owner-reported/candidate until runtime authentication is observed. No secret values or Settings API metadata were read during this change.

Run the [seven-guard preflight](RLL_AGENT_SEVEN_GUARDS_V1.md) before credential-backed work. The GitHub connector used to edit this repository is an independent connection; it is not evidence that an Agents or Actions secret was consumed.
