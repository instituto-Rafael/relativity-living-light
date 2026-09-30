# RLL Paradox Thermodynamic Layer

Status: exploratory.
Rule: Mpemba/Frost are non-equilibrium analogies, not cosmological proof.

Variables: T, P, rho, eta, kappa, chi_i, tau_relax, tau_half.

Term: epsilon_thermo = residual linked to relaxation, phase change, opacity, absorption, and transport.

Targets: H(z), BAO, SNe, CMB foregrounds, spectra.

---

## Successor binding — 2026-08-27

This historical exploratory layer remains preserved. Its Mpemba component is now governed by the bounded strong-gravity successor:

- operational branch: `B10_black_hole_thermodynamics_mpemba_falsifier`;
- implementation: `data/pipelines/strong_gravity/mpemba_horizon_falsifier.py`;
- contract: `data/contracts/mpemba_horizon_falsifier.v1.json`;
- ATLAS/falsifiers: `docs/RLL_MPEMBA_HORIZON_ATLAS.md`;
- global source registry: `data/registries/rll_recent_primary_sources_2026.json`.

The legacy term `epsilon_thermo` is not automatically identified with a black-hole relaxation distance. A B10 Mpemba witness instead requires a declared state and target plus a preregistered distance/threshold:

```text
D_far(0) > D_near(0)
exists t>0: D_far(t) < D_near(t)
tau_far(epsilon) < tau_near(epsilon)
```

Boundary:

```text
Mpemba/Frost analogy != cosmological proof
synthetic Mpemba witness != astrophysical detection
EHT plasma/polarimetry != Hawking thermometry
local strong-gravity anomaly != RLL-over-LambdaCDM evidence
```

Any bridge from this layer to `H(z)`, BAO, SNe or CMB requires its own covariant model equation, likelihood, covariance, baseline and falsification gate. Until that bridge exists, the cosmological implication is `TOKEN_VAZIO`, not zero and not confirmation.
