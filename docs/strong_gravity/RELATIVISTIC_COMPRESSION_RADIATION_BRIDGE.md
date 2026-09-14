# Relativistic compression, radiation and microphysics bridge

## Purpose

This bridge refines the session's compression/radiation hypothesis without collapsing distinct scales. It connects the existing spiral-plasma thermal model to:

- compressive work `Q_comp = -p Theta`;
- magnetic pressure `p_B = B^2/(2 mu0)`;
- radiation momentum flux `p_rad = C F/c`;
- photon thrust `F_gamma = C P/c`;
- radiative acceleration `a_rad = kappa F/c`;
- gravity benchmark `a_g = GM/r^2`;
- Eddington luminosity `L_Edd = 4 pi GMc/kappa`;
- non-relativistic electron degeneracy pressure;
- a configurable ledger of microscopic energy thresholds.

`C` is a coupling factor between 0 and 2: zero coupling, absorption-like transfer near one, and ideal reflection-like transfer near two.

## Compression is not automatic particle destruction

The phrase “particles do not touch” is only a classical teaching image. Microscopic collisions are scattering interactions mediated by fields and quantum amplitudes. Wavefunctions may overlap. For identical fermions, the Pauli rule concerns occupation of the same quantum state; it is not a simple prohibition against occupying the same geometric point.

Compression can increase density, collision rate, temperature, ionization and radiation. It does not automatically convert atoms into nuclei, nuclei into nucleons, or hadrons into quarks. Each transition requires sufficient energy, momentum, reaction channel and cross section.

The module therefore records reached *reference thresholds* but never equates a reached threshold with a process probability or completed transformation.

## Spin boundary

Electron spin contributes a magnetic moment and quantum statistics. Degeneracy pressure is included as a zero-temperature, non-relativistic reference:

```text
P_deg = hbar^2/(5 m_e) * (3 pi^2)^(2/3) * n_e^(5/3)
```

This does not solve spin hydrodynamics, quantum kinetics, polarization transport, Landau quantization or strong-field QED. A macroscopic field is not inferred from spin alone.

## Magnetic fields and gravity

Magnetic field lines are not material strings. They are a representation of the electromagnetic field. In a conducting plasma their evolution is coupled to flow through induction, advection, diffusion and reconnection.

The gravitational source in general relativity is the total stress-energy tensor. Matter, electromagnetic fields and radiation all contribute. The module only reports an equivalent mass-density proxy:

```text
rho_equiv = (u_B + u_rad)/c^2
```

This proxy is not a solution of Einstein's equations and is not a new force called “plasma gravity.” A physical backreaction claim requires a metric plus a covariant matter/field/radiation solution.

## Photon thrust and the Eddington benchmark

For isotropic luminosity:

```text
F_rad = L/(4 pi r^2)
a_rad = kappa F_rad/c
a_grav = GM/r^2
```

With the same opacity assumption:

```text
a_rad/a_grav = L/L_Edd
```

Radiation can therefore oppose inflow, drive winds or contribute to jets. Geometry, opacity, optical depth, anisotropy and relativistic transfer determine the actual result.

## Interaction ladder

The committed baseline uses three explicit references:

- 13.6 eV: hydrogen ionization reference;
- 1.022 MeV: electron-positron rest-energy pair reference;
- 100 MeV: hadronic-resolution reference scale.

They are not universal boundaries for all materials or reactions. Species-specific cross sections and distribution functions remain mandatory.

## Integration

```text
session_multiscale_avalanche.py
  -> ordered flow, damping partition and finite phase permutations

spiral_plasma_thermal_bridge.py
  -> AC conductivity, RF heating, Hall/Pedersen transport and Biermann source

relativistic_compression_radiation_bridge.py
  -> compression work, radiation pressure, photon thrust, degeneracy and thresholds
```

## Claim boundary

```text
GRMHD solution                     = false
quantum kinetic solution           = false
spin hydrodynamics solution        = false
Einstein backreaction solution     = false
nuclear reaction network           = false
laboratory validation              = false
astrophysical validation           = false
RLL cosmology validation           = false
claim_allowed                      = false
```
