#!/usr/bin/env python3
"""Fail-closed validator for exact BITRAF64/toroidal audit claims."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from typing import Any


@dataclass(frozen=True)
class Check:
    id: str
    state: str
    passed: bool
    observed: Any
    expected: Any
    note: str


def gf2_rank(matrix: list[list[int]]) -> int:
    if not matrix:
        return 0
    a = [[v & 1 for v in row] for row in matrix]
    rows = len(a)
    cols = len(a[0])
    rank = 0
    for col in range(cols):
        pivot = next((r for r in range(rank, rows) if a[r][col]), None)
        if pivot is None:
            continue
        a[rank], a[pivot] = a[pivot], a[rank]
        for r in range(rows):
            if r != rank and a[r][col]:
                a[r] = [x ^ y for x, y in zip(a[r], a[rank])]
        rank += 1
        if rank == rows:
            break
    return rank


def build_report() -> dict[str, Any]:
    phi = (1.0 + math.sqrt(5.0)) / 2.0
    r_formula = phi * sum(range(1, 6)) / (math.pi * 42.0)
    redundancy_bit_per_byte = 53.0 / 1024.0
    singular_linear = [[1, 1], [1, 1]]
    checks = [
        Check("BTR-06", "PASS_EXACT", math.isclose(math.log(phi), 0.48121182505960347, rel_tol=0, abs_tol=1e-15), math.log(phi), 0.48121182505960347, "Canonical Fibonacci spectral growth."),
        Check("BTR-04", "PASS_EXACT_CORRECTION", gf2_rank(singular_linear) == 1, gf2_rank(singular_linear), 1, "Linear singular counterexample."),
        Check("BTR-11", "FAIL_EXACT_CLAIM", not math.isclose(r_formula, 0.963999, rel_tol=0, abs_tol=1e-6), r_formula, "!= 0.963999", "Published expression does not derive declared target."),
        Check("BTR-12", "FAIL_EXACT_CLAIM", math.gcd(6000, 2057) == 1, math.gcd(6000, 2057), 1, "Reported value 16 is false."),
        Check("BTR-13", "PASS_EXACT", math.gcd(42, 60) == 6, math.gcd(42, 60), 6, "Exact arithmetic."),
        Check("BTR-14", "FAIL_EXACT_CLAIM", math.isclose(redundancy_bit_per_byte, 0.0517578125, rel_tol=0, abs_tol=1e-15), redundancy_bit_per_byte, 0.0517578125, "53 bits / 1024 bytes."),
        Check("BTR-17", "PASS_EXACT_BOUND", max(i + j + k for i in range(10) for j in range(10) for k in range(10)) == 27, 28, 28, "28 distinct exponents 0..27."),
    ]
    unresolved = [
        "actual GF(2) transforms + rank/round-trip",
        "ECC d_min/unique syndromes + 8192 unit-error injection",
        "psi-chi-rho-delta-sigma-omega stability",
        "entropy/autocorrelation/avalanche measurements",
        "physical SIMD/cache/LUT benchmark",
        "real package-DAG embedding",
        "independent replication",
    ]
    return {
        "schema": "rafaelia.bitraf64.toroidal.audit.v1",
        "global_state": "OBSERVED_LIMITED",
        "claim_allowed": False,
        "production_ready": False,
        "exact_checks_pass": all(c.passed for c in checks),
        "checks": [asdict(c) for c in checks],
        "token_vazio": unresolved,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    report = build_report()
    print(json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True))
    if not report["exact_checks_pass"]:
        return 1
    if args.strict and not report["production_ready"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
