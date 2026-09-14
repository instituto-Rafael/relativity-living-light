# Claim-State Ledger — Hexagonal Matrix / Toro / Sphere / Poincaré Appendix

**Global gate:** `claim_allowed=false`

| ID | Class | State | Claim | Falsifier / promotion requirement |
|---|---|---|---|---|
| `GEO-HEX-001` | `[E]` | `PASS` | `det(H_hex)=sqrt(3)/2`. | Recompute the determinant. |
| `GEO-HEX-002` | `[E]` | `PASS` | `G=H_hex^T H_hex=[[1,1/2],[1/2,1]]`. | Matrix multiplication disagrees. |
| `GEO-HEX-003` | `[E]` | `PASS` | Six axial directions have unit metric distance. | Any declared direction differs from one. |
| `GEO-HEX-004` | `[E]` | `PASS` | Elementary lattice triples are equilateral. | Any of the three side lengths differs. |
| `GEO-HEX-005` | `[E]` | `PASS` | A has 40 states, B has 21 and A×B has 840 relations. | Enumeration differs. |
| `GEO-HEX-006` | `[C]` | `PASS` | The final axis of `8×5×7×3×2` stores `(dx,dy)`. | Schema or implementation changes without versioning. |
| `GEO-TOR-007` | `[E]` | `PASS` | The standard ring torus has radial bounds `R-r` and `R+r`. | A torus point norm lies outside the interval. |
| `GEO-TOR-008` | `[E]` | `PASS` | The meridian section is `(rho-R)^2+z^2=r^2`. | Direct substitution fails. |
| `GEO-TOR-009` | `[E]` | `PASS` | Its upper/lower branches are semicircular square-root branches. | Branch substitution fails. |
| `GEO-TOR-010` | `[E]` | `PASS` | The maximum inscribed equilateral triangle has side `sqrt(3)r`. | Three 120-degree chord lengths differ. |
| `GEO-SQR-011` | `[E]` | `PASS` | A rotating centered square has common radius `s/2` and swept radius `s/sqrt(2)`. | Inradius/circumradius differs. |
| `GEO-QUAD-012` | `[E]` | `PASS` | Line–meridian intersection is a quadratic classified by `Delta`. | Substitution yields different coefficients. |
| `GEO-TAN-013` | `[E,C]` | `PASS` | Imposed `30°` tangents have slope `±1/sqrt(3)` and `Delta=0`. | Generated lines are not tangent. |
| `GEO-SPH-014` | `[E,C]` | `PASS` | Frequency-`f` icosphere counts satisfy `V=10f²+2`, `E=30f²`, `F=20f²`. | Counts fail subdivision combinatorics or Euler characteristic. |
| `GEO-POIN-015` | `[E,C]` | `PASS` | Linear `T²` flow gives `P(v)=v+2π(omega_v/omega_u) mod 2π`. | Direct integration differs. |
| `PHY-VOR-016` | `[H]` | `TOKEN_VAZIO` | The embedding describes a measured physical vortex. | Requires a physical field, units, equations, data and uncertainty. |
| `PHY-VEN-017` | `[H]` | `TOKEN_VAZIO` | The geometric contraction produces a Venturi effect. | Requires continuity, momentum/energy model, fluid parameters and measurements. |
| `COS-TOR-018` | `[H]` | `PROHIBITED_BY_SCOPE` | The torus/sphere construction is the geometry of the physical Universe. | Requires an observational cosmological model and comparison with data. |
| `TOP-SPH-019` | `[H]` | `PROHIBITED` | The sphere is exactly tiled by planar congruent equilateral triangles. | Curvature and radial projection prevent this generic exact tiling. |
| `POIN-CONJ-020` | `[H]` | `PROHIBITED` | The implemented return map proves the Poincaré conjecture. | Category error: return map and 3-manifold conjecture are distinct. |

## Promotion rule

```text
exact finite check PASS
  does not promote
physical mechanism TOKEN_VAZIO
```

A physical claim requires, at minimum:

```text
variables + units + governing equations + initial/boundary conditions
+ data + uncertainty + falsifier + independent reproduction
```
