# RLL Cross-Repository Entrelace Surgery — 2026-07-16

**Status:** `STRUCTURAL_PATCH / CLAIM_GATED / DRAFT_PR_REQUIRED`  
**Owner:** `instituto-Rafael/relativity-living-light`  
**Boundary:** no scientific superiority claim, no automatic cross-repository write, no private payload movement.

## 1. Surgical finding

The ecosystem already contained several bridges, but they were distributed across prose, session contracts and repository-local documents. The precise missing layer was not another general architecture: it was a machine-readable record that says, for each bridge:

```text
exact source + exact target + blob identity
+ what is proven + what is not proven
+ missing artifact + next action + rollback
```

The second urgent finding was temporal: the FASE17–20 graph preserved G4 as `TOKEN_VAZIO`, while FASE22 later quantified it. Replacing the old value would corrupt chronology; leaving it unqualified would corrupt the current reading. The repair is an overlay.

## 2. State of RLL at the cut

Current bounded evidence:

```text
Ωs0 median = 0.000386
Ωs0 UL95   = 0.00178
ln(B10)    = -6.190 ± 0.691
G4 systematic at posterior = 0.7214 Mpc
```

The currently analysed evidence favors ΛCDM. This result is preserved even though it is unfavorable to the additional RLL sector. `claim_allowed=false` remains correct because repository computation is not independent replication or peer review.

## 3. Five measured entrelaces

### 3.1 RLL ↔ RafPolimata

**Role:** method and formal evidence gates.  
**State:** `VERIFIED_LIMITED`.  
**Proven:** compatible promotion chain and responsibility split.  
**Not proven:** shared executable API or physical validation.  
**Next artifact:** one experiment manifest using stable equation IDs, validated on both sides.

### 3.2 RLL ↔ ChipQuantum

**Role:** runtime evidence, numerical error and benchmark custody.  
**State:** `VERIFIED_LIMITED`.  
**Proven:** compatible runtime-manifest fields.  
**Not proven:** imported artifact, cross-architecture equality, or physics validation.  
**Next artifact:** float64 reference + fixed-point run with tolerances, saturation and overflow counters.

### 3.3 RLL ↔ GAIA_phi

**Role:** claim ledger and pointer-index storage.  
**State:** `VERIFIED_LIMITED`.  
**Proven:** compatible ledger chain and gap vocabulary.  
**Not proven:** automatic ingestion or shared schema version.  
**Next artifact:** immutable pointer-only import receipt.

### 3.4 RLL ↔ Vectras

**Role:** Android/QEMU/device carrier.  
**State:** `BLOCKED`.  
**Proven:** documentation responsibility boundary and current `BETA_BLOCKED` status.  
**Not proven:** current APK, real-device smoke, QEMU boot, or RLL execution.  
**Next artifact:** APK hash manifest followed by real-device/QEMU smoke.

### 3.5 RLL ↔ Termux RAFCODEΦ

**Role:** current mobile runtime contract and historical-provenance target.  
**State:** `PARTIAL`.  
**Proven:** pinned package-source contract and ABI metadata; RLL provenance requirements.  
**Not proven:** that early RLL calculations ran in the current fork or on the declared phone.  
**Next artifact:** one original image/CSV linked to original command, environment, input/output hashes and timestamp.

## 4. G4 repair

### Historical truth

At the end of FASE20:

```text
G4 = TOKEN_VAZIO
```

### Current truth

At FASE22:

```text
G4 = VERIFIED_LIMITED
lifecycle = CLOSED_AS_QUANTIFIED_SYSTEMATIC
posterior systematic = 0.7214 Mpc
estimated impact on ln(B10) = 0.1–1.0
qualitative model comparison changed = false
```

### Residual limitation

```text
CAMB/RECFAST rd(Ωm, Ωb) at every MCMC point = TOKEN_VAZIO P1
```

Thus “G4 closed” means the unknown systematic was quantified. It does not mean the approximation was eliminated.

## 5. Files introduced

```text
knowledge_ecosystem/rll_cross_repo_entrelaces_v2.json
schemas/rll_cross_repo_entrelace.schema.json
tools/validate_rll_cross_repo_entrelaces.py
tests/test_rll_cross_repo_entrelaces.py
scripts/build_session_grafo_current_state_overlay.py
results/session_grafo_fase17_20/current_state_overlay.json
```

Files synchronized:

```text
results/session_grafo_fase17_20/session_manifest.json
results/session_grafo_fase17_20/gaps.jsonl
results/session_grafo_fase17_20/report.md
docs/audits/CROSS_REPO_RELATIONSHIP_REGISTRY.md
.github/workflows/validate-cross-repo-relationship-registry.yml
```

## 6. Priority queue

| Priority | Action | Exit evidence |
|---|---|---|
| P0 | Validate overlay and registry in existing workflow | JSON report + checksums + focused tests |
| P1 | Produce one ChipQuantum runtime artifact | source/binary hashes, flags, architecture, numerical comparison |
| P1 | Locate one original mobile RLL artifact | non-retroactive provenance manifest |
| P1 | Replace E&H offset by CAMB/RECFAST per MCMC point | rerun evidence and sensitivity report |
| P2 | Collect Vectras APK/device/QEMU evidence | APK hash + device metadata + smoke report |
| P2 | Define GAIA pointer-only import receipt | immutable pointer receipt and rejection test |

## 7. Rollback

- Close or revert the draft PR to remove the v2 registry layer.
- Preserve the FASE17–20 historical graph and all negative results.
- If the overlay fails validation, return the current reading to `BLOCKED`, not to an invented state.
- No external repository is changed by this PR.

## 8. R₃

```text
F_ok   = exact bridges and G4 temporal transition are now machine-addressable
F_gap  = runtime artifact, historical mobile provenance and per-step CAMB remain absent
F_next = validate this PR, then implement exactly one bounded runtime evidence artifact
```
