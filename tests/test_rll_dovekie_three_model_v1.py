from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "products/rll-evidence-runner"
sys.path.insert(0, str(PRODUCT / "src"))

from rll_evidence.dovekie_fit_three_model import (
    CPL,
    LCDM,
    RLL,
    distance_modulus,
    e2,
    fit_model,
    prepare_data,
    profiled_likelihood,
)


def synthetic_data():
    z_hd = np.array([0.02, 0.04, 0.08, 0.15, 0.3, 0.5, 0.8, 1.0], dtype=float)
    z_hel = z_hd + 0.0002
    precision = np.eye(z_hd.size) / (0.05**2)
    empty = prepare_data(
        z_hd,
        z_hel,
        np.zeros(z_hd.size),
        np.full(z_hd.size, 0.05),
        precision,
        integration_points=512,
    )
    model_mu = distance_modulus(empty, LCDM, [0.3])
    return prepare_data(
        z_hd,
        z_hel,
        model_mu + 0.37,
        np.full(z_hd.size, 0.05),
        precision,
        integration_points=512,
    )


def test_flat_closure_at_zero_for_all_models() -> None:
    z = np.array([0.0])
    assert abs(float(e2(LCDM, z, [0.3])[0]) - 1.0) < 1e-12
    assert abs(float(e2(CPL, z, [0.3, -1.0, 0.0])[0]) - 1.0) < 1e-12
    assert abs(float(e2(RLL, z, [0.3, 0.02, 1.0, 0.3])[0]) - 1.0) < 1e-12


def test_cpl_nests_lcdm() -> None:
    z = np.array([0.0, 0.1, 0.5, 1.0, 2.0])
    np.testing.assert_allclose(
        e2(CPL, z, [0.3, -1.0, 0.0]),
        e2(LCDM, z, [0.3]),
        rtol=0.0,
        atol=1e-12,
    )


def test_profiled_offset_removes_h0_like_absolute_scale() -> None:
    data = synthetic_data()
    chi2, offset, _ = profiled_likelihood(data, LCDM, [0.3])
    assert chi2 < 1e-8
    assert abs(offset - 0.37) < 1e-7


def test_lcdm_multiseed_fit_recovers_synthetic_shape() -> None:
    data = synthetic_data()
    result = fit_model(data, LCDM, [11, 23], maxiter=80, ftol=1e-12)
    assert result["status"] == "PASS"
    assert abs(result["best"]["Omega_m"] - 0.3) < 1e-3
    assert result["best"]["chi2"] < 1e-6


def test_precision_semantics_are_not_diagonal_error_proxy() -> None:
    data = synthetic_data()
    assert data.precision.shape == (data.n, data.n)
    assert data.one_precision_one > 0.0
