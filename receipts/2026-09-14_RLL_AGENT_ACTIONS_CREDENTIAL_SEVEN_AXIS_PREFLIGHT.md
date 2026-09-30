# RLL Agent × Actions Credential Seven-Axis Receipt — 2026-09-14

Status: `IMPLEMENTED_UNTESTED`
Scientific effect: `NONE`
`claim_allowed=false`

## Source / authority

- repository: `instituto-Rafael/relativity-living-light`
- base: `rll/lab@2a6e80ad0efa182217aa76c55665a4c98a4e5523`
- owner-declared Copilot Agent secret names: repository `GIT`; organization `CLIMATE`, `PATGITHUB`
- owner-declared GitHub Actions repository secret names: `CLIMA`, `GITPAT`
- secret values: `NOT_READ / NOT_STORED / NOT_HASHED`

Names are routing metadata only. No secret value is evidence or repository authority.

## Seven-axis guard

| Axis | State | Receipt |
|---|---|---|
| provenance | IMPLEMENTED | canonical repo, policy, base ref and credential workflows recorded |
| context | IMPLEMENTED | Agent and Actions are separate authority planes |
| evidence | TOKEN_VAZIO_RUNTIME | static code/policy changed; runtime secret binding/authentication not yet observed |
| contradiction | RESOLVED_IN_CODE_PENDING_CI | previous Actions Climate name differed from owner-declared `CLIMA`; consumers now map `secrets.CLIMA` to process-local Climate binding |
| uncertainty | OPEN | Agent runtime, org inheritance scope, PAT intrinsic permissions and live provider authentication remain external/runtime state |
| reproduction | READY | run credential validator/unit tests and manual read-only dispatches |
| rollback | READY | revert this branch/PR only; preserve historical receipts and prior credential declarations |

## Invariants

```text
AGENT_SECRET != ACTIONS_SECRET
SECRET != AUTHORITY != EXECUTION != EVIDENCE != CLAIM
SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM
TOKEN_VAZIO != 0
```

Historical receipts are not rewritten.

## μWRITE

```text
μID=RLL-CRED-7AXIS-20260914-001|timestamp=2026-09-14T17:10:00Z|source/ref=owner-declaration+github:rll/lab@2a6e80ad0efa182217aa76c55665a4c98a4e5523|parent=RLL_CREDENTIAL_AUTHORITY_V1|kind=credential-surface-governance|Δsummary=separate Copilot Agent(GIT,CLIMATE,PATGITHUB) from Actions(CLIMA,GITPAT); emit provenance/context/evidence/contradiction/uncertainty/reproduction/rollback in sanitized credential receipt|routes(P,C,R,I,E)=credential-policy,workflow-contract,agent-authority,runtime-probes,tests|evidence=IMPLEMENTED_UNTESTED|gap=runtime dispatch + Agent runtime + org inheritance|next=PR CI then separate manual probes|hash/ref=TOKEN_VAZIO_UNTIL_COMMIT
```

R3 = <F_ok: code/policy surfaces aligned and no secret material persisted; F_gap: runtime evidence absent; F_next: CI, then manual GITPAT and CLIMA probes separately, then Agent runtime receipt separately>.
