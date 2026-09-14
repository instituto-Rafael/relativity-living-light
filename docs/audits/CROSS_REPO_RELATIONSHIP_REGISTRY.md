# Cross-Repo Relationship Registry

## Status

`v2_measured_entrelace / evidence_gated / no_claim_promotion / fail_closed`

## Purpose

This registry preserves useful relationships among repositories without treating documentation proximity as executable integration or scientific confirmation.

The machine-readable layers are:

```text
knowledge_ecosystem/session_operating_system.yml
  -> broad session/source/concept/operation routing

knowledge_ecosystem/rll_cross_repo_entrelaces_v2.json
  -> narrow measured relationships with exact repo/ref/path/blob SHA

results/session_grafo_fase17_20/current_state_overlay.json
  -> temporal synchronization of the historical FASE17-20 graph with FASE22
```

Validation is performed by:

```text
tools/validate_session_operating_system.py
tools/validate_rll_cross_repo_entrelaces.py
scripts/build_session_grafo_current_state_overlay.py --check
```

The v2 layer does not fetch or modify another repository. It records the exact source read, the bounded fact proven, what remains unproven, the required artifact, the next action and rollback.

## Repositories in scope

```text
instituto-Rafael/relativity-living-light
rafaelmeloreisnovo/papers
rafaelmeloreisnovo/ChipQuantum
rafaelmeloreisnovo/termux-app-rafacodephi
rafaelmeloreisnovo/Cosmos
rafaelmeloreisnovo/TeoremasTesesTeorias
rafaelmeloreisnovo/GAIA_phi
rafaelmeloreisnovo/RafPolimata
rafaelmeloreisnovo/Rafaelia_Private
rafaelmeloreisnovo/RafCoder
rafaelmeloreisnovo/Vectras-VM-Android
```

Names or paths not directly read remain `DECLARED_BY_AUTHOR`, `HYPOTHESIS`, `PARTIAL`, `BLOCKED` or `TOKEN_VAZIO`.

## State vocabulary

```text
VERIFIED             evidence located and independently checked in its domain
VERIFIED_LIMITED     exact evidence located for a narrow structural behavior
DECLARED_BY_AUTHOR   declared but not independently verified here
HYPOTHESIS           plausible relationship requiring an artifact or test
PARTIAL              some evidence exists, but the chain is incomplete
TOKEN_VAZIO          required evidence is absent or not located
BLOCKED               a named prerequisite prevents validation
CLAIM_BLOCKED         promotion is prohibited without evidence/test/artifact
CONTRADICTION         evidence conflicts with the claim
ROLLBACK              previous safe state or reversal action
```

## Current measured entrelaces v2

| ID | Relationship | Current state | What is proven | Required next artifact |
|---|---|---|---|---|
| `RLL-RP-FORMAL-001` | RLL ↔ RafPolimata formal method | `VERIFIED_LIMITED` | Both define the same promotion direction: definition → units → model → data → uncertainty → falsifier → bounded claim | one dual-validated `rll.formal_experiment_manifest.v1` |
| `RLL-CQ-RUNTIME-001` | RLL ↔ ChipQuantum runtime evidence | `VERIFIED_LIMITED` | Both define compatible fields for source/binary hash, compiler, flags, equation IDs, dataset, uncertainty and verdict | one float64/fixed-point runtime evidence pair |
| `RLL-GAIA-LEDGER-001` | RLL ↔ GAIA claim ledger | `VERIFIED_LIMITED` | Both preserve claim→repo→path→evidence→test→state→next action and TOKEN_VAZIO | pointer-only import receipt, without payload mutation |
| `RLL-VECTRAS-DEVICE-001` | RLL ↔ Vectras device/QEMU layer | `BLOCKED` | Responsibility boundary and documentation stage are explicit; Vectras remains `BETA_BLOCKED` | current APK manifest + real-device/QEMU smoke artifact |
| `RLL-TERMUX-PROVENANCE-001` | RLL ↔ Termux provenance | `PARTIAL` | RLL defines acceptable provenance; Termux fork has pinned source/ABI contract | one original historical artifact chain command→input→output→hash |

Machine detail, exact blob SHAs, explicit non-proven claims and rollback are in `knowledge_ecosystem/rll_cross_repo_entrelaces_v2.json`.

## Urgent surgery state

### G4 temporal inconsistency

The FASE17–20 graph correctly recorded G4 as `TOKEN_VAZIO` at the end of FASE20. FASE22 later quantified the bias and closed the unknown gap as a limited systematic result. Both facts are preserved:

```text
G4 at snapshot FASE20 = TOKEN_VAZIO
G4 through FASE22      = VERIFIED_LIMITED / CLOSED_AS_QUANTIFIED_SYSTEMATIC
residual precision     = TOKEN_VAZIO (CAMB/RECFAST at each MCMC point)
```

The current state is attached through `current_state_overlay.json`; the historical graph is not rewritten as if FASE22 had already happened.

### Runtime evidence

No external runtime manifest has yet been imported into the RLL graph. Documentation compatibility is not runtime execution.

### Historical mobile provenance

Current Termux infrastructure cannot retroactively prove that early RLL artifacts were generated on the author's phone. One original artifact chain must be located first.

## Historical beta relationship table

The following entries remain useful as candidate routes. Their original state is preserved unless superseded by the v2 measured registry.

| ID | Relationship | State | Safe reading | Blocked claim | Next verification |
|---|---|---|---|---|---|
| RLL-CQ-001 | RLL may export numerical payloads to ChipQuantum | HYPOTHESIS | Candidate data-contract route | RLL already feeds a verified kernel | Verify actual consumer schema in ChipQuantum |
| RLL-CQ-002 | Q16.16 may be a numeric bridge | HYPOTHESIS / CLAIM_BLOCKED | Possible fixed-point interface | Q16.16 conversion must be implemented now | Define scale/range/overflow after checking code/tests |
| RLL-CQ-003 | Attractor count 42 may be a shared conceptual invariant | DECLARED_BY_AUTHOR | Cross-repo invariant candidate | 42-attractor implementation is complete | Verify table, reachability, tests and build logs |
| CQ-TX-001 | ChipQuantum binaries may run under Termux/mobile | HYPOTHESIS | Runtime integration candidate | Mobile execution is validated | Verify build artifact, ABI, loader and runtime logs |
| TX-RLL-001 | Termux/mobile logs may feed RLL audit | HYPOTHESIS | Feedback/attestation route | Mobile result validates RLL | Define log schema, checksum and ingestion path |
| RLL-DATA-001 | Missing legacy path blocks one calc-data route | VERIFIED_LIMITED | Guarded input behavior | Missing file proves data failure | Keep allowlist and intended input policy explicit |
| RLL-DATA-002 | Synthetic fallback may help beta tests | CLAIM_BLOCKED | Explicitly synthetic testing only | Synthetic output satisfies real-data validation | Keep it outside real-data claim paths |
| RLL-VEC-001 | RLL owns science while Vectras may own freestanding runtime | HYPOTHESIS | Candidate architecture split | ARM/device execution is already confirmed | Require build, device and rollback artifacts |
| RLL-VEC-002 | Cosmology pivot belongs to RLL; Vectras may reference constants | HYPOTHESIS | Responsibility boundary | Pivot is a validated discovery | Link to RLL source and preserve claim boundary |
| RLL-VEC-003 | Removed Vectras coverage must remain represented in RLL | CLAIM_BLOCKED | Migration path candidate | Removed tests need no replacement | Compare removed tests to RLL contracts |
| RLL-VEC-004 | Failed real-data CI blocks promotion of pivot results | CLAIM_BLOCKED | CI failure is a blocker | CI failure is a scientific finding | Resolve the actual gate first |
| SES-RLL-001 | RLL is the first scientific body in a wider session | DECLARED_BY_AUTHOR / CLAIM_BLOCKED | Reading order and scope | Every domain is physically unified | Verify each relation by source, units and falsifier |
| RLL-PAP-001 | Public RLL may point to private papers without copying them | VERIFIED_LIMITED | Pointer-only boundary | Public RLL contains the private corpus | Keep formulas and raw sessions private |
| PAP-ML-001 | Private papers contain several engine/research families | VERIFIED_LIMITED | Selected paths were read | Every engine is tested or validated | Verify build/test/ABI/formula-to-code links |
| RLL-PHO-001 | Photonic, magnetic, acoustic and plasma mechanisms may share formal patterns | HYPOTHESIS / CLAIM_BLOCKED | Cross-scale comparison candidate | They are one physical phenomenon | Define carrier, medium, scale, units and falsifier |
| SES-GPT-001 | Session groups may be indexed as an evolving interaction | HYPOTHESIS / CLAIM_BLOCKED | Contextual organization method | Hidden model metadata was reconstructed | Use only supplied/exported pointers |
| RLL-KOS-001 | Session OS links sources, concepts, operations and states | VERIFIED_LIMITED | Machine organizational contract | It proves integration or truth | Validate generated audit and one narrow relation |
| PRIV-001 | Private repositories are public pointers only | VERIFIED_LIMITED | Structural disclosure boundary | Public registry may copy private bodies | Keep validators fail-closed |

## Implantation policy

A relationship can become an issue, code change, workflow or test only when it has:

```text
owner repository
exact ref/path/blob SHA
state and scope
reproduction or citation
required artifact
safe next action
claim boundary
rollback
```

## Safe operator workflow

```text
1. Choose one relationship ID.
2. Read the owning files at the recorded blob SHAs.
3. Produce the smallest missing artifact.
4. Run the local validator and repository-native test.
5. Store hashes and limitations.
6. Update the registry state without deleting negative history.
7. Open a draft PR; merge only after the local gate is green.
```

## Do not do

```text
Do not treat the registry as proof of working integration.
Do not use it to claim production readiness.
Do not use RLL prose alone to change another repository's behavior.
Do not satisfy real-data gates with synthetic fixtures.
Do not convert hypotheses into bugs without verification.
Do not copy private session text or formulas into the public registry.
Do not create a competing orchestration workflow when the existing validator can be extended.
Do not allow a failover, checksum or deterministic execution to validate physics.
```

## Final boundary

The registry improves auditability and provides a surgical queue. It does not validate RLL, private papers, ChipQuantum, Termux, Vectras, hardware execution, GPT internals or cross-domain physical unification. `claim_allowed=false` remains the global boundary.
