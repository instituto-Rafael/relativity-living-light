"""Source-only invariants: H0/r_d CAMB/NumPy 1.x compatibility envelope."""
from pathlib import Path

WORKFLOW = Path(".github/workflows/h0-rd-ablation.yml")


def test_ablation_pandas_numpy_astropy_compatibility_is_explicit():
    src = WORKFLOW.read_text(encoding="utf-8")
    for constraint in (
        '"numpy>=1.26,<2"',
        '"pandas>=2,<3"',
        '"astropy>=5.3,<8"',
        '"contourpy>=1.0,<1.4"',
        '"camb==1.6.6"',
        "python -m pip check",
    ):
        assert constraint in src, f"Missing compatibility envelope: {constraint}"


def test_numerical_falsifiers_and_claim_boundary_remain_active():
    src = WORKFLOW.read_text(encoding="utf-8")
    assert "tests/test_h0_rd_ablation_v1.py" in src
    assert "tests/test_rll_h0_rd_direct_boltzmann_probe_v1.py" in src
    assert "python -m pytest -q" in src
    assert "python tools/run_h0_rd_ablation_v1.py" in src
    assert "python tools/rll_h0_rd_direct_boltzmann_probe_v1.py" in src
    assert "H0/r_d matrix execution is sensitivity-only" in src
    assert "|| true" not in src
