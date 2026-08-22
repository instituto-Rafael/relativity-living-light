import importlib.util
import json
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
G4_MODULE_PATH = ROOT / "tools/run_g4_background_tournament.py"
G5_MODULE_PATH = ROOT / "tools/build_g5_canonical_background_manifest.py"
G6_MODULE_PATH = ROOT / "tools/run_g6_canonical_inference.py"
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


def _ensure_pinned_pantheon_covariance() -> bool:
    """Materialize the exact G2 input when a clean checkout does not contain it.

    Returns True only when this test created the covariance.  The caller uses
    that fact to restore the clean-checkout repository state after the test,
    while preserving the materialization receipt in artifacts/python-tests.
    """
    if PANTHEON_COVARIANCE.exists():
        return False

    materializer = load_module("pantheon_covariance_materializer_integration", PANTHEON_MATERIALIZER_PATH)
    receipt = materializer.materialize(
        PANTHEON_COVARIANCE.parent,
        PANTHEON_MATERIALIZATION_OUT,
    )
    assert receipt["status"] == "PASS"
    assert receipt["claim_allowed"] is False
    assert receipt["artifact"]["sha256"] == materializer.EXPECTED_SHA256
    assert receipt["artifact"]["dimension"] == materializer.EXPECTED_DIMENSION
    assert receipt["policy"]["full_covariance_likelihood_ready"] is True
    assert PANTHEON_COVARIANCE.exists()
    return True


def test_execute_g4_g5_g6_chain_and_emit_receipts(request):
    """Execute the governed scientific chain without silently skipping a gate.

    The ordinary Python-test workflow uploads artifacts/python-tests even on
    failure.  G4 and G5 receipts are written before G6 begins, so a G6
    convergence/evidence failure still preserves the upstream positive and
    negative evidence instead of erasing the run.
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
    G4_OUT.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")

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
    G5_OUT.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    assert manifest["state"] == "READY_G5_CANONICAL_BACKGROUND_LIKELIHOOD"
    assert manifest["claim_allowed"] is False
    assert manifest["scientific_confirmation"] is False
    assert manifest["models"] == list(g4.MODEL_ORDER)
    assert manifest["g4_receipt_sha256"]
    assert manifest["executor_sha256"]

    g6 = load_module("g6bg_integration", G6_MODULE_PATH)
    inference = g6.build_report(G4_OUT, G5_OUT, ROOT)
    G6_OUT.write_text(json.dumps(inference, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    assert inference["state"] == "PASS_LIMITED_G6_CANONICAL_INFERENCE", inference.get("convergence")
    assert inference["claim_allowed"] is False
    assert inference["scientific_confirmation"] is False
    assert inference["negative_results_preserved"] is True
    assert inference["convergence"]["pass_all"] is True
    assert len(inference["nested"]["LCDM"]) == 3
    assert len(inference["nested"]["RLL"]) == 3
    assert inference["mcmc"]["LCDM"]["max_Rhat"] <= 1.10
    assert inference["mcmc"]["RLL"]["max_Rhat"] <= 1.10
