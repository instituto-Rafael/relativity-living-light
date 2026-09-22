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


## Successor geometry v3 — no RLL promotion

The producer repo now contains a v3 candidate that fixes the Q16 boundary falsifier and adds a complete discrete invariant sweep for `r=1`.

```text
producer: rafaelmeloreisnovo/Matem-tica-
path: experiments/geom_equal_circles_q16_armv7_2026-09-22/
v3 materialization commit: 6102f28345e54059873dd848326be7ab0689040b
v3 source local SHA256: ecbf85fe3a7c96ee5e2eebd1695b9875414145e27b8455b2abbf4d415969b42a
```

Observed pre-physical state:

```text
GEOM_V3_HOST_SELFTEST = PASS
GEOM_V3_ARMV7_CROSS_LINK = PASS
GEOM_V3_ARMV7_PHYSICAL = TOKEN_VAZIO
RLL_CANONICAL_ENGINE_ARMV7_PHYSICAL = TOKEN_VAZIO
```

No evidence is transferred from the geometry executable to the RLL executable. A v3 physical receipt can validate the geometry successor only.


## Integrated geometry successor v4

Parallel geometry hardening branches were reconciled in the producer repository into `geom_freestanding_integrated_v4.c`.

```text
integration decision commit: b0fd4f03e36b77c16fec3f1df3d88203fc743688
local source SHA256: 43f363f386e001a4cd568b3ae9e7a919ab9bdbef0e38c48fa2ce99bf951f8d0a
host UBSan selftest+sweep: PASS
ARMv7 cross static structural gate: PASS
physical ARMv7 v4: TOKEN_VAZIO
```

The RLL boundary remains unchanged: geometry pre-physical evidence does not promote the RLL engine. Only an artifact-specific RLL physical receipt can close that gate.


## Physical geometry v4 receipt observed

The integrated geometry v4 producer artifact has now been executed on a physical `armv7l` target.

```text
geometry_source_sha256=43f363f386e001a4cd568b3ae9e7a919ab9bdbef0e38c48fa2ce99bf951f8d0a
geometry_artifact_sha256=ee8da8dd4ab0eaa474483a4932eb0e1666a601fe1fbb12ff53d4df073de38803
geometry_receipt_sha256=183fbe34102c9987224598408918a4ea295cdf4e1535694025b99f4360c69c13
GEOM_INTEGRATED_V4_ARMV7_PHYSICAL=PASS
```

This still does not promote the RLL engine:

```text
RLL_CANONICAL_ENGINE_ARMV7_PHYSICAL=TOKEN_VAZIO
```

The geometry receipt is a toolchain/runtime witness and a schema example only; artifact-specific RLL execution evidence remains required.


## v5 orthogonal validation axes

The geometry producer now separates three evidence types:

```text
FORMAL_TOPOLOGY_PROOF
HOSTED_PROPERTY_PLUS_INDEPENDENT_ORACLE
FREESTANDING_CROSS_SCALE_PROPERTY
```

Formal topology proof covers every representable positive Q16 radius by exact integer partition of raw `d` versus `2r`. Hosted v5 enumerates all 131073 normalized Q16 states and adds one million deterministic radius regressions plus an independent Python oracle.

A new freestanding property axis has pre-physical PASS evidence:

```text
917510 geometry evaluations
786432 cross-scale comparisons
131072 monotonic normalized steps
7 exact scales
host PASS
UBSan PASS
ARMv7 cross static PASS
dynamic/interpreter/undefined/suspicious helpers = 0
```

Its physical ARMv7 state remains:

```text
GEOM_V5F_ARMV7_PHYSICAL=TOKEN_VAZIO
```

No geometry v5 evidence promotes the RLL engine:

```text
RLL_CANONICAL_ENGINE_ARMV7_PHYSICAL=TOKEN_VAZIO
```


## v5 external geometry gates and RLL physical runner

Geometry v5 has now separated these gates:

```text
SECOND_IMPLEMENTATION_ORACLE=PASS
BAREMETAL_RESET_IMAGE_BUILD=PASS
SECOND_PHYSICAL_DEVICE=TOKEN_VAZIO
BAREMETAL_PHYSICAL_RESET_BOOT=TOKEN_VAZIO
```

The RLL engine remains independent. A dedicated physical ARMv7 runner now exists:

```text
scripts/run_rll_canonical_armv7_physical_v2.sh
commit=a1af5fdcede400d0a41b11c7f269b327a67f19ea
gate_doc=docs/evidence/RLL_CANONICAL_ARMV7_PHYSICAL_GATE_V2.md
gate_doc_commit=ace1060fbfbe547b980189d62bbec3b6be1a9e4e
```

Only the output receipt from that runner may promote `RLL_CANONICAL_ENGINE_ARMV7_PHYSICAL`.


## v5 all-radii partition and joint65 physical route

The geometry producer now contains an explicit all-radii proof/reduction set under `.../v5/`:

```text
ALL_Q16_RADII_TOPOLOGY=PROVED_BY_EXACT_INTEGER_RANGE_PARTITION
NORMALIZED_X_DOMAIN_0_TO_2=EXHAUSTIVE_REDUCTION_PASS
SECOND_TOOLCHAIN_REPRODUCTION=PASS
SECOND_LANGUAGE_REFERENCE_REPRODUCTION=PASS
SECOND_PHYSICAL_DEVICE_REPRODUCTION=TOKEN_VAZIO
RESET_VECTOR_BAREMETAL_STRUCTURAL=PASS
RESET_VECTOR_BAREMETAL_EXECUTION=TOKEN_VAZIO
```

RLL remains separate. Two physical gates are now available:

```text
scripts/run_rll_canonical_armv7_physical_gate.sh
  -> 33-row canonical H(z) kernel

scripts/run_rll_joint65_armv7_freestanding_physical_gate.sh
  -> 65-observation joint route with the four committed source files embedded by .incbin
```

The joint65 ELF requires 65/65 bound observations, CMB covariance, pinned chi2 values `4641555` and `4261420`, delta `-380135`, and `claim_allowed=0`, while also requiring zero dynamic/undefined/runtime-helper gates.

Until a physical ARMv7 run is ingested:

```text
RLL_CANONICAL_ENGINE_ARMV7_PHYSICAL=TOKEN_VAZIO
RLL_JOINT65_ARMV7_FREESTANDING_PHYSICAL=TOKEN_VAZIO
GEOM_TO_RLL_EVIDENCE_TRANSFER=FORBIDDEN
```


## v5 r×d boundary sheet at 2r±1

A successor producer branch adds a two-dimensional falsification sheet focused on the exact topology boundary:

```text
producer_repo=rafaelmeloreisnovo/Matem-tica-
producer_pr=#38
producer_branch=agent/geom-v5-rxd-boundary-20260922
producer_head=4af0f0746c1f1a715f8b9e1de58e768791519e58
base_v4_source_sha256=43f363f386e001a4cd568b3ae9e7a919ab9bdbef0e38c48fa2ce99bf951f8d0a
relation=d=2r+delta
delta={-1,0,+1}
```

The executable sheet is intentionally not a brute-force claim over the full `r×d` pairspace. It combines:

- exhaustive raw radii `r=1..65536`;
- 65536 deterministic radii over the domain where `2r+1` remains representable;
- five representability-edge probes around `2^30`.

Expected and independently reproduced integer-oracle counts are:

```text
rxd_rows=131072
rxd_evals=393221
rxd_minus_cases=131072
rxd_tangent_cases=131072
rxd_plus_cases=131072
rxd_special_cases=5
INDEPENDENT_RXD_INTEGER_ORACLE=PASS
oracle_report_sha256=7758bfa89e7d04cec520d876c46fca376c43d0beac75275579d3b7be3be7f078
producer_c_execution_in_oracle=NOT_RUN
```

GitHub Actions run `35782026225` was observed twice and failed before any workflow step became observable; both attempts exposed `steps=[]`, and the job-log blob was unavailable. Therefore the provider state is typed narrowly:

```text
GEOM_RXD_PROVIDER_CI=PROVIDER_PRESTART_FAILURE_REPRODUCED
GEOM_RXD_PROVIDER_PROGRAM_RESULT=TOKEN_VAZIO
GEOM_RXD_ARMV7_PHYSICAL=TOKEN_VAZIO
SECOND_PHYSICAL_DEVICE=TOKEN_VAZIO
BAREMETAL_PHYSICAL_RESET_BOOT=TOKEN_VAZIO
RLL_CANONICAL_ENGINE_ARMV7_PHYSICAL=TOKEN_VAZIO
GEOM_TO_RLL_EVIDENCE_TRANSFER=FORBIDDEN
```

The independent integer oracle reproduces the boundary arithmetic but does not substitute for execution of the producer C artifact, a physical ARMv7 receipt, a second physical device, a board-specific reset-vector boot, or the RLL executable's own physical gate.

### R3 — r×d bridge

F_ok: exact all-Q16 topology proof remains intact; r×d `2r±1` sheet, receipt-v5 runner, master integration and independent arithmetic oracle are materialized in the producer PR; independent oracle counts PASS.

F_gap: provider workflow starts fail before observable steps; producer-C provider result, new physical ARMv7 r×d receipt, second physical device, physical reset boot and RLL physical execution remain open/TOKEN_VAZIO.

F_next: ingest an artifact-specific physical ARMv7 r×d receipt when executed; independently diagnose provider pre-start only if a provider diagnostic becomes available; keep reset boot and RLL engine as separate gates.
