from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "tools/run_h0_rd_ablation_v1.py"
spec = importlib.util.spec_from_file_location("h0_rd_ablation", SCRIPT)
assert spec and spec.loader
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)


def test_matrix_has_exact_six_cells_and_valid_bounds():
    matrix = module.load_matrix()
    assert len(matrix["runs"]) == 6
    assert {row["H0_policy"] for row in matrix["runs"]} == {
        "broad_free",
        "planck_prior",
        "shoes_local_prior",
    }
    assert {row["rd_policy"] for row in matrix["runs"]} == {"fixed_for_all", "derived_for_all"}
    assert all(module.parse_h0_bounds(row["H0_bounds"]) == (50.0, 90.0) for row in matrix["runs"])


def test_planck_conditioning_is_not_called_independent_likelihood():
    matrix = module.load_matrix()
    planck = next(row for row in matrix["runs"] if row["H0_policy"] == "planck_prior")
    role = module.policy_role(planck)
    assert role["independent_external_likelihood"] is False
    assert role["information_criteria_authoritative"] is False
    assert "correlated" in role["role"]


def test_broad_policy_adds_no_h0_penalty():
    matrix = module.load_matrix()
    broad = next(row for row in matrix["runs"] if row["H0_policy"] == "broad_free")
    assert module.h0_penalty(50.0, broad) == 0.0
    assert module.h0_penalty(90.0, broad) == 0.0


def test_declared_gaussian_penalty_is_centered_on_mean():
    matrix = module.load_matrix()
    shoes = next(row for row in matrix["runs"] if row["H0_policy"] == "shoes_local_prior")
    mean = float(shoes["H0_prior_mean"])
    sigma = float(shoes["H0_prior_sigma"])
    assert module.h0_penalty(mean, shoes) == 0.0
    assert abs(module.h0_penalty(mean + sigma, shoes) - 1.0) < 1e-12


def test_fixed_rd_context_restores_original_function():
    original = module.joint.rd_drag_mpc
    with module.rd_policy_context("fixed_for_all", 147.78):
        assert module.joint.rd_drag_mpc(67.4, 0.315, 0.0224) == 147.78
    assert module.joint.rd_drag_mpc is original
