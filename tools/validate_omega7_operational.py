#!/usr/bin/env python3
"""Validate the RLL Ω7 operational invariant assessment.

The assessment is architectural and claim-bounded. Its geometric mean and
minimum are routing conventions over seven declared scores. They are not
physical geometry, probabilities, evidence weights or scientific validation.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import sys
from dataclasses import dataclass, asdict
from pathlib import Path
from typing import Any, Iterable

from jsonschema import Draft202012Validator, FormatChecker

ROOT = Path(__file__).resolve().parents[1]
SCHEMA_PATH = ROOT / "schemas" / "omega_operational_invariant.schema.json"
ASSESSMENT_PATH = ROOT / "data" / "omega_operational" / "rll_omega7_operational.json"
REPORT_DIR = ROOT / "artifacts" / "omega7-operational"

EXPECTED_DIRECTIONS = {
    "D1": "origin_provenance",
    "D2": "semantic_coherence",
    "D3": "geometric_dimensional_integrity",
    "D4": "runtime_execution",
    "D5": "temporal_state_memory",
    "D6": "rights_security",
    "D7": "evidence_falsification",
}
EXPECTED_INVARIANTS = {f"I{i}" for i in range(1, 8)}
EXPECTED_CONDITIONS = {f"U{i}" for i in range(1, 8)}
EPSILON = 1e-9


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str | None = None


def load_json(path: Path) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError(f"{path}: top-level JSON must be an object")
    return payload


def safe_repo_path(value: str) -> bool:
    path = Path(value)
    return bool(value) and not path.is_absolute() and ".." not in path.parts


def duplicate_values(values: Iterable[str]) -> list[str]:
    seen: set[str] = set()
    duplicates: set[str] = set()
    for value in values:
        if value in seen:
            duplicates.add(value)
        seen.add(value)
    return sorted(duplicates)


def expected_decision(omega_g: float, omega_min: float, hard_gate_open: list[str]) -> str:
    if hard_gate_open or omega_min < 0.5:
        return "BLOCKED"
    if omega_g < 0.75:
        return "READY_FOR_TEST"
    if omega_min < 0.75:
        return "AUDITABLE"
    return "COHERENT"


def validate_assessment(
    assessment_path: Path = ASSESSMENT_PATH,
    schema_path: Path = SCHEMA_PATH,
) -> tuple[list[Finding], dict[str, Any]]:
    findings: list[Finding] = []
    schema = load_json(schema_path)
    assessment = load_json(assessment_path)

    validator = Draft202012Validator(schema, format_checker=FormatChecker())
    for error in sorted(validator.iter_errors(assessment), key=lambda item: list(item.path)):
        location = "/".join(str(part) for part in error.path) or "$"
        findings.append(Finding("error", "OMEGA7_SCHEMA", error.message, location))

    directions = assessment.get("directions")
    if not isinstance(directions, list):
        directions = []

    direction_ids = [
        str(item.get("direction_id"))
        for item in directions
        if isinstance(item, dict)
    ]
    for duplicate in duplicate_values(direction_ids):
        findings.append(Finding("error", "OMEGA7_DUPLICATE_DIRECTION", f"duplicate direction {duplicate}", "directions"))

    actual_direction_ids = set(direction_ids)
    expected_direction_ids = set(EXPECTED_DIRECTIONS)
    if actual_direction_ids != expected_direction_ids:
        findings.append(
            Finding(
                "error",
                "OMEGA7_DIRECTION_SET",
                f"directions must be exactly {sorted(expected_direction_ids)}; found {sorted(actual_direction_ids)}",
                "directions",
            )
        )

    normalized_scores: dict[str, float] = {}
    for index, direction in enumerate(directions):
        if not isinstance(direction, dict):
            continue
        direction_id = str(direction.get("direction_id"))
        expected_dimension = EXPECTED_DIRECTIONS.get(direction_id)
        if expected_dimension and direction.get("dimension") != expected_dimension:
            findings.append(
                Finding(
                    "error",
                    "OMEGA7_DIMENSION_MISMATCH",
                    f"{direction_id} must use dimension {expected_dimension!r}",
                    f"directions/{index}/dimension",
                )
            )

        score = direction.get("score")
        normalized = direction.get("normalized_score")
        if isinstance(score, int) and isinstance(normalized, (int, float)):
            expected_normalized = score / 4.0
            normalized_scores[direction_id] = float(normalized)
            if abs(float(normalized) - expected_normalized) > EPSILON:
                findings.append(
                    Finding(
                        "error",
                        "OMEGA7_NORMALIZATION",
                        f"{direction_id} normalized_score must equal score/4 ({expected_normalized})",
                        f"directions/{index}/normalized_score",
                    )
                )

            status = direction.get("status")
            if score == 4 and status != "VERIFIED":
                findings.append(
                    Finding(
                        "error",
                        "OMEGA7_SCORE_STATUS",
                        f"{direction_id} score 4 requires VERIFIED",
                        f"directions/{index}/status",
                    )
                )
            if status == "VERIFIED" and score != 4:
                findings.append(
                    Finding(
                        "error",
                        "OMEGA7_VERIFIED_SCORE",
                        f"{direction_id} VERIFIED requires score 4",
                        f"directions/{index}/score",
                    )
                )
            if score == 0 and status not in {"BLOCKED", "TOKEN_VAZIO"}:
                findings.append(
                    Finding(
                        "error",
                        "OMEGA7_ZERO_STATUS",
                        f"{direction_id} score 0 requires BLOCKED or TOKEN_VAZIO",
                        f"directions/{index}/status",
                    )
                )

        refs = direction.get("evidence_refs")
        if isinstance(refs, list):
            for ref_index, ref in enumerate(refs):
                if isinstance(ref, str) and not safe_repo_path(ref):
                    findings.append(
                        Finding(
                            "error",
                            "OMEGA7_UNSAFE_PATH",
                            f"unsafe repository path: {ref!r}",
                            f"directions/{index}/evidence_refs/{ref_index}",
                        )
                    )
        artifact = direction.get("gate_artifact")
        if isinstance(artifact, str) and not safe_repo_path(artifact):
            findings.append(
                Finding(
                    "error",
                    "OMEGA7_UNSAFE_ARTIFACT",
                    f"unsafe gate artifact path: {artifact!r}",
                    f"directions/{index}/gate_artifact",
                )
            )

    hard_invariants = assessment.get("hard_invariants")
    if not isinstance(hard_invariants, list):
        hard_invariants = []
    invariant_ids = [
        str(item.get("invariant_id"))
        for item in hard_invariants
        if isinstance(item, dict)
    ]
    for duplicate in duplicate_values(invariant_ids):
        findings.append(Finding("error", "OMEGA7_DUPLICATE_INVARIANT", f"duplicate invariant {duplicate}", "hard_invariants"))
    if set(invariant_ids) != EXPECTED_INVARIANTS:
        findings.append(
            Finding(
                "error",
                "OMEGA7_INVARIANT_SET",
                f"hard invariants must be exactly {sorted(EXPECTED_INVARIANTS)}",
                "hard_invariants",
            )
        )

    actual_hard_gate_open = sorted(
        str(item.get("invariant_id"))
        for item in hard_invariants
        if isinstance(item, dict) and item.get("status") != "PASS"
    )

    urgent_conditions = assessment.get("urgent_conditions")
    if not isinstance(urgent_conditions, list):
        urgent_conditions = []
    condition_ids = [
        str(item.get("condition_id"))
        for item in urgent_conditions
        if isinstance(item, dict)
    ]
    for duplicate in duplicate_values(condition_ids):
        findings.append(Finding("error", "OMEGA7_DUPLICATE_CONDITION", f"duplicate condition {duplicate}", "urgent_conditions"))
    if set(condition_ids) != EXPECTED_CONDITIONS:
        findings.append(
            Finding(
                "error",
                "OMEGA7_CONDITION_SET",
                f"urgent conditions must be exactly {sorted(EXPECTED_CONDITIONS)}",
                "urgent_conditions",
            )
        )

    condition_directions = [
        str(item.get("direction_id"))
        for item in urgent_conditions
        if isinstance(item, dict)
    ]
    if sorted(condition_directions) != sorted(EXPECTED_DIRECTIONS):
        findings.append(
            Finding(
                "error",
                "OMEGA7_CONDITION_COVERAGE",
                "urgent conditions must cover each direction exactly once",
                "urgent_conditions",
            )
        )
    for index, condition in enumerate(urgent_conditions):
        if not isinstance(condition, dict):
            continue
        artifact = condition.get("required_artifact")
        if isinstance(artifact, str) and not safe_repo_path(artifact):
            findings.append(
                Finding(
                    "error",
                    "OMEGA7_UNSAFE_REQUIRED_ARTIFACT",
                    f"unsafe required artifact path: {artifact!r}",
                    f"urgent_conditions/{index}/required_artifact",
                )
            )

    metrics = assessment.get("omega_metrics")
    if not isinstance(metrics, dict):
        metrics = {}

    if set(normalized_scores) == set(EXPECTED_DIRECTIONS):
        values = [normalized_scores[key] for key in sorted(EXPECTED_DIRECTIONS)]
        omega_g = math.prod(values) ** (1.0 / 7.0)
        omega_min = min(values)
        weakest = sorted(key for key, value in normalized_scores.items() if abs(value - omega_min) <= EPSILON)

        declared_g = metrics.get("omega_g")
        if isinstance(declared_g, (int, float)) and abs(float(declared_g) - omega_g) > EPSILON:
            findings.append(
                Finding(
                    "error",
                    "OMEGA7_GEOMETRIC_MEAN",
                    f"omega_g must equal {omega_g:.12f}",
                    "omega_metrics/omega_g",
                )
            )
        declared_min = metrics.get("omega_min")
        if isinstance(declared_min, (int, float)) and abs(float(declared_min) - omega_min) > EPSILON:
            findings.append(
                Finding(
                    "error",
                    "OMEGA7_MINIMUM",
                    f"omega_min must equal {omega_min}",
                    "omega_metrics/omega_min",
                )
            )
        if metrics.get("weakest_directions") != weakest:
            findings.append(
                Finding(
                    "error",
                    "OMEGA7_WEAKEST",
                    f"weakest_directions must be {weakest}",
                    "omega_metrics/weakest_directions",
                )
            )

        if metrics.get("hard_gate_open") != actual_hard_gate_open:
            findings.append(
                Finding(
                    "error",
                    "OMEGA7_HARD_GATE_LIST",
                    f"hard_gate_open must be {actual_hard_gate_open}",
                    "omega_metrics/hard_gate_open",
                )
            )

        decision = expected_decision(omega_g, omega_min, actual_hard_gate_open)
        if metrics.get("decision") != decision:
            findings.append(
                Finding(
                    "error",
                    "OMEGA7_DECISION",
                    f"decision must be {decision}",
                    "omega_metrics/decision",
                )
            )
        if assessment.get("state") != decision:
            findings.append(
                Finding(
                    "error",
                    "OMEGA7_STATE",
                    f"state must be {decision}",
                    "state",
                )
            )
    else:
        omega_g = 0.0
        omega_min = 0.0
        weakest = []

    if assessment.get("claim_allowed") is not False:
        findings.append(Finding("error", "OMEGA7_CLAIM_BOUNDARY", "claim_allowed must remain false", "claim_allowed"))

    try:
        assessment_display = str(assessment_path.relative_to(ROOT))
    except ValueError:
        assessment_display = str(assessment_path)

    payload = {
        "schema": "rll.omega7_operational_validation.v1",
        "assessment": assessment_display,
        "passed": not any(item.severity == "error" for item in findings),
        "findings": [asdict(item) for item in findings],
        "direction_count": len(directions),
        "hard_gate_open": actual_hard_gate_open,
        "omega_g": round(omega_g, 12),
        "omega_min": omega_min,
        "weakest_directions": weakest,
        "decision": assessment.get("state"),
        "claim_allowed": assessment.get("claim_allowed"),
        "boundary": (
            "Omega metrics are architectural routing conventions. Passing this validator does not "
            "validate RLL, prove physical geometry, establish model preference or authorize a scientific claim."
        ),
    }
    return findings, payload


def write_reports(payload: dict[str, Any], report_dir: Path = REPORT_DIR) -> None:
    report_dir.mkdir(parents=True, exist_ok=True)
    report_json = report_dir / "omega7_operational_report.json"
    report_md = report_dir / "OMEGA7_OPERATIONAL_REPORT.md"
    checksums = report_dir / "CHECKSUMS.sha256"

    report_json.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    lines = [
        "# Ω7 Operational Invariant Report",
        "",
        f"- passed: `{str(payload['passed']).lower()}`",
        f"- decision: `{payload['decision']}`",
        f"- omega_g: `{payload['omega_g']}`",
        f"- omega_min: `{payload['omega_min']}`",
        f"- weakest_directions: `{', '.join(payload['weakest_directions'])}`",
        f"- hard_gate_open: `{', '.join(payload['hard_gate_open'])}`",
        f"- claim_allowed: `{str(payload['claim_allowed']).lower()}`",
        f"- boundary: {payload['boundary']}",
        "",
        "## Findings",
        "",
    ]
    if payload["findings"]:
        lines.extend(["| severity | code | path | message |", "|---|---|---|---|"])
        for item in payload["findings"]:
            lines.append(
                f"| {item['severity']} | `{item['code']}` | `{item.get('path') or ''}` | {item['message']} |"
            )
    else:
        lines.append("No structural inconsistencies found.")
    report_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

    checksum_lines: list[str] = []
    for path in (report_json, report_md):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        checksum_lines.append(f"{digest}  {path.name}")
    checksums.write_text("\n".join(checksum_lines) + "\n", encoding="utf-8")


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--strict", action="store_true")
    parser.add_argument("--write-report", action="store_true")
    parser.add_argument("--assessment", type=Path, default=ASSESSMENT_PATH)
    parser.add_argument("--schema", type=Path, default=SCHEMA_PATH)
    parser.add_argument("--report-dir", type=Path, default=REPORT_DIR)
    args = parser.parse_args(list(argv) if argv is not None else None)

    assessment_path = args.assessment if args.assessment.is_absolute() else ROOT / args.assessment
    schema_path = args.schema if args.schema.is_absolute() else ROOT / args.schema
    report_dir = args.report_dir if args.report_dir.is_absolute() else ROOT / args.report_dir

    findings, payload = validate_assessment(assessment_path, schema_path)
    if args.write_report:
        write_reports(payload, report_dir)

    for finding in findings:
        print(f"{finding.severity.upper()} {finding.code}: {finding.path or '-'}: {finding.message}")
    if not findings:
        print(
            "Omega7 operational invariant OK: "
            f"decision={payload['decision']} omega_g={payload['omega_g']} "
            f"omega_min={payload['omega_min']} hard_gate_open={len(payload['hard_gate_open'])}"
        )

    has_errors = any(item.severity == "error" for item in findings)
    return 1 if args.strict and has_errors else 0


if __name__ == "__main__":
    sys.exit(main())
