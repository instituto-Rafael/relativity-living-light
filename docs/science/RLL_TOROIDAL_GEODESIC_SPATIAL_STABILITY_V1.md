# RLL — Toroidal Geodesic Spatial Stability V1

**State:** geometry-first implementation / claim_allowed=false  
**Date:** 2026-09-24  
**Author:** Rafael Melo Reis

## Correction of route

The primary object is not a free-parameter dispersion model.

The route is:

```text
geometry of spatial points
-> torus surface
-> +/-30 degree mouth gate
-> 3 up + 3 down toroidal branches
-> Poincare section/return
-> geodesic-sphere projection
-> quadratic fixed points
-> local stability
-> spatial dispersion of stability
```

Only after this geometry is executed may an observational RLL layer ask whether measured data occupy the same structure.

## 1. Exact 30-degree gate

For the meridian circle of the torus, centre `C=(R,0)`, take two points at `+30 deg` and `-30 deg` from one radial median.

Their radial lengths are `r`, and the base is

```text
2 r sin(30 deg) = r.
```

Hence the three sides are equal. The altitude is

```text
h = r cos(30 deg) = (sqrt(3)/2) r.
```

This is the exact isosceles-to-equilateral gate already present in the PBIP authority.

## 2. The two parallel lines and the empty gap

The torus meridian is

```text
(rho-R)^2 + z^2 = r^2.
```

For line family

```text
z = m rho + b
m = +/- tan(30 deg),
```

Bhaskara gives tangency when

```text
b = -mR +/- r sqrt(1+m^2).
```

The perpendicular distance between the two parallel tangents is therefore

```text
|Delta b|/sqrt(1+m^2) = 2r.
```

So the "empty interval" between the two parallel tangent gates is not assigned arbitrarily: in the meridian section it is exactly the torus tube diameter.

The midline is

```text
b_mid = -mR,
```

equidistant from the two tangents.

## 3. Derived Bhaskara mouths

A symmetric quadratic mouth can be fixed without a free fit by requiring:

1. symmetry about `z=0`;
2. passage through the torus boundary at `z=+/-r/2`;
3. local angle `dz/drho=+/-tan(30 deg)`.

The two mirrored solutions are

```text
rho_out(z) = R + sqrt(3) r/4 + (sqrt(3)/r) z^2

rho_in(z)  = R - sqrt(3) r/4 - (sqrt(3)/r) z^2.
```

Their vertices are mirrored around `rho=R`.

They are a **derived geometric model**. They are not yet a physical vortex throat.

## 4. Three ascending and three descending branches

The existing torus Poincare paper already gives the discrete flow:

```text
Delta u = 30 deg
Delta v = 45 deg
period = lcm(12,8) = 24
first u-section return = 12 steps
P(v) = v + pi mod 2pi
P^2 = id.
```

V1 duplicates this flow in three phase classes separated by `120 deg` and in two chiralities `+/-`.

Therefore:

```text
3 phases x 2 chiralities = 6 branches
6 branches x 24 points = 144 torus-surface cells.
```

The number 144 here is a derived matrix cardinality only.

The historical contraction factor is retained as a non-causal cell weight:

```text
q = cos(30 deg) = sqrt(3)/2
w_n = q^n.
```

It does not decide stability by itself.

## 5. Spatial stability: the author's HETE rule

The current session rule says `sin(30 deg)` is the entry pulse.

We therefore define the geometry-only binding

```text
c(u,v)
 = sin(30 deg)
   * (R + r cos(v))/(R+r)
   * exp(i u).
```

There is no fitted `kappa` in this V1.

For

```text
f_c(z)=z^2+c,
```

the fixed points satisfy

```text
z^2-z+c=0
D=1-4c
z_+/-=(1 +/- sqrt(D))/2.
```

The HETE stability test is then used unchanged:

```text
stable(point) <=> min(|2 z_+|, |2 z_-|) < 1.
```

Thus the spatial point generates `c`; Bhaskara generates the fixed points; the derivative of the quadratic map determines stability.

This is the requested direction:

```text
POINT -> GEOMETRY -> BHASKARA -> STABILITY
```

not

```text
chosen number -> fitted parameter -> preferred result.
```

## 6. Sphere geodesic around the torus

The minimal origin-centred sphere enclosing the standard torus has radius

```text
S = R+r.
```

Each torus cell is projected radially:

```text
Pi_S(X) = S X/||X||.
```

The f=2 icosphere supplies the spatial lattice

```text
V=42
E=120
F=80.
```

The implementation retains:

- 12 base icosahedron vertices;
- 30 normalized edge-midpoint vertices;
- 20 normalized face-centres as median intersections;
- six cardinal-axis points as explicit 90-degree landmarks.

A projected torus cell can therefore be related to a geodesic vertex, a median-intersection landmark, or a 90-degree axis by geodesic distance rather than by visual placement.

## 7. Extending a line to the sphere

For

```text
x(t)=x0+t d
```

against `||x||=S`, Bhaskara is applied to

```text
|d|^2 t^2 + 2(x0.d)t + (|x0|^2-S^2)=0.
```

The discriminant distinguishes two impacts, tangency, or no real impact.

At an impact `p`, with `n=p/S`, the reflected direction is

```text
d' = d - 2(d.n)n.
```

That is the precise operator for the "rebatida para dentro" described in the geometry.

## 8. Arbitrarily fine angular seeds

For a central opening `theta`:

```text
q(theta)=R sin(theta/2)
d(theta)=R cos(theta/2)
q^2+d^2=R^2.
```

The cathetus-difference diagnostic is

```text
delta_cat(theta)=|d(theta)-q(theta)|.
```

A seed may be one degree, one arcminute or one arcsecond. Its exact complementary routes are

```text
C60(theta)=60 deg-theta
C90(theta)=90 deg-theta.
```

No discrete angle is declared physically special merely because it closes a triangle.

## 9. Poincare 7D

The private Papers repository contains a distinct `B^7` construction.

That paper itself requires:

```text
Poincare return map != Poincare ball B7.
```

Its canonical lift needs an explicit `1+7` input convention. A 3D torus point does not automatically provide seven physical channels.

Therefore V1 uses the **Poincare return map** in the torus dynamics and preserves

```text
GEOMETRY_TO_B7_CHANNEL_MAP = TOKEN_VAZIO.
```

A later V2 can close it by declaring seven source-bound geometric observables before the hyperbolic lift.

## 10. Figure-eight / four-triangle fold

The session proposes a torus/crown fold into a figure-eight whose overlap yields four equilateral triangles.

The current source set does not yet contain one canonical fold operator that proves this construction. It is therefore preserved as:

```text
TORUS_TO_FIGURE8_FOLD_OPERATOR = TOKEN_VAZIO
FOUR_EQUILATERAL_TRIANGLES_FROM_FOLD = TOKEN_VAZIO
```

The correct next move is not to draw the answer into existence. It is to declare the fold map and then test all side lengths and angles.

## 11. Cultural/calendar imagery

Calendar/mandala imagery can remain a visualization/index layer. It is not used as evidence for the geometry or stability equations.

## Implementation

```text
rx/toroidal_geodesic_stability.py
tests/test_toroidal_geodesic_stability.py
data/governance/RLL_TOROIDAL_GEODESIC_STABILITY_GEOMETRY_V1.json
```

## R3

```text
F_ok =
geometry-first chain
+ exact +/-30 gate
+ exact 2r parallel gap
+ derived mirrored quadratic mouths
+ 6x24 torus spatial matrix
+ Poincare return
+ f2 icosphere projection
+ HETE fixed-point stability

F_gap =
exact-head CI
+ canonical figure-eight fold
+ typed 3D/geometry -> B7 channel map
+ physical vortex field
+ observational binding

F_next =
run/close exact-head CI;
then emit a deterministic 144-cell -> 42-vertex geometry/stability receipt;
then test one strong-gravity observation without altering its standard GR/plasma baseline.
```
