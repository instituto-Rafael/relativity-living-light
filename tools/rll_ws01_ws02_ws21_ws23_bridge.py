#!/usr/bin/env python3
"""Bind WS21 + WS02 + WS01 into a fail-closed WS23 readiness receipt.

This tool does not choose unresolved physics. It verifies that the canonical
background data/likelihood surface is internally consistent, freezes the exact
local bytes consumed by G4/G5, reads the existing RX-PHYSICS-CANONICAL-V2
decision packet, and computes which H(z)/BAO/SN bindings remain blocked.

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from rx.kernel import dump_json, load_json
from tools.rll_current_rx_source_freeze import build as build_source_freeze
from tools.rx_physics_v2_decision_packet import build as build_physics_decision

ROOT = Path(__file__).resolve().parents[1]
WS02 = ROOT / "data/contracts/rll_ws02_canonical_background_surface.v1.json"
G4 = ROOT / "data/contracts/rll_g4_background_tournament.v1.json"
G5 = ROOT / "data/contracts/rll_g5_canonical_background_likelihood.v1.json"
BINDINGS = ROOT / "data/inputs/omega_g/observable_effect_binding_registry.v2.json"
FREEZE_SPEC = ROOT / "data/governance/RLL_CANONICAL_BACKGROUND_SOURCE_FREEZE_SPEC_V1.json"
OUT = ROOT / "artifacts/science/integration/RLL_WS01_WS02_WS21_WS23_BRIDGE_RECEIPT.json"

BACKGROUND_BINDINGS = ("OGB-HZ-001", "OGB-BAO-001", "OGB-SN-001")


def _sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def _must_file(rel: str, blockers: list[str], hashes: dict[str, str]) -> None:
    path = ROOT / rel
    if not path.is_file():
        blockers.append("MISSING:" + rel)
        return
    hashes[rel] = _sha256(path)


def _ws02_consistency() -> dict[str, Any]:
    ws02 = load_json(WS02)
    g4 = load_json(G4)
    g5 = load_json(G5)
    blockers: list[str] = []
    hashes: dict[str, str] = {}

    if ws02.get("schema") != "rll.ws02.canonical_background_surface.v1":
        blockers.append("WS02_SCHEMA")
    if ws02.get("claim_allowed") is not False:
        blockers.append("WS02_CLAIM_BOUNDARY")
    if ws02.get("scope") != g5.get("scope"):
        blockers.append("WS02_G5_SCOPE_MISMATCH")
    if list(ws02.get("models", [])) != list(g5.get("model_policy", {}).get("models", [])):
        blockers.append("WS02_G5_MODEL_ORDER_MISMATCH")

    blocks = ws02.get("blocks", {})
    g4_data = g4.get("datasets", {})

    cc = blocks.get("cosmic_chronometers", {})
    g4_cc = g4_data.get("cosmic_chronometers", {})
    if cc.get("path") != g4_cc.get("path"):
        blockers.append("CC_PATH_MISMATCH")
    if cc.get("selection") != g4_cc.get("selection"):
        blockers.append("CC_SELECTION_MISMATCH")

    desi = blocks.get("desi_dr2_bao", {})
    g4_desi = g4_data.get("desi_dr2_bao", {})
    if desi.get("points") != g4_desi.get("points"):
        blockers.append("DESI_POINTS_MISMATCH")
    if desi.get("covariance") != g4_desi.get("covariance"):
        blockers.append("DESI_COVARIANCE_MISMATCH")

    pan = blocks.get("pantheon_plus", {})
    g4_pan = g4_data.get("pantheon_plus", {})
    for key in ("catalog", "covariance", "selection"):
        if pan.get(key) != g4_pan.get(key):
            blockers.append("PANTHEON_" + key.upper() + "_MISMATCH")
    if pan.get("nuisance") != g4_pan.get("nuisance"):
        blockers.append("PANTHEON_NUISANCE_MISMATCH")

    source_freeze = build_source_freeze(FREEZE_SPEC)
    source_by_path = {
        str(row.get("path")): row
        for row in source_freeze.get("inputs", [])
        if isinstance(row, dict)
    }
    for rel in (
        str(cc.get("path", "")),
        str(desi.get("points", "")),
        str(desi.get("covariance", "")),
        str(pan.get("catalog", "")),
        str(pan.get("covariance", "")),
    ):
        if not rel:
            continue
        source_row = source_by_path.get(rel)
        digest = str((source_row or {}).get("sha256", ""))
        if len(digest) == 64:
            hashes[rel] = digest
        else:
            blockers.append("SOURCE_CUSTODY_UNAVAILABLE:" + rel)

    shared = ws02.get("shared_policy", {})
    for key in ("growth", "cmb"):
        if "EXCLUDED" not in str(shared.get(key, "")):
            blockers.append(key.upper() + "_BACKGROUND_PROMOTION_NOT_BLOCKED")

    return {
        "state": "PASS_WS02_SURFACE_CONSISTENCY" if not blockers else "BLOCKED_WS02_SURFACE_CONSISTENCY",
        "blockers": blockers,
        "input_sha256": hashes,
        "ws02_contract_sha256": _sha256(WS02),
        "g4_contract_sha256": _sha256(G4),
        "g5_contract_sha256": _sha256(G5),
        "claim_allowed": False,
    }


def _binding_state(binding: dict[str, Any], *, ws02_ok: bool, g0_closed: bool, blocking_axes: set[str]) -> dict[str, Any]:
    reasons: list[str] = []
    if not ws02_ok:
        reasons.append("WS02_SURFACE_NOT_VALID")
    if not g0_closed:
        reasons.append("WS21_G0_AUTHORITY_OR_RIGHTS_OPEN")
    required = [str(x) for x in binding.get("required_ws01_axes", [])]
    unresolved = sorted(set(required) & blocking_axes)
    if unresolved:
        reasons.extend("WS01_AXIS:" + axis for axis in unresolved)
    state = "READY_BACKGROUND_BINDING" if not reasons else "BLOCKED"
    return {
        "binding_id": binding.get("binding_id"),
        "observable_id": binding.get("observable_id"),
        "state": state,
        "blockers": reasons,
        "required_ws01_axes": required,
        "claim_allowed": False,
    }


def build() -> dict[str, Any]:
    ws02 = _ws02_consistency()
    source_freeze = build_source_freeze(FREEZE_SPEC)
    physics = build_physics_decision()
    registry = load_json(BINDINGS)

    if registry.get("schema") != "rll.omega_g_observable_binding_registry.v2":
        raise ValueError("unexpected WS23 binding registry schema")
    if registry.get("claim_allowed") is not False:
        raise ValueError("WS23 binding registry must remain claim_allowed=false")

    by_id = {
        str(row.get("binding_id")): row
        for row in registry.get("bindings", [])
        if isinstance(row, dict)
    }
    missing = [binding_id for binding_id in BACKGROUND_BINDINGS if binding_id not in by_id]
    if missing:
        raise ValueError("missing background binding(s): " + ",".join(missing))

    blocking_axes = set(str(x) for x in physics.get("blocking_axes", []))
    ws02_ok = ws02["state"] == "PASS_WS02_SURFACE_CONSISTENCY"
    g0_closed = bool(source_freeze.get("scientific_gate_closed"))
    bindings = [
        _binding_state(
            by_id[binding_id],
            ws02_ok=ws02_ok,
            g0_closed=g0_closed,
            blocking_axes=blocking_axes,
        )
        for binding_id in BACKGROUND_BINDINGS
    ]

    ready = all(row["state"] == "READY_BACKGROUND_BINDING" for row in bindings)
    state = "READY_WS23_BACKGROUND_BINDINGS" if ready else "BLOCKED_WS23_BACKGROUND_BINDINGS"

    return {
        "schema": "rll.ws01_ws02_ws21_ws23_bridge_receipt.v1",
        "state": state,
        "workstreams": {
            "WS21": {
                "state": source_freeze.get("state"),
                "scientific_gate_closed": g0_closed,
                "blockers": source_freeze.get("blockers", []),
            },
            "WS02": ws02,
            "WS01": {
                "state": physics.get("state"),
                "blocking_axes": sorted(blocking_axes),
                "target_contract": physics.get("target_contract"),
            },
            "WS23": {
                "bindings": bindings,
                "ready_count": sum(1 for row in bindings if row["state"] == "READY_BACKGROUND_BINDING"),
                "total_count": len(bindings),
            },
        },
        "source_freeze_spec_sha256": _sha256(FREEZE_SPEC),
        "binding_registry_sha256": _sha256(BINDINGS),
        "scientific_gate_effect": "NONE_UNTIL_PREREQUISITES_PASS",
        "growth_cmb_lensing_promotion": False,
        "negative_results_preserved": True,
        "claim_allowed": False,
        "F_ok": [
            "WS02 canonical background surface is executable and consistency-checkable",
            "WS21 canonical background bytes can be frozen independently of authority closure",
            "WS01 unresolved scientific decisions remain explicit",
            "WS23 H(z)/BAO/SN bindings are typed and dependency-aware",
        ],
        "F_gap": sorted(
            set(source_freeze.get("blockers", []))
            | set("WS01:" + axis for axis in blocking_axes)
            | set(ws02.get("blockers", []))
        ),
        "F_next": (
            "close source authority/rights blockers and make versioned WS01 decisions from preregistered "
            "evidence; rerun this bridge; only READY_WS23_BACKGROUND_BINDINGS may feed downstream multiprobe"
        ),
        "boundary": (
            "A typed binding is not evidence. This bridge refuses to promote H(z), BAO or SN while "
            "source authority or canonical physics semantics remain unresolved."
        ),
    }


def main(argv=None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    parser.add_argument("--require-ready", action="store_true")
    parser.add_argument("--output", type=Path, default=OUT)
    args = parser.parse_args(argv)
    receipt = build()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    if args.write:
        dump_json(output, receipt)
    print(json.dumps({
        "state": receipt["state"],
        "ws23_ready": receipt["workstreams"]["WS23"]["ready_count"],
        "ws23_total": receipt["workstreams"]["WS23"]["total_count"],
        "claim_allowed": False,
    }, ensure_ascii=False, indent=2))
    if args.write:
        print("wrote", output.relative_to(ROOT) if output.is_relative_to(ROOT) else output)
    if args.require_ready and receipt["state"] != "READY_WS23_BACKGROUND_BINDINGS":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
