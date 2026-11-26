"""G4 nested-model upper bound and null-source guard (source-only).

These tests do not require the full Pantheon covariance; integration CI must
evaluate the full joint likelihood on the exact G4 HEAD.
"""
import numpy as np
import pytest
from tools import run_g4_background_tournament as g4


@pytest.mark.parametrize("model", ["wCDM", "CPL", "GEDE", "IDE_QrhoLambda", "RLL"])
def test_best_lcdm_null_embedding_preserves_expansion_model(model):
    best = {"H0": 71.12, "Omega_m": 0.302, "omega_b_h2": 0.026}
    anchor = g4.nested_null_start(model, best)
    baseline = np.array([best[k] for k in g4.COMMON_NAMES])
    z = np.array([0.,0.1,0.7,1.4,2.33])
    np.testing.assert_allclose(g4.e2(model,z,anchor),g4.e2("LCDM",z,baseline),
                               rtol=0.0,atol=1e-12)


def test_g4_nested_worse_fit_is_blocked_not_reported_as_physical_preference():
    assert g4.nested_fit_gap_exceeds_tolerance(1522.7948344813904,1492.574832908293)
    assert not g4.nested_fit_gap_exceeds_tolerance(1492.5748329083,1492.574832908293)
    assert not g4.nested_fit_gap_exceeds_tolerance(1492.524808312079,1492.574832908293)
    assert g4.nested_fit_gap_exceeds_tolerance(float("nan"),1492.57)


def test_g4_nested_anchor_rejects_invalid_baseline():
    with pytest.raises(ValueError):
        g4.nested_null_start("GEDE", {"H0":-70,"Omega_m":.3,"omega_b_h2":.02236})
    with pytest.raises(ValueError):
        g4.nested_null_start("LCDM", {"H0":70,"Omega_m":.3,"omega_b_h2":.02236})


def test_g4_nested_full_background_profiles_are_equal_across_all_blocks():
    """Falsifier: E² equality alone is insufficient for joint-source fidelity.

    Fully synthetic Pantheon (profile M_B), pure CC and three correlated BAO
    coordinates share one likelihood and covariance; no external survey copied.
    """
    from scipy.linalg import cho_factor, cho_solve

    p_cov = np.array([
        [0.12, 0.03, 0.01],
        [0.03, 0.16, 0.02],
        [0.01, 0.02, 0.10],
    ], dtype=float)
    p_chol = cho_factor(p_cov, lower=True, check_finite=True)
    ones = np.ones(3)
    p_cinv_ones = cho_solve(p_chol, ones, check_finite=True)
    pantheon = g4.PantheonBlock(
        z_hd=np.array([0.09, 0.31, 0.75]),
        z_hel=np.array([0.09, 0.31, 0.75]),
        m_b_corr=np.array([18.7, 21.1, 23.3]),
        ceph_dist=np.zeros(3),
        is_calibrator=np.array([False, False, False], dtype=bool),
        cholesky=p_chol,
        cinv_ones=p_cinv_ones,
        one_cinv_one=float(ones @ p_cinv_ones),
    )
    cc = g4.CCBlock(
        z=np.array([0.18, 1.0]), observed=np.array([75.0, 115.0]),
        sigma=np.array([5.0, 8.0]), sources=("CC_SYNTH_A", "CC_SYNTH_B"),
    )
    d_cov = np.array([
        [0.25, 0.02, 0.01],
        [0.02, 0.16, 0.015],
        [0.01, 0.015, 0.30],
    ], dtype=float)
    desi = g4.DESIBlock(
        z=np.array([0.38, 0.71, 2.33]),
        observable=("DM_over_rd", "DV_over_rd", "DH_over_rd"),
        observed=np.array([10.2, 15.1, 8.1]),
        covariance=d_cov,
        cholesky=cho_factor(d_cov, lower=True, check_finite=True),
    )
    data = g4.TournamentData(
        pantheon=pantheon, cc=cc, desi=desi,
        integration_grid=np.linspace(0.0, 2.7, 512),
    )
    best = {"H0": 71.12, "Omega_m": 0.302, "omega_b_h2": 0.02236}
    common = np.asarray([best[k] for k in g4.COMMON_NAMES], dtype=float)
    reference_predictions = g4.model_predictions(data, "LCDM", common)
    reference = g4.profiled_components(data, "LCDM", common)
    assert np.isfinite(reference["total"])
    assert reference["total"] >= 0.0
    assert np.isfinite(reference["M_B"])

    for model in ("wCDM", "CPL", "GEDE", "IDE_QrhoLambda", "RLL"):
        anchor = g4.nested_null_start(model, best)
        predictions = g4.model_predictions(data, model, anchor)
        for actual, expected in zip(predictions, reference_predictions, strict=True):
            np.testing.assert_allclose(actual, expected, rtol=1e-12, atol=1e-10)
        components = g4.profiled_components(data, model, anchor)
        for block in ("Pantheon", "CC", "DESI", "M_B", "total"):
            np.testing.assert_allclose(
                components[block], reference[block], rtol=1e-11, atol=1e-7,
                err_msg=f"{model} nested-null mismatch for {block}",
            )
        assert not g4.nested_fit_gap_exceeds_tolerance(
            float(components["total"]), float(reference["total"])
        )
        assert g4.nested_fit_gap_exceeds_tolerance(
            float(reference["total"] + 0.1), float(reference["total"])
        )


def test_nested_reference_fails_closed_on_missing_or_nonfinite_parameter():
    valid = {"H0": 70.0, "Omega_m": 0.3, "omega_b_h2": 0.02236}
    for model in ("wCDM", "CPL", "GEDE", "IDE_QrhoLambda", "RLL"):
        for corrupt in (
            {"H0": 70.0, "Omega_m": np.nan, "omega_b_h2": 0.02236},
            {"H0": 70.0, "Omega_m": 0.3},
            {"H0": 70.0, "Omega_m": 0.3, "omega_b_h2": np.inf},
        ):
            with pytest.raises((ValueError, KeyError)):
                g4.nested_null_start(model, corrupt)
        anchor = g4.nested_null_start(model, valid)
        assert anchor.size == len(g4.parameter_names(model))
