# RLL Canonical Freestanding Kernel v1

## Status

`IMPLEMENTED` · `VERIFIED_LOCAL` · `ARMV7_OBJECT_VERIFIED` · `CLAIM_ALLOWED=false`

This is the canonical low-level executable path that couples the RLL cosmology to repository data without libc, heap allocation, hosted math, Python at runtime, or external native libraries.

## Real coupling

The executable binds two distinct evidence layers without conflating them:

1. **Directly recomputed H(z) subset**
   - source: `data/real/Hz_data_real.csv`;
   - 33 measurements;
   - sources preserved as numeric IDs: Moresco 2022 cosmic chronometers, CC+BAO BOSS, BAO Lyα;
   - exact decimal-to-Q16.16 materialization checked row by row in the test suite.

2. **Pinned FASE 20 joint-result summary**
   - source: `results/rll_fase20_mcmc_bayes.json`;
   - posterior means: `H0`, `Ωm`, `Ωb`, `Ωs0`, `zt`, `wt`;
   - `n_total=1677`;
   - `ln(B10)=-6.190210762419383 ± 0.6906527421175422`;
   - `ΔBIC=22.27`;
   - `Ωs0 UL95=0.0017772301590821408`.

The H(z) subset is recomputed inside the freestanding ELF. The FASE 20 evidence values are pinned as a separately hashed summary; they are **not falsely presented as recomputed by this small kernel**.

## Mathematical region

The kernel evaluates, in Q16.16:

\[
E^2(z)=\Omega_m(1+z)^3+\Omega_\Lambda+
\Omega_{s0}\left[f(z)+(1-f(z))(1+z)^3\right]
\]

\[
f(z)=\frac{1}{1+\exp((z-z_t)/w_t)}
\qquad
H(z)=H_0\sqrt{E^2(z)}
\]

For the ΛCDM null path:

\[
E_{\Lambda CDM}^2(z)=\Omega_m(1+z)^3+(1-\Omega_m)
\]

The fixed-point exponential uses range reduction by `ln(2)` and a sixth-order polynomial. Square root uses a restoring integer square-root algorithm. Division uses an internal software `u64/u32` divider, preventing unresolved `libgcc`/`compiler-rt` helpers on ARMv7.

## Canonical files

- `core/lowlevel_runtime/include/rll_canonical_freestanding.h`
- `core/lowlevel_runtime/c/rll_canonical_freestanding.c`
- `core/lowlevel_runtime/c/rll_canonical_hz_data.c`
- `core/lowlevel_runtime/c/rll_canonical_entry.c`
- `scripts/build_rll_canonical_freestanding.sh`
- `tests/test_rll_canonical_model_kernel.py`
- `results/rll_canonical_freestanding_receipt.json`

## One-command execution

```sh
./scripts/build_rll_canonical_freestanding.sh
```

The command builds a static ELF with `_start`, direct Linux syscalls and no dynamic imports, verifies unresolved symbols with `nm`, then executes the kernel.

Expected receipt:

```text
RLLCAN1 rows=33 valid=33 rejected=0 chi2_rll_q16=1541113 chi2_lcdm_q16=1541113 delta_q16=0 data_crc32=c7e56bca data_fnv64=f48a2db3d131c45f params_crc32=2505dec9 phase20_crc32=1b6c7c85 joint_n=1677 lnB10_q16=-405682 lnB10_err_q16=45263 delta_bic_q16=1459487 os0_ul95_q16=116 joint_best=LCDM receipt_crc32=34387926 best=TIE claim_allowed=0 token_vazio=7 numeric_flags=0
```

## What the receipt means

- `best=TIE`: with the FASE 20 posterior mean quantized to Q16.16, the 33-row H(z) subset does not distinguish RLL from ΛCDM. The small `Ωs0` contribution cancels against flatness at this precision and redshift range.
- `joint_best=LCDM`: the separately pinned full FASE 20 joint result favors ΛCDM strongly.
- `claim_allowed=0`: executable evidence is preserved without promoting a scientific claim.
- `token_vazio=7`: full covariance, independent replication and external binary audit remain open.
- `numeric_flags=0`: all 33 samples passed validation without division-by-zero, negative \(E^2\), saturation or invalid records.

## Architecture support

Direct Linux syscall entry is implemented for:

- x86_64;
- AArch64;
- ARM EABI/ARMv7;
- RISC-V 64.

The local verification produced:

- static x86_64 ELF;
- zero unresolved symbols;
- zero dynamic imports;
- ARMv7 combined object with zero unresolved symbols and no `__aeabi_*` runtime helpers;
- four passing tests.

## Scientific boundary

This kernel is an execution and custody adapter. It proves that a precise set of repository inputs can be mapped to a deterministic low-level computation and receipt. It does not replace the full joint likelihood, covariance matrices, MCMC, nested sampling, independent replication or peer review.

\[
\boxed{
\text{source}
\rightarrow
\text{Q16 materialization}
\rightarrow
\text{freestanding model}
\rightarrow
\chi^2
\rightarrow
\text{canonical hashes}
\rightarrow
\text{receipt}
}
\]
