# RLL — DESI DR2 Full-Covariance Whitened Residual × Fibonacci Multiscale V1

**Date:** 2026-09-28  
**State:** \`PASS_SOFTWARE_REPRODUCTION / claim_allowed=false\`  
**Author/proponent:** Rafael Melo Reis  
**Producer:** \`instituto-Rafael/relativity-living-light\`  
**Claim gate:** \`claim_allowed=false\`

## Intent

Extend the merged \`RLL_MULTISCALE_HETEROGENEOUS_RESIDUAL_GEOMETRY_V1\`
from reference fixtures to a frozen DESI DR2 real-data surface without changing
the likelihood.

Precision is not obtained by replacing standard deviation with Fibonacci,
\`sqrt(3)/2\`, Poincaré geometry, Venturi, geodesic geometry or calendar
cycles. For the committed DESI vector, the statistical authority is the
committed 13×13 covariance.

\`\`\`text
observed - model
  -> residual r
  -> full covariance C
  -> Cholesky C = L L^T
  -> whitened residual z = L^-1 r
  -> chi2 = sum(z_i^2)
  -> covariance-block decomposition
  -> Fibonacci-sized diagnostic windows on z
  -> claim gate remains closed
\`\`\`

## Statistical baseline

Population standard deviation:

\[
\sigma=\sqrt{\frac{1}{N}\sum_{i=1}^{N}(x_i-\mu)^2}.
\]

Sample standard deviation:

\[
s=\sqrt{\frac{1}{n-1}\sum_{i=1}^{n}(x_i-\bar x)^2}.
\]

For correlated DESI observables, with \(r=y-m\) and covariance \(C\),

\[
\chi^2=r^T C^{-1}r.
\]

With \(C=LL^T\),

\[
z=L^{-1}r,\qquad \chi^2=z^Tz=\sum_i z_i^2.
\]

This is the controlled bridge from scalar standard-deviation intuition to the
multivariate correlated case.

## Frozen sources

- \`data/real/cosmology/desi_dr2_bao_primary_points.csv\`
- \`data/real/desi_dr2_bao_covariance.csv\`
- \`results/RLL_G4_DESI_GEOMETRY_LCDM_RLL_REPRODUCTION_V1.json\`

No observation, covariance element or G4 prediction is invented by this
successor.

## Fibonacci matrix / multiscale role

The predecessor formalism keeps the classical companion matrix

\[
Q_F=
\begin{pmatrix}
1&1\\
1&0
\end{pmatrix},
\qquad
Q_F^n=
\begin{pmatrix}
F_{n+1}&F_n\\
F_n&F_{n-1}
\end{pmatrix}.
\]

This real-data successor uses only the predeclared contiguous window sizes

\[
2,3,5,8,13,\ldots
\]

on the **whitened residual sequence**.

\`\`\`text
FIBONACCI_WINDOW != LIKELIHOOD_WEIGHT
\`\`\`

The scan may expose scale-localized residual structure; it does not change
\`C\`, \(\chi^2\), AIC, BIC or posterior weight.

## Typed geometry retained without statistical substitution

Project sources contain:

- Pythagoras; equilateral/isoceles triangles; tangents and projections;
- \`sqrt(3)/2\` as Euclidean/projective kernel;
- polygonal, geodesic and icosphere constructions;
- Poincaré ball metric and Poincaré return map as distinct objects;
- Venturi as a fluid-domain adapter;
- calendar cycles as temporal comparators.

These do **not** silently enter this BAO likelihood.

For the standard Poincaré disk normalization used in the mathematical
namespace, Gaussian curvature is constant \(K=-1\). Metric distance diverges
toward the boundary; curvature is not described as increasing toward the rim.

## Frozen numerical target

The committed G4 reproduction has the RLL point at \`Omega_s0=0\`, on the LCDM
null submanifold for this background comparison.

The new executor must recover:

\`\`\`text
LCDM chi2 ~= 11.770259180500712
RLL  chi2 ~= 11.770259055546350
\`\`\`

The near identity is expected at this frozen null point and is not evidence of
RLL superiority.

The current DESI covariance is block diagonal across its declared covariance
blocks, so the sum of block chi-square contributions must close to global
chi-square within floating-point tolerance.

## Falsifiers

Fail closed if:

1. observation/prediction ordering differs;
2. covariance dimension differs from the frozen vector;
3. covariance is asymmetric or not positive definite;
4. whitened chi-square fails to reproduce G4;
5. Fibonacci changes likelihood weights;
6. \`sqrt(3)/2\` is substituted for statistical sigma;
7. a geometry matrix is called covariance without statistical derivation;
8. Poincaré/Venturi/calendar analogy is promoted to causal cosmology;
9. null-submanifold reproduction is called model discrimination.

## Materialized successor

- \`scripts/rll_desi_dr2_covariance_multiscale.py\`
- \`data/contracts/rll_desi_dr2_covariance_multiscale.v1.json\`
- \`tests/test_rll_desi_dr2_covariance_multiscale.py\`
- \`.github/workflows/desi-dr2-covariance-multiscale-gate.yml\`

## R3

\`\`\`text
F_ok =
full-covariance whitening defined
+ exact chi2 reproduction target frozen
+ block decomposition defined
+ Fibonacci multiscale retained without likelihood weighting
+ geometry namespaces preserved

F_gap =
independent reproduction
+ non-null/held-out RLL profile for model discrimination
+ physical Poincare/Venturi/calendar binding

F_next =
apply the same frozen diagnostic to a preregistered
   non-null or held-out RLL profile without retuning scales/groups/covariance
\`\`\`


## Provider execution evidence — 2026-09-28

Tested source head: \`adc67d49bd33e5e5ec5eb49b4a4860e654952f2a\`.

Dedicated workflow:

- \`DESI DR2 Covariance Whitened Multiscale Gate\`
- run \`36491451759\`
- job \`109160771657\`
- conclusion: \`success\`

Observed successful steps:

1. contract parse;
2. covariance-whitened reference execution;
3. focused test suite.

Provider log reports:

\`\`\`text
PASS_CONTRACT rll.desi_dr2.covariance_whitened_multiscale.contract.v1
PASS_REFERENCE 11.770259055546353
6 passed in 0.05s
\`\`\`

The PASS is bounded to source/order/covariance validation, positive-definite
Cholesky whitening, chi-square reproduction, block closure and the declared
Fibonacci-window boundary. It does not promote a physical or cosmological
claim. \`claim_allowed=false\` remains.
