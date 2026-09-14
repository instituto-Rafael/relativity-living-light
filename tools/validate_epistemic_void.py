#!/usr/bin/env python3
"""Validate the RLL epistemic-void ledger and emit auditable routing metrics.

The operational entropy reported here is a repository routing convention. It is
not thermodynamic entropy, Shannon entropy, scientific evidence, or a model
selection statistic.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = REPO / "schemas" / "rll_epistemic_void.schema.json"
DEFAULT_LEDGER = REPO / "data" / "epistemic_void" / "rll_epistemic_void.json"
DEFAULT_REPORT_DIR = REPO / "artifacts" / "epistemic-void"

UNRESOLVED_STATES = {
    "TOKEN_VAZIO",
    "BLOCKED",
    "PARTIAL",
    "CONTRADICTION",
    "READY_FOR_TEST",
}


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level JSON must be an object")
    return data


def repo_relative_safe(value: str) -> bool:
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def semantic_findings(ledger: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    record_ids: set[str] = set()

    def add(code: str, message: str, path: str) -> None:
        findings.append({"severity": "error", "code": code, "message": message, "path": path})

    for index, record in enumerate(ledger.get("records", [])):
        base = f"records/{index}"
        record_id = str(record.get("id", ""))
        if record_id in record_ids:
            add("EV_DUPLICATE_RECORD_ID", f"duplicate record id: {record_id}", f"{base}/id")
        record_ids.add(record_id)

        possibility_ids: set[str] = set()
        for p_index, possibility in enumerate(record.get("possibilities", [])):
            p_base = f"{base}/possibilities/{p_index}"
            possibility_id = str(possibility.get("id", ""))
            if possibility_id in possibility_ids:
                add("EV_DUPLICATE_POSSIBILITY_ID", f"duplicate possibility id: {possibility_id}", f"{p_base}/id")
            possibility_ids.add(possibility_id)
            if possibility.get("classification") == "H":
                if not possibility.get("falsifier") or not possibility.get("predicted_observation"):
                    add(
                        "EV_HYPOTHESIS_NOT_TESTABLE",
                        "H-class possibilities require a falsifier and predicted observation",
                        p_base,
                    )

        exit_ids: set[str] = set()
        for x_index, exit_condition in enumerate(record.get("exit_conditions", [])):
            x_base = f"{base}/exit_conditions/{x_index}"
            exit_id = str(exit_condition.get("id", ""))
            if exit_id in exit_ids:
                add("EV_DUPLICATE_EXIT_ID", f"duplicate exit id: {exit_id}", f"{x_base}/id")
            exit_ids.add(exit_id)
            artifact_path = str(exit_condition.get("artifact_path", ""))
            if not repo_relative_safe(artifact_path):
                add(
                    "EV_UNSAFE_ARTIFACT_PATH",
                    "artifact_path must be repository-relative and may not traverse parents",
                    f"{x_base}/artifact_path",
                )

        known = {str(item).strip().casefold() for item in record.get("known", [])}
        unknowns = {str(item).strip().casefold() for item in record.get("unknowns", [])}
        overlap = sorted(known & unknowns)
        if overlap:
            add(
                "EV_KNOWN_UNKNOWN_OVERLAP",
                f"statements cannot be simultaneously known and unknown: {overlap}",
                base,
            )

        state = record.get("state")
        if state in UNRESOLVED_STATES:
            if record.get("conclusion") is not None:
                add("EV_PREMATURE_CONCLUSION", "unresolved records must keep conclusion=null", f"{base}/conclusion")
            if record.get("resolution_evidence"):
                add(
                    "EV_PREMATURE_RESOLUTION_EVIDENCE",
                    "unresolved records may not carry resolution evidence",
                    f"{base}/resolution_evidence",
                )

        for s_index, source_ref in enumerate(record.get("source_refs", [])):
            if not repo_relative_safe(str(source_ref)):
                add(
                    "EV_UNSAFE_SOURCE_REF",
                    "source_refs must be repository-relative and may not traverse parents",
                    f"{base}/source_refs/{s_index}",
                )

    return findings


def build_payload(ledger: dict[str, Any], findings: list[dict[str, str]]) -> dict[str, Any]:
    records: list[dict[str, Any]] = []
    totals = {
        "records": 0,
        "unknowns": 0,
        "possibilities": 0,
        "hypotheses": 0,
        "analogies": 0,
        "conventions": 0,
        "contradictions": 0,
        "exit_conditions": 0,
    }
    states: dict[str, int] = {}

    for record in ledger["records"]:
        possibilities = record["possibilities"]
        unknown_count = len(record["unknowns"])
        contradiction_count = len(record["contradictions"])
        exit_count = len(record["exit_conditions"])
        exploration_load = unknown_count + len(possibilities) + contradiction_count
        closure_denominator = max(1, unknown_count + contradiction_count)
        closure_readiness = round(min(1.0, exit_count / closure_denominator), 3)

        row = {
            "id": record["id"],
            "state": record["state"],
            "priority": record["priority"],
            "domain": record["domain"],
            "unknowns": unknown_count,
            "possibilities": len(possibilities),
            "contradictions": contradiction_count,
            "exit_conditions": exit_count,
            "operational_exploration_load": exploration_load,
            "closure_readiness": closure_readiness,
        }
        records.append(row)

        totals["records"] += 1
        totals["unknowns"] += unknown_count
        totals["possibilities"] += len(possibilities)
        totals["hypotheses"] += sum(1 for item in possibilities if item["classification"] == "H")
        totals["analogies"] += sum(1 for item in possibilities if item["classification"] == "P")
        totals["conventions"] += sum(1 for item in possibilities if item["classification"] == "C")
        totals["contradictions"] += contradiction_count
        totals["exit_conditions"] += exit_count
        states[record["state"]] = states.get(record["state"], 0) + 1

    return {
        "schema": "rll.epistemic_void_validation.v1",
        "ledger_id": ledger["ledger_id"],
        "passed": not findings,
        "claim_allowed": False,
        "operational_entropy_definition": ledger["operational_entropy_definition"],
        "metric_boundary": (
            "operational_exploration_load counts unknowns, possibilities and contradictions "
            "for routing only; it is not thermodynamic entropy, Shannon entropy, evidence, "
            "or a scientific score"
        ),
        "state_counts": dict(sorted(states.items())),
        "totals": totals,
        "records": records,
        "findings": findings,
        "next_gate": ledger["next_gate"],
    }


def write_reports(payload: dict[str, Any], report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "epistemic_void_report.json"
    md_path = report_dir / "EPISTEMIC_VOID_REPORT.md"

    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")

    lines = [
        "# RLL Epistemic Void Report",
        "",
        f"- passed: `{str(payload['passed']).lower()}`",
        f"- ledger_id: `{payload['ledger_id']}`",
        f"- claim_allowed: `{str(payload['claim_allowed']).lower()}`",
        f"- metric_boundary: {payload['metric_boundary']}",
        "",
        "## State counts",
        "",
        "| state | count |",
        "|---|---:|",
    ]
    for state, count in payload["state_counts"].items():
        lines.append(f"| `{state}` | {count} |")

    lines.extend(
        [
            "",
            "## Routing metrics",
            "",
            "| record | state | priority | unknowns | possibilities | contradictions | exits | exploration load | closure readiness |",
            "|---|---|---|---:|---:|---:|---:|---:|---:|",
        ]
    )
    for row in payload["records"]:
        lines.append(
            f"| `{row['id']}` | `{row['state']}` | `{row['priority']}` | "
            f"{row['unknowns']} | {row['possibilities']} | {row['contradictions']} | "
            f"{row['exit_conditions']} | {row['operational_exploration_load']} | "
            f"{row['closure_readiness']:.3f} |"
        )

    lines.extend(["", "## Findings", ""])
    if payload["findings"]:
        lines.extend(["| severity | code | path | message |", "|---|---|---|---|"])
        for finding in payload["findings"]:
            lines.append(
                f"| {finding['severity']} | `{finding['code']}` | `{finding['path']}` | "
                f"{finding['message']} |"
            )
    else:
        lines.append("No semantic inconsistencies found.")

    lines.extend(["", "## Next gate", "", payload["next_gate"], ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    checksum_lines = []
    for path in (json_path, md_path):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        checksum_lines.append(f"{digest}  {path.name}")
    (report_dir / "CHECKSUMS.sha256").write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")


def validate(
    schema_path: Path = DEFAULT_SCHEMA,
    ledger_path: Path = DEFAULT_LEDGER,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    schema = load_json(schema_path)
    ledger = load_json(ledger_path)
    schema_errors = sorted(
        Draft202012Validator(schema, format_checker=FormatChecker()).iter_errors(ledger),
        key=lambda error: list(error.path),
    )
    findings = [
        {
            "severity": "error",
            "code": "EV_SCHEMA",
            "path": "/".join(str(part) for part in error.path),
            "message": error.message,
        }
        for error in schema_errors
    ]
    findings.extend(semantic_findings(ledger))
    return findings, build_payload(ledger, findings)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--ledger", type=Path, default=DEFAULT_LEDGER)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    schema_path = args.schema if args.schema.is_absolute() else REPO / args.schema
    ledger_path = args.ledger if args.ledger.is_absolute() else REPO / args.ledger
    findings, payload = validate(schema_path, ledger_path)

    if args.write_report:
        report_dir = args.report_dir if args.report_dir.is_absolute() else REPO / args.report_dir
        write_reports(payload, report_dir)

    for finding in findings:
        print(f"{finding['severity'].upper()} {finding['code']}: {finding['path']}: {finding['message']}")
    if not findings:
        print(
            "Epistemic void ledger OK: "
            f"{payload['totals']['records']} records, "
            f"{payload['totals']['hypotheses']} testable hypotheses, "
            f"{payload['totals']['exit_conditions']} exit conditions."
        )

    return 1 if args.strict and findings else 0


if __name__ == "__main__":
    sys.exit(main())
