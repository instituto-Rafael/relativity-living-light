from __future__ import annotations

import sys
import tempfile
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "products/rll-evidence-runner"
sys.path.insert(0, str(PRODUCT / "src"))

from rll_evidence.dovekie_cpl_wa_profile import (
    asymptotic_profiled_likelihood,
    classify_profile,
    fit_asymptotic_limit,
    fit_fixed_wa,
)
from rll_evidence.dovekie_fit_three_model import LCDM as D_LCDM
from rll_evidence.dovekie_fit_three_model import distance_modulus as dov_distance_modulus
from rll_evidence.dovekie_fit_three_model import prepare_data as dov_prepare_data
from rll_evidence.pantheon_fit_three_model import LCDM as P_LCDM
from rll_evidence.pantheon_fit_three_model import distance_modulus as pantheon_distance_modulus
from rll_evidence.pantheon_fit_three_model import prepare_data as pantheon_prepare_data
from rll_evidence.pantheon_hubbleflow_profiled import (
    H0_REFERENCE,
    LOCAL_SPECS,
    fit_model as fit_pantheon_hf,
    load_hubbleflow_data,
)


def _pantheon_files(root: Path) -> tuple[Path, Path]:
    z_hd = np.array([0.005, 0.007, 0.02, 0.04, 0.08, 0.15, 0.3, 0.5, 0.8, 1.1])
    z_hel = z_hd + 0.0002
    calibrator = np.array([True, True] + [False] * 8)
    ceph = np.array([31.0, 32.0] + [-9.0] * 8)
    covariance = np.diag(np.full(10, 0.03**2))
    empty = pantheon_prepare_data(
        z_hd, z_hel, np.zeros(10), ceph, calibrator, covariance, integration_points=512
    )
    predicted = pantheon_distance_modulus(empty, P_LCDM, [70.0, 0.3])
    m_b_corr = predicted - 19.25

    catalog = root / "Pantheon.dat"
    cov = root / "Pantheon.cov"
    with catalog.open("w", encoding="utf-8") as handle:
        handle.write("zHD zHEL m_b_corr CEPH_DIST IS_CALIBRATOR\n")
        for row in zip(z_hd, z_hel, m_b_corr, ceph, calibrator):
            handle.write(f"{row[0]} {row[1]} {row[2]} {row[3]} {int(row[4])}\n")
    with cov.open("w", encoding="utf-8") as handle:
        handle.write("10\n")
        for value in covariance.ravel():
            handle.write(f"{value:.17g}\n")
    return catalog, cov


def _dovekie_synthetic():
    z_hd = np.array([0.02, 0.04, 0.08, 0.15, 0.3, 0.5, 0.8, 1.0], dtype=float)
    z_hel = z_hd + 0.0002
    precision = np.eye(z_hd.size) / (0.05**2)
    empty = dov_prepare_data(
        z_hd,
        z_hel,
        np.zeros(z_hd.size),
        np.full(z_hd.size, 0.05),
        precision,
        integration_points=512,
    )
    mu = dov_distance_modulus(empty, D_LCDM, [0.3])
    return dov_prepare_data(
        z_hd,
        z_hel,
        mu + 0.37,
        np.full(z_hd.size, 0.05),
        precision,
        integration_points=512,
    )


def test_hubbleflow_loader_removes_calibrators_and_fixes_reference_h0():
    with tempfile.TemporaryDirectory() as tmp:
        catalog, covariance = _pantheon_files(Path(tmp))
        data, original_rows = load_hubbleflow_data(
            catalog, covariance, z_min=0.01, integration_points=512
        )
        assert original_rows == 10
        assert data.n == 8
        assert not np.any(data.is_calibrator)
        assert H0_REFERENCE == 70.0
        assert LOCAL_SPECS[P_LCDM]["k_including_profiled_offset"] == 2


def test_hubbleflow_lcdm_recovers_synthetic_shape_under_profiled_offset():
    with tempfile.TemporaryDirectory() as tmp:
        catalog, covariance = _pantheon_files(Path(tmp))
        data, _ = load_hubbleflow_data(catalog, covariance, z_min=0.01, integration_points=512)
        fit = fit_pantheon_hf(data, P_LCDM, [11, 23], maxiter=80, ftol=1e-12)
        assert fit["status"] == "PASS"
        assert abs(fit["best"]["Omega_m"] - 0.3) < 2e-3
        assert fit["best"]["chi2"] < 1e-5


def test_wa_profile_classifier_detects_bounded_interior_minimum():
    rows = [
        {"wa": -5.0, "chi2": 8.0},
        {"wa": -4.0, "chi2": 4.5},
        {"wa": -3.0, "chi2": 1.0},
        {"wa": -2.0, "chi2": 0.0},
        {"wa": -1.0, "chi2": 1.2},
        {"wa": 0.0, "chi2": 4.2},
        {"wa": 1.0, "chi2": 8.5},
    ]
    result = classify_profile(rows)
    assert result["state"] == "VERIFIED_BOUNDED_PROFILE"
    assert result["best_wa"] == -2.0
    assert result["minimum_at_profile_edge"] is False
    assert result["bounded_95_on_grid"] is True


def test_wa_profile_classifier_preserves_edge_uncertainty():
    rows = [
        {"wa": -8.0, "chi2": 0.0},
        {"wa": -6.0, "chi2": 0.4},
        {"wa": -4.0, "chi2": 1.2},
        {"wa": -2.0, "chi2": 2.8},
        {"wa": 0.0, "chi2": 5.0},
    ]
    result = classify_profile(rows)
    assert result["state"] == "VERIFIED_LIMITED_EDGE_OR_OPEN_PROFILE"
    assert result["minimum_at_profile_edge"] is True
    assert result["bounded_95_on_grid"] is False


def test_fixed_wa_fit_is_finite_on_synthetic_dovekie_data():
    data = _dovekie_synthetic()
    row = fit_fixed_wa(data, -1.0, [(0.30, -1.0), (0.40, -0.8)], maxiter=60, ftol=1e-12)
    assert np.isfinite(row["chi2"])
    assert 0.10 <= row["Omega_m"] <= 0.60
    assert -2.0 <= row["w0"] <= -0.3
    assert row["wa"] == -1.0


def test_asymptotic_cpl_limit_is_finite_and_w0_free():
    data = _dovekie_synthetic()
    chi2, offset = asymptotic_profiled_likelihood(data, 0.3)
    assert np.isfinite(chi2)
    assert np.isfinite(offset)
    fit = fit_asymptotic_limit(data, maxiter=60, ftol=1e-12)
    assert fit["all_starts_converged"] is True
    assert np.isfinite(fit["chi2"])
    assert 0.10 <= fit["Omega_m"] <= 0.60
    assert fit["w0_identifiable_in_limit"] is False
