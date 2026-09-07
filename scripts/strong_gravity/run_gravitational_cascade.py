#!/usr/bin/env python3
"""Run a JSON gravitational-cascade scenario and emit a deterministic receipt."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.pipelines.strong_gravity.gravitational_cascade_network import (  # noqa: E402
    CascadeNetwork,
    Edge,
    Node,
    branching_potential,
)


def _canonical_sha256(payload: object) -> str:
    encoded = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def load_scenario(path: Path):
    payload = json.loads(path.read_text(encoding="utf-8"))
    network_cfg = payload["network"]
    nodes = [Node(**item) for item in payload["nodes"]]
    edges = [Edge(**item) for item in payload["edges"]]
    net = CascadeNetwork(
        nodes,
        edges,
        attenuation_scale_m=network_cfg["attenuation_scale_m"],
        attenuation_exponent=network_cfg.get("attenuation_exponent", 2.0),
        propagation_speed_m_s=network_cfg.get("propagation_speed_m_s", 299_792_458.0),
    )
    return payload, net


def build_receipt(payload, net, result):
    receipt = {
        "schema_version": "1.0",
        "module": "gravitational_cascade_trigger_network",
        "claim_allowed": False,
        "input_sha256": _canonical_sha256(payload),
        "result": {
            "avalanche_size": result.avalanche_size,
            "active_fraction": result.active_fraction,
            "max_depth": result.max_depth,
            "duration_s": result.duration_s,
            "total_seed_j": result.total_seed_j,
            "total_released_j": result.total_released_j,
            "activations": [
                {
                    "node_id": event.node_id,
                    "time_s": event.time_s,
                    "depth": event.depth,
                    "accumulated_trigger_j": event.accumulated_trigger_j,
                    "released_j": event.released_j,
                }
                for event in result.activations
            ],
            "branching_potential": branching_potential(net),
        },
        "claim_boundary": (
            "Computational threshold cascade only. No physical cosmic-avalanche claim is authorized "
            "without source-specific GR/MHD derivation and observational falsification."
        ),
    }
    receipt["receipt_sha256"] = _canonical_sha256(receipt)
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload, net = load_scenario(args.scenario)
    result = net.run(payload["seed"])
    receipt = build_receipt(payload, net, result)
    text = json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
