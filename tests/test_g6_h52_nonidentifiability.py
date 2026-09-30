from __future__ import annotations

import importlib.util
import json
import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "tools/run_g6_h52_nonidentifiability.py"
CONTRACT_PATH = ROOT / "data/contracts/rll_g6_h52_nonidentifiability.v1.json"


def load_module():
    spec = importlib.util.spec_from_file_location("rll_h52_unit", MODULE_PATH)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[spec.name] = mod
    spec.loader.exec_module(mod)
    return mod


class FakeG4:
    @staticmethod
    def parameter_names(model: str):
        assert model == "RLL"
        return ("H0", "Omega_m", "omega_b_h2", "Omega_s0", "z_t", "w_t")


def test_contract_is_fail_closed_and_preregistered():
    contract = json.loads(CONTRACT_PATH.read_text(encoding="utf-8"))
    assert contract["schema"] == "rll.g6_h52_nonidentifiability.v1"
    assert contract["state"] == "PREREGISTERED_EXECUTABLE_FAIL_CLOSED"
    assert contract["claim_allowed"] is False
    assert contract["mcmc"]["convergence"]["max_split_Rhat"] == 1.10
    assert contract["fixed_shape_diagnostic_arm"]["fixed"] == {"z_t": 1.0, "w_t": 0.30}
    assert contract["mcmc"]["seeds"] == [1103, 2207, 3301, 4409]


def test_projected_vector_restores_exact_rll_order():
    mod = load_module()
    vector = mod._pack_full(
        FakeG4(),
        ("H0", "Omega_m", "omega_b_h2", "Omega_s0"),
        np.asarray([67.0, 0.31, 0.0224, 0.001]),
        {"z_t": 1.0, "w_t": 0.30},
    )
    assert np.allclose(vector, [67.0, 0.31, 0.0224, 0.001, 1.0, 0.30])


def test_projected_vector_rejects_missing_shape_parameter():
    mod = load_module()
    try:
        mod._pack_full(
            FakeG4(),
            ("H0", "Omega_m", "omega_b_h2", "Omega_s0"),
            np.asarray([67.0, 0.31, 0.0224, 0.001]),
            {"z_t": 1.0},
        )
    except ValueError as exc:
        assert "w_t" in str(exc)
    else:
        raise AssertionError("missing fixed parameter must fail closed")


def test_h52_classification_is_predeclared_and_non_promotional():
    mod = load_module()
    t = 1.10
    assert mod._classify(1.20, 1.05, t) == "SUPPORTED_LIMITED_H52_NONIDENTIFIABILITY"
    assert mod._classify(1.05, 1.04, t) == "LONGER_CHAIN_SUFFICIENT_H52_NOT_REQUIRED_FOR_CONVERGENCE"
    assert mod._classify(1.20, 1.15, t) == "H52_NOT_RESOLVED_BOTH_ARMS_NONCONVERGED"
    assert mod._classify(1.05, 1.20, t) == "H52_ANOMALOUS_FIXED_SHAPE_WORSE"


def test_excess_over_one_never_invents_negative_uncertainty():
    mod = load_module()
    assert mod._excess_over_one(0.99) == 0.0
    assert mod._excess_over_one(1.0) == 0.0
    assert abs(mod._excess_over_one(1.27) - 0.27) < 1e-12
