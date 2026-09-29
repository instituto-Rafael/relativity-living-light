# RLL Non-null Split Binary Q16 V3

State: PASS_PROVIDER_SPLIT_BINARY / ARMV7_PHYSICAL_TOKEN_VAZIO
claim_allowed: false

## What changed

V2 proved the one-binary low-level recovery gate. V3 separates production from recovery:

generator -> canonical RLF1 fixture bytes -> recovery

The generator owns the injection. The recovery sees only the 33 Q16 observations plus its frozen search manifold. It has no generator mode and no expected-result comparison.

## Low-level invariants

- one translation unit per executable
- no hosted headers
- no libc/stdlib/stdio/string/math
- no heap/malloc/free/GC
- no structs/classes/function pointers
- no runtime filesystem API
- direct syscall I/O
- Q16.16 only
- static provider ELF
- -Wshadow -Werror=shadow
- -fno-optimize-sibling-calls

## Provider evidence

run=36505526162
job=109205987964
tested_head=887c7b91b2c0309d75852955ebb97caa233dac9e

Exact recovery: 1311,65536,19661, score_q16=0
Stress recovery: 1311,65536,21299, score_q16=4129
Null recovery: Omega_s0=0, score_q16=0

generator_named_tail_branches=0
recovery_named_tail_branches=0

Source hashes:
generator=94c0846f1b35860e7ca4b7a6b629850cbdd3ae7e9924155e2011c48f8c88e7b7
recovery=83d01759bef5ac1e896850f9e882eaeeb41a820ec6b2e1bb4d50ff0713f3cc56

## Physical ARMv7

Materialized runner:
scripts/run_rll_nonnull_split_armv7_physical_v3.sh

It is designed for the existing Termux ARMv7 physical execution surface and emits a hash-bound physical receipt.

Current state:
ARMV7_PHYSICAL_EXECUTION=TOKEN_VAZIO

That state is intentionally not promoted from the provider ARM object build.

## Boundary

BINARY_SEPARATION_PASS != INDEPENDENT_REIMPLEMENTATION
PROVIDER_PASS != PHYSICAL_ARMV7_PASS
SYNTHETIC_RECOVERY != HELD_OUT_REAL_DATA
LOW_LEVEL_EXECUTION != COSMOLOGICAL_VALIDATION

## Next

Run the exact V3 physical runner on the moto e7/ARMv7, ingest the resulting receipt, compare provider and physical outputs byte-for-byte, and only then move the same frozen operator to held-out observational data.
