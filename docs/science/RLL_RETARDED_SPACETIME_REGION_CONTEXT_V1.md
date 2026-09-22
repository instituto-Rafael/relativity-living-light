# RLL Retarded Spacetime Region Context V1

## Status

`HYPOTHESIS_PROTOCOL` — structural formalization only. `claim_allowed=false`.

## Core distinction

A cosmological catalogue is treated as a set of events on the observer's past light cone, not as a simultaneous 3-D snapshot of present-day matter.

For the signal:

[
g_{mu
u}k^mu k^
u=0.
]

For massive matter:

[
g_{mu
u}u^mu u^
u=-c^2.
]

Therefore the emitted state, propagated signal and inferred later/current matter state are separate objects.

## Geometry of epoch rather than "age of a position"

A spatial coordinate is not assigned an absolute age. Each region crossed by the signal receives event-level temporal coordinates such as cosmic time at crossing, lookback time at crossing, scale factor, redshift, local proper time where defined, formation age of a physical structure when evidenced, and a dynamical timescale.

The region must be evaluated at the photon-crossing event. A later change in that region cannot retroactively change a photon that already passed it; it can affect later photons and later observations.

## Intervening-region stack

The line of sight is an ordered sequence of regions. Each segment can carry, when evidenced:

- peculiar/bulk velocity fields;
- expansion-rate context;
- gravitational potential/metric model;
- gravitational redshift;
- lensing convergence/shear;
- Shapiro and lensing time delays;
- matter density / halo membership / neighboring masses;
- electron density, dispersion measure, Faraday rotation, scattering and opacity;
- plasma bulk velocity and a reference to plasma stress-energy.

`TOKEN_VAZIO` is valid for unavailable quantities.

## Plasma boundary

There is no independent "plasma gravity" force in this contract. Plasma contributes mass-energy, pressure and electromagnetic stress to the total stress-energy tensor when those terms are physically modeled, while charged particles also follow electromagnetic and gravitational dynamics. Frequency-dependent plasma propagation is modeled separately from gravitational propagation.

## Time and gravity

The contract preserves proper time as distinct from observer coordinate time. The Schwarzschild expression

[
rac{d	au}{dt}=sqrt{1-r_s/r}
]

is retained only as a special static, exterior example; it is not substituted for a general cosmological metric.

## Statistical binding

Global cosmological parameters remain governed and may not be selected post hoc per datum. Contextual effects enter through predeclared nuisance/hierarchical variables, e.g.

[
eta_i=B(c_i)eta+u_{g(i)}.
]

The preferred uncertainty representation is a full covariance structure including source-state, light-cone propagation, peculiar velocity, lensing, plasma terms, calibration and model selection where applicable.

## Falsification surface

The strongest null is that, after declared systematics and covariance are modeled, whitened residuals do not retain unexplained dependence on context:

[
P(rmid c)=P(r).
]

The protocol also requires cross-survey holdouts, multi-image time-delay consistency, causal time-ordering, parameter penalties, plasma ablations and GR-baseline ablations before any new-physics claim.

## Boundary

Geometry is allowed as a state-space, graph, covariance/posterior geometry, or physically bound geodesic/lensing representation. Visual similarity to octagons, spirals, tori, Poincaré diagrams or other project geometries is not by itself evidence of spacetime topology or a new force.
