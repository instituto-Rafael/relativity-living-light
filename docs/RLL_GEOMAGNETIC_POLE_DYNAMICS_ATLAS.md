# RLL Geomagnetic Pole Dynamics Atlas V1

**State:** `BOUNDED_RESEARCH / claim_allowed=false`  
**Date:** 2026-09-08  
**Execution:** `data/pipelines/geomagnetism/pole_dynamics_gate.py`  
**Contract:** `data/contracts/geomagnetic_pole_dynamics.v1.json`

## 1. Purpose

This adapter uses modern geomagnetic field research as an independent falsification domain for geometric and dynamical operators. It does **not** treat the north magnetic pole as a material body, does **not** equate geomagnetic flow with gravity-assist dynamics, and does **not** infer an RLL cosmological effect from a geomagnetic fit.

The source hierarchy is:

```text
WMM / WMMHR / IGRF / CHAOS / Swarm observations
  -> field and secular variation
  -> field-defined dip-pole zero
  -> pole velocity / acceleration / curvature
  -> source-sensitivity and flow residuals
  -> pre-registered geometric comparisons
  -> falsify / retain TOKEN_VAZIO / bounded evidence
```

## 2. Modern literature anchors

| Source | Year | What is imported into the adapter |
|---|---:|---|
| Livermore, Finlay & Bayliff, Nature Geoscience, DOI `10.1038/s41561-020-0570-9` | 2020 | Canada/Siberia core-mantle-boundary flux-lobe mechanism for north magnetic pole motion |
| Finlay, Kloss & Gillet, PEPI, DOI `10.1016/j.pepi.2025.107447` | 2025 | Eleven-year Swarm description of core-field changes; Canadian strong-field region weakens while Siberian region strengthens |
| Claveau et al., EPS, DOI `10.1186/s40623-025-02248-z` | 2025 | AR-3 temporal cross-covariance prior and short-period spectral cutoff near the core Alfvén time |
| Shakespeare-Rees et al., PEPI, DOI `10.1016/j.pepi.2025.107424` | 2025 | Regional Physics-Informed Neural Network core-flow inversions |
| Madsen et al., EPS, DOI `10.1186/s40623-025-02347-x` | 2026 | Forecasting SV from sinusoidal core-flow acceleration coefficients |
| Shakespeare-Rees et al., EPS, DOI `10.1186/s40623-026-02427-6` | 2026 | IGRF-14 PINN SV forecast using frozen-flux induction equation |
| Kloss et al., EPS, DOI `10.1186/s40623-025-02352-0` | 2026 | CHAOS-8; modern temporal regularization and rapid CMB SV features |
| Beggan et al., EPS, DOI `10.1186/s40623-025-02360-0` | 2026 | Final IGRF-14 spherical-harmonic reference model and 2025-2030 predictive SV |
| NOAA/BGS WMM2025, model DOI `10.25921/aqfd-sd83` | 2024/25 | Navigation-grade main-field and secular-variation coefficients |

## 3. Derivation A — magnetic pole as a moving zero

In a regular local surface chart `p=(x,y)`, define the horizontal magnetic field

\[
\mathbf h(\mathbf p,t)=
\begin{pmatrix}
B_\theta(\mathbf p,t)\\
B_\phi(\mathbf p,t)
\end{pmatrix}.
\]

A magnetic dip pole satisfies

\[
\mathbf h(\mathbf p_*(t),t)=0.
\]

Differentiating the zero condition gives

\[
J_h\dot{\mathbf p}_*+\partial_t\mathbf h=0,
\]

hence

\[
\boxed{\dot{\mathbf p}_*=-J_h^{-1}\partial_t\mathbf h}.
\]

This operator estimates local pole velocity directly from field derivatives. It is valid only where the horizontal-field Jacobian is nonsingular and the coordinate chart is regular.

A second differentiation gives

\[
\boxed{
J_h\ddot{\mathbf p}_*= -\left[
\mathbf h_{tt}
+2\mathbf h_{xt}\dot{\mathbf p}_*
+\mathbf H_h[\dot{\mathbf p}_*,\dot{\mathbf p}_*]
\right]
}.
\]

This provides a field-derivative definition of pole acceleration rather than relying only on finite differences of annual pole coordinates.

## 4. Derivation B — Canada/Siberia lobe sensitivity

For a source-traced additive decomposition

\[
\mathbf h=
\alpha_C\mathbf h_C+
\alpha_S\mathbf h_S+
\mathbf h_R,
\]

implicit differentiation with respect to source amplitude gives

\[
\boxed{
\frac{\partial\mathbf p_*}{\partial\alpha_i}
=-J_h^{-1}\mathbf h_i
}.
\]

This is the quantitative version of a two-lobe competition experiment: it gives the local displacement vector of the dip-pole zero per unit change in a specified source component.

**Boundary:** the decomposition itself is not uniquely inferred by this equation. A Canada/Siberia interpretation is allowed only when `h_C` and `h_S` are produced by a documented field decomposition.

## 5. Derivation C — frozen-flux residual

Recent core-flow work uses the reduced induction equation

\[
\dot B_r+\nabla_H\cdot(\mathbf u_H B_r)=0
\]

under the advection-dominated/frozen-flux approximation. Expanding the divergence defines a diagnostic residual

\[
\boxed{
R_{ff}=\dot B_r+\mathbf u_H\cdot\nabla_H B_r+B_r\nabla_H\cdot\mathbf u_H
}.
\]

`R_ff=0` closes the chosen advection-only model numerically. A nonzero value does **not** uniquely measure magnetic diffusion; it may also contain field-model error, unresolved flow, external contamination or numerical error.

## 6. Derivation D — CHAOS-8 wave number to Madsen-period cross-check

CHAOS-8 reports a small-scale eastward-moving CMB SV feature with approximate azimuthal wave number

\[
m=13
\]

and phase speed near

\[
v_\phi\approx200\;\mathrm{km\,yr^{-1}}
\]

at the CMB equator after 2012. For CMB radius

\[
R_{CMB}=3485\;\mathrm{km},
\]

the azimuthal wavelength and crest-passage period are

\[
\lambda_m=\frac{2\pi R_{CMB}}{m},
\qquad
T_m=\frac{\lambda_m}{v_\phi}
=\frac{2\pi R_{CMB}}{m v_\phi}.
\]

Numerically,

\[
\boxed{\lambda_{13}\approx1684.377\;\mathrm{km}}
\]

and

\[
\boxed{T_{13}\approx8.421885\;\mathrm{yr}}.
\]

Madsen et al. (2026) independently report that the Swarm toroidal flow-acceleration coefficient period distribution peaks around **8-9 years**. This is a useful cross-paper numerical consistency check.

**It is not evidence that both analyses isolate the same physical mode.** Establishing modal identity requires phase, spatial structure, uncertainty and independent reproduction.

## 7. Derivation E — periodic acceleration fit

For a predeclared period `tau`, the recent IGRF-14 flow-acceleration forecast fits

\[
\gamma(t)=A\sin\left(\frac{2\pi t}{\tau}\right)
+B\cos\left(\frac{2\pi t}{\tau}\right).
\]

The adapter implements the corresponding two-column linear least-squares solution and a deterministic scan over `1..20 yr` in `0.1 yr` steps. The period scan is an external scientific operator; it is not a RAFAELIA-frequency fit.

## 8. Derivation F — pre-registered `sqrt(3)/2` falsifier

The prior three-spiral construction uses

\[
q=\frac{\sqrt3}{2}.
\]

To prevent post-hoc fitting, `q` is fixed before real geomagnetic data are evaluated. For a positive scalar observable `x_n` declared in advance, define

\[
\boxed{
R_q=
\sqrt{\frac1{N-1}
\sum_n
\left[
\log\left(\frac{x_{n+1}}{x_n}\right)-\log q
\right]^2}
}.
\]

A perfect `q`-geometric sequence gives `R_q=0`. The observable itself must be predeclared (for example step length, local osculating radius, or another intrinsic trajectory quantity). Selecting an observable after seeing which one matches `q` invalidates the test.

The golden-ratio/quarter-turn test is deliberately **disabled by default** until a projection center and quarter-turn definition are pre-registered. This prevents an arbitrary center from manufacturing a logarithmic spiral.

## 9. Real-data execution ladder

```text
E0 SOURCE
  official WMM2025 / IGRF-14 / CHAOS-8 coefficients

E1 INTEGRITY
  SHA-256 + version + epoch + coefficient normalization

E2 FIELD
  reproduce official test values / magnetic components

E3 POLE
  solve H=sqrt(B_theta^2+B_phi^2) -> minimum/zero

E4 TRAJECTORY
  latitude/longitude -> great-circle step, velocity, acceleration, turning

E5 SOURCE SENSITIVITY
  only if Canada/Siberia source decomposition is supplied

E6 MODERN-MODE TESTS
  frozen-flux residual, sinusoidal acceleration, m-v-T consistency

E7 RAFAELIA FIXED TESTS
  q=sqrt(3)/2 with no fitted q; phi gate only after center pre-registration

E8 CLAIM
  remains false unless independent real-data evidence satisfies FALSIFIABILITY_PROTOCOL.md
```

## 10. Current status

```yaml
SOURCE_WMM2025_CHECKSUM: TOKEN_VAZIO
SOURCE_IGRF14_CHECKSUM: TOKEN_VAZIO
SOURCE_CHAOS8_CHECKSUM: TOKEN_VAZIO
REAL_POLE_TRAJECTORY_EXECUTION: TOKEN_VAZIO
REAL_CANADA_SIBERIA_SOURCE_SENSITIVITY: TOKEN_VAZIO
REAL_SQRT3_OVER_2_MATCH: TOKEN_VAZIO
REAL_PHI_MATCH: TOKEN_VAZIO
claim_allowed: false
```

Synthetic tests validate only the implementation mechanics.

## 11. R3

**F_ok:** modern literature is converted into explicit velocity, acceleration, source-sensitivity, frozen-flux, wave-period and sinusoidal-fit operators; the `sqrt(3)/2` test is fixed before data.  
**F_gap:** official coefficient bytes/checksums and a source-traced Canada/Siberia decomposition are not yet bound.  
**F_next:** bind one official coefficient product, reproduce its reference values, reconstruct the north dip-pole trajectory, then run the pre-registered diagnostics without changing thresholds or observables after viewing results.
