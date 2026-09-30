# Prime-Scale Falsifiable Subset — RLL Validation Intake

**Date:** 2026-09-15  
**State:** MATH_IMPORT_VERIFIED_LIMITED / EMPIRICAL_GATE_OPEN / claim_allowed=false  
**RLL authority:** empirical/falsifiable projection only. Exact mathematical authority remains in rafaelmeloreisnovo/Matem-tica-.  
**Mathematics branch commit:** fe9fa1fb5801d01e10c181012610b44ede56a0bc  
**Papers branch commit:** 6c50608578463318c8e8cb5f98414299268d712b  
**Predecessor:** PapersPub/08_multiscale_validation_methods/session_theory_hashing_20260905.md

## 1. Intake boundary

This appendix imports only the subset of the 200-formula session catalog that can function as:

- an exact mathematical transform;
- a deterministic sampler;
- a falsifier/diagnostic;
- a statistical model-selection component;
- or a preregistered empirical hypothesis.

It does NOT promote any mathematical coincidence into a physical/cosmological law.

Invariants:

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM  
MATHEMATICAL_EXACTNESS != PHYSICAL_VALIDATION  
PRIME_INDEXING != PRIME_CAUSATION  
42_COMBINATORICS != 42_PHYSICAL_ATTRACTORS  
SAME_CONSTANT != SAME_MECHANISM  
claim_allowed=false.

## 2. Imported exact kernel

Let

\[
q=\frac{\sqrt3}{2},\qquad p_k\in\mathbb P,\qquad
g_k=p_{k+1}-p_k.
\]

The following are accepted as mathematical inputs under their declared definitions:

\[
R_k=q^{p_k},
\]

\[
\frac{R_{k+1}}{R_k}=q^{g_k},
\]

and, for consecutive primes above 3,

\[
\boxed{
\frac{R_{k+1}}{R_k}
=
\left(\frac34\right)^{g_k/2}
}.
\]

If angular sampling is defined by

\[
\theta_k=p_k\theta_0,
\]

then

\[
\Delta\theta_k=g_k\theta_0.
\]

Define the complex sampler

\[
z_k=q^{p_k}e^{ip_k\theta_0}.
\]

Then

\[
\boxed{
\frac{z_{k+1}}{z_k}
=
(qe^{i\theta_0})^{g_k}
}.
\]

RLL interpretation: deterministic mathematical sampler only.  
Physical interpretation: TOKEN_VAZIO.

## 3. Multiscale threshold

The q-scale gives

\[
q^{32}\approx0.0100226,
\qquad
q^{33}\approx0.00867982.
\]

Thus 33 is the first integer depth below 1% linear scale.

Allowed RLL use:

- stopping criterion;
- scale-window boundary;
- deterministic multiscale binning parameter.

Blocked interpretation:

- “33 is physically fundamental”;
- universal biological/cosmological meaning.

Those require independent mechanism and evidence.

## 4. Affine recurrence and 42-period falsifier

For the session recurrence

\[
x_{n+1}=qx_n+c,
\qquad
c=-\pi\sin279^\circ,
\]

the fixed point is

\[
x_*=\frac{c}{1-q}\approx23.16046864,
\]

and

\[
x_n=x_*+q^n(x_0-x_*).
\]

Prime-indexed sampling gives

\[
x_{p_k}=x_*+q^{p_k}(x_0-x_*),
\]

with

\[
\boxed{
\frac{x_{p_{k+1}}-x_*}{x_{p_k}-x_*}
=
\left(\frac34\right)^{g_k/2}
}.
\]

A nonstationary exact 42-periodic orbit would require

\[
q^{42}=1,
\]

which is false for \(q=\sqrt3/2\).

Therefore RLL records:

\[
\boxed{
\text{AFFINE_Q_RECURRENCE}
\neq
\text{NONTRIVIAL_EXACT_PERIOD_42}
}
\]

unless a different map/projection/forcing rule is explicitly supplied.

Diagnostic:

\[
D_{42}(n)=|1-q^{42}|\,|x_n-x_*|.
\]

For toroidal states:

\[
D^T_{42}(t)=d_T(s_{t+42},s_t).
\]

Exact period claim requires zero distance under the declared metric/tolerance contract; approximate recurrence requires a preregistered epsilon.

## 5. Prime-indexed spectral operator

For a sequence \(x_n\), define

\[
S_{\mathbb P}(\omega)
=
\sum_k x_{p_k}e^{-i\omega p_k}.
\]

RLL use: nonuniform/prime-indexed spectral probe.

Required baselines:

1. all-index sampling;
2. uniform sparse sampling with same cardinality;
3. random sparse sampling with same cardinality;
4. residue-matched sampling;
5. Ulam-style prime geometry when spatial comparison is relevant.

No “prime frequency physics” claim is permitted from this operator alone.

## 6. Modulo-42 routing

Classical facts:

\[
42=2\cdot3\cdot7,
\]

\[
U(42)=
\{1,5,11,13,17,19,23,25,29,31,37,41\},
\]

\[
\phi_E(42)=12.
\]

For primes \(p>7\),

\[
p\bmod42\in U(42).
\]

RLL may use the 12 invertible classes as a categorical/indexing feature.

Null model requirement: compare against the distribution expected from standard arithmetic constraints and against simpler modulus choices. Residue structure alone is not physical evidence.

## 7. Statistical gates

For any observational fitting use:

\[
\chi^2
=
\sum_i
\left(
\frac{y_i-\hat y_i}{\sigma_i}
\right)^2,
\]

\[
AIC=2k-2\ln\hat L,
\]

\[
BIC=k\ln n-2\ln\hat L.
\]

For Prime-Spiral/radial-gap fitting:

\[
L_P
=
\sum_k
\left[
\ln\left(\frac{R_{k+1}}{R_k}\right)
-
g_k\ln q
\right]^2.
\]

For observed geometric data, a candidate q/prime model must be compared against at least:

- unconstrained logarithmic spiral;
- non-prime q sampler;
- uniform-index sampler;
- random-index sampler;
- domain-standard model.

A lower error on the training set alone is insufficient.

## 8. Preregistered hypothesis set

### RLL-PS-H1 — deterministic algebra reproduction

The implementation reproduces the prime-gap contraction identities to declared numerical tolerance.

State: EXACT_MATH_TEST.  
Falsifier: any reproducible mismatch.

### RLL-PS-H2 — Prime-Spiral distinguishability

Prime-Spiral sampling produces a statistically distinguishable signature from cardinality-matched baseline samplers under preregistered metrics.

State: EMPIRICAL_MATH_HYPOTHESIS.  
Falsifier: null/negative result after multiplicity control.

### RLL-PS-H3 — task utility of U(42) routing

The 12 coprime classes improve a specified prediction/indexing/compression task over simpler baselines after accounting for model complexity.

State: EMPIRICAL_COMPUTATIONAL_HYPOTHESIS.  
Falsifier: no held-out advantage.

### RLL-PS-H4 — 33-depth algorithmic utility

Using the derived q-depth 33 as a stopping boundary improves a declared multiscale procedure against direct epsilon and alternative-depth baselines.

State: EMPIRICAL_COMPUTATIONAL_HYPOTHESIS.  
Falsifier: no robust advantage or equivalence to trivial epsilon thresholding.

### RLL-PS-H5 — approximate 42 recurrence

A declared RLL state series exhibits \(D^T_{42}\le\varepsilon\) more often/strongly than null surrogates.

State: TOKEN_VAZIO_DATA.  
Falsifier: no excess recurrence over preregistered nulls.

This H5 is NOT derived from the affine q recurrence.

## 9. Blocked imports from the 200-formula catalog

The following are intentionally NOT promoted into RLL empirical claims by this intake:

- consciousness/observer interpretations;
- Buckingham/health associations;
- Sigma-SEAL or custom-hash security claims;
- OmegaZIP violation of Shannon;
- physical meaning of E_link without units/mechanism;
- 42 as a physical attractor count;
- Fibonacci/prime causation of galaxy morphology;
- quantum-state meaning of a generic 7D vector;
- biological/cardiac interpretation without defined datasets/protocols;
- ATOMIC_EX_LIGHT or radioluminescence mechanism claims.

State for each: TOKEN_VAZIO_EVIDENCE or BLOCKED_BY_DOMAIN_GATE.

## 10. Minimal executable packet

A future verifier should output deterministic receipts for:

1. prime generation and gap list;
2. algebraic ratio checks;
3. complex Prime-Spiral ratio checks;
4. affine fixed-point and prime-sampled convergence checks;
5. modulo-42 unit-class checks;
6. q-depth 1% crossing;
7. baseline samplers;
8. AIC/BIC/held-out comparison;
9. \(D^T_{42}\) null-surrogate test.

Until such execution exists:

IMPLEMENTED = false  
REPRODUCED = false  
EMPIRICAL_PASS = TOKEN_VAZIO  
claim_allowed = false.

## 11. R3

F_ok = coherent mathematical/falsifiable subset routed into RLL with explicit baselines and negative gates.  
F_gap = executable verifier, observational dataset, preregistration, prior-art, independent reproduction.  
F_next = implement deterministic math verifier first; only then attach domain data and statistical comparison.  
claim_allowed = false.
