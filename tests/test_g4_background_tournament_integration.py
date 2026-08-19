import importlib.util
import json
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
G4_MODULE_PATH = ROOT / "tools/run_g4_background_tournament.py"
G5_MODULE_PATH = ROOT / "tools/build_g5_canonical_background_manifest.py"
G4_OUT = ROOT / "artifacts/python-tests/g4_background_six_model_receipt.json"
G5_OUT = ROOT / "artifacts/python-tests/g5_canonical_background_manifest.json"


def load_module(name: str, path: Path):
    spec = importlib.util.spec_from_file_location(name, path)
    assert spec and spec.loader
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def test_execute_full_six_model_background_tournament_and_emit_receipt():
    """Scientific integration test using the frozen G4 settings and G5 freeze.

    The ordinary Python-test workflow uploads artifacts/python-tests even on
    failure, so an unfavorable model result or implementation regression remains
    observable rather than disappearing behind a green/black-box assertion.
    """
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
