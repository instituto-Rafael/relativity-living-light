"""SDK output simulations; never installs APKs or accesses signing secrets."""
from pathlib import Path
import sys
from unittest.mock import patch

import pytest

sys.path.insert(0, str(Path("tools/android").resolve()))
import rll_android_upgrade_preflight as preflight


def _case(old_pkg="org.rafaelia.rll.debug", new_pkg="org.rafaelia.rll.debug",
          old_code=7, new_code=8, old_cert="a" * 64, new_cert="b" * 64):
    def fake_identity(path):
        if str(path).endswith("old.apk"):
            return dict(package=old_pkg, version_code=old_code,
                        certificate_sha256=old_cert, apk_sha256="1" * 64)
        return dict(package=new_pkg, version_code=new_code,
                    certificate_sha256=new_cert, apk_sha256="2" * 64)
    with patch.object(preflight, "_identity", side_effect=fake_identity):
        return preflight.compare("old.apk", "new.apk")


def test_v07_v08_different_signers_block_without_device_io():
    r = _case()
    assert r["state"] == "BLOCKED_SIGNING_CONTINUITY_UNVERIFIED_ROTATION"
    assert r["device_installation"] == "NOT_ATTEMPTED"
    assert r["signature_rotation_lineage"] == "TOKEN_VAZIO_NOT_EVALUATED"
    assert not r["claim_allowed"]


def test_same_signer_version_increment_is_only_scoped():
    assert _case(new_cert="a" * 64)["state"].startswith("PASS_SCOPED_")


def test_downgrade_not_promoted():
    assert _case(new_code=6, new_cert="a" * 64)["state"] == "BLOCKED_NONINCREASING_VERSION_CODE"


def test_separate_package_not_promoted_as_update():
    assert _case(new_pkg="org.rafaelia.rll.validation")["state"].startswith("DIFFERENT_PACKAGE")


def test_sdk_missing_is_typed_and_fail_closed():
    with patch.object(preflight.subprocess, "run", side_effect=FileNotFoundError):
        with pytest.raises(preflight.PreflightError, match="SDK_TOOL_UNAVAILABLE"):
            preflight._run("apksigner", "verify", "unused")


def test_invalid_sdk_signature_result_is_rejected(tmp_path):
    file = tmp_path / "old.apk"
    file.write_bytes(b"not actually an apk")
    with patch.object(preflight, "_run", side_effect=[
        "Signer #1 certificate SHA-256 digest: garbage\n",
        "package: name='org.rafaelia.rll.debug' versionCode='7'",
    ]):
        with pytest.raises(preflight.PreflightError, match="SIGNING_CERTIFICATE"):
            preflight._identity(file)


def test_sdk_valid_cert_and_package_parse(tmp_path):
    file = tmp_path / "old.apk"
    file.write_bytes(b"synthetic non-APK fixture")
    with patch.object(preflight, "_run", side_effect=[
        "Signer #1 certificate SHA-256 digest: " + "a" * 64 + "\n",
        "package: name='org.rafaelia.rll.debug' versionCode='7' versionName='0.7.0-debug'\n",
    ]):
        r = preflight._identity(file)
    assert r["package"] == "org.rafaelia.rll.debug" and r["version_code"] == 7
    assert r["certificate_sha256"] == "a" * 64


def test_no_install_uninstall_or_signing_key_access():
    src = Path("tools/android/rll_android_upgrade_preflight.py").read_text()
    for forbidden in ("adb install", "adb uninstall", "RLL_RELEASE_KEYSTORE_BASE64", "keytool"):
        assert forbidden not in src
