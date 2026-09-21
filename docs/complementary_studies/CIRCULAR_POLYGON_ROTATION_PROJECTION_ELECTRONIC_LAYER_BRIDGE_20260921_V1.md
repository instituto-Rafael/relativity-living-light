# RLL — Circular/Polygon Rotation × Elliptic Projection × Electronic-Layer Bridge V1

**Date:** 2026-09-21  
**Role:** governed integration/falsification bridge.  
**Mathematical authority:** `rafaelmeloreisnovo/Matem-tica-/docs/formal/CIRCULAR_POLYGON_ROTATION_PROJECTION_LAYER_GEOMETRY_V1.md`  
**Paper projection:** `rafaelmeloreisnovo/papers/research_notes/2026-09-21_CIRCULAR_POLYGON_ROTATION_PROJECTION_LAYER_GEOMETRY_V1.md`  
**State:** `FORMAL_BRIDGE / IMPLEMENTATION_NOT_RUN / claim_allowed=false`.

## 1. Exact geometry admitted into RLL

For radius (R) and central angle (\theta):
[
s=R\theta,quad
c=2R\sin(\theta/2),quad
d=R\cos(\theta/2),quad
f=R(1-\cos(\theta/2)).
]

For regular (n)-gon:
[
s_n=2R\sin(\pi/n),
quad
r_n=R\cos(\pi/n),
quad
\delta_n=\pi/n.
]

Half-step vertex operator:
[
\boxed{V(P_n)\cup V(R_{\pi/n}P_n)=V(P_{2n})}.
]

Nested radius:
[
\boxed{R_m=R_0\prod_k\cos(\pi/n_k)}.
]

## 2. Square rotational sweep

For side (a):
[
R_i=a/2,qquad R_o=a/\sqrt2.
]

Rotating the entire boundary through all angles generates:
[
\boxed{R_i\le r\le R_o}.
]

Rotating the filled square generates:
[
\boxed{0\le r\le R_o}.
]

The all-angle common core is:
[
\boxed{0\le r\le R_i}.
]

At the 45° half-step:
[
c_{45}=R\sqrt{2-\sqrt2},
quad
d_{45}=\frac R2\sqrt{2+\sqrt2}.
]

## 3. sqrt(3)/2 and 3/2 namespace

Preserve the existing RLL `sqrt3_2` kernel:

[
h_a/a=\sqrt3/2.
]

For an equilateral triangle inscribed in circumradius (R):
[
h_a=(3/2)R,
quad
r_{in}=R/2,
quad
r_{in}:R:h_a=1:2:3.
]

These ratios are exact geometry, not evidence weights or cosmological/atomic constants.

## 4. Circle-to-ellipse projection gate

Under orthographic tilt (i):
[
a_e=R,qquad b_e=R|\cos i|,
]
[
e=|\sin i|,
qquad
e^2+(b_e/a_e)^2=1,
]
[
A_e/A_c=|\cos i|.
]

Projected arc differential:
[
ds_e=R\sqrt{1-\sin^2 i\cos^2t}\,dt.
]

This is a projection model. Perspective/camera models require a separate transform.

## 5. Electronic-layer comparison: fail-closed

The geometric layer chain may be compared to an external scale law, but not identified with it.

Project-side expansion:
[
g_k=\sec(\pi/p_k).
]

Simple hydrogenic Bohr-scale comparator:
[
q_n=((n+1)/n)^2.
]

Mismatch:
[
\boxed{\varepsilon_{k,n}=\ln g_k-\ln q_n}.
]

Finite loss:
[
\boxed{
L_{GQ}=\sum_jw_j[
\ln(G_{j+1}/G_j)-2\ln((n_j+1)/n_j)
]^2}.
]

Gate:
[
L_{GQ}\text{ small}
\not\Rightarrow
\text{atomic mechanism}.
]

Modern orbitals are quantum distributions; (n,l,m), Hamiltonian/eigenstate assumptions, (Z), observables and empirical data are required before any physical claim.

## 6. Integration status

`EXACT_MATH`: PASS by derivation for the identities listed above.  
`REPO_FORMALIZATION`: IMPLEMENTED_UNTESTED as this document and cross-repo sources.  
`SYMBOLIC/NUMERIC_TESTS`: NOT_RUN for this new package.  
`ATOMIC_BINDING`: TOKEN_VAZIO.  
`NOVELTY`: PRIOR_ART_REQUIRED.  
`claim_allowed`: false outside exact mathematical statements.

## 7. Proposed RLL test surface

Deterministic tests should check:

1. (f/(c/2)=\tan(\theta/4)) over nonsingular angles;
2. square boundary-sweep radial interval ([a/2,a/\sqrt2]);
3. (n\to2n) interlaced vertex angles for (n=3,4,5,7,8);
4. nested product against iterative application;
5. ellipse axis/eccentricity/area identities;
6. (L_{GQ}) only as a numerical comparator with a negative control and explicit mapping.

No test result may be used to promote an atomic/cosmological causal claim without a separate evidence gate.

## R3

**F_ok:** formal cross-repository bridge created; exact geometry is typed separately from physical interpretation.

**F_gap:** tests are not yet executed; atomic data/model binding and novelty review are open.

**F_next:** add a deterministic test module and receipt; only then promote `IMPLEMENTED_UNTESTED` to a tested state.
