import copy
import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/run_g3_dataset_compatibility.py"
CONTRACT_PATH = ROOT / "data/contracts/rll_g3_dataset_compatibility.v1.json"


def load_module():
    spec = importlib.util.spec_from_file_location("g3", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_g3_current_repository_passes_limited_compatibility_branch():
    mod = load_module()
    report = mod.build_report(ROOT)
    assert report["state"] == "PASS_LIMITED_COMPATIBILITY_BRANCH"
    assert report["claim_allowed"] is False
    assert report["scientific_confirmation"] is False
    assert report["F_AP_gate"]["passed"] is True
    assert report["primary_table_transcription"]["passed"] is True
    assert report["SN_sample_comparison"]["passed"] is True
    assert report["eta_z_gate"]["branch"] == "SHARED_RANGE_PLUS_DESI_HIGH_Z_EXTENSION"
    assert report["compatibility_decision"]["allowed"] is True


def test_g3_keeps_reconstruction_and_cross_survey_residuals_visible():
    mod = load_module()
    report = mod.build_report(ROOT)
    assert "TOKEN_VAZIO_INDEPENDENT_DESI_RECONSTRUCTION_ABLATION" in report["F_gap"]
    assert "TOKEN_VAZIO_EXPLICIT_CROSS_SURVEY_COVARIANCE_MATRIX" in report["F_gap"]
    assert report["reconstruction_sensitivity_report"]["rll_independent_reconstruction_ablation"].startswith("TOKEN_VAZIO")


def test_g3_source_contract_cannot_promote_claim():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert contract["claim_allowed"] is False
    assert contract["joint_branch"]["claim_allowed"] is False
    assert contract["diagnostics"]["eta_z"]["role"].startswith("coverage diagnostic")


def test_fap_gate_uses_primary_sigma_not_exact_rounded_ratio():
    mod = load_module()
    report = mod.build_report(ROOT)
    checks = report["F_AP_gate"]["checks"]
    assert len(checks) == 6
    assert all(item["delta_in_primary_sigma"] <= 1.0 for item in checks)
    # QSO demonstrates why exact equality to a rounded source ratio would be wrong.
    qso = next(item for item in checks if item["tracer"] == "QSO")
    assert qso["absolute_delta"] > 0.0
    assert qso["passed"] is True


def test_pantheon_overlap_is_not_falsely_required_to_cover_high_z_lya():
    mod = load_module()
    report = mod.build_report(ROOT)
    eta = report["eta_z_gate"]
    assert eta["desi_observables_inside_pantheon_span"] < eta["desi_observables_total"]
    assert all(z > eta["pantheon_zHD_span"][1] for z in eta["outside_z"])
    assert eta["passed"] is True
