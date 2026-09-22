# RLL joint65 ARMv7 freestanding physical gate

This is a separate gate from GEOM Q16 and from the 33-row H(z)-only canonical kernel.

The four committed input files are embedded directly into the ELF with assembler `.incbin`; runtime does not use `fopen`, libc or filesystem APIs.

The entry runs both V2 joint profiles and exits with a bitmask if any invariant fails. A PASS requires:

- source hashes accepted by the canonical parser;
- 65 parsed / 65 bound / 0 model TOKEN_VAZIO;
- H(z)=33, BAO=13, fσ8=16, CMB=3;
- CMB covariance path used;
- canonical total=65, evidence=65, blocked=0;
- ΛCDM chi2_q16=4641555;
- RLL chi2_q16=4261420;
- delta=-380135;
- claim_allowed=0 in both routes;
- static ELF with no undefined symbols, PT_INTERP, DT_NEEDED or detected runtime/math helpers.

Run:

```bash
chmod +x scripts/run_rll_joint65_armv7_freestanding_physical_gate.sh
./scripts/run_rll_joint65_armv7_freestanding_physical_gate.sh
```

Until a physical ARMv7 execution receipt exists:

```text
RLL_JOINT65_ARMV7_FREESTANDING_PHYSICAL=TOKEN_VAZIO
GEOM_TO_RLL_EVIDENCE_TRANSFER=FORBIDDEN
```

Even a PASS here does not equal scientific validation of RLL; it validates this deterministic 65-observation compressed route and its pinned parameter profiles.


## Selective bootstrap on constrained ARMv7 — PASS

Observed on 2026-09-22 from Termux/ARMv7:

```text
method=raw.githubusercontent.com selective download
git_clone=not_required
pinned_ref=71c66f8efccef70f20a9b9657146d4dcac112672
downloaded_files=20
capsule_size=179K
status=PASS
```

The downloaded capsule contains only the production sources, required headers, embedded-data assembler, four pinned datasets, and the physical gate runner needed for the Joint65 execution.

This closes only the deployment/bootstrap gate:

```text
RLL_JOINT65_SELECTIVE_BOOTSTRAP_ARMV7=PASS
RLL_JOINT65_ARMV7_FREESTANDING_PHYSICAL=TOKEN_VAZIO
```

No claim about the Joint65 executable itself is promoted until the runner compiles, links, executes and emits its own receipt.
