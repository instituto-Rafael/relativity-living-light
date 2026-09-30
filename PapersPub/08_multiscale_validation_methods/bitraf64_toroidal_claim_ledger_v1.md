# BITRAF64 Toroidal Coherence — Claim Ledger V1

**Date:** 2026-08-08  
**Parent ledger:** `claim_state_ledger.md`  
**Policy:** `evidence_first` / `fail_closed`  
**Global state:** `OBSERVED_LIMITED`  
**Global gate:** `claim_allowed=false`

This ledger separates exact mathematical corrections from implementation-dependent claims. Absence of executable evidence is represented as `TOKEN_VAZIO`; it is never promoted to success.

| ID | Claim | State | Evidence currently admissible | Promotion/falsification gate |
|---|---|---|---|---|
| BTR-01 | A `10×10×10` coordinate system is toroidal when every spatial transition wraps modulo 10. | `CONDITIONAL` | Definition of the quotient lattice `(Z/10Z)^3`. | Execute the actual BITRAF64 transition implementation and prove wraparound on all three axes, including boundary fixtures. |
| BTR-02 | `10^3 × 6` denotes 1000 spatial cells with six discrete lanes/variants. | `CONVENTION` | Shape arithmetic. | Schema/source must declare the six lanes consistently. |
| BTR-03 | `f ∈ {0,…,5}` is by itself a fractal dimension. | `PROHIBITED_TERMINOLOGY` | A six-valued discrete index is not a fractal-dimension estimator. | Supply a scaling law and an accepted dimension calculation. |
| BTR-04 | Linearity over `GF(2)` implies invertibility. | `PROHIBITED` | A linear transform may be singular. | For each actual transform, prove square shape plus full rank / zero kernel. |
| BTR-05 | Every declared BITRAF64 binary transform is invertible. | `TOKEN_VAZIO` | Concrete transform matrices were not supplied to this gate. | Materialize every transform matrix/operator and verify rank `n` over `GF(2)` plus round-trip tests. |
| BTR-06 | `ln(phi) ≈ 0.4812` is the asymptotic spectral growth rate of the canonical Fibonacci recurrence. | `PASS_EXACT` | Dominant eigenvalue `phi` of the Fibonacci companion matrix. | Fails if the implemented recurrence differs from canonical Fibonacci. |
| BTR-07 | Positive `ln(phi)` proves chaotic-but-bounded Fibonacci dynamics. | `PROHIBITED` | Exponential growth of a linear recurrence is not, by itself, a proof of chaos or boundedness. | Define the nonlinear/normalizing map and demonstrate a bounded invariant set plus a valid chaos criterion. |
| BTR-08 | The `ψχρΔΣΩ_LOOP` is bounded and converges after ~30 cycles. | `TOKEN_VAZIO` | No executable recurrence + perturbation ensemble was supplied. | Provide equations/code, normalization, initial-condition domain, perturbation protocol, and stability receipt. |
| BTR-09 | A full-rank `33×33` syndrome matrix alone proves single-bit error correction. | `PROHIBITED` | Full rank alone does not prove unique syndromes for all bit positions. | Show `d_min ≥ 3` or unique nonzero syndrome for every single-bit error. |
| BTR-10 | BITRAF64/Fiber ECC corrects every single-bit error in a 1024-byte word. | `TOKEN_VAZIO` | No complete parity-check mapping / exhaustive injection receipt supplied. | Exhaustively inject all 8192 unit errors and show unique correction plus no-error discrimination. |
| BTR-11 | `phi × sum(1..5) / (pi × 42) = 0.963999`. | `FAIL_EXACT` | Expression evaluates to approximately `0.1839415`. | Recover a different explicit derivation if `0.963999` is intended. |
| BTR-12 | `gcd(6000,2057)=16`. | `FAIL_EXACT` | Euclidean algorithm gives `1`. | None under integer arithmetic. |
| BTR-13 | `gcd(42,60)=6`. | `PASS_EXACT` | Euclidean algorithm. | None under integer arithmetic. |
| BTR-14 | 53 redundancy bits over 1024 bytes equal `0.41 bit/byte`. | `FAIL_EXACT` | `53/1024 = 0.0517578125 bit/byte`. | Change only if redundancy or payload size changes. |
| BTR-15 | Entropy ≈5.5 bits/value and white-noise autocorrelation are verified properties. | `TOKEN_VAZIO` | Empirical statistics not supplied. | Run declared corpus/seed, estimator, intervals and preserve raw receipts. |
| BTR-16 | SIMD yields 4–8× speedup. | `TOKEN_VAZIO` | No homogeneous before/after benchmark receipt supplied. | Same hardware/workload/build, warmup, repetitions, dispersion, clocks/thermal state and flags. |
| BTR-17 | A 12 KiB spiral LUT is required. | `HYPOTHESIS` | For `i,j,k∈[0,9]`, exponent has only 28 values. | Benchmark a 28-entry LUT against alternatives. |
| BTR-18 | Package-DAG ↔ toroidal BITRAF64 alignment follows from the reported GCD relation. | `PROHIBITED` | Reported GCD premise is false. | Define an explicit graph embedding and quantify preserved invariants. |

## Production promotion order

1. `GF(2)` rank + round-trip evidence for actual transforms.
2. ECC `d_min` / unique-syndrome proof + exhaustive 8192-error injection receipt.
3. Executable `ψχρΔΣΩ_LOOP` stability/perturbation characterization.
4. Entropy/autocorrelation/avalanche measurements on declared data.
5. Homogeneous NEON/LUT/cache benchmark on physical target hardware.
6. Only then evaluate a package-DAG mapping as a separate integration hypothesis.

```text
claim_allowed = false
production_ready = false
missing_evidence = TOKEN_VAZIO
absence_of_evidence != PASS
math_correction_PASS != implementation_PASS
CI_green_with_blocked_gate != product_PASS
```
