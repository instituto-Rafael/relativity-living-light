# AGENTS.md — RLL Shared Knowledge Middleware

Status: GOVERNED_DRAFT  
Scope: repository-wide coordination for human operators, ChatGPT, Claude, RAFAELIA, RLL agents, and compatible future clients.  
Scientific effect: NONE.  
Default: `claim_allowed=false`.

## Human authority

Human intent is the root authority. An AI/agent may adapt routing inside the authorized goal but must not create an autonomous goal or silently broaden scope.

## Canonical separation

`SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`.

`TOKEN_VAZIO` is a valid state. Never fill a missing value only to complete a schema.

## Shared Drive house

Canonical middleware house:

https://drive.google.com/drive/folders/1Iza50dV_x13I7amR9gi-y-4qGhoFLxYF

Drive router document:

https://docs.google.com/document/d/1--DKx1FVwkDITpG0tAUS-foOy-oHkx4aqaCo_fOmWgg/edit

Shared AI contract:

https://docs.google.com/document/d/1ahJW3e7bCdrlqsl4vVk4IL5HvuRaNUEJPOFGNp72dh0/edit

Parent architectural source:

https://docs.google.com/document/d/1cVvVhOUedHtCc2C72rLRLPCjcEH2gTmfw1FkMrrVRlw/edit

## Source authority

- Drive: documentary memory, source collections, papers, uploads, indexes, receipts, reconstruction.
- GitHub: code, schemas, specs, tests, workflows, CI, and producer implementation authority.
- Runtime execution evidence outranks narrative claims about runtime state.
- A Drive or GitHub link is a locator, not scientific evidence by itself.

## Work item lifecycle

```text
INTENT
→ SOURCE/AUTHORITY
→ INBOX/HANDOFF
→ CLASSIFY
→ WORKSPACE
→ RELATE/CONTRAST
→ UNCERTAINTY
→ EXECUTE IN AUTHORIZED PRODUCER
→ ARTIFACT
→ EVIDENCE/RECEIPT
→ 6Σ CONTROL
→ INDEX/ROUTE
→ R3
```

## AI handoff envelope

For meaningful cross-agent work, preserve or emit:

- `handoff_id`
- `timestamp`
- `client_name`
- `session_or_ref`
- `human_intent`
- `source_refs[]`
- `authority`
- `workspace`
- `inputs[]`
- `expected_outputs[]`
- `claim_allowed`
- `evidence_required[]`
- `uncertainties[]`
- `contradictions[]`
- `artifact_refs[]`
- `execution_refs[]`
- `receipt_refs[]`
- `F_ok`
- `F_gap`
- `F_next`
- `parent_or_supersedes`
- `hash_or_ref`

Unknown client/tool metadata remains `TOKEN_VAZIO`; do not infer it.

## Typed relations

Use explicit relations where applicable:

- `AGREES_WITHIN_SCOPE`
- `TENSION`
- `CONTRADICTED_BY_EVIDENCE`
- `ORTHOGONAL`
- `INSUFFICIENT_COMPARABILITY`
- `DERIVES_FROM`
- `REPRODUCES`
- `SUPERSEDES`
- `TOKEN_VAZIO_RELATION`

Agreement among agents is not independent replication unless the evidence path is materially independent.

## Upload handling

New uploads enter the Drive middleware INBOX before becoming canonical source material.

```text
UPLOAD → INBOX → IDENTIFY → CLASSIFY → DEDUP/REFERENCE
→ ROUTE → TRANSFORM → VERIFY → EVIDENCE/RECEIPT
→ ARCHIVE/SUPERSEDE
```

Preserve originals where possible. Derived artifacts must point to source/hash/ref.

## 6Σ / DMAIC continuous evolution

Use Six Sigma as process discipline, not as a statistical sigma-level claim unless process metrics justify that claim.

- DEFINE: intent, CTQ, scope, authority, risk.
- MEASURE: sources, baseline, coverage, gaps, contradictions.
- ANALYZE: causes, dependencies, entropy, incoherence, uncertainty.
- IMPROVE: smallest reversible high-value delta.
- CONTROL: tests, receipt, hash/ref, index, rollback/supersession.

Valid uncertainty maturation includes:

`UNSCOPED → CLUSTERED → TYPED → SOURCE_BOUND → METHOD_BOUND → EVIDENCE_BOUND → CLAIM_BOUND`.

A new contradiction can increase local entropy while increasing knowledge. Never hide that delta.

## Mutation boundary

Before writing: resolve authority, source, destination, scope, and rollback/supersession path.

After writing: produce observable evidence/receipt and a routing/index pointer.

Corrections append a successor or superseding record; do not erase history silently.

## Claim gate

Default: `claim_allowed=false`.

Coherence alone never promotes a scientific claim. Promotion requires the evidence required by the applicable domain contract.

## Meaningful cycle close

Close significant work with:

`R3 = <F_ok, F_gap, F_next>`.

Where:

- `F_ok`: observed or implemented state supported by evidence.
- `F_gap`: unresolved uncertainty, contradiction, dependency, or blocker.
- `F_next`: smallest high-value verifiable next gate.

This file coordinates agents; it does not assert that any named AI provider automatically has access to the linked Drive or repository. Access depends on the active authorized session and tools.
