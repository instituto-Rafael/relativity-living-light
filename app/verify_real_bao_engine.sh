#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
tmp="$(mktemp -d)"
trap 'rm -rf "$tmp"' EXIT HUP INT TERM
javac -encoding UTF-8 -d "$tmp" \
  app/src/main/java/org/rafaelia/rll/FormulaEngine.java \
  app/src/main/java/org/rafaelia/rll/RealBaoEngine.java \
  app/src/test/java/org/rafaelia/rll/RealBaoEngineSelfTest.java
java -cp "$tmp" org.rafaelia.rll.RealBaoEngineSelfTest
