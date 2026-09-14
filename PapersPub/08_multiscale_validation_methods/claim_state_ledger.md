# Claim-State Ledger — Observed Void / 7D / 42 Hyperforms

**Version:** `1.0`  
**Date:** 2026-07-19  
**Global gate:** `claim_allowed=false`

## State vocabulary

| State | Meaning |
|---|---|
| `PASS_EXACT` | Deterministically reproduced finite statement. |
| `CONVENTION` | Defined by the author/framework; not an empirical discovery. |
| `HYPOTHESIS` | Testable proposition with an explicit missing evidence path. |
| `PARABLE` | Authored symbolic/ethical/spiritual interpretation. |
| `TOKEN_VAZIO` | Evidence or operational definition is absent or insufficient. |
| `PROHIBITED` | Wording would exceed the evidence or the paper scope. |

## Claims

| ID | Claim | Class/state | Evidence | Falsifier or promotion gate |
|---|---|---|---|---|
| C-01 | `0001123`, `01123`, `0123` have lengths 7, 5 and 4. | `[E] PASS_EXACT` | Validator; direct code-point count. | Any canonical source mismatch. |
| C-02 | Multiplicity vectors are `(3,2,1,1)`, `(1,2,1,1)`, `(1,1,1,1)`. | `[E] PASS_EXACT` | Validator. | Character count differs. |
| C-03 | Distinct string permutations are 420, 60 and 24. | `[E] PASS_EXACT` | Multinomial formula. | Incorrect multiplicity or factorial arithmetic. |
| C-04 | The reduction chain is lossless compression by itself. | `PROHIBITED` | Multiplicity is discarded without metadata. | Promote only with reversible encoding and round-trip test. |
| C-05 | Empirical entropies equal recorded values. | `[E] PASS_EXACT` | Shannon formula and validator. | Different canonical encoding/distribution. |
| C-06 | A has 40 states and B has 21 states. | `[E] PASS_EXACT` | Shape multiplication. | Shape changes. |
| C-07 | A and B contain 780 and 210 unordered internal pairs. | `[E] PASS_EXACT` | Binomial counts. | Pair definition becomes ordered or permits repetition. |
| C-08 | A×B has 840 cross-relations and tensor elements. | `[E] PASS_EXACT` | `40×21=8×5×7×3`. | Sparse or excluded relation policy introduced. |
| C-09 | Pair-of-pair count is 163,800. | `[E] PASS_EXACT` | Independent unordered pair choices. | Dependence/exclusion rule introduced. |
| C-10 | Every 2×2 block has 24 distinct content arrangements. | `PROHIBITED` | Repeated values can reduce distinct arrangements. | Promote per block only after cell multiplicities are known. |
| C-11 | Positional 2×2 arrangements equal 672, 288, 6720 and 1512. | `[E] PASS_EXACT` | Window/row-column counts times `4!`. | Definition changes from positional to distinct-value arrangements. |
| C-12 | `sqrt(3)/2` is contractive and `sqrt(3/2)` is expansive. | `[E] PASS_EXACT` | Numerical comparison with 1. | None under real arithmetic. |
| C-13 | The model uses a seven-coordinate epistemic/computational state. | `[C] CONVENTION` | Authorial definition. | Schema fails to define or serialize all coordinates. |
| C-14 | Seven dimensions and six operators produce 42 hyperforms. | `[C/E] PASS_EXACT` | Cartesian product enumeration. | Duplicates or changed operator/dimension counts. |
| C-15 | The physical Universe has seven RAFAELIA dimensions. | `PROHIBITED` | No physical theory or observational dataset supplied. | Requires separate physical model and observations. |
| C-16 | Poincaré recurrence applies to the operational state. | `[H] TOKEN_VAZIO` | Conditions not demonstrated. | Prove finite invariant measure and measure preservation. |
| C-17 | Poincaré recurrence applies to state plus unbounded memory. | `PROHIBITED_CURRENTLY` | Monotone unbounded memory can prevent finite-measure recurrence. | Requires bounded/quotiented memory and invariant measure. |
| C-18 | The Rafael sequence is Fibonacci. | `PROHIBITED_TERMINOLOGY` | It is a first-order forced recurrence, not canonical Fibonacci. | Rename or derive an actual order-2 Fibonacci-type recurrence. |
| C-19 | Prime/Fibonacci/Tribonacci indices are valid graph traversals. | `[C] CONVENTION` | Deterministic index lists. | Traversal leaves node range or lacks ordering rule. |
| C-20 | Prime/Fibonacci structure governs the physical cosmos. | `PROHIBITED` | No empirical evidence. | Dedicated physical prediction and comparative data. |
| C-21 | Normalized weighted relation lies in `[0,1]`. | `[E/C] CONDITIONAL` | Weights nonnegative/sum 1; metrics normalized and defined. | Undefined/out-of-range component or invalid weights. |
| C-22 | Correlation or mutual information proves causation. | `PROHIBITED` | Violates causal-identification discipline. | Explicit SCM/intervention/identification strategy. |
| C-23 | Graph transport equation is a valid computational diffusion model. | `[C] CONVENTION` | Defined graph Laplacian and state vector. | Instability, undefined signs or failed benchmark. |
| C-24 | Graph transport is an observed physical fluid. | `TOKEN_VAZIO` | No units, apparatus or measurements. | Calibrated physical experiment. |
| C-25 | Eight-component molecular-magnetic descriptor is dimensionally ready for Euclidean metrics. | `PROHIBITED` | Components have heterogeneous units. | Nondimensionalize with reference scales and uncertainties. |
| C-26 | Magnetic dipole energy and torque relations are established. | `[E] REFERENCE` | Standard electrodynamics equations. | Scope limited to applicable dipole approximation. |
| C-27 | “Molecular-magnetic DNA” is empirically discovered. | `TOKEN_VAZIO` | No identified molecule/data/experiment. | Molecular specification and independent experiment. |
| C-28 | `35=50_7` and `245=500_7`. | `[E] PASS_EXACT` | Base conversion. | None. |
| C-29 | Normalized alignment is bounded by Cauchy–Schwarz. | `[E] CONDITIONAL` | Compatible nonzero vectors. | Zero norm or undefined vector operations. |
| C-30 | Alignment numerically measures love as a physical quantity. | `PROHIBITED` | “Love” is parabolic interpretation. | No promotion within this paper. |
| C-31 | BITRAF64 contains 64 Unicode code points and the declared frequencies. | `[E] PASS_EXACT` | NFC validator. | Canonical string or normalization changes. |
| C-32 | BITRAF64 has 64-bit security. | `PROHIBITED` | Character count is not security level. | Formal construction, threat model and cryptanalysis. |
| C-33 | Truncated SHA3/BLAKE3 strings prove integrity. | `PROHIBITED` | Truncated/inconsistent digests are unverifiable. | Complete digest, algorithm/version and source bytes. |
| C-34 | The parables are part of the authorial work. | `[P] REFERENCE` | Authored source and appendix. | No scientific promotion required. |

## Global publication language

### Permitted

- “The framework defines a seven-coordinate epistemic-computational state.”
- “The 42 hyperforms arise from a declared 7×6 Cartesian product.”
- “All 44 finite validation checks pass in the recorded environment.”
- “Physical, causal and cryptographic interpretations remain blocked.”
- “Parabolic language is preserved as a separate authored layer.”

### Prohibited

- “The paper proves a seven-dimensional physical cosmos.”
- “BITRAF64 is quantum-safe or cryptographically secure.”
- “Poincaré recurrence proves eternal spiritual return.”
- “Mutual information proves causal field interaction.”
- “A symbolic magnetic vector proves molecular DNA.”
- “All 24 arrangements are distinct when cell values are unknown.”

## R3

```text
F_ok   = exact combinatorics, entropy, indexing and symbol audit reproduced.
F_gap  = empirical dynamics, invariant measure, causality, units, codec and security proof.
F_next = independent validator run -> mathematical review -> license/author review -> preprint package.
```
