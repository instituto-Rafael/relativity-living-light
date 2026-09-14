# Appendix C — Geodesic 15° Refinement, Toroidal Return and 14-Axis Visual Bridge

Date: 2026-09-12
State: [E/C] FORMAL_GEOMETRY + VISUAL_BRIDGE / PHYSICAL_CLAIMS_BLOCKED
Parent: appendix_b_hex_matrix_projection.md
claim_allowed: false

## C.1 Scope

Appendix B already establishes and validates:
- hexagonal projection basis;
- sqrt(3)/2 determinant/area scale;
- standard torus embedding;
- radial bounds R-r <= ||X|| <= R+r;
- circular meridian section;
- maximum equilateral triangle in that circle;
- quadratic line-circle intersections;
- 30-degree tangent constraint with Delta=0;
- icosphere combinatorics;
- linear Poincare return map;
- 15/15 deterministic checks PASS.

This appendix adds a visualization/refinement layer only. It does not upgrade any physical claim.

## C.2 15-degree angular refinement [C]

Define the declared grid:

Theta_15 = {15°,30°,45°,60°,75°,90°}.

Exact cyclic relations:

3*15°=45°
6*15°=90°
12*15°=180°
24*15°=360°.

The grid is a computational/model refinement. It is not claimed as an intrinsic invariant of all geodesic spheres.

## C.3 Local face geometry [E,C]

For a planar equilateral reference face of side s:

h = (sqrt(3)/2)s.

Median, height and angle bisector coincide.

For an isosceles triangle with equal side l and half-apex angle alpha:

b = 2l sin(alpha)
h = l cos(alpha).

At alpha=30°:

b=l,

which recovers the equilateral case.

The projected f=2 icosphere still uses spherical triangles after radial projection; they are not silently reclassified as congruent planar equilateral faces.

## C.4 Quadratic / Bhaskara bridge [E]

Retain Appendix B:

A rho² + B rho + C = 0
Delta = B² - 4AC.

The sign of Delta classifies line-circle intersection.

A 30° tangent is one declared constraint:

|m| = tan30° = 1/sqrt(3)

with Delta=0.

A 15° line can likewise be evaluated:

|m| = tan15° = 2-sqrt(3),

but tangency still depends on the intercept satisfying the circle-distance condition. The angle alone does not create tangency.

## C.5 Poincare return and toroidal midpoint [E,C]

For the declared linear flow:

P(v)=v+2pi(omega_v/omega_u) mod 2pi.

The visualization may mark:

R-r, R, R+r

as minimum/median/maximum Euclidean radial quantities.

Calling R a "toroidal pulse" is MODEL_CHOICE unless a physical observable is attached to it.

## C.6 Venturi falsification gate [H]

Appendix B currently records:

Venturi mechanism = [H] TOKEN_VAZIO.

To promote the bridge, the next experiment must provide at minimum:

1. tube profile A(x) or r(x);
2. fluid density/viscosity and compressibility regime;
3. inlet/outlet boundary conditions;
4. measured P(x,t) and/or v(x,t);
5. uncertainty;
6. comparison against continuity/Bernoulli or compressible-flow equations;
7. falsifier.

The geometric throat alone is not evidence of a physical Venturi mechanism.

## C.7 Acoustic boundary [E/H]

Do not identify Bernoulli flow with the acoustic wave equation.

Linear acoustic pressure satisfies, under its own assumptions:

d²p/dt² = c_s² Laplacian(p).

Room/resonance observables require measured spectra, phase, damping and boundary conditions.

## C.8 Spiral / recurrence boundary [C/H]

Tribonacci may define a deterministic index path:

T_n = T_(n-1)+T_(n-2)+T_(n-3).

This does not establish that a physical toroidal vortex follows a Tribonacci spiral.

The proposed identity:

three matrices <-> three spirals <-> fourth emergent spiral

remains TOKEN_VAZIO until a bidirectional map/operator is specified.

## C.9 14 operational axes [C]

The visualization groups variables into fourteen analysis axes:

metric | angular | triangular | polynomial | signed/orientational |
curvilinear | rotational | fluidic | spiral/recurrence | focal |
geodesic | toroidal | matrix | transformational

This is a state-description taxonomy, not a 14-dimensional physical manifold claim.

## C.10 Candidate scalars [H]

sqrt(pi/5) and sqrt(pi/12) remain TOKEN_VAZIO_OPERATOR: their numeric existence is trivial; their scientific meaning is not.

## C.11 Visual dependency graph

hex projection
-> torus
-> meridian circle
-> quadratic/discriminant
-> 30° tangent
-> 15° refinement
-> Poincare section
-> geodesic f=2
-> 14-axis state map

meridian circle -. hypothesis .-> Venturi
Venturi -. requires data .-> falsifier

## C.12 Evidence state

| Object | State |
|---|---|
| 15° arithmetic grid | [E] PASS |
| cos30=sqrt3/2 | [E] PASS |
| f=2 counts 42/120/80 | [E] PASS |
| Euler 42-120+80=2 | [E] PASS |
| isosceles half-angle 30 -> equilateral | [E] PASS |
| 14-axis taxonomy | [C] MODEL |
| Venturi/vortex | [H] TOKEN_VAZIO |
| three matrices <-> three spirals | [H] TOKEN_VAZIO |
| physical/cosmological 14D | PROHIBITED_BY_SCOPE |

## C.13 Final invariant

validated geometry
-> declared visualization
-> typed hypothesis
-> measured experiment

No arrow may be skipped.
