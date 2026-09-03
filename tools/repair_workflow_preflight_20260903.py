#!/usr/bin/env python3
"""Deterministic, branch-only repair for GitHub Actions preflight failures.

Scope is intentionally narrow:
- remove the unsupported top-level x-canonical-real-data-policy key from 20 workflows;
- move Android release-secret presence checks out of `if:` and into a step output;
- move the Dashboard JavaScript ternary out of GitHub expression syntax;
- write a regression test and append-only governance receipt.

This script never changes provider settings, secrets, default branches, or scientific claims.
"""
from __future__ import annotations

import json
import re
import subprocess
from pathlib import Path

BASE_MAIN_SHA = "2e28abc33f5bd720dc036dbcaa6efa1967ce53c6"
ROOT = Path(__file__).resolve().parents[1]
WORKFLOWS = ROOT / ".github" / "workflows"

X_CANONICAL_PATHS = [
    "validate-sequence-metrics.yml",
    "repo-real-inventory.yml",
    "dense-feature-matrix.yml",
    "import-data.yml",
    "six-sigma-real-data-controls.yml",
    "desi-dr2-bao-validation.yml",
    "orbital-state-vector-v2.yml",
    "real-seed-ingestion-plan.yml",
    "real-seed-validation-v0.yml",
    "claim-boundary-quality-gates.yml",
    "validacao_real.yml",
    "validate-real-dataset-variance-registry.yml",
    "real-data-bootstrap-validation.yml",
    "real-data-contract-ci.yml",
    "rll-book-data-pipeline.yml",
    "orbital-shape-angular-momentum-validation.yml",
    "canonical-route-artifacts.yml",
    "START_MANUAL_HERE.yml",
    "academic-parameter-governance.yml",
    "rll-real-data-orchestrator.yml",
]

DIRECT_SECRET_IF = (
    "        if: ${{ secrets.RLL_RELEASE_KEYSTORE_BASE64 != '' && "
    "secrets.RLL_RELEASE_STORE_PASSWORD != '' && secrets.RLL_RELEASE_KEY_ALIAS != '' && "
    "secrets.RLL_RELEASE_KEY_PASSWORD != '' }}"
)
SAFE_OUTPUT_IF = "        if: steps.release-signing-inputs.outputs.available == 'true'"


def read(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def write_if_changed(path: Path, content: str) -> bool:
    old = read(path)
    if old == content:
        return False
    path.write_text(content, encoding="utf-8")
    return True


def repair_x_canonical() -> list[str]:
    changed: list[str] = []
    for name in X_CANONICAL_PATHS:
        path = WORKFLOWS / name
        text = read(path)
        lines = text.splitlines(keepends=True)
        hits = [line for line in lines if line.startswith("x-canonical-real-data-policy:")]
        if len(hits) != 1:
            raise SystemExit(f"{name}: expected exactly one top-level x-canonical key, found {len(hits)}")
        new = "".join(line for line in lines if not line.startswith("x-canonical-real-data-policy:"))
        if write_if_changed(path, new):
            changed.append(str(path.relative_to(ROOT)))
    return changed


def repair_android() -> str:
    path = WORKFLOWS / "android-build.yml"
    text = read(path)
    if text.count(DIRECT_SECRET_IF) != 4:
        raise SystemExit(f"android-build.yml: expected 4 direct secret if expressions, found {text.count(DIRECT_SECRET_IF)}")
    text = text.replace(DIRECT_SECRET_IF, SAFE_OUTPUT_IF)

    decode_marker = (
        "      - name: Decode release keystore\n"
        + SAFE_OUTPUT_IF
        + "\n        run: |\n"
    )
    if text.count(decode_marker) != 1:
        raise SystemExit("android-build.yml: decode marker not unique")

    preflight = """      - name: Check release signing inputs
        id: release-signing-inputs
        env:
          RLL_RELEASE_KEYSTORE_BASE64: ${{ secrets.RLL_RELEASE_KEYSTORE_BASE64 }}
          RLL_RELEASE_STORE_PASSWORD: ${{ secrets.RLL_RELEASE_STORE_PASSWORD }}
          RLL_RELEASE_KEY_ALIAS: ${{ secrets.RLL_RELEASE_KEY_ALIAS }}
          RLL_RELEASE_KEY_PASSWORD: ${{ secrets.RLL_RELEASE_KEY_PASSWORD }}
        run: |
          if [ -n "$RLL_RELEASE_KEYSTORE_BASE64" ] && \
             [ -n "$RLL_RELEASE_STORE_PASSWORD" ] && \
             [ -n "$RLL_RELEASE_KEY_ALIAS" ] && \
             [ -n "$RLL_RELEASE_KEY_PASSWORD" ]; then
            echo "available=true" >> "$GITHUB_OUTPUT"
          else
            echo "available=false" >> "$GITHUB_OUTPUT"
          fi

"""
    decode_replacement = (
        preflight
        + "      - name: Decode release keystore\n"
        + SAFE_OUTPUT_IF
        + "\n        env:\n"
        + "          RLL_RELEASE_KEYSTORE_BASE64: ${{ secrets.RLL_RELEASE_KEYSTORE_BASE64 }}\n"
        + "        run: |\n"
    )
    text = text.replace(decode_marker, decode_replacement)
    old_printf = "          printf '%s' \"${{ secrets.RLL_RELEASE_KEYSTORE_BASE64 }}\" | base64 --decode > \"$RUNNER_TEMP/rll-signing/release.jks\""
    new_printf = "          printf '%s' \"$RLL_RELEASE_KEYSTORE_BASE64\" | base64 --decode > \"$RUNNER_TEMP/rll-signing/release.jks\""
    if text.count(old_printf) != 1:
        raise SystemExit("android-build.yml: expected one direct keystore interpolation")
    text = text.replace(old_printf, new_printf)
    write_if_changed(path, text)
    return str(path.relative_to(ROOT))


def repair_dashboard() -> str:
    path = WORKFLOWS / "dashboard-ux-compilation.yml"
    text = read(path)
    bad = "${{ job.status === 'success' ? '✅ Compilation passed!' : '❌ Compilation failed' }}"
    if text.count(bad) != 1:
        raise SystemExit(f"dashboard workflow: expected one invalid ternary, found {text.count(bad)}")
    anchor = "            const status = context.payload.pull_request ? 'pending' : 'success';\n"
    if text.count(anchor) != 1:
        raise SystemExit("dashboard workflow: github-script anchor not unique")
    js = (
        anchor
        + "            const compile = '${{ needs.compile-ux.result }}';\n"
        + "            const tests = '${{ needs.test-ux.result }}';\n"
        + "            const gates = '${{ needs.quality-gates.result }}';\n"
        + "            const statusText = [compile, tests, gates].every(x => x === 'success')\n"
        + "              ? '✅ Compilation passed!'\n"
        + "              : '❌ Compilation failed';\n"
    )
    text = text.replace(anchor, js).replace(bad, "${statusText}")
    write_if_changed(path, text)
    return str(path.relative_to(ROOT))


def write_regression_test() -> str:
    path = ROOT / "tests" / "test_workflow_preflight_static.py"
    content = '''from pathlib import Path\nimport re\n\nROOT = Path(__file__).resolve().parents[1]\nWORKFLOWS = ROOT / ".github" / "workflows"\n\n\ndef workflow_texts():\n    for path in sorted(WORKFLOWS.glob("*.y*ml")):\n        yield path, path.read_text(encoding="utf-8")\n\n\ndef test_no_unsupported_top_level_x_canonical_policy():\n    offenders = []\n    for path, text in workflow_texts():\n        if re.search(r"(?m)^x-canonical-real-data-policy:", text):\n            offenders.append(path.name)\n    assert offenders == []\n\n\ndef test_no_secrets_context_directly_in_if_expression():\n    offenders = []\n    for path, text in workflow_texts():\n        if re.search(r"(?m)^\\s*if:\\s*\\$\\{\\{[^}]*\\bsecrets\\.", text):\n            offenders.append(path.name)\n    assert offenders == []\n\n\ndef test_no_javascript_ternary_inside_github_expression():\n    offenders = []\n    pattern = re.compile(r"\\$\\{\\{[^}\\n]*\\?[^}\\n]*:[^}\\n]*\\}\\}")\n    for path, text in workflow_texts():\n        if pattern.search(text):\n            offenders.append(path.name)\n    assert offenders == []\n'''
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")
    return str(path.relative_to(ROOT))


def validate_static() -> dict:
    all_text = {p.name: read(p) for p in sorted(WORKFLOWS.glob("*.y*ml"))}
    x = [n for n, t in all_text.items() if re.search(r"(?m)^x-canonical-real-data-policy:", t)]
    secret_if = [n for n, t in all_text.items() if re.search(r"(?m)^\s*if:\s*\$\{\{[^}]*\bsecrets\.", t)]
    ternary = [n for n, t in all_text.items() if re.search(r"\$\{\{[^}\n]*\?[^}\n]*:[^}\n]*\}\}", t)]
    if x or secret_if or ternary:
        raise SystemExit(f"static preflight failed: x={x}, secret_if={secret_if}, ternary={ternary}")
    subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
    return {
        "top_level_x_canonical_remaining": x,
        "direct_secrets_in_if_remaining": secret_if,
        "github_expression_ternary_remaining": ternary,
    }


def write_receipt(changed: list[str], static: dict) -> str:
    path = ROOT / "data" / "governance" / "rll_workflow_preflight_repair_20260903.v1.json"
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = {
        "schema": "rll.workflow_preflight_repair.v1",
        "observed_date": "2026-09-03",
        "base_main_sha": BASE_MAIN_SHA,
        "historical_pr802_root_cause": "ROOT_CAUSE_OBSERVED_WORKFLOW_INVENTORY_DRIFT_82_TO_83",
        "current_main_python_tests": "PASS_OBSERVED_BEFORE_REPAIR",
        "current_zero_job_failure_decomposition": {
            "total": 22,
            "unsupported_top_level_x_canonical": 20,
            "android_direct_secrets_in_if": 1,
            "dashboard_github_expression_js_ternary": 1,
        },
        "repair": {
            "changed_paths": sorted(changed),
            "x_canonical_policy_semantics_preserved_by": [
                "workflow canonical-policy comments",
                "CANONICAL_REAL_DATA_WORKFLOW env",
                "CLAIM_BOUNDARY env/artifacts",
            ],
            "android_secret_values_logged": False,
            "provider_settings_changed": False,
            "secrets_changed": False,
            "default_branch_changed": False,
        },
        "static_post_repair": static,
        "verification_state": "IMPLEMENTED_ON_AUDIT_BRANCH_PENDING_PROVIDER_RUN_EVIDENCE",
        "claim_allowed": False,
        "next_verifiable_action": "Open draft PR and require formerly zero-job workflows to create jobs; classify each resulting job outcome separately from parser/preflight repair.",
        "invariants": [
            "TOKEN_VAZIO != PASS",
            "WORKFLOW_PARSES != JOB_PASSES != SCIENTIFIC_CLAIM",
            "VISÃO != ARTEFATO != EXECUÇÃO != EVIDÊNCIA != CLAIM",
        ],
    }
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    return str(path.relative_to(ROOT))


def main() -> None:
    changed = repair_x_canonical()
    changed.append(repair_android())
    changed.append(repair_dashboard())
    changed.append(write_regression_test())
    static = validate_static()
    changed.append(write_receipt(changed, static))
    subprocess.run(["python", "-m", "pytest", "-q", "tests/test_workflow_preflight_static.py"], cwd=ROOT, check=True)
    print(json.dumps({"status": "PASS_LOCAL_REPAIR", "changed": sorted(changed), "static": static}, indent=2))


if __name__ == "__main__":
    main()
