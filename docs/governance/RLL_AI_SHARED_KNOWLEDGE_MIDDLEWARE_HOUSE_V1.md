# RLL AI Shared Knowledge Middleware House V1

Date: 2026-09-20  
State: GOVERNED_DRAFT  
Claim effect: none; `claim_allowed=false`.

## Intent

Connect the RLL repository to the RAFAELIA Drive middleware house so human operators and heterogeneous AI clients can exchange bounded work through explicit source, authority, artifact, execution, evidence, uncertainty, and receipt references.

This is a routing and governance layer. It does not move scientific algorithms into YAML and does not make Drive a runtime executor.

## Drive topology

House:

- <https://drive.google.com/drive/folders/1Iza50dV_x13I7amR9gi-y-4qGhoFLxYF>

Router:

- <https://docs.google.com/document/d/1--DKx1FVwkDITpG0tAUS-foOy-oHkx4aqaCo_fOmWgg/edit>

Shared AI contract:

- <https://docs.google.com/document/d/1ahJW3e7bCdrlqsl4vVk4IL5HvuRaNUEJPOFGNp72dh0/edit>

Parent architectural source:

- <https://docs.google.com/document/d/1cVvVhOUedHtCc2C72rLRLPCjcEH2gTmfw1FkMrrVRlw/edit>

The Drive house is located under:

`13_ORQUESTRADOR_FRONTAL__PRODUTOS_MODULOS_SYSLOG/05_MIDDLEWARE_CHAT_TERMINAL_E_APIS`.

Its zones are:

1. START HERE / tree.
2. agent and AI contracts.
3. inbox/uploads/handoffs.
4. sources/articles/papers.
5. bounded AI/RLL workspaces.
6. uncertainty/coherence/contradictions.
7. artifacts/receipts/evidence.
8. Six Sigma continuous evolution.
9. Drive/GitHub routing links.

The existing `08_LEDGER_DE_PROCEDIMENTOS_MARCOS_E_CONDICOES` remains the process/evidence ledger; the house does not replace it.

## Repository topology

Repository coordination is declared by:

- `/AGENTS.md`: human/agent operating contract.
- `data/governance/RLL_AI_SHARED_KNOWLEDGE_MIDDLEWARE_HOUSE_V1.yml`: machine-readable routing contract.
- this document: implementation-facing rationale and boundaries.

Existing producer-specific workflows and scientific modules remain authoritative for their implementation domains.

## Middleware invariant

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
```

The middleware transports references and state transitions. It must not promote a claim because several agents agree or because a document exists.

## Handoff semantics

A handoff is a bounded transition between actors/clients. It should preserve:

```text
human intent
source refs
authority
workspace
inputs
expected outputs
uncertainties
contradictions
artifact refs
execution refs
receipt refs
claim boundary
F_ok / F_gap / F_next
parent/supersedes
hash/ref
```

Large corpora should be referenced rather than copied unless the task requires a materialized derivative.

## Multi-agent work

Named clients can include ChatGPT, Claude, RAFAELIA, RLL tooling, or future agents.

Rules:

- a client name never grants authority;
- a client may have only the tools actually available in its active session;
- one agent's narrative is not evidence for another;
- disagreement becomes a typed relation, not deleted noise;
- agreement without materially independent evidence is not independent replication;
- unknown client/tool metadata remains `TOKEN_VAZIO`.

## Knowledge lifecycle

```text
INTENT
→ SOURCE/AUTHORITY
→ INBOX/HANDOFF
→ CLASSIFY
→ WORKSPACE
→ RELATE/CONTRAST
→ UNCERTAINTY
→ EXECUTE IN PRODUCER
→ ARTIFACT
→ EVIDENCE/RECEIPT
→ DMAIC CONTROL
→ INDEX/ROUTE
→ R3
```

## Entropy and continuous evolution

The middleware may classify operational entropy through measurable signals such as:

- duplicate objects without a canonical pointer;
- contradictions without typed relation;
- orphan artifacts without source/provenance;
- `TOKEN_VAZIO` without evidence-needed/next gate;
- stale links or schema drift;
- unbounded workspaces;
- claims not tied to evidence.

Progress must not be defined as merely reducing the number of open items. Revealing a real contradiction can increase local complexity while improving knowledge.

Useful uncertainty maturation:

`UNSCOPED → CLUSTERED → TYPED → SOURCE_BOUND → METHOD_BOUND → EVIDENCE_BOUND → CLAIM_BOUND`.

## Six Sigma usage

DMAIC is used as a quality-control method:

- Define — intent, CTQ, scope, authority, risk.
- Measure — source state, baseline, coverage, contradictions, gaps.
- Analyze — causal/dependency structure, uncertainty and process entropy.
- Improve — smallest reversible high-value delta.
- Control — tests, receipts, hashes/refs, indexes, rollback/supersession.

No statistical sigma-level claim is authorized without measured process capability data.

## Upload path

```text
UPLOAD
→ INBOX
→ identify source/MIME/time/hash when available
→ classify
→ deduplicate/reference
→ route
→ transform
→ verify
→ evidence/receipt
→ archive/supersede
```

Original source material should remain preserved when possible. Derived objects point to their source.

## Failure semantics

- missing value → `TOKEN_VAZIO`;
- structural execution success → not scientific confirmation;
- unavailable external authority → blocked/external dependency;
- contradiction → append typed contradiction, do not erase predecessor;
- correction → append successor/supersedes.

## R3

`F_ok`: the Drive house and repository contracts are materialized.  
`F_gap`: runtime interoperability across independent AI providers remains dependent on each provider/session's actual connector/tool access.  
`F_next`: validate YAML/Markdown/AGENTS contracts in CI and then use one real upload/handoff as the first bounded end-to-end specimen.
