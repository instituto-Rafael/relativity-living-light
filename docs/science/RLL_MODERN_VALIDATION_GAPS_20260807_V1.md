# RLL — Modern observational validation gaps — 2026-08-07 V1

Status: `CANONICAL_DRAFT` / `claim_allowed=false` / `publication_ready=false`

This note translates current cosmology observations and recent literature into executable, fail-closed RLL validation gates. It does **not** promote any RLL scientific claim. Papers provide context and benchmark definitions; only materialized data/likelihood/replication receipts can close a gate.

## 1. Operational rule

`source -> immutable provenance -> likelihood -> shared priors/nuisance policy -> fit -> evidence -> independent reproduction -> human review`

If any required element is absent, the state remains `TOKEN_VAZIO`.

The machine-readable authority for this cycle is:

- `data/governance/RLL_MODERN_VALIDATION_GAPS_20260807_V1.json`
- evaluator: `scripts/rll_modern_validation_gate.py`
- tests: `tests/test_rll_modern_validation_gate.py`
- CI: `.github/workflows/rll-modern-validation-gate.yml`

## 2. What changed in the modern observational landscape

### DESI DR2: the benchmark is joint-likelihood reproduction, not one Delta-chi2

DESI DR2 Results II reports that flat LambdaCDM remains a good description of DESI BAO alone, while combinations with CMB and supernovae can prefer w0wa/CPL-like evolution at a significance that depends materially on the supernova compilation. This makes dataset identity, covariance, nuisance treatment and redshift-resolved residuals part of the scientific result.

Primary context:

- DESI Collaboration, DR2 Results II: https://arxiv.org/abs/2503.14738
- Official DR2 publications/data products: https://data.desi.lbl.gov/doc/papers/dr2/

RLL consequence: reproduce the official LCDM/CPL benchmark and per-tracer residual structure before interpreting any RLL improvement.

### Supernova calibration: Pantheon+/DES-SN5YR cannot be treated as a fungible `SN` block

The DES-Dovekie reanalysis updates cross-calibration and related supernova treatment and reports a weaker apparent preference for evolving dark energy than the earlier DES-SN5YR combination. Independent model-independent analyses also show that inferred dark-energy evolution is strongly coupled to the matter-density preference of the chosen SN compilation.

Primary/peer-reviewed context:

- DES-Dovekie MNRAS reanalysis: https://academic.oup.com/mnras/article/548/4/stag632/8653925
- Dovekie calibration reassessment: https://arxiv.org/abs/2506.05471
- Model-independent SN comparison: https://arxiv.org/abs/2604.11883

RLL consequence: maintain separate Pantheon+ and DES-Dovekie calibration variants, hash both vector and covariance provenance, and emit redshift-binned residual diagnostics. Diagonal-only SN fits remain exploratory.

### Bayesian evidence: frequentist significance and model evidence are different gates

A 2026 independent Bayesian reanalysis using nested sampling finds that the model preference can change substantially when prior volume and dataset consistency are included; it also reports strong sensitivity to the chosen supernova calibration. This reinforces an existing RLL invariant: a BIC-derived Bayes proxy is not real Bayesian evidence.

Independent analysis:

- https://arxiv.org/abs/2603.05472

RLL consequence: store versioned prior transforms, sampler/version, stopping criteria, per-model `logZ +/- error`, and independent replication. LCDM, CPL and RLL must use the same materialized likelihood components.

### ACT DR6: an independent CMB likelihood is now a useful cross-check

ACT DR6 provides high-precision TT/TE/EE spectra and likelihood products that are independent of a Planck-only compressed shift-vector route.

Primary context:

- https://arxiv.org/abs/2503.14452

RLL consequence: first reproduce the ACT DR6 LambdaCDM reference under a versioned nuisance/foreground policy; only then evaluate CPL/RLL with the same CMB treatment. A compressed summary must remain explicitly labeled `compressed`.

### DES Y6 3x2pt: growth and S8 should be tested against a current low-redshift structure likelihood

DES Y6 combines cosmic shear, galaxy clustering and galaxy-galaxy lensing over the full survey and provides a modern low-redshift growth benchmark.

Primary context:

- https://arxiv.org/abs/2601.14559

RLL consequence: an S8 point estimate cannot close the weak-lensing gap. The likelihood release, covariance, scale cuts and nuisance model must be versioned and evaluated through the same perturbation backend used for the cosmology prediction.

### CAMB v2 + CLASS: background agreement is no longer enough

CAMB v2 updates numerical integration and dark-energy perturbation handling, including stabilized PPF evolution, and documents precision targets suitable for modern surveys. CLASS remains the required independent Boltzmann-code cross-check.

Primary code references:

- CAMB v2: https://arxiv.org/abs/2607.14854
- CLASS: https://class-code.net/

RLL consequence: backend importability is only a technical prerequisite. The validation receipt must compare at least `H(z)`, `D+(z)`, `f*sigma8`, `P(k,z)` and applicable CMB spectra, with fixed parameter points and recorded numerical tolerances. RLL also needs an explicit perturbation contract (sound speed / anisotropic stress / PPF or another well-defined closure) before perturbative claims can be evaluated.

## 3. Gap ledger

| Gate | Current state | What closes it |
|---|---|---|
| Modern SN full likelihood | `TOKEN_VAZIO_MODERN_SN_FULL_LIKELIHOOD` | materialized Pantheon+/DES-Dovekie vector+covariance provenance, same nuisance policy, full-covariance fit, per-z residuals |
| Real Bayesian evidence | `TOKEN_VAZIO_REAL_BAYES_INFERENCE` | nested sampling for LCDM/CPL/RLL, hashed priors, `logZ` errors, stopping diagnostics, independent replication |
| DESI DR2 official reproduction | `TOKEN_VAZIO_DESI_DR2_OFFICIAL_REPRODUCTION` | official product IDs/hashes, canonical 13-observable order, explicit `r_d` policy, LCDM/CPL reproduction, per-tracer residuals |
| ACT DR6 CMB | `TOKEN_VAZIO_ACT_DR6_LIKELIHOOD` | versioned TT/TE/EE likelihood or explicitly compressed equivalent, nuisance policy, LCDM reference reproduction |
| DES Y6 weak lensing/growth | `TOKEN_VAZIO_DES_Y6_3X2PT_LIKELIHOOD` | versioned 3x2pt likelihood, covariance, scale cuts/nuisances, S8 from the physical perturbation backend |
| CLASS/CAMB perturbations | `TOKEN_VAZIO_CLASS_CAMB_PERTURBATION_BENCHMARK` | cross-backend LCDM/CPL benchmark plus explicit RLL perturbation/stability contract |
| Formal modern H0 likelihood | `TOKEN_VAZIO_MODERN_H0_FORMAL_LIKELIHOOD` | separately versioned early/late-time likelihoods, explicit `r_d`/calibration assumptions, `Delta H0 / sigma` under common model policy |

## 4. Existing code that should be preserved, not duplicated

The repository already contains:

- LambdaCDM/wCDM/CPL/RLL background functions and fair AIC/AICc/BIC helpers;
- covariance readiness gating;
- an approximate linear-growth calculation and S8 helper;
- a CLASS/CAMB availability gate;
- joint real-data infrastructure for H(z), DESI DR2 BAO, f-sigma8 and a compressed CMB shift vector;
- fail-closed scientific-cycle closure requiring real Bayesian evidence plus independent replication.

The important unresolved implementation detail is that the current joint likelihood still has an `Omega_m(z)^0.55` f-sigma8 proxy. It must not be relabeled as a CLASS/CAMB perturbation result.

## 5. Required receipts

The evaluator expects these paths and leaves the corresponding gap open when they do not exist or fail the contract:

- `artifacts/science/sn_modern/full_likelihood_receipt.json`
- `artifacts/science/bayes/nested_sampling_receipt.json`
- `artifacts/science/desi/dr2_official_reproduction_receipt.json`
- `artifacts/science/cmb/act_dr6_likelihood_receipt.json`
- `artifacts/science/lss/des_y6_3x2pt_likelihood_receipt.json`
- `artifacts/science/boltzmann/class_camb_benchmark_receipt.json`
- `artifacts/science/h0/distance_ladder_receipt.json`

A receipt is rejected if it is missing, invalid JSON, has a state other than `VERIFIED`, sets `claim_allowed=true`, or omits a declared provenance/result key. The real-Bayes receipt additionally requires `independent_replication=true`.

## 6. Priority order

1. `P0`: modern SN full covariance/calibration ablation.
2. `P0`: official DESI DR2 reproduction.
3. `P0`: real nested-sampling evidence for LCDM/CPL/RLL.
4. `P1`: CLASS/CAMB perturbation benchmark and RLL perturbation contract.
5. `P1`: DES Y6 3x2pt growth/weak-lensing likelihood.
6. `P1`: ACT DR6 CMB cross-check.
7. `P1`: formal H0 early/late-time likelihood comparison.

The ordering is epistemic rather than rhetorical: first fix likelihood/data provenance and fairness, then compute model evidence, then widen the perturbation/growth observables.

## 7. Uncertainty boundary

Recent preprints proposing additional SN population/age-bias explanations are useful as adversarial challenge sets, but they are not used here as a gate-closing authority. They may generate future sensitivity tests after the primary DESI/DES/ACT likelihood reproduction is stable.

`TOKEN_VAZIO` therefore means: the evidence needed to decide has not yet been materialized under the declared contract. It does not mean zero, false, impossible or validated.
