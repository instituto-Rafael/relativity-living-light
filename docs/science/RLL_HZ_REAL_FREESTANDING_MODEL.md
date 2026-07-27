# RLL H(z) Real Freestanding Model

Status: `IMPLEMENTED / VERIFIED_LOCAL / CLAIM_ALLOWED=false`

## What is coupled

This is the direct data-and-model layer above the canonical C coupling region.
It does not receive a precomputed model value. It computes both models inside the
freestanding runtime and pushes each result through the canonical evidence gate.

```text
data/real/Hz_data_real.csv
        ↓ exact byte digests + 33-row Q16 materialization
rll_hz_moresco_2022_q16.c
        ↓ z, H_obs, sigma_H
rll_hz_freestanding.c
        ├── H_LCDM(z)
        └── H_RLL(z)
        ↓ two canonical observations per row
rll_canonical_coupling.c
        ↓ residual / sigma / chi-square / receipt
hz-real-validation.json
```

## Source anchor

```text
path        data/real/Hz_data_real.csv
Git blob    3ac5da2594bfc127c28c6b4e817259e1bee28085
rows        33
bytes       999
SHA-256     83e36c1fabdb31f6b9a192a1a235f61c7cb10d4dba0ef97c00f34a8a13482f15
FNV-1a 64   8fcfaccd5d192767
CRC32       2840ace1
```

Every decimal `z`, `H_obs` and `sigma_H` value is rounded once to Q16.16 and the
test suite reconstructs all 33 rows from the CSV to prove the compiled table is
not a hand-written substitute.

## Equations implemented in C

For flat ΛCDM:

\[
E_{\Lambda CDM}^2(z)=\Omega_m(1+z)^3+(1-\Omega_m)
\]

\[
H_{\Lambda CDM}(z)=H_0\sqrt{E_{\Lambda CDM}^2(z)}
\]

For the nominal RLL transition used by the existing Python result:

\[
f(z)=\frac{1}{1+\exp((z-z_t)/w_t)}
\]

\[
E_{RLL}^2(z)=\Omega_m(1+z)^3+\Omega_\Lambda+
\Omega_{s0}[f(z)+(1-f(z))(1+z)^3]
\]

\[
\Omega_\Lambda=1-\Omega_m-\Omega_{s0}
\]

The square root and exponential are implemented without `math.h`:

- integer square root over Q16.16;
- exponential range reduction by `ln(2)`;
- fifth-order polynomial on the reduced interval;
- power-of-two rescaling.

## Nominal parameters

```text
H0       67.4
Omega_m  0.315
Omega_s0 0.02
z_t      1.0
w_t      0.3
```

These are the same nominal parameters used by
`scripts/compute_moresco_hz_chi2.py`. They are not fitted by this kernel.

## Deterministic result

```text
                    Q16 integer    decoded
chi2_LCDM           1491933        22.765090942382812
chi2_RLL            1800087        27.467147827148438
delta RLL-LCDM      308154         4.702056884765625
```

The existing float64 reference is:

```text
chi2_LCDM           22.7641
chi2_RLL            27.4651
delta RLL-LCDM      4.7009
```

All absolute differences remain below `0.005`. The small difference is the
explicit Q16.16 quantization and fixed-point exponential/square-root path, not a
silent change of equations.

## Freestanding proof

The validation command:

```bash
python3 tools/validate_rll_hz_real_freestanding.py --write-report
```

performs:

1. byte-level SHA-256/FNV/CRC check of the real CSV;
2. row-for-row CSV ↔ compiled-Q16 comparison;
3. hosted C vector execution;
4. float64 ↔ Q16 result parity;
5. relocatable freestanding link of canonical kernel + models + data;
6. `nm -u` empty-symbol gate;
7. ARMv7 object build;
8. AArch64 object build.

## Boundary

This closes a real execution path for the 33-point H(z) dataset and the nominal
RLL/ΛCDM comparison. It does not claim parameter optimization, MCMC, full
covariance, causal validation, independent replication or general validation of
RLL. `claim_allowed` remains hard-false in both canonical receipts and the dual
receipt.
