from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MODULE_PATH = ROOT / "scripts" / "rll_sn_identifiability_diagnostics.py"
spec = importlib.util.spec_from_file_location("rll_sn_identifiability_diagnostics", MODULE_PATH)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_boundary_hits_detects_cpl_wa_lower_bound() -> None:
    spec = module.dovekie_three.MODEL_SPECS[module.dovekie_three.CPL]
    hits = module.boundary_hits(
        {"Omega_m": 0.41, "w0": -0.79, "wa": -3.0},
        tuple(spec["parameter_names"]),
        tuple(spec["bounds"]),
    )
    assert any(hit["parameter"] == "wa" and hit["side"] == "lower" for hit in hits)


def test_rll_null_nested_outside_support_is_token_vazio() -> None:
    model = module.dovekie_three.RLL
    baseline = module.dovekie_three.LCDM
    result = {
        "models": {
            baseline: {"best": {"chi2": 100.0}},
            model: {
                "best": {
                    "chi2": 100.0,
                    "Omega_m": 0.33,
                    "Omega_s0": 0.10,
                    "z_t": 4.2,
                    "w_t": 0.2,
                },
                "stability": {"chi2_span": 1.0e-7},
                "runs": [
                    {
                        "parameters": {
                            "Omega_m": 0.33,
                            "Omega_s0": 0.0,
                            "z_t": 1.0,
                            "w_t": 0.3,
                        }
                    },
                    {
                        "parameters": {
                            "Omega_m": 0.33,
                            "Omega_s0": 0.10,
                            "z_t": 4.2,
                            "w_t": 0.2,
                        }
                    },
                ],
            },
        }
    }
    diagnostic = module.model_diagnostic(
        result,
        model,
        module.dovekie_three.MODEL_SPECS[model],
        z_max=1.15,
        baseline_model=baseline,
    )
    assert diagnostic["rll_identifiability"]["transition_outside_observed_support"] is True
    assert diagnostic["rll_identifiability"]["delta_chi2_near_zero"] is True
    assert "TOKEN_VAZIO_RLL_SN_ONLY_PARAMETER_IDENTIFIABILITY" in diagnostic["token_vazio"]


def test_nonboundary_cpl_is_not_falsely_flagged() -> None:
    model = module.dovekie_three.CPL
    baseline = module.dovekie_three.LCDM
    result = {
        "models": {
            baseline: {"best": {"chi2": 100.0}},
            model: {
                "best": {"chi2": 98.0, "Omega_m": 0.31, "w0": -0.9, "wa": -0.2},
                "stability": {"chi2_span": 0.001},
                "runs": [
                    {"parameters": {"Omega_m": 0.31, "w0": -0.9, "wa": -0.2}},
                    {"parameters": {"Omega_m": 0.32, "w0": -0.91, "wa": -0.18}},
                ],
            },
        }
    }
    diagnostic = module.model_diagnostic(
        result,
        model,
        module.dovekie_three.MODEL_SPECS[model],
        z_max=1.15,
        baseline_model=baseline,
    )
    assert not diagnostic["boundary_hits"]
    assert not any("BOUNDARY" in token for token in diagnostic["token_vazio"])
