# RLL Authorial Science Fabric V1

Status: `IMPLEMENTED_UNTESTED_CI` · `claim_allowed=false`

This directory gives RLL one low-friction service boundary for scientific source custody, build/measurement adapters and the existing freestanding core.

## Separation that must not collapse

```text
SOURCE -> ARTIFACT -> EXECUTION -> EVIDENCE -> CLAIM
           |
           +-> factory/adapters: Python stdlib, CI, NDK, JNI, SDK, R8, ART/JIT
                               |
                               +-> never a runtime dependency of the freestanding ELF
```

The canonical freestanding computation remains under `core/lowlevel_runtime`. This fabric does not replace it and does not relabel Android userspace as bare metal.

## Directory contract

- `fabric.v1.json` — typed registry of execution/factory/evidence lanes.
- `manifests/` — source manifests. URLs, authority, rights state, byte bounds and expected SHA-256 live here.
- `tools/rll_authorial_ingress.py` — stdlib-only acquisition/custody tool.
- `.github/workflows/rll-authorial-science-fabric-v1.yml` — CI static gate plus manual network materialization.
- `data/governance/RLL_CAPABILITY_SECRET_ROUTER_V1.json` — bounded PAT aliases and non-destructive rules.

Downloaded PDFs, images and datasets are not committed automatically. A manual acquisition run writes them to an ephemeral CI directory and publishes a GitHub Actions artifact together with a receipt. A hash learned for a previously unpinned source is `OBSERVED_UNPINNED`, not `PASS_PINNED`; promotion requires a reviewed successor manifest.

## Credential profiles

Canonical profiles are:

- `PAT_ACTIONS` -> `pat_actions`
- `PAT_AGENTS` -> `pat_agents`
- `PAT_ENV` -> `pat_env`
- `PAT_ENVIRONMENTS` -> `pat_environments`

`PAT_ENVIOREMENTS` is retained only as a legacy typo fallback for the last profile. Secret values are never printed, stored, hashed or compared. Whether these names contain the same PAT value is provider-side state and remains `TOKEN_VAZIO` here.

V1 credentialed acquisition is deliberately narrower than the PAT's possible provider permissions: **GET-only GitHub Contents API**. No push, POST, PUT, PATCH, DELETE, ref deletion or force-push is implemented.

## Internet/source model

Public HTTPS sources need no PAT. Credential profiles are for private/cross-repository GitHub source custody only. Each materialized byte stream gets SHA-256, byte count, authority and rights state in the receipt.

For dynamic/unpinned public sources, use `--allow-unpinned` only for discovery. The next reviewed delta should pin the observed digest if the source is appropriate and legally usable.

## Voynich seed

`manifests/voynich_geometry.discovery.v1.json` starts the angular/graph experiment from the Beinecke MS 408 catalog record. It intentionally does **not** claim a high-resolution image endpoint, image rights, folio hashes or a decipherment. Those unresolved items remain `TOKEN_VAZIO` until resolved from the primary collection source.

## Freestanding meaning

`freestanding_native` means the execution core can be built and run without libc, heap allocation, Python/JVM/Android runtime and external native libraries. Compiler/linker/CI are factory tools, not runtime dependencies. NDK/JNI/SDK/R8/ART lanes may benchmark or bridge the same mathematics but do not redefine the core.

## Success criterion V1

1. static manifest audit PASS;
2. stdlib unit tests PASS;
3. credential-bearing jobs manual-only and non-destructive;
4. manual materialization emits artifact + receipt without secret material;
5. pinned source bytes must match SHA-256 exactly;
6. scientific claims remain disabled until a separate evidence gate exists.

Rollback: close/revert only this feature branch/PR. No history rewrite and no deletion of prior receipts.
