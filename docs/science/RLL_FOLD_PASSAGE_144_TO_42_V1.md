# RLL — Fold / Passage / 144→42 V1

**Date:** 2026-09-24  
**State:** `IMPLEMENTED_EXACT_HEAD_CI_PENDING`  
**claim_allowed:** `false`

## 1. Fold/twist operator

The triangular torus authority already supplies a 60-degree rhombus fundamental domain:

[
P_{60}=Delta_+cupDelta_-.
]

V1 uses two congruent copies of (P_{60}), joined at one vertex, to create a discrete bow-tie / figure-eight cell complex. Each rhombus is cut along its equilateral diagonal, so the complex contains exactly four triangular cells.

A rigid 3D twist is then applied as opposite x-axis rotations (+phi) and (-phi) to the two copies.

The verifier measures the three side lengths of every triangle after the twist.

Expected invariant:

[
a_i=b_i=c_i=s,qquad i=1,ldots,4.
]

The intrinsic 3D triangles remain equilateral under the rigid fold. Their orthogonal (xy) projection is not silently assumed to remain equilateral when (phi
e0).

Boundary:

```text
four intrinsic equilateral cells = testable geometric consequence of the cut/fold construction
smooth T2 homeomorphic to figure-eight = false / not claimed
projected four equilaterals after nonzero twist = must be measured, not assumed
```

## 2. Sphere through the torus hole

For a standard solid torus with major radius (R) and tube radius (r), let a rigid sphere of radius (s) move along the symmetry axis.

The distance from the moving sphere centre at axial coordinate (z) to the torus centre-circle is

[
d(z)=sqrt{R^2+z^2}.
]

Avoiding intersection of the sphere and the torus tube requires

[
d(z)ge r+s.
]

Since the minimum occurs at (z=0), the complete axial passage gate is exactly

[
oxed{Rge r+s}.
]

For the author's same-scale case (s=r):

[
oxed{Rge2r}.
]

Therefore:

```text
R > 2r  -> PASS_WITH_CLEARANCE
R = 2r  -> PASS_TANGENT_LIMIT
R < 2r  -> BLOCKED_INTERSECTION
```

This is ordinary Euclidean rigid-body geometry. It does not imply matter interpenetration, wormholes or a spacetime mechanism.

## 3. 144 torus states → 42 geodesic vertices

The source matrix remains:

[
3 {m phases}	imes2 {m chiralities}	imes24 {m steps}=144.
]

Each torus cell is radially projected to the enclosing sphere (S=R+r), then assigned to the nearest one of the 42 f=2 icosphere vertices by spherical geodesic distance.

The HETE stability label is retained from the original torus cell:

[
{m source torus cell}
	o
{m sphere projection}
	o
{m nearest vertex}
	o
{m aggregate}.
]

Stability is **not recomputed from the vertex**.

## 4. Independent arithmetic replay for the canonical test scale

For the versioned test geometry

[
R=2,qquad r=1,qquad S=3,
]

an independent in-session replay of the committed formulas produced:

```text
source states             = 144
assigned states           = 144
active f=2 vertices       = 22 / 42
HETE stable states        = 126
HETE unstable states      = 18
stable fraction           = 126/144 = 0.875
```

Highest-occupancy all-stable vertices in that replay:

```text
vertex 0 : 12/12 stable
vertex 2 : 12/12 stable
vertex 17:  9/9 stable
vertex 15:  8/8 stable
vertex 34:  7/7 stable
```

Mixed vertices:

```text
vertex 41: 12 total, 6 stable, 6 unstable
vertex 32:  6 total, 3 stable, 3 unstable
vertex 40:  6 total, 3 stable, 3 unstable
vertex 23:  6 total, 3 stable, 3 unstable
vertex 30:  6 total, 3 stable, 3 unstable
```

This replay is a deterministic arithmetic cross-check of the formulas, not yet the exact-head GitHub Actions receipt.

## 5. Shape provenance

Every aggregate keeps the PG-Ω7 family in scope:

[
{I,S^1,Q,Delta_+,Delta_-,T^2,S^2,C,B}.
]

Thus a future observation can be traced through its generating square/triangle/circle/cube/pyramid/sphere/torus relations rather than being reduced to a scalar vertex score.

## R3

```text
F_ok =
fold/twist operator implemented
+ four intrinsic equilateral cells explicitly verified by side lengths
+ exact axial sphere-through-torus gate R>=r+s
+ same-scale gate R>=2r
+ deterministic 144-to-42 concentration operator
+ independent arithmetic replay conserves all 144 states

F_gap =
exact-head CI
+ smooth torus->figure-eight map beyond the cut/fold cell model
+ physical vortex/flow dynamics
+ observational strong-gravity binding

F_next =
close exact-head CI;
if PASS, promote this geometry receipt from local replay to repository-executed evidence;
then compare the stable/unstable geodesic regions against one standard strong-gravity observable without changing the GR/plasma baseline.
```
