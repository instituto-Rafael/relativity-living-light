# Energy-momentum dimensional blocker — 2026-09-22

State: `FAIL_FOUND`  
Scientific claim: `BLOCKED`

## Finding

The current observational ledger declares the following energy-like fields in `J/m^3`:

- `rho_before`
- `rho_rest_after`
- `rho_radiation`
- `rho_kinetic`
- `rho_thermal`
- `rho_field`

while pressure is declared in `Pa`, which is dimensionally equivalent to `J/m^3`.

However, the current bridge implementation computes:

```python
pressure_density = pressure / c**2
```

which has units:

[
rac{J/m^3}{m^2/s^2}=kg/m^3.
]

The code then adds that mass-density quantity to terms declared as energy densities in `J/m^3`.

Therefore the present scalar transition sum is dimensionally inconsistent for nonzero pressure.

## Gate

```text
ENERGY_MOMENTUM_SCALAR_DIMENSIONAL_CONSISTENCY=FAIL_FOUND
ENERGY_MOMENTUM_SCALAR_PHYSICAL_CLAIM=BLOCKED
```

Synthetic tests with `pressure=0` do not expose the dimensional defect because the offending term numerically vanishes.

## Valid repair routes

### Route A — energy-density representation

Keep every rho-like term in `J/m^3`. Pressure remains `Pa = J/m^3`, but it must not be converted by `/c^2` before being combined with energy-density terms. The physical meaning of adding a pressure term to a scalar energy budget must still be explicitly justified; in relativistic fluid dynamics pressure generally belongs in the stress-energy tensor rather than as an arbitrary scalar addend.

### Route B — mass-equivalent density representation

Convert every energy-density term by `/c^2` and work consistently in `kg/m^3`.

### Route C — covariant stress-energy representation (preferred for GR claims)

Represent energy density, momentum density, pressure and stress through the relevant components of `T^{\mu\nu}`, with an explicit metric/frame and conservation contract.

## Required regression

A repaired implementation must include at least one nonzero-pressure fixture whose expected result is checked dimensionally and numerically. The present zero-pressure synthetic fixture is insufficient.

No historical result is deleted. This document supersedes only the assumption that the current scalar bridge is physically dimensionally closed.
