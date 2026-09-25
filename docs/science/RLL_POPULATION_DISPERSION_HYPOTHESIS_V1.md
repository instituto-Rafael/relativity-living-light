# RLL — Population / Transport Dispersion Hypothesis V1

**Date:** 2026-09-24  
**Authority:** instituto-Rafael/relativity-living-light  
**State:** EXECUTABLE_HYPOTHESIS_FAIL_CLOSED  
**Scientific claim allowed:** false

## 1. Intent

Translate the session hypothesis into an auditable RLL layer:

- an observed field may contain objects from different origins and epochs;
- objects can arrive with different velocity distributions;
- capture, ejection, migration, slowing, scattering or long residence can place old and young objects in the same present-day region;
- intervening gas/plasma, projection and selection can alter the observed dispersion;
- hidden reservoirs in other sciences are useful as a methodological warning that visible inventory is not total inventory, but they are not evidence for a new cosmological component.

The implementation is additive. It does **not** modify the canonical RLL cosmological likelihood and it does **not** promote a new physical parameter.

## 2. Hypothesis state

For observation `y_i`, let `k` denote a latent population and `z_i` the latent state:

```text
p(y_i | Theta)
  = sum_k pi_k * integral p(y_i | z_i, k, Theta) p(z_i | k, Theta) dz_i
```

The latent state can include:

```text
origin
age
initial/current velocity
angular momentum or orbit class
transport history
residence time
capture/ejection state
environment/medium
projection state
selection state
```

A minimal transport scaffold is:

```text
dx/dt = v

dv/dt = -grad(Phi) + a_medium + a_RLL + xi(t)
```

and a residence/capture survival term can be written:

```text
P_surv(t) = exp[- integral lambda_capture_or_loss(t) dt]
```

The observation covariance is decomposed conceptually as:

```text
Sigma_obs
  = Sigma_measurement
  + Sigma_intrinsic
  + Sigma_origin
  + Sigma_transport
  + Sigma_medium
  + Sigma_projection
  + cross_covariances
```

The sum is **not** an independence assumption. Cross-covariances remain required unless a dataset contract explicitly justifies a diagonal approximation.

## 3. Why this is useful now

### DESI DR2

The 2026 DESI DR2 Ly-alpha full-shape Alcock-Paczynski analysis reports approximately 1% AP precision at `z_eff=2.33`, and its central value shifts part of the extended-dark-energy inference toward LambdaCDM relative to BAO-only information. The lesson for RLL is not “add arbitrary parameters”; it is “new information can expose model dependence and nuisance structure, so parameter families must be predeclared and compared against a simpler baseline.”

Source: DESI Collaboration, *DESI DR2 Results IV: Alcock-Paczynski Measurements from the Lyman Alpha Forest and Cosmological Constraints*, arXiv:2607.27410.

The 2025 DESI extended-dark-energy analysis used parametric and non-parametric reconstructions and reported that a two-parameter `w(z)` extension was sufficient to capture the principal trend in the then-current data. This is an explicit complexity warning for RLL.

Source: DESI Collaboration / Lodha et al., *Extended Dark Energy analysis using DESI DR2 BAO measurements*, arXiv:2503.14743.

### Galactic populations

Observed stellar velocity dispersion is not a one-variable phenomenon. Published Milky Way work finds joint dependence on age, angular momentum, metallicity and height above the Galactic plane. This supports using age/origin/velocity as latent population variables when the target domain is Galactic kinematics.

Source: *Fundamental relations for the velocity dispersion of stars in the Milky Way*, MNRAS 506, 1761 (2021).

### Planetary populations

A 2025 Nature Astronomy study of more than 1,000 short-period planets reports age dependence in the occurrence and architecture of ultra-short-period systems. That makes age and evolutionary pathway legitimate population variables in the planetary domain.

Source: Tu et al., *Age dependence of the occurrence and architecture of ultra-short-period planet systems*, DOI:10.1038/s41550-025-02539-1.

### Intervening space is not observationally empty

The 2026 DESI Ly-alpha analysis itself uses absorption by neutral hydrogen distributed through the intergalactic medium. In strong-gravity observations, plasma, magnetic fields, scattering and imaging systematics also affect measured morphology.

This must be stated carefully:

```text
intergalactic/interstellar medium != quantum-vacuum microstructure
observed plasma != new cosmological component
```

## 4. Strong-gravity / black-hole specialization

For the first projection image from the session, the correct RLL route is:

```text
G3 strong gravity
  -> G4 plasma / GRMHD
  -> G6 observation projection
```

The observed projective scale is modeled schematically as:

```text
b_obs
  = F_GR(M, a*, i, D, emission_model)
  + Delta_b_medium
  + Delta_b_projection
  + Delta_b_systematics
  + Delta_b_RLL
```

where the baseline nuisance/physical terms include:

- black-hole mass `M`;
- dimensionless spin `a*`;
- observer inclination `i`;
- distance `D`;
- accretion/emission geometry;
- electron-density profile;
- magnetic-field profile;
- scattering/imaging systematics;
- observation epoch.

The RLL-specific residual `Delta_b_RLL` remains `TOKEN_VAZIO` until the standard GR + plasma + projection model is exhausted on held-out data.

This is especially important because 2025 M87* work reports ring ellipticity that must be interpreted through astrophysical and imaging effects rather than as a direct one-parameter spin measurement.

## 5. Hidden reservoirs: what the Earth evidence does and does not say

### Deep mantle

Hydrous ringwoodite found in a diamond is direct evidence that at least local mantle-transition-zone material can contain substantial structurally bound water. Newer geophysical work also investigates water reservoirs below the transition zone.

This does **not** mean that a globally measured liquid ocean has been found inside Earth, and estimates of total deep-Earth water remain model- and region-dependent.

### Beneath the seafloor

Offshore freshened groundwater is directly observed in some continental-shelf aquifers. A 2023 Nature Communications study in the Pearl River estuary/shelf combined borehole porewater, geochemistry, seismic reflection and hydrogeological modeling and estimated a large freshened groundwater body extending offshore.

That is a real hidden reservoir, but:

```text
offshore groundwater != mantle water
mantle water != cosmological hidden component
Earth analogy != RLL evidence
```

Its value here is methodological: **present visible inventory can be incomplete, and origin/age/transport history matter.**

## 6. Parameter admission gate

A parameter enters a quantitative RLL experiment only if all are declared before the fit:

```text
ID
domain
unit/dimension
state
source/model authority
prior
falsifier
covariance/selection relationship
```

Then it must survive:

1. standard baseline first;
2. full covariance or justified approximation;
3. selection-function treatment;
4. information-criterion / Bayesian-evidence / held-out comparison;
5. posterior-predictive residual checks;
6. independent reproduction.

A parameter that merely makes the fit numerically better is not enough.

## 7. Implementation

Added in this change:

```text
rx/population_dispersion.py
data/governance/RLL_POPULATION_DISPERSION_HYPOTHESIS_V1.json
tests/test_population_dispersion.py
docs/science/RLL_POPULATION_DISPERSION_HYPOTHESIS_V1.md
```

The router is stdlib-only and fail-closed. Existing RLL execution plans are unchanged.

Example conceptual route:

```python
from rx.population_dispersion import route_population_dispersion

result = route_population_dispersion({
    "enabled": True,
    "covariance_mode": "full",
    "origin_mixture": True,
    "age_mixture": True,
    "velocity_mixture": True,
    "populations": [{"id": "old_slow"}, {"id": "young_fast"}],
    "parameters": []
})
```

No output from this layer can set `claim_allowed=true`.

## 8. Falsifiers

The hypothesis loses value if:

- a one-population model explains the data after correct covariance/selection treatment;
- mixture weights collapse to zero;
- age/origin/velocity effects disappear after measurement-error correction;
- improvements disappear on held-out data;
- strong-gravity residuals disappear after plasma/scattering/imaging terms;
- an RLL parameter is redundant with an existing nuisance parameter;
- complexity penalties remove the preference.

## R3

`F_ok`: latent population + transport + residence + medium + projection model is typed and executable without changing canonical physics.  
`F_gap`: real dataset priors/covariances, synthetic hidden-truth benchmark, independent reproduction, nonzero RLL deformation.  
`F_next`: run a deterministic two-population hidden-truth benchmark; then bind one real domain before any cosmological promotion.
