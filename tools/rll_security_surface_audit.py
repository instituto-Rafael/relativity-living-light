#!/usr/bin/env python3
"""Static security-surface audit for governed RLL Python routes.

Stdlib only. This is a source-code guardrail, not a vulnerability scanner and
not a proof that code is secure.
"""

from __future__ import annotations

import argparse
import ast
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_SCOPES = ["rx", "validacao_real", "internal/governance"]

CRITICAL_CALLS = {"eval", "exec", "__import__"}
CRITICAL_ATTR_CALLS = {
    "os.system",
    "os.popen",
    "pickle.load",
    "pickle.loads",
    "marshal.load",
    "marshal.loads",
}
REVIEW_ATTR_CALLS = {
    "subprocess.Popen",
    "subprocess.run",
    "subprocess.call",
    "subprocess.check_call",
    "subprocess.check_output",
    "importlib.import_module",
}
NETWORK_ATTR_CALLS = {
    "urllib.request.urlopen",
    "http.client.HTTPConnection",
    "http.client.HTTPSConnection",
    "socket.socket",
}


def _attr_name(node):
    parts = []
    current = node
    while isinstance(current, ast.Attribute):
        parts.append(current.attr)
        current = current.value
    if isinstance(current, ast.Name):
        parts.append(current.id)
        return ".".join(reversed(parts))
    return ""


def _literal_shell_true(node):
    for keyword in getattr(node, "keywords", []):
        if keyword.arg == "shell" and isinstance(keyword.value, ast.Constant):
            return keyword.value.value is True
    return False


def _files_for_scopes(scopes):
    seen = set()
    for scope in scopes:
        base = ROOT / scope
        if base.is_file() and base.suffix == ".py":
            candidates = [base]
        elif base.is_dir():
            candidates = sorted(base.rglob("*.py"))
        else:
            candidates = []
        for path in candidates:
            if "__pycache__" in path.parts:
                continue
            if path not in seen:
                seen.add(path)
                yield path


def audit(scopes=None):
    scopes = scopes or DEFAULT_SCOPES
    findings = []
    parse_errors = []

    for path in _files_for_scopes(scopes):
        rel = path.relative_to(ROOT).as_posix()
        try:
            tree = ast.parse(path.read_text(encoding="utf-8", errors="replace"))
        except SyntaxError as exc:
            parse_errors.append(
                {"path": rel, "line": exc.lineno, "error": str(exc)}
            )
            continue

        for node in ast.walk(tree):
            if not isinstance(node, ast.Call):
                continue

            line = getattr(node, "lineno", 0)
            if isinstance(node.func, ast.Name):
                name = node.func.id
                if name in CRITICAL_CALLS:
                    findings.append(
                        {
                            "severity": "CRITICAL",
                            "path": rel,
                            "line": line,
                            "kind": "dynamic_code_execution",
                            "symbol": name,
                        }
                    )
                elif name == "compile":
                    findings.append(
                        {
                            "severity": "REVIEW",
                            "path": rel,
                            "line": line,
                            "kind": "dynamic_code_compilation",
                            "symbol": name,
                        }
                    )
                continue

            name = _attr_name(node.func)
            if name in CRITICAL_ATTR_CALLS:
                findings.append(
                    {
                        "severity": "CRITICAL",
                        "path": rel,
                        "line": line,
                        "kind": "unsafe_runtime_primitive",
                        "symbol": name,
                    }
                )
                continue

            if name in NETWORK_ATTR_CALLS:
                if rel != "internal/governance/development_guard.py":
                    findings.append(
                        {
                            "severity": "CRITICAL",
                            "path": rel,
                            "line": line,
                            "kind": "network_bypass_of_guard",
                            "symbol": name,
                        }
                    )
                continue

            if name in REVIEW_ATTR_CALLS:
                severity = "CRITICAL" if _literal_shell_true(node) else "REVIEW"
                findings.append(
                    {
                        "severity": severity,
                        "path": rel,
                        "line": line,
                        "kind": (
                            "shell_true_forbidden"
                            if severity == "CRITICAL"
                            else "process_or_dynamic_import_review"
                        ),
                        "symbol": name,
                    }
                )

    critical = [x for x in findings if x["severity"] == "CRITICAL"]
    review = [x for x in findings if x["severity"] == "REVIEW"]
    return {
        "schema": "rll.security_surface_audit.v1",
        "scopes": scopes,
        "critical_count": len(critical),
        "review_count": len(review),
        "parse_error_count": len(parse_errors),
        "findings": findings,
        "parse_errors": parse_errors,
        "strict_pass": not critical and not parse_errors,
        "claim_allowed": False,
        "boundary": (
            "This AST audit checks a small set of dangerous source primitives. "
            "PASS does not prove absence of vulnerabilities, runtime isolation, "
            "authorization, privacy compliance, or scientific validity."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Audit governed RLL Python security surface")
    parser.add_argument("scopes", nargs="*", default=DEFAULT_SCOPES)
    parser.add_argument("--json-out", default="results/security_surface_audit.json")
    parser.add_argument("--md-out", default="results/security_surface_audit.md")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    payload = audit(args.scopes)
    json_out = ROOT / args.json_out
    md_out = ROOT / args.md_out
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    lines = [
        "# RLL security surface audit",
        "",
        "Scopes: " + ", ".join(payload["scopes"]),
        "",
        "- critical: %d" % payload["critical_count"],
        "- review: %d" % payload["review_count"],
        "- parse errors: %d" % payload["parse_error_count"],
        "- strict_pass: %s" % str(payload["strict_pass"]).lower(),
        "",
    ]
    for item in payload["findings"]:
        lines.append(
            "- [%s] %s:%s %s %s"
            % (
                item["severity"],
                item["path"],
                item["line"],
                item["kind"],
                item["symbol"],
            )
        )
    if payload["parse_errors"]:
        lines += ["", "## Parse errors", ""]
        for item in payload["parse_errors"]:
            lines.append("- %s:%s %s" % (item["path"], item["line"], item["error"]))

    md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload["strict_pass"]:
        return 5
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
