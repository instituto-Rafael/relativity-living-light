# RLL — Unified Shape Matrix × Toroidal Transport V2

**Date:** 2026-09-24  
**Author:** RAFAEL MELO REIS  
**State:** \`GEOMETRY_PRIMARY / EXECUTABLE / claim_allowed=false\`

## 1. Correction accepted

The toroidal stability route must retain the complete geometry family already present in the author's corpus:

\`\`\`text
triangle
square
circle
cube
tetrahedron / pyramid
bipyramid
sphere
torus
\`\`\`

The governing relation is not

\`\`\`text
all shapes are the same object
\`\`\`

but

\`\`\`text
all shapes may inhabit one typed relational matrix
while metric, topology, area, volume and incidence remain distinct.
\`\`\`

The formal predecessor is:

\`\`\`text
rafaelmeloreisnovo/papers:
docs/matematica/COMPLEXO_UNIFICADO_TORO_ESFERA_CUBO_BIPIRAMIDE_V1.md
\`\`\`

and the existing RLL executable predecessor is:

\`\`\`text
scripts/unified_geometry_system.py
\`\`\`

## 2. One common measure without collapsing the objects

V2 uses a common radial envelope \(S\).

- equilateral triangle: vertices on radius \(S\);
- square: vertices on radius \(S\);
- circle: radius \(S\);
- cube: vertices normalized to its circumsphere of radius \(S\);
- tetrahedron: vertices on radius \(S\);
- square pyramid: vertices normalized to the common circumsphere;
- triangular bipyramid: vertices on radius \(S\);
- sphere: radius \(S\);
- torus: \(R+r=S\).

Therefore:

\[
\boxed{
R_{\rm envelope}=S
}
\]

is a shared measuring ruler.

This does **not** imply equal areas, equal volumes or object identity.

## 3. Four-equilateral fold operator

The previous V1 preserved the "four equilateral triangles from the fold" as \`TOKEN_VAZIO\`.

The missing operator can now be stated explicitly using two already-authorized ingredients:

1. the square/cross supplies four axes

\[
\alpha_j=j\frac{\pi}{2},
\qquad
j=0,1,2,3;
\]

2. the toroidal pulse supplies the pair

\[
\alpha_j-\frac{\pi}{6},
\qquad
\alpha_j+\frac{\pi}{6}.
\]

For radius \(S\), define:

\[
P_j^-=
S(\cos(\alpha_j-\pi/6),\sin(\alpha_j-\pi/6)),
\]

\[
P_j^+=
S(\cos(\alpha_j+\pi/6),\sin(\alpha_j+\pi/6)).
\]

With common centre \(O\),

\[
|OP_j^-|=|OP_j^+|=S.
\]

The angular separation is \(60^\circ\), hence

\[
|P_j^-P_j^+|
=
2S\sin30^\circ
=
S.
\]

Thus, for every \(j\),

\[
\boxed{
|OP_j^-|
=
|OP_j^+|
=
|P_j^-P_j^+|
=
S
}
\]

and the operator produces exactly four equilateral triangles.

The implemented operator is named:

\`\`\`text
square_axis_cross_x_plusminus30_pulse
\`\`\`

This closes the **four-equilateral geometric subproblem**.

It does not yet prove:

\`\`\`text
physical torus -> literal figure-eight topology
\`\`\`

because a topological twist/fold of the full torus still requires an explicit surface map.

Therefore the new state is:

\`\`\`text
FOUR_EQUILATERAL_CROSS_FOLD = PASS_FORMAL
TORUS_TO_LITERAL_FIGURE8_SURFACE_MAP = TOKEN_VAZIO
\`\`\`

## 4. 2D -> 3D family

The same matrix preserves the prior routes:

\[
Q\times I \rightarrow \text{cube},
\]

\[
\triangle \rightarrow \text{tetrahedral/simplicial lift},
\]

\[
\text{square/cube or bipyramid}
\xrightarrow{\Pi_S}
S^2,
\]

and

\[
S^1\times S^1=T^2.
\]

A projection may preserve a declared invariant while changing other metrics.

Therefore:

\`\`\`text
same envelope != same shape
same projection target != same topology
same numeric radius != same volume
\`\`\`

## 5. "Passing through another of the same size"

The statement is now separated into two mathematically different cases.

### 5.1 Geometric shell / field / coordinate transport

A point cloud or shell can be transported by translation or a declared frame map while preserving every pairwise distance.

For a rigid translation:

\[
T_c(p)=p+c,
\]

\[
|T_c(p_i)-T_c(p_j)|
=
|p_i-p_j|.
\]

So a triangle, square, cube, pyramid, sphere shell or any other represented geometry can traverse the toroidal route without changing its scale.

This is the permitted meaning of:

\`\`\`text
same-size geometry passes through the same coordinate/field region.
\`\`\`

### 5.2 Impenetrable rigid physical solids

For two equal physical spheres of radius \(s\), with centre separation \(d\):

\[
d>2s \Rightarrow \text{disjoint},
\]

\[
d=2s \Rightarrow \text{externally tangent},
\]

\[
0<d<2s \Rightarrow \text{intersecting},
\]

\[
d=0 \Rightarrow \text{coincident}.
\]

Therefore two impenetrable rigid spheres of equal radius cannot literally pass through one another without an overlap/collision phase.

The executable contract records both statements simultaneously:

\`\`\`text
shell_or_field_overlay_allowed = true
impenetrable_rigid_pass_without_collision = condition(d >= 2s)
\`\`\`

This keeps the geometric flow usable without promoting it into unsupported material physics.

## 6. Toroidal carrier and same radial measure

The common carrier can use:

\[
R+r=S.
\]

In the default normalized fixture:

\[
R=\frac{2S}{3},
\qquad
r=\frac{S}{3}.
\]

The outer torus radius equals the same common envelope:

\[
R+r=S.
\]

This lets all shapes be compared against the same radial ruler while still preserving their distinct geometry.

## 7. 144 -> 42 projection executed as a deterministic map

The six toroidal branches remain:

\[
3\text{ phases}\times2\text{ chiralities}=6,
\]

with one Poincaré period:

\[
24\text{ steps}.
\]

Therefore:

\[
6\times24=144
\]

spatial cells.

Each cell is radially projected to the sphere \(S=R+r\), then assigned to the nearest one of the 42 vertices of the frequency-2 icosphere by great-circle distance.

For the fixed reference fixture

\[
R=2,\qquad r=1,\qquad S=3,
\]

the deterministic calculation gives:

\[
\boxed{
144\text{ cells}
\rightarrow
21\text{ occupied vertices of the available }42
}
\]

and the current HETE pointwise rule yields:

\[
\boxed{
126/144 = 0.875
}
\]

stable cells.

This is a property of this declared geometry/model fixture, not an observational cosmology result.

### Highest occupancy

The strongest occupancy sites are:

\`\`\`text
vertex 0  : 12 visits, 12 stable
vertex 2  : 12 visits, 12 stable
vertex 41 : 12 visits,  6 stable
vertex 15 :  9 visits,  9 stable
vertex 17 :  9 visits,  9 stable
\`\`\`

The result immediately distinguishes two concepts:

\`\`\`text
high occupancy != high stability concentration
\`\`\`

Vertex 41 receives the same highest occupancy as 0 and 2, but only 50% of its assigned cells are stable.

That is exactly the kind of geometric discrimination the route was intended to reveal.

## 8. New executable objects

\`\`\`text
rx/unified_shape_toroidal_transport.py
tests/test_unified_shape_toroidal_transport.py
results/geometry/rll_144_to_42_stability_concentration_v1.json
\`\`\`

The module tests:

- common radial envelope across the full shape family;
- four exact equilateral triangles from square-axis × ±30° pulse;
- rigid size preservation under transport;
- equal-sphere overlap versus rigid-body collision boundary;
- 144-to-42 geodesic assignment;
- stability concentration by geodesic vertex.

## 9. Epistemic boundary

\`\`\`text
PASS_FORMAL:
  common radial ruler
  four-equilateral cross-fold
  rigid translation size invariance
  sphere overlap classification
  144-to-42 nearest-geodesic map definition

MODEL_RESULT:
  21/42 vertices occupied in the R=2,r=1 fixture
  126/144 HETE-stable cells in that fixture

TOKEN_VAZIO:
  physical torus -> literal figure-eight surface evolution
  physical interpenetration mechanism for rigid matter
  geometry -> cosmological observable causal bridge
  geometry -> B7 seven-channel map
\`\`\`

## R3

\`\`\`text
F_ok =
CI V1 closed PASS
+ complete shape family restored
+ one common radial ruler without object collapse
+ four-equilateral operator proved
+ same-size transport boundary formalized
+ 144 -> 42 concentration calculated

F_gap =
literal torus-to-figure8 surface map
+ physical flow/interpenetration mechanism
+ B7 channel map
+ external observational binding

F_next =
run exact-head CI on this V2 delta;
then construct the explicit continuous torus-surface fold F:T2->R3
and compare its induced triangle/cube/pyramid/sphere invariants
against the current cross-fold baseline before touching cosmology.
\`\`\`
