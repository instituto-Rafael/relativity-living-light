#!/usr/bin/env python3
"""RAFAELIA research V1: deterministic, offline coprime/prime geometry audit.

Proves only finite arithmetic checks; NOT a proof of prime-distribution novelty
or of any physical/cosmological model. Python standard library only.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
from pathlib import Path

MODULI = (3, 7, 10, 13, 14, 35, 50, 70, 140, 1400)
GLOBAL_MODULUS = 54600
GLOBAL_PHI = 11520
OBSERVED_MODULI = (70, 210, 350, 1400, GLOBAL_MODULUS)
EXPECTED_PHI = {70: 24, 210: 48, 350: 120, 1400: 480, 54600: 11520}
EXCEPTIONAL_PRIMES = (2, 3, 5, 7, 13)


def units(n: int) -> list[int]:
    if n < 2:
        raise ValueError("n must be >= 2")
    return [k for k in range(1, n) if math.gcd(k, n) == 1]


def orbit_vertices(n: int, step: int) -> list[int]:
    if n < 2 or not 0 < step < n:
        raise ValueError("expect n>=2 and 0<step<n")
    seen: set[int] = set()
    pos = 0
    vertices = []
    while pos not in seen:
        seen.add(pos)
        vertices.append(pos)
        pos = (pos + step) % n
    if pos != 0:
        raise AssertionError("orbit failed to return to origin")
    return vertices


def is_prime_trial(n: int) -> bool:
    if n < 2:
        return False
    for d in range(2, math.isqrt(n) + 1):
        if n % d == 0:
            return False
    return True


def prime_sieve(limit: int) -> bytearray:
    if limit < 2:
        raise ValueError("limit must be >= 2")
    flags = bytearray(b"\x01") * (limit + 1)
    flags[:2] = b"\x00\x00"
    for k in range(2, math.isqrt(limit) + 1):
        if flags[k]:
            flags[k * k:limit + 1:k] = b"\x00" * ((limit - k * k) // k + 1)
    return flags


def compute(limit: int) -> dict:
    if not 1000 <= limit <= 1000000:
        raise ValueError("experimental limit must be in [1000, 1000000]")

    assert math.lcm(*MODULI) == GLOBAL_MODULUS
    global_units = units(GLOBAL_MODULUS)
    assert len(global_units) == GLOBAL_PHI

    # Two independent finite checks: explicit fibers and totient ratios.
    projection = {}
    for m in OBSERVED_MODULI:
        assert GLOBAL_MODULUS % m == 0
        local_units = units(m)
        assert len(local_units) == EXPECTED_PHI[m]
        expected = GLOBAL_PHI // len(local_units)
        counts = dict.fromkeys(local_units, 0)
        for r in global_units:
            counts[r % m] += 1
        assert len(set(counts.values())) == 1 and set(counts.values()) == {expected}
        projection[str(m)] = {
            "phi": len(local_units),
            "fiber_count_per_unit": expected,
            "projection_verified_finite": True,
        }

    orbits = []
    for n, step in ((7, 2), (8, 2), (1400, 3), (1400, 7)):
        observed = len(orbit_vertices(n, step))
        predicted = n // math.gcd(n, step)
        assert observed == predicted
        orbits.append({
            "n": n, "step": step, "gcd": math.gcd(n, step),
            "visited": observed, "predicted": predicted,
            "full_cycle": observed == n,
        })

    flags = prime_sieve(limit)
    # Completely independent trial division for a bounded oracle sample.
    for n in range(2, min(limit, 10000) + 1):
        assert bool(flags[n]) == is_prime_trial(n), f"sieve disagreement at {n}"

    n_primes = sum(flags)
    expected_exceptional = [p for p in EXCEPTIONAL_PRIMES if p <= limit]
    observed_exceptional = [p for p in expected_exceptional if flags[p]]
    assert observed_exceptional == expected_exceptional
    retained = [n for n in range(2, limit + 1) if math.gcd(n, GLOBAL_MODULUS) == 1]
    retained_prime_count = sum(flags[n] for n in retained)
    assert retained_prime_count + len(observed_exceptional) == n_primes
    retained_composite_count = len(retained) - retained_prime_count
    assert retained_composite_count > 0

    # Essential negative control: 121 is a coprime candidate, not a prime.
    assert math.gcd(121, GLOBAL_MODULUS) == 1
    assert not flags[121]
    # 169=13² must be rejected by the chosen modulus.
    assert math.gcd(169, GLOBAL_MODULUS) != 1

    prime_hist = {m: {r: 0 for r in units(m)} for m in OBSERVED_MODULI}
    for n in range(2, limit + 1):
        if flags[n] and math.gcd(n, GLOBAL_MODULUS) == 1:
            for m in OBSERVED_MODULI:
                prime_hist[m][n % m] += 1
    for m, histogram in prime_hist.items():
        assert sum(histogram.values()) == retained_prime_count
    for m in OBSERVED_MODULI:
        expected_projection = {r: 0 for r in units(m)}
        for global_r, count in prime_hist[GLOBAL_MODULUS].items():
            expected_projection[global_r % m] += count
        assert expected_projection == prime_hist[m]

    stats = {}
    for m, counts in prime_hist.items():
        values = list(counts.values())
        stats[str(m)] = {
            "classes": len(values),
            "occupied_classes": sum(v > 0 for v in values),
            "min_prime_count": min(values),
            "max_prime_count": max(values),
            "sum_primes": sum(values),
            "max_minus_min": max(values) - min(values),
            "interpretation": "finite-sample descriptive only; not significance or novelty",
        }

    return {
        "schema": "RAFAELIA_PRIME_GEOMETRY_V1",
        "source": "finite arithmetic protocol, no personal data",
        "global_modulus": GLOBAL_MODULUS,
        "global_phi": GLOBAL_PHI,
        "input_moduli": list(MODULI),
        "limit_inclusive": limit,
        "projection": projection,
        "orbits": orbits,
        "prime_filter": {
            "all_primes_count": n_primes,
            "modulus_prime_exceptions": observed_exceptional,
            "coprime_candidates_count": len(retained),
            "actual_primes_among_candidates": retained_prime_count,
            "composites_among_candidates": retained_composite_count,
            "false_negatives_after_exceptions": 0,
            "candidate_precision_numerator": retained_prime_count,
            "candidate_precision_denominator": len(retained),
            "negative_control_121_is_coprime_and_composite": True,
            "negative_control_169_rejected_by_modulus": True,
        },
        "finite_prime_histogram_stats": stats,
        "spectral_dirichlet_character_test": "NOT_EXECUTED",
        "cosmological_model_test": "NOT_EXECUTED",
        "novel_invariant_proof": "TOKEN_VAZIO_PROOF",
        "claim_allowed": False,
        "gate": "PASS_SCOPED_FINITE_ARITHMETIC_ONLY",
    }


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--limit", type=int, default=100000)
    parser.add_argument("--out-dir", type=Path, default=Path("artifacts/prime_geometry"))
    args = parser.parse_args()
    result = compute(args.limit)
    args.out_dir.mkdir(parents=True, exist_ok=True)
    report_path = args.out_dir / "report.json"
    payload = (json.dumps(result, ensure_ascii=False, indent=2, sort_keys=True) + "\n").encode("utf-8")
    report_path.write_bytes(payload)
    digest = hashlib.sha256(payload).hexdigest()
    receipt = (
        "# RAFAELIA Ω · PRIME_GEOMETRY V1 · FINITE RECEIPT\n\n"
        f"- finite_math_gate: `{result['gate']}`\n"
        "- github_ci_exact_head: `NOT_EXECUTED_UNLESS_RUN_ID_OBSERVED`\n"
        "- physical_RLL_claim: `NOT_EXECUTED`\n"
        "- new_mathematical_theorem: `TOKEN_VAZIO_PROOF`\n"
        "- claim_allowed: `false`\n"
        f"- limit_inclusive: `{args.limit}`\n"
        f"- candidates: `{result['prime_filter']['coprime_candidates_count']}`\n"
        f"- confirmed_primes_among_candidates: `{result['prime_filter']['actual_primes_among_candidates']}`\n"
        "- report_digest_type: `SHA256_OF_GENERATED_REPORT_BYTES`\n"
        f"- report_sha256: `{digest}`\n"
        "- cryptographic_signing: `NOT_EXECUTED`\n"
        "- predecessor: `TOKEN_VAZIO_NEW_EXPERIMENT`\n"
        "- rollback: `remove proposed workflow from branch before promotion; never delete existing history`\n"
    )
    (args.out_dir / "receipt.md").write_text(receipt, encoding="utf-8")
    print(json.dumps({
        "gate": result["gate"],
        "limit": args.limit,
        "report_sha256": digest,
        "candidates": result["prime_filter"]["coprime_candidates_count"],
        "primes_among_candidates": result["prime_filter"]["actual_primes_among_candidates"],
        "claim_allowed": False,
    }, sort_keys=True))


if __name__ == "__main__":
    main()