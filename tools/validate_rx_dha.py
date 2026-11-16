#!/usr/bin/env python3
"""Validate the Rx DHA angular-frequency baseline and legacy semantic gap."""

from __future__ import annotations

import json
import math
import random
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rx.dha import (
    angular_frequency_to_cycles,
    cycles_to_angular_frequency,
    scan_angular_gls,
)

rng = random.Random(12345)
omega_true = 2.0 * math.pi / math.log(1000.0)
x = [-4.5 + 9.0 * i / 149.0 for i in range(150)]
sigma = [0.05 for _ in x]
y = [
    0.03 * math.cos(omega_true * xv + 0.5)
    + rng.gauss(0.0, 0.05)
    for xv in x
]

result = scan_angular_gls(
    x,
    y,
    sigma,
    omega_min=0.4,
    omega_max=2.0,
    n_grid=2000,
)

legacy_path = ROOT / "src/rll/desi_dha_extractor.py"
legacy_text = legacy_path.read_text(encoding="utf-8")
legacy_uses_astropy = "LombScargle" in legacy_text
legacy_passes_omega_grid_to_power = (
    "ls.power(omega_grid)" in legacy_text
)

checks = {
    "angular_cycle_roundtrip": abs(
        cycles_to_angular_frequency(
            angular_frequency_to_cycles(omega_true)
        ) - omega_true
    ) < 1.0e-12,
    "synthetic_omega_recovery": (
        abs(result["best_omega"] - omega_true) < 0.12
    ),
    "frequency_semantics_explicit": (
        result["frequency_semantics"]
        == "angular_radians_per_x_unit"
    ),
    "fap_not_invented": (
        result["false_alarm_probability"]
        == "TOKEN_VAZIO_NOT_IMPLEMENTED"
    ),
    "astropy_parity_not_claimed": (
        result["astropy_semantic_parity"]
        == "TOKEN_VAZIO_NOT_CLAIMED"
    ),
    "legacy_astropy_route_detected": legacy_uses_astropy,
    "legacy_omega_to_frequency_gap_detected": (
        legacy_passes_omega_grid_to_power
    ),
    "claim_blocked": result["claim_allowed"] is False,
}

failed = [name for name, ok in checks.items() if not ok]
payload = {
    "schema": "rll.rx.dha_angular_frequency_gate.v1",
    "generated_utc": (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    ),
    "pass": not failed,
    "checks": checks,
    "failed_checks": failed,
    "omega_true": omega_true,
    "best_omega": result["best_omega"],
    "best_frequency_cycles": result["best_frequency_cycles"],
    "legacy_contract": {
        "path": "src/rll/desi_dha_extractor.py",
        "observed_call": "LombScargle(...).power(omega_grid)",
        "observed_variable_semantics": "omega/angular naming",
        "astropy_required_semantics": "cycles_per_x_unit",
        "state": "GAP_2PI_SEMANTICS_REQUIRES_MIGRATION_DECISION",
    },
    "third_party_python_dependencies": [],
    "false_alarm_probability": "TOKEN_VAZIO",
    "astropy_semantic_parity": "TOKEN_VAZIO",
    "legacy_route_replaced": False,
    "claim_allowed": False,
    "boundary": (
        "This gate validates an explicit angular-frequency stdlib baseline. "
        "It does not claim Astropy Lomb-Scargle normalization/FAP parity and "
        "does not retroactively validate legacy DHA results."
    ),
}
out = ROOT / "results/rx_dha_angular_frequency_gate.json"
out.parent.mkdir(exist_ok=True)
out.write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(payload, ensure_ascii=False, indent=2))
raise SystemExit(0 if payload["pass"] else 5)
