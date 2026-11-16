# RLL — PG-Ω7 unified shape complex bridge V1

**Authority:** `rafaelmeloreisnovo/Matem-tica-/docs/PG_OMEGA7_COMPLEXO_UNIFICADO_TORO_ESFERA_CUBO_V1.md`  
**State:** `FORMAL_TYPED_COMPLEX`  
**claim_allowed:** `false`

This bridge prevents the toroidal stability work from reducing the author's geometry to the torus alone.

The primitive family is

[
\mathcal X=\{I,S^1,Q,\Delta_+,\Delta_-,T^2,S^2,C,B\}.
]

It therefore carries, together and with typed maps:

```text
interval -> circle
square -> torus by opposite-edge identification
60-degree rhombus = two equilateral triangles -> triangular-lattice torus
square x interval -> cube
cube -> sphere by radial projection
triangular bipyramid/pyramid pair -> sphere by radial projection
torus <-> sphere only through an explicit map, never by identity
```

The stability matrix must consequently expose one state as a **relational tuple**, not as a torus-only point:

[
\Omega(p)=
(Q,\Delta_+,\Delta_-,S^1,T^2,S^2,C,B;\,M^{(r)}).
]

The relation tensor (M^{(r)}) distinguishes incidence, product, quotient, projection, triangulation, symmetry, metric and provenance.

## Equal sphere / "one passes through another"

Two interpretations are kept separate.

### Mathematical volumes

For equal spheres of radius (r), centres separated by (d):

```text
d = 0    -> coincident
0<d<2r   -> overlapping/interpenetrating mathematical volumes
d = 2r   -> external tangency
d > 2r   -> disjoint
```

This is valid as geometry because mathematical volumes may overlap.

### Rigid passage

A closed sphere surface is not itself a hole. For a rigid sphere of radius (r) to cross a circular aperture of radius (a) without deformation, the size gate is

[
a\ge r.
]

Therefore the statement "one equal sphere passes through another equal sphere" is **not** promoted merely from overlap. It needs an explicit aperture/cut, deformation, quotient, or flow map.

```text
EQUAL_SPHERE_OVERLAP = FORMAL
RIGID_EQUAL_SPHERE_PASSAGE_WITHOUT_APERTURE = TOKEN_VAZIO
TOROIDAL_FLOW_PASSAGE_OPERATOR = TOKEN_VAZIO
```

This distinction lets the later toroidal-flow operator test the author's intended passage rather than assuming it.

## Updated execution order

```text
1. exact-head CI
2. unified PG-Ω7 shape state per spatial cell
3. explicit fold/twist operator
4. test four equilateral triangles
5. explicit sphere/toro passage operator
6. project 144 toroidal states to 42 f=2 geodesic vertices
7. measure HETE stability concentration by shape relation and geodesic region
```

The measurement stage must retain the generating shape route, so a stable point can be traced back to square/triangle/circle/cube/pyramid/sphere/torus relations rather than being reported as an untyped scalar.
