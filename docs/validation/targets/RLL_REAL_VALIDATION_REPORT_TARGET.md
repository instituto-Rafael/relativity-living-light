# RLL Real Validation Report — Target

Required artifact:
- data/results/model_comparison.json

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

Claim boundary:
No superiority claim unless real-data metrics pass predefined thresholds.

Publication language:
RLL is a candidate effective dynamic-transition cosmology under real-data evaluation.
