#!/usr/bin/env python3
"""Prime/base coexistence curve for the bounded arithmetic carrier.

The abscissa is the integer n. Each selected prime contributes a residue/phase
coordinate. Zero residue is a valid coordinate, never semantic absence.
"""
from __future__ import annotations

from math import cos, gcd, lcm, pi, prod, sin
from typing import Iterable

from tools import rll_family_theory_bridge_v1 as bridge

CLAIM_ALLOWED = False
SELECTED_PRIMES = bridge.PRIME_ATOMS


def unit_primes_for_base(base: int, primes: Iterable[int] = SELECTED_PRIMES) -> tuple[int, ...]:
    b = int(base)
    if b < 2:
        raise ValueError("base must be >=2")
    return tuple(int(p) for p in primes if gcd(b, int(p)) == 1)


def prime_carrier_period(primes: Iterable[int] = SELECTED_PRIMES) -> int:
    ps = tuple(int(p) for p in primes)
    if not ps:
        raise ValueError("at least one prime modulus is required")
    return lcm(*ps)


def modular_axis(n: int, modulus: int) -> dict[str, object]:
    m = int(modulus)
    if m <= 1:
        raise ValueError("modulus must be >1")
    r = int(n) % m
    theta = 2.0 * pi * r / m
    return {
        "modulus": m,
        "residue": r,
        "theta": theta,
        "cos": cos(theta),
        "sin": sin(theta),
        "zero_state": "RESIDUE_ZERO" if r == 0 else "NONZERO_RESIDUE",
    }


def abscissa_point(n: int, moduli: Iterable[int] = SELECTED_PRIMES) -> dict[str, object]:
    ms = tuple(int(m) for m in moduli)
    if not ms:
        raise ValueError("at least one modulus required")
    return {
        "x": int(n),
        "axes": {str(m): modular_axis(n, m) for m in ms},
        "residue_signature": tuple(int(n) % m for m in ms),
        "joint_period": lcm(*ms),
    }


def abscissa_curve(start: int, stop: int, moduli: Iterable[int] = SELECTED_PRIMES) -> tuple[dict[str, object], ...]:
    if int(stop) < int(start):
        raise ValueError("stop must be >= start")
    ms = tuple(int(m) for m in moduli)
    return tuple(abscissa_point(n, ms) for n in range(int(start), int(stop)))


def base_prime_receipt() -> dict[str, object]:
    all_primes = tuple(SELECTED_PRIMES)
    base10_units = unit_primes_for_base(10)
    base7_units = unit_primes_for_base(7)
    repunit6 = bridge.repunit(6, 10)
    return {
        "schema": "rll.prime_base_abscissa_curve.v1",
        "claim_allowed": CLAIM_ALLOWED,
        "selected_primes": all_primes,
        "all_prime_crt_period": prime_carrier_period(all_primes),
        "all_prime_product": prod(all_primes),
        "base10_unit_primes": base10_units,
        "base10_unit_prime_period": prime_carrier_period(base10_units),
        "base7_unit_primes": base7_units,
        "base7_unit_prime_period": prime_carrier_period(base7_units),
        "repunit6": repunit6,
        "exact_relations": {
            "base10_unit_period_equals_repunit6": prime_carrier_period(base10_units) == repunit6,
            "all_prime_period_equals_10_times_repunit6": prime_carrier_period(all_primes) == 10 * repunit6,
            "base10_excluded_nonunits": tuple(p for p in all_primes if p not in base10_units),
            "base7_excluded_nonunits": tuple(p for p in all_primes if p not in base7_units),
        },
        "zero_boundary": "A zero residue is an occupied modular coordinate, not EMPTY_SET, NULL_VALUE or TOKEN_VAZIO.",
        "physical_boundary": "Joint arithmetic periods and phase curves are diagnostic carriers only; they are not physical periods without an independent observable contract.",
    }


if __name__ == "__main__":
    import json
    print(json.dumps(base_prime_receipt(), indent=2, sort_keys=True))
