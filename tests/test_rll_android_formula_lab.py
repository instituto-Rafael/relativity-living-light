"""RLL Android formula catalogue and safe version contract, source-only claims."""
from pathlib import Path
import re

BASE=Path("app/src/main/java/org/rafaelia/rll")
ENGINE=BASE/"FormulaEngine.java"
UI=BASE/"FormulaLabView.java"
RELEASE=BASE/"ReleaseGateView.java"
ACTIVITY=BASE/"MainActivity.java"
GRADLE=Path("app/build.gradle")
MANIFEST=Path("app/src/main/AndroidManifest.xml")
ACTION=Path(".github/workflows/android-build.yml")

def test_user_can_select_models_and_individual_formulas():
    source=ENGINE.read_text(encoding="utf-8")
    ui=UI.read_text(encoding="utf-8")
    assert "enum Model { LCDM, WCDM, CPL, RLL }" in source
    assert "COS-HZ" in source and "COS-RD-PROXY" in source
    assert "RLL-CONTINUITY-DOC" in source and "RLL-CONTINUITY-CONS" in source
    assert "COS-DM-QUADRATURE-DELTA" in source
    assert "RLL-NULL-SECTOR" in source
    assert "Exibir apenas a fórmula selecionada" in ui
    assert "Varredura z = 0 até 3 (11 pontos)" in ui
    assert "Calcular todas as fórmulas deste modelo" in ui
    activity=ACTIVITY.read_text(encoding="utf-8")
    # The v0.7 one-click exporter must share the actual attached FormulaLab instance.
    assert "FormulaLabView formulaLab=new FormulaLabView(this);" in activity
    assert "formulaLab.attach(root);" in activity
    assert "realDataLab.bindEvidenceInputs(formulaLab,inputX,inputY);" in activity

def test_source_data_claim_separation_and_negative_domains():
    s=ENGINE.read_text(encoding="utf-8")
    ui=UI.read_text(encoding="utf-8")
    for token in ("claim_allowed=false","USER_INPUT_NOT_REAL_OBSERVATION",
                  "TOKEN_VAZIO_NOT_RUN","TOKEN_VAZIO_DOMAIN_INPUT","TOKEN_VAZIO_E2_NONPOSITIVE"):
        assert token in s
    assert "H(z) observado" in ui
    assert "Erro σH positivo" in ui
    assert "MessageDigest.getInstance(\"SHA-256\")" in ui
    assert "getSystemService(Activity.CLIPBOARD_SERVICE)" in ui

def test_release_detection_is_signed_release_discovery_not_unattended_install():
    rel=RELEASE.read_text(encoding="utf-8")
    manifest=MANIFEST.read_text(encoding="utf-8")
    gradle=GRADLE.read_text(encoding="utf-8")
    assert 'android-rll-v[1-9][0-9]{0,8}' in rel
    assert 'rll-android-release.apk' in rel
    assert 'sha256:[0-9a-f]{64}' in rel
    assert "releases?per_page=25" in rel
    assert "github.com/instituto-Rafael/relativity-living-light/releases/tag/" in rel
    assert "Intent.ACTION_VIEW" in rel and "AlertDialog.Builder" in rel
    assert "PackageInstaller" not in rel and "ACTION_INSTALL_PACKAGE" not in rel
    assert "setConnectTimeout(4000)" in rel and "setReadTimeout(4000)" in rel
    assert 'android.permission.INTERNET' in manifest
    assert 'android:usesCleartextTraffic="false"' in manifest
    assert "RLL_ANDROID_VERSION_CODE" in gradle
    # Version is monotone: pinning 2 breaks on every approved Android bump.
    assert re.search(r"RLL_ANDROID_VERSION_CODE.*getOrElse\([1-9][0-9]*\)", gradle)

def test_no_new_dsp_dependency_and_independent_java_gate():
    action=ACTION.read_text(encoding="utf-8")
    assert "sh app/verify_formula_engine.sh" in action
    sh=Path("app/verify_formula_engine.sh").read_text(encoding="utf-8")
    assert "javac -encoding UTF-8" in sh and "FormulaEngineSelfTest" in sh
    java=Path("app/src/test/java/org/rafaelia/rll/FormulaEngineSelfTest.java").read_text(encoding="utf-8")
    assert "RLL_FORMULA_ENGINE_SELFTEST_PASS" in java
    assert "conserved residual identity" in java
    assert "CPL LCDM null" in java
    assert "RLL Os0=0 LCDM null" in java
