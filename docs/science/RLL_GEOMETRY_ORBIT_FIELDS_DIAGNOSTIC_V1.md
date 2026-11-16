# RLL — Geometry / Radians / Log-scales / Covariance / Orbital & Field Gate V1

**Created:** 2026-11-15; **status:** `IMPLEMENTED_UNTESTED_REMOTE / HOSTED_REFERENCE_MATH_SCOPED`, `claim_allowed=false`.
**Source:** author's layered square/equilateral sketches, cross-figure vertex relations and the V3 mathematical crosswalk in private `rafaelmeloreisnovo/Matem-tica-`. RLL is a typed consumer, not a second mathematical authority.

## Existing producers and RLL authority
- Private math source, no merge: `rafaelmeloreisnovo/Matem-tica-/docs/formal/2026-11-15_TRIGONOMETRIA_RADIANOS_LOGLOG_COVARIANCIA_2D3D_V3.md`, commit `3f7178c8da09e0aaeaedb0e1f3f19332e31f2300`.
- RLL scientific gate: `docs/science/RLL_GEOMETRIC_OPERATOR_OMEGA_G_V1.md`, `data/contracts/rll_geometric_operator_omega_g.v1.yaml`, currently `direct_likelihood_binding=false`.
- RLL existing adapters retained: `data/pipelines/geomagnetism/trajectory_geometry.py`, `data/pipelines/strong_gravity/toroidal_sine_reference.py`, `data/pipelines/structure_d/models.py`, `core/lowlevel_runtime/c/rll_canonical_real_models.c`.
- Pre-existing consumers: `docs/science/RLL_ROTATION_ARC_ELLIPSE_RADIAL_LAYER_BRIDGE_V1.md`, `docs/science/ORBITAL_SHAPE_ANGULAR_MOMENTUM_MAP.md`, `docs/MODELO_COSMOLOGICO_UNIFICADO_MAGNETISMO_RADIACAO_PLASMA.md`.

## Implementation
- Pure Python stdlib: `scripts/validation/rll_geometry_orbit_fields_v1.py`, no network, filesystem writes, likelihood coupling or hidden global state.
- Tests: `tests/test_rll_geometry_orbit_fields_v1.py`, 17 deterministic unittest cases. Run from repo root: `python -m unittest discover -s tests -p test_rll_geometry_orbit_fields_v1.py -v`.
- Contract: `data/contracts/rll_geometry_orbit_fields.v1.json`. No existing workflow was modified.

Adapter implements:
1. 2D rotations, wrapped radians, circle chord/apothem, tangent-line normal separately from trig tan.
2. Orthographic 3D→2D point projection: a circle can project to an ellipse, which does NOT establish an orbit.
3. Dimensionless log similarity for lengths/areas/volumes, with iterated natural log x>1 gate; log-log plot != log(log(x)).
4. Population covariance of finite 2D vertex arrays, rotations and the mean of pairwise squared distances via centroid/covariances.
5. Newtonian two-body focus-centered elliptical state: r=p/(1+e cosν), p=a(1-e²), true anomaly ν in rad; inclination rotates the perifocal plane about x; returns velocity, specific energy and angular momentum. **Equally spaced true anomalies are not equally spaced in time for e>0**.
6. Newtonian point-mass gravitational acceleration g=-μr/r³ in m/s².
7. Static ideal vacuum dipole far field: B≈10^-7[3(m·n)n−m]/r³, magnetic moment A·m², distance metres, field tesla. Factor μ0/(4π) ≈10^-7 is an approximation, not an exactly fixed SI number after 2019. This is NOT a complete magnetosphere, relativistic plasma or magnetohydrodynamic solution.
8. Separate-field probe: common position but INDEPENDENT force-law diagnostics; `measurement_covariance=TOKEN_VAZIO`, `cosmological_likelihood_binding=BLOCKED`.

## Invariants and falsifiers
- e=0 circular orbit: r=a, specific energy E=-μ/(2a), specific h²=μa. For 0≤e<1, all true anomalies preserve two-body E and h within tolerance; fail on degree/radian confusion or center/focus mixup.
- Rotations preserve norms; covariance transforms as Σ'=RΣRᵀ.
- For empirical vertex sets A,B with uniform Cartesian pairs: mean||u−v||² = ||μA−μB||² + trΣA + trΣB. This vertex covariance is NOT observational DESI or Pantheon measurement uncertainty.
- Equal-circumradius square and equilateral have covariance (r²/2)I but are not the same shape: COVARIANCE_MATCH != SHAPE_IDENTITY.
- Central Newtonian g scales ∼r^-2; static dipole B scales ∼r^-3. Same geometrical distance variable does NOT mean the same field law. Gravity acts on all mass-energy; magnetic Lorentz response requires charge/current and regime-specific physics.
- ln(ln x) requires dimensionless x>1. For q<1,n>0, ln(ln(q^n)) is undefined in real numbers.
- Invalid input: NaN/inf, zero-distance singularities, μ≤0, e<0/e≥1, invalid inclination, invalid circle inputs and absent units; raise error, do not replace with 0 or success.

## Cosmological domain boundary — CRITICAL
Keplerian ellipses approximate particular *local bound two-body orbits*, not universal trajectories of all objects in cosmology. General cosmological spacetime, gravitational lensing, magnetized plasmas and background H(z) are separate inference domains. Modeling magnetic energy effects on spacetime requires stress-energy and dynamical source equations; neither sinusoidal similarity nor a dipole is a sufficient bridge.

NO MODIFICATIONS to `H(z)`, BAO, Pantheon, DESI covariance, RLL Q16 core, cosmological model selection, magnetic-plasma hypotheses or other pipelines. Existing H(z) baselines preserved. Observational covariance must not be replaced by spatial vertex covariance.

Science bridge from existing RLL:
`BIND(invariant_id, observable_id, mechanism, units, data_covariance, falsifier, provenance)`.
Pending an observable-specific physical mechanism, dataset-specific errors/covariance, independent reproduction and double-counting audit, scientific claim and likelihood binding remain BLOCKED.

## Public reference baselines
- NASA JPL orbital mechanics supplement (vis-viva/angular momentum):
  https://spsweb.fltops.jpl.nasa.gov/portaldataops/mpg/MPG_Docs/MPG%20Book/Release/Chapter7-OrbitalMechanics.pdf
- NASA, Orbit & Orbit Transfer Equations:
  https://ntrs.nasa.gov/api/citations/19920010006/downloads/19920010006.pdf
These classical baselines do not validate RLL hypothesis-level cosmology.

## Evidence, execution, rollback
- GitHub code and test source written into review branch; tests on that exact code/branch are NOT_RUN until an execution receipt is received. `IMPLEMENTED_UNTESTED != PASS`.
- Mathematical identities have been checked separately; a source write/readback demonstrates persistence only.
- Next: run 17 branch tests; compare selected samples to independently computed high-precision states, bind real JPL/planetary field measurement with covariance, run H(z) regression, then consider a separately scoped observables bridge.
- Rollback: main remains unchanged, review branch can be superseded or closed without deleting source history. No merge, publication, access/share change, automation scheduling or science claim authorized by this document.
