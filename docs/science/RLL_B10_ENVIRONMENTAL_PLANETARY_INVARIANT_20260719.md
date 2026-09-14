# RLL B10 — Environmental and Planetary Context Invariant

**Date:** 2026-07-19  
**State:** `HYPOTHESIS / STRUCTURAL_READY`  
**New-physics claim:** `claim_allowed=false`  
**Scope:** planetary environments, plasma, magnetism, atmosphere, oceans, crust, chemistry, phase changes and propagation  

## 1. Purpose

This branch prevents local environmental processes from being silently promoted
into cosmological evidence. It also preserves them as legitimate, testable
routes when their carrier, scale, equations and observables are declared.

The central separation is:

```math
O_{\rm obs}
=
\mathcal T_{\rm instrument}
\circ
\mathcal T_{\rm environment}[X_p,\nu,t]
\circ
\mathcal T_{\rm cosmology}[H(z),z]
\left(O_{\rm source}\right)
+N.
```

A change in `T_environment` is not automatically a change in `H(z)`, and a
background-fit anomaly is not automatically a propagation effect.

## 2. Planetary state vector

A context is represented by:

```math
X_p=
(M,R,\Omega_{\rm rot},a_\star,F_\star,
\mathbf B,\mathbf E,\mathbf g,T,P,\rho,
\mathbf x_{\rm chem},x_e,\sigma,
\mathcal A,\mathcal O,\mathcal C,t),
```

where:

- `M`, `R`: mass and characteristic radius;
- `Omega_rot`: rotation rate;
- `a_star`, `F_star`: stellar distance and incident stellar flux;
- `B`, `E`, `g`: magnetic, electric and gravitational fields;
- `T`, `P`, `rho`: thermodynamic state;
- `x_chem`: chemical/isotopic composition;
- `x_e`: ionization fraction;
- `sigma`: electrical conductivity;
- `A`, `O`, `C`: atmospheric, oceanic and crustal states;
- `t`: time, season, cycle or evolutionary epoch.

No two environments are treated as physically equivalent merely because one
variable or geometry is similar.

## 3. Possibility-to-claim invariant

```math
\boxed{
\text{possibility}
\longrightarrow
\{\text{carrier, medium, scale, state, conservation, rate,
observable, uncertainty, baseline, falsifier}\}
\longrightarrow
\text{testable claim}
}
```

A proposed relation remains `TOKEN_VAZIO` or `HYPOTHESIS` until it declares:

1. carrier and medium;
2. spatial and temporal scale;
3. state variables and units;
4. initial and boundary conditions;
5. conservation laws;
6. constitutive, transport or reaction-rate equation;
7. data source and provenance;
8. instrument or simulation;
9. uncertainty/covariance;
10. standard null model;
11. falsifier;
12. reproduction artifact and checksum.

## 4. Electromagnetic and plasma layer

A local field decomposition may be written as:

```math
\mathbf B_{\rm obs}
=
\mathbf B_{\rm internal}
+
\mathbf B_{\rm crust}
+
\mathbf B_{\rm ionosphere}
+
\mathbf B_{\rm magnetosphere}
+
\mathbf B_{\rm induced}.
```

A plasma may be quasi-neutral while carrying intense current:

```math
\rho_q\approx0,
\qquad
\mathbf J=\sum_s n_sq_s\mathbf v_s\neq0.
```

A minimal generalized Ohm structure is:

```math
\mathbf E+\mathbf v\times\mathbf B
=
\eta\mathbf J
+
\frac{\mathbf J\times\mathbf B}{en_e}
-
\frac{\nabla p_e}{en_e}
+
\frac{m_e}{e}\frac{d\mathbf v_e}{dt}.
```

Oceanic or atmospheric motion through a magnetic field may contain a motional
term:

```math
\mathbf E_{\rm motional}=-\mathbf v\times\mathbf B.
```

These are standard environmental mechanisms. They are not, by themselves,
evidence for an additional cosmological RLL sector.

## 5. Earth-ionosphere cavity boundary

The Earth-ionosphere system may be treated as a lossy, driven electromagnetic
cavity. Solar-wind coupling may modify magnetospheric and ionospheric boundary
conditions, while lightning is the principal driver of Schumann modes.

The allowed relation language is:

```text
solar wind MODULATES ionospheric conductivity and boundary conditions
ionospheric state MODULATES cavity amplitude, phase and quality factor
local geology MODULATES local electromagnetic response
```

The blocked language is:

```text
solar wind directly becomes a Schumann mode
local ore deposit changes the global cavity without a measured transfer path
matching frequencies establish a causal bridge
```

## 6. Geology and mineral magnetism

Local observations may include:

```math
\mathbf B_{\rm local}
=
\mathbf B_{\rm regional}
+
\mathbf B_{\rm remanent}
+
\mathbf B_{\rm induced}
+
\mathbf B_{\rm current}.
```

Mineral abundance alone is insufficient. The mineral phase, oxidation state,
grain structure, temperature, remanence and measurement geometry must be
specified. `iron-rich` is not equivalent to `strongly magnetic`.

## 7. Chemistry, phases and reaction graph

The chemical/nuclear exploration is a constrained hypergraph:

```math
G_{\rm reaction}=(V_{\rm species},E_{\rm reactions}).
```

Each edge must pass conservation gates:

```math
\sum Z_{\rm in}=\sum Z_{\rm out},
\qquad
\sum A_{\rm in}=\sum A_{\rm out},
\qquad
\sum q_{\rm in}=\sum q_{\rm out},
```

and an energy/rate declaration:

```math
\Delta E=\Delta mc^2+Q,
\qquad
r_j=k_j(T,P,\ldots)\prod_i n_i^{\nu_{ij}}.
```

A species record should minimally contain:

```math
S_i=(Z,A,q,E_{\rm ion},\mu,\chi_m,\sigma_e,
\text{phase},\text{EOS},\text{spectral lines}).
```

Blind permutation of the periodic table is blocked. Conservation, stability,
energy thresholds and rates reduce the search space before simulation.

## 8. Critical-state separation

The term `critical` must be typed:

- thermodynamic critical point;
- nuclear critical mass;
- gravitational or structural instability threshold;
- ionization/dissociation threshold;
- magnetic or plasma instability threshold.

These categories cannot be substituted for each other.

## 9. Relation states

| Relation | State |
|---|---|
| Solar wind changes magnetospheric/ionospheric conditions | `VERIFIED_STANDARD` |
| Those boundary changes may modulate cavity measurements | `PHYSICALLY_PLAUSIBLE / TESTABLE` |
| Local mineralogy changes local magnetic response | `VERIFIED_STANDARD` |
| Local mineralogy changes the global Schumann eigenfrequency materially | `TOKEN_VAZIO` |
| Ocean/atmosphere motion induces electric fields in `B` | `VERIFIED_STANDARD` |
| Plasma current requires large net static charge | `CONTRADICTION` |
| Environment can alter photon propagation | `VERIFIED_STANDARD` |
| Environmental propagation residual is an RLL signal | `TOKEN_VAZIO / CLAIM_BLOCKED` |
| Planetary chemistry is fully captured by element permutations | `CONTRADICTION` |
| Reaction networks constrained by conservation and rates | `VERIFIED_STANDARD` |

## 10. Typed cross-scale relations

The only allowed bridge classes are:

```text
STANDARD_MECHANISM
MODULATES
COUPLES
CORRELATES_WITH
CONTEXTUALIZES
SCALE_BRIDGE_HYPOTHESIS
ANALOGY_ONLY
CONTRADICTS
FALSIFIES
REQUIRES
```

`CORRELATES_WITH` never implies `COUPLES`. `ANALOGY_ONLY` never implies physical
identity. `SCALE_BRIDGE_HYPOTHESIS` requires a coupling equation with units and
a discriminating observable.

## 11. RLL integration route

### B10-A — environmental transfer function

```math
\mathcal T_{\rm environment}
=
\mathcal T_{\rm plasma}
\circ
\mathcal T_{\rm magnetic}
\circ
\mathcal T_{\rm atmospheric}
\circ
\mathcal T_{\rm geologic/oceanic}.
```

### B10-B — standard-baseline residual

```math
R_{\rm env}
=
O_{\rm obs}
-
O_{\rm standard}(X_p,\nu,t).
```

### B10-C — preregistered alternative

```math
R_{\rm env}
=
R_{\rm known}
+
R_{\rm candidate}(\theta_{\rm RLL}),
```

with `theta_RLL` fixed or prior-registered before inspecting the target residual.

### B10-D — falsifier

The candidate fails if it:

- collapses into a known plasma, Faraday, conductivity or calibration term;
- has no stable units or scale dependence;
- cannot outperform the null under held-out data;
- changes sign or magnitude only after post-hoc parameter tuning;
- conflicts with independent environmental observations.

## 12. Repository projections

- `RLL`: equations, observables, null models, falsifiers and claim language;
- `Mapa`: repository membership, authority and typed edges;
- `PlamaticGravity-`: plasma/MHD/gravity-domain mechanisms and safety boundary;
- `Cosmos`: ontology, vocabulary and scale-aware contextualization;
- `papers`: long-form synthesis, provenance and manuscript preparation.

No repository may redefine another repository's evidence state.

## 13. Claim boundary

This branch can establish:

- a coherent state vector;
- relation types;
- scale and domain separation;
- conservation/rate gates;
- a route to environmental residual tests.

It cannot establish:

- a detected RLL propagation residual;
- a causal link from Schumann modes to cosmological expansion;
- gravity control by laboratory plasma;
- global geophysical changes caused by one mineral locality;
- complete chemistry through unrestricted permutations;
- independent replication.

```text
claim_allowed=false
TOKEN_VAZIO remains a valid state
negative and null results remain versioned
```
