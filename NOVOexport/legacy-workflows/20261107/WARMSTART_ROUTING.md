# RLL prewarm G4→G5 and legacy YML orchestration (DRAFT/HOLD)

**Authority:** producer `instituto-Rafael/relativity-living-light`. Do not merge before provider CI and independent review.

## Source / archive route

- `NOVOexport/legacy-workflows/20261107/workflows_index.json`: all 133 original files, exact Git blob SHA-1.
- `.github/workflows/rll-legacy-archive-index.yml`: verifies archived files; cannot run archived YML outside `.github/workflows`.
- Three manual aliases preserve same workflow name/job/FASE24 executor; other old workflows untouched.
- `001_PONTEIRO/RLL_WARMSTART_YML_CURRENT.md`: short state link.

## Pipeline

```text
00 original archive & source SHA → 01 DESI DR2 13x13 / Pantheon+ manifest
 → 02 six baseline models and seven-parameter provenance gate
 → [manual dispatch only: run_g4_g5]
 → 03 download and verify pinned full Pantheon STAT+SYS covariance
 → 04 run original G4 six-model 5-seed background optimizer
 → 05 freeze G5 same likelihood, data, nuisance and covariances
 → 06 G6/CMB/G8/G9/G10 separately; never implicit promotion
```

`workflow_dispatch=preflight` is inexpensive. PR CI runs preflight only. `workflow_dispatch=run_g4_g5`
requests an expensive fitting run on real data, after external covariance checksum verification.
Some source data is not committed (Pantheon full covariance); missing inputs fail closed.

## Seven parameters ≠ seven torus coordinates

A full wCDM-CMB standard profile can use `omega_b`, `omega_c`, `theta_star`,
`ln10As`, `ns`, `tau`, `w`. This is a seven-parameter **full CMB** model and
needs early-time/perturbation likelihood. The existing G4 *background-only* fit
uses `H0`, `Omega_m`, `omega_b_h2` plus model-specific free parameters and
the profiled `M_B` SN nuisance. Pantheon+ and DESI BAO alone do not identify
all seven CMB parameters. No G4 result may be labeled a seven-parameter fit.

## Dataset identity and non-regression

- DESI is a survey; BAO is an observational standard-ruler measurement.
- Pantheon+ is a Type-Ia supernova sample, not a cosmological theory.
- ΛCDM/wCDM/CPL/GEDE/IDE/RLL compare under the original G4/G5 contract.
- No synthetic diagonal substitution, no model-specific hidden observation filtering.
- CI structural PASS ≠ cosmological evidence ≠ Bayesian evidence.
- No artifact upload from the new workflows while the GitHub storage quota is constrained.
- Existing governance/check workflows remain active until dependency-compatible migration.
- `SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM`.

## Reproduction and rollback

```bash
python tools/ci/rll_warmstart_preflight_v1.py
python tools/ci/rll_warmstart_preflight_v1.py --archive-only
python -m unittest discover -s tests -p test_rll_warmstart_preflight_v1.py -v
```

Close DRAFT PR to roll back. Exact legacy workflows recoverable from Git blobs.
Main, existing real-data pipelines, requirements and model kernels are unchanged.
Scientific promotion: `claim_allowed=false` until independently established.
