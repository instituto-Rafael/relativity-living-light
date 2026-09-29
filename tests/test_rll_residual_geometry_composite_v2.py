import importlib.util
import math
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "scripts" / "rll_residual_geometry_composite_v2.py"

spec = importlib.util.spec_from_file_location("composite_v2", PATH)
assert spec and spec.loader
m = importlib.util.module_from_spec(spec)
spec.loader.exec_module(m)


def test_classical_fibonacci_sizes() -> None:
    assert m.classical_fibonacci_sizes(13) == [2, 3, 5, 8, 13]


def test_rafael_affine_sizes_and_matrix_step() -> None:
    assert m.rafael_affine_sizes(13) == [2, 4, 7, 12]
    # [R_1,R_0,1]=[2,1,1] -> R_2=4 -> R_3=7
    assert m.rafael_affine_step((2, 1, 1)) == (4, 2, 1)
    assert m.rafael_affine_step((4, 2, 1)) == (7, 4, 1)


def test_poincare_nd_lift_is_inside_ball() -> None:
    for xs in ([1.0], [1.0, 2.0], [10.0] * 7, [0.0] * 8):
        out = m.poincare_lift(list(xs))
        assert out["inside_unit_ball"] is True
        assert 0.0 <= out["radius"] < 1.0
        assert math.isfinite(out["origin_distance_curvature_minus_1"])


def test_quadratic_descriptor_recovers_known_parabola() -> None:
    xs = [2.0*t*t + 3.0*t + 5.0 for t in range(5)]
    q = m.quadratic_descriptor(xs)
    assert q["state"] == "MEASURED_NUMERIC_DIAGNOSTIC"
    c = q["coefficients"]
    assert math.isclose(c["a"], 2.0, abs_tol=1e-10)
    assert math.isclose(c["b"], 3.0, abs_tol=1e-10)
    assert math.isclose(c["c"], 5.0, abs_tol=1e-10)
    assert math.isclose(q["discriminant"], 9.0 - 40.0, abs_tol=1e-10)


def test_composite_preserves_frozen_likelihood() -> None:
    out = m.evaluate()
    assert out["claim_allowed"] is False
    assert out["likelihood_mutated"] is False
    for name in ("LCDM", "RLL"):
        row = out["diagnostics"][name]
        assert row["chi2_identity_pass"] is True
        assert math.isclose(
            row["chi2_input"],
            row["chi2_reconstructed"],
            rel_tol=1e-12,
            abs_tol=1e-12,
        )
    assert out["typed_adapters"]["venturi"]["state"] == "TOKEN_VAZIO_FLUID_BINDING"
    assert out["typed_adapters"]["calendar"]["state"] == "TOKEN_VAZIO_TEMPORAL_BINDING"
    assert "SQRT3_OVER_2 != SIGMA" in out["hard_boundaries"]
