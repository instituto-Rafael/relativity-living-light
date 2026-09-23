#!/usr/bin/env python3
"""Build/validate the fail-closed RX-PHYSICS-CANONICAL-V2 decision packet."""
from __future__ import annotations

import argparse
import json
from pathlib import Path

from rx.kernel import dump_json, load_json

ROOT = Path(__file__).resolve().parents[1]
AUTHORITY = ROOT / "data/governance/RLL_RX_PHYSICS_V2_DECISION_AUTHORITY_V1.json"
CONTRACTS = ROOT / "configs/rx_physics_contracts.json"
OUT = ROOT / "results/rx_physics_v2_decision_packet.json"


def build():
    authority = load_json(AUTHORITY)
    contracts = load_json(CONTRACTS)
    if authority.get("schema") != "rll.rx.physics_v2_decision_authority.v1":
        raise ValueError("unsupported decision authority schema")
    if authority.get("claim_allowed") is not False:
        raise ValueError("decision authority must remain claim_allowed=false")
    target = contracts.get("contracts", {}).get(authority.get("target_contract"))
    if not isinstance(target, dict):
        raise ValueError("target physics contract missing")
    if target.get("state") != "TOKEN_VAZIO_CONTRACT":
        raise ValueError("decision packet is only valid while canonical V2 remains TOKEN_VAZIO_CONTRACT")

    known = contracts.get("contracts", {})
    rows = []
    blocking = []
    for axis in authority.get("axes", []):
        axis_id = str(axis.get("id", ""))
        if not axis_id or axis_id not in target:
            raise ValueError("axis not present in target contract: %s" % axis_id)
        for option in axis.get("options", []):
            source = option.get("source_contract")
            if isinstance(source, str) and source.startswith("RX-") and source not in known:
                raise ValueError("unknown source contract %s for %s" % (source, axis_id))

        selected = str(axis.get("selected_option", "TOKEN_VAZIO"))
        terminal = not selected.startswith("TOKEN_VAZIO")
        evidence = list(axis.get("required_decision_evidence", []))
        if not terminal:
            blocking.append(axis_id)
        rows.append({
            "axis": axis_id,
            "target_current_value": target.get(axis_id),
            "selected_option": selected,
            "decision_terminal": terminal,
            "required_decision_evidence": evidence,
            "options": axis.get("options", []),
        })

    state = "READY_FOR_VERSIONED_SCIENTIFIC_DECISIONS" if blocking else "READY_FOR_CANONICAL_V2_IMPLEMENTATION"
    return {
        "schema": "rll.rx.physics_v2_decision_packet.v1",
        "target_contract": authority["target_contract"],
        "target_state": target.get("state"),
        "state": state,
        "blocking_axes": blocking,
        "axes": rows,
        "decision_rule": authority.get("decision_rule"),
        "promotion_requirements": authority.get("promotion_requirements", []),
        "claim_allowed": False,
        "boundary": "This packet exposes choices and required evidence. It does not choose scientific semantics from fit quality or assistant preference.",
    }


def main(argv=None):
    parser = argparse.ArgumentParser()
    parser.add_argument("--write", action="store_true")
    args = parser.parse_args(argv)
    payload = build()
    if args.write:
        dump_json(OUT, payload)
    print(json.dumps({
        "state": payload["state"],
        "blocking_axes": payload["blocking_axes"],
        "claim_allowed": False,
    }, ensure_ascii=False, indent=2))
    if args.write:
        print("wrote", OUT.relative_to(ROOT))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
