# RLL — Multilayer Circle–Polygon Geometry V1

**Date:** 2026-09-22  
**Author:** RAFAEL MELO REIS  
**State:** `FORMAL_MATHEMATICS + LOCAL_EXECUTION_PASS / provider_ci=NOT_RUN`  
**Claim boundary:** mathematical structure only; physical/cosmological binding remains `TOKEN_VAZIO_EVIDENCE`.

## 1. Purpose

This package turns the current geometry program into an executable contract. It treats circles, regular polygons, equilateral triangles, angular overlays, concentric layers, projections, symmetry, graph topology, spherical shells and a 3D octagonal-prism extension as typed mathematical scenarios.

The canonical parameterization is

[
v_{j,k}=R_jleft(
cosleft(phi_j+rac{2pi k}{n_j}ight),
sinleft(phi_j+rac{2pi k}{n_j}ight)
ight),
]

with layer radius

[
R_j=R_0lambda^j,qquad 0<lambda<1.
]

## 2. Executable contract

YAML:

`data/contracts/rll_multilayer_circle_polygon_geometry_v1.yml`

Validator:

`scripts/validate_multilayer_circle_polygon_geometry_v1.py`

Unit test:

`tests/test_multilayer_circle_polygon_geometry_v1.py`

Local result:

`results/RLL_MULTILAYER_CIRCLE_POLYGON_GEOMETRY_V1.json`

CI:

`.github/workflows/rll-multilayer-circle-polygon-geometry-v1.yml`

## 3. Scenario matrix

| ID | Domain | What is tested |
|---|---|---|
| S01 | regular polygons | central angle, side, apothem, perimeter, area |
| S02 | chords | chord classes and even-n diameter |
| S03 | equilateral triangle | height, area, circumradius, inradius, R=2r |
| S04 | circle/triangle ratios | in-/circumcircle area ratios |
| S05 | hexagon | six equilateral triangles exactly recover its area |
| S06 | concentric layers | geometric radii, annuli, geometric area series |
| S07 | radial projection | angle preservation and radius transfer |
| S08 | homothety | length and area scaling |
| S09 | rotation | norm and distance invariance |
| S10 | reflection | distance invariance and orientation reversal |
| S11 | circle inversion | radial product and involution |
| S12 | polygon→circle | monotone area/perimeter convergence |
| S13 | K8 | 28 segments, 49 intersections, 40/8/1, 57/136/81, 56/24, beta1=80 |
| S14 | triangle overlays | six 60° rotations→6 angular vertices; six 30° rotations→12 |
| S15 | Snell | classical formula and total-internal-reflection condition |
| S16 | 3D octagonal prism/K16 | 16 vertices, 120 edges, volume/surface/distance |
| S17 | spherical shell | radial shell projection, chord/arc, spherical excess |
| S18 | multilayer graph | vertex sum and all-to-all edge identity |
| S19 | indices | fill, polygonality, scale, chord, topology |
| S20 | D8 symmetry | group order and orbit-stabilizer identities |

## 4. Formula registry

The YAML carries 30 formulas. The central family includes

[
	heta_n=rac{2pi}{n},
qquad
s_n=2Rsinrac{pi}{n},
qquad
a_n=Rcosrac{pi}{n},
]

[
P_n=2nRsinrac{pi}{n},
qquad
A_n=rac n2R^2sinrac{2pi}{n},
]

and chord class

[
ell_{n,k}=2Rsinrac{kpi}{n}.
]

For an equilateral triangle of side (a),

[
h=rac{sqrt3}{2}a,qquad
A_	riangle=rac{sqrt3}{4}a^2,
]

[
R_	riangle=rac{a}{sqrt3},
qquad
r_	riangle=rac{a}{2sqrt3},
qquad
R_	riangle=2r_	riangle.
]

Area ratios:

[
rac{A_{m incircle}}{A_	riangle}
=rac{pi}{3sqrt3},
qquad
rac{A_{m circumcircle}}{A_	riangle}
=rac{4pi}{3sqrt3}.
]

## 5. Layers and transformations

Concentric layers:

[
R_j=R_0lambda^j.
]

Annulus:

[
A_{{m annulus},j}
=pi(R_j^2-R_{j+1}^2).
]

Geometric sum:

[
sum_{j=0}^{infty}pi R_0^2lambda^{2j}
=
rac{pi R_0^2}{1-lambda^2}.
]

Radial projection:

[
Pi_{a	o b}(z)=rac{R_b}{R_a}z.
]

Homothety:

[
H_mu(z)=mu z.
]

Rotation:

[
{m Rot}_	heta(z)=e^{i	heta}z.
]

Reflection:

[
{m Ref}_alpha(z)=e^{2ialpha}overline z.
]

Circle inversion:

[
{m Inv}_ho(z)=rac{ho^2}{overline z}.
]

## 6. Angular superposition of triangles

An equilateral triangle has 120° rotational symmetry. Therefore the number of distinct projected angular vertices depends on the phase schedule rather than merely on the number of copies.

The executed fixtures reproduce:

[
6	imes{m rotations of} 60^circ
longrightarrow 6 {m distinct angular vertices},
]

while

[
6	imes{m rotations of} 30^circ
longrightarrow 12 {m distinct angular vertices}.
]

This gives a controlled mechanism for increasing angular sampling while preserving provenance of the generating triangle.

## 7. K8 no-loss bridge

The fully connected regular octagon reproduces

[
|E(K_8)|=28,
]

49 distinct proper internal intersections, concurrency

[
40 {m double}+8 {m triple}+1 {m quadruple},
]

and planarization

[
V=57,qquad E=136,qquad F=81.
]

Its bounded elementary faces are

[
56 {m triangles}+24 {m quadrilaterals}=80,
]

and its cycle rank is

[
eta_1=E-V+1=80.
]

As previously established, 56/24 is the elementary-face layer only, not the full family of composite closed forms.

## 8. 3D and spherical extensions

For two octagonal layers separated by height (h),

[
D_k=
sqrt{
left(2Rsinrac{kpi}{8}ight)^2+h^2
}.
]

Full pairwise connection of the 16 vertices yields

[
|E(K_{16})|=120=56+64.
]

For a spherical shell, angular separation (gamma) gives

[
c=2R_ssinrac{gamma}{2},
qquad
s=R_sgamma.
]

A spherical triangle obeys

[
A_s=R_s^2(A+B+C-pi).
]

## 9. Classical optics boundary

Snell's relation is included only as a classical formula-level branch:

[
n_1sinalpha=n_2sineta.
]

The executed suite checks an air→glass case and a total-internal-reflection condition. This does not establish that any geometric projection in the RLL corpus is physically caused by optical refraction.

## 10. Dimensionless indices

The YAML carries the index family

[
I_{m fill}=rac{A(S)}{pi R^2},
]

[
I_{m poly}(n)=rac{nsin(2pi/n)}{2pi},
]

[
I_{m scale}=rac{R_{j+1}}{R_j},
qquad
I_{m chord}=rac{ell_{n,k}}R,
]

[
chi=C-H.
]

Symmetry is preserved by orbit and stabilizer rather than destructive deduplication.

## 11. Executed result

Local execution of the exact contract produced:

[
oxed{20 {m scenarios},quad120 {m tests},quad120 PASS,quad0 FAIL}.
]

The committed result is a local execution receipt. GitHub provider CI remains `NOT_RUN` until Actions runs the newly created workflow.

## 12. Falsifiers

The package fails if any declared standard identity or fixture does not reproduce within tolerance. In particular the K8 branch fails if it does not reproduce 49 intersections, 40/8/1 concurrency, 57/136/81 planarization, 56/24 elementary faces, or cycle rank 80.

Physical/cosmological interpretation is not tested by this mathematical suite and therefore remains outside claim scope.

## R3

**F_ok:** one YAML now routes 20 mathematical situations into one reproducible validator and CI contract.  
**F_gap:** exhaustive generative enumeration of arbitrary layer/order/phase combinations and their simple-cycle/D8 orbit ledgers remains open.  
**F_next:** turn generated forms into streaming append-only records with parameters, invariants, topology, symmetry and rollback refs.
