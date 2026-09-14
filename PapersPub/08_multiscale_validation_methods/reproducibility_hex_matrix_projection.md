# Reproducibility — Hexagonal Matrix, Toroidal Attachment and Poincaré Section

**Status:** `analysis_run`  
**Exact geometry:** `PASS`  
**Physical extrapolations:** `TOKEN_VAZIO`  
**Global claim gate:** `claim_allowed=false`

## Scope

This protocol reproduces:

- triangular/hexagonal basis and determinant;
- induced metric;
- six unit neighbors;
- elementary equilateral lattice cell;
- `40`, `21` and `840` matrix/tensor counts;
- torus radial bounds `R-r` and `R+r`;
- equilateral triangle in the meridian circle;
- rotating-square inner and outer envelopes;
- 30-degree tangent condition through a zero discriminant;
- frequency-3 icosphere Euler characteristic;
- one linear Poincaré return example.

It does not reproduce:

- physical fluid flow;
- Venturi behavior;
- material vorticity;
- nonlinear stability;
- a cosmological torus;
- geodesic spacetime;
- the Poincaré conjecture.

## Environment

- Python 3.11 or newer;
- standard library only;
- no network required;
- IEEE-754 binary64 arithmetic.

## Command

From repository root:

```bash
python3 PapersPub/08_multiscale_validation_methods/scripts/validate_hex_matrix_projection.py
```

Expected exit code:

```text
0
```

Expected summary:

```json
{
  "checks_total": 15,
  "checks_passed": 15,
  "checks_failed": 0,
  "status": "PASS",
  "exact_geometry_state": "PASS",
  "physical_claims_state": "TOKEN_VAZIO",
  "claim_allowed": false
}
```

## Independent report

```bash
python3 PapersPub/08_multiscale_validation_methods/scripts/validate_hex_matrix_projection.py \
  --output /tmp/hex_matrix_projection_validation.json
```

Compare with:

```text
PapersPub/08_multiscale_validation_methods/results/hex_matrix_projection_validation.json
```

## Manual equations

```text
det([[1,1/2],[0,sqrt(3)/2]]) = sqrt(3)/2
G = H^T H = [[1,1/2],[1/2,1]]
d² = dc² + dc·dr + dr²
8×5 = 40
7×3 = 21
40×21 = 840
R-r ≤ ||X(u,v)|| ≤ R+r
largest meridian equilateral side = sqrt(3)r
square common radius = s/2
square swept radius = s/sqrt(2)
30-degree tangent slope = ±1/sqrt(3)
V-E+F = 2 for the declared icosphere counts
P(v)=v+2π(omega_v/omega_u) mod 2π
```

## FAILSAFE

Passing the validator allows only exact finite and model-definition statements.

```text
hexagonal_projection = PASS
torus_embedding = PASS
spherical_radial_bounds = PASS
linear_return_map = PASS
physical_vortex = TOKEN_VAZIO
Venturi = TOKEN_VAZIO
cosmological_interpretation = PROHIBITED_BY_SCOPE
```

## Independent implementation

The runtime implementation and unit tests are maintained separately in:

```text
rafaelmeloreisnovo/ChipQuantum
src/geometry/sqrt3_geometry_matrix/
```

RafPolimata maintains the evidence/governance bridge. Cross-repository agreement must be checked by formulas and schemas rather than by copying one implementation into every repository.
