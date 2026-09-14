# RLL ARM32 Superradiance — Fork Ingress Pointer V1

**state:** OBSERVED_EXTERNAL_FORK_EVIDENCE / CANONICAL_INGRESS_POINTER  
**claim_allowed:** false  
**canonical_authority:** `instituto-Rafael/relativity-living-light`  
**source_workspace:** `rafaelmeloreisnovo/relativity-living-light`

## Source identity

Primary source object:

- repo: `rafaelmeloreisnovo/relativity-living-light`
- ref: `c8c1ba72ed27ce5f8972ffa6d80864f0e4fe8f4a`
- path: `evidence/arm32/RLL_ARM32_SUPERRADIANCE_EVIDENCE_20260817_V1.md`
- source blob SHA-1: `9887ec5fba4939bfe922ee92ef3a8174c992f210`
- event_id: `RLL-ARM32-SUPERRADIANCE-EVIDENCE-20260817-1439-BRT`

Companion ingress index in the workspace fork:

- path: `evidence/indexes/RLL_ARM32_SUPERRADIANCE_ANALYSIS_INGRESS_INDEX_V1.md`
- source blob SHA-1: `1d5306a9cf9f8b6103e54cca3e07ac049c5db7bb`

The exact evidence path was probed on both Instituto `main` and `rll/lab` before this ingress pointer was created and was not present under that path. This justifies an ingress pointer; it does **not** prove no semantically equivalent evidence exists elsewhere.

## What the source supports

The source record classifies the following as supported within its own receipt boundary:

- ARMv7-A build/link artifact reported;
- ELF32 / EABI5 identity reported;
- ARM32 machine-code disassembly reported;
- NEON instructions reported in disassembly;
- source/disassembly byte anchors recorded.

Recorded source byte anchors:

- `superradiance_kernel_minimal.c` SHA-256 `927797b6da3fda78ad1cbec006d65fece8c5dd0b15e3f11572b96c1848ad66d5`
- `integration_examples_arm32.c` SHA-256 `f23aa33497b3034926129502a4c539322bea39dbeb05ea2c7429bbb0e238edb5`
- `kernel_disasm.txt` SHA-256 `a81a74e451c334a562008bb94597e0d26b9404399ac201fe63097a423eb608f5`

## What this canonical ingress does NOT promote

The following remain fail-closed:

- QEMU runtime: `TOKEN_VAZIO`;
- physical ARM runtime: `TOKEN_VAZIO`;
- performance advantage: `TOKEN_VAZIO`;
- ARM64 equivalence: `TOKEN_VAZIO`;
- Penrose/Zeldovich/Floquet physical equivalence of BITRAF: `TOKEN_VAZIO / NOT_CLAIMED`;
- scientific preference of RLL over any baseline: not authorized.

Therefore:

`IMPLEMENTATION_EVIDENCE != PHYSICAL_EQUIVALENCE`

`DISASSEMBLY != RUNTIME`

`NEON_EMISSION != PERFORMANCE_ADVANTAGE`

`FORK_RECEIPT != CANONICAL_REPRODUCTION`

## Canonicalization rule

This pointer admits the fork evidence into the Instituto analysis graph without copying private memory payload or pretending that the fork is authoritative.

To promote from `OBSERVED_EXTERNAL_FORK_EVIDENCE` to a stronger canonical evidence state, the Instituto must independently close the relevant gates using current accessible artifacts:

1. bind source/object/linker/ELF hashes;
2. run `nm -u` / equivalent undefined-symbol check;
3. run `readelf` / equivalent ELF identity check;
4. execute under a declared ARM32 runtime or physical ARM target;
5. persist stdout/stderr/exit code and artifact digest;
6. perform baseline A/B only if claiming performance;
7. retain `claim_allowed=false` unless a separate scientific promotion gate is satisfied.

## Gap contract

### `TV-RLL-ARM32-CANONICAL-REPRODUCTION-20260827`

- `source_pointer`: fork ref/path/blob above
- `missing_field`: canonical execution/runtime reproduction
- `blocking_dependency`: accessible current ELF/object/linker artifacts or reproducible build inputs
- `evidence_needed`: exact hashes + build/link evidence + runtime receipt + exit outcomes
- `falsifier`: inability to reproduce the reported architecture/disassembly properties from the bound inputs
- `next_probe`: recover exact build inputs/artifacts and run canonical ARM32 reproduction
- `owner_authority`: `instituto-Rafael/relativity-living-light`
- `urgency`: P1
- `closure_gate`: canonical receipt independently reproduces the bounded implementation claims
- `claim_allowed`: false

## L/O/T/C/P projection

- **L:** preserves the fork event as historical predecessor rather than rewriting it.
- **O:** requires an independent Instituto reproduction axis before promotion.
- **T:** links ARM32/NEON implementation evidence to RLL strong-gravity/superradiance analysis without asserting physical identity.
- **C:** valid only for the source ref/blob and the bounded claims listed above.
- **P:** this pointer is append-only provenance; source and canonical occurrences remain distinct identities.

**F_ok:** unique path-level evidence candidate entered the canonical graph by exact source pointer.  
**F_gap:** canonical build/runtime reproduction remains open.  
**F_next:** bind build inputs/artifacts → reproduce ARM32 evidence in Instituto → receipt → only then strengthen the evidence class.
