#!/usr/bin/env python3
"""Read-only, bounded static preflight for selected GitHub Actions workflows.

Checks literal local script paths called by python/python3/bash/sh, and optionally
checks that explicit Python scripts have stdlib/local imports only. This is not
a YAML parser, CI execution, or a complete transitive dependency proof.
"""
from __future__ import annotations
import argparse
import ast
import json
import re
import shlex
import sys
from pathlib import Path

COMMAND = re.compile(r"(?:^|[;&|]\s*)(python(?:3(?:\.\d+)?)?|bash|sh)\s+(.+)$")
LOCAL_SUFFIXES = (".py", ".sh")


def literal_paths(line: str) -> list[str]:
    line = line.strip()
    if line.startswith("run:"):
        line = line[4:].strip()
    if not line or line.startswith("#"):
        return []
    match = COMMAND.search(line)
    if not match:
        return []
    executable, arguments = match.groups()
    try:
        tokens = shlex.split(arguments.strip().rstrip("\\"), comments=False)
    except ValueError:
        return []
    if not tokens or tokens[0] == "-":  # heredoc: python - <<'PY'
        return []
    if tokens[:2] == ["-m", "py_compile"]:
        candidates = tokens[2:]
    elif tokens[0] == "-m":
        return []
    else:
        candidates = tokens[:1]
    paths = []
    for item in candidates:
        item = item.rstrip("\\")
        if not item.endswith(LOCAL_SUFFIXES) or item.startswith("-"):
            continue
        if "$" in item or "{" in item or item.startswith("/"):
            continue
        paths.append(item.removeprefix("./"))
    return paths


def validate(root: Path, workflows: list[str], stdlib_only: bool = False) -> dict:
    missing: set[str] = set()
    outside: set[str] = set()
    imports: set[str] = set()
    inspected: set[str] = set()
    workflow_missing: set[str] = set()
    for workflow in workflows:
        file = root / workflow
        if not file.is_file():
            workflow_missing.add(workflow)
            continue
        for line in file.read_text(encoding="utf-8").splitlines():
            for name in literal_paths(line):
                path = (root / name).resolve()
                try:
                    path.relative_to(root.resolve())
                except ValueError:
                    outside.add(name)
                    continue
                if not path.is_file():
                    missing.add(name)
                    continue
                inspected.add(name)
                if stdlib_only and path.suffix == ".py":
                    try:
                        syntax = ast.parse(path.read_text(encoding="utf-8"), filename=name)
                    except (SyntaxError, UnicodeError) as error:
                        imports.add(f"{name}:UNPARSEABLE:{type(error).__name__}")
                        continue
                    for node in ast.walk(syntax):
                        if isinstance(node, ast.Import):
                            names = [a.name.split(".")[0] for a in node.names]
                        elif isinstance(node, ast.ImportFrom) and node.level == 0 and node.module:
                            names = [node.module.split(".")[0]]
                        else:
                            continue
                        for module in names:
                            local = (root / module).is_dir() or (root / (module + ".py")).is_file()
                            if not local and module not in sys.stdlib_module_names:
                                imports.add(f"{name}:{module}")
    ok = not (missing or outside or imports or workflow_missing)
    return {
        "schema": "rll.workflow_dependency_preflight.v1",
        "status": "STATIC_SCOPE_PASS" if ok else "STATIC_SCOPE_FAIL",
        "claim_allowed": False,
        "exact_head_ci": "NOT_RUN",
        "scope": "literal_local_script_calls_only",
        "workflows": sorted(set(workflows)),
        "scripts_checked": sorted(inspected),
        "workflow_missing": sorted(workflow_missing),
        "missing_local_scripts": sorted(missing),
        "outside_root": sorted(outside),
        "non_stdlib_imports": sorted(imports),
        "limitations": [
            "Not a full YAML parser; dynamic run expressions, actions/uses, and shell heredocs not resolved.",
            "Direct imports only; no transitive runtime or scientific parity proof.",
            "Static gate does not replace exact-head CI, actionlint, or execution evidence.",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path("."))
    parser.add_argument("--workflow", action="append", required=True)
    parser.add_argument("--stdlib-only", action="store_true")
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    report = validate(args.root.resolve(), args.workflow, args.stdlib_only)
    payload = json.dumps(report, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    else:
        print(payload, end="")
    return 0 if report["status"] == "STATIC_SCOPE_PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
