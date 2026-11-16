# RLL Dashboard PR #1213 — Gradle dependency-submission preflight closure S2 (2026-11-16)

- mu_id: MU-RLL-PR1213-GRADLE-WRAPPER-S2-20261116
- parent: 97a1494560d580e44f88b7c0cad05a2465375a6a
- source: work/rll-main-gradle-wrapper-binary-hotfix-20261116-v1@ccc401ddc2ffc0392fdc1260b33e8b276e2a2d87
- source proof: GitHub Gradle automated dependency submission run https://github.com/instituto-Rafael/relativity-living-light/actions/runs/43821138399 completed SUCCESS after Unix classpath fix.
- bug: Gradle submission on #1213 fails because target (based on Dependabot #1212) lacked wrapper JAR; main old Unix and Windows launchers attempted `java -jar` on an unexecutable wrapper manifest.
- repair: import exact existing Git blobs + modes for Gradle wrapper JAR, Gradle 8.10.2 distribution SHA-256 pin, Unix and Windows classpath launchers, bootstrap diagnostic, fail-closed regression test.
- settings.gradle and build.gradle source/target blobs confirmed identical; no build model policy change.
- ownership: target only branch fix/pr1212-dashboard-toolchain-gates-20261115, PR #1213 base Dependabot branch; do not merge main, disable gate, alter secrets or rewrite existing refs.
- status: WRITTEN_EXACT_BLOBS / CI_NOT_RUN_ON_NEW_HEAD / claim_allowed=false.
- rollback: review successor/revert without force, preserve bot branch updates and previous receipts.
