import hashlib
import json
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CROSSWALK = ROOT / "data/science/rll_recent_data_crosswalk_20260828.v1.json"
CUSTODY = ROOT / "data/science/rll_recent_data_custody_status_20260828.v1.json"
RECEIPT = ROOT / "provenance/receipts/rll_recent_data_crosswalk_20260828.json"


def load():
    return json.loads(CROSSWALK.read_text(encoding="utf-8"))


def test_recent_data_crosswalk_is_fail_closed():
    c = load()
    assert c["claim_allowed"] is False
    assert c["publication_ready"] is False
    assert c["atlas_effect"]["G2"].startswith("PARTIAL_")
    assert c["atlas_effect"]["G3"].startswith("PARTIAL_")
    assert c["atlas_effect"]["G4"].startswith("PARTIAL_")
    assert c["atlas_effect"]["G6"] == "BLOCKED_UNCHANGED"
    assert c["atlas_effect"]["G7"] == "BLOCKED"


def test_receipt_pins_exact_crosswalk_bytes():
    receipt = json.loads(RECEIPT.read_text(encoding="utf-8"))
    digest = hashlib.sha256(CROSSWALK.read_bytes()).hexdigest()
    assert receipt["crosswalk_sha256"] == digest
    assert receipt["claim_allowed"] is False
    assert receipt["publication_ready"] is False


def test_h54_external_custody_blocker_is_append_only_and_fail_closed():
    c = json.loads(CUSTODY.read_text(encoding="utf-8"))
    h54 = c["H54"]
    assert c["mode"] == "APPEND_ONLY_SUCCESSOR"
    assert c["claim_allowed"] is False
    assert c["publication_ready"] is False
    assert h54["previous_state"] == "PRIORITY_INCREASED_TOKEN_VAZIO_JOINT_COVARIANCE"
    assert h54["effective_state"] == "OPEN_EXTERNAL_PUBLIC_CUSTODY_BLOCKER"
    assert "covariance" in " ".join(h54["not_established_public_custody"]).lower()
    assert c["atlas_effect"]["G2"] == "PARTIAL_UNCHANGED"
    assert c["atlas_effect"]["G7"] == "BLOCKED"


def test_h51_is_retrospective_not_confirmation():
    c = load()
    h = c["cross_tests"]["H51"]
    assert h["status"] == "RETROSPECTIVE_CONSISTENCY_ONLY"
    assert h["generated_after_sources"] is True
    assert h["fixed_crossing"]["a"] == 0.75
    assert math.isclose(h["fixed_crossing"]["z"], 1.0 / 3.0, rel_tol=0, abs_tol=1e-15)
    for row in h["central_value_projections"]:
        assert math.isclose(
            row["central_residual_wa"],
            row["wa_observed"] - row["wa_from_H51_w0"],
            rel_tol=0,
            abs_tol=1e-12,
        )


def test_h51_projection_matches_exact_line():
    c = load()
    constraints = {
        row["combination"]: row
        for src in c["sources"]
        if src["id"] == "DES_Y6_DDE_2026"
        for row in src["cpl_constraints"]
    }
    projections = {row["combination"]: row for row in c["cross_tests"]["H51"]["central_value_projections"]}
    for combination, obs in constraints.items():
        expected_wa = -4.0 * (obs["w0"] + 1.0)
        assert math.isclose(projections[combination]["wa_from_H51_w0"], expected_wa, abs_tol=1e-12)


def test_h03_values_follow_declared_formula():
    c = load()
    h = c["cross_tests"]["H03"]
    s = math.sqrt(3.0) / 2.0
    f = lambda z: -1.0 + (1.0 + z) * math.log(s) / 3.0
    assert math.isclose(h["w_at_z0"], f(0.0), abs_tol=1e-15)
    assert math.isclose(h["w_at_z2p33"], f(2.33), abs_tol=1e-15)
    assert h["w_at_z0"] < -1.0 and h["w_at_z2p33"] < -1.0
    assert h["status"] == "QUALITATIVE_TENSION_NOT_EXACT_TEST"


def test_lya_overlap_and_growth_exclusion_are_explicit():
    c = load()
    desi = next(s for s in c["sources"] if s["id"] == "DESI_DR2_LYA_FS_2026")
    text = " ".join(desi["boundary"]).lower()
    assert "must not be appended as an independent likelihood block" in text
    assert "f_sigma8" in text
    h53 = c["cross_tests"]["H53"]
    assert "do not substitute" in h53["forbidden_proxy"].lower()
    assert "excluded" in h53["forbidden_proxy"].lower()


def test_recent_sources_predate_h51_registration():
    c = load()
    source_dates = [s["release_date"] for s in c["sources"]]
    assert max(source_dates) < "2026-08-27"
    assert c["authority"]["hypothesis_packet_pr"] == 777


def test_required_epistemic_invariants_present():
    c = load()
    required = {
        "RECENT_DATA_NE_CONFIRMATION",
        "POST_HOC_NE_HELD_OUT",
        "CENTRAL_VALUE_NE_COVARIANCE_TEST",
        "OVERLAPPING_LYA_AP_BAO_NE_INDEPENDENT_BLOCKS",
        "EXCLUDED_GROWTH_ESTIMATE_NE_RLL_GROWTH_EVIDENCE",
        "PARTIAL_NE_VERIFIED",
        "CLAIM_ALLOWED_FALSE_UNTIL_GATES_CLOSE",
    }
    assert required.issubset(set(c["invariants"]))
