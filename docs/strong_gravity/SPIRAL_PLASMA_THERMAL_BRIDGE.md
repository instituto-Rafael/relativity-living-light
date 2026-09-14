# Spiral–Plasma–Thermal Bridge

## Scope

This document connects four previously separate RLL study blocks:

1. coherent oscillation and spectral analysis;
2. prescribed spiral/toroidal geometry;
3. plasma conductivity, heating and magnetic transport;
4. carbon phase boundaries and compact-remnant interpretation.

It is a **bounded model and test contract**. It does not validate RLL cosmology, a black-hole mechanism, a diamond planet, or a physical role for 144/288 kHz.

```yaml
model_status: implemented_bounded_bridge
144_288_khz_status: external_drive_hypothesis
laboratory_validation: false
astrophysical_validation: false
exoplanet_composition_validation: false
RLL_cosmology_validation: false
claim_allowed: false
```

## 1. Frequency layers

The laboratory light–matter result discussed in the research notes contains vibrational energies near 3.2 and 5.1 meV. Using

\[
f=E/h,
\]

they correspond to approximately

\[
f_{3.2}\approx 0.7737566\,\mathrm{THz},\qquad
f_{5.1}\approx 1.2331745\,\mathrm{THz}.
\]

The canonical low-frequency pair is instead

\[
f_1=144\,\mathrm{kHz},\qquad f_2=288\,\mathrm{kHz}=2f_1.
\]

The low-frequency pair is therefore represented only as an external AC drive:

\[
E(t)=E_1\cos(2\pi f_1t+\phi_1)
+E_2\cos(2\pi f_2t+\phi_2).
\]

It is not treated as a one-photon atomic, molecular or phonon transition. A measurable role would require voltage/current phase, absorbed power, harmonics, sidebands, thermal response and controls.

## 2. Spiral geometry

The existing geometric ratio is preserved as

\[
h=\frac{\sqrt3}{2},\qquad
r_n=r_0h^n,
\]

with a 60-degree sector per step. Its continuous interpolation is

\[
r(\varphi)=r_0\exp\left[
\frac{\ln(\sqrt3/2)}{\pi/3}\varphi
\right].
\]

This is a prescribed geometric path. It is not, by itself, a geodesic, an MHD trajectory or a derived accretion orbit.

## 3. AC conductivity and heating

For a collision-damped electron fluid, the dissipative part of a Drude-like conductivity is

\[
\operatorname{Re}\sigma(\omega)=
\frac{n_ee^2\nu_m}{m_e(\nu_m^2+\omega^2)}.
\]

The RF heating density is

\[
Q_{\mathrm{RF}}(\omega)=
\frac12\operatorname{Re}\sigma(\omega)|E_\omega|^2.
\]

The implementation evaluates separate contributions at 144 and 288 kHz. It does not assume that the second harmonic is generated; generation must be demonstrated from a nonlinear response and phase relation.

## 4. Magnetized transport

A scalar resistance is insufficient when the plasma is magnetized. The bridge reports

\[
\mathbf J=
\sigma_\parallel\mathbf E_\parallel
+\sigma_P\mathbf E_\perp
+\sigma_H(\mathbf E_\perp\times\hat{\mathbf b}),
\]

using

\[
\beta_e=\frac{\omega_{ce}}{\nu_m},\qquad
\omega_{ce}=\frac{eB}{m_e}.
\]

The classical components are represented as

\[
\sigma_P=\frac{\sigma_\parallel}{1+\beta_e^2},
\qquad
\sigma_H=\frac{\sigma_\parallel\beta_e}{1+\beta_e^2}.
\]

This separates parallel conduction, dissipative transverse conduction and Hall transport.

## 5. Thermal budget

The bridge closes the earlier energy ledger with an explicit volumetric heat capacity:

\[
C_V\frac{dT}{dt}=
Q_{\mathrm{comp}}
+Q_{\mathrm{grav}}
+Q_{\mathrm{rec}}
+Q_{\mathrm{abs}}
+Q_{144}
+Q_{288}
+Q_{\mathrm{mix}}
-Q_{\mathrm{cool}}
-Q_{\mathrm{out}}.
\]

All terms must use compatible SI units, normally W m\(^{-3}\), while \(C_V\) is J m\(^{-3}\) K\(^{-1}\). The geometric path metric in `torus_path_sweep.c` is not silently interpreted as heat.

Along a rotating path,

\[
\frac{dT}{d\varphi}=\frac{1}{\Omega_{\mathrm{rot}}}\frac{dT}{dt},
\]

but \(\Omega_{\mathrm{rot}}\) must come from a declared dynamical model.

## 6. Magnetic-field seed

Crossed density and temperature gradients can seed a magnetic field through the Biermann term:

\[
\frac{\partial\mathbf B}{\partial t}
\supset
-\frac{k_B}{e}
\frac{\nabla n_e\times\nabla T_e}{n_e}.
\]

The implementation returns the source magnitude. Parallel gradients must yield zero; crossed gradients must yield a nonzero source.

Static charge separation is not equated with sustained magnetism. A magnetic field requires current, changing electric field, or a battery/dynamo mechanism.

## 7. Corona boundary

Two meanings remain separate:

- **electrical corona:** partial gas breakdown controlled by local field, density, pressure, temperature, geometry and composition;
- **astrophysical corona:** hot, dilute, magnetized plasma associated with an accretion flow and high-energy radiation.

The present code does not implement avalanche ionization, Paschen/Townsend kinetics, radiative transfer or pair creation. Those remain independent gates.

## 8. Carbon and “diamond planet” boundary

The phase path must not collapse distinct regimes:

\[
\text{condensed carbon}
\rightarrow
\text{liquid/vapor}
\rightarrow
\text{ionized plasma}
\rightarrow
\text{cooling/recombination}
\rightarrow
\text{possible condensation/crystallization}.
\]

Diamond-like \(sp^3\) bonding is a condensed-matter phase and does not survive in a fully ionized hot plasma. Carbon-rich plasma may later cool and nucleate solid phases, but the outcome depends on the complete \(P\)-\(T\)-\(\rho\)-composition-time path.

The pulsar companion PSR J1719−1438 b is treated only as a compact-remnant composition hypothesis. Its extreme density is measured indirectly through timing and orbital constraints; “entirely diamond” is not a direct compositional observation. Crystallized carbon/oxygen matter supported by electron degeneracy must not be identified automatically with ordinary mineral diamond.

## 9. Required observables

A physical 144/288 kHz claim requires, at minimum:

\[
V(t),\ I(t),\ \phi_{VI}(t),\ T_e(t),\ T_i(t),\ n_e(t),\ x_e(t),\ B(t),\ S(\omega).
\]

Derived gates include

\[
Z(\omega)=\frac{V(\omega)}{I(\omega)},
\qquad
P(\omega)=\frac12\operatorname{Re}[V(\omega)I^*(\omega)],
\]

\[
H_2=\frac{|I(288\,\mathrm{kHz})|}{|I(144\,\mathrm{kHz})|},
\qquad
\Delta\phi_2=\phi_{288}-2\phi_{144}.
\]

Promotion requires controls, uncertainty, power scaling, reproducibility and a mechanism that distinguishes ordinary plasma response from the proposed effect.

## 10. Falsifiers

The bounded bridge is rejected or revised if any of the following occurs:

1. units cannot be made consistent;
2. the 288 kHz component is claimed as generated without nonlinear evidence;
3. 144/288 kHz is promoted as an atomic transition from photon energy alone;
4. a scalar resistance is used where magnetized anisotropy is material;
5. a geometric path metric is relabeled as thermodynamic energy;
6. diamond is claimed inside a fully ionized plasma;
7. PSR J1719−1438 b is described as compositionally confirmed;
8. the bridge is used as cosmological validation.

## 11. Implementation

- model: `data/pipelines/strong_gravity/spiral_plasma_thermal_bridge.py`
- contract: `data/contracts/spiral_plasma_thermal_bridge.v1.json`
- deterministic baseline: `data/results/strong_gravity/spiral_plasma_thermal_bridge_baseline.json`
- tests: `tests/strong_gravity/test_spiral_plasma_thermal_bridge.py`

The implementation uses only the Python standard library and keeps `claim_allowed=false` in every generated result.
