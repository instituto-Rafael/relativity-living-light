from __future__ import annotations

from dataclasses import dataclass
from fractions import Fraction
from functools import reduce
from math import gcd
from typing import Iterable, Sequence

Point = tuple[Fraction, Fraction]
Triangle = tuple[Point, Point, Point]

CLAIM_ALLOWED = False
PRIOR_ART_STATUS = "INCOMPLETE"
PHYSICAL_BINDING = "TOKEN_VAZIO_PHYSICAL_BINDING"
IMAGE_METRIC_STATUS = "IMAGE_PIXEL_EVIDENCE_ONLY"


def F(x: int | Fraction) -> Fraction:
    return x if isinstance(x, Fraction) else Fraction(x)


def point(x: int | Fraction, y: int | Fraction) -> Point:
    return (F(x), F(y))


def centroid(t: Triangle) -> Point:
    return (
        sum((p[0] for p in t), Fraction()) / 3,
        sum((p[1] for p in t), Fraction()) / 3,
    )


def medial_step(t: Triangle) -> Triangle:
    a, b, c = t
    return (
        ((b[0] + c[0]) / 2, (b[1] + c[1]) / 2),
        ((c[0] + a[0]) / 2, (c[1] + a[1]) / 2),
        ((a[0] + b[0]) / 2, (a[1] + b[1]) / 2),
    )


def medial_closed_form(t: Triangle, k: int) -> Triangle:
    if k < 0:
        raise ValueError("k must be non-negative")
    g = centroid(t)
    q = Fraction((-1) ** k, 2**k)
    return tuple(
        (g[0] + q * (p[0] - g[0]), g[1] + q * (p[1] - g[1])) for p in t
    )  # type: ignore[return-value]


def medial_iterate(t: Triangle, k: int) -> Triangle:
    out = t
    for _ in range(k):
        out = medial_step(out)
    return out


def signed_double_area(t: Triangle) -> Fraction:
    (x1, y1), (x2, y2), (x3, y3) = t
    return (x2 - x1) * (y3 - y1) - (y2 - y1) * (x3 - x1)


def area_ratio(t0: Triangle, tk: Triangle) -> Fraction:
    a0 = abs(signed_double_area(t0))
    if a0 == 0:
        raise ValueError("degenerate triangle")
    return abs(signed_double_area(tk)) / a0


def cyclic_side_division(t: Triangle, u: Fraction) -> Triangle:
    """A'=(1-u)B+uC, B'=(1-u)C+uA, C'=(1-u)A+uB."""
    a, b, c = t
    v = 1 - u
    def mix(p: Point, q: Point) -> Point:
        return (v * p[0] + u * q[0], v * p[1] + u * q[1])
    return (mix(b, c), mix(c, a), mix(a, b))


def cyclic_area_factor(u: Fraction) -> Fraction:
    return 1 - 3 * u + 3 * u * u


def lcm(a: int, b: int) -> int:
    return abs(a * b) // gcd(a, b) if a and b else 0


def lcm_many(values: Iterable[int]) -> int:
    vals = tuple(values)
    if not vals or any(v <= 0 for v in vals):
        raise ValueError("moduli must be positive and non-empty")
    return reduce(lcm, vals, 1)


def residue_signature(k: int, moduli: Sequence[int]) -> tuple[int, ...]:
    return tuple(k % m for m in moduli)


def digits_in_base(n: int, base: int) -> tuple[int, ...]:
    if n < 0 or base < 2:
        raise ValueError("n >= 0 and base >= 2 required")
    if n == 0:
        return (0,)
    out: list[int] = []
    while n:
        out.append(n % base)
        n //= base
    return tuple(reversed(out))


def value_from_digits(digits: Sequence[int], base: int) -> int:
    if base < 2 or any(d < 0 or d >= base for d in digits):
        raise ValueError("invalid digit/base")
    out = 0
    for d in digits:
        out = out * base + d
    return out


@dataclass(frozen=True)
class MulticarrierState:
    k: int
    centroid: Point
    triangle: Triangle
    residue_signature: tuple[int, ...]
    base_representations: tuple[tuple[int, tuple[int, ...]], ...]
    graph_signature: tuple[str, ...]
    set_signature: tuple[str, ...]


def product_carrier_state(
    t0: Triangle,
    k: int,
    moduli: Sequence[int],
    bases: Sequence[int],
) -> MulticarrierState:
    tk = medial_closed_form(t0, k)
    return MulticarrierState(
        k=k,
        centroid=centroid(t0),
        triangle=tk,
        residue_signature=residue_signature(k, moduli),
        base_representations=tuple((b, digits_in_base(k, b)) for b in bases),
        graph_signature=("BOUNDARY_C3", "MEDIAN_INCIDENCE_TEMPLATE"),
        set_signature=("NESTED_TRIANGLE", "NONEMPTY", "CENTROID_LIMIT"),
    )


def stroboscopic_medial_relation(k: int, moduli: Sequence[int]) -> dict[str, object]:
    L = lcm_many(moduli)
    return {
        "period": L,
        "same_residue_signature": residue_signature(k, moduli)
        == residue_signature(k + L, moduli),
        "length_factor": Fraction(1, 2**L),
        "signed_vertex_factor": Fraction((-1) ** L, 2**L),
        "area_factor": Fraction(1, 4**L),
        "orientation_parity_same": (L % 2 == 0),
    }


def theorem_registry() -> tuple[dict[str, object], ...]:
    return (
        {
            "id": "T1",
            "name": "Iterated medial contraction",
            "state": "KNOWN_CLASSICAL",
            "claim_allowed": False,
        },
        {
            "id": "T2",
            "name": "Cyclic side-division centroid/area map",
            "state": "DERIVED_KNOWN_FAMILY",
            "claim_allowed": False,
        },
        {
            "id": "T3",
            "name": "Non-void zero-measure centroid limit",
            "state": "DERIVED_CLASSICAL_COROLLARY",
            "claim_allowed": False,
        },
        {
            "id": "T4",
            "name": "Stroboscopic median-residue multicarrier relation",
            "state": "CANDIDATE_NEW_COMPOSITION",
            "prior_art_status": PRIOR_ART_STATUS,
            "claim_allowed": False,
        },
        {
            "id": "T5",
            "name": "Typed product-carrier dynamics",
            "state": "ENGINEERING_COMPOSITION",
            "claim_allowed": False,
        },
    )
