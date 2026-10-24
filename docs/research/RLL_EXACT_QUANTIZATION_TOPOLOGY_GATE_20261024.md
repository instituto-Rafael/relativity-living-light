# RLL / RAFAELIA — Exact quantization and cyclic-topology gate (2026-10-24)

**Status:** SOURCE_IMPLEMENTED / LOCAL_TESTS_PASS / RLL_CI_UNVERIFIED / PHYSICAL_COUPLING_BLOCKED.  
**Authority:** laboratory branch rll/lab, not main; isolated mathematical oracle only.  
**Authorial composition:** RAFAELIA (Rafael Melo Reis), AI-assisted scoped test implementation. Established formulas are not presented as original theorems.  
**Claim boundary:** claim_allowed=false, release_allowed=false. SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.

## Defined operator and proof boundary

For integers b>0 and n>=0, let alpha=sqrt(3)/2 and k=floor(b*alpha^n).
The file tools/rll_exact_quantized_orbit.py implements k using only integers and math.isqrt:
- n=2m: k=(b*3^m)//4^m.
- n=2m+1: k=isqrt(3*(b*3^m)^2)//(2*4^m).

The odd case follows from floor(floor(sqrt(A))/D)=floor(sqrt(A)/D) for positive integer D; squared integer inequalities certify both floor bounds. There is no floating-point tolerance. The reference is **Python arbitrary precision**, not freestanding C/ARM.

For translation T_(b,k)(x)=(x+k) mod b:
- cycle count = gcd(b,k);
- vertices per cycle = b/gcd(b,k);
- permutation sign = (-1)^(b-gcd(b,k)).

Crossings of edges in a planar drawing do not automatically become vertices. Base representation of an integer is distinct from the modulus chosen for an operator.

## Concrete diagnostic

For b=100, n=2, exact k=75 -> 25 cycles of 4, permutation sign -1.
Replacing k by 74 -> 2 cycles of 50, sign +1. A one-unit perturbation can cause a large discrete structural change.
For b=16, n=4, exact k=9, another integer-boundary fixture.
For even n=2m, b*alpha^n is integer if and only if 4^m divides b.
**This is a numeric/graph topology gate, not a cosmological prediction.**

## Implementation, tests, and limitations

Files:
- tools/rll_exact_quantized_orbit.py (new reference/oracle)
- tests/test_rll_exact_quantized_orbit.py (new seven local unittest methods)

Local host execution on 2026-10-24 (separate from provider CI):
- seven unittest methods PASS;
- 384 exact integer inequality certificates for b in {6,7,8,13,16,100}, 64 exponents;
- 180 independent Decimal cross-checks for odd n at precision 130;
- boundary, cycle/permutation, invalid-input and near-boundary perturbation gates.
The exact scope of these counts must not be inherited by any RLL branch HEAD unless rerun there.

Outstanding: exact-head GitHub CI, independent review, input-size/time/memory bounds, benchmarking, fixed-width overflow analysis, ARM32/ARM64 physical device execution and upstream math-producer adoption remain TOKEN_VAZIO. Integer arbitrary precision is **not** O(1) memory and does not satisfy freestanding/heapless deployment claims.

## Applicability gate to RLL

Allowed now: read-only formal verifier, fixture generator, research documentation, falsifier for integer-discretized cyclic graphs.

Not allowed without a new authorized, independently reviewed experiment: changing cosmological likelihoods, CMB/DESI parameters, physical field equations, geodesic solvers, toroidal dynamics, existing CI workflows, generated evidence or public scientific claims.

Proposed future consumer contract (not implemented): declared base/modulus; declared quantizer; exact mathematical object; fixed-width overflow policy or typed unknown; evidence of repeatability and scientifically meaningful data mapping. Do not infer a physical observable from an abstract arithmetic cycle.

## Prior art / references and non-copying boundary

- Li et al., "MSz: An Efficient Parallel Algorithm for Correcting Morse-Smale Segmentations in Error-Bounded Lossy Compressors," arXiv:2406.09423. Supports the general concern that small numeric deviations may alter topology of scientific outputs. This RLL module does **not** implement, copy or reproduce their algorithm.
- "Preserving Continuous Symmetry in Discrete Spaces: Geometric-Aware Quantization for SO(3)-Equivariant GNNs," arXiv:2603.05343 — related research context, not a validation of this oracle.
- RAFAELIA theory ledger 2026-09-05 (Drive ID 1mOw5adv9okRlWIO-AneslhUw-9GqlOGT), identity-only theory hashing, including preserving geometric scale in 77/33 versus 7/3.
- RLL docs/research/SIGMA_RAFAELIA_TRIANGULAR_TORUS_TYPED_VOID_ADAPTER_GATE_20261023.md — existing uncoupled science boundary.
- RLL docs/research/RLL_GEOMETRIC_DISPERSION_FALSE_POSITIVE_GATE_V1.md — geometric false-positive controls.

Classical mathematics and external literature are credited; no source logic, code structure, or copyrighted passages from those publications were copied.

## Falsifiers / R3 / rollback

Falsifier F1: one certified squared-inequality fixture violates floor bounds.  
Falsifier F2: a cycle count or permutation sign disagrees with explicit enumeration for small b.  
Falsifier F3: any scientific model or CI gate begins importing this mathematical reference without a separate reviewed contract.

Rollback: revert only the three additive files on the feature branch, keeping Git history and receipts; no deletion of predecessors.

R3: F_ok=local seven tests and exact arithmetic; F_gap=independent verification, RLL CI, ARM, physics and publication; F_next=review draft PR to rll/lab and separate mathematical producer contract before considering any physical usage.  
**PROMOTION=HOLD**. **claim_allowed=false**.
