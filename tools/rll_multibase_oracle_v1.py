"""RLL mathematical reference oracle (hosted, stdlib-only, NOT cosmology).

Authorial composition of standard integer identities; no physics claims.
"""
from fractions import Fraction
from math import gcd, lcm, isqrt

DIGITS = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"


def numeral_value(digits: str, base: int) -> int:
    """Exact positional interpretation; 2 <= base <= 36."""
    if not 2 <= base <= len(DIGITS) or not digits:
        raise ValueError("invalid base or empty numeral")
    acc = 0
    for c in digits.upper():
        d = DIGITS.find(c)
        if d < 0 or d >= base:
            raise ValueError("digit outside base")
        acc = acc * base + d
    return acc


def complement_pair(x: int, base: int, scale: int = 1):
    """Auxiliary scaled representation k*x + k*(b-x) = k*b."""
    if base < 2 or scale <= 0 or not (0 <= x <= base):
        raise ValueError("outside complement domain")
    return scale * x, scale * (base - x), scale * base


def lift_additive(x: int, base: int, scale: int) -> int:
    """Well-defined additive injection Z/base -> Z/(scale*base), [x]->[scale*x].

    This is NOT a unital ring homomorphism nor a base conversion.
    """
    if base < 2 or scale < 1:
        raise ValueError("invalid modulus or scale")
    return scale * (x % base) % (scale * base)


def near_anchor_product(x: int, y: int, anchor: int):
    """Exact signed virtual area: a²+a(u+v)+uv=(a+u)(a+v)."""
    u, v = x - anchor, y - anchor
    return anchor * anchor + anchor * (u + v) + u * v


def nine_via_ten(n: int) -> int:
    return 10 * n - n


def multiply_by_base_minus_one(n: int, base: int) -> int:
    if base < 2:
        raise ValueError("invalid base")
    return base * n - n


def phase_fraction(k: int, divisions: int) -> Fraction:
    """Position on unit circle as exact fraction of one turn."""
    if divisions < 1:
        raise ValueError("positive number of divisions required")
    return Fraction(k % divisions, divisions)


def intersection_count(n: int, m: int) -> int:
    if n < 1 or m < 1:
        raise ValueError("positive grids required")
    return gcd(n, m)


def supergrid(*grids: int) -> int:
    if not grids or any(n < 1 for n in grids):
        raise ValueError("positive nonempty grids required")
    return lcm(*grids)


def compatible_crt(r14: int, r10: int) -> bool:
    """CRT compatibility for mod 14 and 10: same parity."""
    return r14 % 2 == r10 % 2


def digital_root_decimal(n: int) -> int:
    if n < 0:
        raise ValueError("nonnegative only")
    return 0 if n == 0 else 1 + (n - 1) % 9


def is_prime(n: int) -> bool:
    if n < 2:
        return False
    return all(n % d for d in range(2, isqrt(n) + 1))
