# RLL — Heterogeneous Residual Geometry Composite V2

**Date:** 2026-09-28  
**State:** \`IMPLEMENTED_UNTESTED_PROVIDER / claim_allowed=false\`  
**Author/proponent:** Rafael Melo Reis  
**Producer:** \`instituto-Rafael/relativity-living-light\`

## 0. Purpose

Extend the already-governed full-covariance residual diagnostic without replacing standard deviation, covariance or likelihood.

The central distinction is:

\[
\text{statistical authority}\neq\text{diagnostic geometry}.
\]

For the frozen DESI DR2 surface:

\[
r=y-m,\qquad C=LL^T,\qquad z=L^{-1}r,\qquad \chi^2=z^Tz.
\]

V2 leaves \(C\), \(z\), \(\chi^2\), AIC/BIC and model weights untouched. It asks whether the **shape of the already-whitened residual** changes across declared scales and typed geometric projections.

## 1. Standard deviation remains standard deviation

Population:

\[
\sigma^2=\frac1N\sum_{i=1}^{N}(x_i-\mu)^2.
\]

Sample:

\[
s^2=\frac1{n-1}\sum_{i=1}^{n}(x_i-\bar x)^2.
\]

For correlated observations the committed covariance matrix is stronger than a single scalar sigma because it includes variances and cross-covariances.

Hard boundary:

\[
\boxed{\sqrt3/2\neq\sigma}.
\]

The geometric constant \(\sqrt3/2\), Fibonacci scales and Poincaré coordinates never substitute for statistical dispersion.

## 2. Heterogeneity / residual budget

V1 already preserves:

\[
TSS=WSS+BSS
\]

and residual classes \`DELTA_MEASUREMENT\`, \`DELTA_MODEL\`,
\`DELTA_OMITTED_VARIABLE\`, \`DELTA_LATENT\`, \`DELTA_STOCHASTIC\`,
and \`DELTA_UNCLASSIFIED\`.

An unexplained residual remains visible until evidence permits reclassification:

\[
DELTA_{UNCLASSIFIED}\xrightarrow{\text{evidence}}DELTA_{typed}.
\]

Reclassification does not erase the original observation.

## 3. Two recurrence/matrix families

### 3.1 Classical Fibonacci

\[
F_{n+1}=F_n+F_{n-1},
\qquad
Q_F=
\begin{pmatrix}1&1\\1&0\end{pmatrix}.
\]

For the 13-element DESI residual vector, diagnostic windows are:

\[
2,3,5,8,13.
\]

### 3.2 Rafael affine +1 recurrence

The corpus records:

\[
R_{n+1}=R_n+R_{n-1}+1
\]

and equivalently:

\[
R_n=F_{n+3}-1.
\]

The affine recurrence is represented in homogeneous coordinates:

\[
\begin{pmatrix}
R_{n+1}\\R_n\\1
\end{pmatrix}
=
\begin{pmatrix}
1&1&1\\
1&0&0\\
0&0&1
\end{pmatrix}
\begin{pmatrix}
R_n\\R_{n-1}\\1
\end{pmatrix}.
\]

With seeds \(1,2\), the bounded DESI window family is:

\[
2,4,7,12.
\]

Both families are diagnostic scales only:

\[
FIBONACCI\_WINDOW\neq LIKELIHOOD\_WEIGHT,
\]

\[
RAFAEL\_AFFINE\_WINDOW\neq LIKELIHOOD\_WEIGHT.
\]

## 4. Window diagnostics

For every declared window on the whitened residual \(z\), V2 computes:

1. mean, population variance, sum of squares and RMS;
2. first-difference and second-difference energy;
3. endpoint finite-difference tangent;
4. least-squares quadratic \(z(t)\approx at^2+bt+c\) and the Bhaskara discriminant
   \[
   \Delta_B=b^2-4ac;
   \]
5. graph-triangle descriptors from first/middle/last points;
6. generic Poincaré-ball lift;
7. seven-dimensional Poincaré prefix when the window has at least seven entries;
8. unit-sphere/geodesic directional descriptor.

The quadratic discriminant is a shape descriptor:

\[
\Delta_B\neq\Delta\chi^2\neq \text{causal discriminator}.
\]

## 5. Pitágoras / isosceles / equilateral / tangency

The formal predecessor chain is preserved:

\[
\text{Pythagoras}
\to
\text{projection/difference}
\to
\text{medians/isoceles}
\to
\text{quadratic polynomial}
\to
\text{Bhaskara/discriminant}
\to
\text{cut/tangency}
\to
\text{torus/sphere}
\to
\text{Poincare section}.
\]

For equal sides \(L\) and half-apex angle \(\alpha\):

\[
b=2L\sin\alpha,\qquad h=L\cos\alpha.
\]

At \(\alpha=30^\circ\):

\[
b=L,\qquad h=(\sqrt3/2)L.
\]

V2 reports normalized deviation from these geometric classes; it does not assert that a residual graph triangle is physically equilateral or isosceles.

## 6. Poincaré nD and 7D

For a diagnostic vector \(x\in\mathbb R^d\), V2 uses the bounded computational map

\[
u=\frac{x}{1+\|x\|}.
\]

Then \(\|u\|<1\), and the curvature \(-1\) Poincaré-ball distance from the origin is

\[
d_{\mathbb B}(0,u)=2\,\operatorname{atanh}(\|u\|).
\]

For windows of size at least seven, the first seven components additionally enter a 7D namespace.

This is consistent with the separately formalized 7D hyperboloid-to-ball architecture, but does not make the DESI residual a physical hyperbolic spacetime.

\[
POINCARE\_BALL\neq POINCARE\_RETURN\_MAP\neq POINCARE\_CONJECTURE.
\]

## 7. Geodesic sphere descriptor

A nonzero residual window is normalized to a point on \(S^{d-1}\):

\[
\hat z=\frac{z}{\|z\|}.
\]

V2 records the great-circle angle to a declared uniform reference direction. This is a directional diagnostic, not a physical geodesic-sphere claim.

The existing icosphere \(f=2\) authority remains separate:

\[
(V,E,F)=(42,120,80).
\]

## 8. Venturi adapter

The project contains a fluid branch using continuity and Bernoulli:

\[
A_1v_1=A_2v_2,
\]

\[
P+\frac12\rho v^2+\rho gh=\mathrm{constant}
\]

under its assumptions.

DESI BAO residuals do not supply the required fluid state. Therefore V2 records:

\`TOKEN_VAZIO_FLUID_BINDING\`.

Promotion requires geometry, fluid identity, units, boundary conditions, viscosity, temperature, covariance and a falsifier.

\[
VENTURI_{PHYSICAL}\neq VENTURI_{METAPHOR}\neq VENTURI_{COMPUTATIONAL}.
\]

## 9. Calendar / Maya route

Project sources contain calendar-comparison work and Calendar Round arithmetic:

\[
\operatorname{lcm}(365,260)=18980\text{ days}.
\]

This may define temporal comparison windows for a genuine time-indexed dataset. DESI redshift ordering is not a Maya/calendar time coordinate.

Therefore V2 records:

\`TOKEN_VAZIO_TEMPORAL_BINDING\`.

\[
CALENDAR\_PERIODICITY\neq ASTROPHYSICAL\_MECHANISM.
\]

## 10. Source and authority

### Formal mathematics
- \`rafaelmeloreisnovo/Matem-tica-/docs/formal/PITAGORAS_BHASKARA_ISOSCELES_POINCARE_CROSSWALK_V1.md\`
- \`.../GEODESIC_PI_PHI_MOD7_INVARIANTS_V1.md\`

### Publication/crosswalk
- \`rafaelmeloreisnovo/papers/research_notes/2026-09-19_EIGHT_CONNECTED_GEOMETRY_PREDECESSOR_CROSSWALK_V1.md\`
- \`.../docs/matematica/FORMALISMO_HIPERBOLICO_7D_POINCARE_AUDITORIA_V1.md\`
- \`.../papers/archaeoastronomy_geometry_calendar_invariants_v1/paper.md\`

### Drive documentary memory
- \`1D5BiFz50W-nHD1Qeo8meZXZd_4tUWe0pLWuqeUly6YQ\` — isosceles / Pythagoras
- \`1Wrkcwhf7YRDCbcG5biP1DDqLI43CtuMzlb-yknIicJk\` — angular / sqrt3/2 / geodesic
- \`1bcF3RlvPrLMyKn2MNLtFEzYWtAflKSW34jm5DWEEdtE\` — geodesic/toro/Fibonacci
- \`1vaLvqB-lWSGaIXzUYSFXjLWvA54yicRVy_PanN_SH7U\` — icosphere f=2 / Fibonacci
- \`18g4LXbZjA-LmgiLIjFLDTbD1dtl5EJF_GTXiWQvjXPI\` — error→attention
- \`1wSCyqfdmUd17aeRoj6mT34Iw37q6SA8n3_6hl2eB7KE\` — physical Venturi/hydraulics

Drive is documentary memory; RLL is integration/runtime producer.

## 11. Testable invariants

Provider gate must verify:

1. Fibonacci scales \(2,3,5,8,13\);
2. Rafael affine scales \(2,4,7,12\);
3. affine homogeneous recurrence;
4. Poincaré nD lift always has \(\|u\|<1\);
5. a synthetic parabola recovers its coefficients;
6. baseline LCDM/RLL \(\chi^2\) remains unchanged;
7. Venturi/calendar remain blocked on the DESI surface;
8. \(\sqrt3/2\neq\sigma\) remains explicit.

## 12. Promotion boundary

A software PASS would establish only that the composition is internally consistent and non-invasive to the frozen likelihood.

It would not establish RLL superiority, a new physical law, physical Poincaré geometry of the Universe, Venturi behavior in cosmological residuals, Maya/calendar causality, or universal significance of Fibonacci or \(\sqrt3/2\).

## R3

\`\`\`text
F_ok =
  full covariance remains authority
  + residual geometry becomes multiscale and typed
  + classical/Rafael Fibonacci coexist without weighting likelihood
  + Pythagoras/Bhaskara/tangent/Poincare/geodesic descriptors are explicit

F_gap =
  provider execution
  + held-out/non-null model discrimination
  + physical domain bindings
  + independent reproduction

F_next =
  execute provider gate
  -> freeze held-out/non-null profile
  -> compare diagnostic stability without retuning
\`\`\`
