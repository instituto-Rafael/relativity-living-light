# RLL — Dynamic Structural Geometry Context Router V1

**Date:** 2026-09-22  
**Author:** RAFAEL MELO REIS  
**Parent:** \`docs/canonicos/34_RMRCTI_OMEGA_WORLDLINE_CASCADE_ROUTER.md\`  
**Sibling:** \`docs/science/CAUSAL_SCENARIO_ENSEMBLE_BODY_Y_V1.md\`  
**State:** \`MODEL_CONTRACT / DYNAMIC_GEOMETRY_ROUTER / claim_allowed=false\`

## 0. Purpose

This layer formalizes a hybrid dynamic context for observations whose present physical state may differ from the state encoded in the received light.

It does **not** assume one global Euclidean geometry and does **not** promote RMRCTI \(\Delta P\approx0.18\) to a physical constant.

The central object is a region/event-specific geometry context:

\[
\Gamma_j=
(\mathcal D_j,g_j,\mathcal F_j,\mathcal T_j,\mathcal V_j,\mathcal O_j,\Sigma_j)
\]

where:

- \(\mathcal D_j\): spatial/spacetime domain;
- \(g_j\): metric or approved local approximation;
- \(\mathcal F_j\): reference frame/tetrad;
- \(\mathcal T_j\): relevant timescales;
- \(\mathcal V_j\): validity conditions;
- \(\mathcal O_j\): observables available in the region;
- \(\Sigma_j\): uncertainty/covariance.

The invariant is:

\[
\boxed{\text{geometry is selected by regime + evidence + validity, not visual resemblance}}
\]

## 1. Observation is a retarded state

Astronomical observation is not a simultaneous map of the current Universe.

For a photon worldline:

\[
g_{\mu\nu}k^\mu k^\nu=0.
\]

The observation state must preserve at least

\[
T_{\rm obs}=
\{t_{\rm emit},t_{\rm arrival},t_{\rm observer},\tau_{\rm source}\}.
\]

Therefore:

\[
\boxed{\text{observed position/state}\neq\text{guaranteed present position/state}}
\]

and

\[
\boxed{\text{same image epoch}\neq\text{same emission epoch for all distances}}.
\]

No object is propagated from its observed state to a present-state estimate without a declared dynamics model and covariance.

## 2. Dynamic structural state

For body/packet/object \(Y\):

\[
X_Y=
\left(
x^\mu,u^\mu,p^\mu,m,J,\omega,
\rho,T,B,\mathrm{composition},
\mathrm{provenance},\Sigma_X
\right).
\]

Between discrete events:

\[
X_{k+1}^{-}
=
\Phi_k
\left(
X_k^{+};\Gamma_k,\eta_k
\right).
\]

At an event:

\[
X_{k+1}^{+}
=
\mathcal E_{k+1}
\left(
X_{k+1}^{-};\xi_{k+1}
\right).
\]

Candidate events include, only when physically admitted by evidence:

- flyby / gravitational deflection;
- binary or multi-body interaction;
- gravitational slingshot;
- collision;
- merger;
- fragmentation/ejecta;
- tidal disruption;
- capture/ejection;
- accretion;
- shock/plasma impulse;
- strong-field passage.

Logical possibility is not assigned positive scientific weight without a likelihood/prior/evidence route.

## 3. Geometry/regime router

The router chooses the mathematical geometry by the local physical regime.

### G0 — Euclidean local diagnostic

Allowed for local shape/coordinate diagnostics when curvature and relativistic effects are negligible over the modeled domain.

Examples:
- circles, ellipses, polygons, cones, annuli;
- covariance ellipses;
- local tangent-plane projections.

Boundary:

\[
\text{Euclidean diagnostic geometry}\neq\text{spacetime metric}.
\]

### G1 — Newtonian / N-body weak field

Use when both:

\[
\epsilon_g=\frac{GM}{rc^2}\ll1,
\qquad
\beta_v=\frac{v}{c}\ll1
\]

within a predeclared tolerance.

Then:

\[
\dot{\mathbf r}=\mathbf v,
\qquad
\dot{\mathbf v}
=
-\sum_i GM_i
\frac{\mathbf r-\mathbf r_i}{|\mathbf r-\mathbf r_i|^3}
+
\mathbf a_{\rm NG}.
\]

### G2 — post-Newtonian / relativistic local dynamics

Use when weak-field Newtonian assumptions become insufficient but full numerical GR is not yet required.

The actual PN order is a model decision and must be recorded.

### G3 — strong gravity

Route to Schwarzschild/Kerr/geodesic or numerical-relativity machinery as required.

No Euclidean slingshot construction is accepted as a substitute for strong-field dynamics.

### G4 — plasma/MHD/GRMHD

Use for magnetized plasma, jets, shocks, disks and outflows when electromagnetic stress is dynamically relevant.

### G5 — cosmological FLRW background

Use for:

\[
H(z),E(z),D_H,D_M,D_A,D_L,\mu,\mathrm{BAO}.
\]

Local stellar collisions/ejections are not explained by the background Friedmann equation alone.

### G6 — observation/projection geometry

Instrument, sky projection, selection function, PSF, lensing, line-of-sight overlap and covariance are handled as an observation map:

\[
D=M_{\rm obs}(X,\Gamma)+\epsilon.
\]

## 4. Hybrid context

The full context for one datum is:

\[
\boxed{
\mathcal H=
(O,L,E,\Gamma,S,C,R)
}
\]

with:

- \(O\): observation and instrument provenance;
- \(L\): light-cone / retarded-time relation;
- \(E\): event-chain history;
- \(\Gamma\): local geometry/regime;
- \(S\): scenario ensemble;
- \(C\): covariance/uncertainty;
- \(R\): residuals and stability diagnostics.

This is the required "hybrid contextualization": no single layer is allowed to absorb the others.

## 5. Scenario ensemble for displaced/unexpected objects

For a source observed in an apparently surprising location/velocity, define:

\[
\mathcal S=
\{
s_{\rm native},
s_{\rm flyby},
s_{\rm slingshot},
s_{\rm binary\ eject},
s_{\rm merger},
s_{\rm fragment},
s_{\rm tidal},
s_{\rm capture},
s_{\rm strongfield},
s_{\rm projection}
\}.
\]

Posterior:

\[
P(s_j\mid D,M)
=
\frac{P(D\mid s_j,M)P(s_j\mid M)}
{\sum_kP(D\mid s_k,M)P(s_k\mid M)}.
\]

The router must preserve:

\[
\text{unexpected location}
\neq
\text{proof of exotic mechanism}.
\]

A mundane but rare dynamical history remains admissible until falsified.

## 6. Cascade sensitivity

For an event map

\[
X_{k+1}=F_k(X_k),
\]

define the local Jacobian:

\[
J_k=\frac{\partial F_k}{\partial X_k}.
\]

For a chain:

\[
A_{i\to j}
=
\left\|
J_{j-1}\cdots J_i
\right\|,
\]

and for numerical stability:

\[
\boxed{
\Lambda_{i\to j}
=
\sum_{k=i}^{j-1}\log\|J_k\|
}.
\]

Interpretation is diagnostic:

- \(\Lambda\gg0\): perturbation amplification candidate;
- \(\Lambda\approx0\): neutral/local-linear candidate;
- \(\Lambda\ll0\): contraction/recovery candidate.

Thresholds are domain-specific and must be calibrated before use.

## 7. RMRCTI ΔP adapter

Verified source lineage:

\`rafaelmeloreisnovo/llamaRafaelia/rmrCti/gbs3_color.c\`

The actual metric is:

\[
\boxed{
\Delta P=
P(stable\_any=1\mid peak)
-
P(stable\_any=1\mid nonpeak)
}.
\]

The recurring target \(\Delta P\approx0.18\) remains:

\[
\boxed{\texttt{STABILITY_CANDIDATE}}
\]

and not:

- physical pressure;
- cosmological density;
- force;
- gravitational constant;
- universal attractor;
- physical threshold.

A source re-check resolves the earlier spoken “around 70” ambiguity as a **decimal observation around 0.70**, not an index 70.

The committed RMRCTI artifact

`rmrCti/zone_stats.txt`

contains the exact row

```text
zone=28  refs=95  IC_mean=0.147400  PP_mean=0.136800  CV_mean=0.700000
```

and `rmrCti/omega_zone_pipeline_fix.c` computes `CV_mean` as the per-zone mean of `CV`.

The upstream implementation in `rmrCti/omega_metrics_v2.c` defines:

```text
CV = top10% value share using buckets
```

Therefore the reconciled state is:

\[
\boxed{CV_{mean}(zone\ 28)=0.700000}.
\]

Within the project this may be carried as a **stability/concentration proxy candidate**, but its source semantics must stay attached:

\[
CV_{mean}=0.70
\neq
stable\_any\ rate
\neq
\Delta P
\neq
\text{physical stability constant}.
\]

The toroidal default \(r=0.7\) also exists independently. Equal decimals do not establish equal variables:

\[
\boxed{CV_{mean}=0.7\;\neq\;r=0.7}.
\]

### Operational use

After a physical model produces residual/state classifications:

\[
\text{physical model}
\to
\text{observables}
\to
\text{residuals}
\to
\text{predeclared peak/nonpeak classifier}
\to
\Delta P_{\rm op}.
\]

Then \(\Delta P_{\rm op}\) may test whether the *routing/classification behavior* is stable under:

- seeds;
- data resampling within covariance;
- event-chain perturbations;
- regime substitutions;
- observation-window changes;
- implementation/device changes.

It is never inserted into the equations of motion merely because its numerical value is near 0.18.

## 8. Ω persistence adapter

The RMRCTI Ω layer is used as a persistence/routing diagnostic.

For projection direction \(d\):

\[
\tau_{t,d}
=
\operatorname{distance}
\left(
P_d(S_t),P_d(S_{t-1})
\right).
\]

A persistent signal means:

\[
\texttt{PERSISTENCE}\to\texttt{EXPAND/PROBE},
\]

not:

\[
\texttt{PERSISTENCE}\to\texttt{PHYSICAL\_TRUTH}.
\]

This allows Ω to identify regions/event branches requiring finer geometry without pre-deciding the physical mechanism.

## 9. Dynamic geometry selection score

For each candidate geometry/regime \(\Gamma_j\), define an operational routing score:

\[
S_j
=
w_E E_j
+
w_V V_j
+
w_R R_j
-
w_C C_j
-
w_U U_j,
\]

where:

- \(E_j\): evidence compatibility;
- \(V_j\): validity-domain satisfaction;
- \(R_j\): residual improvement on held-out/predeclared tests;
- \(C_j\): computational/model complexity;
- \(U_j\): unresolved uncertainty/contradiction penalty.

Weights must be predeclared.

This score is triage only; it cannot promote a claim.

## 10. Stability surface rather than one stability number

The correct stability object is a surface:

\[
\mathcal S_{\rm stab}
=
\mathcal S_{\rm stab}
(
\mathrm{seed},
\mathrm{parameters},
\mathrm{event\ history},
\mathrm{geometry},
\mathrm{window},
\mathrm{dataset}
).
\]

For the RMRCTI component:

\[
\Delta P
=
\Delta P
(
\mathrm{seed},
R,r,\kappa,\alpha,\beta,\lambda,
\mathrm{corpus},
\mathrm{chunking}
).
\]

For the astrophysical component, stability is measured separately through residuals, posterior branch weights and sensitivity/Jacobian structure.

Therefore:

\[
\boxed{
\text{stable architecture}
=
\text{robust region/basin}
\neq
\text{one recurring decimal}
}.
\]

## 11. Required dynamic experiment

The first executable experiment should be synthetic and provenance-complete:

1. create a body \(Y\) with state/covariance;
2. emit/observe it with a retarded-time relation;
3. propagate in G1 weak-field N-body geometry;
4. apply a close encounter/slingshot event;
5. optionally branch into collision/fragmentation;
6. route a strong-field branch only when its gate is met;
7. generate observables at the observer;
8. reconstruct under competing scenario histories;
9. compare linearized vs nonlinear propagation;
10. compute \(J_k\), \(\Lambda\), residuals and posterior scenario weights;
11. only then route residual classifications to RMRCTI \(\Delta P_{\rm op}\) and Ω persistence;
12. repeat with seeded perturbations and null controls.

## 12. Required controls

- no-event baseline;
- wrong-event-order control;
- wrong-geometry control;
- line-of-sight superposition control;
- covariance resampling;
- parameter perturbation;
- hidden/held-out synthetic truth;
- seed replication;
- multiple-scenario correction;
- alternative integrator/implementation;
- negative runs preserved.

## 13. Relation to DESI / Pantheon+ / LCDM / RLL

DESI/Pantheon+/LCDM/RLL remain the cosmological-background geometry branch G5.

Their observables:

\[
D_H,D_M,D_A,D_L,F_{\rm AP},\mu
\]

may be inputs to the hybrid context.

They are not automatically mixed with local stellar/black-hole event-chain dynamics.

The current G4 evidence has RLL on the \(\Omega_{s0}=0\) null boundary in the tested background scope; this negative/null result remains intact.

## 14. Hard boundaries

\[
\Delta P\approx0.18
\neq
\text{physical stability constant}
\]

\[
\text{toroidal morphology}
\neq
\text{toroidal physical mechanism}
\]

\[
\text{observed position}
\neq
\text{present position}
\]

\[
\text{possible event history}
\neq
\text{inferred event history}
\]

\[
\text{geometry fit}
\neq
\text{causal explanation}
\]

\[
\text{RMRCTI routing stability}
\neq
\text{cosmological likelihood}
\]

## 15. R3

**F_ok:** the existing RMRCTI ΔP, Ω persistence, worldline/cascade router and scenario ensemble already provide most of the required skeleton; the dynamic structural geometry layer now types the missing geometry/regime selection explicitly.

**F_gap:** no executed end-to-end synthetic event-chain benchmark yet binds retarded observation, regime switching, event cascades, covariance, Ω persistence and ΔP routing in one receipt.

**F_next:** implement the synthetic body-Y benchmark with known hidden truth, execute null/adversarial branches, then test whether the router recovers the correct event history and geometry without using ΔP≈0.18 as a fitted physical parameter.
