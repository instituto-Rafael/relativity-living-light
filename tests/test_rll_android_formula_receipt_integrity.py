"""Receipt integrity source-side falsifiers for on-device native/FormulaLab evidence.
No private user receipt or observational values are committed here.
"""
from pathlib import Path

ROOT=Path("app/src/main/java/org/rafaelia/rll")
ENGINE=(ROOT/"FormulaEngine.java").read_text(encoding="utf-8")
VIEW=(ROOT/"FormulaLabView.java").read_text(encoding="utf-8")

def test_exact_input_and_observation_pair_are_recorded():
    assert 'SCHEMA = "rll.android.formula-lab.v2"' in ENGINE
    assert 'append("Hobs=")' in ENGINE and 'append(";Hsigma=")' in ENGINE
    assert "Double.toString(a.hObserved)" in ENGINE
    assert "Double.toString(a.hSigma)" in ENGINE
    assert "observation_status=USER_ENTERED_UNVERIFIED" in ENGINE
    assert "TOKEN_VAZIO_NOT_PROVIDED" in ENGINE
    assert "TOKEN_VAZIO_INVALID_PAIR" in ENGINE
    assert "sb.append(String.format(Locale.US," not in ENGINE

def test_repeated_sweep_is_not_accumulated():
    assert 'lastReceipt=lastBaseReceipt+evidence.toString()' in VIEW
    assert 'lastReceipt+=evidence.toString()' not in VIEW
    assert 'lastBaseReceipt=r.receipt(a)' in VIEW
    assert 'calculate();' in VIEW[VIEW.index('private void sweep()'):VIEW.index('private void normalize()')]

def test_formatted_output_uses_real_java_newlines():
    # The v1 code accidentally used literal "\\n" sequences in sweep/preview strings.
    double_escaped='\\\\' + 'n'
    assert double_escaped not in VIEW
    assert 'StringBuilder("Varredura numérica 0 ≤ z ≤ 3, passo 0,3\\n")' in VIEW
    assert 'String.format(Locale.US,"%.2f;%.9g;%.9g\\n"' in VIEW

def test_copy_is_fail_closed_after_input_or_model_change():
    assert 'private boolean inputsMatchLastCalculation()' in VIEW
    assert 'current.equals(lastBaseReceipt)' in VIEW
    show=VIEW[VIEW.index('private void showSelected()'):VIEW.index('private void sweep()')]
    assert 'if(!inputsMatchLastCalculation())' in show
    copy=VIEW[VIEW.index('private void copy()'):VIEW.index('public void attach(')]
    assert 'if(!inputsMatchLastCalculation())' in copy
    assert 'FORMULA_LAB_PAYLOAD_UTF8_ONLY' in copy
    assert 'sha256(scope)' in copy
    assert 'receipt_sha256=' in copy

def test_jvm_cross_model_residual_invariant_and_no_physics_claim():
    tests=Path("app/src/test/java/org/rafaelia/rll/FormulaEngineSelfTest.java").read_text(encoding="utf-8")
    assert '(resR-resW)*compare.hSigma,hW-hR' in tests
    assert "shared Hobs/sigma cross-model invariant" in tests
    assert "observation_status=TOKEN_VAZIO_INVALID_PAIR" in tests
    assert "claim_allowed=false" in ENGINE
    assert "physical_validation=TOKEN_VAZIO_NOT_RUN" in ENGINE
