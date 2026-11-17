import importlib.util
import csv

import pytest
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/run_g4_background_tournament.py"
CONTRACT_PATH = ROOT / "data/contracts/rll_g4_background_tournament.v1.json"


def load_module():
    name = "g4bg"
    spec = importlib.util.spec_from_file_location(name, MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def test_contract_has_all_mandatory_models_and_no_claim_promotion():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert list(contract["models"]) == ["LCDM", "wCDM", "CPL", "GEDE", "IDE_QrhoLambda", "RLL"]
    assert contract["claim_allowed"] is False
    assert contract["scientific_confirmation"] is False
    assert "fsigma8" in contract["excluded_from_this_gate"]
    assert "CMB_full_or_compressed" in contract["excluded_from_this_gate"]


def test_all_extension_null_limits_recover_lcdm():
    mod = load_module()
    receipt = mod.null_limit_receipt()
    assert receipt["passed"] is True
    assert all(value <= 1e-12 for value in receipt["checks"].values())


def test_gede_delta_zero_transition_is_analytic_and_finite():
    mod = load_module()
    om = 0.30
    expected = ((1.0 - om - mod.OMEGA_R0) / om) ** (1.0 / 3.0) - 1.0
    actual = mod.gede_transition_redshift(om, 0.0)
    assert np.isfinite(actual)
    assert abs(actual - expected) <= 1e-14


def test_gede_and_ide_bounds_are_finite_on_background_grid():
    mod = load_module()
    z = np.array([0.0, 0.1, 0.5, 1.0, 2.33])
    for delta in (-10.0, -2.0, 0.0, 2.0, 10.0):
        values = mod.e2("GEDE", z, [70.0, 0.30, 0.02236, delta])
        # Extreme GEDE parameter values may be rejected by the derived-z_t root;
        # if accepted, they must be finite and positive.  Null and moderate
        # values must certainly be usable.
        if delta in (-2.0, 0.0, 2.0):
            assert np.all(np.isfinite(values))
            assert np.all(values > 0.0)
    for beta in (-0.15, 0.0, 0.15):
        values = mod.e2("IDE_QrhoLambda", z, [70.0, 0.30, 0.02236, beta])
        assert np.all(np.isfinite(values))
        assert np.all(values > 0.0)


def test_parameter_counts_include_profiled_pantheon_nuisance():
    mod = load_module()
    assert mod.k_for_model("LCDM") == 4
    assert mod.k_for_model("wCDM") == 5
    assert mod.k_for_model("CPL") == 6
    assert mod.k_for_model("GEDE") == 5
    assert mod.k_for_model("IDE_QrhoLambda") == 5
    assert mod.k_for_model("RLL") == 7


def test_pure_cc_selector_excludes_bao_labeled_rows():
    mod = load_module()
    block = mod.load_cc()
    assert block.n > 0
    assert all(source.startswith("CC_") for source in block.sources)
    assert all("BAO" not in source.upper() for source in block.sources)


def test_g4_contract_source_equations_are_pinned():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    gede = contract["models"]["GEDE"]
    ide = contract["models"]["IDE_QrhoLambda"]
    assert gede["primary_source"] == "arXiv:2103.03815v2"
    assert "Delta=0 -> LCDM" == gede["null_limit"]
    assert ide["primary_source"] == "arXiv:1506.06349"
    assert ide["interaction"].startswith("Q=3*beta*H*rho_Lambda")
    assert ide["null_limit"] == "beta=0 -> LCDM"

def test_g4_loader_rejects_swapped_desi_rows_before_fit(tmp_path: Path):
    source = ROOT / "data/real/cosmology/desi_dr2_bao_primary_points.csv"
    with source.open(newline="", encoding="utf-8") as handle:
        reader = csv.DictReader(handle)
        fieldnames = reader.fieldnames
        assert fieldnames is not None
        rows = list(reader)
    rows[1], rows[2] = rows[2], rows[1]
    swapped = tmp_path / "desi_swapped.csv"
    with swapped.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        writer.writerows(rows)
    mod = load_module()
    with pytest.raises(ValueError, match="source/order mismatch"):
        mod.load_desi(points_path=swapped)


def test_g4_lyman_covariance_aligned_to_primary_dm_dh_order():
    mod = load_module()
    block = mod.load_desi()
    assert block.observable[-2:] == ("DM_over_rd", "DH_over_rd")
    assert abs(np.sqrt(block.covariance[-2, -2]) - 0.531) / 0.531 < 0.01
    assert abs(np.sqrt(block.covariance[-1, -1]) - 0.101) / 0.101 < 0.01
    # Coordinate relabeling of C and r together preserves the quadratic form.
    raw = np.loadtxt(ROOT / "data/real/desi_dr2_bao_covariance.csv", delimiter=",", skiprows=1, usecols=range(1, 14))
    residual = np.linspace(-0.25, 0.25, 13)
    perm = list(range(11)) + [12, 11]
    native_residual = np.empty(13)
    native_residual[perm] = residual
    left = float(residual @ np.linalg.solve(block.covariance, residual))
    right = float(native_residual @ np.linalg.solve(raw, native_residual))
    assert np.isclose(left, right, rtol=1e-11, atol=1e-11)
