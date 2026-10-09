# RLL Android signing gate source-side correction — 2026-10-09

**Status:** `SOURCE_FALSIFIER_COMMITTED / EXACT_HEAD_CI_PENDING / claim_allowed=false`.

## Observed counterexample
At RLL `rll/lab` source blob `960c4bde04e527150890c31254db96e2cc25a0e8`, `.github/workflows/android-build.yml` contains four direct `if: ${{ secrets.* }}` expressions (keystore decode, release build, upload signed APK, upload signed AAB). GitHub's official Actions syntax documentation explicitly states `secrets` cannot be directly referenced in `if:` conditions.

References:
- https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax
- https://docs.github.com/en/actions/how-tos/write-workflows/choose-what-workflows-do/use-secrets

## Minimal correction
- Compute only **availability boolean** at job `env.RLL_RELEASE_SIGNING_AVAILABLE`, with complete four-secret presence AND rule. No secret values or their lengths are stored at job scope.
- Each of four signing steps checks `env.RLL_RELEASE_SIGNING_AVAILABLE == 'true'`. Unsigned debug/validation path remains unchanged.
- Actual keystore bytes are passed only to the decode step's environment, not interpolated into the shell script source. Passwords/alias remain step-scoped in release-build step.
- Delete runner-temp keystore material with `always()` (host runner cleanup; **not** freestanding L0).
- Static negative source tests enforce the four intended signing gates and prevent future direct secret references in `if`.

## Evidence boundary
This is a **documented unsupported Actions expression**, a reproducible source-side condition; it is not proof that every historical no-job Actions failure was caused by this condition. The four historical failures with empty jobs include workflows with unrelated triggers. No manual runs, keystore access, secret disclosure, credential creation, policy bypass, APK signing or physical Android validation occurred here.

F_ok=source-signing guard corrected on reversible feature branch after source check. F_gap=exact-head CI, historical run annotation, actual SDK/NDK build, Android physical runtime, artifact digests, license P0, service protections. F_next=consume exact-head Actions Python/source tests and inspect workflow interpretation; separately review other 3 workflows without attributing causality. Rollback=revert only workflow/test/doc successor. `claim_allowed=false`.
