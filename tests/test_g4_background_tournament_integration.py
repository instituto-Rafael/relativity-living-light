import importlib.util
import json
import sys
from pathlib import Path

import numpy as np


ROOT = Path(__file__).resolve().parents[1]
G4_MODULE_PATH = ROOT / "tools/run_g4_background_tournament.py"
G5_MODULE_PATH = ROOT / "tools/build_g5_canonical_background_manifest.py"
G6_MODULE_PATH = ROOT / "tools/run_g6_canonical_inference.py"
STRICT_JSON_PATH = ROOT / "tools/strict_json_receipt.py"
PANTHEON_MATERIALIZER_PATH = ROOT / "scripts/fetch_pantheon_covariance.py"
PANTHEON_COVARIANCE = (
    ROOT
    / "data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR"
    / "Pantheon+SH0ES_STAT+SYS.cov"
)
PANTHEON_COVARIANCE_SIDECAR = PANTHEON_COVARIANCE.with_name(PANTHEON_COVARIANCE.name + ".sha256")
G4_OUT = ROOT / "artifacts/python-tests/g4_background_six_model_receipt.json"
G5_OUT = ROOT / "artifacts/python-tests/g5_canonical_background_manifest.json"
G6_OUT = ROOT / "artifacts/python-tests/g6_canonical_inference_receipt.json"
PANTHEON_MATERIALIZATION_OUT = (
    ROOT / "artifacts/python-tests/pantheon_covariance_materialization.json"
)


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    sys.modules[name] = mod
    spec.loader.exec_module(mod)
    return mod


def _assert_pinned_covariance_receipt(receipt, materializer):
    assert receipt["status"] == "PASS"
    assert receipt["claim_allowed"] is False
    assert receipt["artifact"]["sha256"] == materializer.EXPECTED_SHA256
    assert receipt["artifact"]["bytes"] == materializer.EXPECTED_BYTES
    assert receipt["artifact"]["dimension"] == materializer.EXPECTED_DIMENSION
    assert receipt["artifact"]["values"] == materializer.EXPECTED_VALUES
    assert receipt["policy"]["full_covariance_likelihood_ready"] is True


def _ensure_pinned_pantheon_covariance() -> bool:
    """Materialize or reverify the exact G2 input and emit a current receipt.

    Returns True only when this test created the covariance. The caller uses
    that fact to restore the clean-checkout repository state after the test.
    A pre-existing ignored covariance is never trusted by mere existence: it is
    rehashed/reinspected with the pinned upstream identity before G4 executes.
    """
    materializer = load_module("pantheon_covariance_materializer_integration", PANTHEON_MATERIALIZER_PATH)
    if PANTHEON_COVARIANCE.exists():
        receipt = materializer.verify_existing(
            PANTHEON_COVARIANCE,
            PANTHEON_MATERIALIZATION_OUT,
        )
        _assert_pinned_covariance_receipt(receipt, materializer)
        return False

    receipt = materializer.materialize(
        PANTHEON_COVARIANCE.parent,
        PANTHEON_MATERIALIZATION_OUT,
    )
    _assert_pinned_covariance_receipt(receipt, materializer)
    assert PANTHEON_COVARIANCE.exists()
    return True


def _write_strict_receipt(path: Path, value) -> None:
    strict_json = load_module("strict_json_receipt_integration", STRICT_JSON_PATH)
    path.write_text(strict_json.dumps(value, indent=2) + "\n", encoding="utf-8")
    # Receipt bytes must be standard JSON and retain null markers for any
    # non-finite failed-attempt diagnostics rather than NaN/Infinity literals.
    parsed = json.loads(path.read_text(encoding="utf-8"))
    assert isinstance(parsed, dict)


def _assert_g6_state_consistency(inference) -> None:
    """Separate execution validity from the scientific convergence gate.

    A BLOCKED G6 receipt is a valid, auditable execution outcome when its
    convergence vector and F_gap explain the block. CI must not rewrite that
    scientific result into PASS merely to make software tests green.
    """
    allowed = {
        "PASS_LIMITED_G6_CANONICAL_INFERENCE",
        "BLOCKED_G6_CONVERGENCE_OR_EVIDENCE",
    }
    assert inference["state"] in allowed
    assert inference["claim_allowed"] is False
    assert inference["scientific_confirmation"] is False
    assert inference["negative_results_preserved"] is True
    assert len(inference["nested"]["LCDM"]) == 3
    assert len(inference["nested"]["RLL"]) == 3

    convergence = inference["convergence"]
    pass_all = convergence["pass_all"]
    if inference["state"] == "PASS_LIMITED_G6_CANONICAL_INFERENCE":
        assert pass_all is True
        assert inference["F_gap"] == []
        assert inference["mcmc"]["LCDM"]["max_Rhat"] <= 1.10
        assert inference["mcmc"]["RLL"]["max_Rhat"] <= 1.10
        return

    assert pass_all is False
    assert inference["F_gap"]
    failed_components = [
        key for key, value in convergence.items()
        if key != "pass_all" and value is False
    ]
    assert failed_components
    mapping = {
        "mcmc_pass": "MCMC_CONVERGENCE",
        "nested_finite": "NESTED_FINITE",
        "nested_not_maxiter": "NESTED_MAXITER",
        "lnB10_span_pass": "NESTED_SEED_STABILITY",
        "prior_sensitivity_finite": "PRIOR_SENSITIVITY",
    }
    assert set(inference["F_gap"]) == {mapping[key] for key in failed_components}
    if not convergence["mcmc_pass"]:
        assert max(
            inference["mcmc"]["LCDM"]["max_Rhat"],
            inference["mcmc"]["RLL"]["max_Rhat"],
        ) > 1.10


def test_strict_json_preserves_failed_diagnostic_without_fake_zero():
    strict_json = load_module("strict_json_receipt_unit", STRICT_JSON_PATH)
    normalized = strict_json.normalize({"finite": 1.5, "bad": float("inf"), "nan": float("nan")})
    assert normalized == {"finite": 1.5, "bad": None, "nan": None}
    assert "Infinity" not in strict_json.dumps(normalized)
    assert "NaN" not in strict_json.dumps(normalized)


def test_g6_emcee_proposal_rng_is_deterministic():
    g6 = load_module("g6_rng_unit", G6_MODULE_PATH)
    p0 = np.asarray([[-1.0], [-0.25], [0.25], [1.0]], dtype=float)

    def sample(seed: int):
        sampler = g6.emcee.EnsembleSampler(
            4,
            1,
            lambda theta: -0.5 * float(np.asarray(theta, dtype=float)[0] ** 2),
        )
        fingerprint = g6._seed_emcee_sampler(sampler, seed)
        sampler.run_mcmc(
            p0,
            12,
            progress=False,
            skip_initial_state_check=True,
        )
        return fingerprint, np.asarray(sampler.get_chain(), dtype=float)

    fingerprint_a, chain_a = sample(12345)
    fingerprint_b, chain_b = sample(12345)
    fingerprint_c, chain_c = sample(54321)

    assert fingerprint_a == fingerprint_b
    assert np.array_equal(chain_a, chain_b)
    assert fingerprint_c != fingerprint_a
    assert not np.array_equal(chain_a, chain_c)


def test_execute_g4_g5_g6_chain_and_emit_receipts(request):
    """Execute the governed scientific chain without silently skipping a gate.

    The ordinary Python-test workflow uploads artifacts/python-tests even on
    failure. G4 and G5 receipts are written before G6 begins. A scientifically
    BLOCKED G6 is accepted only as an auditable execution state; it does not
    become a PASS, does not clear F_gap, and does not promote a claim.
    """
    created_covariance = _ensure_pinned_pantheon_covariance()
    if created_covariance:
        request.addfinalizer(lambda: PANTHEON_COVARIANCE.unlink(missing_ok=True))
        request.addfinalizer(lambda: PANTHEON_COVARIANCE_SIDECAR.unlink(missing_ok=True))

    g4 = load_module("g4bg_integration", G4_MODULE_PATH)
    report = g4.build_report(
        seeds=(11, 23, 37, 53, 71),
        maxiter=250,
        ftol=1.0e-10,
        integration_points=4096,
    )
    G4_OUT.parent.mkdir(parents=True, exist_ok=True)
    _write_strict_receipt(G4_OUT, report)

    assert report["state"] == "PASS_LIMITED_G4_BACKGROUND_TOURNAMENT"
    assert report["claim_allowed"] is False
    assert report["scientific_confirmation"] is False
    assert report["negative_results_preserved"] is True
    assert report["null_limits"]["passed"] is True
    assert [row["model"] for row in report["rows"]] == list(g4.MODEL_ORDER)
    assert report["datasets"]["DESI_rows"] == 13
    assert report["datasets"]["Pantheon_rows"] == 1657
    assert report["datasets"]["pure_CC_rows"] > 0
    assert report["datasets"]["growth_CMB_policy"] == "DEFER_TO_G8_G9_NO_PROXY_PROMOTION"

    g5 = load_module("g5bg_integration", G5_MODULE_PATH)
    manifest = g5.build_manifest(G4_OUT, ROOT)
    _write_strict_receipt(G5_OUT, manifest)
    assert manifest["state"] == "READY_G5_CANONICAL_BACKGROUND_LIKELIHOOD"
    assert manifest["claim_allowed"] is False
    assert manifest["scientific_confirmation"] is False
    assert manifest["models"] == list(g4.MODEL_ORDER)
    assert manifest["g4_receipt_sha256"]
    assert manifest["executor_sha256"]

    g6 = load_module("g6bg_integration", G6_MODULE_PATH)
    inference = g6.build_report(G4_OUT, G5_OUT, ROOT)
    _write_strict_receipt(G6_OUT, inference)
    _assert_g6_state_consistency(inference)
