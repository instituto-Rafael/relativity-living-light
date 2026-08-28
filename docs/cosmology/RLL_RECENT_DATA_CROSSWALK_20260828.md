# RLL Recent Data Crosswalk — 2026-08-28

State: `APPEND_ONLY_FAIL_CLOSED`  
`claim_allowed=false` · `publication_ready=false`

This overlay crosses the current RLL successor hypotheses with the newest primary cosmology results already public by 2026-08-28. It does **not** rewrite the historical Ω6 record or promote any hypothesis.

## Sources crossed

1. **DESI DR2 Results IV — Lyα full-shape/AP** (`arXiv:2607.27410`, v3 2026-08-04)
   - `z_eff=2.33`
   - `DH/rd = 8.600 ± 0.066`
   - `DM/rd = 39.32 ± 0.33`
   - under ΛCDM: `Ωm = 0.325 ± 0.018`
   - Lyα full-shape + BBN: `H0 = 66.5 ± 1.3 km s^-1 Mpc^-1`
   - evolving-DE preference: `2.7σ` for DESI+CMB and `3.2σ` with supernovae.
   - the new high-z anchor moves the DESI/CMB discrepancy from `2.4σ` to `2.2σ`.

2. **DESI DR2 Lyα full-shape validation** (`arXiv:2607.27411`, v2 2026-08-04)
   - BAO and AP parameters satisfy the declared validation requirements and remain stable across the tested analysis variants.
   - mock studies identify a significant bias in the inferred `fσ8`.
   - the collaboration therefore excludes that growth measurement from the final analysis.
   - consequence for RLL: this release can sharpen H54 geometry tests but its excluded `fσ8` must not be promoted into H53 growth evidence.

3. **DES Y6 3×2pt** (`arXiv:2601.14559`)
   - `S8 = 0.789 ± 0.012`
   - `Ωm = 0.333 +0.023/-0.028`
   - Y6 3×2pt `wCDM`: `w = -1.12 +0.26/-0.20`
   - combined Y6 3×2pt + CMB + low-z: `w = -0.981 +0.021/-0.022`, with no significant preference over ΛCDM in this one-parameter wCDM slice.

4. **DES Y6 dynamical dark energy** (`arXiv:2605.27221`)
   - DES-only: `w0=-0.84±0.10`, `wa=-0.44 +0.60/-0.55`
   - + DESI DR2: `w0=-0.84 +0.06/-0.07`, `wa=-0.53 +0.33/-0.28`
   - + primary CMB: `w0=-0.82±0.05`, `wa=-0.63 +0.21/-0.18`
   - quoted departures from ΛCDM: `2.2σ`, `2.3σ`, and `3.0σ` respectively.

## H51 — fixed crossing

H51 was registered on 2026-08-27 **after all source releases above**. Therefore this is retrospective consistency only.

The exact H51 line is

```text
wa = -4 (w0 + 1)
a_cross = 0.75
z_cross = 1/3
```

Using only published central values:

| combination | observed w0 | H51 wa from w0 | observed wa | central residual |
|---|---:|---:|---:|---:|
| DES Y6 | -0.84 | -0.64 | -0.44 | +0.20 |
| DES Y6 + DESI DR2 | -0.84 | -0.64 | -0.53 | +0.11 |
| + primary CMB | -0.82 | -0.72 | -0.63 | +0.09 |

The central values lie in the same `w0>-1, wa<0` quadrant and near the H51 line, but **no significance is computed without the joint `(w0,wa)` covariance**. This is not confirmation and cannot be converted into a claim.

## H03 — phantom-only shape

For the historical H03 `s^z` interpretation,

```text
w_H03(z) = -1 + (1+z) ln(sqrt(3)/2)/3
```

so

```text
w_H03(0)    = -1.0479470121
w_H03(2.33) = -1.1596635502
```

H03 stays phantom for all `z>=0`, unlike the current CPL central region that has `w0>-1` and `wa<0`. This is a sharper qualitative tension, **not an exact falsification**, because H03 is not CPL. The next valid test is an equal-treatment likelihood using H03 distances directly.

## H53 — growth

DES Y6 materially raises the priority of H53 because it provides precise late-time growth information. RLL still lacks the exact perturbation/growth completion needed to consume that information as an RLL test.

Do not use the DESI DR2 Lyα full-shape `fσ8` as a substitute: `arXiv:2607.27411` reports a significant mock bias and excludes that growth measurement from the final analysis.

## H54 — high-z AP

H54 becomes the highest-value background-data upgrade. The new DESI Lyα full-shape/AP point is a ~1% high-redshift geometry anchor.

Critical rule:

```text
Lyα AP/full-shape + Lyα BAO overlap in spectra
=> never append them as statistically independent blocks
```

Promotion requires authoritative joint covariance/likelihood custody or an explicit replacement of the overlapping Lyα BAO block.

## ATLAS effect

No maturity inflation is authorized:

```text
G2 = PARTIAL
G3 = PARTIAL
G4 = PARTIAL
G6 = BLOCKED
G7 = BLOCKED
```

Recent evidence changes **priority and falsifier sharpness**, not truth status.

## R3

`F_ok`: recent DESI/DES evidence cross-indexed against H03/H51/H53/H54; post-hoc boundary explicit; anti-double-counting explicit; DESI growth-validation exclusion pinned.

`F_gap`: executable Lyα AP+BAO covariance/likelihood; H51 held-out/future test; H03 exact likelihood; H53 perturbation/growth closure; G6 convergence; independent replication.

`F_next`: materialize H54 likelihood custody first, then project H03/H51 through the same frozen background likelihood, then consume DES Y6 growth only after H53 closure.
