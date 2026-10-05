# RLL Minimal One-Parameter Benchmark V1

**Date:** 2026-10-04  
**Status:** `EXECUTABLE_FALSIFIER / CLAIM_BLOCKED`  
**Scope:** DESI DR2 BAO 13-vector currently materialized in this repository.

## Question

Can the present RLL transition family obtain a chi-square improvement comparable
to roughly `-8` or `-10` relative to an equally profiled LCDM baseline while
adding only one extra free parameter, and then remain eligible for independent
Ly-alpha full-shape, growth and Bayesian-evidence tests?

This benchmark answers only the first clause. It refuses to infer the successor
clauses from BAO-only data.

## Minimal nested comparison

Both models profile the same two quantities:

1. `Omega_m`;
2. `q = c / (H0 * r_d)`, profiled analytically as the common BAO scale.

LCDM uses those two quantities.

RLL-min adds exactly one quantity:

- `Omega_s0`.

The transition coordinates remain frozen for this falsifier:

```text
z_t = 1.0
w_t = 0.3
Omega_r = 9.2e-5
```

The RLL-min background is the current repository transition family with only its
amplitude released. At `Omega_s0 = 0`, RLL-min must reproduce LCDM numerically.
The test suite enforces this nesting identity.

## Why this is a hotfix instead of a replacement

The pre-existing `scripts/compute_desi_dr2_bao_zml.py` remains untouched. It is
a fixed-parameter real-data comparison and is useful for provenance, but it does
not answer the one-extra-parameter optimization question because its model
parameters are nominal rather than jointly/profiled under equal conditions.

This benchmark is intentionally parallel and reversible.

## Frozen-data expected result

On the current 13-element DESI DR2 BAO vector and its 13x13 covariance, the
deterministic coarse-to-fine profile is expected to land near:

```text
LCDM chi2      ~= 10.28
RLL-min chi2   ~= 8.96
delta chi2     ~= -1.32
```

The exact CI receipt is authoritative for an execution. These values are a
reproducibility fence, not a publication claim.

Therefore, on the current materialization:

```text
target delta chi2 <= -8   -> expected FAIL
target delta chi2 <= -10  -> expected FAIL
AIC improvement           -> expected FAIL
BIC improvement           -> expected FAIL
```

A smaller chi-square by itself is not sufficient because RLL-min pays one extra
parameter.

## Successor gates

### DESI Ly-alpha full-shape/AP

`NOT_RUN`.

The repository already records a 2026 Ly-alpha full-shape source and an explicit
anti-double-counting boundary. The two Ly-alpha entries in the current 13-vector
are BAO measurements; they are not the independent full-shape/AP likelihood.
No full-shape pass may be inferred from their residuals.

### Growth / f-sigma8

`TOKEN_VAZIO`.

The minimal benchmark specifies only the homogeneous background expansion. A
physically justified perturbation equation, transfer function and growth
prediction are not yet bound to this one-parameter model. No GR-like growth law
is silently assumed.

### Bayesian evidence

`NOT_RUN`.

Profile chi-square, AIC and BIC are not Bayesian evidence. Evidence requires
explicit priors and an evidence integral or validated nested-sampling equivalent.
Until those exist for the exact same frozen parameterization, `ln Z` and Bayes
factors remain unavailable.

## Contemporary comparison target

The September 2026 literature makes a one-parameter competitor especially
important: `arXiv:2609.40176` reports a one-parameter cosmological-gravity
mismatch fit alongside DESI DR2 and CMB. It is an external comparator, not an
RLL component and not evidence for RLL.

The repository's 2026 Ly-alpha full-shape evidence remains a separate falsifier;
it must not be appended to overlapping Ly-alpha BAO as though statistically
independent.

## Promotion rule

The minimal family advances to the expensive successor stack only if a frozen,
reproducible configuration clears the predefined BAO gate without adding hidden
parameters:

```text
primary target: delta chi2 <= -8
strong target:  delta chi2 <= -10
complexity:     exactly one RLL-only free parameter
```

If the target fails, the correct action is to revise or falsify the physical
term before adding dimensions, not to release `z_t`, `w_t`, geometry or other
parameters merely to buy fit quality.

## Invariants

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
TOKEN_VAZIO != 0
IMPLEMENTED_UNTESTED != PASS
PROFILE_LIKELIHOOD != BAYESIAN_EVIDENCE
LYA_BAO != LYA_FULL_SHAPE
BETTER_CHI2 != BETTER_MODEL
```

## Reproduction

```bash
python scripts/run_rll_minimal_model_benchmark.py \
  --output-dir artifacts/rll-minimal-benchmark

pytest -q tests/test_rll_minimal_model_benchmark.py
```

Expected artifact set:

```text
artifacts/rll-minimal-benchmark/benchmark.json
artifacts/rll-minimal-benchmark/REPORT.md
artifacts/rll-minimal-benchmark/CLAIM_BOUNDARY.txt   # CI
artifacts/rll-minimal-benchmark/CHECKSUMS.sha256     # CI
```

## Rollback

The change is isolated. Rollback consists of reverting/removing:

```text
scripts/run_rll_minimal_model_benchmark.py
tests/test_rll_minimal_model_benchmark.py
.github/workflows/rll-minimal-model-benchmark.yml
docs/science/RLL_MINIMAL_ONE_PARAMETER_BENCHMARK_V1.md
data/contracts/rll_minimal_one_parameter_benchmark.v1.json
```

No canonical observational input, prior result, or existing scientific runner is
mutated.

## R3

**F_ok**

- equal shared profiling between LCDM and RLL-min;
- exactly one additional RLL-min parameter;
- full current 13x13 covariance used;
- AIC/BIC and predefined `-8/-10` gates emitted;
- Ly-alpha BAO/full-shape epistemic boundary explicit;
- branch/workflow is non-publishing and reversible.

**F_gap**

- `DESI_DR2_LYA_FULLSHAPE_NON_OVERLAP_LIKELIHOOD`;
- `RLL_MIN_PERTURBATION_GROWTH_MODEL`;
- `RLL_MIN_BAYESIAN_PRIORS_AND_EVIDENCE`;
- `CMB_JOINT_LIKELIHOOD_SAME_PARAMETERIZATION`.

**F_next**

Do not spend complexity on later gates unless the one-parameter background first
survives the frozen BAO target. If it fails, retain the failure receipt as
evidence and search for a physically motivated term, not a numerically convenient
extra degree of freedom.
