#!/usr/bin/env python3
"""Execute the governed Climate Engine bridge without exposing credential material."""
from __future__ import annotations

import hashlib
import json
import os
from pathlib import Path
import subprocess
import sys
from typing import Iterable

OUT = Path("artifacts/rll-climate-engine")
BRIDGE_RECEIPT = OUT / "bridge-receipt.json"
CONTROL_RECEIPT = OUT / "RLL_CLIMATE_ENGINE_LIVE_CONTROL_RECEIPT.json"
ALLOWED = {"metadata_dates", "metadata_variables", "timeseries_coordinates", "map_values"}
RECEIPT_FORBIDDEN_KEYS = {"secret_value", "secret_length", "secret_hash", "authorization_header"}


def env(name: str, default: str = "") -> str:
    return os.environ.get(name, default).strip()


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def build_argv() -> tuple[str, list[str]]:
    operation = env("RLL_CLIMATE_OPERATION")
    if operation not in ALLOWED:
        raise ValueError(f"unsupported operation: {operation!r}")

    values = {
        "dataset": env("RLL_CLIMATE_DATASET"),
        "variable": env("RLL_CLIMATE_VARIABLE"),
        "start_date": env("RLL_CLIMATE_START_DATE"),
        "end_date": env("RLL_CLIMATE_END_DATE"),
        "coordinates": env("RLL_CLIMATE_COORDINATES", "[]"),
        "area_reducer": env("RLL_CLIMATE_AREA_REDUCER", "mean"),
        "temporal_statistic": env("RLL_CLIMATE_TEMPORAL_STATISTIC", "mean"),
    }
    required = {
        "metadata_dates": ("dataset",),
        "metadata_variables": ("dataset",),
        "timeseries_coordinates": ("dataset", "variable", "start_date", "end_date", "coordinates"),
        "map_values": ("dataset", "variable", "start_date", "end_date", "temporal_statistic"),
    }[operation]
    missing = [key for key in required if not values[key]]
    if missing:
        raise ValueError(f"missing required dispatch inputs: {missing}")

    argv = [
        sys.executable,
        "scripts/rll_climate_engine_bridge.py",
        "--operation", operation,
        "--execute",
        "--output-dir", str(OUT),
        "--receipt", str(BRIDGE_RECEIPT),
        "--dataset", values["dataset"],
    ]
    if values["variable"]:
        argv += ["--variable", values["variable"]]
    if values["start_date"]:
        argv += ["--start-date", values["start_date"]]
    if values["end_date"]:
        argv += ["--end-date", values["end_date"]]
    if operation == "timeseries_coordinates":
        argv += ["--coordinates", values["coordinates"], "--area-reducer", values["area_reducer"]]
    if operation == "map_values":
        argv += ["--temporal-statistic", values["temporal_statistic"]]
    return operation, argv


def walk_keys(value):
    if isinstance(value, dict):
        for key, item in value.items():
            yield str(key)
            yield from walk_keys(item)
    elif isinstance(value, list):
        for item in value:
            yield from walk_keys(item)


def assert_secret_absent(paths: Iterable[Path], secret: str | None) -> None:
    if not secret:
        return
    needle = secret.encode("utf-8")
    for path in paths:
        if path.is_file() and needle in path.read_bytes():
            raise RuntimeError(f"credential material detected in artifact: {path}")


def main() -> int:
    OUT.mkdir(parents=True, exist_ok=True)
    secret = os.environ.get("CLIMATE_ENGINE_API_KEY")
    secret_present = bool(secret)
    operation = env("RLL_CLIMATE_OPERATION") or "TOKEN_VAZIO"
    bridge_rc = 2
    bridge = {}
    decision = "FAIL_CLOSED"
    error_state = None

    try:
        operation, argv = build_argv()
        completed = subprocess.run(argv, check=False, env=os.environ.copy())
        bridge_rc = completed.returncode
        if BRIDGE_RECEIPT.exists():
            bridge = json.loads(BRIDGE_RECEIPT.read_text(encoding="utf-8"))
            forbidden = RECEIPT_FORBIDDEN_KEYS.intersection({k.lower() for k in walk_keys(bridge)})
            if forbidden:
                raise RuntimeError(f"forbidden receipt fields present: {sorted(forbidden)}")
        else:
            raise RuntimeError("bridge receipt was not materialized")

        artifacts = list(OUT.rglob("*"))
        assert_secret_absent(artifacts, secret)
        gate = bridge.get("gate_status")
        if bridge_rc == 0 and gate == "EXTERNAL_COMPUTE_RESPONSE_OBSERVED" and secret_present:
            decision = "PASS_BOUNDED_EXTERNAL_COMPUTE"
        elif gate == "BLOCKED_CREDENTIAL":
            decision = "BLOCKED_CREDENTIAL"
        else:
            decision = "FAIL_CLOSED"
    except Exception as exc:
        error_state = type(exc).__name__
        decision = "FAIL_CLOSED"

    sanitized_products = []
    for path in sorted(OUT.glob("*.sanitized.json")):
        sanitized_products.append({"path": str(path), "sha256": sha256_file(path)})

    control = {
        "schema": "rll.climate_engine_live_control_receipt.v1",
        "provider": "Climate Engine",
        "provider_role": "EXTERNAL_COMPUTE_AND_VISUALIZATION",
        "repository": os.environ.get("GITHUB_REPOSITORY", "TOKEN_VAZIO"),
        "commit_sha": os.environ.get("GITHUB_SHA", "TOKEN_VAZIO"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "TOKEN_VAZIO"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "TOKEN_VAZIO"),
        "operation": operation,
        "secret_name": "RLL_CLIMATE_ENGINE_TRIAL_TOKEN",
        "secret_binding_present_boolean": secret_present,
        "secret_value_persisted": False,
        "secret_hash_persisted": False,
        "secret_length_persisted": False,
        "bridge_returncode": bridge_rc,
        "bridge_gate_status": bridge.get("gate_status", "TOKEN_VAZIO"),
        "bridge_receipt_sha256": sha256_file(BRIDGE_RECEIPT) if BRIDGE_RECEIPT.exists() else None,
        "sanitized_products": sanitized_products,
        "decision": decision,
        "error_state": error_state,
        "source_primary_authority": "PRESERVE_UPSTREAM_DATASET_AUTHORITY",
        "provider_output_state": "EXTERNAL_COMPUTE_PRODUCT",
        "cause": "TOKEN_VAZIO_CAUSA",
        "claim_allowed": False,
        "F_gap": "provider output is not independent causal evidence",
        "F_next": "bind receipt to independently sourced RLL path before numerical or causal promotion",
    }
    CONTROL_RECEIPT.write_text(json.dumps(control, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    assert_secret_absent([CONTROL_RECEIPT, BRIDGE_RECEIPT, *OUT.glob("*.sanitized.json")], secret)

    print(json.dumps({
        "decision": decision,
        "operation": operation,
        "secret_binding_present_boolean": secret_present,
        "bridge_gate_status": control["bridge_gate_status"],
        "claim_allowed": False,
    }, sort_keys=True))
    return 0 if decision == "PASS_BOUNDED_EXTERNAL_COMPUTE" else (bridge_rc if bridge_rc else 2)


if __name__ == "__main__":
    raise SystemExit(main())
