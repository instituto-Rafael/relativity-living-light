#!/usr/bin/env python3
"""Formal bridge across sets, numbers, primes, graphs, bases and fluids.

This module extends the bounded permutation census without changing RLL physics.
Mathematical identities can PASS inside their declared assumptions; any physical
RLL binding remains claim-gated and fail-closed.
"""
from __future__ import annotations

from collections import defaultdict, deque
from dataclasses import dataclass, asdict
from math import gcd, prod, sqrt
from typing import Iterable, Sequence

from tools import rll_full_permutation_void_census_v1 as census

CLAIM_ALLOWED = False
PHYSICAL_FLUID_BINDING_STATE = "TOKEN_VAZIO_FLUID_BINDING"
PHYSICAL_COSMOLOGY_BINDING_STATE = "TOKEN_VAZIO_COSMOLOGY_BINDING"

PRIME_ATOMS = (2, 3, 5, 7, 11, 13, 37)
INTEGER_MOLDS = (10, 12, 14, 18, 21, 30, 42, 50, 70, 33, 77, 333, 777, 999)
CRT_21 = (3, 7)
CRT_42 = (2, 3, 7)


@dataclass(frozen=True)
class TheoryFamily:
    family_id: str
    domain: str
    status: str
    statement: str
    boundary: str


FAMILIES: tuple[TheoryFamily, ...] = (
    TheoryFamily("SET-01", "set_theory", "MATH_FORMAL", "Finite carriers, subsets, products, equivalence classes and typed emptiness.", "Equal cardinality does not imply equal typed objects."),
    TheoryFamily("NUM-01", "number_theory", "MATH_FORMAL", "Divisibility, gcd/lcm, factorization, repdigits, repunits and base representations.", "Equal numeric value does not imply equal representation provenance."),
    TheoryFamily("PRIME-01", "prime_theory", "MATH_FORMAL", "Prime factors, Euler phi and multiplicative order of the base modulo a prime or coprime modulus.", "Decimal-cycle structure is arithmetic, not a physical cycle."),
    TheoryFamily("BASE-01", "positional_systems", "MATH_FORMAL", "Digit strings are interpreted relative to a declared base; 10_b=b.", "Digit 0 is not semantic absence."),
    TheoryFamily("MOD-01", "modular_arithmetic", "MATH_FORMAL", "Residues, residue-zero, phase carriers and functional remainder maps.", "Residue zero is a valid class, not EMPTY_SET or TOKEN_VAZIO."),
    TheoryFamily("CRT-01", "product_arithmetic", "MATH_FORMAL", "Pairwise-coprime residue coordinates reconstruct a unique class modulo the product.", "CRT coordinates do not establish physical independent axes."),
    TheoryFamily("GRAPH-01", "functional_graphs", "MATH_FORMAL", "Remainder recurrences define finite directed functional graphs with cycles and basins.", "Graph topology is not automatically spatial geometry."),
    TheoryFamily("GRAPH-02", "factor_graphs", "MATH_FORMAL", "Composite molds and prime factors define a bipartite incidence graph.", "Shared factor means arithmetic relation only."),
    TheoryFamily("GRAPH-03", "cayley_graphs", "MATH_FORMAL", "Z_m with additive step defines a cycle/Cayley carrier when gcd(step,m)=1.", "Carrier period is not a cosmological period."),
    TheoryFamily("GEOM-01", "regular_geometry", "MATH_FORMAL", "Polygon and star-polygon molds use declared n and step k.", "{n/1} and {n/k} remain distinct objects."),
    TheoryFamily("RAD-01", "radicals_ratios", "MATH_FORMAL", "Radicals, reciprocal pairs and exact/near equalities are separately classified.", "Approximate equality never upgrades to identity."),
    TheoryFamily("VOID-01", "typed_void", "MATH_FORMAL", "Numeric zero, residue zero, empty set, null, undefined and TOKEN_VAZIO are typed separately.", "TOKEN_VAZIO != 0."),
    TheoryFamily("FLUID-01", "continuity", "FORMAL_UNDER_ASSUMPTIONS", "Mass conservation uses rho*A*v in steady one-dimensional flow.", "Requires declared density, geometry, velocity and regime."),
    TheoryFamily("FLUID-02", "bernoulli_venturi", "FORMAL_UNDER_ASSUMPTIONS", "Bernoulli/Venturi relations are available under ideal-flow assumptions.", "Viscous/compressible/loss terms cannot be silently ignored."),
    TheoryFamily("FLUID-03", "graph_flow", "MATH_FORMAL", "Directed edge flows induce node balances; zero balance is conservation, not missingness.", "Discrete graph flow is not automatically a continuum fluid."),
    TheoryFamily("RLL-01", "physical_binding", "TOKEN_VAZIO", "Geometry/prime/graph/fluid families may become diagnostic covariates only after an explicit physical contract.", "No numeric coincidence promotes a cosmological claim."),
)


def is_prime(n: int) -> bool:
    n = int(n)
    if n < 2:
        return False
    if n in (2, 3):
        return True
    if n % 2 == 0:
        return False
    d = 3
    while d * d <= n:
        if n % d == 0:
            return False
        d += 2
    return True


def prime_factors(n: int) -> tuple[int, ...]:
    n = int(n)
    if n == 0:
        raise ValueError("prime factorization of zero is undefined")
    n = abs(n)
    if n == 1:
        return ()
    out: list[int] = []
    d = 2
    while d * d <= n:
        while n % d == 0:
            out.append(d)
            n //= d
        d = 3 if d == 2 else d + 2
    if n > 1:
        out.append(n)
    return tuple(out)


def euler_phi(n: int) -> int:
    n = int(n)
    if n < 1:
        raise ValueError("Euler phi requires n >= 1")
    result = n
    for p in sorted(set(prime_factors(n))):
        result -= result // p
    return result


def multiplicative_order(base: int, modulus: int) -> int | None:
    base = int(base)
    modulus = int(modulus)
    if modulus <= 1:
        raise ValueError("modulus must be > 1")
    if gcd(base, modulus) != 1:
        return None
    x = 1
    for k in range(1, euler_phi(modulus) + 1):
        x = (x * base) % modulus
        if x == 1:
            return k
    raise RuntimeError("order must divide Euler phi for coprime finite modulus")


def repunit(length: int, base: int = 10) -> int:
    if length < 1 or base < 2:
        raise ValueError("require length >=1 and base >=2")
    return (base**length - 1) // (base - 1)


def int_to_base(n: int, base: int) -> str:
    if not 2 <= base <= 36:
        raise ValueError("base must be in [2,36]")
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    n = int(n)
    if n == 0:
        return "0"
    sign = "-" if n < 0 else ""
    n = abs(n)
    out: list[str] = []
    while n:
        n, r = divmod(n, base)
        out.append(digits[r])
    return sign + "".join(reversed(out))


def residue_class_window(modulus: int, residue: int = 0, radius: int = 3) -> tuple[int, ...]:
    modulus = int(modulus)
    if modulus <= 0 or radius < 0:
        raise ValueError("positive modulus and non-negative radius required")
    r = int(residue) % modulus
    return tuple(r + k * modulus for k in range(-radius, radius + 1))


def set_carriers() -> dict[str, frozenset[object]]:
    primes = frozenset(PRIME_ATOMS)
    integers = frozenset(int(a.value) for a in census.ATOMS if float(a.value).is_integer())
    composites = frozenset(n for n in integers if n > 1 and not is_prime(n))
    radicals = frozenset(a.name for a in census.ATOMS if "sqrt" in a.name)
    return {
        "prime_atoms": primes,
        "integer_atoms": integers,
        "composite_integer_atoms": composites,
        "radical_names": radicals,
        "void_kinds": frozenset(v.value for v in census.VoidKind),
    }


def set_relation(left: Iterable[object], right: Iterable[object]) -> dict[str, object]:
    a = frozenset(left)
    b = frozenset(right)
    return {
        "left_cardinality": len(a),
        "right_cardinality": len(b),
        "intersection": sorted(a & b, key=str),
        "union_cardinality": len(a | b),
        "left_only": sorted(a - b, key=str),
        "right_only": sorted(b - a, key=str),
        "left_subset_right": a <= b,
        "right_subset_left": b <= a,
        "equal": a == b,
        "cartesian_product_cardinality": len(a) * len(b),
    }


def equivalence_partition(values: Iterable[int], modulus: int) -> dict[int, tuple[int, ...]]:
    m = int(modulus)
    if m <= 0:
        raise ValueError("positive modulus required")
    buckets: dict[int, list[int]] = defaultdict(list)
    for n in values:
        buckets[int(n) % m].append(int(n))
    return {r: tuple(vs) for r, vs in sorted(buckets.items())}


def crt_coordinates(n: int, moduli: Sequence[int]) -> tuple[int, ...]:
    _validate_pairwise_coprime(moduli)
    return tuple(int(n) % int(m) for m in moduli)


def _validate_pairwise_coprime(moduli: Sequence[int]) -> None:
    ms = tuple(int(m) for m in moduli)
    if not ms or any(m <= 1 for m in ms):
        raise ValueError("moduli must all be > 1")
    for i, a in enumerate(ms):
        for b in ms[i + 1 :]:
            if gcd(a, b) != 1:
                raise ValueError("CRT helper requires pairwise-coprime moduli")


def crt_reconstruct(residues: Sequence[int], moduli: Sequence[int]) -> int:
    if len(residues) != len(moduli):
        raise ValueError("residues and moduli must have equal length")
    _validate_pairwise_coprime(moduli)
    ms = tuple(int(m) for m in moduli)
    M = prod(ms)
    total = 0
    for residue, m in zip(residues, ms):
        Mi = M // m
        total += (int(residue) % m) * Mi * pow(Mi, -1, m)
    return total % M


def functional_graph(digit: int, modulus: int, base: int = 10) -> dict[int, int]:
    m = int(modulus)
    if m <= 0:
        raise ValueError("positive modulus required")
    return {r: (int(base) * r + int(digit)) % m for r in range(m)}


def _canonical_cycle(cycle: Sequence[int]) -> tuple[int, ...]:
    c = tuple(cycle)
    if not c:
        return ()
    rotations = [c[i:] + c[:i] for i in range(len(c))]
    return min(rotations)


def functional_cycles(mapping: dict[int, int]) -> tuple[tuple[int, ...], ...]:
    cycles: set[tuple[int, ...]] = set()
    for start in mapping:
        path: list[int] = []
        index: dict[int, int] = {}
        x = start
        while x not in index:
            index[x] = len(path)
            path.append(x)
            x = mapping[x]
        cyc = path[index[x] :]
        cycles.add(_canonical_cycle(cyc))
    return tuple(sorted(cycles))


def cayley_cycle(modulus: int, step: int = 1) -> tuple[tuple[int, int], ...]:
    m = int(modulus)
    s = int(step) % m
    if m < 2 or s == 0:
        raise ValueError("require modulus >=2 and non-zero step")
    return tuple((r, (r + s) % m) for r in range(m))


def undirected_graph_invariants(vertices: Iterable[object], edges: Iterable[tuple[object, object]]) -> dict[str, object]:
    vs = set(vertices)
    adjacency: dict[object, set[object]] = defaultdict(set)
    normalized_edges: set[frozenset[object]] = set()
    for u, v in edges:
        vs.add(u)
        vs.add(v)
        if u == v:
            normalized_edges.add(frozenset((u,)))
            adjacency[u].add(v)
        else:
            normalized_edges.add(frozenset((u, v)))
            adjacency[u].add(v)
            adjacency[v].add(u)
    components = 0
    seen: set[object] = set()
    for root in vs:
        if root in seen:
            continue
        components += 1
        queue = deque([root])
        seen.add(root)
        while queue:
            x = queue.popleft()
            for y in adjacency.get(x, ()):
                if y not in seen:
                    seen.add(y)
                    queue.append(y)
    V = len(vs)
    E = len(normalized_edges)
    beta1 = E - V + components
    return {
        "V": V,
        "E": E,
        "components": components,
        "beta1": beta1,
        "degree_sequence": tuple(sorted((len(adjacency.get(v, ())) for v in vs), reverse=True)),
    }


def factor_incidence_graph(numbers: Iterable[int]) -> dict[str, object]:
    number_nodes: set[str] = set()
    prime_nodes: set[str] = set()
    edges: set[tuple[str, str]] = set()
    for n0 in numbers:
        n = int(n0)
        if abs(n) < 2:
            continue
        nn = f"n:{n}"
        number_nodes.add(nn)
        for p in sorted(set(prime_factors(n))):
            pp = f"p:{p}"
            prime_nodes.add(pp)
            edges.add((nn, pp))
    inv = undirected_graph_invariants(number_nodes | prime_nodes, edges)
    return {
        "number_nodes": tuple(sorted(number_nodes)),
        "prime_nodes": tuple(sorted(prime_nodes)),
        "edges": tuple(sorted(edges)),
        "invariants": inv,
    }


def steady_mass_flux(density: float, area: float, velocity: float) -> float:
    rho, A, v = float(density), float(area), float(velocity)
    if rho <= 0.0 or A <= 0.0:
        raise ValueError("density and area must be positive")
    return rho * A * v


def continuity_residual(
    rho1: float, area1: float, velocity1: float,
    rho2: float, area2: float, velocity2: float,
) -> float:
    return steady_mass_flux(rho1, area1, velocity1) - steady_mass_flux(rho2, area2, velocity2)


def bernoulli_energy_density(pressure: float, density: float, velocity: float, height: float = 0.0, gravity: float = 9.80665) -> float:
    P, rho, v, h, g = map(float, (pressure, density, velocity, height, gravity))
    if rho <= 0.0 or g <= 0.0:
        raise ValueError("density and gravity must be positive")
    return P + 0.5 * rho * v * v + rho * g * h


def venturi_ideal_equal_height_flow(area1: float, area2: float, density: float, delta_pressure: float) -> float:
    A1, A2, rho, dp = map(float, (area1, area2, density, delta_pressure))
    if not (A1 > A2 > 0.0) or rho <= 0.0 or dp < 0.0:
        raise ValueError("require A1>A2>0, density>0 and delta_pressure>=0")
    return A1 * A2 * sqrt((2.0 * dp) / (rho * (A1 * A1 - A2 * A2)))


def reynolds_number(density: float, velocity: float, diameter: float, dynamic_viscosity: float) -> float:
    rho, v, D, mu = map(float, (density, velocity, diameter, dynamic_viscosity))
    if rho <= 0.0 or D <= 0.0 or mu <= 0.0:
        raise ValueError("density, diameter and dynamic viscosity must be positive")
    return rho * abs(v) * D / mu


def graph_flow_balance(edges: Iterable[tuple[str, str, float]]) -> dict[str, float]:
    """Net node balance = inflow - outflow for directed edge flows."""
    balance: dict[str, float] = defaultdict(float)
    for u, v, q0 in edges:
        q = float(q0)
        balance[str(u)] -= q
        balance[str(v)] += q
    return dict(sorted(balance.items()))


def fluid_binding_gate(contract: dict[str, object]) -> dict[str, object]:
    required = (
        "geometry",
        "fluid_identity",
        "density",
        "viscosity",
        "temperature",
        "compressibility_regime",
        "units",
        "boundary_conditions",
        "measurement_source",
        "uncertainty",
        "covariance_or_error_model",
        "falsifier",
    )
    missing = tuple(k for k in required if contract.get(k) in (None, "", (), [], {}))
    return {
        "required": required,
        "missing": missing,
        "state": "READY_FOR_PHYSICAL_TEST" if not missing else PHYSICAL_FLUID_BINDING_STATE,
        "claim_allowed": False,
    }


def prime_decimal_orders() -> dict[int, int | None]:
    return {p: multiplicative_order(10, p) for p in PRIME_ATOMS}


def family_manifest() -> dict[str, object]:
    carriers = set_carriers()
    map_7_by_3 = functional_graph(7, 3)
    map_3_by_7 = functional_graph(3, 7)
    factor_graph = factor_incidence_graph((18, 21, 42, 77, 33, 333, 777, 999, 1001, 111111))
    example_flow = graph_flow_balance((
        ("inlet", "junction", 2.0),
        ("junction", "out_a", 0.75),
        ("junction", "out_b", 1.25),
    ))
    return {
        "schema": "rll.family_theory_bridge.v1",
        "claim_allowed": CLAIM_ALLOWED,
        "source_boundary": "SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM",
        "families": [asdict(f) for f in FAMILIES],
        "family_count": len(FAMILIES),
        "set_theory": {
            "carriers": {k: sorted(v, key=str) for k, v in carriers.items()},
            "prime_subset_of_integer_atoms": carriers["prime_atoms"] <= carriers["integer_atoms"],
            "zero_residue_class_mod7_window": residue_class_window(7, 0, 3),
            "empty_set_cardinality": 0,
            "zero_residue_class_cardinality_infinite": True,
        },
        "number_theory": {
            "prime_factors": {str(n): prime_factors(n) for n in (11, 13, 18, 21, 42, 77, 333, 777, 999, 1001, 111111)},
            "repunit6": repunit(6),
            "repunit6_factorization": prime_factors(repunit(6)),
            "base_points": {"10_base10": int_to_base(10, 10), "7_as_base10": int_to_base(7, 10), "10_base7_value": census.positional_value_10(7)},
        },
        "prime_theory": {
            "base10_orders": prime_decimal_orders(),
            "full_reptend_in_selected_primes": tuple(p for p in PRIME_ATOMS if multiplicative_order(10, p) == p - 1),
        },
        "crt": {
            "21_moduli": CRT_21,
            "42_moduli": CRT_42,
            "sample_20_mod21": crt_coordinates(20, CRT_21),
            "sample_41_mod42": crt_coordinates(41, CRT_42),
            "reconstruct_20_mod21": crt_reconstruct(crt_coordinates(20, CRT_21), CRT_21),
            "reconstruct_41_mod42": crt_reconstruct(crt_coordinates(41, CRT_42), CRT_42),
        },
        "graphs": {
            "rep7_mod3_mapping": map_7_by_3,
            "rep7_mod3_cycles": functional_cycles(map_7_by_3),
            "rep3_mod7_mapping": map_3_by_7,
            "rep3_mod7_cycles": functional_cycles(map_3_by_7),
            "factor_incidence": factor_graph,
            "cayley_z7_step1": cayley_cycle(7, 1),
        },
        "fluids": {
            "formal_equations": {
                "steady_mass_flux": "m_dot = rho*A*v",
                "bernoulli": "P + 0.5*rho*v^2 + rho*g*h = constant",
                "graph_balance": "node_balance = inflow - outflow",
            },
            "example_graph_flow_balance": example_flow,
            "junction_zero_is_conservation_not_missing": abs(example_flow["junction"]) < 1e-15,
            "physical_binding_state": PHYSICAL_FLUID_BINDING_STATE,
        },
        "physical_boundaries": {
            "fluid_binding": PHYSICAL_FLUID_BINDING_STATE,
            "cosmology_binding": PHYSICAL_COSMOLOGY_BINDING_STATE,
            "rule": "Formal mathematics may pass while physical RLL binding remains TOKEN_VAZIO.",
        },
    }


if __name__ == "__main__":
    import json
    print(json.dumps(family_manifest(), indent=2, sort_keys=True))
