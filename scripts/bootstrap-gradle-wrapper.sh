#!/usr/bin/env bash
set -euo pipefail

ROOT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$ROOT_DIR"

WRAPPER_VERSION="${RLL_GRADLE_WRAPPER_VERSION:-8.10.2}"
WRAPPER_JAR="gradle/wrapper/gradle-wrapper.jar"

if [[ -f "$WRAPPER_JAR" ]]; then
  echo "Gradle Wrapper JAR already exists: $WRAPPER_JAR"
  exit 0
fi

if ! command -v gradle >/dev/null 2>&1; then
  cat >&2 <<MSG
Gradle executable not found and $WRAPPER_JAR is missing.
Restore the verified wrapper JAR from version control, or run this script after installing the pinned Gradle version.
MSG
  exit 127
fi

echo "Generating $WRAPPER_JAR with Gradle $WRAPPER_VERSION"
gradle --no-daemon wrapper --gradle-version "$WRAPPER_VERSION"
