# RLL + GEOM — Triple-pass retrofeedback audit — 2026-09-22

State: `AUDIT_RECORDED`  
Claim boundary: `claim_allowed=false`

This document reconciles the conversation execution history, the uploaded RLL snapshot, the live RLL repository, the GEOM Q16 producer repository, and the newly formalized retarded-spacetime/source-state layer.

## Pass 1 — execution/provenance reconciliation

### Joint65 physical ARMv7

Observed on physical `armv7l`:

```text
RLL_JOINT65_SELECTIVE_BOOTSTRAP_ARMV7=PASS
RLL_JOINT65_STRICT_NO_RUNTIME_LINK=FAIL
RLL_JOINT65_STATIC_BUILTINS_PHYSICAL=PASS
RLL_JOINT65_STRICT_NO_RUNTIME_PHYSICAL=TOKEN_VAZIO
```

Physical artifact:

```text
artifact_sha256=4ea887b8a679dd0db6f5ad36ec63030a5fed6ed0affd7a8c6b229f3452020a2b
compiler_rt_builtins_sha256=dcb6cfe8f1afa5bb37b935173e7b90709cb474c3d6b6104e8b8f386a5f108e60
local_runtime_shim_sha256=b3462dd2612f79428e7415d52b8b731e3f0b1342ce4c9dc59a7cb403e0a167cb
receipt_sha256=db822ebf5152f21b9e57faa4af7c0df68299ec08a56aa7a3142fdad0a067639b
execution_exit=0
undefined_symbols=0
interpreter_segments=0
needed_entries=0
libc_like_undefined=0
```

The entry source checks 65 parsed/bound rows, zero model TOKEN_VAZIO rows, CMB covariance use, the pinned Q16 chi-square values and `claim_allowed=0`. Therefore `execution_exit=0` closes those deterministic checks for this artifact. The receipt itself stores the expected values rather than independently printing the computed values, so a future receipt format should emit an observed-value block or a machine-readable in-memory/output witness as well.

This PASS proves static physical execution with toolchain builtins linked into the ELF. It does not prove strict zero-runtime freestanding execution.

### GEOM v5

The exact canonical GEOM v5 property route has a physical ARMv7 PASS receipt, but some older state documents still carry pre-physical TOKEN_VAZIO values. Those documents must be superseded/index-reconciled rather than silently rewritten.

## Pass 2 — scientific/model-boundary audit

### Pinned diagnostic != optimized inference

The physical Joint65 route is a deterministic pinned-profile gate. It does not perform a fresh posterior/likelihood optimization. It therefore cannot be used as evidence that RLL outperforms ΛCDM.

The uploaded snapshot contains optimized/full routes in which the extra RLL sector collapses toward its null boundary and receives AIC/BIC/Bayes penalties. Both states can coexist because they answer different questions.

### Retarded spacetime applicability must be observable-specific

The new source-state/light-cone layer is structurally coherent, but it must not be attached identically to all compressed observables.

Examples:
- H(z) cosmic-chronometer measurements already depend on differential source-age inference;
- BAO compressed points represent distance-scale combinations, not single-source photon tracks;
- fσ8 points are growth summaries with survey/window modeling;
- CMB shift parameters are highly compressed early-universe summaries.

Therefore each propagation/source-state term needs an `observable × effect × aggregation` applicability contract before entering the Joint65 likelihood. Otherwise lensing, gravitational redshift, peculiar velocity, plasma, or selection terms may be double-counted.

### Energy-momentum bridge dimensional blocker

Current code defines `pressure_density = P/c^2`, which has mass-density units (kg/m^3), while the other rho terms in the ledger are declared in J/m^3. Summing them directly is dimensionally invalid.

Until one common representation is chosen:

```text
ENERGY_MOMENTUM_SCALAR_PHYSICAL_CLAIM=BLOCKED
```

Acceptable repairs include:
1. convert every term to mass-equivalent density, or
2. keep energy density and pressure as distinct components of a covariant stress-energy tensor.

## Pass 3 — subtle/second-order gaps

### 1. Lossy-projection invariant

A shared engineering/science invariant emerged:

```text
CLASSIFY_OR_BIND_IN_NATIVE_CAUSAL_DOMAIN_BEFORE_LOSSY_NORMALIZATION_OR_PROJECTION
```

Examples:
- GEOM: classify raw `d` vs `2r` before Q16 quotient truncation;
- cosmology: bind emission/crossing events before projecting to a present-time interpretation;
- runtime: close ABI/runtime dependencies before assigning a strict-freestanding label.

This is an analogy/invariant of method, not evidence that the three domains are physically equivalent.

### 2. Quantization sensitivity

Joint65 physical execution proves exact reproduction of the pinned Q16 route. A separate float64/reference comparison with explicit per-observable and total chi-square quantization error bounds is still needed before treating Q16 numerical equivalence as scientifically negligible.

### 3. Runtime shim boundary

The local stack-check guard used to close compiler-rt linkage is a deterministic guard for execution gating, not a security-grade randomized stack-protector deployment. The byte-copy `__aeabi_memcpy{,4,8}` shim also deserves an explicit ABI/overlap/alignment contract.

### 4. Receipt completeness

The successful static-builtins receipt hashes the final ELF, compiler-rt archive and local runtime shim. Future canonical receipts should additionally hash:
- all production C/H sources;
- entry source;
- embedded-blob assembler;
- all four input datasets;
- every linked object or an aggregate manifest;
- runner script itself.

### 5. Multiple-testing/look-elsewhere control

The project has hundreds of formulas, geometric relations, contexts and candidate correlations. Any residual/geometric discovery search must use predeclared hypothesis families, held-out data and an explicit multiplicity correction or equivalent confirmatory design. Otherwise a visually compelling relation can emerge by search alone.

### 6. Identifiability

A flexible source-state/context hierarchy can absorb cosmological signal. Before promoting a context effect, require:
- prior predictive checks;
- simulation-based calibration where feasible;
- parameter/Jacobian rank or Fisher/identifiability diagnostics;
- shrinkage/partial pooling;
- out-of-sample recovery of injected effects.

### 7. Entropy coordinate dependence

Raw differential entropy can change under reparameterization. Cross-model/context comparisons should prefer KL divergence, mutual information or a declared invariant information-gain quantity rather than treating raw posterior differential entropy as an absolute physical scalar.

### 8. Gauge/observer dependence

Context features involving potentials, velocities, coordinates or time slices must declare observer/frame/gauge conventions. Physical promotion should rely on covariant observables or explicitly frame-bound quantities.

### 9. Correlated foreground paths

Multiple lensed paths and neighboring line-of-sight segments can share foreground structure. Segment covariance is not zero by default. Multi-path tests require shared-foreground covariance rather than independent-path multiplication.

## Reconciled open gates

```text
GEOM_V5_CANONICAL_ARMV7_PROPERTY=PASS
GEOM_RXD_ARMV7_PHYSICAL=TOKEN_VAZIO
GEOM_SECOND_PHYSICAL_DEVICE=TOKEN_VAZIO
GEOM_BAREMETAL_PHYSICAL_RESET_BOOT=TOKEN_VAZIO

RLL_JOINT65_STATIC_BUILTINS_PHYSICAL=PASS
RLL_JOINT65_STRICT_NO_RUNTIME_PHYSICAL=TOKEN_VAZIO
RLL_CANONICAL_33ROW_ENGINE_ARMV7_PHYSICAL=TOKEN_VAZIO

RLL_RETARDED_SPACETIME_STRUCTURAL=PASS_LOCAL
RLL_RETARDED_SPACETIME_REAL_DATA_BINDING=TOKEN_VAZIO
RLL_OBSERVABLE_EFFECT_AGGREGATION_MATRIX=TOKEN_VAZIO
RLL_EXTERNAL_INDEPENDENT_REPLICATION=TOKEN_VAZIO

ENERGY_MOMENTUM_DIMENSIONAL_CONTRACT=FAIL_FOUND
SCIENTIFIC_CLAIM=BLOCKED
```

## Highest-value next order

1. Canonically ingest the observed Joint65 static-builtins ARMv7 receipt and harden the repository runner to reproduce it.
2. Supersede stale GEOM/RLL state documents without deleting old evidence.
3. Repair the energy-momentum dimensional contract.
4. Build an observable × effect × aggregation applicability matrix before connecting source-state/retarded-spacetime terms to compressed Joint65 data.
5. Add Q16-vs-float64 numerical error bounds.
6. Execute synthetic light-cone, moving-region, lensing-delay and plasma-frequency mocks.
7. Run matched full-likelihood/covariance comparisons and independent reproduction.

R3=<F_ok: physical GEOM v5 PASS, physical Joint65 static-builtins PASS, strong provenance/governance, retarded-spacetime contract formalized; F_gap: strict runtime-free, second device, reset boot, rxd physical, dimensional bridge, observable binding, quantization bound and external reproduction; F_next: ingest/reconcile receipts first, then repair dimensional/model-binding gaps before any new-physics promotion>.
