# RLL Strong-Gravity Heuristic Calibration — 2026-07-17

**Domain:** B08 strong-gravity magnetokinetic/electrodissociative branch  
**State:** executable reference calibration  
**Raw data:** immutable  
**New-physics claim:** `claim_allowed=false`

## 1. Session compression

The session proposed a coupled picture in which a large inflow of matter:

1. contributes collectively to the gravitational field;
2. is compressed and heated while retaining an outward pressure response;
3. moves in a rotating, shearing, magnetized flow;
4. undergoes molecular dissociation, ionization and eventually pair-plasma processes;
5. converts pressure, velocity and radiation gradients into electric current and magnetic structure;
6. can oscillate, shock, reconnect and radiate.

The implementation preserves the analogy but separates its physical mechanisms:

```text
solid fatigue/electrolysis analogy
        ↓ scale and phase gate
molecular dissociation / photoionization / impact ionization
        ↓
plasma current, generalized Ohm law, Hall and pressure terms
        ↓
self-gravitating GRMHD/GRPIC comparison
```

This extends the previous magnetokinetic conversion and self-gravity analysis. It does not merge the branch into the cosmological parameter `Omega_s0` without a demonstrated bridge.

## 2. RNN wording resolved

Within this delivery, “RNN” is interpreted from the session context as a **recurrent RLL state calibration**:

\[
X_t=(\rho_t,x_{e,t},J_t,u_t),
\qquad
X_{t+1}=F(X_t;\Gamma,Q,\Delta t).
\]

It is not represented as a trained recurrent neural network because the session did not provide:

- a training corpus;
- labels or targets;
- a loss function;
- train/validation/test partitions;
- an observational covariance contract.

The neural-training state therefore remains `TOKEN_VAZIO`. The transparent recurrence is useful for equations, unit tests and future inverse calibration.

## 3. Eight calibration heuristics

| Gate | Purpose | Failure prevented |
|---|---|---|
| H1 scale separation | atomic → material → plasma → disk → spacetime | mixing atomic gravity with collective gravity |
| H2 force dominance | compare local EM/pressure to bulk gravity | assigning molecular binding to gravity |
| H3 phase ladder | track molecular, atomic, plasma and pair regimes | applying fatigue/electrolysis literally after ionization |
| H4 self-gravity | use `mu_d` and Toomre `Q_T` | treating every dense flow as self-gravitating/fragmenting |
| H5 transduction | map gradients to current through explicit terms | renaming known plasma physics as a new effect |
| H6 photon threshold | use `E=h nu` plus material response | treating microwave heating as direct ionization |
| H7 recurrence | explicit rates, timestep and bounds | opaque evolution without numerical contract |
| H8 falsifier | standard GRMHD/GRPIC/radiation baseline | promoting a residual before null-model comparison |

## 4. Implemented operators

### 4.1 Geometry and orbital scale

\[
r_g=\frac{GM}{c^2},
\qquad
\Omega_K=\sqrt{\frac{GM}{r^3}},
\qquad
T_{orb}=\frac{2\pi}{\Omega_K}.
\]

### 4.2 Collective self-gravity

\[
\mu_d=\frac{M_d}{M_{BH}},
\qquad
\Sigma_{ref}=\frac{M_d}{\pi r^2},
\qquad
Q_T=\frac{c_s\kappa}{\pi G\Sigma}.
\]

Interpretation policy:

- `Q_T <= 1`: self-gravity instability candidate under the reference assumptions;
- `mu_d >= 0.1` with `Q_T > 1`: disk backreaction may be relevant, but fragmentation is not inferred;
- neither gate: self-gravity subdominant in the reference calculation.

### 4.3 Compression and expansion competition

\[
Q_{comp}=-p\Theta,
\qquad \Theta<0\Rightarrow Q_{comp}>0,
\]

\[
\mathcal R_{GT}=\frac{P_{th}+P_B+P_{rad}}{\rho|\Phi_{eff}|}.
\]

`R_GT` is a diagnostic, not a universal law:

- below one: inward binding dominates the declared local budget;
- around one: transitional/oscillatory regime;
- above one: pressure/outflow channel becomes competitive.

### 4.4 Mechanical-to-electric transduction

\[
\mathcal G_{ME}=\frac{P_{electric}}{P_{compressive}+\epsilon}.
\]

This measures a declared conversion ratio. A physical calculation must derive electrical power from a generalized Ohm law or kinetic plasma model rather than insert it by label.

### 4.5 Oscillation and tidal gradient

\[
\mathcal Q_{osc}=\frac{\omega_0}{2\gamma},
\qquad
\Delta a_{tidal}=\frac{2GM L}{r^3}.
\]

The tidal term is kept separate from photoionization and collision rates, preventing gravitational energy from being double-counted as direct atomic ionization.

### 4.6 Radiation ladder

\[
E_\gamma=h\nu.
\]

The code classifies broad channels only. Material-specific statements require cross sections, opacity and composition.

### 4.7 Recurrent cascade

\[
\dot\rho=-\rho\Theta,
\]

\[
\dot x_e=\Gamma_{photo}+\Gamma_{impact}+\Gamma_{field}+\Gamma_{tidal}-\Gamma_{rec}x_e,
\]

\[
\dot J=\frac{J_{drive}-J}{\tau_J},
\]

\[
\dot u=Q_{comp}+Q_{grav}+Q_{EM}+Q_{rad}-Q_{cool}-Q_{out}.
\]

The implementation clamps only quantities with explicit physical bounds (`rho>=0`, `0<=x_e<=1`, `u>=0`). Signs and units remain caller responsibilities.

## 5. Numerical execution

Command:

```bash
PYTHONPATH=src python scripts/run_strong_gravity_calibration.py
```

Committed output:

```text
results/strong_gravity_calibration/session_reference_sweep_20260717.json
```

### 5.1 Water expansion reference

Using the ideal-gas approximation for 1 kg of water vapor at 373.15 K and 1 atm:

\[
V\approx1.69965\;m^3,
\qquad
V/(1\;litre)\approx1699.65.
\]

This validates the session's order-of-magnitude intuition of roughly 1,600–1,700 litres, not 1,600 cubic metres. It is a reference calculation; saturated-steam tables differ slightly.

### 5.2 Atomic force scale

For an electron and proton:

\[
\frac{F_E}{F_G}\approx2.26866\times10^{39}.
\]

Therefore local atomic/molecular restoring forces are electromagnetic. This does not remove the collective gravitational field of a massive disk.

### 5.3 Black-hole scale sweep

Assumptions:

- radius: `20 r_g`;
- sound speed: `0.05 c`;
- mean reference surface density: `M_d/(pi r^2)`;
- Newtonian Kepler/Toomre reference, not a GRMHD solution.

For both a 10-solar-mass black hole and a 4.3-million-solar-mass black hole, the dimensionless Toomre values are identical under equal scaled assumptions:

| `M_d/M_BH` | Reference `Q_T` | Gate |
|---:|---:|---|
| 0.001 | 223.6068 | self-gravity subdominant |
| 0.010 | 22.3607 | self-gravity subdominant |
| 0.100 | 2.2361 | disk backreaction relevant |
| 0.250 | 0.8944 | instability candidate |

The orbital period at `20 r_g` changes with mass:

- `10 M_sun`: `0.0276814 s`;
- `4.3e6 M_sun`: `11902.9874 s` ≈ `3.3064 h`.

This demonstrates a useful calibration invariant: the dimensionless regime can remain similar while the physical clock scales linearly with central mass.

### 5.4 Radiation reference

| Band reference | Photon energy | Broad channel |
|---|---:|---|
| 2.45 GHz microwave | `1.013e-5 eV` | collective/rotational heating |
| 30 THz infrared | `0.1241 eV` | vibrational/electronic heating |
| 3 PHz ultraviolet | `12.407 eV` | dissociation/photoionization depending on species |
| 10 keV X-ray | `9999.999 eV` | photoionization and secondary electrons |
| 1 MeV gamma | `999999.9 eV` | high-energy Compton/nuclear thresholds; below free-space pair rest threshold |

### 5.5 Recurrent algorithm smoke test

A deliberately synthetic, dimensionless 20-step recurrence produced:

| State | Initial | Final |
|---|---:|---:|
| density | 1.0000 | 1.48595 |
| ionization fraction | 0.0500 | 0.49613 |
| current density | 0.0000 | 1.28303 |
| internal energy density | 1.0000 | 1.66000 |

This proves only that the recurrence, bounds and signs behave as configured. It is not a fit to a black hole or a trained RNN.

## 6. TOKEN_VAZIO before real calibration

A physical calibration remains blocked until the following exist:

```text
source mass and spin
accretion rate and disk mass profile
magnetic field topology
T_e and T_i
radiation spectrum/opacity
composition and reaction cross sections
observational target and covariance
GRMHD/GRPIC baseline
registered objective and falsifier
```

## 7. Falsifier

The strong-gravity RLL branch adds explanatory value only if a preregistered observable residual survives:

\[
\mathrm{GRMHD}_{self-gravity}
+\mathrm{radiation}
+\mathrm{chemistry/ionization}
+\mathrm{kinetic\ plasma}
\]

under the same initial conditions, nuisance model and covariance.

Safe state:

```text
implemented mathematics       yes
reference numerical sweep     yes
observational calibration     TOKEN_VAZIO
trained recurrent neural net  TOKEN_VAZIO
new physical coupling         not demonstrated
```
