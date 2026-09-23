import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
RUNNER = ROOT / "tools/run_omega_g_cosmology_tournament.py"

spec = importlib.util.spec_from_file_location("omega_g_tournament", RUNNER)
assert spec and spec.loader
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def test_contract_registry_valid():
    result = mod.validate_contract_and_registry()
    assert result["valid"], result["errors"]
    assert result["claim_allowed"] is False


def test_required_background_models_present():
    contract = mod._read_yaml(mod.CONTRACT)
    declared = tuple(contract["models"]["baseline"]) + tuple(contract["models"]["candidate"])
    for model in ("LCDM", "wCDM", "CPL", "RLL"):
        assert model in declared


def test_required_background_datasets_present():
    contract = mod._read_yaml(mod.CONTRACT)
    blocks = contract["datasets"]["G4_background"]
    assert "cosmic_chronometers_Hz" in blocks
    assert "DESI_DR2_BAO" in blocks
    assert "PantheonPlus_SH0ES" in blocks


def test_null_binding_exact_parity():
    result = mod.null_parity()
    assert result["state"] == "PASS"
    assert result["global_max_abs_delta_E2"] == 0.0
    assert all(row["pass"] for row in result["models"])


def test_no_active_binding_without_mechanism():
    registry = mod._read_yaml(mod.REGISTRY)
    assert all(item["state"] != "APPROVED_FOR_TEST" for item in registry["bindings"])


def test_growth_and_cmb_not_silently_bound_at_background_level():
    contract = mod._read_yaml(mod.CONTRACT)
    pert = contract["datasets"]["perturbation_level"]
    assert pert["fsigma8"]["status"].startswith("BLOCKED")
    assert pert["CMB_full_or_compressed"]["status"].startswith("BLOCKED")


def test_nonfinite_diagnostics_are_preserved_as_null_with_path():
    seen = []
    value = mod._sanitize_for_json(
        {"ok": 1.0, "bad": float("inf"), "nan": float("nan")},
        path="report",
        nonfinite=seen,
    )
    assert value["ok"] == 1.0
    assert value["bad"] is None
    assert value["nan"] is None
    assert {item["path"] for item in seen} == {"report.bad", "report.nan"}
    assert {item["value"] for item in seen} == {"inf", "nan"}
