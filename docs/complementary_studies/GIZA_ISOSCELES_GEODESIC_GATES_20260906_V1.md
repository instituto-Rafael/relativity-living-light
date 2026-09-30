# Giza — Isosceles, Geodesic and Toroidal Gate Model — 2026-09-06

**State:** `COMPLEMENTARY_STUDY / HYPOTHESIS / CLAIM_BLOCKED`  
**Claim boundary:** documentation and mathematical derivation are not scientific or historical validation.  
**Cross-repository companion:** `rafaelmeloreisnovo/papers/papers/archaeoastronomy_geometry_calendar_invariants_v1/addendum_giza_isosceles_geodesic_gates_20260906.md`

## 0. Epistemic contract

This note follows the RLL claim-gated architecture:

```text
hypothesis -> data -> baseline -> metric -> uncertainty -> falsifier -> claim gate
```

Four layers are kept separate:

```text
M1 = archaeological/survey inputs and literature values
M2 = exact mathematical identities
M3 = geometric constructions derived from declared inputs
M4 = historical/physical interpretation
```

Rules:

```text
M2 != evidence of M4
M3 != historical intent
numerical coincidence != encoded design
projection != topology-preserving equivalence
```

## 1. Unified requested object

The working construction is

\[
\boxed{
\text{Great Pyramid}
\oplus\text{North gate}
\oplus\text{base/Queen triangle}
\oplus\text{north shaft pair}
\oplus\text{south shaft pair}
\xrightarrow{\Pi_S}
\text{geodesic sphere}
}
\]

The same isosceles operator is applied to every object, while preserving whether the input is structural, directional or idealized.

## 2. Isosceles operator and equilateral gate [M2]

For an isosceles triangle with equal sides `L` and half-apex angle `alpha`:

\[
b=2L\sin\alpha,
\qquad
h=L\cos\alpha,
\qquad
\theta_{apex}=2\alpha.
\]

Define the opening ratio

\[
\kappa=\frac{b}{L}=2\sin\alpha
\]

and distance to the equilateral half-angle

\[
\Delta_\alpha=30^\circ-\alpha.
\]

The equilateral gate is exact:

\[
\alpha=30^\circ
\Longrightarrow
b=L,
\qquad
h=\frac{\sqrt3}{2}L,
\qquad
\theta_{apex}=60^\circ.
\]

Two explicit adequation operators are retained:

\[
\mathcal E_L(T)=\left(L,30^\circ,L,\frac{\sqrt3}{2}L\right)
\]

when preserving the equal-side length, and

\[
\mathcal E_b(T)=\left(b,30^\circ,b,\frac{\sqrt3}{2}b\right)
\]

when preserving the base.

Interpretation of `kappa`:

```text
kappa = 1  -> equilateral
kappa < 1  -> narrower/collimated relative to equilateral
kappa > 1  -> more open than equilateral
```

## 3. Great Pyramid face [M3]

Using the standard idealized reconstruction

\[
H=280c,
\qquad
B=440c,
\]

with `c` denoting a royal cubit, an apex-to-base-corner edge of one triangular face is

\[
L_P=\sqrt{280^2+220^2+220^2}
=\sqrt{175200}
\approx418.569c.
\]

For face base `b_P=440c`:

\[
\alpha_P
=\arcsin\left(\frac{440}{2L_P}\right)
\approx31.709^\circ,
\]

\[
\theta_{P,apex}\approx63.417^\circ,
\qquad
\Delta_{\alpha,P}\approx-1.709^\circ,
\qquad
\kappa_P\approx1.05120.
\]

This is a near-equilateral derived face model, slightly more open than the equilateral gate. It is not a claim that the pyramid face was designed from an equilateral triangle.

## 4. North ascending/descending gate [M3]

As a first meridional proxy, take principal passage inclinations near

```text
descending ≈ 26.52°
ascending  ≈ 26.18°
```

and construct an isosceles-like angular gate from their opposed directions:

\[
\theta_N\approx26.52^\circ+26.18^\circ=52.70^\circ,
\]

\[
\alpha_N\approx26.35^\circ.
\]

Normalized to `L=1`:

\[
b_N\approx2\sin26.35^\circ\approx0.887,
\qquad
h_N\approx\cos26.35^\circ\approx0.896,
\]

\[
\Delta_{\alpha,N}\approx3.65^\circ.
\]

This is explicitly a constructed angular gate. The two passages are not promoted to a single archaeologically established physical triangle.

## 5. Base/Queen compass construction [M3]

Use only as an integer idealization the rounded coordinates

\[
Q=(0,41),
\qquad
K=(21,82)
\]

in cubits. These values approximate surveyed relationships and MUST NOT be relabeled as exact measured coordinates.

A circle centered on `Q` and passing through `K` has

\[
R_Q^2=41^2+21^2=2122.
\]

Intersecting that circle with the base plane `z=0` gives

\[
x^2+41^2=2122
\Longrightarrow
x^2=441
\Longrightarrow
x=\pm21.
\]

The resulting isosceles triangle has

\[
b_B=42,
\qquad
h_B=41,
\qquad
L_B=\sqrt{2122}\approx46.065.
\]

Therefore

\[
\alpha_B=\arctan\frac{21}{41}\approx27.121^\circ,
\]

\[
\theta_{B,apex}\approx54.243^\circ,
\qquad
\Delta_{\alpha,B}\approx2.879^\circ,
\qquad
\kappa_B\approx0.91175.
\]

The same circle/base intersection written as a quadratic is

\[
x^2-441=0,
\]

so

\[
\Delta_{Bhaskara}=0^2-4(1)(-441)=1764=42^2,
\]

and the roots are `±21`. This is an exact consequence of the declared rounded model, not evidence of intentional historical encoding of 21 or 42.

## 6. Directional shaft-pair proxies [M3]

This layer uses simplified principal elevations only. Real shafts contain bends, variable slopes, horizontal sections and construction irregularities.

### 6.1 North pair

Using the meridional elevation proxy

```text
King north  ≈ 32.600°
Queen north ≈ 39.124°
```

produces angular separation

\[
\delta_{N*}\approx6.524^\circ,
\qquad
\alpha_{N*}\approx3.262^\circ.
\]

On a sphere of radius `S`:

\[
b_{N*}=2S\sin3.262^\circ\approx0.1138S,
\]

\[
h_{N*}=S\cos3.262^\circ\approx0.9984S,
\]

\[
\Delta_{\alpha,N*}\approx26.738^\circ.
\]

### 6.2 South pair

Using

```text
Queen south ≈ 39.608°
King south  ≈ 45.000°
```

produces

\[
\delta_{S*}\approx5.392^\circ,
\qquad
\alpha_{S*}\approx2.696^\circ,
\]

\[
b_{S*}\approx0.0941S,
\qquad
h_{S*}\approx0.9989S,
\qquad
\Delta_{\alpha,S*}\approx27.304^\circ.
\]

These two shaft-pair objects are collimated directional triangles, not near-equilateral structural triangles. A true 3D angular separation requires full shaft polylines and azimuths.

## 7. Structural vs collimated families [M3]

| object | half-angle `alpha` | `Delta_alpha` | `kappa=b/L` | model class |
|---|---:|---:|---:|---|
| pyramid face | ~31.709° | ~-1.709° | ~1.0512 | near-equilateral/open |
| base/Queen compass | ~27.121° | ~+2.879° | ~0.9118 | near-equilateral/closed |
| north passage gate | ~26.350° | ~+3.650° | ~0.887 | near-equilateral/closed |
| north shaft pair | ~3.262° | ~+26.738° | ~0.1138 | collimated |
| south shaft pair | ~2.696° | ~+27.304° | ~0.0941 | collimated |

The split into two families is part of the model and is preferable to forcing every object into a 60° triangle.

## 8. Toro, toroid and Bhaskara/Pythagoras gate [M2/M3]

Surface torus:

\[
X(u,v)=((R+r\cos v)\cos u,(R+r\cos v)\sin u,r\sin v).
\]

Solid toroid meridional domain:

\[
\mathcal T^3=\{(\rho,z):(\rho-R)^2+z^2\le r^2\}.
\]

A line `z=m rho+b` substituted into the torus section gives

\[
A\rho^2+B\rho+C=0
\]

with

\[
A=1+m^2,
\quad
B=2(mb-R),
\quad
C=R^2+b^2-r^2.
\]

The discriminant classifies the intersection:

```text
Delta > 0 -> two real section crossings
Delta = 0 -> tangency
Delta < 0 -> no real section crossing
```

For a unit-direction line at perpendicular distance `d_perp` from a circular-section center,

\[
q^2=r^2-d_\perp^2,
\qquad
\Delta=4q^2.
\]

Thus Pitagoras and the quadratic discriminant encode the same chord/tangency gate in two algebraic languages.

At

\[
m=\pm\tan30^\circ=\pm\frac1{\sqrt3},
\]

the tangent family is

\[
b=-mR\pm r\sqrt{1+m^2},
\]

giving four signed tangents, all satisfying `Delta=0`.

## 9. Projection to the sphere and geodesic shell [M2/M3]

For any nonzero direction vector `v`:

\[
\Pi_S(\vec v)=S\frac{\vec v}{\|\vec v\|}.
\]

For a torus point `X`:

\[
\Pi_S(X)=S\frac{X}{\|X\|}.
\]

This is a projection, not a homeomorphism. In particular,

\[
\chi(T^2)=0,
\qquad
\chi(S^2)=2,
\qquad
T^2\not\cong S^2.
\]

For an icosphere of frequency `f`:

\[
V=10f^2+2,
\qquad
E=30f^2,
\qquad
F=20f^2.
\]

At `f=2`:

\[
(V,E,F)=(42,120,80),
\qquad
V-E+F=2.
\]

`42` is therefore structural in this geodesic mesh. The bridge `42_geodesic <-> 42_Giza` remains `HYPOTHESIS/TOKEN_VAZIO` unless an independent physical or historical mechanism is demonstrated.

## 10. Optional modular coordinate layer [M2/M3]

The continuous geometry is not replaced by modular encoding. A separate coordinate layer may be defined as

\[
\mathcal R(n)=(n\bmod7,n\bmod14,n\bmod13,n\bmod10,n\bmod20,n\bmod60,n\bmod144,n\bmod146,n\bmod14000,n\bmod144000,n\bmod288000).
\]

Exact relations retained as arithmetic facts include

\[
\frac7{14}=\frac{144000}{288000}=\frac12,
\]

\[
14\to42\to126\quad(\times3),
\]

\[
14=(112)_3,\quad42=(1120)_3,\quad126=(11200)_3,
\]

\[
14\equiv144\equiv+1\pmod{13},
\]

\[
14000\equiv144000\equiv-1\pmod{13},
\]

and

\[
\operatorname{lcm}(7,14,13,10,20,60,144,146,14000,144000,288000)
=1\,913\,184\,000.
\]

These relations are coordinate/arithmetic facts only. They do not promote an archaeological claim.

## 11. Open evidence gates

```text
TOKEN_VAZIO_SHAFT_POLYLINE_3D
TOKEN_VAZIO_SHAFT_AZIMUTH_PROFILE
TOKEN_VAZIO_SHAFT_UNCERTAINTY_CONES
TOKEN_VAZIO_ORIGINAL_CASING_INTERSECTIONS
TOKEN_VAZIO_H8_INTENT
TOKEN_VAZIO_EPOCH_SWEEP
TOKEN_VAZIO_CATALOG_WIDE_STAR_CONTROL
TOKEN_VAZIO_HISTORICAL_INTENT
```

A promotion test requires, at minimum:

```text
measured/source-traced 3D shaft polylines
-> uncertainty propagation
-> local horizon directions at Giza
-> precession/nutation/proper-motion reconstruction
-> catalog-wide stellar control
-> geometric-only null model
-> residual comparison
-> independent historical evidence
```

## 12. Falsifiers

The integrated interpretation must weaken or fail if any of the following occurs:

1. full 3D shaft geometry destroys the simplified north/south angular pairings;
2. the near-30° structural clustering disappears when non-rounded survey values are used;
3. catalog-wide star controls produce many equally good or better epoch matches;
4. architectural constraints explain the geometry without an astronomical term;
5. modular correspondences depend on arbitrary unit choice or rounding;
6. no independent evidence links the mathematical construction to historical intent.

## 13. R3

```text
F_ok   = isosceles/equilateral operator, torus/toroid discriminant gate, geodesic projection and five Giza model objects registered
F_gap  = physical 3D shaft paths, uncertainties, epoch sweep, H8 intent and historical encoding remain TOKEN_VAZIO
F_next = source full shaft geometry, compute true 3D angular separations, project uncertainty cones to S^2 and compare against geometric and stellar null models
```
