import importlib.util
import sys
from pathlib import Path

import pytest


ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "data/pipelines/structure_d/dark_dimension_benchmark.py"


def load_module():
    name = "dark_dimension_benchmark_v1"
    spec = importlib.util.spec_from_file_location(name, MODULE_PATH)
    assert spec and spec.loader
    module = importlib.util.module_from_spec(spec)
    sys.modules[name] = module
    spec.loader.exec_module(module)
    return module


def test_effective_4d_asymptotic_limit():
    mod = load_module()
    result = mod.classify_dimension_regime(100.0, 1.0)
    assert result.state == "EFFECTIVE_4D_ASYMPTOTIC"
    assert result.chi == 100.0
    assert result.claim_allowed is False


def test_five_d_sensitive_asymptotic_limit():
    mod = load_module()
    result = mod.classify_dimension_regime(0.01, 1.0)
    assert result.state == "FIVE_D_SENSITIVE_ASYMPTOTIC"
    assert result.chi == 0.01
    assert result.claim_allowed is False


def test_order_one_crossover_remains_token_vazio():
    mod = load_module()
    result = mod.classify_dimension_regime(1.0, 1.0)
    assert result.state == "CROSSOVER_TOKEN_VAZIO"
    assert "full model-specific" in result.interpretation


def test_invalid_lengths_fail_closed():
    mod = load_module()
    with pytest.raises(ValueError):
        mod.classify_dimension_regime(0.0, 1.0)
    with pytest.raises(ValueError):
        mod.classify_dimension_regime(1.0, -1.0)


def test_separation_factor_cannot_fake_sharp_transition():
    mod = load_module()
    with pytest.raises(ValueError):
        mod.classify_dimension_regime(1.0, 1.0, separation_factor=1.0)


def test_gl_mass_ratio_is_dimensionless_only():
    mod = load_module()
    assert mod.gregory_laflamme_mass_ratio(2.0, 4.0) == 0.5
    with pytest.raises(ValueError):
        mod.gregory_laflamme_mass_ratio(1.0, 0.0)


def test_receipt_keeps_likelihood_and_combined_model_blocked():
    mod = load_module()
    receipt = mod.build_benchmark_receipt(r_h_m=100.0, compact_radius_m=1.0)
    assert receipt["likelihood_parity"] == "TOKEN_VAZIO_NOT_EXECUTED"
    assert receipt["desi_dr2_sn_fit"] == "TOKEN_VAZIO_NOT_EXECUTED"
    assert receipt["rll_plus_dark_dimension"] == "BLOCKED_UNTIL_G5_PARITY"
    assert receipt["claim_allowed"] is False
