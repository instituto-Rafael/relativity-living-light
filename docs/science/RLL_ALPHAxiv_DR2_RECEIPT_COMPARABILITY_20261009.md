# RLL Android receipt v2 — αXiv DESI DR2 external comparator (2026-10-09)

**Authority:** external scientific paper (not RLL validation). Source: Gan Gu et al., *Dynamical Dark Energy in light of the DESI DR2 Baryonic Acoustic Oscillations Measurements*, [arXiv:2504.06118v3](https://arxiv.org/abs/2504.06118), v3 dated 2025-09-01, accessed using connected alphaXiv text. Original authors retain their copyright and licenses; no article content or third-party code is redistributed here. This is a short interpretation and falsifiability note.

## What the research does and does not show
- The study investigates DESI DR1/DR2 BAO with three Type Ia SN compilations (PantheonPlus, Union3, DESY5) and CMB distance priors. Reconstructs w(z) via shape-function and correlated-prior/nonparametric methods and compares departure from ΛCDM with sensitivity to dataset combinations, priors and possible systematics.
- Its abstract describes moderate Bayesian evidence for dynamic dark energy in some comparisons and approximately 3σ tension with ΛCDM (dataset/method dependent). This is **not confirmation of any particular new RLL model** and must not be mapped to RLL confidence levels.
- A model-only H(z) calculation, BAO distance-ratio *proxy*, numerical quadrature convergence, or normalization E²(0)=1 is a self-check, not real observational likelihood or posterior evidence.
- A single H(z) manually entered on Android without dataset origin, sigma, cross-probe covariance, model priors and independent numerical pipeline cannot reproduce the reported DESI DR2 statistical preference or establish cosmological validity.

## Source → artifact → execution → evidence → claim
1. **External SOURCE:** alphaXiv paper arXiv:2504.06118v3; scope BAO+SN+CMB and the paper's published priors/methodology.
2. **Android SOURCE:** RLL FormulaEngine v2 on branch `fix/rll-android-receipt-observation-sweep-20261009`; native C diagnostic comes from user-submitted runtime, distinct from publication.
3. **ARTIFACT:** debug APK produced by GitHub Actions at exact HEAD and its scoped SHA; its existence is not device installation.
4. **EXECUTION:** JVM on GitHub run 37901249056 reports 42 assertions and unsigned APK build success. User-submitted native ARM32 v1 reports 4/4 JNI Java vs C scores; v2 physical rerun not yet done.
5. **EVIDENCE:** v1 RLL and wCDM residual/χ² transcripts omit Hobs/Hsigma; if interpreted as same Hobs and positive sigma, the relation `(rR-rW)*sigma=H_W-H_R` would imply negative sigma. **Thus the v1 one-point χ² values are not inter-model comparable.** The user might simply have changed manual inputs.
6. **CLAIM:** `claim_allowed=false`; no RLL preference, dark-energy discovery, DESI validation, external reviewer endorsement or physical approval inferred.

## Four independent gates

| Gate | Required evidence | Current state |
|---|---|---|
| G-CODE | exact-HEAD branch static source falsifiers + Java numeric selftest, Android build | Java 42 PASS + Android debug build PASS at earlier SHA; Python static CI gate newly added, pending execution on new SHA |
| G-RUNTIME | v2 receipt on real ARM32 with exact app version/code/signer evidence and 4-vector JNI retest | TOKEN_VAZIO_NOT_RUN |
| G-OBS | paired RLL/wCDM runs with identical provenance-tagged Hobs, positive Hsigma and redshift, source of measurement + covariance | TOKEN_VAZIO_NOT_RUN |
| G-SCI | independent DESI DR2 BAO likelihood/covariance, SNe+CMB priors and physically specified r_d, growth/CAMB/CLASS as relevant | TOKEN_VAZIO_NOT_RUN |

Do not equate `fsigma8 = sigma8*Ω_m(z)^0.55` with a solved growth ODE, the empirical r_d scaling with a full sound-horizon code, or the CMB shift proxy with a CMB likelihood.

**No upstream physical model changes in this increment.** Preserve historical v1 receipts and SHA-256s; add a new v2 receipt only from a new application execution. On rollback revert only this note and the standalone CI workflow from the feature branch. Do not merge without the repository's authorized review and checks.
