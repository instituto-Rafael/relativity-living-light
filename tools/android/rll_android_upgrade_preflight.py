#!/usr/bin/env python3
"""Read-only Android upgrade safety check using authoritative Android SDK tools.

Requires Android SDK Build Tools 'apksigner' and 'aapt'. No device I/O,
keystore access, installation, uninstall or network. Signer rotation must be
reviewed separately; mismatched certificates are deliberately fail-closed.
"""
import hashlib
import json
from pathlib import Path
import re
import subprocess
import sys


class PreflightError(ValueError):
    pass


def _run(*argv):
    try:
        result = subprocess.run(argv, capture_output=True, text=True,
                                timeout=45, check=False)
    except (FileNotFoundError, OSError, subprocess.TimeoutExpired) as exc:
        raise PreflightError("SDK_TOOL_UNAVAILABLE_OR_TIMEOUT") from exc
    if result.returncode:
        raise PreflightError("SDK_CHECK_FAILED:" + argv[0])
    return result.stdout


def _identity(path):
    if not path.is_file() or path.stat().st_size == 0:
        raise PreflightError("APK_NOT_PRESENT_OR_EMPTY")
    apk = path.read_bytes()
    signature = _run("apksigner", "verify", "--verbose", "--print-certs", str(path))
    certs = re.findall(r"^Signer #\d+ certificate SHA-256 digest:\s*([0-9a-fA-F]{64})\s*$",
                       signature, re.MULTILINE)
    if len(certs) != 1:
        raise PreflightError("SIGNING_CERTIFICATE_ABSENT_OR_MULTIPLE_SIGNERS")
    badging = _run("aapt", "dump", "badging", str(path))
    pkg = re.search(r"^package:\s+name='([^']+)'\s+versionCode='([0-9]+)'", badging,
                    re.MULTILINE)
    if pkg is None:
        raise PreflightError("PACKAGE_VERSION_NOT_OBSERVED")
    return {"package": pkg.group(1), "version_code": int(pkg.group(2)),
            "certificate_sha256": certs[0].lower(),
            "apk_sha256": hashlib.sha256(apk).hexdigest()}


def compare(old_path, new_path):
    old = _identity(Path(old_path))
    new = _identity(Path(new_path))
    if old["package"] != new["package"]:
        state = "DIFFERENT_PACKAGE_SEPARATE_INSTALL_NOT_A_DATA_PRESERVING_UPGRADE"
    elif old["certificate_sha256"] != new["certificate_sha256"]:
        state = "BLOCKED_SIGNING_CONTINUITY_UNVERIFIED_ROTATION"
    elif new["version_code"] <= old["version_code"]:
        state = "BLOCKED_NONINCREASING_VERSION_CODE"
    else:
        state = "PASS_SCOPED_SAME_SIGNER_HIGHER_VERSION_DEVICE_NOT_TESTED"
    return {"state": state, "baseline": old, "candidate": new,
            "signature_rotation_lineage": "TOKEN_VAZIO_NOT_EVALUATED",
            "device_installation": "NOT_ATTEMPTED",
            "data_preservation": "NO_DEVICE_MUTATION", "claim_allowed": False}


def main(argv):
    if len(argv) != 3:
        print("usage: rll_android_upgrade_preflight.py installed-baseline.apk candidate.apk",
              file=sys.stderr)
        return 2
    try:
        report = compare(argv[1], argv[2])
    except PreflightError as exc:
        print(json.dumps({"state": "FAIL_CLOSED", "reason": str(exc)}), file=sys.stderr)
        return 2
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if report["state"].startswith("PASS_SCOPED_") else 3


if __name__ == "__main__":
    raise SystemExit(main(sys.argv))
