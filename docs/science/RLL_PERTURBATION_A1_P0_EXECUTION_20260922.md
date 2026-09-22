# RLL P0 — Perturbation Closure A1.1 Execution

**Date:** 2026-09-22  
**Authority:** instituto-Rafael/relativity-living-light  
**State:** MATERIALIZED / CANONICAL CI PENDING  
**claim_allowed:** false

## Why this delta exists

The RLL background is executable, but a background function does not uniquely determine
linear perturbations. The previous minimal closure

\[
c_s^2=c_a^2,\qquad Q_\mu=0,\qquad \sigma_s=0
\]

was tested and failed all 9 declared transition cases as a global default.

That negative result is preserved.

The next bounded route already identified by the repository is A1:
a separately conserved effective fluid with an **independent rest-frame pressure closure**.

## Candidate A1.1

This successor instantiates one research candidate:

\[
p_{\rm cons}
=
-\rho_s-\frac13\frac{d\rho_s}{d\ln a},
\]

\[
c_{s,\mathrm{rest}}^2=1,
\qquad
Q_\mu=0,
\qquad
\sigma_s=0.
\]

The value \(c_{s,\mathrm{rest}}^2=1\) is not inferred from the logistic background.
It is an explicit candidate assumption corresponding to the canonical minimally-coupled
scalar reference sub-route already documented in the RLL corpus.

Therefore:

\[
\boxed{
\text{candidate assumption}
\neq
\text{derived RLL property}
}
\]

## What can be tested now

The executable gate evaluates nine \((z_t,w_t)\) combinations over
\(0\le z\le10^4\).

Necessary tests:

1. \(\rho_s\) remains finite and positive;
2. \(p_{\rm cons}\) and \(w_{\rm cons}\) remain finite;
3. the separately-conserved continuity residual is zero within tolerance;
4. \(1+w_{\rm cons}\ge0\) within tolerance over the declared sweep;
5. \(0\le c_{s,\mathrm{rest}}^2\le1\).

These are necessary conditions only.

## What cannot yet be tested honestly

The candidate still lacks:

- C01: a full \(\delta_s\) evolution equation;
- C02: a full \(\theta_s\) / Euler equation;
- C07: gauge convention and CLASS↔CAMB mapping;
- C07: super-horizon initial conditions;
- C08: perturbative transition/crossing regularization;
- a constraint/Bianchi residual calculation for the full perturbed system.

Therefore a PASS here must produce:

\[
\texttt{A1\_1\_NECESSARY\_GATES\_PASS\_GAUGE\_IC\_OPEN}
\]

and never:

\[
\texttt{PERTURBATION\_CLOSURE\_RESOLVED}.
\]

## CLASS/CAMB boundary

CLASS and CAMB RLL perturbation implementations remain blocked until the same frozen
A1.1 closure has complete C01/C02/C07/C08 equations and passes limiting, gauge,
constraint and regularity tests.

The standard LCDM/CPL CLASS/CAMB crosscheck remains an independent baseline authority.
The existing RLL recombination benchmark remains a background/recombination benchmark,
not an RLL perturbation backend.

## Dependency graph

\[
\boxed{
A1.1
\to
\text{gauge}
\to
(\delta_s,\theta_s)
\to
\text{IC}
\to
\text{Bianchi/constraints}
\to
\text{regularity}
\to
\text{CLASS}
\parallel
\text{CAMB}
\to
\text{cross-engine parity}
}
\]

Only after that chain can exact \(D(z)\), \(f(z)\), \(f\sigma_8\), CMB \(C_\ell\)
and linear \(P(k)\) be attributed to an RLL perturbation model.

## Rollback

If A1.1 fails any necessary or later perturbative gate:
- preserve the receipt;
- mark A1.1 REFUTADO for that scope;
- remove only this candidate as active successor;
- restore A1 to open/TOKEN_VAZIO;
- do not erase A0 negative evidence or the C background-only fallback.

## R3

F_ok:
- A1.1 candidate fully typed;
- C03/C04/C05/C06 assumptions explicit;
- executable necessary-condition gate and tests materialized;
- CLASS/CAMB dependency routing updated;
- registry distinguishes derived pressure identity from candidate sound speed.

F_gap:
- C01, C02, C07 and perturbative C08;
- full perturbed conservation/Bianchi gate;
- independent RLL CLASS/CAMB implementation;
- exact growth and observational likelihood propagation.

F_next:
- consume canonical CI for A1.1;
- if necessary gates PASS, freeze a gauge contract and derive C01/C02 plus super-horizon IC;
- otherwise preserve FAIL and return A1 to open state.
