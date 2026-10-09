"""Source-only GitHub Actions policy falsifiers: no secret access is performed."""
from pathlib import Path
import re

WORKFLOW=Path(".github/workflows/android-build.yml")

def test_android_release_guards_never_use_secret_context_in_if():
    source=WORKFLOW.read_text(encoding="utf-8")
    if_lines=re.findall(r"^\s*if:\s*.*$",source,re.MULTILINE)
    assert len([line for line in if_lines if "RLL_RELEASE_SIGNING_AVAILABLE" in line])==4
    assert all("secrets." not in line for line in if_lines)
    assert source.count("if: ${{ env.RLL_RELEASE_SIGNING_AVAILABLE == 'true' }}")==4

def test_android_secret_presence_boolean_and_step_owned_keystore():
    source=WORKFLOW.read_text(encoding="utf-8")
    assert "RLL_RELEASE_SIGNING_AVAILABLE: ${{ secrets.RLL_RELEASE_KEYSTORE_BASE64 != ''" in source
    assert "RLL_RELEASE_KEYSTORE_BASE64: ${{ secrets.RLL_RELEASE_KEYSTORE_BASE64 }}" in source
    assert """printf '%s' "$RLL_RELEASE_KEYSTORE_BASE64" """ in source
    assert """printf '%s' "${{ secrets.RLL_RELEASE_KEYSTORE_BASE64 }}" """ not in source
    assert 'rm -f "$RUNNER_TEMP/rll-signing/release.jks"' in source

def test_release_unsigned_lanes_preserved():
    source=WORKFLOW.read_text(encoding="utf-8")
    assert ":app:assembleDebug :app:assembleValidationUnsigned" in source
    assert "if-no-files-found: error" in source
    assert "contents: read" in source
