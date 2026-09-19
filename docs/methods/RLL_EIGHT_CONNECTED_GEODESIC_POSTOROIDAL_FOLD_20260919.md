# RLL — Eight-Connected Geodesic / Hexagram / Post-Toroidal Fold V1

Date: 2026-09-19
State: METHOD_CONTRACT / GEOMETRY_KERNEL
claim_allowed: false

## 0. Lineage

This note extends, without replacing:

- docs/science/RAFAELIA_CLASSICAL_MATH_FORMULA_AUDIT_20260808.md
- docs/science/MODULAR_FOLD_GAP_RULER_NUCLEAR_BRIDGE_20260902.md
- PapersPub/2026-08-29_RAFAELIAN_EXACT_RATIO_GEOMETRY_SESSION_FEEDBACK.md
- docs/methods/RLL_FORM_GENOME_DUAL_WATCHDOG_MANDALA_20260919.md

The current user construction is preserved as an authorial geometry program, then decomposed into exact mathematics, explicit assumptions, and TOKEN_VAZIO mappings.

## 1. Eight connected positions

A natural square-derived carrier has four angular positions and two position classes:

P8 = Z4 x {VERTEX, EDGE_MIDPOINT}

This gives eight addressable slots.

For a square with circumradius R:

V_q = R (cos(q*pi/2), sin(q*pi/2))

and the actual midpoint of the edge from V_q to V_(q+1) is:

M_q = (V_q + V_(q+1))/2

so |M_q| = R/sqrt(2).

This cleanly separates four outer vertex positions from four inner edge-midpoint positions.

The user's exact intended assignment of "two outside / one inside / height" is not forced:

EIGHT_POSITION_SEMANTICS = TOKEN_VAZIO_LAYOUT

The carrier is valid independently of that semantic assignment.

## 2. Square inverse/projection family

The square symmetry group D4 has 8 actions:

- 4 rotations;
- 4 reflections.

Reflections can use axes through opposite vertices or opposite edge midpoints.

D4 acts on the eight slots while preserving the class VERTEX versus EDGE_MIDPOINT.

This realizes the user's "rotate/invert edge/median/opposite vertex" request as a finite operator family.

Important boundary:

ROTATED_SQUARE != HEXAGRAM

A square transformation may feed another construction, but a Star of David / regular hexagram is not obtained merely by rotating a square.

## 3. Hexagram from two equilateral triangles

Use two equilateral triangles with the same center and circumradius R.

Upper triangle angles:
pi/2, pi/2 + 2*pi/3, pi/2 + 4*pi/3

Lower/inverted triangle angles:
pi/6, pi/6 + 2*pi/3, pi/6 + 4*pi/3

Their union gives the six outer vertices of a regular hexagram.

For each constituent equilateral triangle:

side L = sqrt(3) R

height h = sqrt(3)/2 * L.

The central regular hexagon has circumradius/side:

rho_hex = R/sqrt(3) = L/3.

Thus the exact sqrt(3)/2 geometry and the hexagram decomposition coexist without treating them as the same quantity.

## 4. 30-degree entry and the 15-degree branch

Exact:

sin(30 deg) = 1/2
cos(30 deg) = sqrt(3)/2
tan(30 deg) = 1/sqrt(3)

If a total relative torsion of 30 degrees is explicitly split symmetrically between two faces/branches, then each branch carries 15 degrees:

theta_plus = +15 deg
theta_minus = -15 deg

with exact values:

tan(15 deg) = 2 - sqrt(3)
sin(15 deg) = (sqrt(6)-sqrt(2))/4
cos(15 deg) = (sqrt(6)+sqrt(2))/4

This 15-degree result is valid only under the symmetric-split assumption:

SYMMETRIC_30_TO_15 = VALID_IF_ASSUMED

It is not inferred from an unspecified isosceles triangle.

## 5. Standard torus layer

For major radius R and tube radius r, R>r>0:

T(u,v) =
(
 (R+r cos v) cos u,
 (R+r cos v) sin u,
 r sin v
)

At a cross-sectional entry v=30 degrees:

radial_offset = r cos(30) = r sqrt(3)/2
vertical_offset = r sin(30) = r/2

This provides an exact location for a declared "30-degree torus entry".

Normalized local frame:

e_u = (-sin u, cos u, 0)

e_v = (-sin v cos u, -sin v sin u, cos v)

n   = ( cos v cos u,  cos v sin u, sin v)

The matrix Q=[e_u e_v n] provides the local orientation frame to attach a planar form to the torus tangent plane.

TANGENT_ATTACHMENT != EXACT_SURFACE_GEODESIC_ATTACHMENT

For exact on-surface placement, coordinates must be lifted through the torus parameter chart or exponential/geodesic machinery.

## 6. Triangle matrix attached to the torus

For equilateral side L, local planar coordinates may be:

p0=(-L/2,0,0)
p1=( L/2,0,0)
p2=(0,sqrt(3)L/2,0)

Tangent placement at (u0,v0):

X_i = T(u0,v0) + Q p_i

This is a tangent-plane construction.

A first-order surface lift uses:

u_i = u0 + x_i/(R+r cos v0)
v_i = v0 + y_i/r

then evaluates T(u_i,v_i).

The latter remains a chart approximation for finite L; geodesic distortion must be measured.

## 7. Poincare / gluing boundary

Two different established constructions must remain distinct.

### 7.1 Euclidean square edge identification

Identifying opposite edges of a square:

(0,y) ~ (1,y)
(x,0) ~ (x,1)

produces a 2-dimensional torus as a quotient surface.

### 7.2 Poincare disk

In the Poincare disk, hyperbolic geodesics are Euclidean diameters or circle arcs orthogonal to the unit-circle boundary.

A commonly used convention is:

ds^2 = 4(dx^2+dy^2)/(1-r^2)^2

(up to overall scale convention).

Therefore:

SQUARE_EDGE_GLUE -> TORUS
POINCARE_DISK -> HYPERBOLIC_METRIC/GEODESICS

They can participate in a common quotient/group-action program, but they are not the same construction.

## 8. Sphere and geodesic projection

For Euclidean sphere radius A:

S^2_A = {p in R3 : ||p||=A}.

Radial projection of nonzero x:

Pi_A(x)=A*x/||x||.

This preserves ray direction, not planar distance or geodesic distance.

Great-circle/geodesic distance:

d_S(p,q)=A arccos( (p dot q)/A^2 ).

Thus a planar hexagram can be projected onto a sphere and its edge lengths remeasured geodesically.

PLANAR_HEXAGRAM -> RADIAL_SPHERE_PROJECTION
does not imply
EDGE_LENGTH_PRESERVED.

## 9. Reflections at the sphere wall

A mathematically typed reflection through a plane through the sphere center with unit normal n is the Householder map:

H_n(x)=x-2(n dot x)n.

Repeated reflection generators produce an orbit:

O(x)={g x : g in <H_n1,...,H_nk>}.

This formalizes the user's idea that repeated internal reflections can turn a small set of triangle vertices into many derived vertices.

The number of unique vertices depends on the reflection group:
- finite group -> finite orbit;
- non-closed/unconstrained generators may generate many or infinitely many orbit points.

SPHERE_COMPRESSION alone does not automatically increase combinatorial vertex count; the increase comes from the declared reflection/folding operators.

## 10. Post-toroidal authorial deformation

"Post-toroidal" is treated as an authorial deformation class, not a standard named geometry.

One controlled family is:

T_post(u,v) =
(
 (R+rho(v) cos v) cos(u+tau(v)),
 (R+rho(v) cos v) sin(u+tau(v)),
 rho(v) sin v
)

with:
rho(v)>0,
rho(v+2*pi)=rho(v),
tau(v+2*pi)-tau(v)=2*pi*k or another explicitly closed winding condition.

If regularity/closure/no-self-intersection fail, the object must not be promoted as a torus.

## 11. Quadratic "mouth" profile / Bhaskara gate

A separate meridional radius profile can be defined:

rho(z)=a z^2+b z+c.

A desired mouth radius rho_* is reached where:

a z^2+b z+(c-rho_*)=0.

Quadratic formula:

z_+/- =
[-b +/- sqrt(b^2-4a(c-rho_*))]/(2a).

Existence of real crossings requires:

Delta = b^2-4a(c-rho_*) >= 0.

For mirror-symmetric upper/lower mouths, one convenient condition is b=0.

To impose local 30-degree wall slope:

rho'(z)=2az+b = +/- tan(30 deg)=+/-1/sqrt(3).

The coefficients a,b,c and target radius remain model parameters, not derived from the narrative:

POSTOROIDAL_QUADRATIC_COEFFICIENTS = TOKEN_VAZIO_PARAMETERS.

## 12. Curved abscissa / modular angular coordinate

For integer n and modulus m>0:

theta_m(n)=2*pi*(n mod m)/m.

This maps a linear/discrete index to a circular abscissa.

The family requested in the session:

M={1,2,3,5,7,10,14,35,50,70}.

Their full simultaneous zero-phase recurrence is controlled by:

LCM(M)=1050.

Therefore:

n=1050*k

gives theta_m(n)=0 for every m in M.

A smaller subset may synchronize earlier.

For arbitrary pairs (n,m) and (n',m') exact phase equality requires:

(n mod m)/m = (n' mod m')/m'  mod 1.

The engine tests normalized phase; it does not infer coincidence from visually related numbers.

## 13. Divisibility / angular families

Useful exact relations:

14=2*7
35=5*7
70=10*7
50=2*5^2

and:

lcm(7,10,14,35,50,70)=350
lcm(1,2,3,5,7,10,14,35,50,70)=1050.

This explains real recurrence structure without asserting a new physical angular law.

## 14. Negative-base / polynomial layer

A negative positional base -b, b>=2, is mathematically valid.

A digit string corresponds to polynomial evaluation:

N = sum_k d_k (-b)^k.

Multiplication can be performed as polynomial convolution followed by carry normalization in base -b.

This must remain distinct from:
- modular arithmetic;
- geometric area;
- quadratic equation solving.

A quadratic area/overlap condition may separately create:

a x^2+b x+c=0.

NEGATIVE_BASE * POLYNOMIAL_CONVOLUTION
does not by itself generate a missing geometric area.

## 15. Eight-connected to form-genome integration

The new form gene can add:

geometry_carrier:
  square_slot8
  hexagram6
  torus_uv
  sphere_xyz
  modular_phase

operators:
  D4_ROTATE
  D4_REFLECT
  HEXAGRAM_SUPERPOSE
  TORUS_ATTACH
  SPHERE_PROJECT
  HOUSEHOLDER_REFLECT
  POSTOROID_DEFORM
  MODULAR_CURVE
  NEGATIVE_BASE_REPRESENT

Every composition emits:
source,
parameters,
exact/symbolic form,
approximation metadata,
operator order,
watchdog receipt,
TOKEN_VAZIO fields.

## 16. Falsification / audit gates

A geometric candidate is blocked if:
- dimensions do not match;
- a projection is called an isometry without proof;
- a planar edge length is reused as spherical geodesic length without recomputation;
- torus closure/regularity is not checked;
- Poincare geometry is conflated with Euclidean edge gluing;
- an 8-to-42 mapping is invented;
- modular coincidence is declared without normalized-phase equality;
- post-toroidal coefficients are missing but numerical conclusions are asserted.

## 17. R3

F_ok:
- exact sqrt(3)/2, 30-degree and conditional 15-degree identities;
- square D4 family and eight-slot carrier;
- two-equilateral-triangle hexagram with central hexagon;
- standard torus parameterization and local frame;
- sphere radial projection and great-circle distance;
- modular phase and LCM=1050 recurrence;
- quadratic-profile gate and negative-base separation.

F_gap:
- exact semantic assignment of the eight user positions;
- coefficients of the post-toroidal mouth profile;
- explicit map from square branch to hexagram branch;
- any physical meaning for modular angular coincidences;
- 8-sector mandala to 42-state hyperforma mapping.

F_next:
implement exact property tests and a bounded composition sampler that keeps Euclidean, spherical, hyperbolic, toroidal and modular metrics typed separately.
