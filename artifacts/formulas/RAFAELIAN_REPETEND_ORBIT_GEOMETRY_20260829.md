# RAFAELIAN Repetend Orbit Geometry

Date: 2026-08-29
State: FORMAL_MATHEMATICAL_NOTE
claim_allowed: false

## Exact object before digit expansion

Let `p/q` be a reduced rational and let `b >= 2` be an integer positional base. The exact number is `p/q`. Its digit expansion in base `b` is a representation derived by long division.

Define the remainder state by

`r_0 = p mod q`

`r_(k+1) = (b*r_k) mod q`.

The emitted digit at step `k+1` is

`d_(k+1) = floor(b*r_k/q)`.

Because there are only finitely many residue states modulo `q`, the remainder trajectory must either reach `0` (terminating expansion) or enter a cycle (repeating expansion).

This gives a rigorous geometric interpretation of a repetend without changing the rational number.

## Circular embedding

Embed each remainder state on a circle of `q` positions:

`theta_k = 2*pi*r_k/q`

`z_k = exp(i*theta_k)`.

Then the repeating expansion corresponds to a closed orbit of residue states on that finite circle.

The geometry is exact at the symbolic level: angles are stored as rational multiples of `2*pi`; no finite decimal is required.

## Multiplicative order

After removing denominator factors shared with the base, let the remaining coprime denominator be `q'`. When `gcd(b,q')=1`, the repeating period divides and, for `1/q'`, is given by the multiplicative order

`period = ord_(q')(b)`,

where `ord_(q')(b)` is the least positive `t` such that

`b^t = 1 (mod q')`.

## Examples

### 1/3 in base 10

Remainder orbit:

`1 -> 1 -> 1 -> ...`

Period `1`; digit `3` repeats.

Exact canonical value: `1/3`.

Exact base-10 expansion: `0.(3)`.

Finite `0.333` is only an approximation.

### 1/7 in base 10

Remainder orbit:

`1 -> 3 -> 2 -> 6 -> 4 -> 5 -> 1`.

This is a six-state closed cycle and generates the repetend `142857`.

The corresponding exact angular orbit is

`theta_k = 2*pi*r_k/7`.

Thus the repetend can be studied as a permutation/orbit on the nonzero residue classes modulo 7.

### 1/3 in base 3

The remainder reaches zero after one digit:

`1/3 = 0.1_3`.

The rational is unchanged; only the positional representation changes.

## RAFAELIAN representation contract

Store at least:

```yaml
exact_ratio:
  numerator_raw: p_raw
  denominator_raw: q_raw
  numerator_reduced: p
  denominator_reduced: q
  base: b
  remainder_orbit: [r_0, r_1, ...]
  repetend_period: t_or_0
  angular_orbit: "2*pi*r_k/q"
  geometry_context: OPTIONAL_EVIDENCED
  provenance_hash: REQUIRED_WHEN_PERSISTED
```

The unreduced tuple may retain scale/count/provenance even though arithmetic evaluation uses the reduced rational.

## Boundary

This construction does **not** turn a repeating rational into a different non-repeating irrational number. It replaces a potentially inconvenient digit string by an exact rational + finite modular orbit + exact angular embedding.

That is the precision-preserving geometric transformation.
