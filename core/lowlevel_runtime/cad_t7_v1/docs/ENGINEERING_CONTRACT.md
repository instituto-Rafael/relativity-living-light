# RAFAELIA Ω · Engineering model G0 — 2D pin-jointed truss V1

**Source:** New illustrative mathematical implementation (2026-11-08). External reference boundary: standard planar statics, linear elasticity and Euler buckling with stated assumptions. **Not a standard-compliant bridge design.**

## Exactly defined mechanical system

A 3-bar triangular truss has supports at `(0,0)` (pin), `(L,0)` (vertical roller), apex `(L/2,H)` under a vertical downward point load `P`. No horizontal load, no member weight, no distributed load. Members are axial only; no moments. Both sloping members are modeled as identical uniform solid circular sections with area `A_d`. Bottom tie is area `A_t`. Material is illustrative linear elastic with modulus `E` and yield stress `f_y`. Both diagonals have length `d = sqrt(H² + (L/2)²)` and angle `theta = atan(2H/L)`; baseline L=1000mm and H=500mm gives exactly 45 degrees.

Units: `L,H,d,δ` mm; `P,N_d,T,P_cr` kN; `A` mm²; `E` GPa; `σ` MPa; alpha µstrain/K. Multiplying `E[GPa]*A[mm²]` gives axial stiffness scaling in `kN` when divided by length `mm` (since 1 GPa = 1 kN/mm²).

### Verified analytic relationships (conditional on this mechanical model)

- Diagonal axial compression magnitude: `N_d = P*d/(2H)`.
- Bottom tie tension: `T = P*L/(4H)`.
- Nominal axial stress: `σ_d[MPa] = 1000*N_d[kN]/A_d[mm²]`; analogously for tie.
- Vertical apex deflection by virtual work/linear energy: `δ = (2 N_d² d /(E A_d) + T² L/(E A_t))/P`, with `E[GPa]`, `P[kN]`, `d,L[mm]`.
- Pinned–pinned ideal Euler buckling of each sloping member: `P_cr[kN] = π/4 × E[GPa] × (A_d[mm²]/d[mm])²`. Derives from `Pcr=π²EI/(K d)², K=1, I=A²/(4π)` for a solid circular section. Does NOT include effective length uncertainty, connection eccentricity, geometrical imperfections, plastic buckling, composite action or member self weight.
- Equivalent circular projected diameter used as SVG `stroke-width` in millimetres: `D=√(4A/π)`. **SVG line width here encodes this model's member diameter**, not its safety, and physical print/export scaling must be verified outside the file.
- Free thermal expansion: `ΔL_free = L × alpha_micro_per_K × ΔT / 10^6`. This is not a restrained thermal force; pin/roller supports may permit motion but the actual thermal displacement field is NOT solved.

### Fixed-point contract

All floating engineering values internal to the freestanding kernel use signed **Q16.16** integers. Only `alpha_micro_per_K` uses integer micro/K because 12×10⁻⁶ cannot be represented as an accurate Q16 strain-per-K. Arithmetic is guarded against invalid domains and overflow; division is implemented as a deterministic 64-bit software long division to remove ARMv7 `__aeabi_ldivmod` dependencies. Fixed-point rounding introduces bounded numerical discrepancies; compare against an independent double reference in `qa/cad_checks.py`. This is a model arithmetic test, not laboratory evidence.

Parameter bounds: `100 ≤ span ≤ 2000 mm`, `100 ≤ rise ≤ 1000 mm`, `10 ≤ area ≤ 1000 mm²`, `0 < P ≤ 10 kN`, `1 ≤ E ≤ 400 GPa`, `10 ≤ f_y ≤ 1000 MPa`, `-100 ≤ ΔT ≤100 K`, `0 ≤ alpha_micro ≤200`. No inference is allowed outside the bounded input domain.

### Warning/claim states

- `INVALID_INPUT` or `NUMERIC_OVERFLOW`: fail-closed; no output promotion.
- `WARN_YIELD`: nominal axial stress meets/exceeds the declared yield threshold.
- `WARN_BUCKLING`: Euler ratio less than 2 (illustrative threshold, NOT a normative safety factor).
- `WARN_DEFLECTION`: apex displacement greater than L/500 (illustrative threshold, NOT normative).
- `WARN_THERMAL_MODEL`: always set because thermal restraint not modeled.
- `claim_allowed=false` even when no warning triggers. No load combinations, code design checks, capacity factors, fatigue, seismic effects, failure probability or physical verification.

## Seven-dimensional reparameterization — NOT physical 7D mechanics

`T^7=(R/Z)^7` is the **seven-dimensional periodic parameter domain**; it is not a discovery that a bridge exists in seven physical spatial dimensions or that a torus mediates real material forces.

Coordinates control, respectively: `(L, H, Ad, At, P, E, ΔT)`.

Samples are 42 deterministic points along a one-dimensional periodic sweep embedded in the 7D torus. They **do not uniformly cover T⁷**, do not show stability/convergence over the entire domain, and have no statistical randomness claim. A simple triangular wave maps each phase into bounded multiplicative perturbations. `yield_MPa` and alpha are held fixed to isolate the sweep.

## Falsifiers and next components

- Independent 2D finite-element truss stiffness matrix for identical geometry and boundary conditions; compare all 42 Q16 outputs against a double precision, independently sourced solver.
- Exact input/output dimension and load equilibrium; verify reactions and member forces using forces/moment balance.
- End-to-end Q16 error bounds under worst-case input variation; monitor overflow, div-by-zero, saturation, hardware ABI and adversarial geometries.
- To model **beam shear, torsion and bending**, add Euler-Bernoulli/Timoshenko beam elements with appropriate moment of inertia, torsion constant, shear area, local coordinate systems, boundary constraints and independent solver oracle. A truss axial element cannot supply those outputs.
- Material nonlinearity, buckling mode factors K, fatigue, design standards, weld/bolt connection resistance, loads, real environmental evidence and hardware thermal/dynamic tests are all `NOT_RUN`.

`SOURCE ≠ ARTIFACT ≠ EXECUTION ≠ EVIDENCE ≠ CLAIM`. No numerical value in this synthetic demonstration is evidence that any real bridge is safe.
