#!/usr/bin/env python3
"""Fail-closed validator for exact BITRAF64/toroidal audit claims.

This script proves only finite arithmetic/logical corrections that can be checked
without the missing BITRAF64 implementation artifacts. Implementation-dependent
claims remain TOKEN_VAZIO and therefore production promotion remains blocked.
"""

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
    """Return rank over GF(2) using deterministic Gaussian elimination."""
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
    redundancy_fraction_payload_bits = 53.0 / (1024.0 * 8.0)
    singular_linear = [[1, 1], [1, 1]]

    checks = [
        Check("BTR-06", "PASS_EXACT", math.isclose(math.log(phi), 0.48121182505960347, rel_tol=0, abs_tol=1e-15), math.log(phi), 0.48121182505960347, "Spectral growth rate for canonical Fibonacci companion matrix."),
        Check("BTR-04", "PASS_EXACT_CORRECTION", gf2_rank(singular_linear) == 1, gf2_rank(singular_linear), 1, "Linear singular counterexample disproves linearity => invertibility."),
        Check("BTR-11", "FAIL_EXACT_CLAIM", not math.isclose(r_formula, 0.963999, rel_tol=0, abs_tol=1e-6), r_formula, "!= 0.963999", "Declared formula does not derive the target constant."),
        Check("BTR-12", "FAIL_EXACT_CLAIM", math.gcd(6000, 2057) == 1, math.gcd(6000, 2057), 1, "Reported value 16 is false."),
        Check("BTR-13", "PASS_EXACT", math.gcd(42, 60) == 6, math.gcd(42, 60), 6, "Exact integer arithmetic."),
        Check("BTR-14a", "FAIL_EXACT_CLAIM", math.isclose(redundancy_bit_per_byte, 0.0517578125, rel_tol=0, abs_tol=1e-15), redundancy_bit_per_byte, 0.0517578125, "53 redundancy bits / 1024 payload bytes."),
        Check("BTR-14b", "PASS_EXACT_CORRECTION", math.isclose(redundancy_fraction_payload_bits * 100.0, 0.64697265625, rel_tol=0, abs_tol=1e-12), redundancy_fraction_payload_bits * 100.0, 0.64697265625, "Redundancy bits as percent of 8192 payload bits."),
        Check("BTR-17", "PASS_EXACT_BOUND", max(i + j + k for i in range(10) for j in range(10) for k in range(10)) == 27, 28, 28, "Only 28 distinct exponents 0..27 are needed for a direct spiral-weight LUT."),
    ]

    unresolved = [
        {
            "id": "BTR-01",
            "state": "TOKEN_VAZIO",
            "missing": "actual transition code + boundary fixtures proving mod-10 wrap on every spatial axis",
        },
        {
            "id": "BTR-05",
            "state": "TOKEN_VAZIO",
            "missing": "actual GF(2) transform matrices/operators + full-rank and round-trip receipts",
        },
        {
            "id": "BTR-08",
            "state": "TOKEN_VAZIO",
            "missing": "executable psi-chi-rho-delta-sigma-omega recurrence + perturbation/stability protocol",
        },
        {
            "id": "BTR-10",
            "state": "TOKEN_VAZIO",
            "missing": "complete ECC parity-check mapping + exhaustive 8192 single-bit error injection receipt",
        },
        {
            "id": "BTR-15",
            "state": "TOKEN_VAZIO",
            "missing": "declared dataset/seed + entropy and autocorrelation raw measurements with uncertainty",
        },
        {
            "id": "BTR-16",
            "state": "TOKEN_VAZIO",
            "missing": "homogeneous physical-device SIMD/cache/LUT benchmark receipts",
        },
        {
            "id": "BTR-18",
            "state": "TOKEN_VAZIO",
            "missing": "explicit package-DAG to toroidal-lattice embedding and preserved-invariant metric",
        },
    ]

    exact_checks_pass = all(c.passed for c in checks)
    return {
        "schema": "rafaelia.bitraf64.toroidal.audit.v1",
        "global_state": "OBSERVED_LIMITED",
        "claim_allowed": False,
        "production_ready": False,
        "exact_checks_pass": exact_checks_pass,
        "checks": [asdict(c) for c in checks],
        "unresolved": unresolved,
        "promotion_order": [
            "GF2 rank and round-trip",
            "ECC unique syndromes / d_min and exhaustive error injection",
            "feedback-loop stability",
            "entropy/autocorrelation/avalanche",
            "physical SIMD/cache/LUT benchmark",
            "package-DAG embedding",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--strict", action="store_true", help="return 2 while production promotion is blocked")
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
