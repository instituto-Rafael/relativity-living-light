#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
d="$(mktemp -d)"
trap 'rm -rf "$d"' EXIT HUP INT TERM
javac -encoding UTF-8 -d "$d" \
  app/src/main/java/org/rafaelia/rll/FormulaEngine.java \
  app/src/test/java/org/rafaelia/rll/FormulaEngineSelfTest.java
java -cp "$d" org.rafaelia.rll.FormulaEngineSelfTest
