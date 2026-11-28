# RLL background / growth / CMB — successor candidate V1

Status: LOCAL_SCOPED_TESTS; full repository CI, provider write, real-data runner and physical claims NOT_RUN. claim_allowed=false. Base inspected: rll/lab c73b560bed94f12a9c9714afc556615fa907a937. Predecessor PR #1260 (head 0a53a4a08efd96a3877232fc1fcf6d840fe12bff; observed open). No changes to the predecessor or historical outputs. Producer model functions in rll_vs_lcdm.py (blob 6ff9d76d6dfa5859e139521af29f876bfc049c84). The local test harness used a manually transcribed excerpt of those functions, not a full checkout. Do not ship the excerpt as a second producer.

## Route and non-regression

- BG is an observable capability, not a replacement for the F/C/I/S/U/G hypotheses. F is phenomenology; C and I need distinct perturbation closure; S/U/G remain open. GR and CMB capability gates do not select a physical winner.
- Use `data/pipelines/structure_d/background_likelihood_v1.py` as opt-in adapter. Canonical low-z producer reused; radiation omitted in this route. Flatness, finite parameters, explicit free rd, covariance SPD, ordered row keys, separate SN compilations, overlap groups, SN offset profiling. No automatic covariance or zero fallback. Source/overlap identity is caller-declared; a trusted manifest is still required for non-DESI inputs. SN_mu assumes calibrated distance-modulus data with z_hel and z_cos and a single additive offset, not a universal SN raw-light-curve likelihood.
- `run_background_desi_v1.py` reuses the existing producer's native covariance order guard, refuses summary fallback, and checks input hashes. It fits the BAO-only shape with H0 fixed to 70 as an arbitrary pivot (only H0*rd identifiable). No H0 or rd physical inference individually. Bounds are candidate engineering choices, not physical priors: vary in subsequent sensitivity tests. Same seed set, per-model convergence, nested-null optimizer check. AIC/AICc/BIC descriptive, not evidence; RLL null boundary makes standard likelihood-ratio asymptotics nonregular. No joint likelihood or MCMC claim.
- Existing `joint_real_likelihood.json` and flat/Rx successors preserved. The historical N=64 artifact has LCDM chi2=93.9535456, CPL=63.1195546, RLL=93.9598307 and RLL Os0=0. The old `lcdm_preferred` label contradicts CPL ranking; legacy flatness also requires attention (LCDM Om+OL > 1 in artifact). These are historical metrics, not reproduced here.
- Current H(z) CSV contains 27 rows tagged CC_Moresco2022, four CC+BAO_BOSS and one BAO_Lya. The latter five must not silently be labeled pure chronometers. Independence and full CC covariance still require verification. Do not claim overlap is proven solely by a similar tracer label.
- RLL high-z limit: with f->0, E_RLL^2~(Om+Os0)(1+z)^3 in the matter era; matter-like slope does NOT imply convergence to LCDM amplitude at fixed Om. With Om=.315, Os0=.02 the limiting H ratio is sqrt(.335/.315). Early radiation/perturbations not covered. Test whether the effective matter is clustered before CMB or growth interpretation.

## Sources and data gates (cut-off 2026-11-27)

| Probe | Published observation or inference | Next gate |
|---|---|---|
| DESI DR2 BAO | >14 million objects; BAO-CMB flat LCDM parameter tension 2.3 sigma, not a RLL detection | source https://doi.org/10.1103/tr6y-kpc6; reuse 13-point native binding guard |
| Ly-alpha AP+BAO | z=2.33, DH/rd=8.600 +/- .066 and DM/rd=39.32 +/- .33 | https://arxiv.org/abs/2607.27410; replace overlapping Ly-alpha block only with official joint covariance and validated cross-block assumptions; never append by default |
| DESI CC | z=.46, .67, .83; H=88.48,119.45,108.28; stat .57,6.39,10.07; syst 12.32,16.64,15.08 km/s/Mpc | https://arxiv.org/abs/2511.02730; reconcile systematics and correlations before inference |
| SN recalibration | DES-Dovekie updated calibration and color law; comparison with Pantheon+ and Union3 is compilation-dependent | https://doi.org/10.1093/mnras/stag632; native release, covariance and calibration mode required separately |
| Updated joint literature | Union3.1/Dovekie, DESI DR2/DES Y6 BAO, Planck and 38 CC; ~3 sigma preference not decisive Bayes evidence | https://doi.org/10.1093/mnras/stag1607; audit overlap, exact selection, likelihood and priors |
| ACT DR6 | H0=68.43 +/- .27 with DESI DR2 under LCDM; concordance 1.6 sigma | https://doi.org/10.1088/1475-7516/2025/11/062; full TT/TE/EE+lensing with model-dependent transfer functions, not an H0 prior independent of BAO |
| DESI local growth | fs8(.07)=.450+/-.055, gamma=.58+/-.11 with ShapeFit | https://doi.org/10.1088/1475-7516/2026/04/026; validate growth closure and avoid reuse of overlapping consensus inputs |

## Acceptance and execution

At clean lab checkout, apply patch without rewriting history. Run:

```
python -m unittest discover -s tests -p test_background_likelihood_v1.py -v
python -m data.pipelines.structure_d.run_background_desi_v1 --output /tmp/rll_bg_desi_20261127.json
```

Run existing producer tests, branch maturity and exact-head CI; compare legacy output with unchanged inputs; preserve receipt and failed seeds. Holdouts must use independent blocks; SN holdout offset profiling is not a fixed-calibration out-of-sample prediction. Test coverage using null mocks, predeclared thresholds, multi-seed/prior sensitivity, explicit r_d policy, full covariances, convergence and no data reuse. CMB/growth remain TOKEN_VAZIO_PHYSICAL_CLOSURE. No mutation of workflows or permission/ruleset. Rollback: do not apply the patch or revert its future isolated commit (no history rewriting). No merge authorized by this artifact.
