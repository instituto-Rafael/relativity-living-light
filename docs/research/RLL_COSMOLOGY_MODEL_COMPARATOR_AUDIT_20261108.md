# RLL 2026-11-08 — Comparator evidence matrix, source-separated

State: RESEARCH DRAFT/HOLD, claim_allowed=false. This document is a read-only evidence audit, not a new cosmological fit or a physics validation.

## What differs?

Positive delta χ² = χ²(RLL) − χ²(LCDM): RLL fits worse in that particular experiment. Negative = better *raw* fit, not a global model victory.

| Regime and committed source | N | χ² LCDM | χ² RLL | Δχ² | Critical boundary |
|---|---:|---:|---:|---:|---|
| results/audit/rll_model_evidence_scan.json + results/structure_d/joint_real_likelihood.csv | 64 | 93.9535456 | 93.9598307 | +0.0062851 | H(z), DESI BAO, fσ8, compressed CMB shift; k 5/8 |
| data/results/desi_dr2_bao_model_comparison.json | 13 | 28.6937410 | 34.5275360 | +5.8337950 | 13x13 BAO, fixed current parametrization |
| results/RLL_chi2_results.csv | 45 | 123.681 | 123.968 | +0.287 | historical setup, k 4/7 |
| data/results/model_comparison.json | 64 | 82.9162470 | 256.0005237 | +173.0842766 | a DIFFERENT joint setup, k 2/5; never conflate with first N=64 |
| results/growth_comparison_rll_vs_lcdm.json | 16 | 18.9391112 | 17.9234628 | −1.0156484 | linear growth proxy, diagonal-only errors |

Same number N=64 does not establish same observations, likelihood, nuisance, covariance, priors, initial conditions or optimizer. No combining, ranking, averaging or difference of χ² across these regimes.

## First N=64 information criteria

| Model | χ² | AICc | BIC | k |
|---|---:|---:|---:|---:|
| CPL | 63.1195546 | 79.1195546 | 92.2317362 | 7 |
| LCDM | 93.9535456 | 104.9880284 | 114.7479610 | 5 |
| wCDM | 92.7942706 | 106.2679548 | 117.7475691 | 6 |
| RLL | 93.9598307 | 112.5780125 | 127.2308954 | 8 |

RLL−LCDM ΔAICc +7.5899841; RLL−CPL ΔAICc +33.4584579; RLL−LCDM ΔBIC +12.4829343. The authorial Omega_s0 hits zero in this fit. The original committed scan states CLAIM_BLOCKED. AICc and BIC are not integrated Bayes evidence.

## Computes already, vs remaining

- Present scoped: background H(z), distances, DESI BAO with a full 13x13 matrix in its own route; joint proxy with a *compressed* CMB shift; linear D(z), fσ8 and approximate growth comparison. Model families LCDM, wCDM, CPL, GEDE, IDE, RLL have background contracts.
- Not demonstrated as complete RLL output: CMB TT/TE/EE/lensing spectra from Boltzmann evolution; nonlinear matter P(k,z), N-body and baryonic feedback; model-specific perturbative sound-speed/anisotropic-stress/stability closure; independent RLL CLASS/CAMB cross-check; modern lensing 3x2pt full likelihood.
- Inference boundary: G6 H52 showed limited longer-chain MCMC convergence, NOT closed nested multiseed evidence stability nor independent replication. Pantheon+ full STAT+SYS with nuisance M_B should be combined with primary DESI covariance and pure chronometers in ONE canonical G4/G5 likelihood before comparing priors/evidence.
- Exact missing observation is TOKEN_VAZIO, not zero. Presence of a kernel does not imply physical validation.

## Executable audit

Tool tools/ci/rll_comparator_evidence_matrix_v1.py reads eleven actual committed sources, hashes each SHA256, validates component χ² sums, χ²/AIC/AICc/BIC, N/k/dof, DESI delta, growth boundaries, claim_allowed flags and missing CMB/nonlinear output. No data fitting, score optimization or modification of old results.

Run from the root:

    python3 -m unittest discover -s tests -p test_rll_comparator_evidence_matrix_v1.py -v
    python3 tools/ci/rll_comparator_evidence_matrix_v1.py --root . --output artifacts/python-tests/rll_comparator_evidence_matrix_v1.json

CI inserts ONE scoped check before the unchanged original pytest; PASS_SCOPED is not global CI PASS. RLL scientific claims remain HOLD. Never weaken historical negative gates.

NEXT: reconcile two N=64 regimes via exact dataset/covariance/prior hashes and model parameter counts, then run frozen G4/G5/G6 and compare with CLASS/CAMB perturbations. SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM. Rollback closing PR or reverting only additive files/step.
