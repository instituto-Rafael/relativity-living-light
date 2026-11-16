#!/usr/bin/env python3
"""Bounded permutation + typed-void census for the RLL geometry thread.

This is a diagnostic mathematical catalogue. It deliberately separates numeric
zero, residue zero, empty set, missing/undefined states and TOKEN_VAZIO.
It does not modify or validate cosmological physics.
"""
from __future__ import annotations

from dataclasses import dataclass, asdict
from enum import Enum
from fractions import Fraction
from itertools import permutations
from math import gcd, lcm, pi, sqrt, sin, isfinite
from typing import Iterable

PHI = (1.0 + sqrt(5.0)) / 2.0
CLAIM_ALLOWED = False

class VoidKind(str, Enum):
    NUMERIC_ZERO = "NUMERIC_ZERO"
    RESIDUE_ZERO = "RESIDUE_ZERO"
    EMPTY_SET = "EMPTY_SET"
    NULL_VALUE = "NULL_VALUE"
    TOKEN_VAZIO = "TOKEN_VAZIO"
    UNDEFINED = "UNDEFINED"
    NO_REAL_SOLUTION = "NO_REAL_SOLUTION"
    MISSING_OBSERVATION = "MISSING_OBSERVATION"
    NOT_APPLICABLE = "NOT_APPLICABLE"
    APPROX_ZERO = "APPROX_ZERO"

@dataclass(frozen=True)
class Atom:
    name: str
    value: float
    family: str

ATOMS: tuple[Atom, ...] = (
    Atom("2", 2.0, "prime"),
    Atom("3", 3.0, "prime_repdigit_seed"),
    Atom("5", 5.0, "prime_pentagonal"),
    Atom("7", 7.0, "prime_repdigit_seed"),
    Atom("11", 11.0, "prime_mold"),
    Atom("13", 13.0, "prime_mold"),
    Atom("37", 37.0, "prime_repunit_factor"),
    Atom("10", 10.0, "base10_mold"),
    Atom("12", 12.0, "dodeca_mold"),
    Atom("14", 14.0, "composite"),
    Atom("18", 18.0, "composite"),
    Atom("21", 21.0, "crt_3x7"),
    Atom("30", 30.0, "angular_composite"),
    Atom("42", 42.0, "crt_2x3x7"),
    Atom("50", 50.0, "composite"),
    Atom("70", 70.0, "composite"),
    Atom("33", 33.0, "repdigit_3"),
    Atom("77", 77.0, "repdigit_7"),
    Atom("333", 333.0, "repdigit_3"),
    Atom("777", 777.0, "repdigit_7"),
    Atom("999", 999.0, "repdigit_9"),
    Atom("pi", pi, "irrational"),
    Atom("phi", PHI, "irrational"),
    Atom("sqrt5", sqrt(5.0), "radical"),
    Atom("sqrt_pi", sqrt(pi), "radical"),
    Atom("sqrt_phi", sqrt(PHI), "radical"),
    Atom("sqrt3_over_2", sqrt(3.0) / 2.0, "spiral_contraction"),
    Atom("sqrt_3_over_2", sqrt(3.0 / 2.0), "distinct_expansion"),
    Atom("three_over_2", 1.5, "rational_expansion_control"),
    Atom("sqrt5_over_pi", sqrt(5.0) / pi, "derived_scalar"),
    Atom("sqrt_pi_over_5", sqrt(pi / 5.0), "pentagonal_half_angle_scalar"),
    Atom("sqrt_pi_over_12", sqrt(pi / 12.0), "dodecagonal_half_angle_scalar"),
    Atom("sqrt_pi_over_pi", sqrt(pi) / pi, "derived_scalar"),
    Atom("sqrt_phi_over_pi", sqrt(PHI) / pi, "derived_scalar"),
    Atom("sqrt_pi_over_phi", sqrt(pi) / PHI, "derived_scalar"),
    Atom("sqrt_phi_over_sqrt_pi", sqrt(PHI / pi), "reciprocal_pair"),
    Atom("sqrt_pi_over_sqrt_phi", sqrt(pi / PHI), "reciprocal_pair"),
)

MODULI: tuple[int, ...] = (2, 3, 5, 7, 10, 11, 12, 13, 14, 18, 21, 30, 42, 50, 70)
MASTER_MOD_PERIOD = lcm(*MODULI)

def repdigit(digit: int, length: int, base: int = 10) -> int:
    if not (0 <= digit < base):
        raise ValueError("digit must be representable in base")
    if length < 1:
        raise ValueError("length must be >=1")
    return digit * sum(base**k for k in range(length))

def repdigit_division(digit: int, length: int, divisor: int) -> dict[str, int | str]:
    n = repdigit(digit, length)
    q, r = divmod(n, divisor)
    return {"n": n, "q": q, "r": r, "fraction": str(Fraction(n, divisor))}

def repdigit_remainder_orbit(digit: int, modulus: int, start: int = 0) -> list[int]:
    """Orbit of prefix remainders r -> base10*r+digit (mod modulus)."""
    seen: dict[int, int] = {}
    orbit: list[int] = []
    r = start % modulus
    while r not in seen:
        seen[r] = len(orbit)
        r = (10 * r + digit) % modulus
        orbit.append(r)
    return orbit

def positional_value_10(base: int) -> int:
    """The digit string '10' in base b has numeric value b."""
    if base < 2:
        raise ValueError("base >=2 required")
    return base

def residue_signature(n: int, moduli: Iterable[int] = MODULI) -> tuple[int, ...]:
    return tuple(n % m for m in moduli)

def phase(n: int, modulus: int) -> float:
    return 2.0 * pi * (n % modulus) / modulus

def ordered_binary_permutations() -> list[dict[str, object]]:
    """All ordered two-atom candidates under a bounded operator grammar.

    These are candidates, not claims. Ordering is preserved so a/b != b/a and
    a-b != b-a; commutative operations are intentionally duplicated because the
    census records provenance/order rather than quotienting by symmetry.
    """
    out: list[dict[str, object]] = []
    for a, b in permutations(ATOMS, 2):
        candidates = (
            ("sum", a.value + b.value),
            ("difference", a.value - b.value),
            ("product", a.value * b.value),
        )
        for op, v in candidates:
            if isfinite(v):
                out.append({"left": a.name, "op": op, "right": b.name, "value": v})
        if b.value != 0.0:
            v = a.value / b.value
            if isfinite(v):
                out.append({"left": a.name, "op": "ratio", "right": b.name, "value": v})
    return out

def unary_permutations() -> list[dict[str, object]]:
    out: list[dict[str, object]] = []
    for a in ATOMS:
        out.append({"op": "square", "atom": a.name, "value": a.value*a.value})
        if a.value != 0.0:
            out.append({"op": "inverse", "atom": a.name, "value": 1.0/a.value})
        if a.value >= 0.0:
            out.append({"op": "sqrt", "atom": a.name, "value": sqrt(a.value)})
    return out

def regular_mold(n: int, step: int = 1, radius: float = 1.0) -> dict[str, object]:
    """Regular polygon/star-polygon carrier {n/step} on one circle."""
    if n < 3 or not (1 <= step < n):
        raise ValueError("require n>=3 and 1<=step<n")
    g = gcd(n, step)
    theta = 2.0*pi*step/n
    return {
        "schlafli": f"{{{n}/{step}}}",
        "n": n,
        "step": step,
        "components": g,
        "cycle_length": n//g,
        "step_angle_rad": theta,
        "half_step_angle_rad": theta/2.0,
        "chord": 2.0*radius*sin(theta/2.0),
    }

def integer_mod_permutations() -> list[dict[str, int | str]]:
    ints = [a for a in ATOMS if float(a.value).is_integer()]
    out: list[dict[str, int | str]] = []
    for atom in ints:
        n = int(atom.value)
        for m in MODULI:
            out.append({"atom": atom.name, "modulus": m, "residue": n % m})
    return out

def exact_invariants() -> dict[str, object]:
    return {
        "sqrt_pi_over_pi_equals_inverse_sqrt_pi": abs(sqrt(pi)/pi - 1/sqrt(pi)) < 1e-15,
        "sqrt_phi_pi_reciprocal_product": sqrt(PHI/pi) * sqrt(pi/PHI),
        "sqrt_pi5_square": (sqrt(pi/5.0))**2,
        "sqrt_pi12_square": (sqrt(pi/12.0))**2,
        "crown_bridge": ((sqrt(3)/2)*sqrt(pi/12.0))/((1/2)*sqrt(pi/5.0)),
        "ratio_77_33": str(Fraction(77, 33)),
        "ratio_777_333": str(Fraction(777, 333)),
        "factor_1001": 7*11*13,
        "factor_21": 3*7,
        "factor_42": 2*3*7,
        "repunit6_factorization_check": 3*7*11*13*37,
        "repunit6": 111111,
    }

def void_relation(left: VoidKind, right: VoidKind) -> str:
    if left == right:
        return "SAME_TYPED_STATE"
    if {left, right} == {VoidKind.NUMERIC_ZERO, VoidKind.APPROX_ZERO}:
        return "APPROX_NEAR_NOT_EQUAL"
    if {left, right} == {VoidKind.NUMERIC_ZERO, VoidKind.RESIDUE_ZERO}:
        return "CONTEXT_RELATED_NOT_IDENTICAL"
    return "DISTINCT_OR_NOT_COMPARABLE"

def void_matrix() -> list[dict[str, str]]:
    return [
        {"left": a.value, "right": b.value, "relation": void_relation(a, b)}
        for a in VoidKind for b in VoidKind
    ]

def near_pairs(relative_tol: float = 0.01) -> list[dict[str, object]]:
    """Diagnostic near-equality only; never upgrades to identity."""
    out: list[dict[str, object]] = []
    for i, a in enumerate(ATOMS):
        for b in ATOMS[i+1:]:
            scale = max(abs(a.value), abs(b.value), 1e-300)
            rel = abs(a.value-b.value)/scale
            if 0.0 < rel <= relative_tol:
                out.append({"a": a.name, "b": b.name, "relative_difference": rel})
    return out

def receipt() -> dict[str, object]:
    binaries = ordered_binary_permutations()
    unaries = unary_permutations()
    mods = integer_mod_permutations()
    return {
        "schema": "rll.full_permutation_void_census.v1",
        "claim_allowed": CLAIM_ALLOWED,
        "scope": "bounded_current_thread_plus_source_anchors",
        "atom_count": len(ATOMS),
        "ordered_binary_candidate_count": len(binaries),
        "unary_candidate_count": len(unaries),
        "integer_mod_permutation_count": len(mods),
        "master_mod_period": MASTER_MOD_PERIOD,
        "rep7_div3": [repdigit_division(7, n, 3) for n in (1,2,3)],
        "rep3_div7": [repdigit_division(3, n, 7) for n in (1,2,3)],
        "rep7_mod3_orbit": repdigit_remainder_orbit(7, 3),
        "rep3_mod7_orbit": repdigit_remainder_orbit(3, 7),
        "base_points": {"10_base10": positional_value_10(10), "10_base7": positional_value_10(7)},
        "exact_invariants": exact_invariants(),
        "geometry_molds": {
            "pentagon": regular_mold(5, 1),
            "pentagram": regular_mold(5, 2),
            "dodecagon": regular_mold(12, 1),
            "dodecagram_12_5": regular_mold(12, 5),
            "heptagon": regular_mold(7, 1),
            "mold_11": regular_mold(11, 1),
            "mold_13": regular_mold(13, 1),
            "mold_18": regular_mold(18, 1),
            "mold_21": regular_mold(21, 1),
            "mold_42": regular_mold(42, 1),
        },
        "near_pairs_1pct": near_pairs(0.01),
        "void_state_count": len(VoidKind),
        "void_relation_count": len(void_matrix()),
        "boundary": (
            "ZERO != EMPTY_SET != NULL != TOKEN_VAZIO. Approximate-zero is a "
            "numeric tolerance state, not semantic absence. Pairwise permutations "
            "are diagnostic candidates only; physical promotion requires independent gates."
        ),
    }

if __name__ == "__main__":
    import json
    print(json.dumps(receipt(), indent=2, sort_keys=True))
