#!/usr/bin/env python3
"""Fail-closed zero-third-party gate for the active Rx/RLL runtime surface."""

from __future__ import annotations

import ast
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

active_files = sorted((ROOT / "rx").glob("*.py")) + [
    ROOT / "validacao_real" / "run_rx_pipeline.py",
    ROOT / "validacao_real" / "run_rx_multiprobe.py",
    ROOT / "validacao_real" / "compute_validation_stdlib.py",
    ROOT / "data" / "pipelines" / "structure_d" / "__init__.py",
    ROOT / "data" / "pipelines" / "structure_d" / "joint_real_likelihood_rx.py",
    ROOT / "tools" / "rx_no_ai_gate.py",
    ROOT / "tools" / "rx_selftest.py",
    ROOT / "tools" / "rx_sound_horizon_selftest.py",
    ROOT / "tools" / "rx_freestanding65_parity.py",
    ROOT / "tools" / "rx_semantic_parity.py",
    ROOT / "tools" / "rx_dependency_audit.py",
    ROOT / "tools" / "rx_dependency_migration_plan.py",
    ROOT / "tools" / "rx_development_gate.py",
    ROOT / "internal" / "governance" / "development_guard.py",
    ROOT / "tools" / "validate_rll_development_governance.py",
    ROOT / "tools" / "rll_security_surface_audit.py",
]

stdlib = set(getattr(sys, "stdlib_module_names", ()))
stdlib.update({"__future__"})

local_roots = {"rx", "validacao_real", "data", "tools", "internal"}
for child in ROOT.iterdir():
    if child.is_dir():
        local_roots.add(child.name)
    elif child.suffix == ".py":
        local_roots.add(child.stem)

violations = []
scanned = []

for path in active_files:
    rel = str(path.relative_to(ROOT))
    if not path.exists():
        violations.append({"path": rel, "reason": "missing_active_file"})
        continue
    scanned.append(rel)
    tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            imports.update(alias.name.split(".")[0] for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module and node.level == 0:
            imports.add(node.module.split(".")[0])
    external = sorted(
        name for name in imports
        if name not in stdlib and name not in local_roots
    )
    if external:
        violations.append({
            "path": rel,
            "reason": "third_party_import",
            "modules": external,
        })

payload = {
    "schema": "rll.rx.zero_dependency_gate.v1",
    "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "state": "PASS" if not violations else "FAIL",
    "active_files_scanned": scanned,
    "third_party_python_dependencies": [],
    "violations": violations,
    "training": False,
    "ai_runtime": False,
    "claim_allowed": False,
}

out = ROOT / "results" / "rx_zero_dependency_gate.json"
out.parent.mkdir(exist_ok=True)
out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

if violations:
    print("RX_ZERO_DEPENDENCY_GATE=FAIL")
    for row in violations:
        print(row)
    raise SystemExit(1)

print("RX_ZERO_DEPENDENCY_GATE=PASS")
print("active_files=", len(scanned))
print("third_party_python_dependencies=0")
print("training=False ai_runtime=False")
print("wrote", out.relative_to(ROOT))
