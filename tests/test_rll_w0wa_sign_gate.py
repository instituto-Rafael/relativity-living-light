from __future__ import annotations

import importlib.util
import json
import math
from pathlib import Path

from tools import rll_w0wa_sign_gate as gate

ROOT = Path(__file__).resolve().parents[1]


def _load_mapper():
    path = ROOT / "scripts/map_rll_to_w0wa_eff.py"
    spec = importlib.util.spec_from_file_location("rll_mapper", path)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def test_sector_wa_exact_coefficient_is_three_plus_one_over_wt() -> None:
    zt = 1.2
    wt = 0.35
    f0 = gate.stable_f0(zt, wt)
    w0, wa = gate.sector_local_cpl(zt, wt)
    assert math.isclose(w0, -f0, abs_tol=1e-15)
    assert math.isclose(wa, f0 * (1.0 - f0) * (3.0 + 1.0 / wt), abs_tol=1e-15)
    wrong_two_over_wt = f0 * (1.0 - f0) * (3.0 + 2.0 / wt)
    assert not math.isclose(wa, wrong_two_over_wt, rel_tol=1e-6)


def test_total_dark_analytic_wa_matches_numeric_mapper_definition() -> None:
    mapper = _load_mapper()
    om = 0.315
    os0 = 0.08
    ol = 1.0 - om - os0
    zt = 1.2
    wt = 0.35

    w0, wa = gate.total_dark_local_cpl(ol, os0, zt, wt)

    def fn(a: float) -> float:
        return mapper.rll_dark_w(a, om, os0, zt, wt)

    wa_numeric = -mapper.derivative_dw_da(fn, h=1.0e-5)
    assert math.isclose(w0, fn(1.0), abs_tol=1e-13)
    assert math.isclose(wa, wa_numeric, abs_tol=1e-8)


def test_os0_zero_is_lcdm_local_limit_and_zt_wt_inactive() -> None:
    for zt in (0.1, 1.2, 10.0):
        for wt in (0.05, 0.35, 2.0):
            w0, wa = gate.total_dark_local_cpl(0.68491, 0.0, zt, wt)
            assert math.isclose(w0, -1.0, abs_tol=1e-15)
            assert math.isclose(wa, 0.0, abs_tol=1e-15)


def test_current_rll_bounds_have_nonnegative_local_wa_domain() -> None:
    contract = json.loads((ROOT / "data/contracts/cosmology_model_family_shadow.v1.json").read_text())
    registry = json.loads((ROOT / "data/governance/RLL_EXTERNAL_EVIDENCE_REGISTRY_V1.json").read_text())
    cfg = json.loads((ROOT / "data/governance/RLL_W0WA_SIGN_FALSIFIABILITY_GATE_V1.json").read_text())
    report = gate.build_report(contract, registry, cfg)
    assert report["canonical_sign_theorem"]["pass"] is True
    assert report["canonical_sign_theorem"]["w0_domain_pass"] is True
    assert report["canonical_sign_theorem"]["min_w0_eff"] >= -1.0 - 1e-12
    assert report["canonical_sign_theorem"]["max_w0_eff"] < 0.0
    assert report["canonical_sign_theorem"]["min_wa_eff"] >= -1e-12
    assert report["canonical_sign_theorem"]["derivative_crosscheck_pass"] is True


def test_external_2026_joint_fs_bao_w0_sign_is_positive_not_negative() -> None:
    registry = json.loads((ROOT / "data/governance/RLL_EXTERNAL_EVIDENCE_REGISTRY_V1.json").read_text())
    src = next(x for x in registry["sources"] if x["id"] == "DESI_DR1_FS_DR2_BAO_2026")
    assert src["published_context"]["w0"]["value"] == 0.49
    assert src["published_context"]["wa"]["value"] == -1.52
    assert src["dataset_identity"] == "DESI_DR1_FULL_SHAPE_PLUS_DESI_DR2_BAO"


def test_sign_tension_is_not_auto_promoted_to_falsified() -> None:
    cfg = json.loads((ROOT / "data/governance/RLL_W0WA_SIGN_FALSIFIABILITY_GATE_V1.json").read_text())
    assert cfg["observational_gate"]["state"] == "STRUCTURAL_SIGN_TENSION_NOT_YET_FALSIFICATION"
    assert "posterior" in cfg["observational_gate"]["falsification_condition"].lower()
    assert cfg["claim_allowed"] is False


def test_custom_license_is_separate_from_scientific_falsifiability() -> None:
    cfg = json.loads((ROOT / "data/governance/RLL_W0WA_SIGN_FALSIFIABILITY_GATE_V1.json").read_text())
    boundary = cfg["license_boundary"]
    assert boundary["repository_license_is_standard_spdx"] is False
    assert boundary["scientific_falsifiability_depends_on_license"] is False
    assert boundary["operational_reproducibility_may_be_affected"] is True



def test_wa_halfplane_is_only_a_coarse_gate_not_full_rll_domain() -> None:
    cfg = json.loads((ROOT / "data/governance/RLL_W0WA_SIGN_FALSIFIABILITY_GATE_V1.json").read_text())
    required = " ".join(cfg["observational_gate"]["required_next_test"]).lower()
    assert "p(wa>=0" in required
    assert "2d posterior overlap" in required
    assert "P(wa>=0) != FULL_2D_RLL_DOMAIN_OVERLAP" in cfg["invariants"]
