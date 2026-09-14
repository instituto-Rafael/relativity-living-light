# RAFAELIAN Exact-Ratio Geometry — Session Feedback

Date: 2026-08-29
State: RESEARCH_NOTE / claim_allowed=false
Custody: append-only research branch

## 1. Core invariant

Decimal expansion is a representation, not the exact mathematical object. Preserve exact forms whenever available:

- `1/3` remains `1/3`; `0.333...` is a base-dependent expansion.
- `sqrt(3)/2` remains `sqrt(3)/2`.
- `pi` remains the exact ratio `C/d` for Euclidean circles; a finite decimal is only an approximation.
- trigonometric values should remain symbolic/exact when known.

## 2. Geometry-bearing fractions

RAFAELIAN provenance rule: a fraction may carry geometry and construction history in its unreduced numerator/denominator. Therefore preserve both layers:

`ratio_value = reduce(p/q)`
`geometric_representation = p/q`

Example:

- `77/33 = 7/3` as rational numbers.
- But `77:33` and `7:3` may encode different geometric scales, counts, partitions, lattice periods, or provenance.

Do not assert numerical inequality. Preserve representation as metadata instead of changing arithmetic equality.

Suggested typed object:

```yaml
rafaelian_ratio:
  numerator: 77
  denominator: 33
  reduced_numerator: 7
  reduced_denominator: 3
  exact_value_equal: true
  representation_preserved: true
  geometry_context: TOKEN_VAZIO
  source: session_2026-08-29
```

## 3. Terminating and repeating expansions

For rational `p/q` in base `b`, after reduction the expansion terminates iff every prime factor of `q` divides `b`; otherwise it repeats.

Thus periodicity is a property of the chosen base representation, not loss of exactness in the rational number itself.

Examples:

- `1/3` repeats in base 10, but terminates as `0.1_3` in base 3.
- `1/8` terminates in base 10 and base 2.

This supports a multi-base geometry layer: the exact fraction is invariant; the digit orbit changes with base.

## 4. Circle and trigonometric invariants

For Euclidean circles:

`C = 2*pi*r = pi*d`

`pi = C/d` is irrational, hence not a periodic decimal in any integer base. Preserve `pi` symbolically.

For the equilateral triangle:

`h/l = sqrt(3)/2`

For phase geometry:

`x = r cos(theta)`
`y = r sin(theta)`
`tan(theta) = sin(theta)/cos(theta)` when `cos(theta) != 0`.

Discrete contraction used in the current RAFAELIA formula catalog:

`r_n = (sqrt(3)/2)^n`.

## 5. Multi-base state representation

Do not force all quantities through base 10. Represent a mathematical object as:

`X = (exact_object, base, digit_string, geometry_context, provenance)`.

Candidate bases for comparative study from the session: `2, 8, 10, 18, 20, 42, 60`.

Important historical boundary: Maya numeration is primarily vigesimal (base 20), with a modified 18x20 place in calendrical counting; base 60 is classically Mesopotamian/Babylonian. Do not attribute every listed base to the Maya without source evidence.

## 6. Modular / angular geometry

Map integer states to the circle by

`theta_m(n) = 2*pi*(n mod m)/m`.

Then

`P_m(n) = (cos(theta_m(n)), sin(theta_m(n)))`.

This creates an exact bridge among integer residues, angular partitions, unit-circle geometry, and trigonometric lookup.

Families emphasized in this session: `70, 7, 56, 35, 50, 14, 3, 10, 20, 6, 2, 1`.

Observed exact relations:

- `50 = 7^2 + 1`
- `50 mod 7 = 1`
- `35 = 5*7`
- `56 = 8*7`
- `70 = 10*7`

## 7. Geometry, Poincare and curvature

Keep Euclidean and hyperbolic metrics distinct. In the Poincare unit disk:

`ds^2 = 4(dx^2+dy^2)/(1-r^2)^2`.

A Euclidean contraction `r_(n+1)=(sqrt(3)/2) r_n` is a coordinate rule; it is not by itself a hyperbolic geodesic claim.

## 8. Sine overlap, tangent and curvature

For `y=A sin(kx+phi)`:

`y' = A k cos(kx+phi)`

`y'' = -A k^2 sin(kx+phi)`

`kappa = |y''|/(1+y'^2)^(3/2)`.

Two curves can be tested for progressively stronger coexistence at the same abscissa:

1. position: `y1(x)=y2(x)`
2. tangent: `y1'(x)=y2'(x)`
3. curvature: `kappa1(x)=kappa2(x)`

## 9. Area decomposition and quadratic closure

"Borrowing area" is formalized as decomposition / inclusion-exclusion:

`Area(A union B)=Area(A)+Area(B)-Area(A intersect B)`.

Triangulation or overlap constraints may produce `a x^2+b x+c=0`; then the exact roots are

`x=(-b +- sqrt(b^2-4ac))/(2a)`.

Preserve the discriminant symbolically where possible.

## 10. Exactness contract for implementation

1. Never replace an exact symbolic value with a truncated decimal in canonical data.
2. Store decimal approximations only as derived display fields with precision metadata.
3. Preserve unreduced fraction form when it carries geometry/provenance, while also storing the reduced arithmetic value.
4. Preserve base explicitly for every digit string.
5. Distinguish numeric equality from representational identity.
6. Distinguish Euclidean metric, Poincare metric, modular phase and symbolic metaphor.
7. `TOKEN_VAZIO` is preferred to invented geometry_context or historical attribution.

## 11. Cross-repository integration targets

- RLL formula registry / PapersPub: exact-ratio and multi-base invariants.
- ChipQuantum evidence route: ISA/representation tests only; no physical quantum claim from symbolic geometry.
- Papers repository: formal note and falsifiable experiments comparing exact symbolic storage versus decimalized storage.
- Longitudinal memory: append-only receipt linking this session, formulas, hashes and future tests.

## F-state

F_ok:
- exact-value versus representation distinction formalized;
- unreduced geometry-bearing ratio preserved without denying arithmetic equality;
- circle, triangle, modular phase, trigonometry, curvature and Poincare relations integrated;
- multi-base test surface defined.

F_gap:
- empirical evidence that unreduced ratio forms improve a specific model or physical prediction is not yet demonstrated;
- exact mapping of each base to a historical civilization requires source-by-source verification;
- full ChipQuantum runtime/ISA execution for these invariants not executed in this session.

F_next:
- add machine-readable exact-ratio schema;
- run cross-base periodicity tests;
- bind to existing RLL formula IDs;
- issue a receipt with commit/blob hashes and test status.
