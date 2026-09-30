from __future__ import annotations

import math

import numpy as np
import pytest

from data.pipelines.structure_d import joint_real_likelihood as legacy
from data.pipelines.structure_d import joint_real_likelihood_flat as flat
from tools import rll_cosmology_flat_closure_preflight as preflight


def _sample(model: str, fraction: float) -> np.ndarray:
    return np.asarray(
        [lo + fraction * (hi - lo) for lo, hi in flat.FLAT_MODEL_BOUNDS[model]],
        dtype=float,
    )


def test_flat_successor_removes_Omega_Lambda_from_free_parameter_vectors() -> None:
    for model in flat.MODEL_ORDER:
        assert "OL" not in flat.FLAT_MODEL_PARAM_NAMES[model]


def test_flat_successor_enforces_e0_one_across_bounds() -> None:
    for model in flat.MODEL_ORDER:
        for fraction in (0.0, 0.5, 1.0):
            vector = _sample(model, fraction)
            assert flat.derived_omega_lambda(model, vector) > 0.0
            assert math.isclose(flat.e0_squared(model, vector), 1.0, rel_tol=0.0, abs_tol=1.0e-12)


def test_h_of_zero_is_h0_after_flat_expansion() -> None:
    for model in flat.MODEL_ORDER:
        vector = _sample(model, 0.5)
        expanded = flat.expand_flat_vector(model, vector)
        e2_fn, params, h0, *_ = legacy._model_runtime(model, expanded)
        hz0 = float(legacy.hz_from_e2(0.0, e2_fn, params))
        assert math.isclose(hz0, h0, rel_tol=0.0, abs_tol=1.0e-10)


def test_rll_closure_includes_Omega_s0_in_present_day_budget() -> None:
    vector = _sample(flat.MODEL_RLL, 0.5)
    values = dict(zip(flat.FLAT_MODEL_PARAM_NAMES[flat.MODEL_RLL], vector))
    expected = 1.0 - legacy.ORAD - values["Om"] - values["Os0"]
    assert math.isclose(flat.derived_omega_lambda(flat.MODEL_RLL, vector), expected, rel_tol=0.0, abs_tol=1.0e-12)


def test_flat_successor_refuses_historical_canonical_output_stem() -> None:
    with pytest.raises(ValueError):
        flat.run_joint_likelihood_flat(output_stem="joint_real_likelihood")


def test_preflight_resolves_closure_but_keeps_growth_and_cmb_fail_closed() -> None:
    report = preflight.build_report()
    assert report["status"] == "CLOSURE_READY_OTHER_GATES_BLOCKED"
    assert report["closure_claim_allowed"] is True
    assert report["claim_allowed"] is False
    assert report["model_selection_claim_allowed"] is False
    assert report["historical_results_mutated"] is False
    assert report["checks"]["growth_likelihood"]["pass"] is False
    assert report["checks"]["cmb_acoustic_scale"]["pass"] is False
