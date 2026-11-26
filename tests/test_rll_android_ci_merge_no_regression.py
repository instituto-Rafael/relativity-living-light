"""A/B regression contract: preserve both main signature evidence and lab Android gates."""
from __future__ import annotations

from pathlib import Path
import yaml

ROOT = Path(__file__).resolve().parents[1]
WORKFLOW = ROOT / ".github/workflows/android-build.yml"


def _steps() -> dict[str, dict]:
    document = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    return {step["name"]: step for step in document["jobs"]["android"]["steps"]}


def test_main_apk_signature_receipt_survives_merge_without_public_subject() -> None:
    steps = _steps()
    generation = steps["Generate signed APK verification receipt"]
    upload = steps["Upload APK signature receipt"]
    assert "env.RLL_RELEASE_SIGNING_AVAILABLE" in generation["if"]
    assert "env.RLL_RELEASE_SIGNING_AVAILABLE" in upload["if"]
    code = generation["run"]
    assert 'apksigner" verify --verbose --print-certs' in code
    assert "apk-signature-receipts/receipt.json" in code
    assert '"artifact_sha256"' in code
    assert '"certificate"' in code
    assert '"claim_allowed": False' in code
    assert "Missing signer certificate SHA-256 receipt" in code
    assert "certificate_subject_exported" in code
    assert 'cert["dn"]' not in code
    assert "apk-signature-receipts/apksigner.txt" not in code
    assert 'trap \'rm -f "$RUNNER_TEMP/rll-apksigner-verified.txt"\' EXIT' in code
    assert upload["uses"] == (
        "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9"
    )
    assert upload["with"]["if-no-files-found"] == "error"


def test_lab_newer_actions_and_three_android_falsifier_steps_survive_merge() -> None:
    steps = _steps()
    assert steps["Set up JDK 17"]["uses"] == "actions/setup-java@d1374f8ac74474200d16ef8ecee22c7ae7a51880"
    assert steps["Set up JDK 17"]["with"]["problem-matcher"] is True
    assert "8da46b539cd8fe6ab27ca75128919a18d757604c" in steps["Set up Gradle"]["uses"]
    assert "be39fa834029ff78f1a44aa3bb0819b8fc2bd8fd" in steps["Set up Android SDK and NDK"]["uses"]
    for name in (
        "Formula engine standalone JVM falsifiers",
        "Full covariance DESI DR2 numerical self-test (hosted Java)",
        "Canonical Omega 1-click ZIP integrity adversarial test",
    ):
        assert name in steps
    assert "Remove temporary signing material" in steps
    assert "Build debug unsigned APK" in steps
    assert "Build signed release APK and AAB" in steps
    assert "Upload validation unsigned APK" in steps


def test_release_receipt_never_runs_without_release_keys() -> None:
    document = yaml.safe_load(WORKFLOW.read_text(encoding="utf-8"))
    expression = document["jobs"]["android"]["env"]["RLL_RELEASE_SIGNING_AVAILABLE"]
    for secret in (
        "RLL_RELEASE_KEYSTORE_BASE64",
        "RLL_RELEASE_STORE_PASSWORD",
        "RLL_RELEASE_KEY_ALIAS",
        "RLL_RELEASE_KEY_PASSWORD",
    ):
        assert secret in expression
    steps = _steps()
    for name in (
        "Decode release keystore",
        "Build signed release APK and AAB",
        "Generate signed APK verification receipt",
        "Upload APK signature receipt",
        "Upload signed release APK",
        "Upload signed release AAB",
    ):
        assert "env.RLL_RELEASE_SIGNING_AVAILABLE" in steps[name]["if"]
