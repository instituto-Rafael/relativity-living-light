import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/contracts/dataset_rights_reconciliation_20260822.v1.json"


def load():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_rights_reconciliation_is_fail_closed():
    data = load()
    assert data["schema"] == "rll.dataset_rights_reconciliation.v1"
    assert data["append_only"] is True
    assert data["claim_allowed"] is False
    assert data["legal_effect_claim"] is False
    assert data["training_allowed"] is False
    assert data["redistribution_allowed"] is False
    assert data["predecessor"]["rights_complete"] == 0
    assert data["predecessor"]["license_verified"] == 0
    rec = data["reconciliation"]
    assert rec["rights_consequence"] == "NO_PERMISSION_PROMOTION"
    assert rec["dataset_v2_state_preserved"] is True
    assert rec["rights_complete_after_reconciliation"] == 0
    assert rec["license_verified_after_reconciliation"] == 0
    assert rec["training_allowed_after_reconciliation"] is False
    assert rec["redistribution_allowed_after_reconciliation"] is False


def test_root_license_observation_does_not_grant_third_party_rights():
    data = load()
    root = next(x for x in data["later_evidence"] if x["event_id"] == "ROOT-LICENSE-OBSERVED-20260822")
    blocked = set(root["does_not_imply"])
    assert "third_party_dataset_permission" in blocked
    assert "training_permission_for_external_material" in blocked
    assert "redistribution_permission_for_external_material" in blocked


def test_des_sn5yr_negative_audit_remains_conservative():
    data = load()
    audit = next(x for x in data["later_evidence"] if x["event_id"] == "DES-SN5YR-NEGATIVE-ROOT-LICENSE-AUDIT-20260807")
    assert audit["redistribution_allowed_by_audit"] is False
    route = next(x for x in data["dataset_routes"] if x["dataset_id"] == "DS-DES-SN5YR")
    assert route["state"] == "BLOCKED_NEGATIVE_ROOT_LICENSE_EVIDENCE"


def test_rights_routes_have_unique_ids_and_no_permission_promotion():
    data = load()
    routes = data["dataset_routes"]
    ids = [x["dataset_id"] for x in routes]
    assert len(ids) == len(set(ids))
    for route in routes:
        assert route["state"].startswith(("TOKEN_VAZIO", "BLOCKED_"))
        assert route["F_next"].strip()


def test_later_evidence_is_bound_to_existing_repository_artifacts():
    data = load()
    for event in data["later_evidence"]:
        assert (ROOT / event["path"]).exists(), event["path"]
        sha = event["git_blob_sha1"]
        assert len(sha) == 40
        assert all(c in "0123456789abcdef" for c in sha)
