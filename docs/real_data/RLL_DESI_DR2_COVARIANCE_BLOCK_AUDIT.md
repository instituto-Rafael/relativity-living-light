# RLL DESI DR2 BAO Covariance Block Audit

**Status:** `BLOCK_MATRIX_OPERATIONAL / VECTOR_LIKELIHOOD_PENDING / CLAIM_BLOCKED`  
**Scope:** repository-declared covariance blocks associated with `desi_dr2_bao_primary_points.csv`.

## Why this audit exists

The repository already stores:

- 13 primary DESI DR2 BAO observables;
- one isotropic `DV/rd` point;
- six anisotropic pairs `DM/rd` and `DH/rd`;
- uncertainties and correlation coefficients;
- six declared off-diagonal covariance values.

However, storing correlations in a CSV does not prove that a likelihood consumes them. This audit creates the intermediate evidence layer:

```text
primary points + covariance summary
→ cross-check sigma, rho and covariance
→ reconstruct each 2x2 block
→ validate positive definiteness
→ materialize ordered 13x13 block-diagonal matrix
→ demonstrate off-diagonal effect on a synthetic one-sigma residual
→ preserve fit-level integration as TOKEN_VAZIO
```

## Claim boundary

```text
repository-declared covariance reconstruction
!= full official joint covariance
!= vector likelihood integration
!= cosmological fit
!= RLL confirmation or superiority
```

The deterministic residual used to demonstrate the matrix operator is explicitly synthetic. It proves only that the off-diagonal term is numerically active.

`claim_allowed=false` remains mandatory.

## Canonical implementation

- builder: `tools/audit_desi_dr2_covariance_blocks.py`
- tests: `tests/test_desi_dr2_covariance_blocks.py`
- workflow: `.github/workflows/rll-desi-dr2-covariance-audit.yml`
- inputs:
  - `data/real/cosmology/desi_dr2_bao_primary_points.csv`
  - `data/real/cosmology/desi_dr2_bao_covariance_summary.csv`
- artifact: `rll-desi-dr2-covariance-${RUN_ID}`

## Artifact contract

```text
DESI_DR2_BAO_BLOCK_COVARIANCE.csv
OBSERVABLE_ORDER.csv
COVARIANCE_AUDIT.json
REPORT.md
MANIFEST.json
CHECKSUMS.sha256
BUILD.log
```

## Invariants

For each anisotropic block:

\[
C_i=
\begin{bmatrix}
\sigma_{a,i}^{2} & \rho_i\sigma_{a,i}\sigma_{b,i}\\
\rho_i\sigma_{a,i}\sigma_{b,i} & \sigma_{b,i}^{2}
\end{bmatrix}.
\]

The gate requires:

\[
-1<\rho_i<1,
\qquad
\det C_i=\sigma_{a,i}^{2}\sigma_{b,i}^{2}(1-\rho_i^2)>0.
\]

It also verifies that the covariance written in the summary equals:

\[
\operatorname{Cov}(a,b)=\rho_i\sigma_{a,i}\sigma_{b,i}.
\]

## What becomes partially resolved

The repository can now demonstrate that:

1. the declared six paired covariance blocks are internally consistent;
2. their matrices are invertible and positive definite;
3. an ordered 13-dimensional block matrix can be reproduced;
4. an off-diagonal term changes a quadratic form relative to the diagonal approximation;
5. source hashes and output checksums are preserved.

Therefore:

```text
TV-RLL-REALDATA-COVARIANCE.state = PARTIALLY_RESOLVED
```

## What remains TOKEN_VAZIO

- full official cross-block covariance, when available;
- independent verification of the repository transcription;
- model functions for the combined `DV/rd`, `DM/rd`, `DH/rd` vector;
- likelihood integration using the emitted observable order;
- fit-level comparison between full-block and diagonal approximations;
- influence on posterior, AIC, BIC or Bayes factor;
- independent scientific review.

## Safe next integration

The next code layer must be an isolated adapter:

```text
model parameters
→ predictions in OBSERVABLE_ORDER.csv
→ residual vector
→ chi2 = r^T C^-1 r
→ comparison with diagonal chi2
→ regression receipt
```

It must not replace the existing `run_all_real.py` path until:

- predictions for all three observable types are tested;
- units and sound-horizon convention are fixed;
- block ordering is proven;
- diagonal and covariance modes are both reproducible;
- negative and unexpected results remain visible.

## F_ok

- repository-declared blocks can be materialized and tested;
- covariance use has a deterministic, falsifiable diagnostic;
- output order, hashes and checksums are explicit;
- no fit or scientific claim is inferred.

## F_gap

- vector model adapter;
- full source covariance and cross-block terms;
- source-independent verification;
- real fit and external review.

## F_next

Implement the isolated DESI DR2 vector-likelihood adapter and keep its output claim-blocked until it reproduces diagonal mode and passes an independent source audit.
