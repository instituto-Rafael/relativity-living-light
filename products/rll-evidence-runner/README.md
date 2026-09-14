# RLL Evidence Runner V1

A fail-closed product surface for executing or replaying scientific experiments while preserving evidence boundaries.

```text
experiment YAML
→ schema and policy validation
→ input identity and sidecar verification
→ argv execution without shell=True
→ output hashing
→ model metric extraction
→ baseline comparison
→ semantic receipt
→ verification
```

## Non-authorizations

```text
claim_allowed=false
publication_effect=NONE
CI PASS != scientific truth
replay != fresh fit
readiness != likelihood
numerical preference != confirmation
TOKEN_VAZIO != PASS
```

## Install

From the repository root:

```bash
python -m pip install -e products/rll-evidence-runner
```

## Core commands

```bash
rll-evidence validate products/rll-evidence-runner/experiments/joint_real_lcdm_rll_v1.yml
rll-evidence run products/rll-evidence-runner/experiments/joint_real_lcdm_rll_v1.yml
rll-evidence verify artifacts/evidence/RLL-EVIDENCE-JOINT-REAL-001/receipt.json
rll-evidence compare artifacts/evidence/RLL-EVIDENCE-JOINT-REAL-001/receipt.json \
  --baseline LCDM_joint_real --candidate RLL_joint_real
```

## Pantheon+ full covariance

Materialize and verify the official matrix outside Git:

```bash
python scripts/fetch_pantheon_covariance.py
rll-evidence run \
  products/rll-evidence-runner/experiments/pantheon_full_covariance_readiness_v1.yml
```

Execute the model-bound fit:

```bash
rll-evidence run \
  products/rll-evidence-runner/experiments/pantheon_full_covariance_lcdm_rll_fit_v1.yml
```

The adapter is also exposed directly:

```bash
rll-pantheon-fit \
  --catalog data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat \
  --covariance data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES_STAT+SYS.cov \
  --output artifacts/evidence/RLL-EVIDENCE-PANTHEON-FIT-001/pantheon_fit_result.json \
  --seeds 11,23,37,53,71 \
  --maxiter 250
```

### Likelihood contract

```text
observable              = m_b_corr
selection               = (zHD > 0.01) OR IS_CALIBRATOR == 1
calibrator prediction   = CEPH_DIST
Hubble-flow prediction  = 5 log10[(1+zHEL) D_C(zHD)] + 25
covariance              = full STAT+SYS selected as C[mask, mask]
nuisance                = M_B analytically profiled and counted in k
linear algebra          = Cholesky solve, no diagonal approximation, no jitter
optimizer               = deterministic multi-start L-BFGS-B
models                  = flat LCDM and flat RLL logistic transition
```

The first start is the nested null point (`Omega_s0=0`) and the remaining starts are generated from frozen seeds. Every run records initial values, final parameters, convergence state, boundary hits, evaluations and runtime.

### Result boundary

The generated JSON contains rows compatible with the Evidence Runner extractor:

```text
chi2, AIC, AICc, BIC, N, k, dof
```

A favorable delta is only a numerical result inside this Pantheon+SH0ES likelihood. It does not authorize a claim of physical confirmation, superiority, external validation or publication readiness.

## Receipt model

Each receipt contains:

- experiment and commit identity;
- Python/platform context;
- input and output hashes;
- exact argv and exit state;
- bounded stdout/stderr;
- extracted model metrics;
- candidate-minus-baseline deltas;
- `F_ok`, `F_gap`, `F_next`;
- a semantic digest excluding wall-clock duration;
- a full receipt digest;
- invariant `claim_allowed=false`.

## Profiles

| Profile | What it proves | What it does not prove |
|---|---|---|
| Joint-real replay | Existing result artifact is readable, hashed and compared consistently | Fresh optimization or independent replication |
| Pantheon readiness | Catalog and covariance satisfy strict presence/integrity gates | Likelihood execution or cosmological preference |
| Pantheon full fit | LCDM and RLL are evaluated on the same selected full covariance with frozen seeds and bounds | Independent validation or a complete joint cosmological analysis |

## Current continuation

```text
F_ok   = model-bound full-covariance adapter implemented
F_gap  = real matrix execution and independent cross-implementation receipt not yet committed
F_next = execute, reproduce externally, then compose with DESI BAO, H(z), growth and CMB
```
