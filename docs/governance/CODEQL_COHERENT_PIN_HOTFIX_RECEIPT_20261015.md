# QREL/RLL provider hotfix — coherent CodeQL pin across workflows · 2026-10-15

**Purpose:** Fix a reproduced provider CI config error; no change to scientific model, runtime or other security gates.

## Evidence

PR #1110 (`analyze` only), head `d09f44f032c9ab6c70555c4b7c0ec9feb3847613`, CodeQL Platform Assurance run `38327924028`, job `115070812165` logged: `Loaded a configuration file for version '4.38.2', but running version '4.38.3'. All steps ... must use the same version`.

PR #1109 (`init` only), head `f663f12522e948bc89c39e5b2708182689454360`, is the symmetric dependency half. Each separate PR changed one action only, which cannot be tested alone against the older counterpart. Both are held open; this is a combined successor on `rll/lab`, not a merge of those unvalidated branches.

## Minimal source delta

Both `.github/workflows/github-platform-assurance.yml` and `.github/workflows/github-platform-assurance-v2.yml` pin `github/codeql-action/init` **and** `github/codeql-action/analyze` to immutable SHA `24c54180a607b1449ed407dd24f251e4e9147c8d` (CodeQL Action v4.38.3). Exactly four original references to `2892aa5e19bbd11bc0cff5427e3b750a04d9e3c2` updated, no other workflow source rewritten.

## Additional nonconflated blockers

The same #1110 run `38327924122` deep YAML audit scanned 253 YAMLs / 119 workflows, syntax_failures=0, severity ERROR=2 / HIGH=82 / MEDIUM=241 / LOW=136. The two severity ERROR findings must be recovered from its emitted audit artifact and classified independently; **do not bypass `--fail-on error`**. CodeQL config mismatch is one confirmed cause but not proven to explain these two YAML findings. Provider protection / branch rules, independent reviewer and original audit remain separate gates.

## Falsifier / source gate

On the exact hotfix HEAD:

- Assert each of two workflow files has exactly one pinned `init` and one pinned `analyze` with the **same exact ref**.
- Re-run CodeQL V1/V2 actions and python and YAML Deep Audit; reject if any check fails or if SHA changed.
- Check results of `Dependency review` and `External repository settings`; a prior success at another SHA does not prove this HEAD.
- Compare diff with both Dependabot proposals to ensure no unauthorized settings, secrets, removed checks or downgrade.

## Rollback

No release/main changes. To reverse this PR, close it without merging; original `rll/lab` retains consistent older v4.38.2. If merged in future with explicit provider approval, revert the combined two-file change together, not one step independently. Never delete the original failure receipts.

## R3

F_ok: real CodeQL log points to mismatched pinned versions; corrective source patch in dedicated branch. F_gap: new CI exact SHA; 2 YAML audit ERROR source findings; provider security/enforcement and independent review. F_next: verify CodeQL job logs and full YAML report, then decide whether promotion is allowed. `claim_allowed=false`; `NO_MERGE` pending gates.
