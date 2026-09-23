# RLL Retarded Spacetime / Source-State Contract V1

Status: FORMAL_MODEL_SHADOW  
Date: 2026-09-22  
Claim gate: blocked

## Purpose

This contract extends the existing Source State Lookback track without replacing it.

The observational unit is no longer treated as a present-time 3D point. It is modeled as:

1. an emission event at a cosmological epoch;
2. a signal path through an evolving spacetime/foreground;
3. an observer/instrument event;
4. a separate inferred matter worldline after emission.

The central separation is:

```text
OBSERVATION_EVENT != PRESENT_SOURCE_STATE
NULL_SIGNAL_PATH != TIMELIKE_MATTER_WORLDLINE
```

## Geometry of "age"

A position has no intrinsic age. The contract stores distinct time quantities:

- cosmological age at emission;
- lookback time;
- scale factor at emission;
- coordinate time when a declared metric uses one;
- source proper time / source-age estimate;
- formation-age proxy only when independently defined.

This prevents "age of a place" from silently mixing cosmological epoch, source age, and proper time.

## Dynamic path

A photon can traverse foreground regions that themselves evolve while the photon crosses them. Each segment therefore has entry/exit state and may carry, when physically defined:

- gravitational potential / metric model;
- peculiar or medium velocity;
- lensing convergence/shear and geometric delay;
- Shapiro delay;
- electron density, temperature and ionization;
- magnetic-field component;
- dispersion/rotation/scattering measures;
- optical depth and plasma group delay.

The contract explicitly forbids replacing this whole path by one timeless scalar unless that approximation is tested.

## Vacuum, plasma and gravity

For vacuum geometric optics:

[
g_{\mu\nu} k^\mu k^\nu = 0.
]

For matter:

[
g_{\mu\nu} u^\mu u^\nu = -c^2.
]

For plasma propagation, the contract uses a general dispersion relation container rather than pretending that every ray remains a vacuum null ray.

"Plasma gravity" is not introduced as a new force. Plasma/fluid and electromagnetic fields can contribute to stress-energy, while plasma also changes photon propagation. Any strong-gravity plasma claim is routed to the existing GRMHD/GRPIC authority.

## Time and redshift

The contract keeps:

[
t_L(z)=\int_0^z \frac{dz'}{(1+z')H(z')}
]

and

[
1+z=\frac{(k_\mu u^\mu)_e}{(k_\mu u^\mu)_o}
]

as reference relations within their declared assumptions.

The Schwarzschild clock expression is retained only as a static-observer special case; it is not generalized to arbitrary infall or arbitrary metrics.

## Uncertainty

The existing uncertainty ledger remains authoritative. New contextual axes are added without replacing it:

- source-state uncertainty;
- light-cone epoch;
- peculiar velocity;
- dynamic foreground;
- lensing path;
- plasma propagation;
- time-reference uncertainty.

Cross terms are not assumed to vanish.

## Relational geometry

The octagon/graph, Poincare, sphere, torus and related constructions may represent state relations or kernels. They are not promoted to the physical metric or topology of the Universe.

A permitted relation layer is:

[
d_{ij}^2=(c_i-c_j)^T\Sigma_c^{-1}(c_i-c_j),
quad
w_{ij}=e^{-d_{ij}^2/(2\ell^2)}.
]

## Primary falsifier

After declared source, propagation, foreground, selection and instrument terms are modeled, test whether whitened residuals remain context-dependent:

[
P(r\mid c) \stackrel{H_0}{\approx} P(r).
]

Residual structure must be separated into instrumental, selection, source evolution, foreground/plasma, gravitational/lensing and cosmological-model causes before any new-physics claim.

## State

```text
schema validation                 IMPLEMENTED
synthetic light-cone recovery      TOKEN_VAZIO
dynamic foreground recovery        TOKEN_VAZIO
lensing time-delay recovery        TOKEN_VAZIO
plasma propagation recovery        TOKEN_VAZIO
real-data context ablation         TOKEN_VAZIO
cross-survey reproduction          TOKEN_VAZIO
claim_allowed                      false
```

The next executable step is synthetic recovery before any real-data promotion.
