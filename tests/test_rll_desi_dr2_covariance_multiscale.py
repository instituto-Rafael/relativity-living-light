import importlib.util
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "scripts" / "rll_desi_dr2_covariance_multiscale.py"

spec = importlib.util.spec_from_file_location("rll_desi_dr2_covariance_multiscale", SCRIPT)
assert spec is not None and spec.loader is not None
mod = importlib.util.module_from_spec(spec)
spec.loader.exec_module(mod)


def _out():
    return mod.evaluate()


def test_full_covariance_reproduces_committed_rll_g4_chi2():
    out = _out()
    rll = out["models"]["RLL"]
    assert rll["chi2_reproduction_match"] is True
    assert math.isclose(rll["chi2_from_whitened"], 11.77025905554635, rel_tol=1e-11, abs_tol=1e-11)


def test_full_covariance_reproduces_committed_lcdm_g4_chi2():
    out = _out()
    lcdm = out["models"]["LCDM"]
    assert lcdm["chi2_reproduction_match"] is True
    assert math.isclose(lcdm["chi2_from_whitened"], 11.770259180500712, rel_tol=1e-11, abs_tol=1e-11)


def test_covariance_blocks_close():
    out = _out()
    for model in ("LCDM", "RLL"):
        m = out["models"][model]
        b = m["block_diagnostics"]
        assert b["covariance_is_block_diagonal_observed"] is True
        assert b["cross_block_max_abs_covariance"] == 0.0
        assert b["block_closure_pass"] is True
        assert math.isclose(m["chi2_from_whitened"], b["block_chi2_sum"], rel_tol=1e-12, abs_tol=1e-12)


def test_fibonacci_windows_are_diagnostic_not_weights():
    out = _out()
    for model in ("LCDM", "RLL"):
        multi = out["models"][model]["fibonacci_multiscale"]
        assert multi["weights_likelihood"] is False
        assert [row["size"] for row in multi["scales"]] == [2, 3, 5, 8, 13]


def test_geometry_does_not_replace_covariance():
    out = _out()
    assert out["covariance"]["role"] == "LIKELIHOOD_AND_WHITENING_AUTHORITY"
    for key in ("sqrt3_over_2", "poincare", "venturi", "calendar"):
        assert out["geometry_bindings"][key]["changes_likelihood"] is False


def test_null_submanifold_and_claim_gate():
    out = _out()
    assert out["cross_model"]["rll_on_lcdm_null_submanifold"] is True
    assert out["claim_allowed"] is False
