#!/usr/bin/env python3
import json
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MESH = ROOT / "data/registries/rll_session_evolution_mesh.v1.json"
LEDGER = ROOT / "data/registries/rll_session_interaction_ledger_20260827.v1.json"
B10 = ROOT / "data/registries/rll_mpemba_horizon_closure_registry.v1.json"
ATLAS_GATE = ROOT / "data/governance/RLL_ATLAS_EVOLUTION_GATE_20260827_V1.json"
RECEIPT = ROOT / "provenance/receipts/rll_session_evolution_mesh_20260827.json"
ATLAS = ROOT / "docs/RLL_SESSION_EVOLUTION_ATLAS_20260827.md"


def load(path: Path):
    if not path.exists():
        raise AssertionError(f"missing artifact: {path.relative_to(ROOT)}")
    return json.loads(path.read_text(encoding="utf-8"))


def main() -> int:
    mesh = load(MESH)
    ledger = load(LEDGER)
    b10 = load(B10)
    atlas_gate = load(ATLAS_GATE)
    receipt = load(RECEIPT)
    if not ATLAS.exists():
        raise AssertionError("missing session ATLAS")

    assert mesh["schema"] == "rll.session_evolution_mesh.v1"
    assert mesh["authority"] == "instituto-Rafael/relativity-living-light"
    assert mesh["baseline_commit"] == "75323d72c9c8d0180c2a01dfb7c7601f5da735c5"
    assert mesh["predecessor_closure_commit"] == "30e4d2fd7af3d7b9db3096ba530b72d0275e37f2"
    assert mesh["claim_allowed"] is False
    assert mesh["no_untracked_session_gaps"] is True

    fences = mesh["six_continuous_evolution_fences"]
    expected = {
        "FENCE-01-AUTHORITY",
        "FENCE-02-NONREGRESSION",
        "FENCE-03-FALSIFIABILITY",
        "FENCE-04-ROLLBACK",
        "FENCE-05-DRIFT",
        "FENCE-06-INDEPENDENCE",
    }
    assert len(fences) == 6
    assert {f["id"] for f in fences} == expected
    for fence in fences:
        assert fence["state"] == "ENFORCED"
        assert fence["rule"].strip()
        assert fence["automatic_check"].strip()
        assert fence["risk_reduced"]
        assert fence["maps_to_existing_gates"]

    assert mesh["continuous_operation"]["autonomous_validation"] is True
    assert mesh["continuous_operation"]["autonomous_source_writes"] is False
    assert mesh["continuous_operation"]["failure_mode"] == "FAIL_CLOSED"

    assert b10["no_untracked_gaps"] is True
    assert b10["global_scientific_claim_allowed"] is False
    b10_items = {item["id"]: item for item in b10["items"]}
    for gap_id in ("B10-CLOSE-P0-001", "B10-CLOSE-P0-002", "B10-CLOSE-P0-003", "B10-CLOSE-P0-005"):
        assert gap_id in b10_items
    assert b10_items["B10-CLOSE-P0-005"]["owner_class"] == "INDEPENDENT_OPERATOR_OR_REPOSITORY"

    assert atlas_gate["schema"] == "rll.atlas_evolution_gate.v1"
    assert atlas_gate["append_only"] is True
    assert atlas_gate["claim_allowed"] is False
    gates = {g["id"]: g for g in atlas_gate["gates"]}
    assert gates["G7_CLAIM_DECISION"]["status"] == "BLOCKED"
    assert gates["G7_CLAIM_DECISION"]["maturity"] == 0
    blockers = {x["token"]: x for x in atlas_gate["blocking_tokens"]}
    assert blockers["TOKEN_VAZIO_INDEPENDENT_REPLICATION"]["state"] == "OPEN"
    assert blockers["TOKEN_VAZIO_INDEPENDENT_REPLICATION"]["required_for_claim"] == "RESOLVED"
    assert atlas_gate["promotion_contract"]["no_regression"]["gate_maturity_non_decreasing"] is True
    assert atlas_gate["promotion_contract"]["no_regression"]["historical_records_append_only"] is True

    assert ledger["capture_mode"] == "SEMANTIC_TURN_RECEIPTS"
    assert ledger["verbatim_transcript_embedded"] is False
    assert ledger["session_state"]["untracked_material_prompts"] == 0
    assert ledger["session_state"]["scientific_claim_allowed"] is False
    assert ledger["session_state"]["concurrent_lab_evolution_consumed"] == "RLL_ATLAS_EVOLUTION_GATE_20260827_V1"
    ids = [row["id"] for row in ledger["interactions"]]
    assert ids == ["SESSION-20260827-P01", "SESSION-20260827-P02", "SESSION-20260827-P03"]
    for row in ledger["interactions"]:
        for key in ("intent", "response_contract", "risk_before", "risk_reduction", "artifacts_or_evidence", "remaining_gap_ids"):
            assert row[key], f"{row['id']} missing {key}"
        assert row["verbatim_prompt_sha256"] == "TOKEN_VAZIO"

    assert receipt["baseline_commit"] == mesh["baseline_commit"]
    assert receipt["predecessor_closure_commit"] == mesh["predecessor_closure_commit"]
    assert receipt["claim_boundary"]["scientific_claim_allowed"] is False
    assert receipt["claim_boundary"]["g0_g7_claim_allowed"] is False
    assert receipt["claim_boundary"]["independent_replication_self_closable"] is False
    assert receipt["custody"]["raw_chat_transcript_materialized"] is False
    assert receipt["custody"]["raw_chat_transcript_sha256"] == "TOKEN_VAZIO"

    print(json.dumps({
        "status": "PASS",
        "schema": mesh["schema"],
        "fences": len(fences),
        "interactions": len(ledger["interactions"]),
        "b10_no_untracked_gaps": True,
        "g7_status": gates["G7_CLAIM_DECISION"]["status"],
        "independent_replication_blocker": blockers["TOKEN_VAZIO_INDEPENDENT_REPLICATION"]["state"],
        "scientific_claim_allowed": False,
        "autonomous_source_writes": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    try:
        raise SystemExit(main())
    except (AssertionError, KeyError, json.JSONDecodeError) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        raise SystemExit(2)
