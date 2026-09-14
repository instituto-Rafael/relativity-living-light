# RLL Joint Real Model Bridge V2

**State:** implemented / executable / fail-closed / `claim_allowed=false`

## Purpose

V1 completed the raw-input boundary for four committed cosmology sources, but
only the 33 H(z) observations had an executable model callback. The remaining
13 BAO, 16 growth and 3 CMB observations were valid measurements with verified
custody, yet intentionally remained `TOKEN_VAZIO` on the model side.

V2 closes that specific gap without replacing the parser, duplicating datasets
or inventing predictions:

```text
four raw committed sources
→ SHA-256 and strict schema parser
→ 65 typed observations
→ joint ΛCDM or RLL profile
→ existing freestanding cosmology evaluator
→ canonical Q16 observation gate
→ covariance-aware aggregate receipt
```

## Data surface

| Route | Count | Observables |
|---|---:|---|
| Cosmic chronometers | 33 | H(z) [km s⁻¹ Mpc⁻¹] |
| DESI DR2 BAO | 13 | DV/r_d, DM/r_d, DH/r_d |
| Growth compilation | 16 | fσ8 |
| Planck distance priors | 3 | R, l_A, Ω_b h² |
| **Total** | **65** | — |

The source digests remain compiled and checked by
`rll_canonical_real_inputs.c`; V2 does not weaken source custody.

## Profiles

The historical V1 profiles remain byte-for-byte compatible in behavior:

```text
RLL_REAL_PROFILE_LCDM_NOMINAL = 1  → H(z) only
RLL_REAL_PROFILE_RLL_NOMINAL  = 2  → H(z) only
```

V2 adds:

```text
RLL_REAL_PROFILE_LCDM_JOINT_FASE18E = 3
RLL_REAL_PROFILE_RLL_JOINT_FASE18E  = 4
```

The joint constructors use the parameter records already defined by the RLL
canonical evaluator:

```text
rll_params_fase18e_lcdm()
rll_params_fase18e_map()
```

No parameter optimization is run inside the callback.

## Evaluators reused

`rll_canonical_real_models.c` maps the typed input quantity to the public
freestanding evaluator in `rll_canonical_real.c`:

```text
RLL_Q_HUBBLE             → RLL_OBS_HZ_KM_S_MPC
RLL_Q_FSIGMA8             → RLL_OBS_FSIGMA8
RLL_Q_BAO_DV_RS           → RLL_OBS_BAO_DV_OVER_RD
RLL_Q_BAO_DM_RS           → RLL_OBS_BAO_DM_OVER_RD
RLL_Q_BAO_DH_RS           → RLL_OBS_BAO_DH_OVER_RD
RLL_Q_CMB_SHIFT_R         → RLL_OBS_CMB_R
RLL_Q_CMB_ACOUSTIC_SCALE  → RLL_OBS_CMB_LA
RLL_Q_CMB_OMEGA_B_H2      → RLL_OBS_CMB_OBH2
```

The evaluator supplies:

- logistic or ΛCDM expansion history;
- Simpson integration for comoving distance;
- growth-index approximation for fσ8;
- DV/r_d, DM/r_d and DH/r_d;
- compressed CMB R, l_A and Ω_b h².

The adapter converts only the API boundary between Q16.16 records and the
freestanding evaluator's internal `double`. It does not call libc, `math.h`,
heap allocation or filesystem functions.

## Covariance path

The parser keeps the existing covariance treatment:

- DESI anisotropic DM/DH pairs retain their reported correlation coefficient;
- the three CMB priors use the committed positive-definite 3×3 covariance;
- no diagonal fallback is silently substituted when a full covariance route is
  expected.

A complete joint execution therefore requires:

```text
source_verified_mask = 15
parsed_rows = 65
model_bound_rows = 65
model_token_vazio_rows = 0
cmb_covariance_used = 1
canonical.total = 65
canonical.evidence = 65
canonical.blocked = 0
claim_allowed = 0
```

## Pinned deterministic receipts

The exact Q16 receipts emitted by the GitHub runner are:

| Profile | χ² Q16 | Decoded χ² |
|---|---:|---:|
| ΛCDM joint FASE18E | 4,641,555 | 70.82450866699219 |
| RLL joint FASE18E | 4,261,420 | 65.02410888671875 |
| Δχ² RLL−ΛCDM | −380,135 | −5.8003997802734375 |

These values are pinned in the test suite and in:

```text
artifacts/canonical-coupling/joint-real-model-v2.json
```

The negative delta belongs only to this compressed 65-observation route and the
stored FASE18E parameter records. It is not the result of a fresh fit and must
not be substituted for the repository's full 1,677-point likelihood result.

## Compatibility receipts

The original H(z)-only paths remain mandatory:

```text
ΛCDM H(z) V1 chi2_q16 = 1491916
RLL  H(z) V1 chi2_q16 = 1800068
```

This prevents a new joint feature from silently rewriting previous evidence.

## Verification

The complete test assembles:

```text
rll_canonical_coupling.c
rll_canonical_real_inputs.c
rll_canonical_real_models.c
rll_canonical_real.c
rll_canonical_real_data.c
rll_hz_freestanding.c
rll_hz_moresco_2022_q16.c
```

and verifies:

1. strict hosted C11 compilation;
2. relocatable freestanding link;
3. empty `nm -u` result;
4. ARMv7 cross-compilation;
5. AArch64 cross-compilation;
6. exact source hashes and row counts;
7. deterministic repeated joint executions;
8. exact pinned χ² receipts and delta;
9. all 65 observations bound for both profiles;
10. single-byte tamper rejection before parsing;
11. `claim_allowed=0` throughout.

## Scientific boundary

This implementation proves an executable and deterministic low-level route from
committed measurements to model predictions and covariance-aware receipts. It
does not prove:

- that the compressed 65-observation route is equivalent to the complete RLL
  likelihood;
- that Planck distance priors replace the full Planck likelihood;
- that the growth compilation is covariance-complete;
- that the FASE18E parameters are newly optimized here;
- that RLL is independently replicated or scientifically confirmed.

Therefore:

```text
model_bound_rows=65 != scientific_validation
negative_delta_chi2 != claim_allowed
claim_allowed=false
```
