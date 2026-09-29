# RLL Real Validation — Operational Coherence Prompt

You are in the repository relativity-living-light.

Goal:
Generate an auditable real-data model comparison artifact:

data/results/model_comparison.json

using Pantheon+ real data and covariance, comparing RLL vs ΛCDM conservatively.

Publication language:
RLL is a candidate effective dynamic-transition cosmology under real-data evaluation.

Claim boundary:
No superiority claim unless real-data metrics pass predefined thresholds.

Required inputs:
- Pantheon+ light-curve file
- Pantheon+ covariance matrix
- SHA256 for every real-data file
- exact command used
- git commit hash
- Python/package versions

Required metrics:
- n_obs
- k_rll = 5
- k_lcdm = 2
- chi2_rll
- chi2_lcdm
- AIC_rll
- AIC_lcdm
- BIC_rll
- BIC_lcdm
- delta_chi2_rll_minus_lcdm
- delta_aic_rll_minus_lcdm
- delta_bic_rll_minus_lcdm
- interpretation_label

Formulas:
AIC = chi2 + 2k
BIC = chi2 + k * ln(n_obs)

Deltas:
delta_chi2_rll_minus_lcdm = chi2_rll - chi2_lcdm
delta_aic_rll_minus_lcdm = AIC_rll - AIC_lcdm
delta_bic_rll_minus_lcdm = BIC_rll - BIC_lcdm

Implement:
interpret_model_comparison(delta: dict) -> dict

Allowed labels:
- inconclusive
- lcdm_preferred
- rll_preferred_tentative
- rll_preferred_strong

Conservative thresholds:
- Missing/invalid AIC or BIC: inconclusive
- delta_aic > 0 or delta_bic > 0: lcdm_preferred
- delta_aic <= -2 and delta_bic <= -2: rll_preferred_tentative
- delta_aic <= -6 and delta_bic <= -6 and delta_chi2 < 0: rll_preferred_strong
- otherwise: inconclusive

Tasks:
1. Inspect scripts/run_real_pantheon_validation.py.
2. Ensure it produces data/results/model_comparison.json from data/results/pantheon_fit_summary.json.
3. Add SHA256 tracking for every real-data file.
4. Add exact command tracking.
5. Add git commit hash tracking.
6. Add Python/platform/package version tracking.
7. Calculate chi2, AIC, BIC and deltas.
8. Add conservative interpretation into delta.
9. Preserve k_rll = 5 and k_lcdm = 2.
10. Add or update tests.

Tests must verify:
- required JSON fields exist
- k_rll == 5
- k_lcdm == 2
- AIC/BIC formulas
- deltas equal RLL minus ΛCDM
- interpretation_label is one of the allowed labels
- claim_boundary exact string
- no fake real-data result is accepted when Pantheon+ files are missing

Optional:
Generate data/results/model_comparison_report.md with:
- dataset
- n_obs
- file paths
- SHA256
- exact command
- git commit
- environment
- RLL vs ΛCDM table
- deltas
- interpretation
- claim boundary
- publication-safe language

Forbidden claims:
- RLL proves ΛCDM wrong
- RLL beats ΛCDM
- RLL is superior
- RLL is confirmed

Run:
pytest -q

Return:
- modified files
- technical summary
- test result
- generated artifact path
- interpretation result
- whether any superiority claim is allowed

Make the smallest logical commit.
