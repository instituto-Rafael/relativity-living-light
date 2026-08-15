# RLL Stellar Light Ledger / Olbers Boundary — 2026-08-15

Status: `GOVERNED_CONCEPTUAL_EXTENSION`

Claim boundary: `claim_allowed_dark_energy_photon_literal=false`

This note preserves the session insight that stellar emission, stellar motion, stellar death, black-hole formation, and long propagation times must be treated as a ledger, not as a static picture.

## 1. Physical intuition preserved

If every direction in space eventually pointed to a star in an infinite, eternal, static universe, the sky should be bright. The fact that it is dark creates the classical Olbers boundary condition: the universe is not an infinite static lamp field from the observer's perspective.

In RLL language:

```math
observed\ light \neq emitted\ light\ at\ source\ time
```

The observer receives a delayed, redshifted, filtered, and geometrically diluted ledger of events.

## 2. Stellar ledger

A star is not a fixed emitter. Across cosmic time it can:

- reduce luminosity;
- move relative to the observer;
- eject mass;
- become a compact remnant;
- collapse into a black hole;
- stop emitting visible light while its previous photons still propagate.

Therefore the relevant RLL object is a trajectory ledger:

```math
\mathcal{L}_\star(t)
=
\{M_\star(t), L_\gamma(t), x_\star(t), z(t), R_{rem}(t), \Phi_\gamma(t)\}
```

Where:

- `M_star(t)` is stellar/remnant matter state;
- `L_gamma(t)` is photon luminosity/emission;
- `x_star(t)` is position/worldline;
- `z(t)` is cosmological/kinematic redshift proxy;
- `R_rem(t)` is remnant/black-hole/state transition marker;
- `Phi_gamma(t)` is received photon flux at the observer or local buffer.

## 3. Conservation boundary

Locally, matter-energy bookkeeping remains required: emitted photons, ejecta, remnant mass, kinetic energy, thermal energy, neutrinos, and gravitational effects cannot be ignored.

However, in an expanding cosmological spacetime, there is no simple global Newtonian box where photon energy is conserved as an unchanged scalar along all cosmic propagation. Redshift and geometry must be part of the ledger.

RLL should therefore track:

```math
E_{ledger}
=
E_{photons,received}
+
E_{redshifted/lost\ to\ expansion\ bookkeeping}
+
E_{remnant}
+
E_{ejecta}
+
E_{fields}
+
TOKEN\_VAZIO_{unobserved}
```

`TOKEN_VAZIO_unobserved` is mandatory where the causal path, source identity, or remnant state is not observed.

## 4. Dark matter / dark energy claim boundary

The session phrase "dark energy is the photon here" is preserved as a local proxy intuition:

```math
\Phi_\gamma(t) = local\ energetic\ flux\ proxy
```

It is **not** promoted to a literal cosmological identity:

```math
photon \neq dark\ energy\ standard\ component
```

Similarly, matter no longer visible from an old source is not automatically dark matter. It may be ordinary matter, remnant matter, black-hole mass, dust, gas, radiation history, or an unobserved ledger component.

```math
unseen\ source\ matter \neq dark\ matter\ by\ default
```

The defensible RLL form is:

```math
M_{inferred}(t)
=
M_{visible}(t)
+M_{remnant}(t)
+M_{gas/dust}(t)
+M_{compact}(t)
+M_{unknown}(t)
```

Only after gravitational inference and known-baryon accounting fail does a dark-matter-like residual become relevant.

## 5. Observer / mirror / photon cross-link

The stellar ledger is not the final measurement. The next transform is now governed by:

- `RLL_OBSERVER_MIRROR_PHOTON_GATE_20260815.md`
- `scripts/rll_observer_mirror_photon_gate.py`

The cross-link is:

```math
L_{observed}
=
T_{observer}\circ T_{mirror}\circ T_{space}(L_{emitted})
```

and therefore:

```math
\Phi_\gamma(t)_{usable}
=
O_{frame}\left[R_{mirror}(\gamma_{source})\right]
```

This separates source emission, propagation, optical path, camera registration, and observer frame.

## 6. RLL projection

The stellar-light ledger becomes an input to the homeostatic field gate:

```math
\frac{d\rho_{org}}{dt}
=
\alpha \Phi_\gamma(t)S(t)
+
\beta C(t)
-
\chi J_{diss}(t)
-
\delta R(t)
+
\eta H(t)
```

with `Phi_gamma(t)` explicitly defined as received/usable flux, not total emitted source energy.

## 7. Next falsification gates

1. Build source/remnant ledgers for stellar populations.
2. Separate received photons from emitted photons.
3. Include redshift and luminosity-distance dilution.
4. Compare baryonic/remnant accounting against lensing and rotation residuals.
5. Only then test whether an RLL residual maps to dark-matter or dark-energy observables.
6. Add observer/mirror/camera transformation data where the measurement path is nontrivial.

## 8. Invariants

- `photon != dark_energy_literal`
- `unseen ordinary matter != dark_matter_by_default`
- `local conservation bookkeeping != simple global cosmological conservation`
- `Olbers boundary must be explicit`
- `observed_image != untransformed_photon_ledger`
- `observed_light != emitted_light_at_source_time`
- `TOKEN_VAZIO` preserves unobserved source/remnant paths
- `claim_allowed_dark_energy_photon_literal=false`
