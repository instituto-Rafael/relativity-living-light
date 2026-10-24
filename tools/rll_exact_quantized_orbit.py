#!/usr/bin/env python3
# RAFAELIA / RLL laboratory, 2026-10-24.
# Authored scoped mathematical oracle; not a physical model or ARM implementation.
# Standard-library only. Source mathematics: alpha = sqrt(3)/2.
# Prior art: docs/research/RLL_EXACT_QUANTIZATION_TOPOLOGY_GATE_20261024.md.
"""Exact integer quantization and orbit-signature diagnostics.

For positive integer base b and nonnegative n, evaluate
floor(b*(sqrt(3)/2)**n) without floating-point operations.
"""

import json
from math import gcd, isqrt


def quantized_step(base: int, exponent: int) -> int:
    """Return the mathematically exact floor; no float or tolerance."""
    if type(base) is not int or type(exponent) is not int:
        raise TypeError("base and exponent must be integers (not bool)")
    if base <= 0 or exponent < 0:
        raise ValueError("base > 0 and exponent >= 0 required")
    half, odd = divmod(exponent, 2)
    numerator = base * pow(3, half)
    denominator = pow(4, half)
    if odd:
        # floor(floor(sqrt(3*numerator**2))/(2*denominator))
        # == floor(numerator*sqrt(3)/(2*denominator)).
        return isqrt(3 * numerator * numerator) // (2 * denominator)
    return numerator // denominator


def orbit_signature(base: int, step: int) -> dict:
    """Translation x -> (x+step) mod base; crossings are not new vertices."""
    if type(base) is not int or type(step) is not int:
        raise TypeError("base and step must be integers")
    if base <= 0:
        raise ValueError("base > 0 required")
    count = gcd(base, step)
    return {
        "vertices": base,
        "step_mod_base": step % base,
        "cycles": count,
        "vertices_per_cycle": base // count,
        "permutation_sign": -1 if (base - count) % 2 else 1,
    }


def is_integer_boundary(base: int, exponent: int) -> bool:
    """Exact-boundary flag for even powers; odd powers remain irrational."""
    if type(base) is not int or type(exponent) is not int:
        raise TypeError("base and exponent must be integers")
    if base <= 0 or exponent < 0:
        raise ValueError("base > 0 and exponent >= 0 required")
    return exponent % 2 == 0 and base % pow(4, exponent // 2) == 0


def audit(base: int, exponent: int) -> dict:
    """A scoped mathematical record, not a physics or runtime receipt."""
    step = quantized_step(base, exponent)
    return {
        "operator": "floor(base*(sqrt(3)/2)^exponent)",
        "base": base,
        "exponent": exponent,
        "exact_step": step,
        "integer_boundary": is_integer_boundary(base, exponent),
        "orbit": orbit_signature(base, step),
        "claim_allowed": False,
        "scope": "finite_integer_arithmetic_only",
    }


def main() -> int:
    records = [audit(b, n) for b in (6, 7, 8, 13, 16, 100)
               for n in range(12)]
    print(json.dumps({"schema": "rll.quantization.oracle.v1",
                      "state": "LOCAL_REFERENCE_NOT_PHYSICAL",
                      "claim_allowed": False, "records": records},
                     ensure_ascii=False, indent=2))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
