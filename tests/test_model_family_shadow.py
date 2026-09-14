import json
from pathlib import Path

import numpy as np

from data.pipelines.structure_d.model_family_shadow import (
    COMPOSITION_MODEL_IDS,
    CONTRACT_PATH,
    CORE_MODEL_IDS,
    closure_fractions,
    e2_for_model,
    load_contract,
    load_model_specs,
    transverse_comoving_distance_mpc,
)


def _vector(spec, **overrides):
    values = []
    for name, (low, high) in zip(spec.parameter_names, spec.bounds):
        values.append(float(overrides.get(name, (low + high) / 2.0)))
    return np.asarray(values, dtype=float)


def _shared(**extra):
    return {"H0": 70.0, "Om": 0.30, "Ob_h2": 0.022, **extra}


def test_contract_is_shadow_and_non_promotional():
    contract = load_contract()
    assert contract["status"] == "EXPERIMENTAL_SHADOW"
    assert contract["claim_allowed"] is False
    assert contract["canonical_outputs_modified"] is False
    assert contract["scientific_boundary"]["comparison_scope"] == "background_expansion_only"
    assert set(contract["scientific_boundary"]["included_terms"]) == {"H(z)", "DESI_DR2_BAO"}


def test_registry_has_ten_core_and_five_compositions():
    specs = load_model_specs()
    assert len(CORE_MODEL_IDS) == 10
    assert len(COMPOSITION_MODEL_IDS) == 5
    assert set(specs) == set(CORE_MODEL_IDS) | set(COMPOSITION_MODEL_IDS)


def test_parameter_names_and_bounds_are_unique_and_finite():
    for spec in load_model_specs().values():
        assert len(spec.parameter_names) == len(set(spec.parameter_names))
        assert len(spec.parameter_names) == len(spec.bounds)
        for low, high in spec.bounds:
            assert np.isfinite(low)
            assert np.isfinite(high)
            assert low < high


def test_flat_models_do_not_fit_omega_lambda_independently():
    for spec in load_model_specs().values():
        if spec.geometry == "flat":
            assert "OL" not in spec.parameter_names
            assert "Omega_Lambda" not in spec.parameter_names


def test_every_model_is_exactly_normalized_at_z_zero():
    for spec in load_model_specs().values():
        vector = _vector(spec)
        got = float(e2_for_model(spec, 0.0, vector))
        assert np.isclose(got, 1.0, rtol=0.0, atol=1.0e-10), spec.model_id


def test_fraction_closure_is_exact():
    for spec in load_model_specs().values():
        fractions = closure_fractions(spec, _vector(spec))
        assert np.isclose(sum(fractions.values()), 1.0, rtol=0.0, atol=1.0e-12), spec.model_id


def test_standard_dynamic_models_nest_flat_lcdm():
    specs = load_model_specs()
    z = np.array([0.0, 0.25, 0.8, 2.0, 5.0])
    baseline = e2_for_model(specs["FLCDM"], z, _vector(specs["FLCDM"], **_shared()))
    cases = {
        "wCDM": _shared(w=-1.0),
        "CPL": _shared(w0=-1.0, wa=0.0),
        "JBP": _shared(w0=-1.0, wa=0.0),
        "BA": _shared(w0=-1.0, wa=0.0),
        "FSLL1": _shared(w0=-1.0, wa=0.0),
        "GCG": _shared(As=1.0, alpha=0.0),
    }
    for model_id, values in cases.items():
        got = e2_for_model(specs[model_id], z, _vector(specs[model_id], **values))
        assert np.allclose(got, baseline, rtol=1.0e-12, atol=1.0e-12), model_id


def test_rll_zero_fraction_nests_flat_lcdm():
    specs = load_model_specs()
    z = np.array([0.0, 0.3, 1.0, 3.0])
    baseline = e2_for_model(specs["FLCDM"], z, _vector(specs["FLCDM"], **_shared()))
    rll = e2_for_model(
        specs["RLL"],
        z,
        _vector(specs["RLL"], **_shared(Os0=0.0, zt=1.2, wt=0.4)),
    )
    assert np.allclose(rll, baseline, rtol=1.0e-12, atol=1.0e-12)


def test_rll_compositions_nest_their_companion_when_os0_is_zero():
    specs = load_model_specs()
    z = np.array([0.0, 0.4, 1.1, 2.5])
    pairs = {
        "RLL_wCDM": ("wCDM", {"w": -0.9}),
        "RLL_CPL": ("CPL", {"w0": -0.95, "wa": 0.3}),
        "RLL_JBP": ("JBP", {"w0": -0.95, "wa": 0.3}),
        "RLL_BA": ("BA", {"w0": -0.95, "wa": 0.3}),
        "RLL_PEDE": ("PEDE", {}),
    }
    for composite, (companion, dynamic) in pairs.items():
        companion_values = _shared(**dynamic)
        composite_values = _shared(Os0=0.0, zt=1.3, wt=0.5, **dynamic)
        expected = e2_for_model(
            specs[companion], z, _vector(specs[companion], **companion_values)
        )
        got = e2_for_model(
            specs[composite], z, _vector(specs[composite], **composite_values)
        )
        assert np.allclose(got, expected, rtol=1.0e-12, atol=1.0e-12), composite


def test_curved_lcdm_nests_flat_geometry_at_ok_zero():
    specs = load_model_specs()
    flat_v = _vector(specs["FLCDM"], **_shared())
    curved_v = _vector(specs["oLCDM"], **_shared(Ok=0.0))
    z = np.array([0.0, 0.2, 0.8, 2.0])
    assert np.allclose(
        e2_for_model(specs["oLCDM"], z, curved_v),
        e2_for_model(specs["FLCDM"], z, flat_v),
        rtol=1.0e-12,
        atol=1.0e-12,
    )
    assert np.isclose(
        transverse_comoving_distance_mpc(specs["oLCDM"], 1.0, curved_v),
        transverse_comoving_distance_mpc(specs["FLCDM"], 1.0, flat_v),
        rtol=1.0e-10,
        atol=1.0e-8,
    )


def test_curvature_changes_transverse_distance_not_only_hubble_rate():
    specs = load_model_specs()
    open_v = _vector(specs["oLCDM"], **_shared(Ok=0.10))
    flat_v = _vector(specs["oLCDM"], **_shared(Ok=0.0))
    open_distance = transverse_comoving_distance_mpc(specs["oLCDM"], 1.5, open_v)
    flat_distance = transverse_comoving_distance_mpc(specs["oLCDM"], 1.5, flat_v)
    assert not np.isclose(open_distance, flat_distance, rtol=1.0e-6, atol=1.0e-6)


def test_excluded_terms_are_explicit_token_vazio_states():
    contract = load_contract()
    excluded = contract["scientific_boundary"]["excluded_terms"]
    assert excluded["CMB_shift"].startswith("TOKEN_VAZIO_")
    assert excluded["fsigma8"].startswith("TOKEN_VAZIO_")
    assert excluded["PantheonPlus"].startswith("TOKEN_VAZIO_")


def test_post_hoc_number_adaptation_is_explicitly_forbidden():
    policy = load_contract()["execution_policy"]
    assert policy["same_objective_for_all_models"] is True
    assert policy["same_data_for_all_models"] is True
    assert policy["same_covariance_for_all_models"] is True
    assert policy["bounds_frozen_before_execution"] is True
    assert policy["post_hoc_bound_changes_forbidden"] is True


def test_composition_policy_blocks_unstructured_permutations():
    policy = load_contract()["composition_policy"]
    assert policy["allowed_anchor"] == "RLL"
    assert set(policy["allowed_companions"]) == {"wCDM", "CPL", "JBP", "BA", "PEDE"}
    assert policy["maximum_nonstandard_sectors"] == 2
    assert "TOKEN_VAZIO_IDENTIFIABILITY" in policy["promotion_gate"]


def test_contract_json_is_strictly_parseable_and_has_no_nan():
    raw = Path(CONTRACT_PATH).read_text(encoding="utf-8")
    parsed = json.loads(
        raw,
        parse_constant=lambda value: (_ for _ in ()).throw(ValueError(value)),
    )
    assert parsed["schema"] == "rll.cosmology_model_family_shadow.v1"
