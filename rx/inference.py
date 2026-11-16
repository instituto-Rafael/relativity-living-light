"""Deterministic, stdlib-only inference baselines for Rx/RLL.

This module provides small auditable inference primitives so the active Rx
runtime does not need emcee for a basic posterior-sampling diagnostic.

It is NOT a semantic replacement for emcee's ensemble sampler and is NOT a
replacement for dynesty/nested evidence. Those routes remain explicitly open.
"""

from __future__ import annotations

import math
import random


def _validate_bounds(start, bounds):
    if len(start) != len(bounds):
        raise ValueError("start/bounds mismatch")
    x = [float(value) for value in start]
    normalized = []
    for idx, pair in enumerate(bounds):
        if len(pair) != 2:
            raise ValueError("each bound must contain (lo, hi)")
        lo, hi = float(pair[0]), float(pair[1])
        if not (math.isfinite(lo) and math.isfinite(hi) and hi > lo):
            raise ValueError("invalid bound at index %d" % idx)
        if not (lo <= x[idx] <= hi):
            raise ValueError("start outside bounds at index %d" % idx)
        normalized.append((lo, hi))
    return x, normalized


def bounded_random_walk_metropolis(
    log_probability,
    start,
    bounds,
    *,
    steps=4000,
    burn_in=500,
    thin=1,
    proposal_fraction=0.04,
    seed=1,
):
    """Run a deterministic-seeded bounded random-walk Metropolis baseline."""

    total_steps = int(steps)
    burn = int(burn_in)
    thin_value = int(thin)
    scale = float(proposal_fraction)
    if total_steps <= 0:
        raise ValueError("steps must be positive")
    if burn < 0 or burn >= total_steps:
        raise ValueError("burn_in must satisfy 0 <= burn_in < steps")
    if thin_value <= 0:
        raise ValueError("thin must be positive")
    if not (scale > 0.0 and math.isfinite(scale)):
        raise ValueError("proposal_fraction must be finite and positive")

    current, normalized_bounds = _validate_bounds(start, bounds)
    current_lp = float(log_probability(current))
    if not math.isfinite(current_lp):
        raise ValueError("initial log_probability must be finite")

    rng = random.Random(int(seed))
    spans = [hi - lo for lo, hi in normalized_bounds]
    accepted = 0
    proposals_in_bounds = 0
    chain = []
    log_probabilities = []

    for step in range(total_steps):
        proposal = [
            current[i] + rng.gauss(0.0, scale * spans[i])
            for i in range(len(current))
        ]
        in_bounds = all(
            lo <= proposal[i] <= hi
            for i, (lo, hi) in enumerate(normalized_bounds)
        )

        if in_bounds:
            proposals_in_bounds += 1
            proposal_lp = float(log_probability(proposal))
            if math.isfinite(proposal_lp):
                delta = proposal_lp - current_lp
                accept = delta >= 0.0
                if not accept:
                    accept = math.log(max(rng.random(), 1.0e-300)) < delta
                if accept:
                    current = proposal
                    current_lp = proposal_lp
                    accepted += 1

        if step >= burn and ((step - burn) % thin_value == 0):
            chain.append(current[:])
            log_probabilities.append(current_lp)

    return {
        "method": "rx_bounded_random_walk_metropolis_v1",
        "seed": int(seed),
        "steps": total_steps,
        "burn_in": burn,
        "thin": thin_value,
        "proposal_fraction": scale,
        "accepted": accepted,
        "acceptance_fraction": accepted / float(total_steps),
        "proposals_in_bounds": proposals_in_bounds,
        "bounds": [[lo, hi] for lo, hi in normalized_bounds],
        "chain": chain,
        "log_probabilities": log_probabilities,
        "semantic_parity": {
            "emcee": "TOKEN_VAZIO_NOT_EQUIVALENT",
            "dynesty": "TOKEN_VAZIO_NOT_IMPLEMENTED",
        },
        "claim_allowed": False,
    }


def quantile(values, q):
    ordered = sorted(float(value) for value in values)
    if not ordered:
        raise ValueError("quantile requires at least one value")
    q_value = float(q)
    if not 0.0 <= q_value <= 1.0:
        raise ValueError("q must be in [0, 1]")
    position = q_value * (len(ordered) - 1)
    lo = int(math.floor(position))
    hi = int(math.ceil(position))
    if lo == hi:
        return ordered[lo]
    weight = position - lo
    return ordered[lo] * (1.0 - weight) + ordered[hi] * weight


def summarize_chain(chain):
    rows = [list(map(float, row)) for row in chain]
    if not rows:
        raise ValueError("chain must be non-empty")
    width = len(rows[0])
    if width == 0 or any(len(row) != width for row in rows):
        raise ValueError("chain rows must have one consistent nonzero width")

    summaries = []
    for column in range(width):
        values = [row[column] for row in rows]
        mean = sum(values) / len(values)
        summaries.append(
            {
                "index": column,
                "mean": mean,
                "median": quantile(values, 0.5),
                "q16": quantile(values, 0.16),
                "q84": quantile(values, 0.84),
                "min": min(values),
                "max": max(values),
            }
        )
    return {
        "samples": len(rows),
        "dimensions": width,
        "parameters": summaries,
        "diagnostic_boundary": (
            "Summary statistics only; convergence, effective sample size, "
            "multimodality and Bayesian evidence require separate gates."
        ),
    }
