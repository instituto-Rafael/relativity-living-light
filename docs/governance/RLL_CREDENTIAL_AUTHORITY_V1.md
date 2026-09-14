# RLL Credential Authority V1 — Repository Secrets × Actions × Agent Boundary

Status: `ACTIVE_GOVERNANCE`  
Scientific effect: `NONE`  
`claim_allowed=false`

## Canonical authority

The two credentials named by the repository owner are **GitHub Actions Repository Secrets**:

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

## Agent secret surface declared by owner

Copilot cloud-agent secrets are a separate authority plane: repository `GIT`; organization `CLIMATE` and `PATGITHUB`. Their names may be recorded for routing, but their values are never read, persisted, or hashed. Actions must not consume these Agent secret names. Runtime use remains `TOKEN_VAZIO_AGENT_RUNTIME` until an Agent execution receipt is observed.

## Agent / Secretary

The Secretary/Agent is a **separate authority plane**. Repository Secrets are not treated as Agent secrets and direct Agent access to `GITPAT` or `CLIMA` is not inferred.

Legacy Agent selector names remain non-canonical compatibility concepts only; they do not redefine the two repository credentials.

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
