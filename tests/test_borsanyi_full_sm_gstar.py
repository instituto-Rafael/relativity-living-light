from __future__ import annotations

import importlib.util
import math
import sys
from pathlib import Path

MODULE_PATH = Path(__file__).resolve().parents[1] / "tools" / "borsanyi_full_sm_gstar.py"
SPEC = importlib.util.spec_from_file_location("borsanyi_full_sm_gstar", MODULE_PATH)
assert SPEC and SPEC.loader
mod = importlib.util.module_from_spec(SPEC)
sys.modules[SPEC.name] = mod
SPEC.loader.exec_module(mod)


def test_source_table_has_exact_27_knots_and_expected_domain():
    payload = mod.load_table()
    assert len(payload["rows"]) == 27
    assert payload["rows"][0]["log10_T_MeV"] == 0.0
    assert payload["rows"][-1]["log10_T_MeV"] == 5.45


def test_exact_source_knots_are_not_modified():
    payload = mod.load_table()
    for row in payload["rows"]:
        point = mod.evaluate(10.0 ** row["log10_T_MeV"], payload)
        assert point.g_rho == row["g_rho"]
        assert point.g_rho_over_g_s == row["g_rho_over_g_s"]
        assert point.g_s == row["g_rho"] / row["g_rho_over_g_s"]
        assert point.interpolation == "EXACT_SOURCE_KNOT"


def test_qcd_interval_is_inside_full_sm_source_domain():
    for temperature in (130.0, 154.0, 200.0, 400.0):
        point = mod.evaluate(temperature)
        assert point.g_rho > 0.0
        assert point.g_s > 0.0
        assert point.g_rho_over_g_s > 0.0


def test_representative_qcd_values_are_reproducible():
    p130 = mod.evaluate(130.0)
    p154 = mod.evaluate(154.0)
    p200 = mod.evaluate(200.0)
    p400 = mod.evaluate(400.0)
    assert math.isclose(p130.g_rho, 21.22731330345283, rel_tol=0.0, abs_tol=1e-11)
    assert math.isclose(p154.g_rho, 27.65033376929897, rel_tol=0.0, abs_tol=1e-11)
    assert math.isclose(p200.g_rho, 40.839117970133714, rel_tol=0.0, abs_tol=1e-11)
    assert math.isclose(p400.g_rho, 57.928433990390545, rel_tol=0.0, abs_tol=1e-11)


def test_gs_identity_is_preserved_after_interpolation():
    for temperature in (2.0, 17.0, 130.0, 177.0, 400.0, 1000.0, 100000.0):
        point = mod.evaluate(temperature)
        assert math.isclose(point.g_s * point.g_rho_over_g_s, point.g_rho, rel_tol=1e-14)


def test_extrapolation_fails_closed():
    for temperature in (0.99, 10.0**5.451):
        try:
            mod.evaluate(temperature)
        except ValueError as exc:
            assert "outside Borsanyi Table S3 domain" in str(exc)
        else:
            raise AssertionError("extrapolation must fail closed")


def test_nonphysical_temperatures_fail_closed():
    for temperature in (0.0, -1.0, float("inf"), float("nan")):
        try:
            mod.evaluate(temperature)
        except ValueError:
            pass
        else:
            raise AssertionError("nonphysical temperature must fail closed")


def test_receipt_keeps_claim_boundary_and_source_identity():
    receipt = mod.build_receipt([130.0, 154.0, 400.0])
    assert receipt["status"] == "MATERIALIZED_BORSANYI_TABLE_S3"
    assert receipt["claim_allowed"] is False
    assert receipt["publication_effect"] == "NONE"
    assert receipt["table_knots"] == 27
    assert receipt["source_table"].endswith("Table S3")
