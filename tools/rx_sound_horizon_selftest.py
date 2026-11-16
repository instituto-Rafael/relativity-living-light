#!/usr/bin/env python3
"""Rx sound-horizon reference-vector selftest."""

from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rx.sound_horizon import sound_horizons

references = {
    "LCDM": {
        "vector": [
            67.66725167785673,
            0.3162598585368923,
            0.022440865749970035,
            0.811,
        ],
        "rd_mpc": 149.8314329013423,
        "rs_star_mpc": 143.67973843293154,
    },
    "RLL": {
        "vector": [
            66.99367300987414,
            0.32475606452625294,
            0.011594905594391598,
            11.452558895186602,
            0.22656819958262459,
            0.022412064168652816,
            0.811,
        ],
        "rd_mpc": 148.98654354573253,
        "rs_star_mpc": 142.91992714632195,
    },
}

tolerance_mpc = 0.12
rows = {}
failures = []

for model, ref in references.items():
    got = sound_horizons(model, ref["vector"], omega_r=9.18e-5, steps=4000)
    rd_delta = got["rd_mpc"] - ref["rd_mpc"]
    rs_delta = got["rs_star_mpc"] - ref["rs_star_mpc"]
    row = {
        "computed": got,
        "reference": {
            "rd_mpc": ref["rd_mpc"],
            "rs_star_mpc": ref["rs_star_mpc"],
        },
        "delta_mpc": {
            "rd": rd_delta,
            "rs_star": rs_delta,
        },
        "pass": abs(rd_delta) <= tolerance_mpc and abs(rs_delta) <= tolerance_mpc,
    }
    rows[model] = row
    if row["pass"]:
        print("PASS", model, "rd_delta=%.6f" % rd_delta, "rs_delta=%.6f" % rs_delta)
    else:
        print("FAIL", model, "rd_delta=%.6f" % rd_delta, "rs_delta=%.6f" % rs_delta)
        failures.append(model)

payload = {
    "schema": "rll.rx.sound_horizon_selftest.v1",
    "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "reference_source": "results/rll_fase18e_calibrado.json",
    "omega_r": 9.18e-5,
    "tolerance_mpc": tolerance_mpc,
    "rows": rows,
    "pass": not failures,
    "training": False,
    "ai_runtime": False,
    "claim_allowed": False,
}

out = ROOT / "results" / "rx_sound_horizon_selftest.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if failures:
    print("RX_SOUND_HORIZON_SELFTEST=FAIL", failures)
    raise SystemExit(1)

print("RX_SOUND_HORIZON_SELFTEST=PASS")
print("wrote", out.relative_to(ROOT))
