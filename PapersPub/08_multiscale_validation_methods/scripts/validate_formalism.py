#!/usr/bin/env python3
"""Deterministic validator for the 7D/42-hyperform paper.

Scope: exact finite arithmetic, character counts, entropy, indexing and declared
conventions. This script MUST NOT promote physical, causal, cosmological or
cryptographic claims.
"""

from __future__ import annotations

import argparse
import json
import math
import platform
import sys
import unicodedata
from collections import Counter
from pathlib import Path
from typing import Any

BITRAF64 = (
    "AΔBΩΔTTΦIIBΩΔΣΣRΩRΔΔBΦΦFΔTTRRFΔBΩΣΣAFΦARΣFΦIΔRΦIFBRΦΩFIΦΩΩFΣFAΦΔ"
)
ALPHABET_ORDER = ["Σ", "Ω", "Δ", "Φ", "B", "I", "T", "R", "A", "F"]
SEQUENCES = ["0001123", "01123", "0123"]
OPERATORS = ["READ", "FEED", "EXPAND", "VALIDATE", "EXECUTE", "ALIGN"]


def empirical_entropy(text: str) -> float:
    if not text:
        return 0.0
    counts = Counter(text)
    n = len(text)
    return -sum((count / n) * math.log2(count / n) for count in counts.values())


def distinct_permutations(text: str) -> int:
    result = math.factorial(len(text))
    for count in Counter(text).values():
        result //= math.factorial(count)
    return result


def check(name: str, observed: Any, expected: Any, *, tolerance: float | None = None) -> dict[str, Any]:
    if tolerance is None:
        passed = observed == expected
    else:
        passed = math.isclose(float(observed), float(expected), rel_tol=0.0, abs_tol=tolerance)
    return {
        "name": name,
        "observed": observed,
        "expected": expected,
        "passed": passed,
    }


def build_report() -> dict[str, Any]:
    checks: list[dict[str, Any]] = []

    expected_sequence_data = {
        "0001123": {"length": 7, "multiplicity": [3, 2, 1, 1], "permutations": 420, "entropy": 1.8423709931771084},
        "01123": {"length": 5, "multiplicity": [1, 2, 1, 1], "permutations": 60, "entropy": 1.9219280948873623},
        "0123": {"length": 4, "multiplicity": [1, 1, 1, 1], "permutations": 24, "entropy": 2.0},
    }

    sequence_results: dict[str, Any] = {}
    for text in SEQUENCES:
        counts = Counter(text)
        multiplicity = [counts[str(i)] for i in range(4)]
        row = {
            "length": len(text),
            "multiplicity_0_1_2_3": multiplicity,
            "distinct_permutations": distinct_permutations(text),
            "entropy_bits_per_symbol": empirical_entropy(text),
        }
        sequence_results[text] = row
        expected = expected_sequence_data[text]
        checks.extend(
            [
                check(f"{text}.length", row["length"], expected["length"]),
                check(f"{text}.multiplicity", multiplicity, expected["multiplicity"]),
                check(f"{text}.permutations", row["distinct_permutations"], expected["permutations"]),
                check(f"{text}.entropy", row["entropy_bits_per_symbol"], expected["entropy"], tolerance=1e-12),
            ]
        )

    matrix_results = {
        "A_states": 8 * 5,
        "B_states": 7 * 3,
        "pairs_A": math.comb(40, 2),
        "pairs_B": math.comb(21, 2),
        "cross_A_B": 40 * 21,
        "pairs_of_pairs": math.comb(40, 2) * math.comb(21, 2),
        "A_adjacent_2x2": (8 - 1) * (5 - 1),
        "B_adjacent_2x2": (7 - 1) * (3 - 1),
        "positional_permutations_per_2x2": math.factorial(4),
        "A_adjacent_positional_arrangements": (8 - 1) * (5 - 1) * math.factorial(4),
        "B_adjacent_positional_arrangements": (7 - 1) * (3 - 1) * math.factorial(4),
        "A_general_positional_arrangements": math.comb(8, 2) * math.comb(5, 2) * math.factorial(4),
        "B_general_positional_arrangements": math.comb(7, 2) * math.comb(3, 2) * math.factorial(4),
        "tensor_elements": 8 * 5 * 7 * 3,
    }
    expected_matrix = {
        "A_states": 40,
        "B_states": 21,
        "pairs_A": 780,
        "pairs_B": 210,
        "cross_A_B": 840,
        "pairs_of_pairs": 163800,
        "A_adjacent_2x2": 28,
        "B_adjacent_2x2": 12,
        "positional_permutations_per_2x2": 24,
        "A_adjacent_positional_arrangements": 672,
        "B_adjacent_positional_arrangements": 288,
        "A_general_positional_arrangements": 6720,
        "B_general_positional_arrangements": 1512,
        "tensor_elements": 840,
    }
    checks.extend(check(f"matrices.{key}", value, expected_matrix[key]) for key, value in matrix_results.items())

    index_A = {5 * r + c for r in range(8) for c in range(5)}
    index_B = {3 * u + v for u in range(7) for v in range(3)}
    checks.extend(
        [
            check("index_A.complete", sorted(index_A), list(range(40))),
            check("index_B.complete", sorted(index_B), list(range(21))),
        ]
    )

    hyperforms = [f"H_{dimension}_{operator}" for dimension in range(1, 8) for operator in OPERATORS]
    checks.extend(
        [
            check("hyperforms.count", len(hyperforms), 42),
            check("hyperforms.unique", len(set(hyperforms)), 42),
        ]
    )

    base7_results = {
        "70_times_7": 70 * 7,
        "half_axis_70": 70 // 2,
        "half_axis_70_base7": numpy_free_base(35, 7),
        "half_product_490": 490 // 2,
        "half_product_490_base7": numpy_free_base(245, 7),
    }
    checks.extend(
        [
            check("base7.70_times_7", base7_results["70_times_7"], 490),
            check("base7.half_axis", base7_results["half_axis_70"], 35),
            check("base7.35", base7_results["half_axis_70_base7"], "50"),
            check("base7.half_product", base7_results["half_product_490"], 245),
            check("base7.245", base7_results["half_product_490_base7"], "500"),
        ]
    )

    bitraf_nfc = unicodedata.normalize("NFC", BITRAF64)
    bitraf_counts = Counter(bitraf_nfc)
    bitraf_vector = [bitraf_counts[symbol] for symbol in ALPHABET_ORDER]
    bitraf_results = {
        "unicode_normalization": "NFC",
        "codepoint_length": len(bitraf_nfc),
        "alphabet_order": ALPHABET_ORDER,
        "frequency_vector": bitraf_vector,
        "alphabet_exact": sorted(bitraf_counts) == sorted(ALPHABET_ORDER),
        "entropy_bits_per_symbol": empirical_entropy(bitraf_nfc),
        "uniform_10_symbol_max_entropy": math.log2(10),
    }
    checks.extend(
        [
            check("bitraf.length", bitraf_results["codepoint_length"], 64),
            check("bitraf.frequency_vector", bitraf_vector, [6, 7, 9, 9, 5, 5, 4, 7, 4, 8]),
            check("bitraf.frequency_sum", sum(bitraf_vector), 64),
            check("bitraf.alphabet_exact", bitraf_results["alphabet_exact"], True),
            check("bitraf.entropy", bitraf_results["entropy_bits_per_symbol"], 3.26420820487549, tolerance=1e-12),
        ]
    )

    geometry_results = {
        "sqrt3_over_2": math.sqrt(3) / 2,
        "sqrt_3_over_2": math.sqrt(3 / 2),
        "first_is_contractive": math.sqrt(3) / 2 < 1,
        "second_is_expansive": math.sqrt(3 / 2) > 1,
    }
    checks.extend(
        [
            check("geometry.sqrt3_over_2", geometry_results["sqrt3_over_2"], 0.8660254037844386, tolerance=1e-15),
            check("geometry.sqrt_3_over_2", geometry_results["sqrt_3_over_2"], 1.224744871391589, tolerance=1e-15),
            check("geometry.contract", geometry_results["first_is_contractive"], True),
            check("geometry.expand", geometry_results["second_is_expansive"], True),
        ]
    )

    exact_pass = all(item["passed"] for item in checks)
    return {
        "schema_version": "1.0",
        "paper": "from_observed_void_to_recurrence_7d_42_hyperforms",
        "claim_allowed": False,
        "validation_scope": "exact finite arithmetic and symbolic invariants only",
        "runtime": {
            "python": sys.version.split()[0],
            "implementation": platform.python_implementation(),
            "platform": platform.platform(),
            "unicode_version": unicodedata.unidata_version,
        },
        "results": {
            "sequences": sequence_results,
            "matrices_and_tensor": matrix_results,
            "hyperforms_count": len(hyperforms),
            "base7": base7_results,
            "bitraf64": bitraf_results,
            "geometry": geometry_results,
        },
        "checks": checks,
        "summary": {
            "checks_total": len(checks),
            "checks_passed": sum(item["passed"] for item in checks),
            "checks_failed": sum(not item["passed"] for item in checks),
            "exact_invariants_status": "PASS" if exact_pass else "FAIL",
            "poincare_recurrence": "TOKEN_VAZIO: invariant finite measure and measure preservation not demonstrated",
            "causal_component": "TOKEN_VAZIO: no structural causal model or intervention",
            "physical_cosmos_claim": "PROHIBITED_BY_SCOPE",
            "magnetic_molecular_claim": "TOKEN_VAZIO: no molecule, units, dataset or experiment",
            "bitraf_cryptographic_security": "TOKEN_VAZIO: symbolic seal is not a security proof",
        },
    }


def numpy_free_base(number: int, base: int) -> str:
    if number == 0:
        return "0"
    if number < 0 or base < 2 or base > 36:
        raise ValueError("number must be non-negative and base must be in [2, 36]")
    digits = "0123456789ABCDEFGHIJKLMNOPQRSTUVWXYZ"
    out: list[str] = []
    value = number
    while value:
        value, remainder = divmod(value, base)
        out.append(digits[remainder])
    return "".join(reversed(out))


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="PapersPub/08_multiscale_validation_methods/results/validation_report.json",
    )
    args = parser.parse_args()

    report = build_report()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps(report["summary"], indent=2, ensure_ascii=False))
    return 0 if report["summary"]["exact_invariants_status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
