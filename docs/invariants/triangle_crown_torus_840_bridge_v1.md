# RLL — Triangle × Crown × Torus × 840 Bridge V1

**Date:** 2026-09-22  
**Author:** RAFAEL MELO REIS  
**State:** \`FORMAL_DERIVED_DELTA / CLAIM_BOUNDARY_ACTIVE\`  
**claim_allowed:** \`false\`

## 0. Predecessor boundary

This file is a **successor delta**, not a new origin.

Canonical RLL predecessors:
- \`docs/invariants/circle_triangle_cone_annulus_v1.md\`
- \`docs/invariants/geometric_weave_invariants_v1.md\`
- \`docs/invariants/sqrt3_2_kernel.md\`

Cross-repository mathematical predecessors:
- \`rafaelmeloreisnovo/Matem-tica-\`: PBIP / crown / toroidal formalizations
- \`rafaelmeloreisnovo/papers\`: crown-geodesic reflection, Poincaré torus mobile, radial 5–6–7–8 partition paper

The new delta is restricted to:
1. standard torus projection as an annulus and its area relation;
2. polygon-sweep annulus → toroidal-shell fraction;
3. hexagonal cross-section → torus volume approximation;
4. exact separation of parallel tangents in a torus meridian;
5. six planar sectors → three equal opposite-pair toroidal volumes;
6. common-phase \(5,6,7,8\) counts \(22/16/32\);
7. separation of two distinct period/order-840 constructions.

Rule:

\[
\text{EXACT GEOMETRY}
\neq
\text{GEOMETRIC MODEL}
\neq
\text{MODULAR ENCODING}
\neq
\text{PHYSICAL MECHANISM}.
\]

## 1. Equilateral kernel inside a torus section

RLL already has:

\[
h=\frac{\sqrt3}{2}.
\]

For the standard torus

\[
T(u,v)=
((R+r\cos v)\cos u,\,
(R+r\cos v)\sin u,\,
r\sin v),
\qquad R>r>0,
\]

the local tube-section coordinates at \(v=30^\circ\) are:

\[
r\cos30^\circ=\frac{\sqrt3}{2}r,
\qquad
r\sin30^\circ=\frac12r.
\]

Thus the same \(30^\circ\!-\!60^\circ\!-\!90^\circ\) kernel used by the equilateral triangle parameterizes a point of the circular torus section.

This is reuse of exact trigonometry, not the statement “triangle = torus”.

## 2. Six equilateral directions in the tube section

Define:

\[
v_k=\frac{k\pi}{3},
\qquad
k=0,\ldots,5.
\]

Then the meridional points are:

\[
(\rho_k,z_k)=
(R+r\cos v_k,\;r\sin v_k).
\]

Relative to the section center \((R,0)\), these are the vertices of a regular hexagon of circumradius \(r\).

Letting \(u\) sweep through \([0,2\pi)\) with \(v=v_k\) fixed produces six toroidal circles.

Therefore:

\[
\boxed{
\text{six section vertices}
\longrightarrow
\text{six toroidal circles}
}.
\]

## 3. Orthographic xy projection of the standard ring torus

The projected radial coordinate satisfies:

\[
R-r\le\rho\le R+r.
\]

Hence the projection is the annulus:

\[
\mathcal A_T
=
\{(\rho,\theta):R-r\le\rho\le R+r\}.
\]

Its area is:

\[
A_{\rm crown}
=
\pi[(R+r)^2-(R-r)^2]
=
\boxed{4\pi Rr}.
\]

The torus surface area is:

\[
A_T=4\pi^2Rr.
\]

Therefore:

\[
\boxed{
A_T=\pi A_{\rm crown}
}.
\]

Boundary:

\[
\text{projected annulus}
\neq
\text{torus surface}.
\]

## 4. Polygon sweep annulus → toroidal shell

For a regular \(n\)-gon of circumradius \(a\), the inradius is:

\[
a_n=a\cos\frac{\pi}{n}.
\]

The continuous rotation sweep of its boundary fills:

\[
a\cos\frac{\pi}{n}\le\rho\le a.
\]

Thus:

\[
\boxed{
\frac{A_{\rm ann,n}}{\pi a^2}
=
\sin^2\frac{\pi}{n}
}.
\]

If this centered annular cross-section is revolved around an external axis whose distance from the section centroid is \(R>a\), Pappus gives:

\[
V_{\rm shell,n}=2\pi R A_{\rm ann,n}.
\]

The full circular-tube torus has volume:

\[
V_T=2\pi^2Ra^2.
\]

Therefore:

\[
\boxed{
\frac{V_{\rm shell,n}}{V_T}
=
\sin^2\frac{\pi}{n}
}.
\]

Special cases:

\[
n=3:\frac34,\qquad
n=4:\frac12,\qquad
n=6:\frac14,\qquad
n=8:\frac{2-\sqrt2}{4}.
\]

The equality of fractions follows from the shared centroid/revolution radius. It does not identify the planar annulus with the toroidal shell.

## 5. Six equilateral triangles → hexagonal torus approximation

An inscribed regular hexagon of circumradius \(r\) has area:

\[
A_6=\frac{3\sqrt3}{2}r^2.
\]

Revolve it around an external axis at distance \(R\):

\[
V_6=2\pi R A_6
=3\sqrt3\,\pi Rr^2.
\]

For the circular torus:

\[
V_T=2\pi^2Rr^2.
\]

Hence:

\[
\boxed{
\frac{V_6}{V_T}
=
\frac{3\sqrt3}{2\pi}
\approx0.8269933431
}.
\]

For a regular \(n\)-gon:

\[
\boxed{
\frac{V_n}{V_T}
=
\frac{n\sin(2\pi/n)}{2\pi}
}
\]

and:

\[
\lim_{n\to\infty}\frac{V_n}{V_T}=1.
\]

## 6. Parallel tangents of the torus meridian

The meridian circle is:

\[
(\rho-R)^2+z^2=r^2.
\]

For a line family:

\[
z=m\rho+b,
\]

the two parallel tangents have:

\[
b_\pm=-mR\pm r\sqrt{1+m^2}.
\]

Their perpendicular separation is:

\[
\frac{|b_+-b_-|}{\sqrt{1+m^2}}
=
\boxed{2r}.
\]

For:

\[
m=\pm\tan30^\circ
=
\pm\frac1{\sqrt3},
\]

this recovers the mirrored \(30^\circ\) families already present in the PBIP/crown lineage.

## 7. Six equal planar sectors and toroidal volume asymmetry

Take an annular local cross-section:

\[
r_i\le s\le r_o
\]

and an angular sector of width \(\alpha\), centered at \(v_0\).

Under revolution:

\[
\boxed{
V(v_0,\alpha)
=
\pi R\alpha(r_o^2-r_i^2)
+
\frac{4\pi}{3}(r_o^3-r_i^3)
\cos v_0\sin\frac{\alpha}{2}
}.
\]

For six sectors:

\[
\alpha=\frac{\pi}{3}.
\]

The planar sector areas are equal, but the toroidal volumes generally are not.

For opposite sectors:

\[
v_0\leftrightarrow v_0+\pi,
\]

the cosine terms cancel:

\[
\boxed{
V(v_0)+V(v_0+\pi)
=
\frac13V_{\rm shell,total}
}.
\]

Hence:

\[
6\text{ equal planar sectors}
\not\Rightarrow
6\text{ equal toroidal volumes},
\]

while:

\[
\boxed{
3\text{ opposite pairs}
\Rightarrow
3\text{ equal pair-volumes}.
}
\]

## 8. 30° × 45° toroidal clocks

The existing Poincaré torus predecessor uses:

\[
\Delta u=30^\circ,\qquad
\Delta v=45^\circ.
\]

The discrete cycle lengths are \(12\) and \(8\), so:

\[
\boxed{
\operatorname{lcm}(12,8)=24
}.
\]

The sixfold \(60^\circ\) family is a subgrid of the \(30^\circ\) clock:

\[
\mathbb Z_6\hookrightarrow\mathbb Z_{12}.
\]

## 9. 5–6–7–8 common angular grid

\[
\boxed{
\operatorname{lcm}(5,6,7,8)=840
}.
\]

The common angular unit is:

\[
\delta\theta
=
\frac{2\pi}{840}
=
\frac{\pi}{420}
=
\frac37^\circ.
\]

Sector weights are:

\[
\frac{840}{5}=168,\quad
\frac{840}{6}=140,\quad
\frac{840}{7}=120,\quad
\frac{840}{8}=105.
\]

Under a common phase:

\[
\boxed{
5+6+7+8=26
\text{ nominal rays}
\to
22\text{ distinct rays}
}.
\]

Under antipodal identification \(\theta\sim\theta+\pi\):

\[
\boxed{
16\text{ distinct full-line orientations}
}.
\]

Materializing all full lines through the center yields:

\[
\boxed{
32\text{ half-rays/sectors}.
}
\]

## 10. Another 840 already present in the RLL lineage

The formal carrier:

\[
\mathbb Z_{24}\times
\mathbb Z_{10}\times
\mathbb Z_{42}
\]

has synchronous diagonal period:

\[
\boxed{
\operatorname{lcm}(24,10,42)=840.
}
\]

The diagonal cyclic subgroup is abstractly:

\[
\langle(1,1,1)\rangle
\cong
\mathbb Z_{840}.
\]

The \(5,6,7,8\) angular refinement is also represented on a cyclic grid of order \(840\).

But:

\[
\boxed{
840_{\rm angular}
\neq
840_{\rm modular\ semantics}
}
\]

until a specific state-to-angle mapping is declared and tested.

Same cyclic order is not same meaning.

## 11. Sphere ↔ torus topology boundary

\[
\chi(S^2)=2,
\qquad
\chi(T^2)=0.
\]

Therefore:

\[
S^2\not\cong T^2
\]

globally.

Allowed bridges require explicit operations such as:
- projection;
- cut/seam;
- quotient;
- local chart;
- revolution;
- distortion metadata.

## 12. Executable gates

The deterministic verifier checks:

- G01 \(h^2=3/4\);
- G02 \(30^\circ\) torus-section kernel;
- G03 projected annulus area;
- G04 \(A_T/A_{\rm crown}=\pi\);
- G05 polygon sweep fractions for \(n=3,4,6,8\);
- G06 toroidal shell fractions for \(n=3,4,6,8\);
- G07 hexagon/circular-torus volume ratio;
- G08 tangent-pair distance \(2r\);
- G09 opposite-pair closure of six toroidal sectors;
- G10 30°×45° period 24;
- G11 \(\operatorname{lcm}(5,6,7,8)=840\);
- G12 22 distinct common-phase rays;
- G13 16 antipodal line orientations;
- G14 32 half-rays;
- G15 \(\operatorname{lcm}(24,10,42)=840\).

## 13. Claim boundary

\`\`\`text
FORMAL_GEOMETRY != PHYSICAL_MECHANISM
TRIANGLE_KERNEL != TORUS
PLANAR_ANNULUS != TORUS_SURFACE
SAME_FRACTION != SAME_OBJECT
SPHERE != TORUS
PLANAR_HEXAGRAM != SPHERICAL_GEODESIC_HEXAGRAM
840_ANGULAR != 840_MODULAR_SEMANTICS
\`\`\`

## 14. R3

**F_ok**
- new torus/annulus metric relations formalized as successor deltas;
- polygon sweep fraction propagated to toroidal-shell fraction;
- six-equilateral/hexagon torus approximation derived;
- tangent separation and six-sector opposite-pair closure derived;
- 22/16/32 common-phase counts retained;
- the two 840 constructions remain explicitly distinct.

**F_gap**
- canonical semantic map between the two 840 carriers;
- spherical hexagram mapping;
- physical vortex model/data;
- independent external reproduction beyond the recorded assistant-runtime receipt.

**F_next**
1. run the verifier in canonical RLL CI;
2. add \(u\times v\) six-point sweep fixtures;
3. enumerate tangent/chord intersections;
4. test 30°/45°/60°/72° orbit combinations;
5. only then define any domain-specific physical hypothesis.


## 15. Successor delta — triangle simplex, embedding and recursive scale

The current torus/crown bridge is extended by a more general 2D representation rule.

A nondegenerate triangle

\[
T=(p_0,p_1,p_2)
\]

is the 2-simplex. Every point in its affine span has barycentric representation

\[
\boxed{
x=\lambda_0p_0+\lambda_1p_1+\lambda_2p_2,
\qquad
\lambda_0+\lambda_1+\lambda_2=1.
}
\]

This gives a local coordinate frame for position and proportion.

### Similarity transport

\[
\boxed{
F(x)=\lambda R_\theta x+t
}
\]

moves a construction to arbitrary scale, rotation and translation while preserving angles and dimensionless ratios.

\[
L\mapsto\lambda L,
\qquad
A\mapsto\lambda^2A.
\]

### Affine transport

\[
\boxed{
F(x)=Ax+t,
\qquad
\det A\neq0.
}
\]

Any reference triangle can be mapped to any other nondegenerate triangle.

\[
\boxed{
A(F(T))=|\det A|A(T).
}
\]

### Triangulation gate

Any simple polygon with \(n\) vertices admits a triangulation into

\[
\boxed{n-2}
\]

triangles.

Thus piecewise-linear planar geometry can be represented exactly by triangular cells. Curved boundaries require approximation/refinement or a separate exact parametrization.

### Canonical circles from a triangle

For sides \(a,b,c\), semiperimeter \(s\) and area \(K\):

\[
\boxed{
r_{\rm in}=\frac Ks,
\qquad
R_{\rm circ}=\frac{abc}{4K}.
}
\]

The full triangle geometry therefore provides canonical inside/outside circles.

### Embedding operator

A form \(S\) inside a triangle \(T\) is represented as:

\[
f:S\hookrightarrow T.
\]

A triangle inside another form is:

\[
g:T\hookrightarrow S.
\]

The map must declare which constraints are preserved: incidence, tangency, scale, orientation, symmetry, area or distance.

### Recursive nesting

Let:

\[
T_{k+1}=F_k(T_k),
\qquad
F_k(x)=\lambda_kR_kx+t_k,
\qquad
0<\lambda_k<1.
\]

Then:

\[
\boxed{
\operatorname{diam}(T_m)
=
\operatorname{diam}(T_0)
\prod_{k=0}^{m-1}\lambda_k.
}
\]

If \(\lambda_k\le q<1\):

\[
\boxed{
\operatorname{diam}(T_m)\to0.
}
\]

This gives an infinite nested hierarchy in the mathematical sense.

For a finite family of contractions, an iterated-function-system attractor satisfies:

\[
\boxed{
K=\bigcup_iF_i(K).
}
\]

Boundary:

\[
\boxed{
\text{infinite recursive nesting}
\neq
\text{claim of physically realized infinity}.
}
\]

Also:

\[
\boxed{
A_\triangle\text{ alone}
\neq
\text{complete geometry}.
}
\]

The universal role comes from the simplex geometry plus transformation/embedding rules, not from one scalar area value.

### Integration with existing RLL weave

The existing polygon layer:

\[
R_{k+1}=R_k\cos\frac{\pi}{n_k}
\]

and half-step operator:

\[
V(P_n)\cup V(R_{\pi/n}P_n)=V(P_{2n})
\]

now combine with simplex transport:

\[
\boxed{
\text{triangle simplex}
\to
\text{triangulation}
\to
\text{polygon family}
\to
\text{rotation}
\to
\text{embedding}
\to
\text{nested scale}
\to
\text{recursive hierarchy}.
}
\]

This is a formal geometry/representation result only; it does not establish a physical mechanism.
