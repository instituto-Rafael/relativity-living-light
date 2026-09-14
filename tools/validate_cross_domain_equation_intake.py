#!/usr/bin/env python3
"""Validate the fail-closed RLL cross-domain equation intake registry."""
from __future__ import annotations

import argparse
import hashlib
import json
import sys
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

REPO = Path(__file__).resolve().parents[1]
DEFAULT_SCHEMA = REPO / "schemas" / "rll_cross_domain_equation_intake.schema.json"
DEFAULT_REGISTRY = REPO / "data" / "contracts" / "cross_domain_equation_intake.v1.json"
DEFAULT_REPORT_DIR = REPO / "artifacts" / "cross-domain-equation-intake"


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level JSON must be an object")
    return data


def repo_relative_safe(value: str) -> bool:
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def targets_prefix(target: str, protected: str) -> bool:
    normalized_target = target.rstrip("/")
    normalized_protected = protected.rstrip("/")
    return normalized_target == normalized_protected or normalized_target.startswith(
        normalized_protected + "/"
    )


def semantic_findings(registry: dict[str, Any]) -> list[dict[str, str]]:
    findings: list[dict[str, str]] = []
    protected = [str(item) for item in registry.get("protected_target_prefixes", [])]

    def add(code: str, message: str, path: str) -> None:
        findings.append(
            {"severity": "error", "code": code, "message": message, "path": path}
        )

    if registry.get("claim_allowed") is not False:
        add("CDI_GLOBAL_CLAIM_OPEN", "global claim gate must fail closed", "claim_allowed")
    if registry.get("direct_model_integration_allowed") is not False:
        add(
            "CDI_GLOBAL_INTEGRATION_OPEN",
            "global direct model integration must remain forbidden",
            "direct_model_integration_allowed",
        )
    if registry.get("aggregation_rule") != "NON_COMPENSATORY":
        add(
            "CDI_AGGREGATION_NOT_FAIL_CLOSED",
            "aggregation must be non-compensatory",
            "aggregation_rule",
        )

    record_ids: set[str] = set()
    for index, record in enumerate(registry.get("records", [])):
        base = f"records/{index}"
        record_id = str(record.get("id", ""))
        if record_id in record_ids:
            add("CDI_DUPLICATE_ID", f"duplicate record id: {record_id}", f"{base}/id")
        record_ids.add(record_id)

        if record.get("claim_allowed") is not False:
            add("CDI_RECORD_CLAIM_OPEN", "record claim gate must be false", base)
        if record.get("direct_model_integration_allowed") is not False:
            add(
                "CDI_DIRECT_INTEGRATION_OPEN",
                "direct model integration must remain forbidden",
                f"{base}/direct_model_integration_allowed",
            )
        if record.get("affects_cosmology_evidence") is not False:
            add(
                "CDI_EVIDENCE_EFFECT_OPEN",
                "quarantined equations may not affect cosmology evidence",
                f"{base}/affects_cosmology_evidence",
            )

        domain = record.get("domain")
        if domain != "cosmology" and record.get("rll_relevance") not in {
            "REFERENCE_ONLY",
            "OUT_OF_SCOPE",
        }:
            add(
                "CDI_DOMAIN_LEAKAGE",
                "non-cosmology records may only be reference-only or out-of-scope",
                f"{base}/rll_relevance",
            )

        epistemic_class = record.get("epistemic_class")
        if epistemic_class == "H":
            for field in ("falsifier", "predicted_observation", "promotion_gate"):
                if not record.get(field):
                    add(
                        "CDI_HYPOTHESIS_NOT_TESTABLE",
                        f"H-class record requires {field}",
                        f"{base}/{field}",
                    )
        if epistemic_class == "P":
            if record.get("integration_targets"):
                add(
                    "CDI_METAPHOR_TARGETED",
                    "P-class analogy may not have integration targets",
                    f"{base}/integration_targets",
                )
            if record.get("rll_relevance") != "OUT_OF_SCOPE":
                add(
                    "CDI_METAPHOR_SCOPE",
                    "P-class analogy must remain out-of-scope",
                    f"{base}/rll_relevance",
                )

        source_status = record.get("source_status")
        source_refs = record.get("source_refs", [])
        source_gap = record.get("source_gap")
        if source_status == "TOKEN_VAZIO":
            if source_refs:
                add(
                    "CDI_SOURCE_STATE_CONFLICT",
                    "TOKEN_VAZIO source status cannot carry source refs",
                    f"{base}/source_refs",
                )
            if not source_gap:
                add(
                    "CDI_SOURCE_GAP_HIDDEN",
                    "TOKEN_VAZIO source status requires an explicit gap",
                    f"{base}/source_gap",
                )
        elif source_status in {"VERIFIED", "REVIEWED"}:
            if not source_refs:
                add(
                    "CDI_SOURCE_REFS_MISSING",
                    "reviewed or verified records require source refs",
                    f"{base}/source_refs",
                )
            if source_gap is not None:
                add(
                    "CDI_SOURCE_GAP_CONFLICT",
                    "reviewed or verified records must clear source_gap",
                    f"{base}/source_gap",
                )

        for target_index, target in enumerate(record.get("integration_targets", [])):
            target = str(target)
            if not repo_relative_safe(target):
                add(
                    "CDI_UNSAFE_TARGET_PATH",
                    "integration target must be repository-relative and non-traversing",
                    f"{base}/integration_targets/{target_index}",
                )
                continue
            for protected_prefix in protected:
                if targets_prefix(target, protected_prefix):
                    add(
                        "CDI_PROTECTED_TARGET",
                        f"integration target enters protected scientific surface: {protected_prefix}",
                        f"{base}/integration_targets/{target_index}",
                    )

        if record.get("integration_state") == "READY_FOR_TEST":
            if record.get("rll_relevance") != "CANDIDATE_FOR_ISOLATED_TEST":
                add(
                    "CDI_READY_WITHOUT_CANDIDATE",
                    "READY_FOR_TEST requires isolated-test relevance",
                    f"{base}/rll_relevance",
                )
            if not record.get("integration_targets"):
                add(
                    "CDI_READY_WITHOUT_TARGET",
                    "READY_FOR_TEST requires an isolated target",
                    f"{base}/integration_targets",
                )

    return findings


def build_payload(
    registry: dict[str, Any], findings: list[dict[str, str]]
) -> dict[str, Any]:
    class_counts: dict[str, int] = {}
    domain_counts: dict[str, int] = {}
    source_counts: dict[str, int] = {}
    state_counts: dict[str, int] = {}

    for record in registry.get("records", []):
        for bucket, key in (
            (class_counts, str(record.get("epistemic_class"))),
            (domain_counts, str(record.get("domain"))),
            (source_counts, str(record.get("source_status"))),
            (state_counts, str(record.get("integration_state"))),
        ):
            bucket[key] = bucket.get(key, 0) + 1

    return {
        "schema": "rll.cross_domain_equation_intake_validation.v1",
        "registry_id": registry.get("registry_id"),
        "passed": not findings,
        "claim_allowed": False,
        "direct_model_integration_allowed": False,
        "aggregation_rule": "NON_COMPENSATORY",
        "record_count": len(registry.get("records", [])),
        "class_counts": dict(sorted(class_counts.items())),
        "domain_counts": dict(sorted(domain_counts.items())),
        "source_counts": dict(sorted(source_counts.items())),
        "integration_state_counts": dict(sorted(state_counts.items())),
        "protected_target_prefix_count": len(
            registry.get("protected_target_prefixes", [])
        ),
        "findings": findings,
        "next_gate": registry.get("next_gate"),
    }


def write_reports(payload: dict[str, Any], report_dir: Path) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    json_path = report_dir / "validation.json"
    md_path = report_dir / "VALIDATION.md"

    json_path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    lines = [
        "# Cross-Domain Equation Intake Validation",
        "",
        f"- passed: `{str(payload['passed']).lower()}`",
        f"- registry_id: `{payload['registry_id']}`",
        f"- record_count: `{payload['record_count']}`",
        f"- claim_allowed: `{str(payload['claim_allowed']).lower()}`",
        "- aggregation_rule: `NON_COMPENSATORY`",
        "- direct_model_integration_allowed: `false`",
        "",
        "## Counts",
        "",
        f"- epistemic classes: `{json.dumps(payload['class_counts'], ensure_ascii=False, sort_keys=True)}`",
        f"- source states: `{json.dumps(payload['source_counts'], ensure_ascii=False, sort_keys=True)}`",
        f"- integration states: `{json.dumps(payload['integration_state_counts'], ensure_ascii=False, sort_keys=True)}`",
        f"- protected target prefixes: `{payload['protected_target_prefix_count']}`",
        "",
        "## Findings",
        "",
    ]
    if payload["findings"]:
        lines.extend(["| severity | code | path | message |", "|---|---|---|---|"])
        for finding in payload["findings"]:
            lines.append(
                f"| {finding['severity']} | `{finding['code']}` | "
                f"`{finding['path']}` | {finding['message']} |"
            )
    else:
        lines.append("No schema or semantic boundary violation found.")

    lines.extend(["", "## Next gate", "", str(payload["next_gate"]), ""])
    md_path.write_text("\n".join(lines), encoding="utf-8")

    checksum_lines = []
    for path in (json_path, md_path):
        checksum_lines.append(f"{hashlib.sha256(path.read_bytes()).hexdigest()}  {path.name}")
    (report_dir / "CHECKSUMS.sha256").write_text(
        "\n".join(checksum_lines) + "\n", encoding="utf-8"
    )


def validate(
    schema_path: Path = DEFAULT_SCHEMA,
    registry_path: Path = DEFAULT_REGISTRY,
) -> tuple[list[dict[str, str]], dict[str, Any]]:
    schema = load_json(schema_path)
    registry = load_json(registry_path)
    schema_errors = sorted(
        Draft202012Validator(
            schema, format_checker=FormatChecker()
        ).iter_errors(registry),
        key=lambda error: list(error.path),
    )
    findings = [
        {
            "severity": "error",
            "code": "CDI_SCHEMA",
            "path": "/".join(str(part) for part in error.path),
            "message": error.message,
        }
        for error in schema_errors
    ]
    findings.extend(semantic_findings(registry))
    return findings, build_payload(registry, findings)


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--schema", type=Path, default=DEFAULT_SCHEMA)
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--report-dir", type=Path, default=DEFAULT_REPORT_DIR)
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(list(argv) if argv is not None else None)

    schema_path = args.schema if args.schema.is_absolute() else REPO / args.schema
    registry_path = (
        args.registry if args.registry.is_absolute() else REPO / args.registry
    )
    findings, payload = validate(schema_path, registry_path)

    if args.write_report:
        report_dir = (
            args.report_dir if args.report_dir.is_absolute() else REPO / args.report_dir
        )
        write_reports(payload, report_dir)

    for finding in findings:
        print(
            f"{finding['severity'].upper()} {finding['code']}: "
            f"{finding['path']}: {finding['message']}"
        )
    if not findings:
        print(
            "Cross-domain equation intake OK: "
            f"{payload['record_count']} quarantined records, "
            f"{payload['protected_target_prefix_count']} protected target prefixes, "
            "claim_allowed=false."
        )

    return 1 if args.strict and findings else 0


if __name__ == "__main__":
    sys.exit(main())
