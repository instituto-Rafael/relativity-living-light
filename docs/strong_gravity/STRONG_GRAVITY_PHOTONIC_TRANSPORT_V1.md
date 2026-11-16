# Strong-Gravity Photonic Transport V1

Status: **hypothesis-and-baseline extension**  
Authority: `instituto-Rafael/relativity-living-light`  
Parent route: `B08_strong_gravity_magnetokinetic`  
Scientific claim allowed: **false**

## 1. Scope

This document extends the existing strong-gravity calibration with a radiative/photon transport layer. It does **not** model the event horizon as a luminous material cloud. Radiation is emitted, absorbed, scattered and polarized by plasma/disk/corona/magnetospheric regions outside the horizon, while null rays propagate through curved spacetime.

The extension preserves the boundary:

```text
standard GR/GRMHD/GRRMHD/GRPIC/GRRT baseline
!=
new RLL physics
```

A new RLL claim requires an observable residual that survives the declared standard baselines.

## 2. Three spectra kept separate

1. **Fluid/plasma modes**: acoustic, ion-acoustic, Alfvén, slow/fast magnetosonic, shocks.
2. **Photon spectrum**: radio -> microwave -> IR -> visible -> UV -> X-ray -> gamma.
3. **Relativistic transfer/deformation**: Doppler, gravitational red/blueshift, lensing, absorption, scattering and Comptonization.

No equation in this extension identifies a plasma wave with a photon.

## 3. Established equations [F]

### Local observer frequency

For a future-directed null wave-vector `k^mu` and timelike observer `u^mu`,

```text
omega(u) = - k_mu u^mu > 0
```

and the measured frequency ratio is

```text
g = nu_obs / nu_em = omega_obs / omega_em.
```

Sequential deterministic frequency gains compose multiplicatively:

```text
g_total = product_j g_j
H_nu = ln(g_total) = sum_j ln(g_j).
```

The phrase "inverse Doppler" is therefore treated only as an analogy. The physical channels are ordinary relativistic Doppler/gravitational shifts and, where applicable, bulk Comptonization.

### Invariant radiative transfer

```text
Ical = I_nu / nu^3
Ecal = j_nu / nu^2
Acal = nu alpha_nu

dIcal/dlambda = Ecal - Acal Ical.
```

For constant non-negative coefficients over affine length `Delta lambda`,

```text
Ical_1 = Ical_0 exp(-Acal Delta lambda)
         + (Ecal/Acal) [1-exp(-Acal Delta lambda)]
```

with the continuous limit `Ical_1=Ical_0+Ecal Delta lambda` for `Acal=0`.

### Adiabatic trapped-radiation scaling

Under the conditional assumptions of isotropic radiation, `p_rad=u_rad/3`, and adiabatic compression,

```text
u_rad V^(4/3) = constant.
```

If the radiation field is additionally thermal, `u_rad=a T_gamma^4`, then

```text
T_gamma V^(1/3) = constant.
```

These are conditional identities, not claims that all photons near a black hole form a trapped blackbody.

### Plasma characteristic frequencies

```text
omega_pe = sqrt(n_e e^2/(epsilon_0 m_e))
omega_ce = |e B|/m_e.
```

### Local spiral-mode wavelength

For a phase

```text
Phi = m phi + integral k_r dr - integral omega dt + phi_0,
```

the local radial wavelength is

```text
lambda_r = 2 pi / |k_r|.
```

An inward increase of `|k_r|` implies radial wavelength contraction. This is a phase-geometry statement, not a new force.

## 4. Dimensionless hypothesis diagnostic [H]

The earlier verbal "Upside-Down Hammer" is retained only as a falsifiable diagnostic.

Define

```text
C_down = max(0,-Theta) tau_flow
R_ram  = p_ram/(p_th+p_B+p_rad)
M_f    = |v_n|/c_f
H_down = C_down M_f R_ram.
```

All factors and `H_down` are dimensionless.

Interpretation is intentionally limited:

```text
large H_down -> simultaneous strong convergence, fast-mode Mach loading,
                and ram dominance candidate
```

It is **not** a universal shock criterion. Its falsifier is direct: if `H_down` adds no predictive power for shock/heating/spectral hardening after conditioning on `Theta`, `M_f`, pressure ratios and the GRMHD/GRRT baseline, it is redundant and must not be promoted.

## 5. Timescale gate [D]

For any process `i`,

```text
Da_i = tau_flow/tau_i.
```

For the explicit first-order comparator `dX/dt=(1-X)/tau_i`,

```text
X(tau_flow) = 1-exp(-Da_i).
```

This converts the session question "does the state have time to change?" into a measurable residence-time comparison.

## 6. Phenomenological logistic gate [H]

A logistic transition may be tested only after declaring a physical control variable `chi` and its normalization:

```text
f_gamma(chi) = 1/[1+exp((chi-chi_t)/w_chi)].
```

Exact identities:

```text
f_gamma(chi_t)=1/2
f'_gamma(chi_t)=-1/(4 w_chi).
```

Candidate controls include dimensionless optical depth, compactness, magnetization or a normalized radius. A fitted logistic shape is not itself evidence for new physics.

## 7. Observable layer

The required observable state includes at minimum

```text
I_nu, Q_nu, U_nu, V_nu, tau_nu, j_nu, alpha_nu
```

plus plasma and flow state. Candidate temporal ordering:

```text
compression -> spectral hardening -> polarization change -> flare/outflow
```

The ordering is a hypothesis, not a result. It is testable through preregistered cross-correlation/lag analysis.

## 8. Mandatory baselines

Before any additional RLL term is needed, compare against:

- ideal GRMHD;
- resistive/non-ideal GRMHD;
- two-temperature GRRMHD;
- GRPIC where kinetic closure matters;
- general-relativistic radiative transfer including polarization where data permit;
- standard synchrotron, free-free, Compton and pair-process treatments appropriate to the source.

## 9. Falsifiability contract

The extension is unnecessary if either condition holds:

1. the proposed diagnostics are functions of existing baseline variables without independent predictive gain; or
2. out-of-sample likelihood/evidence does not improve after complexity penalties and uncertainty propagation.

Current states:

```text
module implemented             = true
deterministic unit tests added = true
remote CI                      = TOKEN_VAZIO
calibrated source solution     = TOKEN_VAZIO
exclusive RLL observable       = TOKEN_VAZIO
new physics confirmed          = false
claim_allowed                  = false
```

## 10. Non-regression invariants

- Historical strong-gravity calibration remains unchanged.
- `TOKEN_VAZIO != 0`.
- `IMPLEMENTED_UNTESTED != PASS`.
- No horizon-as-material-surface claim.
- No additive treatment of sequential frequency shifts.
- No classical magnetosonic formula is promoted as the relativistic GRMHD characteristic solver.
- No pycnonuclear/fission/nuclear rate is invented without a declared nuclear network/EOS.
