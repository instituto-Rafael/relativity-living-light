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
suspicious_undefined_runtime_symbols=0
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


## Runtime-helper audit hardening

The canonical physical runner was corrected in commit
`45b1ec7bdef74a7a4d5a8f4cf9cb5f58cd25932d`.

The previous grep scanned all ELF symbols and could theoretically confuse an internal function whose name contains `sqrt` with a forbidden external dependency. The hardened gate scans only undefined/imported symbols:

```text
nm -u ELF -> suspicious runtime-helper filter
```

This is stricter semantically: external runtime helpers remain forbidden, while legitimate internal fixed-point routines are not mislabeled.

The independent hard gate `undefined_symbols=0` remains unchanged.


## Exact canonical receipt pinning

The physical runner was further hardened in commit
`75e9fc8e7a3c8401b38703caa7b66f750f365cf9`.

Promotion now requires the complete emitted `RLLCAN1` line to match the canonical expected line byte-for-byte after command-substitution newline normalization. This binds the physical run to the declared Q16 χ² values, data hashes, parameter/phase hashes, pinned joint summary, `claim_allowed=0`, `token_vazio=7`, and `numeric_flags=0`.

The receipt records both the expected-line SHA-256 and the observed stdout SHA-256. Structural gates remain mandatory in parallel; exact line matching does not replace ELF/dependency auditing.
