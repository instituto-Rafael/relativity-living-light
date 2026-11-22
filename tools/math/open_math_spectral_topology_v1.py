#!/usr/bin/env python3
"""Two bounded, falsifiable RAFAELIA mathematics research experiments.

Experiment A: prime-residue Fourier *exploration* using a conditional null that
preserves mod-70 candidate and prime totals while testing finer mod-350 signal.
Experiment B: exact F2 homology of a tetrahedral sphere and triangulated torus.

No proof of a new theorem, no claims about Riemann, no empirical generalization.
Python standard library only; synthetic arithmetic inputs; offline operation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import platform
import random
import tempfile
from collections import defaultdict
from pathlib import Path

MASTER_MODULUS = 54600
COARSE_MODULUS = 70
FINE_MODULUS = 350
FOURIER_MODES = tuple(range(1, 17))  # fixed before examining outcomes
SCHEMA = "rll.open_math_spectral_topology.v1"


def sieve(limit: int) -> bytearray:
    if limit < 2:
        raise ValueError("limit must be >= 2")
    flags = bytearray(b"\x01") * (limit + 1)
    flags[:2] = b"\x00\x00"
    for d in range(2, math.isqrt(limit) + 1):
        if flags[d]:
            flags[d * d:limit + 1:d] = b"\x00" * ((limit - d*d)//d + 1)
    return flags


def admissible_residues(modulus: int) -> list[int]:
    return [r for r in range(modulus) if math.gcd(r, modulus) == 1]


def conditional_profile(limit: int) -> tuple[dict[int, list[int]], dict[int, int], dict[int, int], int]:
    """Observed finite counts; baseline holds each mod-70 prime total fixed."""
    flags = sieve(limit)
    groups: dict[int, list[int]] = defaultdict(list)
    for n in range(2, limit + 1):
        if math.gcd(n, MASTER_MODULUS) == 1:
            groups[n % COARSE_MODULUS].append(n)
    fine_candidates: dict[int, int] = defaultdict(int)
    fine_observed: dict[int, int] = defaultdict(int)
    coarse_prime: dict[int, int] = {}
    for coarse, values in groups.items():
        coarse_prime[coarse] = sum(flags[v] for v in values)
        for v in values:
            fine_candidates[v % FINE_MODULUS] += 1
            fine_observed[v % FINE_MODULUS] += flags[v]
    return dict(groups), coarse_prime, dict(fine_candidates), dict(fine_observed)


def conditional_expectations(groups: dict[int, list[int]],
                             coarse_prime: dict[int, int],
                             fine_candidates: dict[int, int]) -> dict[int, float]:
    return {r: count * coarse_prime[r % COARSE_MODULUS]
            / len(groups[r % COARSE_MODULUS])
            for r, count in fine_candidates.items()}


def fourier_power(counts: dict[int, int], expectations: dict[int, float],
                  modes: tuple[int, ...] = FOURIER_MODES) -> dict:
    """Additive Fourier on the declared Z/350Z embedding, not Dirichlet L-data."""
    if not modes or not expectations:
        raise ValueError("nonempty frequencies and expected counts required")
    residuals = [(r, counts.get(r, 0) - expected)
                 for r, expected in sorted(expectations.items())]
    denominator = sum(expectations.values())
    if denominator <= 0:
        return {"max_power": 0.0, "winning_mode": None, "mode_count": len(modes)}
    powers = []
    for mode in modes:
        real = math.fsum(delta * math.cos(2 * math.pi * mode * r / FINE_MODULUS)
                         for r, delta in residuals)
        imag = math.fsum(delta * math.sin(2 * math.pi * mode * r / FINE_MODULUS)
                         for r, delta in residuals)
        powers.append((real*real + imag*imag) / denominator)
    win = max(range(len(powers)), key=lambda i: powers[i])
    return {"max_power": powers[win], "winning_mode": modes[win],
            "mode_count": len(modes)}


def conditional_randomization(limit: int = 10000, draws: int = 127,
                              seed: int = 20261121) -> dict:
    if not 1000 <= limit <= 20000 or not 9 <= draws <= 511:
        raise ValueError("bounded limit [1000,20000], draws [9,511]")
    if not 0 <= seed < (1 << 63):
        raise ValueError("seed out of range")
    groups, coarse_prime, fine_candidates, fine_observed = conditional_profile(limit)
    expectations = conditional_expectations(groups, coarse_prime, fine_candidates)
    rng = random.Random(seed)
    original = fourier_power(fine_observed, expectations)
    exceed = 0
    max_null = 0.0
    # Each permutation selects exactly k prime labels from each fixed mod-70
    # candidate group. This preserves coarse counts and all CRT projections.
    for _ in range(draws):
        shuffled: dict[int, int] = defaultdict(int)
        for coarse, members in sorted(groups.items()):
            for selected in rng.sample(members, coarse_prime[coarse]):
                shuffled[selected % FINE_MODULUS] += 1
        assert sum(shuffled.values()) == sum(coarse_prime.values())
        assert all(sum(shuffled.get(r, 0) for r in fine_candidates
                       if r % COARSE_MODULUS == coarse) == coarse_prime[coarse]
                   for coarse in groups)
        value = fourier_power(shuffled, expectations)["max_power"]
        exceed += value >= original["max_power"] - 1e-12
        max_null = max(max_null, value)
    return {
        "interpretation": "finite exploratory conditional null; not confirmatory significance",
        "global_modulus": MASTER_MODULUS, "coarse_modulus": COARSE_MODULUS,
        "fine_modulus": FINE_MODULUS, "limit_inclusive": limit,
        "candidate_count": sum(len(x) for x in groups.values()),
        "primes_among_candidates": sum(coarse_prime.values()),
        "composites_among_candidates": sum(len(x) for x in groups.values()) - sum(coarse_prime.values()),
        "coarse_classes": len(groups), "fine_classes": len(fine_candidates),
        "conditional_null": "uniform labels within each observed mod-70 class, fixed class prime counts",
        "fourier_domain": "additive Z/350Z, fixed modes 1..16; NOT Dirichlet characters",
        "statistic": "max normalized Fourier power (16 predeclared modes)",
        "observed_max_power": original["max_power"],
        "winning_mode": original["winning_mode"],
        "draws": draws, "seed": seed, "null_exceedances": exceed,
        "max_null_power": max_null,
        "empirical_tail_fraction": (exceed + 1) / (draws + 1),
        "minimum_tail_resolution": 1 / (draws + 1),
        "hypothesis_H0": "no incremental fine-modulus structure under the conditional label null",
        "hypothesis_H1": "extra structured power relative to this specific null only",
        "limitations": ["post-selection and finite-range effects not excluded",
                        "conditional shuffle is not a complete prime-race null",
                        "no conductor-preserving character surrogate",
                        "no independent holdout or general asymptotic statement"],
        "claim_allowed": False, "state": "EXPLORATORY_ONLY",
    }


def gf2_rank(columns: list[int]) -> int:
    """Exact column rank over F2, using bitset pivot elimination."""
    pivots: dict[int, int] = {}
    for col in columns:
        while col:
            high = col.bit_length() - 1
            if high not in pivots:
                pivots[high] = col
                break
            col ^= pivots[high]
    return len(pivots)


def homology_f2(faces: list[tuple[int, int, int]]) -> dict:
    if not faces or any(len(set(f)) != 3 or len(f) != 3 for f in faces):
        raise ValueError("triangular faces with three distinct vertices required")
    normalized = {tuple(sorted(f)) for f in faces}
    if len(normalized) != len(faces):
        raise ValueError("duplicate triangular faces")
    vertices = sorted({v for f in faces for v in f})
    if len(vertices) > 256 or len(faces) > 512:
        raise ValueError("bounded finite complex only")
    v_index = {v: i for i, v in enumerate(vertices)}
    edges = sorted({tuple(sorted((a, b))) for a, b, c in faces
                    for a, b in ((a, b), (b, c), (c, a))})
    e_index = {e: i for i, e in enumerate(edges)}
    boundary1 = [(1 << v_index[a]) ^ (1 << v_index[b]) for a, b in edges]
    boundary2 = []
    for a, b, c in faces:
        edge_bits = 0
        chain_boundary = 0
        for u, v in ((a, b), (b, c), (c, a)):
            idx = e_index[tuple(sorted((u, v)))]
            edge_bits ^= 1 << idx
            chain_boundary ^= boundary1[idx]
        if chain_boundary:
            raise AssertionError("boundary of boundary must be zero")
        boundary2.append(edge_bits)
    n0, n1, n2 = len(vertices), len(edges), len(faces)
    r1, r2 = gf2_rank(boundary1), gf2_rank(boundary2)
    betti = (n0-r1, n1-r1-r2, n2-r2)
    euler = n0-n1+n2
    assert euler == betti[0]-betti[1]+betti[2]
    assert all(b >= 0 for b in betti)
    return {"vertices": n0, "edges": n1, "faces": n2,
            "boundary1_rank": r1, "boundary2_rank": r2,
            "boundary_squared_zero": True,
            "euler_characteristic": euler, "betti_f2": list(betti)}


def tetrahedron_boundary() -> list[tuple[int, int, int]]:
    return [(0, 1, 2), (0, 1, 3), (0, 2, 3), (1, 2, 3)]


def periodic_torus(n: int = 3) -> list[tuple[int, int, int]]:
    if not 3 <= n <= 8:
        raise ValueError("n must be 3..8 to avoid degenerate quotient triangulations")
    point = lambda x, y: (y % n)*n + (x % n)
    faces = []
    for y in range(n):
        for x in range(n):
            a, b = point(x, y), point(x+1, y)
            c, d = point(x+1, y+1), point(x, y+1)
            faces.extend(((a, b, c), (a, c, d)))
    return faces


def topology_experiment(grid: int = 3) -> dict:
    sphere = homology_f2(tetrahedron_boundary())
    torus_faces = periodic_torus(grid)
    torus = homology_f2(torus_faces)
    punctured = homology_f2(torus_faces[:-1])
    assert sphere["betti_f2"] == [1, 0, 1]
    assert torus["betti_f2"] == [1, 2, 1]
    assert punctured["betti_f2"] == [1, 2, 0]
    assert [sphere["euler_characteristic"], torus["euler_characteristic"],
            punctured["euler_characteristic"]] == [2, 0, -1]
    return {"grid": grid, "coefficients": "F2", "sphere": sphere,
            "torus": torus, "punctured_torus_negative_control": punctured,
            "hypothesis": "finite triangulated sphere and torus are distinguished by F2 Betti invariants",
            "state": "FINITE_CLASSICAL_IDENTITY_VERIFIED", "new_topological_theorem": "NOT_CLAIMED",
            "claim_allowed": False}


def compute(limit: int = 10000, draws: int = 127,
            seed: int = 20261121, grid: int = 3) -> dict:
    return {"schema": SCHEMA, "source": "synthetic bounded arithmetic and explicit finite triangulations",
            "spectral_exploration": conditional_randomization(limit, draws, seed),
            "topology_exact": topology_experiment(grid),
            "source_disclosure": "finite synthetic only; no corpus or external observational data",
            "independent_replication": "NOT_RUN", "physical_RLL_link": "NOT_TESTED",
            "new_theorem": "TOKEN_VAZIO_PROOF", "claim_allowed": False}


def write_report(out_dir: Path, report: dict) -> str:
    if out_dir.exists() or out_dir.is_symlink():
        raise FileExistsError("immutable output directory already exists")
    out_dir.parent.mkdir(parents=True, exist_ok=True)
    report_bytes = (json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False,
                               allow_nan=False) + "\n").encode("utf-8")
    sha = hashlib.sha256(report_bytes).hexdigest()
    source_sha = hashlib.sha256(Path(__file__).read_bytes()).hexdigest()
    receipt = ("# RLL OPEN MATH V1 — BOUNDED SHADOW RECEIPT\n\n"
               f"- report_sha256_bytes: `{sha}`\n"
               f"- source_sha256_bytes: `{source_sha}`\n"
               f"- python_version: `{platform.python_version()}`\n"
               f"- github_sha: `{os.getenv('GITHUB_SHA') or 'TOKEN_VAZIO_NOT_IN_GITHUB'}`\n"
               "- status: `FINITE_TESTED_ONLY`\n"
               "- randomization_inference: `EXPLORATORY_NOT_CONFIRMATORY`\n"
               "- independent_review: `TOKEN_VAZIO`\n"
               "- mathematical_novelty: `TOKEN_VAZIO`\n"
               "- claim_allowed: `false`\n"
               "- rollback: `git revert in research branch; preserve receipts`\n")
    with tempfile.TemporaryDirectory(prefix=".open-math-stage-", dir=out_dir.parent) as stage:
        staging = Path(stage)
        (staging / "report.json").write_bytes(report_bytes)
        (staging / "receipt.md").write_text(receipt, encoding="utf-8")
        if hashlib.sha256((staging / "report.json").read_bytes()).hexdigest() != sha:
            raise RuntimeError("readback digest mismatch")
        # Publish both files under one directory rename, not individual outputs.
        os.rename(staging, out_dir)
    return sha


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--limit", type=int, default=10000)
    ap.add_argument("--draws", type=int, default=127)
    ap.add_argument("--seed", type=int, default=20261121)
    ap.add_argument("--grid", type=int, default=3)
    ap.add_argument("--out-dir", type=Path, default=Path("artifacts/omega-math-explorer/open_math_v1"))
    args = ap.parse_args()
    report = compute(args.limit, args.draws, args.seed, args.grid)
    digest = write_report(args.out_dir, report)
    result = report["spectral_exploration"]
    print(json.dumps({"gate": "PASS_SCOPED_FINITE_ONLY", "claim_allowed": False,
                      "candidate_count": result["candidate_count"],
                      "primes_among_candidates": result["primes_among_candidates"],
                      "draws": result["draws"], "report_sha256": digest}, sort_keys=True))


if __name__ == "__main__":
    main()
