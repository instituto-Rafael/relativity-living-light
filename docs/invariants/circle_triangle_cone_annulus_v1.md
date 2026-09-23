# RLL — Circle / Triangle / Cone / Annulus Geometry V1

**Date:** 2026-09-21  
**Author:** RAFAEL MELO REIS  
**State:** \`FORMALIZED_EXACT_GEOMETRY / COSMOLOGY_BINDING_BLOCKED\`

## 1. Source idea

A circle can be nested inside a triangle or polygon, and a triangle can be rotated around an axis to generate a surface/solid of revolution. Nested radii generate circular crowns (annuli), and nested similar cones generate conical shells/frusta.

This document formalizes that geometry before any cosmological interpretation.

## 2. Equilateral triangle -> right triangle -> cone

For an equilateral triangle of side \(a\),

\[
h=\frac{\sqrt3}{2}a.
\]

Cutting along the altitude gives a \(30^\circ-60^\circ-90^\circ\) triangle with:

\[
r_b=\frac a2,\qquad h=\frac{\sqrt3}{2}a,\qquad \ell=a.
\]

Rotate this right triangle about the altitude. The result is a right circular cone:

\[
\boxed{r_b=\frac a2},
\qquad
\boxed{h=\frac{\sqrt3}{2}a},
\qquad
\boxed{\ell=a}.
\]

Its half-angle is

\[
\boxed{\alpha=30^\circ},
\]

because

\[
\sin\alpha=\frac{r_b}{\ell}=\frac12,
\qquad
\cos\alpha=\frac{h}{\ell}=\frac{\sqrt3}{2},
\qquad
\tan\alpha=\frac{r_b}{h}=\frac1{\sqrt3}.
\]

Surface and volume:

\[
A_{\rm lateral}=\pi r_b\ell=\frac{\pi a^2}{2},
\]

\[
A_{\rm base}=\pi r_b^2=\frac{\pi a^2}{4},
\]

\[
V=\frac13\pi r_b^2h
=\boxed{\frac{\sqrt3\pi}{24}a^3}.
\]

## 3. Incircle and circumcircle of the source equilateral triangle

\[
r_{\triangle}=\frac{\sqrt3}{6}a,
\qquad
R_{\triangle}=\frac{\sqrt3}{3}a,
\]

hence

\[
\boxed{R_{\triangle}=2r_{\triangle}}.
\]

These are not the same radius as the cone base \(a/2\); the three radii must remain typed separately.

## 4. Nested circles and circular crowns

For outer radius \(R\) and inner radius \(r\),

\[
\boxed{A_{\rm annulus}=\pi(R^2-r^2)}.
\]

With scale ratio

\[
\lambda=\frac rR,
\]

the normalized crown area is

\[
\boxed{\frac{A_{\rm annulus}}{\pi R^2}=1-\lambda^2}.
\]

If the nested polygon rule is

\[
R_{k+1}=R_k\cos\frac{\pi}{n_k},
\]

then the crown between consecutive radii has normalized area

\[
\boxed{
\frac{\Delta A_k}{\pi R_k^2}
=
1-\cos^2\frac{\pi}{n_k}
=
\sin^2\frac{\pi}{n_k}
}.
\]

Thus the earlier polygon core/annulus decomposition extends directly to nested circular crowns.

## 5. Nested similar cones

If cone \(k+1\) is similar to cone \(k\) by factor \(\lambda_k\),

\[
r_{k+1}=\lambda_k r_k,
\qquad
h_{k+1}=\lambda_k h_k,
\qquad
\ell_{k+1}=\lambda_k \ell_k.
\]

Then

\[
\frac{A_{k+1}}{A_k}=\lambda_k^2,
\qquad
\boxed{\frac{V_{k+1}}{V_k}=\lambda_k^3}.
\]

With

\[
\lambda_k=\cos\frac{\pi}{n_k},
\]

\[
\boxed{
\frac{V_m}{V_0}
=
\prod_k\cos^3\frac{\pi}{n_k}
}.
\]

This is the 3D analogue of the 2D radius/area layer law.

## 6. Conical shell / frustum

For a frustum of height \(H\), outer radius \(R\), inner/top radius \(r\):

\[
\boxed{
V_{\rm frustum}
=
\frac{\pi H}{3}(R^2+Rr+r^2)
}.
\]

Slant length:

\[
s=\sqrt{H^2+(R-r)^2}.
\]

Lateral area:

\[
A_{\rm lat}=\pi(R+r)s.
\]

These give a precise way to represent the "difference between two cone proportions" rather than treating the gap visually.

## 7. Circle rotation boundary

Rotating a **circle in its own plane** does not create a cone; it remains the same circle.

A cone is generated when a line segment/right triangle is revolved about an axis in 3D.

Rotating a circle about:
- a diameter -> sphere surface/solid under disk revolution;
- an external coplanar axis -> torus under circle revolution;
- its center-normal axis -> the same circle/disk.

This distinction is a hard geometry gate.

## 8. Cosmology boundary

A Euclidean cone of revolution is not automatically a cosmological light cone.

Allowed bridge:

\[
\text{Euclidean cone/crown geometry}
\to
\text{diagnostic basis / visualization / transform family}.
\]

Separate relativistic object:

\[
\text{FLRW past light cone}
\]

which is defined by spacetime null geodesics and the cosmological metric.

No physical identification is promoted without a derivation.

## R3

**F_ok:** circles, triangular generators, cones, nested cones, annuli and frusta are now one exact dimensional hierarchy.

**F_gap:** no empirical cosmological mapping has been established.

**F_next:** test these normalized 2D/3D ratios as diagnostic coordinates against DESI/Pantheon+/LCDM/RLL distance curves, while keeping the light-cone distinction explicit.
