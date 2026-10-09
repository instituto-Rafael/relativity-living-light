#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
out="$(mktemp -d)"
trap 'rm -rf "$out"' EXIT HUP INT TERM
javac -encoding UTF-8 -d "$out" \
  app/src/main/java/org/rafaelia/rll/FormulaEngine.java \
  app/src/main/java/org/rafaelia/rll/RealBaoEngine.java \
  app/src/main/java/org/rafaelia/rll/CanonicalOmegaBundle.java \
  app/src/test/java/org/rafaelia/rll/CanonicalOmegaBundleSelfTest.java
java -cp "$out" org.rafaelia.rll.CanonicalOmegaBundleSelfTest
