#!/usr/bin/env python3
"""Build a typed migration plan from the global Rx dependency audit.

This tool plans migration; it does not rewrite files automatically.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "results" / "rx_dependency_audit.json"
OUT_JSON = ROOT / "results" / "rx_dependency_migration_plan.json"
OUT_MD = ROOT / "results" / "rx_dependency_migration_plan.md"

if not AUDIT.exists():
    raise SystemExit("dependency audit missing; run tools/rx_dependency_audit.py first")

audit = json.loads(AUDIT.read_text(encoding="utf-8"))

replacement = {
    "numpy": "RX_KERNEL_NUMERIC_OR_DOMAIN_PORT",
    "pandas": "PYTHON_STDLIB_CSV_JSON_OR_RX_IO",
    "scipy": "RX_OPTIMIZER_INTEGRATION_LINEAR_ALGEBRA",
    "yaml": "VERSIONED_JSON_OR_EXPLICIT_SUBSET_PARSER",
    "matplotlib": "RX_SVG_OUTPUT",
    "emcee": "TOKEN_VAZIO_INFERENCE_REPLACEMENT",
    "dynesty": "TOKEN_VAZIO_INFERENCE_REPLACEMENT",
    "astropy": "TOKEN_VAZIO_DOMAIN_REPLACEMENT",
}

def classify(path):
    if path.startswith("data/pipelines/structure_d/"):
        return "RLL_LEGACY_SCIENCE"
    if path.startswith("validacao_real/") or path.startswith("scripts/rll"):
        return "RLL_LEGACY_VALIDATION"
    if path.startswith("tests/"):
        return "TEST_LEGACY"
    if path.startswith("tools/") or path.startswith("internal/"):
        return "TOOLING_GOVERNANCE"
    if "notebook" in path.lower() or path.endswith(".ipynb"):
        return "HISTORICAL_NOTEBOOK"
    return "OTHER_REPOSITORY_CODE"

rows = []
by_class = Counter()
by_module = Counter()
token_vazio = []

for item in audit.get("files", []):
    path = item["path"]
    cls = classify(path)
    modules = list(item.get("external_imports", []))
    routes = {}
    for module in modules:
        route = replacement.get(module, "TOKEN_VAZIO_REPLACEMENT_ROUTE")
        routes[module] = route
        by_module[module] += 1
        if route.startswith("TOKEN_VAZIO"):
            token_vazio.append({"path": path, "module": module, "route": route})
    by_class[cls] += 1
    rows.append({
        "path": path,
        "class": cls,
        "external_imports": modules,
        "replacement_routes": routes,
        "automatic_rewrite_allowed": False,
        "reason": "semantic parity must be demonstrated before replacement",
    })

priority_order = {
    "RLL_LEGACY_SCIENCE": 0,
    "RLL_LEGACY_VALIDATION": 1,
    "TOOLING_GOVERNANCE": 2,
    "TEST_LEGACY": 3,
    "OTHER_REPOSITORY_CODE": 4,
    "HISTORICAL_NOTEBOOK": 5,
}
rows.sort(key=lambda row: (priority_order.get(row["class"], 99), row["path"]))

payload = {
    "schema": "rll.rx.dependency_migration_plan.v1",
    "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "source": str(AUDIT.relative_to(ROOT)),
    "files_with_external_imports": audit.get("python_files_with_external_imports", 0),
    "by_class": dict(by_class),
    "by_module": dict(by_module),
    "rows": rows,
    "token_vazio_replacements": token_vazio,
    "policy": {
        "automatic_mass_rewrite": False,
        "active_rx_runtime_already_zero_dependency": True,
        "migration_rule": "port -> parity gate -> switch route -> preserve legacy -> rollback",
        "training": False,
        "ai_runtime": False,
    },
    "claim_allowed": False,
}

OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

lines = [
    "# Rx dependency migration plan",
    "",
    "Global legacy files with external imports: **%d**." % payload["files_with_external_imports"],
    "",
    "Active Rx runtime remains zero-third-party; this ledger covers legacy/repository-wide debt.",
    "",
    "## By class",
    "",
]
for name, count in sorted(by_class.items(), key=lambda item: (-item[1], item[0])):
    lines.append("- %s: %d" % (name, count))

lines += ["", "## By module", ""]
for name, count in sorted(by_module.items(), key=lambda item: (-item[1], item[0])):
    lines.append("- %s: %d -> %s" % (name, count, replacement.get(name, "TOKEN_VAZIO_REPLACEMENT_ROUTE")))

lines += [
    "",
    "## Migration invariant",
    "",
    "port -> parity gate -> switch route -> preserve legacy -> rollback",
    "",
    "No mass search/replace is authorized because NumPy/SciPy/Pandas/YAML imports often encode scientific or serialization semantics, not only syntax.",
]
OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("RX_DEPENDENCY_MIGRATION_PLAN=PASS")
print("files=", payload["files_with_external_imports"])
for name, count in sorted(by_class.items(), key=lambda item: (-item[1], item[0])):
    print(name, count)
print("token_vazio_replacements=", len(token_vazio))
print("wrote", OUT_JSON.relative_to(ROOT))
print("wrote", OUT_MD.relative_to(ROOT))
