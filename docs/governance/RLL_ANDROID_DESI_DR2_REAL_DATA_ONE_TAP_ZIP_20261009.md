# RLL Android DESI DR2 real-data ZIP experiment (source-first)

User action: a single button fetches two pinned GitHub raw DESI DR2 files via HTTPS and then opens Android ACTION_CREATE_DOCUMENT to save a research ZIP. The system save dialog requires user confirmation; no automatic installation or remote upload occurs.

## Authenticated source boundary
Original scientific results: DESI DR2 arXiv:2503.14738. Bytes downloaded from CobayaSampler/bao_data at pinned commit bb0c1c9009dc76d1391300e169e8df38fd1096db.
Mean 13 points: desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_mean.txt SHA1 git blob 8aff444fdb42c0946342aa0011ab287eda097c4c.
Covariance 13x13: desi_bao_dr2/desi_gaussian_bao_ALL_GCcomb_cov.txt SHA1 git blob fd8e5697ab61379b07b52efb781ea6713417a4d9.
Source host strict HTTPS, commit and blob fixed; no redirects; bounded 64 KiB; wrong matrix/negative-definite/nonfinite/incomplete files abort instead of producing fit.
These data are from a public scientific repo, but repository-wide redistribution rights are not attested. The ZIP is intended for the researcher's local use; republishing source data requires checking rights.

## Scientific and parameter stability boundaries
Four background families LCDM/WCDM/CPL/RLL. A complete Gaussian quadratic form uses the 13x13 covariance via Cholesky: chi2=(prediction-observation)^T C^-1(prediction-observation).
Model input parameters are prespecified and closed E2(0)=1. Only local, fixed finite differences in Om (+/-0.005), H0 (+/-0.5), and zt (+/-0.05 RLL) are measured. There is no numerical optimizer, no best-fit, posterior, Bayes factor or claim of preference.
BAO model calculations currently use a calibrated empirical r_drag proxy instead of a physically model-matched sound-horizon code. A cosmological validation must compare against independent DESI priors/likelihood and CLASS/CAMB or a validated model-specific compressed likelihood.
RMRCTI stability source: llamaRafaelia/rmrCti/RMRCTI_DELTA_P_STABILITY_CONTRACT.md; DeltaP=P(stable_any=1|peak)-P(stable_any=1|nonpeak). BAO table lacks these indicators, so DeltaP is TOKEN_VAZIO_NO_STABLE_ANY_PEAK_TRACE, never fit to 0.18.
Torus R=2,r=0.7 2D parametrization closure is a geometric identity, NOT a Poincare recurrence or cosmic dynamic stability proof. No Poincare recurrence inferred from sparse redshift samples.
Literature references: arXiv:2503.14738 primary BAO; arXiv:2504.06118 external DR2 dark energy comparator; arXiv:2606.18455 CMBComp model-specific compressed likelihood validation, RLL not among five validated model classes.

## ZIP evidence and device boundary
Raw files and their SHA256, predicted and observed data CSV, model chi2 and sensitivity CSV, parameter/source receipt, local installed-package PackageManager first/last install time, version/code, APK SHA256 if readable and signing certificate SHA256, and per-entry SHA256 manifest.
PackageManager data are self-reported on a real app execution, not independent cryptographic device attestation. A ZIP is portable; no proprietary RAR encoder is used.
All data stays on-device except the two user-requested HTTPS downloads. No new manifest permissions, no arbitrary storage access, and no user identity or private conversations are sent.

## Tests, gates, rollback
Standalone hosted Java test checks synthetic 13x13 covariance, model invariants, fixed parameter sensitivity, SPD rejection, git pins, and torus geometric closure; Android CI compiles debug/unsigned for ARM32 and ARM64. Neither test alone proves physical install.
Rollback only new adapter/engine/tests/workflow/MainActivity hooks/docs. No changes to RLL scientific source/old results or llamaRafaelia primary RMRCTI engines.
claim_allowed=false