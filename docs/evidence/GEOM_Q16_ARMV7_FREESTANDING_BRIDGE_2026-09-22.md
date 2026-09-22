# GEOM Q16 ARMv7 — evidence bridge into RLL

Date: 2026-09-22  
State: `EVIDENCE_BRIDGE_ONLY`  
Claim gate: `claim_allowed=false`

## Producer

Canonical implementation/evidence is stored in:

```text
repo: rafaelmeloreisnovo/Matem-tica-
commit: 5f79863bc9d6cc77cf9a9dfdd59fefbb1ecc2bca
path: experiments/geom_equal_circles_q16_armv7_2026-09-22/
source_sha256: 348a49ddf76d55af160d6814d0af203c0080918b4062bc030b3dd3f135475362
receipt_v2_sha256: 724a24012be35c3a36f5eb26eb8dc8622aeb1fa72522d3103209d258df13dcfc
```

## What this adds to RLL

A separate geometry kernel using Q16.16 and `sqrt(3)/2 = 56756` has an observed physical ARMv7 execution receipt with static/no-interpreter/no-DT_NEEDED/no-undefined gates and `selftest_exit=0`.

This is useful as:

- a physical ARMv7 freestanding-userspace toolchain witness;
- a receipt pattern for RLL low-level kernels;
- a regression target for integer sqrt/division/multiplication and geometric invariants.

## What this does not close

It does **not** close the RLL canonical engine's own physical ARMv7 gate. Different executable bytes require different execution evidence.

```text
GEOM_Q16_ARMV7_PHYSICAL = PASS_LIMITED
RLL_CANONICAL_ENGINE_ARMV7_PHYSICAL = TOKEN_VAZIO
RAFAELIA_OMEGA_HARDENED_ENGINE_ARMV7_PHYSICAL = TOKEN_VAZIO
```

No cosmological likelihood or physical-model claim is promoted by this bridge.

## Audit gap carried forward

The geometry implementation currently classifies circle topology after Q16 normalization. A counterexample exists near `d=2r` for radii where `d/r` truncates back to exactly 2.0. Until fixed:

```text
QUANTIZED_BOUNDARY_CORRECTNESS = FAIL_FOUND
FULL_DOMAIN_GEOMETRY = TOKEN_VAZIO
```

Recommended correction: compare raw nonnegative Q16 inputs with a wide exact relation `(u64)d` vs `2*(u64)r` for topology; use normalized Q16 only for derived metrics.

## Next RLL-specific gate

Run the actual RLL ARMv7 executable on the physical ARMv7 target and produce an artifact-specific receipt. The geometry receipt may be reused as schema, not as substitute evidence.
