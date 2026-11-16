#!/usr/bin/env python3
"""Audit Python third-party imports for the Rx migration.

Stdlib only. This tool does not mutate source files.
"""

from __future__ import annotations

import ast
import json
import sys
from collections import Counter
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
OUT = ROOT / "results"
OUT.mkdir(exist_ok=True)

stdlib = set(getattr(sys, "stdlib_module_names", ()))
stdlib.update({"__future__"})

local_roots = {"rx"}
for child in ROOT.iterdir():
    if child.is_dir() and any(child.rglob("*.py")):
        local_roots.add(child.name)
for child in ROOT.glob("*.py"):
    local_roots.add(child.stem)

skip_parts = {".git", ".venv", "venv", "__pycache__", "node_modules"}
records = []
counts = Counter()
parse_errors = []

for path in sorted(ROOT.rglob("*.py")):
    rel = path.relative_to(ROOT)
    if any(part in skip_parts for part in rel.parts):
        continue
    try:
        tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
    except SyntaxError as exc:
        parse_errors.append({"path": str(rel), "error": str(exc)})
        continue

    imports = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            for alias in node.names:
                imports.add(alias.name.split(".")[0])
        elif isinstance(node, ast.ImportFrom) and node.module:
            imports.add(node.module.split(".")[0])

    external = sorted(
        name for name in imports
        if name not in stdlib and name not in local_roots
    )
    if external:
        records.append({"path": str(rel), "external_imports": external})
        counts.update(external)

payload = {
    "schema": "rll.rx_dependency_audit.v1",
    "python_files_with_external_imports": len(records),
    "external_import_occurrences_by_module": dict(sorted(counts.items())),
    "files": records,
    "parse_errors": parse_errors,
    "claim_boundary": (
        "An import audit identifies runtime coupling candidates. "
        "It does not prove a file executes, that a dependency is reachable, "
        "or that replacement preserves scientific equivalence."
    ),
}

(OUT / "rx_dependency_audit.json").write_text(
    json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
    encoding="utf-8",
)

lines = [
    "# Rx dependency audit",
    "",
    "Python files with candidate external imports: **%d**." % len(records),
    "",
    "| module | files/import occurrences |",
    "|---|---:|",
]
for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
    lines.append("| %s | %d |" % (name, count))
lines += ["", "## Files", ""]
for row in records:
    lines.append("- %s :: %s" % (row["path"], ", ".join(row["external_imports"])))
if parse_errors:
    lines += ["", "## Parse errors", ""]
    for row in parse_errors:
        lines.append("- %s :: %s" % (row["path"], row["error"]))

(OUT / "rx_dependency_audit.md").write_text(
    "\n".join(lines) + "\n",
    encoding="utf-8",
)

print("rx_dependency_audit")
print("files_with_external_imports=", len(records))
for name, count in sorted(counts.items(), key=lambda item: (-item[1], item[0])):
    print(name, count)
print("json=", (OUT / "rx_dependency_audit.json").relative_to(ROOT))
print("md=", (OUT / "rx_dependency_audit.md").relative_to(ROOT))
