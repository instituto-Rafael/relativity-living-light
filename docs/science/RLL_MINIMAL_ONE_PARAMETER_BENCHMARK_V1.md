# RLL Minimal One-Parameter Benchmark V1

**Date:** 2026-10-05  
**Status:** `EXECUTABLE_FALSIFIER / CLAIM_BLOCKED`  
**Route:** `work/* -> rll/lab`  
**Scope:** DESI DR2 BAO 13-vector currently materialized in this repository.

## Question

Can the present RLL transition family obtain a chi-square improvement comparable to `-8` or `-10` relative to an equally profiled LCDM baseline while adding only one extra free parameter, and then remain eligible for independent Ly-alpha full-shape, growth and Bayesian-evidence tests?

This benchmark answers only the BAO clause. It does not infer any successor gate from BAO-only goodness of fit.

## Minimal nested comparison

Both models profile the same quantities:

1. `Omega_m`;
2. `q = c/(H0*r_d)`, analytically profiled as the common BAO scale.

LCDM has no model-specific extra parameter. RLL-min adds exactly:

- `Omega_s0`.

Frozen transition coordinates:

```text
z_t = 1.0
w_t = 0.3
Omega_r = 9.2e-5
```

At `Omega_s0 = 0`, RLL-min must reproduce the LCDM background numerically. The test suite enforces this nesting identity.

## Why this is a hotfix instead of a replacement

The existing `scripts/compute_desi_dr2_bao_zml.py` remains untouched. It is useful provenance for the fixed-parameter comparison, but it does not answer the one-extra-parameter question under equal profiling.

This benchmark is additive and reversible. The canonical lab route intentionally adds **no new workflow**; existing repository CI executes the tests, keeping workflow inventory unchanged.

## Frozen-data reproducibility fence

Using the current 13-element DESI DR2 BAO vector and full 13x13 covariance, the same code/data already produced approximately:

```text
LCDM chi2      = 10.284028
RLL-min chi2   = 8.964441
delta chi2     = -1.319586
delta AIC      = +0.680414
delta BIC      = +1.245363
```

Therefore the expected scientific decision on this materialization is:

```text
target delta chi2 <= -8   -> FAIL
target delta chi2 <= -10  -> FAIL
AIC improvement           -> FAIL
BIC improvement           -> FAIL
```

A smaller chi-square alone is not sufficient because RLL-min pays one extra parameter. These values are a reproducibility fence, not a publication claim.

## Successor gates

### DESI Ly-alpha full-shape/AP

`NOT_RUN`.

The two Ly-alpha entries in the current 13-vector are BAO measurements. They are not the independent 2026 full-shape/AP likelihood, and overlapping Ly-alpha information must not be double counted.

### Growth / f-sigma8

`TOKEN_VAZIO`.

This minimal benchmark specifies only homogeneous background expansion. A justified perturbation equation, transfer function and growth prediction are not yet bound to this exact one-parameter model.

### Bayesian evidence

`NOT_RUN`.

Profile chi-square, AIC and BIC are not Bayesian evidence. Evidence requires explicit priors and an evidence integral or validated nested-sampling equivalent for the same frozen parameterization.

### Joint CMB

`NOT_RUN`.

The same one-parameter model must be exposed to a joint CMB likelihood before any comparison with contemporary one-parameter competitors can be claimed.

## Promotion rule

The family advances to the expensive successor stack only if a frozen, reproducible configuration clears all of the following without hidden parameters:

```text
primary target: delta chi2 <= -8
strong target:  delta chi2 <= -10
complexity:     exactly one RLL-only free parameter
AIC:            must improve
BIC:            must improve
```

If the target fails, the correct action is to revise or falsify the physical term before releasing `z_t`, `w_t`, geometry or other degrees of freedom merely to buy fit quality.

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

Direct runner outputs:

```text
artifacts/rll-minimal-benchmark/benchmark.json
artifacts/rll-minimal-benchmark/REPORT.md
```

Repository CI is authoritative for merge gating. No dedicated workflow is added by this hotfix.

## Rollback

Rollback is exactly the revert/removal of these four additive files:

```text
scripts/run_rll_minimal_model_benchmark.py
tests/test_rll_minimal_model_benchmark.py
docs/science/RLL_MINIMAL_ONE_PARAMETER_BENCHMARK_V1.md
data/contracts/rll_minimal_one_parameter_benchmark.v1.json
```

No canonical observational input, workflow inventory, prior scientific result or existing runner is mutated.

## R3

**F_ok**

- equal shared profiling between LCDM and RLL-min;
- exactly one additional RLL-min parameter;
- full current 13x13 covariance used;
- AIC/BIC and predefined `-8/-10` gates emitted;
- Ly-alpha BAO/full-shape epistemic boundary explicit;
- canonical `work/* -> rll/lab` route;
- zero workflow-inventory expansion.

**F_gap**

- `DESI_DR2_LYA_FULLSHAPE_NON_OVERLAP_LIKELIHOOD`;
- `RLL_MIN_PERTURBATION_GROWTH_MODEL`;
- `RLL_MIN_BAYESIAN_PRIORS_AND_EVIDENCE`;
- `CMB_JOINT_LIKELIHOOD_SAME_PARAMETERIZATION`.

**F_next**

Do not spend complexity on later gates unless the one-parameter background first survives the frozen BAO target. If it fails, retain the failure receipt as evidence and search for a physically motivated term rather than a numerically convenient extra degree of freedom.
