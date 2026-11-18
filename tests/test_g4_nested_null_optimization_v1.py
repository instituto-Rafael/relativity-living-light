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
