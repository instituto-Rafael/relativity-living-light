# RLL Multiphysics Ruler V1

**Route token:** `ΩRULER-MP-V1`  
**Date:** 2026-09-09  
**State:** `ACTIVE_OPERATIONAL_PROTOCOL`  
**Claim default:** `false`  
**Mode:** append-only / fail-closed

## 1. Purpose

Provide a single auditable inspection route for RLL/RAFAELIA material involving geometry, waves/frequency, acoustic trapping, optical forces, thermal transport, electromagnetic/plasma channels, three-spiral/cardial-circle geometry, or analog horizons.

This document is a governance/model route. It is not physical evidence.

## 2. Hard epistemic invariants

```text
SOURCE != MODEL
MODEL != EXECUTION
EXECUTION != EVIDENCE
EVIDENCE != CLAIM
TOKEN_VAZIO != 0
geometric_circulation != physical_vortex
analogy != mechanism
real_gravitational_horizon != analog_horizon
```

No formula, image, simulation, semantic proximity or geometric resemblance is promoted to a physical claim without the corresponding observable gates.

## 3. Mandatory inspection route

For every relevant artifact, traverse in this order:

1. **provenance** — path/ref/commit, version, date, source;
2. **epistemic state** — `SOURCE | MODEL | EXECUTION | EVIDENCE | CLAIM`;
3. **units** — coherent physical units are mandatory for physical interpretation;
4. **mechanism** — distinguish geometry, analogy and physical mechanism;
5. **multiphysics channels** — `G/A/O/T/E/H`;
6. **coupling** — measure/model cross-response; semantic proximity is not causality;
7. **energy closure** — account for input, output and stored energy with uncertainty;
8. **stability** — require a restoring/stability observable when trapping is claimed;
9. **analog-horizon gate** — require its channel-specific condition;
10. **uncertainty and reproducibility** — calibration, clock, source digest and repetition;
11. **claim state** — fail closed;
12. **R3** — append `F_ok + F_gap + F_next`.

## 4. Six-channel decomposition

```text
G = geometry
A = acoustic
O = optical
T = thermal
E = electromagnetic / plasma
H = analog horizon
```

The six channels have `C(6,2)=15` binary pairs. Ternary and higher-order couplings are admitted only after a lower-order measurable cross-response justifies expansion.

## 5. Claim gate

Define

```text
Ω_claim = G_D AND G_F AND G_E AND G_H AND G_S AND G_R
```

where:

- `G_D`: dimensional/unit closure;
- `G_F`: force closure where forces are part of the mechanism;
- `G_E`: energy closure;
- `G_H`: analog-horizon condition, when applicable;
- `G_S`: local stability/restoring response;
- `G_R`: independent reproduction.

A failed or absent gate cannot be compensated by another successful gate.

## 6. Coupling Jacobian

Use

```text
J_ij = ∂y_i / ∂u_j
```

Reference controls:

```text
u = (f_US, phi_US, A_US, P_L, lambda_L, E, B, p, T)
```

Reference observables:

```text
y = (x, y, z, k_trap, T, q, I(lambda), v, P_out)
```

A coupling is promoted from hypothesis only when its response is distinguishable from uncertainty. A measured null becomes `NO_COUPLING_OBSERVED`; a missing measurement remains `TOKEN_VAZIO_MEASUREMENT`.

## 7. Energy and force closure

Reference energy residual:

```text
R_E = P_in - P_out - dU/dt
```

The acceptance criterion must be stated relative to uncertainty; `R_E ≈ 0` without uncertainty is not a closure claim.

For trapping/mechanical equilibrium, define the relevant force residual explicitly. A local restoring metric such as

```text
k_trap = -∂F/∂x
```

must have a documented sign convention and measured/modelled uncertainty before stability is claimed.

## 8. Analog horizon separation

### Acoustic

An acoustic analog horizon requires a documented crossing of a characteristic speed condition such as

```text
M = |u| / c_s = 1
```

with the medium, flow and sound speed explicitly defined.

### Optical

An optical analog horizon requires an explicit dispersive/index model and a moving perturbation/boundary whose characteristic velocity relationship is measured or modelled with units.

Neither condition licenses a gravitational event-horizon claim.

## 9. Three-spiral / cardial-circle inherited state

Inherited from the 2026-09-08 finite computational witness/receipt:

```text
quarter_turn_circle = PASS
sqrt3_radial_recurrence = PASS
golden_quarter_turn_ratio_phi = PASS
unpowered_flyby_relative_speed_invariant = PASS
third_spiral_existing_identity = TOKEN_VAZIO_NOT_ESTABLISHED
geometric_radius_equals_physical_periapsis = TOKEN_VAZIO_NO_SCALE_BINDING
physical_measurement = TOKEN_VAZIO_NOT_SUPPLIED
```

The central circle is admissible as a geometric/calibration model, not as a physical horizon by identity.

## 10. Falsifiable acoustic scale family

Define the scale family

```text
D_Ω(alpha,f,T,p) = alpha * c_s(T,p) / f
alpha ∈ {1/4, 1/2, 1, 2}
```

`alpha` is swept experimentally; it is not selected for aesthetic agreement.

For each `(alpha,f)` record at minimum, where applicable:

```text
k_trap
sigma_position
acoustic_power
temperature
phase
position
repeatability
energy_residual
uncertainty
```

A candidate optimum may be expressed as

```text
alpha* = argmax_alpha(k_trap)
```

subject to energy closure, uncertainty and reproduction gates.

`D_Ω = lambda/2` is therefore the testable member `alpha=1/2`, not a predetermined identity.

## 11. Claim states

Allowed terminal/intermediate states:

```text
PASS
FAIL
TOKEN_VAZIO
NO_COUPLING_OBSERVED
PROHIBITED_BY_SCOPE
```

Use a narrower `TOKEN_VAZIO_*` successor whenever the missing observable is known.

## 12. Required inspection record

```yaml
Ω_INSPECTION:
  source: null
  custody: null
  epistemic_state: null
  units: null
  geometry: null
  mechanism: null
  channels: []
  coupling_jacobian: null
  energy_closure: null
  uncertainty: null
  reproducibility: null
  claim_state: TOKEN_VAZIO
  F_ok: []
  F_gap: []
  F_next: null
```

## 13. Semantic routing

Trigger this route on:

`ΩRULER-MP-V1`, `THREE-SPIRAL`, `CARDIAL-CIRCLE`, `MULTIPHYSICS`, `ACOUSTIC-TRAP`, `OPTICAL-TWEEZER`, `ANALOG-HORIZON`, `ENERGY-CLOSURE`, `JACOBIAN`, `TOKEN_VAZIO`, `CUSTODY`, or equivalent concepts.

## 14. Provenance anchors

Project lineage includes:

- `rafaelia_three_spiral_slingshot_v1.py`;
- `RAFAELIA_THREE_SPIRAL_CARDIAL_SLINGSHOT_RECEIPT_20260908.v1.json`;
- RLL geometric-circulation / physical-vortex separation;
- RLL canonical freestanding coupling and geophysical systematics discipline;
- Drive canonical protocol `RAFAELIA — Ω-RULER MULTIPHYSICS — Protocolo Permanente de Inspeção Drive × GitHub — V1 — 2026-09-09`.

## 15. R3

```text
F_ok   = finite three-spiral geometry witness exists; fail-closed multiphysics route is specified
F_gap  = physical scale, measured couplings and physical measurements remain TOKEN_VAZIO where absent
F_next = apply Ω_INSPECTION to the next relevant observable artifact and append only the first claim that crosses units + mechanism + energy + uncertainty + reproduction
```
