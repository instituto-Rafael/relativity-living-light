"""Negative and positive static contracts for the native diagnostic UI.

No emulator or physical device is claimed. Android compilation is covered by
the existing real Gradle/CMake workflow, separately from these source gates.
"""
from pathlib import Path

ACTIVITY = Path("app/src/main/java/org/rafaelia/rll/MainActivity.java")
BRIDGE = Path("app/src/main/java/org/rafaelia/rll/KernelBridge.java")
NATIVE = Path("core/lowlevel_runtime/c/kernel_bridge.c")

def test_not_three_line_smoke_ui_anymore():
    text = ACTIVITY.read_text(encoding="utf-8")
    assert 'view.setText("RLL native runtime OK\\narch="' not in text
    for section in ("01  Estado da execução", "02  Testes de fronteira JNI",
                    "03  Explorar o kernel", "04  Evidências e limites"):
        assert section in text
    assert "ScrollView" in text
    assert "setContentView(scroll)" in text

def test_interactions_produce_real_results_not_mock_success():
    text = ACTIVITY.read_text(encoding="utf-8")
    assert 'v -> runDiagnostics()' in text
    assert 'v -> runManual()' in text
    assert 'v -> copyReceipt()' in text
    assert "KernelBridge.archDetect()" in text
    assert "KernelBridge.kernelScore(x, y)" in text
    assert "int expected = expectedScore(arch, x, y)" in text
    assert "observed == expected" in text
    assert 'gate=FAIL_JNI' in text
    assert 'TOKEN_VAZIO_RUNTIME_EXECUTION' in text

def test_bounded_safe_score_inputs_and_no_network():
    text = ACTIVITY.read_text(encoding="utf-8")
    assert "private static final int LIMIT = 10000;" in text
    assert "x < -LIMIT || x > LIMIT || y < -LIMIT || y > LIMIT" in text
    assert "((x * 31) ^ (y * 17)) + arch" in text
    assert "getSystemService(CLIPBOARD_SERVICE)" in text
    assert "android.permission" not in text
    assert "HttpURLConnection" not in text
    assert "claim_allowed=false" in text

def test_platform_boundary_and_native_abi_preserved():
    app = ACTIVITY.read_text(encoding="utf-8")
    bridge = BRIDGE.read_text(encoding="utf-8")
    native = NATIVE.read_text(encoding="utf-8")
    assert "Hosted Android diagnostic surface" in app
    assert "not a cosmology solver or freestanding L0" in app
    assert 'System.loadLibrary("rll_kernel_bridge")' in bridge
    assert "int rll_kernel_score(int x, int y)" in native
