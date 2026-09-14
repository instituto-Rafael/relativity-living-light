# Claim-state ledger — Four-axis ports and cyclic-base curvature

| ID | Statement | Class | State | Evidence/Falsifier |
|---|---|---|---|---|
| `FLOW-E-001` | Four opposed axes produce eight distinct meridian ports. | `[E]` | `PASS` | Direct enumeration: `4×2=8`. |
| `FLOW-E-002` | Every opposed pair has midpoint `C` and length `2r`. | `[E]` | `PASS` | Coordinate substitution. |
| `FLOW-E-003` | Every port lies on the meridian circle. | `[E]` | `PASS` | `||P-C||=r`. |
| `FLOW-E-004` | Every aperture tangent is perpendicular to its radial normal. | `[E]` | `PASS` | `n·t=0`. |
| `FLOW-E-005` | The tangent-line distance from the center equals `r`. | `[E]` | `PASS` | Point-line distance. |
| `FLOW-E-006` | The eight directions cover axial and square-diagonal neighbors. | `[E/C]` | `PASS/REFERENCE` | Exact set comparison plus declared stencil. |
| `FLOW-E-007` | Unit diagonal directions have components `±1/sqrt(2)`. | `[E]` | `PASS` | Euclidean normalization. |
| `FLOW-E-008` | Sweeping each port around `u` preserves the meridian radius. | `[E]` | `PASS` | Substitution in the torus meridian equation. |
| `FLOW-C-009` | Ports function as matrix gates or channel labels. | `[C]` | `REFERENCE` | Computational convention. |
| `FLOW-E-010` | Base Venturi is the reversible fold `V_b(n)=(q,r)` with `n=bq+r`. | `[E]` | `PASS` | Reconstruction identity. |
| `FLOW-E-011` | Decimal `7` is written `10` in ordinary base-seven notation. | `[E]` | `PASS` | Positional encoding. |
| `FLOW-E-012` | `7 mod 7=0` is only the remainder; the complete state is `(1,0)`. | `[E]` | `PASS` | Euclidean division. |
| `FLOW-E-013` | The one-based cyclic phase of decimal `7` in a seven-phase cycle is `7`. | `[E]` | `PASS` | `1+((7-1) mod 7)=7`. |
| `FLOW-E-014` | Additive vortex return preserves cycle/carry when the visible phase wraps. | `[E]` | `PASS` | `W_b(n,δ)=E_b(n+δ)`. |
| `FLOW-E-015` | The circular seam may coincide geometrically while lifted winding remains distinct. | `[E]` | `PASS` | Helical lift `Gamma_b`. |
| `FLOW-E-016` | Zero is a valid value/seam/remainder and is not equivalent to absent information. | `[E]` | `PASS` | State-model definition. |
| `FLOW-E-017` | Fixed-width unsigned subtraction may be encoded as addition of two's complement. | `[E]` | `PASS` | `a-b == a+(~b+1) mod 2^w`. |

```text
exact_geometry_state = PASS
operator_state = PASS
empirical_fluid_interpretation = NOT_APPLICABLE
claim_allowed = true
```
