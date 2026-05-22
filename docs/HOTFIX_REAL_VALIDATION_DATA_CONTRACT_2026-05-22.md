# HOTFIX — Real Validation Data Contract

Date: 2026-05-22
Status: hotfix documentation layer
Scope: RLL real-data validation boundary

## Purpose

This hotfix adds an explicit data contract for the real-validation path of Relativity Living Light (RLL), especially the Pantheon+ comparison flow against the equivalent ΛCDM baseline.

The objective is to prevent ambiguous scientific communication and to ensure that future numerical claims are backed by reproducible real-data artifacts.

## Core rule

No superiority claim is allowed unless `data/results/model_comparison.json` exists and contains real-data metrics generated from declared inputs, with provenance, hashes, command, environment, and git commit hash.

## Required real-data inputs

The minimal Pantheon+ validation requires:

1. `data/pantheon/lcparam_full_long_zhel.txt`
2. `data/pantheon/Pantheon+SH0ES_STAT+SYS.cov`

Each file must have:

- source URL or official archive reference;
- download or materialization date in UTC;
- byte size;
- SHA256;
- license/terms note when available;
- local path inside the repository or execution environment.

## Required command sequence

```bash
python scripts/verify_pantheon_inputs.py --json
python -m rll.cli preflight-real --json
python -m rll.cli run --data real --model both --with-covariance
python scripts/run_real_pantheon_validation.py
```

## Required final artifact

The required final artifact is:

```text
data/results/model_comparison.json
```

It must contain at minimum:

- `n_obs`
- `k_rll = 5`
- `k_lcdm = 2`
- `chi2_rll`
- `chi2_lcdm`
- `AIC_rll`
- `AIC_lcdm`
- `BIC_rll`
- `BIC_lcdm`
- `delta_chi2_rll_minus_lcdm`
- `delta_aic_rll_minus_lcdm`
- `delta_bic_rll_minus_lcdm`
- `interpretation_label`
- `claim_boundary`
- `command_used`
- `git_commit_hash`
- `environment`
- `real_data_files_sha256`

## Minimal schema sketch

```json
{
  "n_obs": null,
  "k_rll": 5,
  "k_lcdm": 2,
  "chi2_rll": null,
  "chi2_lcdm": null,
  "AIC_rll": null,
  "AIC_lcdm": null,
  "BIC_rll": null,
  "BIC_lcdm": null,
  "delta_chi2_rll_minus_lcdm": null,
  "delta_aic_rll_minus_lcdm": null,
  "delta_bic_rll_minus_lcdm": null,
  "interpretation_label": "inconclusive",
  "claim_boundary": "No superiority claim unless real-data metrics pass predefined thresholds.",
  "command_used": null,
  "git_commit_hash": null,
  "environment": {},
  "real_data_files_sha256": {}
}
```

## Interpretation labels

The interpretation layer must remain conservative:

- `inconclusive`
- `lcdm_preferred`
- `rll_preferred_tentative`
- `rll_preferred_strong`

These labels are model-comparison labels only. They do not establish a final cosmological replacement claim.

## Publication-safe language

Until a complete real-data artifact exists, use:

> RLL is a candidate effective dynamic-transition cosmology under real-data evaluation.

After a valid real-data artifact exists, use:

> Under the declared Pantheon+ run and its documented assumptions, the RLL-vs-ΛCDM comparison produced the reported chi2/AIC/BIC deltas. Broader cosmological interpretation requires independent replication and cross-dataset validation.

## Claim boundary

```text
No superiority claim unless real-data metrics pass predefined thresholds.
```

## Why this hotfix exists

This hotfix converts the validation discussion into an operational contract. It keeps the archive, symbolic material, and exploratory theory intact, while forcing scientific claims through the reproducible data boundary.

## Next required action

Materialize the Pantheon+ files, run the full sequence, and commit only the normalized `data/results/model_comparison.json` plus its provenance manifest if redistribution rights permit.
