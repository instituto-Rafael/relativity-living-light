"""Fail-closed Gradle wrapper source checks (stdlib only; no network)."""
import re
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
WRAPPER = ROOT / "gradle/wrapper/gradle-wrapper.jar"
PROPERTIES = ROOT / "gradle/wrapper/gradle-wrapper.properties"


def test_gradle_wrapper_binary_is_tracked_and_executable_zip():
    assert WRAPPER.is_file(), "Gradle wrapper JAR must be versioned; do not hide missing runtime"
    assert WRAPPER.stat().st_size > 1024
    with zipfile.ZipFile(WRAPPER) as archive:
        assert archive.testzip() is None
        assert "org/gradle/wrapper/GradleWrapperMain.class" in archive.namelist()


def test_gradle_8102_distribution_has_explicit_hash_pin():
    data = PROPERTIES.read_text(encoding="utf-8")
    assert "gradle-8.10.2-bin.zip" in data
    matches = re.findall(r"^distributionSha256Sum=([0-9a-f]{64})$", data, re.M)
    assert matches == ["31c55713e40233a8303827ceb42ca48a47267a0ad4bab9177123121e71524c26"]
