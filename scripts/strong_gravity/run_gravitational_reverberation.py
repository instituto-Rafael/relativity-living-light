#!/usr/bin/env python3
"""Run a bounded gravitational reverberation reference scenario."""

from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import sys

ROOT = Path(__file__).resolve().parents[2]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.pipelines.strong_gravity.gravitational_reverberation_response import (  # noqa: E402
    DampedMode,
    ReverberationConfig,
    response_summary,
    sample_response,
)


def canonical_sha256(payload: object) -> str:
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def float_range(start: float, stop: float, step: float):
    if step <= 0.0:
        raise ValueError("sampling step must be > 0")
    if stop < start:
        raise ValueError("sampling stop must be >= start")
    count = int((stop - start) / step + 0.5)
    for index in range(count + 1):
        value = start + index * step
        if value <= stop + step * 1.0e-9:
            yield value


def load_config(payload: dict) -> ReverberationConfig:
    cfg = payload["config"]
    modes = tuple(DampedMode(**mode) for mode in cfg.get("modes", []))
    return ReverberationConfig(
        event_time_s=cfg.get("event_time_s", 0.0),
        direct_amplitude=cfg.get("direct_amplitude", 0.0),
        direct_width_s=cfg.get("direct_width_s", 1.0),
        modes=modes,
        tail_amplitude=cfg.get("tail_amplitude", 0.0),
        tail_scale_s=cfg.get("tail_scale_s", 1.0),
        tail_power=cfg.get("tail_power", 2.0),
        memory_delta=cfg.get("memory_delta", 0.0),
        memory_rise_s=cfg.get("memory_rise_s", 1.0),
    )


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("scenario", type=Path)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()

    payload = json.loads(args.scenario.read_text(encoding="utf-8"))
    cfg = load_config(payload)
    observer = payload.get("observer", {})
    sampling = payload["sampling"]
    times = tuple(float_range(sampling["start_s"], sampling["stop_s"], sampling["step_s"]))
    samples = sample_response(
        cfg,
        times,
        distance_m=observer.get("distance_m", 0.0),
        propagation_speed_m_s=observer.get("propagation_speed_m_s", 299_792_458.0),
    )

    receipt = {
        "schema_version": "1.0",
        "module": "gravitational_reverberation_response",
        "claim_allowed": False,
        "input_sha256": canonical_sha256(payload),
        "summary": response_summary(samples, cfg),
        "samples": [
            {
                "time_s": sample.time_s,
                "retarded_time_s": sample.retarded_time_s,
                "direct": sample.direct,
                "ringdown": sample.ringdown,
                "tail": sample.tail,
                "memory": sample.memory,
                "total": sample.total,
            }
            for sample in samples
        ],
        "cascade_energy_bridge": "TOKEN_VAZIO",
        "claim_boundary": "Synthetic signal reference only; no astrophysical fit or new-physics claim.",
    }
    receipt["receipt_sha256"] = canonical_sha256(receipt)
    text = json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n"

    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    else:
        sys.stdout.write(text)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
