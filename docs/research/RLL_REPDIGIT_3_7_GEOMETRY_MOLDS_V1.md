# RLL — Repdigit 3↔7 Geometry and Mold Family V1

Status: `MATH_FORMAL + REPRESENTATION_DYNAMICS + claim_allowed=false`  
Date: 2026-10-04  
Parent: `RLL_GEOMETRIC_DISPERSION_FALSE_POSITIVE_GATE_V1.md`

## 0. Boundary

This note formalizes arithmetic and Euclidean phase molds only.

```text
NUMBER_PATTERN != PHYSICAL_MECHANISM
EQUAL_VALUE != EQUAL_REPRESENTATION
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
```

No cosmological parameter is changed by this note.

## 1. Repeated 7 divided by 3

Let

```text
A_n = 77...7  (n copies of digit 7)
    = 7(10^n-1)/9.
```

Then

```text
A_n/3 = 7(10^n-1)/27.
```

Requested values:

```text
7/3   = 2 + 1/3   = 2.333333...
77/3  = 25 + 2/3  = 25.666666...
777/3 = 259        exact integer
```

First six integer quotients:

```text
2, 25, 259, 2592, 25925, 259259
```

They expose the repeating quotient-prefix block `259`, because

```text
7/27 = 0.259259259...
```

### 1.1 Mod-3 geometry

Appending another digit 7 obeys

```text
A_(n+1) = 10 A_n + 7.
```

Modulo 3:

```text
r_(n+1) = r_n + 1 mod 3.
```

Starting from `7 mod 3 = 1`:

```text
1 -> 2 -> 0 -> 1 -> ...
```

So the remainder dynamics is an exact 3-cycle. Embedded with

```text
theta(r)=2*pi*r/3
```

it gives the three phase classes of a regular triangular carrier. This is arithmetic phase geometry, not a physical triangle in space.

## 2. Repeated 3 divided by 7

Let

```text
B_n = 33...3  (n copies of digit 3)
    = 3(10^n-1)/9
    = (10^n-1)/3.
```

Then

```text
B_n/7 = (10^n-1)/21.
```

This makes the requested `21` appear exactly, without insertion by hand.

Requested values:

```text
3/7   = 0 + 3/7  = 0.428571428571...
33/7  = 4 + 5/7  = 4.714285714285...
333/7 = 47 + 4/7 = 47.571428571428...
```

Continuing through one full residue period:

```text
3333/7   = 476  + 1/7
33333/7  = 4761 + 6/7
333333/7 = 47619 exact integer
```

The integer quotient prefixes are therefore

```text
0, 4, 47, 476, 4761, 47619, 476190, ...
```

which is the prefix structure induced by

```text
1/21 = 0.047619047619...
```

### 2.1 Mod-7 geometry: one fixed point plus one six-cycle

Appending digit 3 gives

```text
B_(n+1)=10B_n+3.
```

Modulo 7, since `10=3 mod 7`:

```text
T(r)=3r+3 mod 7.
```

The requested repdigit orbit is

```text
3 -> 5 -> 4 -> 1 -> 6 -> 0 -> 3.
```

It is a six-cycle containing every residue except `2`.

The omitted residue is not missing randomly: it is the unique fixed point,

```text
T(2)=3*2+3=9=2 mod 7.
```

Therefore the complete functional graph on `Z7` decomposes exactly as

```text
{2} fixed point
+
(3 5 4 1 6 0) six-cycle.
```

This is the strongest clean geometry in the requested 3/7 family. If residues are placed at seventh roots of unity, the six-cycle is a dynamical cycle on six of the seven heptagonal phase positions; it is not claimed to be a Euclidean regular hexagon.

## 3. Two different periodic molds

The two directions are not symmetric:

```text
7-repdigit / 3 -> residue period 3 -> quotient block 259
3-repdigit / 7 -> residue period 6 -> quotient block 476190
```

The periods follow from the decimal/base-10 modular dynamics and should not be promoted to a physical period.

## 4. Integer molds 11, 18, 13, 21, 42

Two simultaneous molds are retained.

### 4.1 Factor mold

```text
11 = prime
13 = prime
18 = 2*3^2
21 = 3*7
42 = 2*3*7
1001 = 7*11*13
```

The last identity is useful as a representation checkpoint around the `7,11,13` family; no physical meaning is inferred.

### 4.2 Regular-polygon mold

For every integer `n>=3` and circumradius `R`:

```text
central_angle(n)      = 2*pi/n
half_central_angle(n) = pi/n
side(n)               = 2R*sin(pi/n)
apothem(n)            = R*cos(pi/n)
sector_area(n)         = pi*R^2/n
polygon_area(n)        = (n/2)R^2*sin(2*pi/n)
```

Apply independently to

```text
n in {11,18,13,21,42}.
```

The exact `21 -> 42` refinement is especially clean:

```text
central_angle(42)=pi/21=central_angle(21)/2.
```

Equivalently, the half-step rotation of a regular 21-gon produces the 42-position carrier already compatible with the project rule `n -> 2n`.

## 5. sqrt(5), phi and sqrt(5)/pi

The pentagonal relation is standard:

```text
phi=(1+sqrt(5))/2
sqrt(5)=2phi-1.
```

For a regular pentagon, the diagonal/side ratio is exactly

```text
diagonal/side = phi.
```

Therefore `sqrt(5)` belongs naturally to the pentagram namespace through `phi`.

The requested normalized scalar is

```text
sqrt(5)/pi ~= 0.7117625434171772.
```

It is retained as a numeric normalization only:

```text
sqrt5_over_pi_role = TOKEN_VAZIO_PHYSICAL_ROLE
```

No standard physical or pentagram law is inferred from dividing by `pi`.

## 6. sqrt(pi/5) and sqrt(pi/12)

Retain the already-formal Crown scalars:

```text
s5  = sqrt(pi/5)  ~= 0.7926654595212022
s12 = sqrt(pi/12) ~= 0.5116633539732443
```

with exact squares

```text
s5^2  = pi/5  = 36 degrees
s12^2 = pi/12 = 15 degrees.
```

These are exactly the half-central angles of the regular 5-fold and 12-fold base meshes:

```text
pentagon central angle   = 72 degrees; half = 36 degrees = pi/5
12-gon central angle     = 30 degrees; half = 15 degrees = pi/12.
```

Also:

```text
s5/s12 = sqrt(12/5).
```

The existing Crown identity remains:

```text
cos(30)*s12 / (sin(30)*s5) = sqrt(5)/2.
```

This is an exact bridge among the 30-degree ruler, the `5` and `12` area-root/half-angle molds, and `sqrt(5)`.

## 7. Pentagram mold

Use the regular star polygon

```text
{5/2}.
```

For circumradius `R`:

```text
pentagon side       = 2R*sin(pi/5)
pentagram star edge = 2R*sin(2*pi/5)
star_edge/base_side = phi.
```

The base 5-fold half-angle `pi/5` must stay distinct from the star-edge half-chord angle `2*pi/5`.

## 8. Dodeca mold

Interpret `dodeca` as a 12-position family while keeping two objects separate:

```text
base regular dodecagon = {12/1}
connected dodecagram   = {12/5}.
```

For the base 12-gon:

```text
central angle      = pi/6  = 30 degrees
half-central angle = pi/12 = 15 degrees.
```

For the connected `{12/5}` star:

```text
step angle       = 2*pi*(5/12) = 5*pi/6 = 150 degrees
half-chord angle = 5*pi/12 = 75 degrees.
```

Thus `sqrt(pi/12)^2=pi/12` anchors the 12-fold base half-angle, not the dodecagram star-edge angle. Collapsing those two would be a geometry error.

## 9. False-positive gates added by this family

A downstream RLL feature fails if it:

```text
- treats the mod-7 six-cycle as a physical six-fold symmetry without evidence;
- treats residue 2 as absent rather than recognizing it as the affine fixed point;
- confuses quotient-prefix periodicity with cosmological periodicity;
- identifies sqrt(pi/5) or sqrt(pi/12) with a physical length without units;
- identifies pentagon base angle with pentagram star-edge angle;
- identifies dodecagon base angle with dodecagram {12/5} step angle;
- counts 21 and 42 as the same object merely because 42=2*21.
```

## 10. Executable verifier

```bash
python tools/rll_repdigit_geometry_molds_v1.py
python -m unittest tests.test_rll_repdigit_geometry_molds_v1 -v
```

## R3

```text
F_ok   = 7/3,77/3,777/3 and 3/7,33/7,333/7 generalized exactly; mod-3 triangle carrier and mod-7 fixed-point+six-cycle exposed; integer, pentagram, dodeca and area-root molds materialized
F_gap  = no observational/cosmological binding is justified by these arithmetic geometries; sqrt(5)/pi physical role remains TOKEN_VAZIO
F_next = let CI test the exact identities, then use these molds only as preregistered diagnostic features/negative controls against held-out RLL residuals
```
