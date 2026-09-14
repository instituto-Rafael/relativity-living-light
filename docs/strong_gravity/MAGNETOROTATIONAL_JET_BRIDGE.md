# Magnetorotational deflection, MAD and relativistic-jet bridge

## Authority and scope

Authority: `instituto-Rafael/relativity-living-light`

This bounded bridge records the strongest coherent chain extracted from the
complete session and its preceding interactions:

```text
rotating dipole parable
-> angular inertia, precession and phase lag
-> electroaerodynamic deflection invariant
-> electromagnetic force density in plasma
-> magnetic pressure and flux accumulation
-> magnetically arrested accretion candidate
-> Poynting transport and Kerr rotation
-> relativistic-jet candidate
-> source-specific observables
```

It does **not** modify the RLL background cosmology, its likelihoods or the
published constraints on `Omega_s0`.

## Epistemic separation

| Mark | Meaning |
|---|---|
| `[E]` | established equation or exact scaling used as a diagnostic |
| `[C]` | explicit bridge convention |
| `[H]` | testable hypothesis requiring source-specific modelling |
| `[P]` | parable preserving intuition without physical promotion |

The “cosmic N55” is `[P]`: a compact image for a coherent rotating magnetic
domain. The physically transported quantities are magnetic flux, current,
helicity, vorticity and angular momentum, not a literal NdFeB block surviving
near a horizon.

## 1. Rotating dipole and angular memory

For a dipole in an external field:

\[
\boldsymbol{\tau}=\boldsymbol{\mu}\times\mathbf B,
\qquad
\frac{d\mathbf L}{dt}=\boldsymbol{\tau}.
\]

A rapidly rotating body does not need to align instantaneously. Torque may
produce precession, phase lag or a synchronized dynamical state.

The bridge defines:

\[
\mathcal G_{\rm rot}
=
\frac{|\mu B|}{I\,\omega_s\,\Omega_F}.
\]

```text
G_rot < 0.1        -> angular_inertia_dominated
0.1 <= G_rot <= 10 -> phase_lock_transition
G_rot > 10         -> field_torque_dominated
```

The thresholds are `[C]`, not universal phase transitions.

### Similar-body scaling

For geometrically similar bodies with fixed material properties:

\[
\mu\propto V,
\qquad
I\propto V^{5/3},
\qquad
\mathcal G_{\rm rot}\propto V^{-2/3}.
\]

Thus a tenfold volume increase gives:

\[
I_{10}/I_1=10^{5/3},
\qquad
\mathcal G_{10}/\mathcal G_1=10^{-2/3}.
\]

This preserves the session insight: a larger coherent rotating domain can carry
greater angular memory even though magnetic acceleration per unit mass does not
automatically increase.

## 2. Lifter/ionocraft to plasma

The electroaerodynamic limit is:

\[
\mathbf f_{\rm EAD}=\rho_q\mathbf E.
\]

In a magnetized plasma:

\[
\boxed{
\mathbf f_{\rm EM}
=
\rho_q\mathbf E+\mathbf J\times\mathbf B
}
\]

The common invariant is:

```text
field asymmetry
-> charge drift or separation
-> momentum transfer
-> directed material flow
```

The media are not equivalent. An ionocraft transfers momentum to a partially
neutral gas; a black-hole environment requires relativistic plasma dynamics,
current sheets, reconnection, pair creation and curved spacetime.

## 3. Poynting transport

\[
\mathbf S=\frac{\mathbf E\times\mathbf B}{\mu_0}.
\]

A nonzero Poynting flux does not prove a relativistic particle jet. Conversion
depends on mass loading, topology, reconnection, optical depth, radiative loss
and causal critical surfaces.

## 4. Magnetic arrest candidate

\[
p_B=\frac{B^2}{2\mu_0},
\qquad
p_{\rm ram}=\rho v_r^2.
\]

The bridge defines:

\[
\boxed{
\mathcal A_B
=
\frac{p_B}{p_{\rm ram}+p_{\rm th}}
}
\]

```text
A_B < 0.1       -> magnetically_subdominant
0.1 <= A_B < 1 -> magnetic_transition
A_B >= 1       -> mad_candidate
```

`mad_candidate` means only that the scalar magnetic-pressure proxy is comparable
to the chosen material-pressure proxy. It is not GRMHD confirmation of a MAD.

The MAD literature establishes that accumulated poloidal flux can disrupt
near-axisymmetric accretion and produce streams, magnetic islands, eruptions
and powerful outflows. It does not permit unbounded field growth.

## 5. Kerr rotation and light cylinder

For dimensionless Kerr spin `a_*`:

\[
\Omega_H
=
\frac{a_*c^3}
{2GM\left(1+\sqrt{1-a_*^2}\right)}.
\]

For field-line angular frequency `Omega_F`:

\[
r_{\rm LC}=\frac{c}{\Omega_F}.
\]

The light cylinder is a causal rotation scale: rigid corotation beyond it would
require superluminal tangential motion. The actual system reorganizes through
currents, waves and outflow.

## 6. Relativistic magnetization

\[
\boxed{
\sigma
=
\frac{B^2}{\mu_0\rho h c^2}
}
\]

```text
sigma < 0.1       -> matter_energy_dominated
0.1 <= sigma < 1 -> mixed_conversion
sigma >= 1       -> poynting_dominated_candidate
```

The relativistic opportunity grows when electromagnetic energy density rises
relative to mass loading:

\[
B^2/(\rho h)\uparrow.
\]

`sigma >= 1` does not fix the terminal Lorentz factor and does not prove an
observed jet.

## 7. Blandford-Znajek scaling proxy

\[
P_{\rm BZ,proxy}
=
\kappa\frac{\Phi_B^2\Omega_H^2}{\mu_0c}.
\]

It preserves the established dependence:

\[
P_{\rm jet}\propto\Phi_B^2\Omega_H^2.
\]

The coefficient `kappa` is model-dependent. This proxy does not replace a
horizon-integrated electromagnetic stress-energy flux.

## 8. Matter-state ladder

```text
ferromagnetic domains
-> mechanical fracture
-> heating and loss of coercivity
-> melting/vaporization
-> ionized plasma
-> current-supported magnetic organization
```

The solid can lose crystalline magnetic order while the system retains
organization through flux, current, helicity, vorticity and angular momentum.
This is the defensible meaning of “the magnet explodes but magnetic memory
continues”.

## 9. Existing RLL strong-gravity stack

```text
session_multiscale_avalanche.py
  -> ordered flow, damping and finite phase permutations

spiral_plasma_thermal_bridge.py
  -> AC conductivity, RF heating, Hall/Pedersen transport and Biermann source

relativistic_compression_radiation_bridge.py
  -> compression work, radiation pressure, thresholds and Eddington benchmark

magnetorotational_jet_bridge.py
  -> rotating-domain response, EAD/plasma force density, Poynting transport,
     MAD/sigma diagnostics, Kerr rotation, light cylinder and BZ scaling
```

## 10. Modern observational routes

### Horizon-scale polarimetry

- linear and circular polarization;
- electric-vector position-angle pattern;
- Faraday rotation;
- time-varying polarized structure;
- forward-modelled GRMHD images.

### Jet energetics and geometry

- jet power;
- opening angle and collimation;
- proper-motion Lorentz factor;
- core shift and spectral energy distribution;
- disk-jet time lag.

### High-energy timing

- X-ray/gamma flares;
- quasi-periodic oscillations;
- reconnection and pair-loading signatures;
- spectral-state transitions.

### Disk self-gravity and gravitational radiation

This is a separate route requiring disk mass, non-axisymmetric modes and a
relativistic source model. Microscopic particle motion is not promoted to a
detectable gravitational-wave claim.

## 11. Cosmological boundary

Local strong-gravity plasma physics is not automatically a correction to:

\[
H(z),\quad D_A(z),\quad D_L(z),\quad f\sigma_8,\quad C_\ell.
\]

To enter an RLL cosmological likelihood, the bridge would need an explicit:

1. population-integrated source term;
2. covariant effective stress-energy contribution;
3. propagation transfer function;
4. cosmological-observable bias model;
5. likelihood and covariance;
6. falsifier against standard astrophysical populations.

Until then:

```text
strong-gravity bridge -> source physics / context
strong-gravity bridge != cosmological background evidence
```

## 12. Primary scientific anchors

- Blandford & Znajek (1977), `doi:10.1093/mnras/179.3.433`.
- Narayan, Igumenshchev & Abramowicz (2003),
  `doi:10.1093/pasj/55.6.L69`.
- Tchekhovskoy, Narayan & McKinney (2011),
  `doi:10.1111/j.1745-3933.2011.01147.x`.
- Event Horizon Telescope Collaboration, M87 VII (2021),
  `doi:10.3847/2041-8213/abe71d`.
- Event Horizon Telescope Collaboration, M87 VIII (2021),
  `doi:10.3847/2041-8213/abe4de`.

## Claim boundary

```text
rotating-dipole dynamics diagnostic = implemented
similar-body scaling                = implemented
EAD/plasma force-density bridge     = implemented
Poynting diagnostic                 = implemented
MAD scalar candidate diagnostic     = implemented
Kerr/light-cylinder diagnostic      = implemented
BZ dimensional scaling proxy        = implemented

GRMHD solution                      = false
force-free global solution          = false
PIC/kinetic solution                = false
radiative-transfer solution         = false
source-specific observational fit   = false
RLL cosmological likelihood link    = false
new force                           = false
claim_allowed                       = false
```
