# RLL canonical engine — ARMv7 physical gate v2

Status before execution: `TOKEN_VAZIO_ARMV7_PHYSICAL`.

This gate is intentionally separate from the geometry ARMv7 receipt. The geometry executable proves the geometry artifact; it does not execute the RLL canonical engine.

## Physical runner

`scripts/run_rll_canonical_armv7_physical_v2.sh` compiles on the target device:

- `rll_canonical_freestanding.c`;
- `rll_canonical_hz_data.c`;
- `rll_canonical_entry.c`;

then links a static ARM EABI ELF directly with LLD, audits dependencies, executes it and writes an artifact-specific receipt.

Promotion requires all of:

```text
run_exit=0
undefined_symbols=0
interpreter_segments=0
needed_entries=0
suspicious_runtime_symbols=0
receipt_line starts RLLCAN1
rows=33
valid=33
rejected=0
claim_allowed=0
numeric_flags=0
```

A PASS proves deterministic physical execution of the **33-row canonical H(z) kernel** and its pinned receipt metadata on that ARMv7 device. It does not recompute the full 1677-point joint likelihood, MCMC or nested sampling and does not change `claim_allowed=false`.

## Boundary

```text
RLL_ARMV7_OBJECT_VERIFIED = PASS historical
RLL_ARMV7_EMULATION/CROSS = PASS historical
RLL_CANONICAL_ENGINE_ARMV7_PHYSICAL = TOKEN_VAZIO until runner receipt
FULL_JOINT_PHYSICAL_RECOMPUTE = TOKEN_VAZIO
INDEPENDENT_SECOND_DEVICE_RLL = TOKEN_VAZIO
```
