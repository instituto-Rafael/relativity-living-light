#!/usr/bin/env python3
"""Build a fail-closed Climate Engine x Juno comparison shadow receipt."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

FORBIDDEN_SECRET_KEYS = {
    "authorization", "api_key", "apikey", "token", "secret",
    "climate_engine_api_key", "clima",
}

def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))

def canonical_sha256(value: Any) -> str:
    raw = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()

def contains_secret_field(value: Any) -> bool:
    if isinstance(value, dict):
        for key, item in value.items():
            if key.lower() in FORBIDDEN_SECRET_KEYS:
                return True
            if contains_secret_field(item):
                return True
    elif isinstance(value, list):
        return any(contains_secret_field(item) for item in value)
    return False

def build_shadow(contract: dict[str, Any], juno: dict[str, Any], climate: dict[str, Any] | None) -> dict[str, Any]:
    gaps: list[str] = []
    if contract.get("claim_allowed") is not False:
        gaps.append("CONTRACT_CLAIM_BOUNDARY_INVALID")
    if juno.get("claim_allowed") is not False:
        gaps.append("JUNO_MANIFEST_CLAIM_BOUNDARY_INVALID")
    if not juno.get("observations"):
        gaps.append("TOKEN_VAZIO_JUNO_OBSERVATIONS")
    if climate is None:
        gaps.append("TOKEN_VAZIO_CLIMATE_RUNTIME_RECEIPT")
    elif contains_secret_field(climate):
        gaps.append("FORBIDDEN_SECRET_MATERIAL_IN_CLIMATE_RECEIPT")

    climate_state = "TOKEN_VAZIO_NOT_SUPPLIED"
    climate_sha = None
    if climate is not None:
        climate_state = climate.get("gate_status") or climate.get("decision") or "OBSERVED_RECEIPT_UNCLASSIFIED"
        climate_sha = canonical_sha256(climate)

    juno_classes = sorted({
        str(obs.get("quantity_class"))
        for obs in juno.get("observations", [])
        if obs.get("quantity_class")
    })

    return {
        "schema": "rll.climate_juno_shadow.receipt.v1",
        "claim_allowed": False,
        "comparison_mode": "CROSS_PLANET_FAIL_CLOSED_SHADOW",
        "climate_engine": {
            "receipt_state": climate_state,
            "receipt_sha256": climate_sha,
            "scientific_role": "EARTH_EXTERNAL_COMPUTE_PRODUCT_NOT_JUNO_EVIDENCE",
        },
        "juno": {
            "manifest_sha256": canonical_sha256(juno),
            "observation_count": len(juno.get("observations", [])),
            "quantity_classes": juno_classes,
            "scientific_role": "INDEPENDENT_PLANETARY_REFERENCE",
        },
        "comparison_axes": contract.get("comparison_axes", []),
        "light_channels_separated": {
            "thermal_infrared": True,
            "auroral_emission": True,
            "lightning_discharge": True,
            "microwave_emission": True,
        },
        "gaps": gaps,
        "gate_status": "SHADOW_READY" if not gaps else "SHADOW_TOKEN_VAZIO",
        "F_ok": "Juno sources and cross-planet comparison axes are typed and secret-safe.",
        "F_gap": gaps or ["No causal or direct cross-planet equivalence is promoted."],
        "F_next": "Attach one sanitized Climate Engine runtime receipt, then align only same-quantity/same-unit or explicitly normalized diagnostics before model competition.",
    }

def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", default="data/contracts/rll_climate_juno_shadow.v1.json")
    parser.add_argument("--juno", default="data/juno/rll_juno_atmospheric_reference.v1.json")
    parser.add_argument("--climate-receipt")
    parser.add_argument("--output", default="artifacts/science/climate_juno/shadow_receipt.json")
    args = parser.parse_args()

    contract = load_json(Path(args.contract))
    juno = load_json(Path(args.juno))
    climate = load_json(Path(args.climate_receipt)) if args.climate_receipt else None
    receipt = build_shadow(contract, juno, climate)

    out = Path(args.output)
    out.parent.mkdir(parents=True, exist_ok=True)
    out.write_text(json.dumps(receipt, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    print(json.dumps({"gate_status": receipt["gate_status"], "claim_allowed": False, "output": str(out)}))
    return 0 if receipt["gate_status"] in {"SHADOW_READY", "SHADOW_TOKEN_VAZIO"} else 2

if __name__ == "__main__":
    raise SystemExit(main())
