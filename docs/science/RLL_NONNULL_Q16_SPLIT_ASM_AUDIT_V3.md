# RLL Non-null Q16 — Split Process + Assembly Audit V3

Date: 2026-09-29
State: IMPLEMENTED_UNTESTED
claim_allowed: false

## Delta

V2 proved one static x86_64 ELF and one ARMv7 freestanding object. V3 removes the same-process generator/recovery coupling.

Two standalone translation units now exist:

- core/lowlevel_runtime/c/rll_nonnull_q16_generator_freestanding.c
- core/lowlevel_runtime/c/rll_nonnull_q16_recovery_freestanding.c

The generator writes exactly 33 signed Q16.16 observations (132 bytes) to stdout. The recovery executable reads exactly 132 bytes from stdin and receives no injected parameter metadata.

Transport:

generator ELF -> raw 132-byte Q16 matrix -> recovery ELF

No JSON, text parser, runtime filesystem, heap, malloc, libc or dynamic loader is introduced.

## Tail policy

Both binaries are compiled with -fno-optimize-sibling-calls. This disables compiler sibling/tail-call optimization for this gate. It does not mean all machine-code jumps disappear, so the state is MINIMIZED_AND_GATED rather than ZERO_TAIL.

## Shadow policy

Both sources are compiled with -Wshadow -Werror. The binary audit also rejects symbols matching stack_chk, shadow, malloc, free, printf or libc. This establishes a bounded source/runtime shadow gate; it is not a universal claim about every possible meaning of shadow state.

## Artifact freeze

The gate emits SHA-256 for both source files, both x86_64 static ELFs, and the 132-byte matrix. Those hashes are execution evidence only after provider completion.

## ARMv7

The same two sources are cross-compiled to separate ELF32 ARM objects and audited for undefined symbols. Static ARM link and physical moto e7 execution remain TOKEN_VAZIO until observed.

## Independence boundary

SEPARATE_PROCESS_ADDRESS_SPACES = intended and testable here.
SEPARATE_EXECUTABLE_ARTIFACTS = intended and testable here.
INDEPENDENT_SCIENTIFIC_REIMPLEMENTATION = false.

The two sources derive from the same canonical RLL numerical primitives. Therefore V3 improves execution separation but does not yet constitute independent scientific replication.

## R3

F_ok = V2 merged + generator/recovery source split + raw matrix transport + tail optimization disabled + shadow warnings promoted to errors.

F_gap = provider execution + frozen hashes + ARMv7 static link + physical moto e7 execution + independently authored numerical reimplementation + held-out real-data discrimination.

F_next = run provider V3 -> record exact hashes/assembly evidence -> execute the frozen sources on physical ARMv7 -> only then create a separately implemented recovery kernel for independent replication.
