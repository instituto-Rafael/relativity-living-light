from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "rll_primordial_assurance_v2.py"
SPEC = importlib.util.spec_from_file_location("rll_primordial_assurance_v2", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def test_neff_radiation_factor():
    assert math.isclose(mod.NEFF_RADIATION_FACTOR, 0.227107317660239, rel_tol=1e-14)


def test_act_bbn_gaussian_compatibility_envelope():
    row = mod.gaussian_neff_compatibility_envelope("ACT_DR6_PLUS_BBN_2025", 2.89, 0.11, role="HYBRID_COMPATIBILITY_PROXY")
    assert math.isclose(row.neff_upper, 3.1056, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(row.delta_neff_extra_upper, 0.0616, rel_tol=0, abs_tol=1e-12)
    assert math.isclose(row.omega_extra_h2_upper, 3.459400406679065e-7, rel_tol=1e-12)


def test_pdg_bbn_background_proxy_is_weaker_than_act_bbn_hybrid():
    rows = {r.source: r for r in mod.reference_neff_envelopes()}
    assert rows["PDG_BBN_2024"].omega_extra_h2_upper > rows["ACT_DR6_PLUS_BBN_2025"].omega_extra_h2_upper


def test_planck_proxy_is_weaker_than_act_dr6():
    rows = {r.source: r for r in mod.reference_neff_envelopes()}
    assert rows["PLANCK_BAO_2018"].omega_extra_h2_upper > rows["ACT_DR6_2025"].omega_extra_h2_upper


def test_omega_conversion_largest_at_small_h0():
    row = mod.gaussian_neff_compatibility_envelope("x", 2.89, 0.11)
    assert row.omega_extra_upper_at_h0_min > row.omega_extra_upper_at_h0_max


def test_radiation_sum_omega_h2():
    assert math.isclose(mod.radiation_sum_omega_h2(1e-6, 1e-6, 70.0), 9.8e-7, rel_tol=1e-15)


def test_blueprint_minimum_sum_exceeds_strongest_envelope_across_h0_range():
    row = mod.gaussian_neff_compatibility_envelope("ACT+BBN", 2.89, 0.11)
    diag = mod.blueprint_minimum_diagnostic(row.omega_extra_h2_upper)
    assert diag["minimum_exceeds_envelope_for_entire_declared_H0_range"] is True
    assert diag["H0_threshold_km_s_Mpc_where_minimum_equals_envelope"] < 50.0


def test_blueprint_is_not_declared_falsification():
    row = mod.gaussian_neff_compatibility_envelope("ACT+BBN", 2.89, 0.11)
    diag = mod.blueprint_minimum_diagnostic(row.omega_extra_h2_upper)
    assert "does not falsify RLL" in diag["forbidden_inference"]


def test_hotqcd_pressure_fit_130_mev_close_to_table():
    q = mod.hotqcd_thermodynamics(130.0)
    assert abs(q.pressure_over_T4 - 0.439) < 0.01


def test_hotqcd_trace_identity_at_130_mev_close_to_table():
    q = mod.hotqcd_thermodynamics(130.0)
    assert abs(q.trace_over_T4 - 1.01) < 0.03


def test_hotqcd_energy_entropy_identities():
    q = mod.hotqcd_thermodynamics(155.0)
    assert math.isclose(q.energy_over_T4, q.trace_over_T4 + 3.0 * q.pressure_over_T4, rel_tol=1e-12)
    assert math.isclose(q.entropy_over_T3, q.energy_over_T4 + q.pressure_over_T4, rel_tol=1e-12)


def test_hotqcd_effective_dof_positive():
    for t in (130.0, 155.0, 200.0, 300.0, 400.0):
        q = mod.hotqcd_thermodynamics(t)
        assert q.g_rho_qcd > 0.0
        assert q.g_s_qcd > 0.0


def test_hotqcd_softest_region_is_softer_than_400_mev():
    q150 = mod.hotqcd_thermodynamics(150.0)
    q400 = mod.hotqcd_thermodynamics(400.0)
    assert q150.cs2 < q400.cs2
    assert 0.13 < q150.cs2 < 0.17
    assert 0.28 < q400.cs2 < 0.32


def test_hotqcd_domain_guard():
    import pytest
    with pytest.raises(ValueError):
        mod.hotqcd_pressure_over_t4(99.0)
    with pytest.raises(ValueError):
        mod.hotqcd_pressure_over_t4(401.0)


def test_hubble_requires_total_g_rho():
    import pytest
    with pytest.raises(ValueError):
        mod.radiation_dominated_hubble_s_inv(150.0, 0.0)
    assert mod.radiation_dominated_hubble_s_inv(150.0, 50.0) > 0.0


def test_full_rll_gate_remains_token_vazio():
    gates = mod.build_attention_gates()
    assert gates["full_RLL_primordial_verdict"] == "TOKEN_VAZIO"
    assert gates["claim_allowed"] is False


def test_unresolved_sign_and_perturbation_physics_are_explicit():
    gates = mod.build_attention_gates()
    assert gates["Omega_B0_sign_authority"] == "TOKEN_VAZIO"
    assert gates["Omega_P0_sign_authority"] == "TOKEN_VAZIO"
    assert gates["Omega_B0_P0_perturbation_physics"] == "TOKEN_VAZIO"


def test_receipt_forbids_censorship_inference_from_missing_material():
    class Args:
        sigma_multiplier = 1.96
    receipt = mod.build_receipt(Args())
    assert any("censorship" in x.lower() for x in receipt["forbidden_inferences"])


def test_hotqcd_machine_input_matches_code_constants():
    import json
    path = Path(__file__).resolve().parents[1] / "data" / "inputs" / "qcd_primordial" / "hotqcd_2014_eos_fit.v1.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    assert payload["formula"]["Tc_MeV"] == mod.HOTQCD_TC_MEV
    assert payload["coefficients"] == mod.HOTQCD
    assert payload["superseded_provenance"]["active_use"] is False


def test_attention_ledger_never_promotes_unverified_censorship():
    import json
    path = Path(__file__).resolve().parents[1] / "data" / "inputs" / "qcd_primordial" / "rll_primordial_attention_ledger.v1.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    row = next(x for x in payload["entries"] if x["id"] == "CENSORSHIP_CLASSIFICATION")
    assert row["epistemic_status"] == "NO_DOCUMENTED_INSTANCE_IN_CURRENT_SURVEY"
    assert payload["claim_allowed"] is False


def test_evidence_registry_preserves_blueprint_boundary():
    import json
    path = Path(__file__).resolve().parents[1] / "data" / "inputs" / "qcd_primordial" / "rll_primordial_evidence_registry.v2.json"
    payload = json.loads(path.read_text(encoding="utf-8"))
    row = next(x for x in payload["sources"] if x["source_id"] == "RMR_BLUEPRINT_METADATA")
    assert row["kind"] == "BLUEPRINT_NOT_AUTHORITY"
    assert "not" in row["forbidden_inference"].lower()


def test_committed_receipt_matches_generator():
    import json
    class Args:
        sigma_multiplier = 1.96
    expected = mod.build_receipt(Args())
    path = Path(__file__).resolve().parents[1] / "data" / "results" / "rll_primordial_assurance_v2.receipt.json"
    actual = json.loads(path.read_text(encoding="utf-8"))
    assert actual == expected
