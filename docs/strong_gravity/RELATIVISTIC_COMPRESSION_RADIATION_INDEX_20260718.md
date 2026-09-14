# Relativistic compression and radiation integration index — 2026-07-18

## Authority

`instituto-Rafael/relativity-living-light`

## Integrated artifacts

### Compression/radiation bridge

```text
data/pipelines/strong_gravity/relativistic_compression_radiation_bridge.py
data/contracts/relativistic_compression_radiation_bridge.v1.json
data/results/strong_gravity/relativistic_compression_radiation_baseline.json
data/results/strong_gravity/relativistic_compression_radiation_validation_receipt.json
tests/strong_gravity/test_relativistic_compression_radiation_bridge.py
docs/strong_gravity/RELATIVISTIC_COMPRESSION_RADIATION_BRIDGE.md
```

### Magnetorotational/MAD/jet extension — 2026-07-20

```text
data/pipelines/strong_gravity/magnetorotational_jet_bridge.py
data/contracts/magnetorotational_jet_bridge.v1.json
data/results/strong_gravity/magnetorotational_jet_bridge_baseline.json
data/results/strong_gravity/magnetorotational_jet_bridge_validation_receipt.json
tests/strong_gravity/test_magnetorotational_jet_bridge.py
docs/strong_gravity/MAGNETOROTATIONAL_JET_BRIDGE.md
docs/strong_gravity/SESSION_MAGNETIC_GRAVITY_COSMOLOGY_SYNTHESIS_20260720.md
```

### Toroidal/sine-reference research adapter — 2026-07-20

```text
data/pipelines/strong_gravity/toroidal_sine_reference.py
data/contracts/toroidal_research_cycle_adapter.v1.json
data/results/strong_gravity/toroidal_sine_reference_baseline.json
data/results/strong_gravity/toroidal_sine_reference_validation_receipt.json
tests/strong_gravity/test_toroidal_sine_reference.py
docs/strong_gravity/TOROIDAL_SINE_REFERENCE_ADAPTER.md
```

### Shared formula inventory

```text
data/formulas/FORMULAS_ARTIFACTS_MANIFEST.json
```

## Physics separation

```text
compression work              = -p Theta
magnetic pressure             = B^2/(2 mu0)
radiation pressure            = coupling * flux/c
photon thrust                 = coupling * power/c
radiative acceleration        = opacity * flux/c
gravity acceleration          = GM/r^2
Eddington benchmark           = 4 pi GMc/opacity
electron degeneracy pressure  = non-relativistic reference only

rotating-dipole response      = |mu B|/(I omega_s Omega_F)
electromagnetic force density = rho_q E + J x B
Poynting flux                 = E x B / mu0
MAD-candidate scalar          = p_B/(rho v_r^2 + p_th)
relativistic magnetization    = B^2/(mu0 rho h c^2)
Kerr horizon rotation         = a_* c^3/[2GM(1+sqrt(1-a_*^2))]
light-cylinder radius         = c/Omega_F
BZ dimensional proxy          = kappa Phi_B^2 Omega_H^2/(mu0 c)

toroidal coordinates          = ((R+r cos theta) cos phi,
                                 (R+r cos theta) sin phi,
                                  r sin theta)
sine reference                = A sin(2 pi f t + phi0)
wrapped phase residual        = atan2(sin Delta_phi, cos Delta_phi)
phase-lock score convention   = (1 + cos Delta_phi)/2
normalized tracking error     = RMS(s_obs-s_ref)/A
geometric path metric         = sum((||x_i-x_(i-1)||/R)^2)
```

## Semantic corrections

- microscopic collision means scattering/interaction, not literal hard-sphere contact;
- Pauli exclusion concerns quantum-state occupation, not a universal geometric no-overlap statement;
- compression does not automatically create subparticles;
- a reached energy reference does not prove a reaction occurred;
- electron spin does not automatically create a macroscopic magnetic field;
- field lines are representations of the electromagnetic field, not material strings;
- electromagnetic and radiation energy contribute to stress-energy, but a scalar proxy is not an Einstein-equation solution;
- photon momentum can oppose inflow or help drive an outflow;
- the N55 object is preserved as a rotating-dipole parable, not literal near-horizon material;
- increasing a similar permanent magnet's size does not automatically increase its surface field;
- a larger similar rotating domain increases inertia faster than magnetic moment;
- an electroaerodynamic lifter and a black-hole jet share a force-density pattern but not the same medium or complete dynamics;
- `A_B >= 1` is a MAD candidate diagnostic, not proof of a magnetically arrested disk;
- `sigma >= 1` is a Poynting-dominated candidate, not proof of a measured relativistic jet;
- toroidal coordinates are a geometry, not proof that the investigated source is a physical torus;
- a pure sine is a reference waveform, not a universal stabilizer;
- a dimensionless path metric is not thermodynamic energy, jet power or stress-energy;
- a tokamak stabilization result cannot be transferred directly to black-hole accretion;
- local source physics does not modify the RLL cosmological background without an explicit covariant, population or propagation bridge.

## Integration order

```text
session_multiscale_avalanche.py
  -> ordered flow, damping partition and finite phase permutations

spiral_plasma_thermal_bridge.py
  -> AC conductivity, RF heating, Hall/Pedersen transport and Biermann source

relativistic_compression_radiation_bridge.py
  -> compression work, radiation pressure, photon thrust, degeneracy and thresholds

magnetorotational_jet_bridge.py
  -> angular memory, EAD/plasma force density, Poynting transport,
     MAD/sigma diagnostics, Kerr rotation, light cylinder and BZ scaling

toroidal_sine_reference.py
  -> double-period geometry, bounded sine reference, phase error,
     closure residual and dimensionless path diagnostics
```

## Validation boundary

```text
compression/radiation focused tests = 15 PASS (recorded pre-commit execution)
magnetorotational focused tests      = 21 PASS (recorded local execution)
toroidal/sine focused tests          = 15 PASS (recorded local execution)

GRMHD solution                       = false
force-free global solution           = false
quantum/PIC kinetic solution         = false
spin hydrodynamics solution          = false
radiative-transfer solution          = false
Einstein backreaction                = false
nuclear network                      = false
laboratory validation                = false
astrophysical source fit             = false
universal sine stabilization         = false
RLL cosmology validation             = false
claim_allowed                        = false
```

No new workflow YAML was introduced.
