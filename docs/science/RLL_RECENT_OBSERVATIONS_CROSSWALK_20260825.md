# RLL recent observations crosswalk — 2026-08-25

State: `PASS_PRIMARY_SOURCE_CROSSWALK_SCIENTIFIC_EXECUTION_OPEN`  
Claim boundary: `claim_allowed=false`  
Checked: `2026-08-25T08:08:27Z` (`05:08:27 BRT`)

This is an append-only successor to the latent-thesis registry and July crosswalk. It binds active cosmology routes to dated primary publications and records what is materialized, what likelihood is still missing, which adversary must be used and what would falsify the route.

| Observation family | Primary record | Latest recorded revision | Safe RLL role | Current gate |
|---|---|---|---|---|
| DESI DR2 BAO | [arXiv:2503.14738](https://arxiv.org/abs/2503.14738) | 2025-10-09 | test input + CPL context | limited points/covariance summary materialized |
| DES-Dovekie SNe | [arXiv:2511.07517](https://arxiv.org/abs/2511.07517) | 2026-03-27 | recent SN adversary/calibration context | canonical vector/covariance/likelihood `TOKEN_VAZIO` |
| DES Y6 3×2pt | [arXiv:2601.14559](https://arxiv.org/abs/2601.14559) | 2026-01-29 | growth/lensing discriminator | data vector/covariance/likelihood `TOKEN_VAZIO` |
| ACT DR6 CMB | [arXiv:2503.14452](https://arxiv.org/abs/2503.14452) | 2025-06-24 | early-universe adversary | full likelihood + exact release/rights receipt `TOKEN_VAZIO` |
| Pantheon+ | [arXiv:2202.04077](https://arxiv.org/abs/2202.04077) | 2022-11-14 | SN baseline/reproduction | canonical full covariance reconciliation `TOKEN_VAZIO` |

## Coherence rule

```text
paper metadata -> hypothesis selection
dataset + rights + SHA256 -> custody
observable schema + covariance -> likelihood input
same likelihood + baselines -> fair comparison
multi-seed posterior + falsifier -> result
result + gate review -> claim decision
```

The current smoke result remains a negative/bounded baseline: RLL is not preferred and `Os0=0.0`. This crosswalk does not overwrite it.

## Gates

G0 source/rights freeze and G1 schema are partial. G2 full covariance, G3 likelihood parity, G4 baseline recovery, G5 robust inference and G6 physical growth/perturbations remain open. Therefore G7 claim decision is blocked.

`F_ok` = five primary-source observation families are dated and crossed to LT-001/002/003.  
`F_gap` = full SN, DES Y6, ACT likelihoods; rights; unified covariance; robust parity run; growth backend.  
`F_next` = freeze one rights-cleared full SN likelihood, reconcile covariance, then run LCDM/wCDM/CPL/RLL with identical inputs and robust multi-seed diagnostics.
