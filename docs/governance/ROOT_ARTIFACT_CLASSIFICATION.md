# Root Artifact Classification

Status: `governance_record / operational_control_layer`

Purpose: classify loose root-level artifacts without moving, deleting, renaming, or changing their scientific content. This document is an operational index only; it does not validate RLL, alter equations, or promote any artifact to real-data evidence.

## Allowed classes

| Class | Meaning |
|---|---|
| `canonical_entrypoint` | A root file that intentionally guides users toward repository navigation or primary context. |
| `validation_artifact` | A validation plan, status, protocol, or evidence-routing artifact. |
| `governance_record` | A repository organization, migration, audit, or decision record. |
| `legacy_mirror` | A preserved copy or mirror retained for continuity or historical traceability. |
| `raw_authorial` | Author-originated conceptual, mathematical, multilingual, or exploratory material preserved as source expression. |
| `operational_config` | A root-level configuration file used by automation or validation routing. |
| `audit_pending` | A root artifact whose final purpose, provenance, or canonical destination remains unresolved. |

## Classification table

| Root artifact | Class | Operational handling |
|---|---|---|
| `CAMINHOS_VALIDACAO_NOVOS.yml` | `operational_config` | Keep at root until validation routing is consolidated; treat as automation/config input, not as scientific proof. |
| `COMPREHENSIVE_REPOSITORY_ANALYSIS.md` | `governance_record` | Preserve as repository-level analysis and migration context. |
| `FALSIFIABILITY_PROTOCOL.md` | `validation_artifact` | Treat as a falsifiability/claim-boundary protocol; do not use it to declare validation without real-data metrics. |
| `GOVERNANCE_REORG_DRAFT.md` | `governance_record` | Treat as a draft governance/reorganization record until superseded by a canonical governance index. |
| `VALIDATION_STATUS.md` | `validation_artifact` | Treat as validation-status routing; status language must remain bounded by current evidence. |
| `NEXT_RLL_VALIDATION_STEP.md` | `validation_artifact` | Treat as next-action guidance for validation, not as completed validation. |
| `Matemática.md` | `raw_authorial` | Preserve as authorial mathematical material; do not normalize or relocate in this control PR. |
| `MathRaf.md` | `raw_authorial` | Preserve as authorial mathematical/conceptual material under future provenance review. |
| `Numprimod.md` | `raw_authorial` | Preserve as authorial numerical/prime-number material under future provenance review. |

## Control rules

- Do not move or delete classified root artifacts as part of this document.
- Do not change scientific equations when classifying artifacts.
- Do not infer that a classified artifact is validated real-data evidence.
- Use this table as a lightweight routing layer for future cleanup, inventory, and governance PRs.

## Physical refactor Wave 2 — 2026-09-29

START HERE authority for this repository now routes through `docs/presentation/00_START_HERE_RLL.md` as `Ω V2.1 DISPATCH`.

### Wave 2A — legacy bodies

| Root stub | Destination | State |
|---|---|---|
| `Códex1.md` | `docs/legacy/root/prompts/Códex1.md` | body moved, stub retained |
| `Codex2.md` | `docs/legacy/root/prompts/Codex2.md` | body moved, stub retained |
| `Provaw.md` | `docs/legacy/root/experiments/Provaw.md` | body moved, stub retained |
| `Toadd01.md` | `docs/legacy/root/prototypes/Toadd01.md` | body moved, stub retained |
| `docs_toroidal_knowledge.md` | `docs/legacy/root/concepts/docs_toroidal_knowledge.md` | body moved, stub retained |
| `Rsfael` | `docs/legacy/root/raw/Rsfael.txt` | text/plain identified; body moved; stub retained |

### Wave 2B — active validation routes

| Root stub | Destination | State |
|---|---|---|
| `RLL_REAL_VALIDATION_PROMPT.md` | `docs/validation/prompts/RLL_REAL_VALIDATION_PROMPT.md` | active content moved, stub retained |
| `RLL_REAL_VALIDATION_REPORT_TARGET.md` | `docs/validation/targets/RLL_REAL_VALIDATION_REPORT_TARGET.md` | active content moved, stub retained |
| `RLL_WANDERING_BLACK_HOLE_TEST.md` | `docs/validation/cases/RLL_WANDERING_BLACK_HOLE_TEST.md` | active content moved, stub retained |

Physical movement does not change scientific/epistemic status. Git blob preservation is verified by the dedicated Wave 2 gate before promotion.
