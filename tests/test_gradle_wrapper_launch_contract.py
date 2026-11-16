"""Regression checks for the official Gradle Wrapper invocation.

The wrapper JAR is a classpath dependency, not an executable -jar archive.
These are fail-closed syntax, provenance and source-level launch contracts;
the Android Build workflow provides the actual JVM/Gradle execution evidence.
"""
from __future__ import annotations

import hashlib
import subprocess
import zipfile
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
SCRIPT = ROOT / "gradlew"
JAR = ROOT / "gradle/wrapper/gradle-wrapper.jar"
PROPS = ROOT / "gradle/wrapper/gradle-wrapper.properties"
EXPECTED_WRAPPER_SHA256 = (
    "2db75c40782f5e8ba1fc278a5574bab070adccb2d21ca5a6e5ed840888448046"
)


def test_gradlew_launches_main_class_from_jar_classpath() -> None:
    source = SCRIPT.read_text(encoding="utf-8")
    assert "CLASSPATH=$APP_HOME/gradle/wrapper/gradle-wrapper.jar" in source
    assert '-classpath "$CLASSPATH"' in source
    assert "org.gradle.wrapper.GradleWrapperMain" in source
    assert '-jar "$APP_HOME/gradle/wrapper/gradle-wrapper.jar"' not in source


def test_wrapper_jar_is_validated_and_contains_entrypoint_class() -> None:
    assert JAR.is_file(), "versioned wrapper JAR missing from current candidate"
    digest = hashlib.sha256(JAR.read_bytes()).hexdigest()
    assert digest == EXPECTED_WRAPPER_SHA256, "wrapper binary provenance drift"
    with zipfile.ZipFile(JAR) as jar:
        assert "org/gradle/wrapper/GradleWrapperMain.class" in jar.namelist()


def test_gradle_distribution_pinned_without_runtime_downgrade() -> None:
    content = PROPS.read_text(encoding="utf-8")
    assert "gradle-8.10.2-bin.zip" in content
    assert "distributionSha256Sum=31c55713e40233a8303827ceb42ca48a47267a0ad4bab9177123121e71524c26" in content
    source = SCRIPT.read_text(encoding="utf-8")
    assert "exec \"$JAVACMD\" \"$@\"" in source


def test_posix_wrapper_shell_syntax() -> None:
    subprocess.run(["sh", "-n", str(SCRIPT)], cwd=ROOT, check=True)
