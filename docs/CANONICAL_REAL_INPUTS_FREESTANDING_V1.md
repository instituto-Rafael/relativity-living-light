# RLL Canonical Real Inputs — Freestanding C V1

**State:** implemented / fail-closed / `claim_allowed=false`  
**Base kernel:** `rll_canonical_coupling.c` merged in PR #592.

## Purpose

This module closes the executable boundary between the real files committed in
RLL and the canonical observation accumulator:

```text
raw committed bytes
→ internal SHA-256 verification
→ strict schema parser
→ typed observable + unit + uncertainty
→ model callback
→ canonical coupling decision
→ covariance-aware contribution
→ deterministic receipt
```

It does not replace the Python scientific likelihood, CLASS/CAMB, Planck full
chains or independent replication. It makes the low-level input boundary real,
typed and falsifiable.

## Exact committed inputs

| Dataset | Path | Rows coupled | Pinned digest source |
|---|---|---:|---|
| Cosmic chronometers H(z) | `data/real/Hz_data_real.csv` | 33 | `real_hz` |
| DESI DR2 BAO | `data/real/cosmology/desi_dr2_bao_primary_points.csv` | 13 | `real_desi_dr2_bao` |
| fσ8/RSD | `data/real/cosmology/fsigma8_growth_real.csv` | 16 | `real_fsigma8_*` |
| Planck distance priors | `data/real/CMB_shift_real.json` | 3 | `real_cmb_shift*` |

Total: **65 observations**. The expected SHA-256 values are compiled from
`data/real/cosmology/real_source_signatures.json`. Any single-byte change is
rejected before parsing.

## Freestanding boundary

`rll_canonical_real_inputs.c` contains:

- a complete streaming SHA-256 implementation;
- strict CSV parsers for H(z), DESI DR2 BAO and fσ8;
- a targeted JSON parser for the committed CMB block;
- decimal/scientific-notation conversion to Q16.16;
- no heap, libc, file I/O, floating point or locale dependency;
- fixed stack/state memory only;
- host, ARMv7 and AArch64 object validation.

The hosted runner uses `stdio` only to load the four files into buffers. The
production API receives buffers and lengths directly.

## Observable coverage

The original coupling ABI already represents H(z), isotropic BAO and fσ8. This
adapter preserves that ABI and adds extension IDs without renumbering existing
values:

- `RLL_Q_BAO_DM_RS`;
- `RLL_Q_BAO_DH_RS`;
- `RLL_Q_CMB_SHIFT_R`;
- `RLL_Q_CMB_ACOUSTIC_SCALE`;
- `RLL_Q_CMB_OMEGA_B_H2`.

The DESI `DV/r_d`, `DM/r_d` and `DH/r_d` rows therefore remain distinct rather
than being collapsed into one generic BAO scalar.

## Model coupling

The parser never invents model predictions. A caller supplies
`rll_real_model_callback`, receiving dataset, quantity, axis/redshift,
observation and uncertainty.

- callback returns `RLL_REAL_MODEL_OK`: the prediction is bound and the record
  may enter the canonical evidence accumulator;
- callback returns `RLL_REAL_MODEL_TOKEN_VAZIO` or is absent: the observation is
  preserved but blocked from evidence promotion;
- callback returns `RLL_REAL_MODEL_BLOCKED`: the record is explicitly blocked.

The test identity callback returns the observation itself only to prove the
mechanical path and therefore yields χ²=0. It is not a cosmological model and
never authorizes a scientific claim.

## CMB covariance

When all three CMB predictions are supplied, the adapter uses the committed
3×3 correlation matrix together with the three reported uncertainties:

```text
u_i = (observation_i - model_i) / sigma_i
chi2_CMB = u^T correlation_inverse u
```

The inversion and quadratic form are fixed-point. If the correlation matrix is
singular, non-positive or malformed, ingestion fails closed. Without all three
model predictions, no diagonal fallback is silently substituted.

## Receipt invariants

A successful structural ingestion requires:

```text
source_verified_mask = 0x0F
parsed_rows = 65
hz_rows = 33
bao_rows = 13
fsigma8_rows = 16
cmb_rows = 3
claim_allowed = 0
```

With no model callback, the expected state is:

```text
model_token_vazio_rows = 65
canonical.evidence = 0
canonical.blocked = 65
claim_allowed = 0
```

This is deliberate: real measurements are not automatically evidence for an
unregistered model.

## Verification

```bash
pytest -q tests/test_rll_canonical_real_inputs.py
```

The test suite verifies:

1. strict freestanding compilation of the existing coupling kernel and adapter;
2. a combined relocatable object with no unresolved symbols;
3. ARMv7 and AArch64 cross-compilation;
4. exact ingestion of all four committed files;
5. 65 model-bound observations through the structural identity harness;
6. fail-closed behavior when no model callback exists;
7. rejection after a single-byte source mutation.

## Scientific boundary

`RLL_REAL_OK` means the committed inputs passed byte integrity, schema, units,
uncertainty and coupling mechanics. It does **not** mean that RLL fits the data,
outperforms ΛCDM/CPL, resolves a tension or has been independently reproduced.
Every receipt remains `claim_allowed=0` until the higher scientific gates pass.
