# RLL / DESI DR2 — adversarial falsification: fixed point vs profiled likelihood (2026-10-09)

**State:** independent numerical diagnostic; bounded search; `claim_allowed=false`. This is not a physical validation, a global optimum certificate, or an external peer review. Existing source, outputs, APK, and gates are unchanged.

## Authority and pinned sources
- Producer: `instituto-Rafael/relativity-living-light`, active default `main`; diagnostic documentation is isolated on this branch.
- Input vector: `data/real/desi_dr2_bao_measurements.csv`, Git blob `8611587e98e60389f7f7b1cb2cf9ab095654d74a`.
- Covariance: `data/real/desi_dr2_bao_covariance.csv`, Git blob `e01d0235a2f0e61d81af0c36a7338953f845f5c3`.
- Script under audit: `scripts/compute_desi_dr2_bao_zml.py`, Git blob `d21490e13c5f024b3a83a110c10a140c5a6fe51c`.
- Independent public comparator: https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt and https://raw.githubusercontent.com/CobayaSampler/bao_data/master/desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt . All 13 rounded means and 13x13 covariance entries matched the copied source values, with the Lyα final pair ordered DH then DM.
- Published DESI DR2 collaboration measurements: https://arxiv.org/abs/2503.14738 .

## Observational operator / measurement geometry

Let `y` be 13 BAO distance-ratio observations ordered (DV,DM,DH,...,DH_Lya,DM_Lya), `m(theta)` the model prediction and `C` the positive-definite 13x13 covariance matrix.

`chi2(theta) = (m(theta)-y)^T C^{-1}(m(theta)-y) = ||L^{-1}(m-y)||_2^2` with `LL^T=C`.

The RLL parametrization audited is exactly the one in the producer script:
`E(z)^2 = Om(1+z)^3 + Or(1+z)^4 + (1-Om-Or-Os) + Os[f(z)+(1-f(z))(1+z)^3]`,
`f(z)=1/(1+exp((z-zt)/wt))`,
`H(z)=H0*E(z)`, `DH/rd=c/(H(z)*rd)`, `DM/rd=(c/(H0*rd))*int_0^z dz'/E(z')` and `DV/rd=[z*(DM/rd)^2*(DH/rd)]^(1/3)` in a spatially-flat background.

Inputs held fixed for exploratory re-fit: `rd=147.09 Mpc`, `Or=9.2e-5`. Units: `H0` km/s/Mpc, `z, E, DM/rd, DH/rd, DV/rd, chi2` dimensionless.

## TEST F01: independent reconstruction at fixed source parameters — REPRODUCED

`LCDM: H0=67.4, Om=0.315, Or=9.2e-5`.
`RLL: same + Os=0.02, zt=1, wt=0.3`.

| Model | fixed-point chi2 |
|---|---:|
| LCDM | 28.693741018891984 |
| RLL | 34.527535985331930 |

`delta_chi2(RLL-LCDM)=+5.833794966439946` (matches the existing ZML rounded diagnostic). Covariance `min_eigenvalue ~ 0.005789987`, condition number ~116.824; max diagonal sqrt/column sigma difference `4.7e-13`. An independent Gaussian 64-node quadrature implementation and SciPy adaptive quadrature agreed to approximately `1.2e-13` in all model predictions at these points.

**Falsifier identified:** the producer script counts `k_params=3` vs `5` and publishes AIC/BIC preference based on two predetermined parameter vectors. The displayed values are fixed-point penalized scores, not necessarily the model-specific minimum deviance needed for defensible fitted AIC/BIC. Its parameter counts also do not correspond directly to the 2-vs-5 free variables of the experiment below. Therefore do not promote fixed-point `delta_BIC=10.96369368` to physical model-selection evidence.

## TEST F02: bounded parameter profiling — EXPLORATORY / OPTIMUM NOT CERTIFIED

Optimization used the same 13 means and full covariance, independently implemented numerical BAO predictions, Cholesky whitening, scipy.optimize.least_squares (52 different RLL initializations) and one separate differential-evolution run that did not converge to the lowest found basin.

Bounds: `H0 [55,85]`, `Om [0.10,0.50]`; RLL additionally `Os [0,0.25]`, `zt [0.05,3.0]`, `wt [0.05,1.5]`. Fixed `rd` and `Or`. These are exploration bounds, NOT observational priors.

| Model | lowest found chi2 | parameters |
|---|---:|---|
| LCDM (2 fitted) | 10.284009526976376 | H0=69.038743603, Om=0.297136567 |
| RLL (5 fitted) | 7.813068489597264 | H0=71.74798166, Om=0.1345220919, Os=0.1339438339, zt=0.3987865349, wt=0.0500000000 |

`delta_chi2=-2.470941037379112`: the extra three fitted variables improve in-sample deviance slightly. If ordinary regular Gaussian IC assumptions and `k=2` vs `5` are **provisionally** imposed:
- `delta_AIC=+3.529058962620888`
- `delta_AICc=+10.900487534049457` (13 observations)
- `delta_BIC=+5.223907035005499`
all for RLL minus LCDM. Positive values favor LCDM for the stated in-sample penalty scheme. **ICs are diagnostic only** because the nested `Os=0` boundary makes `zt,wt` unidentified under the null; `wt` hits the imposed lower bound in the lowest RLL basin; other local minima exist. Asymptotic null tests and Bayesian evidences need proper calibration.

## TEST F03: local identifiability — ILL-CONDITIONED
At lowest-found RLL fit, singular values of the scaled, whitened 13x5 Jacobian (`theta_scales=[70,.3,.1,.4,.1]`): `[365.011,40.074,4.794,1.587,0.504]`.
Approximate scaled Fisher `condition_number~5.25e5`. This depends on parameter scales and local linearization; it indicates weakly constrained combinations, not a proof of non-identifiability.
The derivative columns for `Om` and `Os` are strongly aligned (`correlation ~0.988`). Independent claims about these parameters cannot rely on this small BAO-only sample.

## TEST F04: leave-one-tracer-out robustness — EXPLORATORY, LIMITED RESTARTS

Refit each model using 7 RLL restarts after excluding a whole tracer group, with covariance submatrix, no leakage of omitted samples. Lower chi2 is in-sample only. `delta=chi2_RLL-chi2_LCDM`:

| Omitted block | delta chi2 |
|---|---:|
| BGS | -2.5546 |
| LRG1 | -1.2217 |
| LRG2 | -0.7471 |
| LRG3+ELG1 | -4.1513 |
| ELG2 | -2.4174 |
| QSO | about 0 |
| Lyα | about 0 |

For QSO / Lyα, this bounded search fell into the `Os≈0` basin; it may have missed better local minima. Therefore these rows are **optimizer-diagnostic**, not firm null results. Model rankings across unequal `n` are never pooled by raw chi2.

## Falsification gates and alternative hypotheses

| ID | Hypothesis / target | Minimal rejection or nonpromotion condition | Present state |
|---|---|---|---|
| G01 | RLL has distinctive BAO benefit | Joint bounded/multi-start improvement fails to overcome calibrated complexity penalty and held-out performance | no warranted superiority |
| G02 | RLL transition parameters are identified | Boundary-hit, unstable posterior, or near-singular Fisher after scaling | preliminary warning observed |
| G03 | Proxy `fsigma8` is a physical growth observable | No solved D(z), normalization, perturbation equations and verified RSD covariance | proxy cannot be promoted |
| G04 | Claimed curvature/geodesy bridges matter physically | No independent observable, dimensional analysis, FLRW null test, covariance and uncertainty propagation | hypothesis only |
| G05 | RLL beats CPL/w0waCDM | Failure versus independently optimized CPL on same full likelihood/priors | comparative test not performed |
| G06 | Robust independent cosmology | Cannot reproduce with CLASS/CAMB, joint CMB/SNe/RSD, full cross-covariance and independent holdout | external validation not performed |

Useful research comparators, without assuming they support RLL:
- https://www.alphaxiv.org/abs/2604.07244 — Heinesen & Clifton: FLRW geometric consistency observables `C(z)=0` and curvature operators. Null tests test **geometry**, not preference between two models that both assume flat FLRW.
- https://www.alphaxiv.org/abs/2606.23936 — DESI DR1 full-shape/bispectrum + DR2 BAO: cross-covariance/prior-volume sensitivity.
- https://www.alphaxiv.org/abs/2607.13283 — multi-model H0 competition on common likelihoods.
- https://www.desi.lbl.gov/2025/03/19/desi-dr2-results-march-19-guide/ — DESI observables and systematics.
- https://academic.oup.com/mnras/article/494/1/819/5801028 — independent growth-to-expansion inverse relation.
- https://www.darkenergysurvey.org/des-y6-cosmology-results-papers/ — newer independent geometric/growth constraints.

Suggested falsifying experiment: pre-register blind blocks (DESI 13 covariance, cosmic chronometers, Pantheon+ full covariance, CMB, RSD with real growth D(z)); common optimizers and well-stated priors for LCDM, CPL and RLL; exact data/code hashes and covariances; multiple seeds and posterior convergence; profile likelihood calibrated at `Os=0` nonregular boundary; posterior predictive checks; leave-survey-out, permutation of nuisance structures only when physically justified; independent CLASS/CAMB control.

Geometry and wave-function analogies should never be interpreted as evidence of plasma gravity or quantum cosmology without equations and observables for the proposed physical bridge.

## Reconstructibility / receipt
- READ: Drive CURRENT_STATE Ω V4.5 + START HERE Ω V2.2; Github source files listed above; official Cobaya dataset; alphaXiv papers.
- COMPUTATION: independent local SciPy/NumPy bounded screening, 64-point Gauss-Legendre integration compared with adaptive integration, Cholesky covariance inversion, 52 RLL multi-start fits, 7 leave-tracer-out diagnostics.
- EVIDENCE: numerical results above; source file Git blobs; no fabricated CI proof.
- SCOPE: BAO-only, independent diagnostic; does **not** validate physical perturbations, gravitation, plasma effects, apk/device state or worldwide parameter inference.
- F_gap: external full-likelihood, null-calibrated p-value, prior sensitivity, CLASS/CAMB, blinded heldout, independent referee, calibrated global minimization.
- F_next: run exact-source, archival, versioned output of the profiled/heldout test in governed CI; challenge RLL against CPL and real independent RSD growth. No existing code/production artifact changed.
- `claim_allowed=false`, `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`, `IMPLEMENTED_UNTESTED != PASS`.
