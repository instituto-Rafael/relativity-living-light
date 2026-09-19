#!/usr/bin/env python3
"""Bounded adaptive fragment permutation ruler for RLL.

Search heuristic only. A high score is never scientific evidence.
"""

from __future__ import annotations

import argparse
import hashlib
import itertools
import json
import math
import random
from dataclasses import dataclass
from pathlib import Path
from typing import Any


BLOCKING_GATES = {
    "TOKEN_VAZIO",
    "TOKEN_VAZIO_THRESHOLD",
    "TOKEN_VAZIO_COMPARATOR",
    "TOKEN_VAZIO_CAUSAL",
    "BLOCKED",
    "CONTEXT_ONLY",
    "CANCER_CONTEXT",
}


@dataclass(frozen=True)
class Fragment:
    id: str
    name: str
    layer: str
    impact: float
    uncertainty_reduction: float
    effort: float
    undercoverage: float
    recurrence: float
    testability: float
    novelty: float
    provenance: float
    claim_gate: str

    @classmethod
    def from_dict(cls, row: dict[str, Any]) -> "Fragment":
        return cls(
            id=str(row["id"]),
            name=str(row["name"]),
            layer=str(row["layer"]),
            impact=float(row["impact"]),
            uncertainty_reduction=float(row["uncertainty_reduction"]),
            effort=float(row["effort"]),
            undercoverage=float(row["undercoverage"]),
            recurrence=float(row["recurrence"]),
            testability=float(row["testability"]),
            novelty=float(row["novelty"]),
            provenance=float(row["provenance"]),
            claim_gate=str(row["claim_gate"]),
        )


def log_priority(f: Fragment) -> float:
    if min(f.impact, f.uncertainty_reduction, f.effort) <= 0:
        raise ValueError(f"non-positive priority factor in {f.id}")
    return (
        math.log2(f.impact)
        + math.log2(f.uncertainty_reduction)
        - math.log2(f.effort)
    )


def candidate_features(parts: tuple[Fragment, ...]) -> dict[str, float]:
    n = float(len(parts))
    layers = len({p.layer for p in parts})
    duplicate_layers = len(parts) - layers
    return {
        "base_priority": sum(log_priority(p) for p in parts) / n,
        "undercoverage": sum(p.undercoverage for p in parts) / n,
        "recurrence": sum(p.recurrence for p in parts) / n,
        "testability": sum(p.testability for p in parts) / n,
        "cross_layer": layers / n,
        "novelty": sum(p.novelty for p in parts) / n,
        "provenance": sum(p.provenance for p in parts) / n,
        "redundancy": duplicate_layers / n,
    }


def score_candidate(parts: tuple[Fragment, ...], weights: dict[str, float]) -> tuple[float, dict[str, float]]:
    q = candidate_features(parts)
    score = q["base_priority"]
    score += weights.get("undercoverage", 1.0) * q["undercoverage"]
    score += weights.get("recurrence", 1.0) * q["recurrence"]
    score += weights.get("testability", 1.0) * q["testability"]
    score += weights.get("cross_layer", 1.0) * q["cross_layer"]
    score += weights.get("novelty", 0.75) * q["novelty"]
    score += weights.get("provenance", 1.25) * q["provenance"]
    score -= weights.get("redundancy_penalty", 1.0) * q["redundancy"]
    return score, q


def promotion_allowed(parts: tuple[Fragment, ...]) -> bool:
    return not any(
        p.claim_gate in BLOCKING_GATES or p.claim_gate.startswith("TOKEN_VAZIO")
        for p in parts
    )


def tuple_hash(ids: tuple[str, ...]) -> str:
    raw = "|".join(ids).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def exact_combination_count(n: int, max_size: int) -> int:
    upper = min(max_size, n)
    return sum(math.comb(n, k) for k in range(2, upper + 1))


def update_weights(
    weights: dict[str, float],
    features: dict[str, float],
    reward: float,
    eta: float = 0.05,
) -> dict[str, float]:
    keys = [
        "undercoverage",
        "recurrence",
        "testability",
        "cross_layer",
        "novelty",
        "provenance",
    ]
    out = dict(weights)
    vals = []
    for key in keys:
        old = max(float(weights.get(key, 1.0)), 1e-12)
        value = old * math.exp(eta * reward * float(features.get(key, 0.0)))
        out[key] = value
        vals.append(value)
    total = sum(vals)
    if total > 0:
        target_total = float(len(keys))
        for key in keys:
            out[key] = out[key] / total * target_total
    return out


def search(
    fragments: list[Fragment],
    weights: dict[str, float],
    *,
    seed: int,
    sample_budget: int,
    max_size: int,
    beam_width: int,
    epsilon: float,
    patience: int,
    require_cross_layer: bool,
) -> dict[str, Any]:
    rng = random.Random(seed)
    if len(fragments) < 2:
        return {"candidates": [], "samples_attempted": 0, "stop_reason": "TOO_FEW_FRAGMENTS"}

    seen: set[tuple[str, ...]] = set()
    beam: list[dict[str, Any]] = []
    best = -math.inf
    stale = 0
    attempted = 0

    max_size = min(max_size, len(fragments))

    while attempted < sample_budget and stale < patience:
        attempted += 1
        k = rng.randint(2, max_size)
        parts = tuple(rng.sample(fragments, k))
        ids = tuple(sorted(p.id for p in parts))
        if ids in seen:
            stale += 1
            continue
        seen.add(ids)

        if require_cross_layer and len({p.layer for p in parts}) < 2:
            stale += 1
            continue

        score, features = score_candidate(parts, weights)
        row = {
            "ids": list(ids),
            "score": round(score, 8),
            "features": {k: round(v, 8) for k, v in features.items()},
            "promotion_allowed": promotion_allowed(parts),
            "tuple_hash": tuple_hash(ids),
        }
        beam.append(row)
        beam.sort(key=lambda x: (-x["score"], x["ids"]))
        beam = beam[:beam_width]

        if score > best + epsilon:
            best = score
            stale = 0
        else:
            stale += 1

    stop = "PATIENCE" if stale >= patience else "SAMPLE_BUDGET"
    return {
        "policy": {
            "blind_cartesian_product": "FORBIDDEN",
            "seed": seed,
            "sample_budget": sample_budget,
            "max_size": max_size,
            "beam_width": beam_width,
            "epsilon": epsilon,
            "patience": patience,
            "require_cross_layer": require_cross_layer,
        },
        "exact_finite_combination_count_metadata_only": exact_combination_count(len(fragments), max_size),
        "samples_attempted": attempted,
        "unique_candidates_seen": len(seen),
        "stop_reason": stop,
        "candidates": beam,
        "search_score_is_evidence": False,
        "claim_allowed": False,
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ledger", required=True)
    ap.add_argument("--output")
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--samples", type=int, default=256)
    ap.add_argument("--max-size", type=int, default=4)
    ap.add_argument("--beam", type=int, default=20)
    ap.add_argument("--epsilon", type=float, default=0.01)
    ap.add_argument("--patience", type=int, default=64)
    ap.add_argument("--allow-same-layer", action="store_true")
    args = ap.parse_args()

    data = json.loads(Path(args.ledger).read_text(encoding="utf-8"))
    fragments = [Fragment.from_dict(x) for x in data["fragments"]]
    weights = data.get("adaptive_weights", {})
    result = search(
        fragments,
        weights,
        seed=args.seed,
        sample_budget=args.samples,
        max_size=args.max_size,
        beam_width=args.beam,
        epsilon=args.epsilon,
        patience=args.patience,
        require_cross_layer=not args.allow_same_layer,
    )
    payload = json.dumps(result, indent=2, sort_keys=True)
    if args.output:
        Path(args.output).write_text(payload + "\n", encoding="utf-8")
    else:
        print(payload)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
