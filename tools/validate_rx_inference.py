#!/usr/bin/env python3
"""Validate deterministic Rx inference baseline without third-party packages."""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rx.inference import bounded_random_walk_metropolis, summarize_chain


def log_probability(vector):
    x = float(vector[0])
    y = float(vector[1])
    return -0.5 * (
        ((x - 1.25) / 0.40) ** 2
        + ((y + 0.5) / 0.70) ** 2
    )


kwargs = {
    "steps": 6000,
    "burn_in": 1000,
    "thin": 2,
    "proposal_fraction": 0.05,
    "seed": 963,
}
first = bounded_random_walk_metropolis(
    log_probability,
    [0.0, 0.0],
    [(-3.0, 3.0), (-4.0, 4.0)],
    **kwargs,
)
second = bounded_random_walk_metropolis(
    log_probability,
    [0.0, 0.0],
    [(-3.0, 3.0), (-4.0, 4.0)],
    **kwargs,
)
summary = summarize_chain(first["chain"])

checks = {
    "exact_seed_reproducibility": (
        first["chain"] == second["chain"]
        and first["log_probabilities"] == second["log_probabilities"]
    ),
    "expected_sample_count": len(first["chain"]) == 2500,
    "acceptance_non_degenerate": (
        0.05 < first["acceptance_fraction"] < 0.95
    ),
    "bounds_preserved": all(
        -3.0 <= row[0] <= 3.0 and -4.0 <= row[1] <= 4.0
        for row in first["chain"]
    ),
    "gaussian_center_x_smoke": (
        abs(summary["parameters"][0]["mean"] - 1.25) < 0.10
    ),
    "gaussian_center_y_smoke": (
        abs(summary["parameters"][1]["mean"] + 0.5) < 0.15
    ),
    "summary_finite": all(
        math.isfinite(float(item[key]))
        for item in summary["parameters"]
        for key in ("mean", "median", "q16", "q84", "min", "max")
    ),
    "emcee_parity_left_open": (
        first["semantic_parity"]["emcee"]
        == "TOKEN_VAZIO_NOT_EQUIVALENT"
    ),
    "dynesty_left_open": (
        first["semantic_parity"]["dynesty"]
        == "TOKEN_VAZIO_NOT_IMPLEMENTED"
    ),
    "claim_blocked": first["claim_allowed"] is False,
}

failed = [name for name, passed in checks.items() if not passed]
payload = {
    "schema": "rll.rx.inference_baseline_gate.v1",
    "generated_utc": (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    ),
    "pass": not failed,
    "checks": checks,
    "failed_checks": failed,
    "method": first["method"],
    "samples": len(first["chain"]),
    "acceptance_fraction": first["acceptance_fraction"],
    "third_party_python_dependencies": [],
    "emcee_semantic_parity": "TOKEN_VAZIO",
    "dynesty_nested_evidence": "TOKEN_VAZIO",
    "claim_allowed": False,
    "boundary": (
        "A seeded Metropolis baseline is now available without emcee. "
        "It is not ensemble-sampler parity, not a nested sampler, and not "
        "scientific evidence for RLL."
    ),
}
out = ROOT / "results/rx_inference_baseline_gate.json"
out.parent.mkdir(exist_ok=True)
out.write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(payload, ensure_ascii=False, indent=2))
raise SystemExit(0 if payload["pass"] else 5)
