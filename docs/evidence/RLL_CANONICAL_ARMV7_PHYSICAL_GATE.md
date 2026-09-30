# RLL canonical engine — ARMv7 physical gate

This gate is artifact-specific. Geometry Q16 receipts are not accepted as evidence for this executable.

The runner:
- compiles the canonical H(z) freestanding kernel on the physical ARMv7 Termux device;
- links a static ARM EABI ET_EXEC;
- audits undefined symbols, PT_INTERP, DT_NEEDED and suspicious runtime helpers;
- executes the ELF;
- requires byte-for-byte canonical receipt-line equality;
- requires `claim_allowed=0` and `numeric_flags=0`;
- writes an artifact-specific physical receipt.

Run from repository root:

```bash
chmod +x scripts/run_rll_canonical_armv7_physical_gate.sh
./scripts/run_rll_canonical_armv7_physical_gate.sh
```

Current state before a physical device run:

```text
RLL_CANONICAL_ENGINE_ARMV7_CROSS = PASS
RLL_CANONICAL_ENGINE_ARMV7_PHYSICAL = TOKEN_VAZIO
GEOM_V5_TO_RLL_EVIDENCE_TRANSFER = FORBIDDEN
```

A PASS here closes only the physical execution gate for the 33-row canonical H(z) freestanding kernel. It does not promote the full joint cosmological claim, covariance completion, external audit, or peer review.
