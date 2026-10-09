#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
out="$(mktemp -d)"
trap 'rm -rf "$out"' EXIT HUP INT TERM
javac -encoding UTF-8 -d "$out" \
  app/src/main/java/org/rafaelia/rll/FormulaEngine.java \
  app/src/main/java/org/rafaelia/rll/RealBaoEngine.java \
  app/src/main/java/org/rafaelia/rll/CanonicalOmegaBundle.java \
  app/src/main/java/org/rafaelia/rll/OmegaScientificChecks.java \
  app/src/main/java/org/rafaelia/rll/OmegaCrossModelComparison.java \
  app/src/main/java/org/rafaelia/rll/OmegaBinaryInspector.java \
  app/src/test/java/org/rafaelia/rll/OmegaCrossModelComparisonSelfTest.java \
  app/src/test/java/org/rafaelia/rll/OmegaBinaryInspectorSelfTest.java \
  app/src/test/java/org/rafaelia/rll/OmegaScientificChecksSelfTest.java \
  app/src/test/java/org/rafaelia/rll/CanonicalOmegaBundleSelfTest.java
java -cp "$out" org.rafaelia.rll.CanonicalOmegaBundleSelfTest

java -cp "$out" org.rafaelia.rll.OmegaScientificChecksSelfTest

java -cp "$out" org.rafaelia.rll.OmegaCrossModelComparisonSelfTest
java -cp "$out" org.rafaelia.rll.OmegaBinaryInspectorSelfTest
