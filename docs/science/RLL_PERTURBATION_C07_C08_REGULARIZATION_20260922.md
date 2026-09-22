# RLL P0 — C07/C08 Gauge and Regular-Variable Preflight V1

**Date:** 2026-09-22  
**State:** FORMALIZED / CANONICAL CI PENDING  
**claim_allowed:** false

## Scope

A1.1 passed its nine necessary background/closure cases, but the next problem is not observational fitting. It is constructing perturbation variables that remain mathematically and numerically meaningful when the component approaches `w_s = -1`.

## Frozen representation convention

The derivation reference gauge is **synchronous**. This is a computational convention only; it is not a physical claim and does not yet define the independent CLASS/CAMB mappings.

Primary candidate variables:

\[
\delta\rho_s,
\qquad
q_s=(\rho_s+p_s)\theta_s.
\]

The fractional density contrast remains derived when \(\rho_s>0\):

\[
\delta_s=\frac{\delta\rho_s}{\rho_s}.
\]

Velocity divergence is not a primary variable near enthalpy degeneracy:

\[
\theta_s=\frac{q_s}{\rho_s+p_s}
\]

only where \(\rho_s+p_s\) is demonstrably nonzero and conditioned.

## Exact background identity

From the separately conserved candidate pressure

\[
p_s=-\rho_s-\frac13\frac{d\rho_s}{d\ln a},
\]

follows

\[
\boxed{\rho_s+p_s=-\frac13\frac{d\rho_s}{d\ln a}}.
\]

This identity is executable now and does not require a perturbation gauge.

## Regularity rule

The primary perturbation system must not contain an unproved naked division by \(1+w_s\). Numerical epsilon-clipping is explicitly forbidden as a substitute for an analytic limit.

The preflight therefore reports samples where \(|1+w_s|\) becomes small, but does not alter the equations.

## What remains TOKEN_VAZIO

- C01: evolution equation for \(\delta\rho_s\);
- C02: evolution equation for \(q_s\);
- C07: CLASS/CAMB gauge mapping;
- C07: super-horizon initial conditions;
- C08: analytic enthalpy-degenerate limit;
- C08: perturbed conservation/Bianchi/constraint residual.

## Promotion boundary

A preflight PASS means only that the regular-variable choice is algebraically coherent with the A1.1 background sweep. It does not establish the missing dynamics, stability, initial conditions, solver implementation, or physical validity.

## External-governance residual

Promotion PR #955 (`rll/lab -> rll/integration`) is intentionally blocked because the GitHub integration cannot read complete branch-protection authority above lab maturity. An active default-branch ruleset was observed, but the branch-protection endpoint returns 403 for the integration. No bypass is authorized.

## Next gate

Derive C01/C02 directly in \((\delta\rho_s,q_s)\), prove the enthalpy-degenerate limit analytically, then derive super-horizon IC and independent CLASS/CAMB mappings.
