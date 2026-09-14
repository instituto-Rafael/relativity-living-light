#!/usr/bin/env python3
"""Fail-closed validator for the public cosmological matter observation contract."""

from __future__ import annotations

import argparse
import json
import re
from pathlib import Path
from typing import Any

REQUIRED = {
    "manifest_id", "evidence_state", "target", "target_layer", "probe_family",
    "method", "spectral_coordinate", "instrument", "calibration",
    "uncertainty", "provenance", "retrieval", "epistemic_boundary",
    "claim_allowed",
}
PRIVATE_PATTERNS = [
    re.compile(r"/(?:home|data/data|sdcard|storage/emulated)/", re.I),
    re.compile(r"[A-Z]:\\\\", re.I),
    re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----"),
    re.compile(r"\bgh[pousr]_[A-Za-z0-9_]{20,}\b"),
]

def fail(message: str) -> None:
    raise ValueError(message)

def load(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        fail("manifest must be an object")
    return data

def classify_wavelength_m(value: float) -> str:
    if value <= 0:
        fail("wavelength must be positive")
    if value < 1e-8:
        return "x_ray_or_gamma"
    if value < 4e-7:
        return "ultraviolet"
    if value < 7e-7:
        return "visible"
    if value < 3e-6:
        return "near_infrared"
    if value < 3e-5:
        return "mid_infrared"
    if value < 1e-3:
        return "far_infrared_submillimeter"
    if value < 1e-1:
        return "microwave"
    return "radio"

def to_wavelength_m(value: float, unit: str) -> float:
    factors = {"m":1.0, "mm":1e-3, "um":1e-6, "µm":1e-6, "nm":1e-9}
    if unit not in factors:
        fail(f"unsupported wavelength unit: {unit}")
    return value * factors[unit]

def scan_private(data: dict[str, Any]) -> None:
    text = json.dumps(data, ensure_ascii=False)
    for pattern in PRIVATE_PATTERNS:
        if pattern.search(text):
            fail("private path or secret-like material detected")

def validate(data: dict[str, Any]) -> None:
    missing = sorted(REQUIRED - data.keys())
    if missing:
        fail(f"missing fields: {', '.join(missing)}")
    if data.get("claim_allowed") is not False:
        fail("claim_allowed must be false")
    if data.get("provenance", {}).get("private_data_included") is not False:
        fail("private_data_included must be false")
    if data.get("epistemic_boundary", {}).get("composition_is_inference") is not True:
        fail("composition_is_inference must be true")

    instrument = data.get("instrument", {})
    calibration = data.get("calibration", {})
    uncertainty = data.get("uncertainty", {})
    retrieval = data.get("retrieval", {})
    for key in ("response_declared", "resolution_declared"):
        if instrument.get(key) is not True:
            fail(f"instrument.{key} must be true")
    for key in ("units_declared", "background_declared"):
        if calibration.get(key) is not True:
            fail(f"calibration.{key} must be true")
    for key in ("statistical_declared", "systematics_declared"):
        if uncertainty.get(key) is not True:
            fail(f"uncertainty.{key} must be true")
    for key in ("model", "line_or_reference_database", "falsifier"):
        if not isinstance(retrieval.get(key), str) or not retrieval[key].strip():
            fail(f"retrieval.{key} must be non-empty")
    if retrieval.get("priors_declared") is not True:
        fail("retrieval.priors_declared must be true")
    if retrieval.get("alternatives_tested") is not True:
        fail("retrieval.alternatives_tested must be true")

    spectral = data.get("spectral_coordinate", {})
    if spectral.get("kind") == "wavelength":
        unit = spectral.get("unit")
        low = spectral.get("min")
        high = spectral.get("max")
        if not isinstance(low, (int, float)) or not isinstance(high, (int, float)):
            fail("wavelength min/max must be numeric")
        if low <= 0 or high <= low:
            fail("invalid wavelength interval")
        to_wavelength_m(float(low), str(unit))
        to_wavelength_m(float(high), str(unit))

    scan_private(data)

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("manifest", type=Path)
    args = parser.parse_args()
    data = load(args.manifest)
    validate(data)
    print("PASS: structural contract valid; scientific claim remains blocked")
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
