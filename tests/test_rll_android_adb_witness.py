"""Read-only source-side ADB falsifiers. Mock ADB only; no device execution."""
import hashlib
import os
from pathlib import Path
import subprocess
import tempfile

SCRIPT = Path("tools/android/rll_capture_install_via_adb.sh")
MOCK_ADB = r'''#!/bin/sh
printf '%s\n' "$*" >> "$ADB_TEST_CALLS"
case "$1" in
    devices)
        printf 'List of devices attached\n'
        if [ "${ADB_TEST_DEVICES:-one}" = 'two' ]; then
            printf 'testA\tdevice\ntestB\tdevice\n'
        else
            printf 'testA\tdevice\n'
        fi
        ;;
    shell)
        case "$2 $3" in
            'getprop ro.build.version.sdk') printf '29\r\n' ;;
            'getprop ro.product.cpu.abi') printf 'armeabi-v7a\r\n' ;;
            'pm path')
                if [ "${ADB_TEST_NO_BASE:-0}" = 1 ]; then
                    printf 'package:/data/app/split_config.apk\r\n'
                else
                    printf 'package:/data/app/example/base.apk\r\n'
                    if [ "${ADB_TEST_SPLITS:-0}" = 1 ]; then
                        printf 'package:/data/app/example/split_config.arm64_v8a.apk\r\n'
                    fi
                fi
                ;;
            *) exit 77 ;;
        esac
        ;;
    pull)
        [ "$2" = '/data/app/example/base.apk' ] || exit 78
        cp "$ADB_TEST_APK" "$3"
        ;;
    *) exit 76 ;;
esac
'''


def _execute(sha_kind="match", *, device_state="one", no_base=False, split_paths=False):
    with tempfile.TemporaryDirectory() as temp:
        folder = Path(temp)
        bin_path = folder / "bin"
        bin_path.mkdir()
        adb = bin_path / "adb"
        adb.write_text(MOCK_ADB, encoding="utf-8")
        adb.chmod(0o700)
        apk = folder / "installed.apk"
        apk.write_bytes(b"Synthetic unsigned APK bytes. Not a real app or device.")
        good_hash = hashlib.sha256(apk.read_bytes()).hexdigest()
        digest = good_hash if sha_kind == "match" else (
            "a" * 64 if sha_kind == "mismatch" else (
                "bad" if sha_kind == "malformed" else ""
            )
        )
        output = folder / "receipt"
        calls = folder / "adb_calls"
        env = dict(os.environ, PATH=f"{bin_path}:{os.environ['PATH']}",
                   ADB_TEST_CALLS=str(calls), ADB_TEST_APK=str(apk),
                   ADB_TEST_DEVICES=device_state,
                   ADB_TEST_NO_BASE="1" if no_base else "0",
                   ADB_TEST_SPLITS="1" if split_paths else "0")
        result = subprocess.run(["sh", str(SCRIPT), str(output), digest],
                                env=env, capture_output=True, text=True,
                                timeout=10)
        receipt = (output / "receipt.txt").read_text() if (output / "receipt.txt").exists() else ""
        status = (output / "STATUS.txt").read_text() if (output / "STATUS.txt").exists() else ""
        audit = calls.read_text() if calls.exists() else ""
        return result, receipt, status, audit, output.exists(), good_hash


def test_shell_syntax_is_valid():
    result = subprocess.run(["sh", "-n", str(SCRIPT)], capture_output=True, text=True)
    assert result.returncode == 0, result.stderr


def test_external_capture_hash_positive_is_scoped():
    result, receipt, status, calls, exists, expected = _execute()
    assert result.returncode == 0, result.stderr
    assert "apk_identity=MATCH_EXPECTED_APK" in receipt
    assert "installed_base_apk_sha256=" + expected in receipt
    assert "PASS_SCOPED_EXTERNAL_ADB_APK_HASH" in status
    assert "NOT_HARDWARE_ATTESTATION" in receipt
    assert "shell pm path org.rafaelia.rll.debug" in calls
    assert not any(line.startswith(("install ", "uninstall ", "install-multiple "))
                   for line in calls.splitlines())


def test_apk_hash_mismatch_is_negative():
    result, receipt, status, _, _, _ = _execute("mismatch")
    assert result.returncode == 5
    assert "apk_identity=MISMATCH_EXPECTED_APK" in receipt
    assert "FAIL_APK_HASH_MISMATCH" in status
    assert "apk_identity=MATCH_EXPECTED_APK\n" not in receipt


def test_missing_expected_hash_never_passes():
    result, receipt, status, calls, _, _ = _execute("missing")
    assert result.returncode == 4
    assert "TOKEN_VAZIO_EXPECTED_HASH_NOT_SUPPLIED" in receipt
    assert "HOLD_EXPECTED_HASH_NOT_SUPPLIED" in status
    # Input gate must precede all ADB commands, not merely reject after adb pull.
    assert not calls, "Missing expected digest must not access the device"


def test_bad_expected_hash_fails_before_device_access():
    result, receipt, status, calls, exists, _ = _execute("malformed")
    assert result.returncode == 2
    assert not exists and not calls


def test_multiple_devices_fail_closed():
    result, receipt, status, calls, _, _ = _execute(device_state="two")
    assert result.returncode == 3
    assert "EXPECT_ONE_AUTHORIZED_DEVICE" in status
    assert "shell" not in calls


def test_missing_base_apk_is_typed_gap():
    result, receipt, status, calls, _, _ = _execute(no_base=True)
    assert result.returncode == 3
    assert "TOKEN_VAZIO_PM_BASE_APK_ABSENT" in receipt
    assert "pull" not in calls


def test_split_package_fails_before_any_apk_pull():
    result, receipt, status, calls, _, _ = _execute(split_paths=True)
    assert result.returncode == 3
    assert "TOKEN_VAZIO_SPLIT_APKS_REQUIRE_FULL_MANIFEST" in receipt
    assert "ROUTE_STATE=BLOCKED SPLIT_APKS_REQUIRE_FULL_MANIFEST" in status
    assert "shell pm path org.rafaelia.rll.debug" in calls
    assert not any(line.startswith("pull ") for line in calls.splitlines())


def test_privacy_no_default_dumpsys_or_install():
    source = SCRIPT.read_text(encoding="utf-8")
    assert "dumpsys" not in source
    assert "adb install" not in source
    assert "adb uninstall" not in source
    assert "umask 077" in source
    assert '[ -e "$OUT" ]' in source
