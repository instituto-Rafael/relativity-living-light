from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "src" / "rll_photonic" / "omega_adapter.py"
SPEC = importlib.util.spec_from_file_location(
    "rll_photonic_omega_adapter",
    MODULE_PATH,
)
if SPEC is None or SPEC.loader is None:
    raise RuntimeError(f"cannot load adapter: {MODULE_PATH}")
ADAPTER = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = ADAPTER
SPEC.loader.exec_module(ADAPTER)

ResidualChecks = ADAPTER.ResidualChecks
normalized_residual = ADAPTER.normalized_residual
opposition_gate = ADAPTER.opposition_gate
photonic_invariant_errors = ADAPTER.photonic_invariant_errors
report_dict = ADAPTER.report_dict
screen_residuals = ADAPTER.screen_residuals


def build_report(payload: dict) -> dict:
    observed = payload.get("observed")
    predicted = payload.get("predicted")
    sigma_observed = payload.get("sigma_observed")
    sigma_model = payload.get("sigma_model", [0.0] * len(observed or []))
    arrays = (observed, predicted, sigma_observed, sigma_model)
    if not all(isinstance(values, list) for values in arrays):
        raise ValueError(
            "observed, predicted and uncertainty fields must be arrays"
        )
    lengths = {len(values) for values in arrays}
    if len(lengths) != 1 or not observed:
        raise ValueError("all arrays must have equal non-zero length")

    checks_payload = payload.get("checks")
    if not isinstance(checks_payload, dict):
        raise ValueError("checks must be an object")
    checks = ResidualChecks(**checks_payload)
    normalized = [
        normalized_residual(o, p, so, sm)
        for o, p, so, sm in zip(
            observed,
            predicted,
            sigma_observed,
            sigma_model,
        )
    ]
    screen = screen_residuals(
        normalized,
        threshold=float(payload["threshold"]),
        checks=checks,
    )
    gate = opposition_gate(
        support_weight=float(payload.get("support_weight", 0.0)),
        refutation_weight=float(payload.get("refutation_weight", 0.0)),
        scope_overlap=float(payload.get("scope_overlap", 0.0)),
        evidence_complete=bool(payload.get("evidence_complete", False)),
    )
    report = report_dict(screen, gate)
    report["normalized_residuals"] = normalized
    state = payload.get("photonic_state")
    report["photonic_invariant_errors"] = (
        []
        if state is None
        else photonic_invariant_errors(
            intensity=float(state["intensity"]),
            q=float(state.get("q", 0.0)),
            u=float(state.get("u", 0.0)),
            v=float(state.get("v", 0.0)),
        )
    )
    return report


def main() -> int:
    parser = argparse.ArgumentParser(
        description=(
            "Audit RLL residuals without promoting magnitude to a physical claim."
        )
    )
    parser.add_argument("input", type=Path)
    parser.add_argument("--output", type=Path)
    parser.add_argument(
        "--strict",
        action="store_true",
        help="Fail when photonic invariants are violated.",
    )
    args = parser.parse_args()
    payload = json.loads(args.input.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise SystemExit("input must be a JSON object")
    report = build_report(payload)
    text = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True)
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text + "\n", encoding="utf-8")
    else:
        print(text)
    if args.strict and report["photonic_invariant_errors"]:
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
