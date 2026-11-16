# RLL — Figure-Eight Toroidal Immersion × Unified Shape Cross V3

**Date:** 2026-09-24  
**Author:** RAFAEL MELO REIS  
**State:** \`FORMAL_IMMERSED_GEOMETRY + EXECUTABLE / claim_allowed=false\`

## 1. Why an immersion is the correct mathematical object

The requested geometry contains a toroidal flow that can "cross through itself" while retaining the same scale.

For a mathematical surface this can be represented exactly by an **immersion with self-intersection**. This is distinct from a physical claim that two impenetrable material bodies pass through one another.

The distinction is:

\`\`\`text
same coordinates in an immersed representation
!=
same material volume occupied by two impenetrable solids
\`\`\`

## 2. Continuous figure-eight torus map

Let

\[
(u,v)\in T^2,
\qquad
R>a>0.
\]

Use a translated Gerono figure-eight as the meridian:

\[
\rho(v)=R+a\cos v,
\]

\[
z(v)=\frac{a}{2}\sin(2v).
\]

Sweep the meridian around the azimuth \(u\):

\[
\boxed{
F(u,v)=
\left(
\rho(v)\cos u,\,
\rho(v)\sin u,\,
\frac a2\sin2v
\right).
}
\]

This is a continuous periodic map

\[
F:T^2\rightarrow\mathbb R^3.
\]

It is not globally injective.

## 3. Exact self-intersection

At

\[
v_1=\frac{\pi}{2},
\qquad
v_2=\frac{3\pi}{2},
\]

we have

\[
\cos v_1=\cos v_2=0,
\qquad
\sin2v_1=\sin2v_2=0.
\]

Therefore

\[
\boxed{
F(u,\pi/2)
=
F(u,3\pi/2)
=
(R\cos u,R\sin u,0).
}
\]

The two different torus parameters map to the same spatial point.

As \(u\) varies, the self-intersection is a circle of radius \(R\).

This closes the previously open object as:

\`\`\`text
CONTINUOUS_TORUS_TO_FIGURE8_IMMERSION = PASS_FORMAL
\`\`\`

while keeping:

\`\`\`text
PHYSICAL_MATERIAL_INTERPENETRATION = NOT_CLAIMED
\`\`\`

## 4. The two sheets cross at exactly 90 degrees

Differentiate with respect to the meridian coordinate \(v\):

\[
\partial_vF
=
\left(
-a\sin v\cos u,\,
-a\sin v\sin u,\,
a\cos2v
\right).
\]

At the two preimages of the double point:

\[
t_1=
\partial_vF(u,\pi/2)
=
(-a\cos u,-a\sin u,-a),
\]

\[
t_2=
\partial_vF(u,3\pi/2)
=
(a\cos u,a\sin u,-a).
\]

Their dot product is

\[
t_1\cdot t_2
=
-a^2(\cos^2u+\sin^2u)+a^2
=
0.
\]

Thus:

\[
\boxed{
t_1\perp t_2.
}
\]

The two sheets meet in an exact right-angle cross.

This is not inserted as a chosen square. It is derived from the figure-eight immersion.

## 5. Figure-eight -> square cross -> four equilateral triangles

Each tangent **line** has two orientations. Two orthogonal lines therefore give four rays spaced by

\[
90^\circ.
\]

That is the local square/cross structure.

For each ray direction \(\alpha_j\), apply the existing pulse:

\[
\alpha_j-\frac{\pi}{6},
\qquad
\alpha_j+\frac{\pi}{6}.
\]

The two endpoints and the common crossing centre form:

\[
|OP_j^-|=|OP_j^+|=S,
\]

and

\[
|P_j^-P_j^+|
=
2S\sin30^\circ
=
S.
\]

Therefore:

\[
\boxed{
\text{figure-eight sheet crossing}
\rightarrow
90^\circ\text{ cross}
\rightarrow
4\times\triangle_{\rm equilateral}.
}
\]

This is now an explicit relation rather than a visual assumption.

## 6. Relation to the complete shape family

The local cross is a bridge, not a collapse of objects.

The typed family remains:

\[
\{
\triangle,\,
\square,\,
S^1,\,
\text{cube},\,
\text{tetrahedron},\,
\text{square pyramid},\,
\text{bipyramid},\,
S^2,\,
T^2
\}.
\]

The current common radial ruler is \(S\).

The main routes are:

\`\`\`text
triangle -> tetrahedron
square -> cube
square cross -> 4 equilateral pulse sectors
circle x circle -> torus
torus -> figure-eight immersion
cube/bipyramid -> radial sphere projection
torus states -> geodesic sphere f=2
sphere/toroidal frames -> transported shape clouds
\`\`\`

## 7. "One goes through another of the same size"

Three cases are now typed.

### A — Parametric sheet crossing

At the figure-eight double point:

\[
F(u,\pi/2)=F(u,3\pi/2).
\]

Two distinct parameter sheets pass through the same spatial location.

State:

\`\`\`text
PASS_FORMAL_IMMERSION
\`\`\`

### B — Geometric shell / field overlay

Two represented shells or fields may overlap while preserving their scale.

State:

\`\`\`text
MODEL_ALLOWED
\`\`\`

### C — Impenetrable material solids

Equal rigid spheres of radius \(s\) require centre separation

\[
d\ge2s
\]

to avoid overlap.

State:

\`\`\`text
NO_COLLISION_PASSAGE_WHEN_d<2s
\`\`\`

Thus the geometry keeps the user's "passing through" operation while preventing a category error between manifold representation and rigid-body physics.

## 8. Executable implementation

Functions added:

\`\`\`text
figure8_torus_immersion
figure8_double_point
figure8_sheet_tangent_cross
figure8_cross_equilateral_bridge
\`\`\`

Tests assert:

\`\`\`text
two distinct v values -> same double point
sheet tangent dot product = 0
sheet crossing angle = 90 degrees
local cross -> four exact equilateral triangles
physical_interpenetration_claim = false
\`\`\`

## 9. Current closure matrix

\`\`\`text
FULL_SHAPE_RELATIONAL_MATRIX             = IMPLEMENTED
COMMON_RADIAL_ENVELOPE                   = PASS_FORMAL
FOUR_EQUILATERAL_CROSS_FOLD              = PASS_FORMAL
CONTINUOUS_TORUS_TO_FIGURE8_IMMERSION    = PASS_FORMAL
FIGURE8_DOUBLE_POINT                     = PASS_FORMAL
FIGURE8_SHEET_CROSS_90_DEG               = PASS_FORMAL
FIGURE8_CROSS_TO_4_EQUILATERALS          = PASS_FORMAL_LOCAL
144_TO_42_STABILITY_MAP                  = IMPLEMENTED_REFERENCE
PHYSICAL_RIGID_INTERPENETRATION           = NOT_CLAIMED
GEOMETRY_TO_B7_CHANNEL_MAP               = TOKEN_VAZIO
COSMOLOGICAL_CAUSAL_BINDING              = TOKEN_VAZIO
\`\`\`

## R3

\`\`\`text
F_ok =
full geometry family
+ common measure
+ continuous figure-eight torus immersion
+ exact self-intersection
+ exact 90-degree sheet cross
+ local square-cross -> four equilaterals
+ 144->42 HETE concentration

F_gap =
exact-head CI for V3
+ transport of cube/pyramid local frames on the immersed surface
+ B7 seven-channel construction
+ physical observable bridge

F_next =
close V3 exact-head;
then attach a moving orthonormal frame to F(u,v)
and transport triangle/square/cube/pyramid/sphere representatives through
both sheets while measuring metric distortion, orientation reversal,
self-intersection and HETE stability.
\`\`\`
