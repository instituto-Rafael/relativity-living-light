# Receipt — RLL Q16 Split Process + Assembly Audit V3

Date: 2026-09-29
Provider run: 36506144719
Provider job: 109207925129
Tested head: 0bedd09a4f98256c032c8dd1a7510b2f86d089e0
claim_allowed: false

## Provider result

conclusion=success
PASS_MINIMAL_TOOLCHAIN
PASS_SHADOW_SOURCE_DIAGNOSTIC
PASS_NO_UNDEFINED_OR_DYNAMIC_RUNTIME
TAIL_POLICY=PASS_FNO_OPTIMIZE_SIBLING_CALLS
PASS_SPLIT_PROCESS_RECOVERY
PASS_HASH_FREEZE
PASS_ARMV7_SPLIT_OBJECTS

Recovery output:
RLLRECOVERYQ16V3 best=1311,65536,19661 grid_evals=1782 claim_allowed=0

Transport:
MATRIX_BYTES=132

## Frozen SHA-256

generator_source = 51970b8d1352198a63884c6deddf869d90759631f49b78897d4bf256a1059689
recovery_source  = 70eac05757364c9ac2356c59a6a69456b581969c8106b73912afeb8dd430cd39
generator_elf    = f06d68438bbb5312831cdab7e8b15a85ea7b4df794107e7878feb671b66ab462
recovery_elf     = f2a6e39fadc97e5c0866735e6a4ab3708dc8c2e6f25a1d85e31c821ee589c522
matrix_q16       = 406d13ea9a5ad10af3629a01d2df9af4ca8bd667ac0f2192c00324262658ab94

## Separation evidence

The generator and recovery are separate static x86_64 ELF processes. The only generator-to-recovery payload is the 132-byte raw Q16 matrix. No parameter metadata is transported.

Recovery reproduced best=1311,65536,19661 over 1782 grid cells.

## Tail / shadow evidence

Both sources compile under -Wshadow -Werror.
Both sources compile under -fno-optimize-sibling-calls.
Both static ELFs pass the no-undefined/no-dynamic-runtime audit.
Binary symbol audit rejects stack_chk, shadow, malloc, free, printf and libc matches.

This supports MINIMIZED_AND_GATED tail/shadow state, not an absolute ZERO_TAIL/ZERO_SHADOW claim.

## ARMv7

PASS_ARMV7_SPLIT_OBJECTS
ARMV7_STATIC_LINK=TOKEN_VAZIO_TOOLCHAIN_LINKER
ARMV7_PHYSICAL_EXECUTION=TOKEN_VAZIO

## Boundary

SEPARATE_EXECUTABLES != INDEPENDENT_SCIENTIFIC_REIMPLEMENTATION
CROSS_COMPILED_OBJECT != PHYSICAL_ARM_EXECUTION
SYNTHETIC_RECOVERY != HELD_OUT_REAL_DATA_VALIDATION
claim_allowed=false

## R3

F_ok = V2 merged + generator/recovery process split + 132-byte raw matrix boundary + exact recovery PASS + source/ELF/matrix SHA-256 freeze + shadow compiler gate + sibling/tail optimization disabled + ARMv7 split objects PASS.

F_gap = ARMv7 static link + physical moto e7 execution + independently authored recovery implementation + held-out real-data discrimination.

F_next = reproduce these source hashes on physical ARMv7; freeze resulting ARM ELF hashes and device receipt; then build a second recovery implementation that does not copy the canonical numerical primitive implementation.
