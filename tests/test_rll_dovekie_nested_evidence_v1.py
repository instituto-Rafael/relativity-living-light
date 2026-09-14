from __future__ import annotations

import sys
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
PRODUCT = ROOT / "products/rll-evidence-runner"
sys.path.insert(0, str(PRODUCT / "src"))

from rll_evidence import dovekie_fit_three_model as dov
from rll_evidence.dovekie_nested_evidence import (
    gaussian_loglike_factory,
    load_prior_registry,
    run_one,
)

PRIORS = ROOT / "data/governance/RLL_MODERN_BAYES_PRIORS_DOVEKIE_20260807_V1.json"


def synthetic_data():
    z_hd = np.array([0.02, 0.05, 0.10, 0.20, 0.40, 0.80], dtype=float)
    z_hel = z_hd + 0.0002
    precision = np.eye(z_hd.size) / (0.05**2)
    empty = dov.prepare_data(
        z_hd,
        z_hel,
        np.zeros(z_hd.size),
        np.full(z_hd.size, 0.05),
        precision,
        integration_points=256,
    )
    mu = dov.distance_modulus(empty, dov.LCDM, [0.3])
    return dov.prepare_data(
        z_hd,
        z_hel,
        mu + 0.25,
        np.full(z_hd.size, 0.05),
        precision,
        integration_points=256,
    )


def test_prior_registry_is_three_model_and_proper_nuisance_shared():
    registry = load_prior_registry(PRIORS)
    assert registry["claim_allowed"] is False
    assert registry["priors"][dov.LCDM]["M_offset"] == [-2.0, 2.0]
    assert registry["priors"][dov.CPL]["M_offset"] == [-2.0, 2.0]
    assert registry["priors"][dov.RLL]["M_offset"] == [-2.0, 2.0]
    assert registry["priors"][dov.CPL]["wa"][0] < -3.0


def test_gaussian_loglike_samples_offset_instead_of_profiling_it():
    data = synthetic_data()
    loglike, log_norm = gaussian_loglike_factory(data, dov.LCDM)
    at_true = loglike(np.array([0.3, 0.25]))
    at_wrong_offset = loglike(np.array([0.3, 0.0]))
    assert np.isfinite(log_norm)
    assert np.isfinite(at_true)
    assert at_true > at_wrong_offset


def test_tiny_nested_run_returns_finite_logz_and_posterior():
    data = synthetic_data()
    registry = load_prior_registry(PRIORS)
    result, summary = run_one(
        data,
        registry,
        dov.LCDM,
        seed=12345,
        nlive=24,
        dlogz=2.0,
    )
    assert np.isfinite(summary["logZ"])
    assert summary["logZ_error"] > 0.0
    assert summary["ncall"] > 0
    assert "Omega_m" in summary["posterior"]
    assert "M_offset" in summary["posterior"]
    assert result.logz.size > 0
