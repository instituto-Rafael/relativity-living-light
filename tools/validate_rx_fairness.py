#!/usr/bin/env python3
"""Validate the stdlib-only Rx fairness/statistics module."""

from __future__ import annotations

import json
import math
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rx.fairness import (
    aic,
    aicc,
    bic,
    covariance_readiness,
    growth_backend_benchmark_status,
    load_parameter_origin_registry,
    s8_parameter,
    w_eff_rll_density,
)

checks = {}

checks["aic"] = abs(aic(20.0, 3) - 26.0) < 1.0e-12
checks["aicc"] = abs(
    aicc(20.0, 3, 30)
    - (20.0 + 6.0 + 2.0 * 3.0 * 4.0 / 26.0)
) < 1.0e-12
checks["bic"] = abs(
    bic(20.0, 3, 30) - (20.0 + 3.0 * math.log(30.0))
) < 1.0e-12
try:
    aicc(20.0, 3, 4)
except ValueError:
    checks["aicc_undefined_rejected"] = True
else:
    checks["aicc_undefined_rejected"] = False

checks["s8_reference"] = abs(s8_parameter(0.8, 0.3) - 0.8) < 1.0e-12

w = w_eff_rll_density([0.0, 1.0, 8.0], 1.0, 0.3)
checks["w_eff_finite"] = all(math.isfinite(value) for value in w)
checks["w_eff_lowz_negative"] = w[0] < 0.0
checks["w_eff_highz_matterlike"] = abs(w[-1]) < 1.0e-6
checks["w_eff_bounded_smoke"] = all(value < 1.0 for value in w)

cov = [[4.0, 0.2], [0.2, 9.0]]
partial = covariance_readiness(cov, mode="block_summary")
full = covariance_readiness(cov, mode="official_full")
bad = covariance_readiness(
    [[1.0, 2.0], [0.0, 1.0]], mode="official_full"
)
indefinite = covariance_readiness(
    [[1.0, 2.0], [2.0, 1.0]], mode="official_full"
)
checks["cov_partial_ready_claim_blocked"] = (
    partial.ready and not partial.claim_allowed
)
checks["cov_full_ready"] = full.ready and full.claim_allowed
checks["cov_asymmetry_rejected"] = not bad.ready
checks["cov_indefinite_rejected"] = not indefinite.ready

registry = json.loads(
    (
        ROOT / "data/inputs/cosmology_joint/parameter_origin_registry.json"
    ).read_text(encoding="utf-8")
)
normalized = load_parameter_origin_registry(registry)
names = {str(row["name"]) for row in normalized["parameters"]}
checks["parameter_registry_contract"] = {
    "H0", "Os0", "w0", "wa"
}.issubset(names)

backend = growth_backend_benchmark_status(require_external=False)
checks["backend_availability_not_claim"] = backend["claim_allowed"] is False
checks["backend_status_shape"] = {
    "status",
    "available_backends",
    "checked_backends",
    "claim_allowed",
    "reason",
}.issubset(backend)

failed = [name for name, passed in checks.items() if not passed]
payload = {
    "schema": "rll.rx.fairness_stdlib_gate.v1",
    "generated_utc": (
        datetime.now(timezone.utc).replace(microsecond=0).isoformat()
    ),
    "pass": not failed,
    "checks": checks,
    "failed_checks": failed,
    "third_party_python_dependencies": [],
    "scientific_semantics_changed": False,
    "legacy_numpy_route_replaced": False,
    "claim_allowed": False,
    "boundary": (
        "This gate validates a stdlib implementation surface and governance "
        "semantics. It does not select a cosmology or promote a scientific claim."
    ),
}
out = ROOT / "results/rx_fairness_stdlib_gate.json"
out.parent.mkdir(exist_ok=True)
out.write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)
print(json.dumps(payload, ensure_ascii=False, indent=2))
raise SystemExit(0 if payload["pass"] else 5)
