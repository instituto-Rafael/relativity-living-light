# RLL — HETE Stability Boundary Geometry V1

**Date:** 2026-09-24  
**State:** `DERIVED_MODEL_RESULT + EXACT_HEAD_CI_PENDING`  
**claim_allowed:** `false`

## Canonical q=R/r=2 result

For the 30°/45° toroidal flow with the geometry-generated HETE parameter `c`, the 18 non-stable source states collapse to five unique torus positions:

\[
\mathcal U=\{(0,0)\}\cup\{(\pm30^\circ,\pm45^\circ)\}.
\]

Each of the six branches has exactly three cyclic non-stable steps out of 24, hence:

\[126/144=7/8.\]

The branch arcs are phase 0°: `{23,0,1}`, phase 120°: `{7,8,9}`, phase 240°: `{15,16,17}`, for both chiralities.

## What the break does and does not coincide with

- All 18 non-stable states are on the outer torus side (`v=0` or `v=±45°`).
- None is at the inner throat `v=180°`.
- None is at the previously derived meridional `v=±30°` tangent mouth.
- The central non-stable point is on the outer radial median.
- The first ±30° azimuth / ±45° meridian neighbours are non-stable; the next discrete step is stable at q=2.

Therefore the current model does not support a throat-caused instability, and it must keep `u=±30°` azimuth separate from the `v=±30°` meridional mouth.

## Five-point support shape

The four off-axis source points have:

\[
x_c=(R+r/\sqrt2)\cos30^\circ,\quad
y=\pm\tfrac12(R+r/\sqrt2),\quad
z=\pm r/\sqrt2.
\]

Together with the axial point `(R+r,0,0)`, they form a right rectangular-pyramid support. Its base sides are:

\[L_y=R+r/\sqrt2,\qquad L_z=\sqrt2 r.\]

A square base would require `R/r=1/sqrt(2)`, incompatible with a ring torus `R/r>1`. Thus this instability support is not the square/cube layer of PG-Ω7.

## Exact ratio regimes

Let `q=R/r>1`. The attracting fixed-point boundary has radial values `|c|=1/4` at `u=0°` and `|c|=sqrt(3)/4` at `u=±30°`.

The derived thresholds are:

\[
q_1=\frac{\cos30^\circ-\cos45^\circ}{1-\cos30^\circ}\approx1.186184747608386,
\]

\[q_2=3,\]

\[
q_3=\frac{\cos30^\circ+\cos45^\circ}{1-\cos30^\circ}\approx11.742018482667117.
\]

With strict HETE inequality, the 144-state lattice has:

| q regime | stable | non-stable | stable fraction |
|---|---:|---:|---:|
| `1<q<q1` | 138 | 6 | 23/24 |
| `q1<=q<3` | 126 | 18 | 7/8 |
| `3<=q<q3` | 120 | 24 | 5/6 |
| `q>=q3` | 108 | 36 | 3/4 |

The same-scale passage point `R=2r` lies inside the 7/8 plateau; it is not itself a HETE bifurcation.

## 144→42 alias finding

The mixed icosphere vertices are exactly `{23,30,32,40,41}` in the canonical replay. They mix distinct torus source states after radial projection / nearest-vertex quantization. Example: vertex 41 receives both outer `(u,v)=(0,0)` non-stable and inner `(0,180°)` stable states.

Therefore `mixed sphere bin != mixed source stability`. Source torus coordinates must remain attached after projection.

## R3

`F_ok`: 18 states localized; five source positions; exact 3/24 arc; exact q thresholds; throat and meridional-30 coincidence falsified for q=2; projection aliasing identified; support classified as rectangular-pyramid.

`F_gap`: exact-head CI; mesh-refinement persistence; physical vortex dynamics; strong-gravity observational binding.

`F_next`: after CI, refine the lattice at 15°, 7.5° and 1° without refitting the HETE gate and test whether the five-point/three-step boundary converges to a continuous curve or disappears as a discretization artifact.