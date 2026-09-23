# RLL — Rotation / Arc / Ellipse / Radial-Layer Bridge V1

**Date:** 2026-09-21  
**State:** `FORMAL_GEOMETRY_IMPORTED + COMPARISON_MODEL_DEFINED + PHYSICAL_GATE_OPEN`  
**claim_allowed:** `false` for atomic/electronic physical derivation.

## 0. Authority routing

Formal mathematics is governed by:

`rafaelmeloreisnovo/Matem-tica-/docs/formal/ROTATION_ARC_ELLIPSE_RADIAL_LAYERS_V1.md`

Research narrative is governed by:

`rafaelmeloreisnovo/papers/research_notes/2026-09-21_ROTATION_ARC_ELLIPSE_RADIAL_LAYERS_SESSION_SYNTHESIS.md`

RLL consumes only typed mathematical objects and defines the physics-facing comparison boundary.

```text
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
FORMAL_GEOMETRY != QUANTUM_PHYSICS
```

## 1. Imported exact geometry

For a circle of radius (R) and angle (	heta):

[
s=R	heta,
qquad
c=2Rsin(	heta/2),
]

[
d=Rcos(	heta/2),
qquad
f=R(1-cos(	heta/2)).
]

Sector, triangle and segment:

[
A_{sector}=rac12R^2	heta,
]

[
A_{triangle}=rac12R^2sin	heta,
]

[
A_{segment}=rac{R^2}{2}(	heta-sin	heta).
]

For regular (p)-gons:

[
s_p=2Rsin(pi/p),
qquad
r_p=Rcos(pi/p).
]

The half-step rotation is:

[
delta_p=pi/p,
]

which interlaces two (p)-vertex sets into (2p) equally spaced angular directions.

## 2. Square-rotation case

For square side (a):

[
R_{mid}=rac a2,
qquad
R_{vertex}=rac a{sqrt2}.
]

Continuous rotation of the square boundary generates the radial annulus:

[
rac a2le rlerac a{sqrt2}.
]

At half-step:

[
delta_4=pi/4.
]

The eight angular vertex positions form a regular octagonal carrier.

This is exact planar geometry. No physical field is inferred from it.

## 3. Elliptic projection layer

For a circular layer of radius (R), orthographically projected with inclination (i):

[
a=R,
qquad
b=R|cos i|.
]

Define projection anisotropy:

[
I_{proj}=rac ba=|cos i|.
]

Eccentricity:

[
e=|sin i|,
]

so:

[
I_{proj}^2+e^2=1.
]

The projected local arc metric is:

[
ds_e
=
Rsqrt{1-sin^2icos^2t},dt.
]

Define local arc distortion:

[
J(t,i)
=
rac{ds_e}{Rdt}
=
sqrt{1-sin^2icos^2t}.
]

For the complete ellipse:

[
C_e=4aE(e).
]

These objects may be used as measurement/projection operators in RLL, but not as evidence of orbital geometry.

## 4. Geometric radial-layer operator

For a chain of nested regular polygons/circles:

[
R_{k+1}
=
R_kcosrac{pi}{p_k}.
]

Hence:

[
R_m
=
R_0
prod_{k=0}^{m-1}
cosrac{pi}{p_k}.
]

For outward expansion:

[
R_{k+1}
=
R_ksecrac{pi}{p_k}.
]

Define the logarithmic geometric step:

[
L_G(p)
=
lnsecrac{pi}{p}.
]

This gives an additive representation of multiplicative radial expansion.

## 5. Atomic/electronic comparison boundary

The session proposed that the visual nested layers might be compared with electronic-shell structure. RLL records the comparison only after replacing classical orbit imagery with quantum-state quantities.

For a hydrogenic state:

[
psi_{nell m}(r,	heta,phi)
=
R_{nell}(r)Y_ell^m(	heta,phi).
]

The shell contains:

[
sum_{ell=0}^{n-1}(2ell+1)=n^2
]

spatial orbital states and, with two spin states:

[
N_n=2n^2.
]

Hydrogenic radial expectation:

[
langle rangle_{nell}
=
rac{a_0}{2Z}
left(3n^2-ell(ell+1)ight).
]

A separate semiclassical Bohr scale is:

[
r_n^{Bohr}=rac{a_0}{Z}n^2.
]

RLL MUST NOT collapse these objects:

```text
Bohr radius scale
!= general quantum radial expectation
!= probability-density isosurface
!= projected ellipse
!= geometric polygon layer
```

## 6. Geometry–quantum comparison metric

For the Bohr-scale ratio:

[
Q_n
=
rac{r_{n+1}^{Bohr}}{r_n^{Bohr}}
=
left(rac{n+1}{n}ight)^2.
]

For a regular-polygon radial expansion:

[
G_p=secrac{pi}{p}.
]

Define:

[
oxed{
M_{GQ}(n,p)
=
left|
ln G_p-ln Q_n
ight|
}
]

or equivalently:

[
M_{GQ}(n,p)
=
left|
lnsecrac{pi}{p}
-
2lnrac{n+1}{n}
ight|.
]

Interpretation:

- (M_{GQ}=0): exact equality of the two declared ratios;
- small (M_{GQ}): numerical ratio similarity;
- neither case establishes shared mechanism.

The continuous fitted polygon-order parameter is:

[
p_n^*
=
rac{pi}
{arccosleft(n^2/(n+1)^2ight)}.
]

If a regular polygon is required, use nearest integer (p) and record the residual (M_{GQ}).

## 7. New falsifiers

The bridge fails as a physical model if any of the following is asserted without added evidence:

1. electron probability density is identified with a rotating square/polygon boundary;
2. ellipse eccentricity is interpreted as orbital eccentricity for stationary quantum states;
3. a small (M_{GQ}) is promoted to atomic mechanism;
4. (7	o14), (sqrt3/2), or (3/2) is treated as a universal physical constant relation outside its stated geometry;
5. historical/biblical numeric patterns are used as physical evidence.

## 8. Test plan

Deterministic formal checks:

- verify arc/chord/sagitta identities;
- verify (E_{AC}(	heta)	o0) as (	heta	o0);
- verify polygon convergence (E_P,E_A,E_R	o0) as (p	oinfty);
- verify (I_{proj}^2+e^2=1);
- verify nested product-of-cosines recurrence;
- tabulate (M_{GQ}(n,p)) for bounded (n,p) as a null/comparison grid.

Empirical/physics gate remains separate:

```text
PHYSICAL_ELECTRON_SHELL_BRIDGE = TOKEN_VAZIO
```

until a quantum-mechanical observable, dataset, prediction and falsifier are explicitly defined.

## 9. R3

```text
F_ok =
formal geometry imported with typed projection and radial-scale operators;
quantum shell counting/radial quantities separated from classical orbit imagery;
dimensionless comparison metric M_GQ defined.

F_gap =
no physical mechanism/evidence linking polygon rotations to electronic structure;
no executed RLL numeric grid yet.

F_next =
implement bounded validator for exact identities and M_GQ null grid;
emit receipt;
keep claim_allowed=false for physical inference.
```


## 10. Reconciliation with existing RLL predecessor

Canonical readback found an earlier same-day RLL baseline at commit `b71eb98bf3da4857c95a2869d59fb2dca73c6fc3`, already binding rotation/arc/ellipse/electronic-layer comparison with `claim_allowed=false`.

This file is a supplemental successor. The incremental RLL contribution is:

- explicit hydrogenic factorization (psi_{nell m}=R_{nell}Y_ell^m);
- explicit (langle rangle_{nell}) dependence on both (n) and (ell);
- continuous diagnostic (p_n^*);
- absolute log mismatch (M_{GQ}) as a normalized successor to the prior signed/log-loss comparator.

No earlier physical gap is closed by this supplement.
