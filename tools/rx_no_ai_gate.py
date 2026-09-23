#!/usr/bin/env python3
"""Fail-closed no-AI runtime gate for the active Rx development chain."""

from __future__ import annotations

import ast
import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_ROOTS = {
    "torch",
    "tensorflow",
    "jax",
    "jaxlib",
    "transformers",
    "openai",
    "anthropic",
    "sklearn",
    "keras",
    "onnxruntime",
    "langchain",
    "llama_cpp",
    "diffusers",
    "accelerate",
    "pytorch_lightning",
    "sentence_transformers",
}

active_files = sorted((ROOT / "rx").glob("*.py")) + [
    ROOT / "validacao_real" / "run_rx_pipeline.py",
    ROOT / "validacao_real" / "run_rx_multiprobe.py",
    ROOT / "validacao_real" / "compute_validation_stdlib.py",
    ROOT / "data" / "pipelines" / "structure_d" / "joint_real_likelihood_rx.py",
    ROOT / "tools" / "rx_selftest.py",
    ROOT / "tools" / "rx_sound_horizon_selftest.py",
    ROOT / "tools" / "rx_freestanding65_parity.py",
    ROOT / "tools" / "rx_semantic_parity.py",
    ROOT / "tools" / "rx_dependency_audit.py",
    ROOT / "tools" / "rx_dependency_migration_plan.py",
    ROOT / "tools" / "rx_development_gate.py",
    ROOT / "tools" / "rx_zero_dependency_gate.py",
    ROOT / "internal" / "governance" / "development_guard.py",
    ROOT / "tools" / "validate_rll_development_governance.py",
    ROOT / "tools" / "rll_security_surface_audit.py",
    ROOT / "tools" / "validate_calc_data_stdlib_migration.py",
    ROOT / "scripts" / "calc_data.py",
    ROOT / "tools" / "validate_watch_config_stdlib_migration.py",
    ROOT / "scripts" / "validate_watch_config.py",
    ROOT / "tools" / "validate_rll_credential_authority.py",
    ROOT / "tools" / "validate_credential_authority_stdlib_migration.py",
    ROOT / "scripts" / "import_data.py",
    ROOT / "scripts" / "fetch_public_astronomy_catalog_samples.py",
    ROOT / "scripts" / "fetch_real_sources.py",
    ROOT / "tools" / "validate_rx_http_migration.py",
    ROOT / "tools" / "validate_executable_entrypoint_authority_registry.py",
]

violations = []
scanned = []

for path in active_files:
    if not path.exists():
        violations.append({"path": str(path.relative_to(ROOT)), "reason": "missing_active_file"})
        continue
    rel = str(path.relative_to(ROOT))
    scanned.append(rel)
    tree = ast.parse(path.read_text(encoding="utf-8"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imports.add(node.module.split(".")[0])
    bad = sorted(imports & FORBIDDEN_ROOTS)
    if bad:
        violations.append({"path": rel, "reason": "forbidden_ai_import", "modules": bad})

payload = {
    "schema": "rll.rx.no_ai_runtime_gate.v1",
    "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "state": "PASS" if not violations else "FAIL",
    "policy": {
        "training": False,
        "ai_runtime": False,
        "forbidden_import_roots": sorted(FORBIDDEN_ROOTS),
        "mathematical_optimization_allowed": True,
        "deterministic_programs_allowed": True,
    },
    "scanned_files": scanned,
    "violations": violations,
    "claim_allowed": False,
}

out = ROOT / "results" / "rx_no_ai_runtime_gate.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if violations:
    print("RX_NO_AI_RUNTIME_GATE=FAIL")
    for row in violations:
        print(row)
    raise SystemExit(1)

print("RX_NO_AI_RUNTIME_GATE=PASS")
print("training=False ai_runtime=False mathematical_optimization_allowed=True")
print("scanned_files=", len(scanned))
print("wrote", out.relative_to(ROOT))
