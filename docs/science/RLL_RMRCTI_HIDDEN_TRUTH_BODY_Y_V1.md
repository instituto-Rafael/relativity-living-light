# RLL — Body-Y Hidden-Truth × G6 Geometry Benchmark V1

**Date:** 2026-09-25  
**State:** `SYNTHETIC_EXECUTABLE / claim_allowed=false`  
**Workstream:** `WS18`

The benchmark freezes a synthetic two-impulse weak-field trajectory before noise,
creates retarded observations, and compares five fixed histories: truth, no-event,
wrong event order, wrong geometry, and wrong impulse sign.

Primary G6 statistic:

[
d^2=\Delta x^T\Sigma^{-1}\Delta x.
]

No candidate is fitted after seeing the noise.

## Adaptive numerics

Local curvature controls only RK4 subdivision; it never changes physical parameters.
Reference (dt=0.002); router (dt=0.08).

Local deterministic replay:
- fixed RMSE: (6.915461477726151\times10^{-5});
- adaptive RMSE: (6.908074343892289\times10^{-5});
- fixed RK4 steps: 45;
- adaptive RK4 steps: 179;
- max subdivision: 8.

The gain is deliberately modest: the result is a non-regression/type-boundary test,
not a large performance claim.

## Hidden truth

Seeds: 17, 23, 42, 633, 144000. The true scenario ranked first in 5/5.

## RMRCTI diagnostic

[
\Delta P_{op}=P(stable|peak)-P(stable|nonpeak).
]

Values: ([-0.25,0,0,-0.25,-0.25]), mean (-0.15). The historical project
target 0.18 was not fitted and is not a physical constant. Recovery persistence
across the five seeded trials is 1.0.

## G6 / multiple testing

The only confirmatory selector here is total 2D Mahalanobis residual under the
frozen scenario family. No p-value claim is made. Any later feature-family
significance requires a registered family and Holm correction.

## R3

**F_ok:** hidden truth 5/5 recovered; retarded observation explicit; weak-field
gate passed; negative controls preserved; adaptive numerics did not change physics.

**F_gap:** independent real RMRCTI trace package and domain-calibrated sensitivity
thresholds remain open; no observational astrophysical claim is promoted.

**F_next:** independent trace replication and threshold calibration against a
source-bound dataset while preserving this synthetic fixture unchanged.
