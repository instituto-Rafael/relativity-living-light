# RLL canonical real-data kernel — freestanding C

Status: `IMPLEMENTED_AND_LOCALLY_EXECUTED`  
Claim gate: `claim_allowed=false`

This kernel is the low-level canonical region for real cosmological couplings already materialized in the repository. It is not a mock loader, a YAML plan, or a replacement for the hosted scientific pipeline.

## Runtime contract

```text
real committed data
→ pinned SHA-256 provenance
→ typed observable
→ SI/astronomical unit contract
→ RLL or LCDM prediction
→ diagonal/correlated/full-covariance residual
→ chi-square receipt
→ claim gate remains false
```

The C runtime uses:

- no libc;
- no `stdio`, `stdlib`, `string.h`, or `math.h`;
- no `malloc`, heap, GC, or hidden allocation;
- caller-owned buffers for arbitrary full covariance;
- a real `-nostdlib -static` ELF self-test;
- direct Linux exit syscall only in the self-test entrypoint.

## Real data embedded

| Block | Points | Covariance handling | Committed source |
|---|---:|---|---|
| Moresco/CC H(z) | 33 | diagonal uncertainties | `data/real/Hz_data_real.csv` |
| Real fσ8 compilation | 16 | diagonal, limitation preserved | `data/real/cosmology/fsigma8_growth_real.csv` |
| DESI DR2 BAO | 13 | six correlated DM/DH blocks + one DV point | `data/real/cosmology/desi_dr2_bao_primary_points.csv` |
| Planck compressed CMB prior | 3 | complete 3×3 covariance through LDLᵀ | `data/real/CMB_shift_real.json` |

Every block carries its repository path, source URL, local SHA-256, and provenance state. The growth compilation retains `PRIMARY_PARTIAL` because one secondary source route returned HTTP 403; the verified 6dFGS anchor and committed local hash are preserved without hiding that limitation.

## Implemented observables

- `H(z)` in km s⁻¹ Mpc⁻¹;
- `fσ8(z)` through an explicit growth-index approximation;
- DESI `D_H/r_d`, `D_M/r_d`, and `D_V/r_d`;
- CMB shift parameter `R`;
- CMB acoustic scale `l_A` using `r_s(z*)`, not `r_d`;
- `Ω_b h²`;
- supernova distance modulus `μ(z)` for externally supplied Pantheon+/SH0ES arrays;
- generic full-covariance `LDLᵀ` likelihood with caller-owned memory, so large SN covariance can be connected without adding a heap.

## FASE 18-E numerical cross-check

Using the committed FASE 18-E MAP parameters, the freestanding implementation produced:

| Block | Python FASE 18-E | freestanding C | absolute difference |
|---|---:|---:|---:|
| Moresco H(z) | 23.96968192673179 | 23.969658191726 | 0.000023735006 |
| DESI DR2 | 21.78806427901191 | 21.787983337656 | 0.000080941356 |
| CMB shift | 0.7616672954080195 | 0.761677264076 | 0.000009968668 |

All differences are below `2×10⁻⁴`. The cross-check is a reproduction of defined calculations, not evidence that the RLL model is physically preferred.

## Files

```text
core/lowlevel_runtime/include/rll_canonical_real.h
core/lowlevel_runtime/c/rll_canonical_real.c
core/lowlevel_runtime/c/rll_canonical_real_data.c
core/lowlevel_runtime/c/rll_canonical_real_selftest.c
tests/test_rll_canonical_real_freestanding.py
tools/run_rll_canonical_real_freestanding.sh
results/rll_canonical_real_freestanding.json
```

## Execute

```bash
sh tools/run_rll_canonical_real_freestanding.sh
pytest -q tests/test_rll_canonical_real_freestanding.py
```

## Boundary

`claim_allowed=false` is hard-coded in the result. A successful ELF proves that the data snapshot, equations, covariance algebra, provenance table and self-test execute without libc. It does not turn a compressed CMB likelihood into the complete Planck likelihood, does not manufacture missing Pantheon covariance, and does not convert a posterior into physical truth.
