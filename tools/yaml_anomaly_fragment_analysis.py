#!/usr/bin/env python3
"""Distribute YAML anomaly findings into explanatory fragments and aggregate receipts.

The input is the machine-readable output from tools/deep_yaml_audit.py.
This tool never promotes a runtime or scientific causal claim from static CI structure.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from collections import Counter
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

FRAGMENT_SCHEMA = "rll.yaml_anomaly_fragment.v1"
AGGREGATE_SCHEMA = "rll.yaml_anomaly_explanatory_aggregate.v1"

LENSES = (
    "startup_preflight",
    "authority_security",
    "runtime_operability",
    "provenance_inventory",
    "scientific_boundary",
    "format_structure",
    "unclassified",
)

STARTUP_CODES = {
    "YAML_PARSE_FAILURE",
    "DUPLICATE_YAML_KEY",
    "WORKFLOW_TOP_LEVEL_NOT_MAPPING",
    "WORKFLOW_REQUIRED_KEY_MISSING",
    "JOBS_EMPTY",
    "JOB_NOT_MAPPING",
    "RUNNER_MISSING",
    "JOB_STEPS_EMPTY",
}
SECURITY_CODES = {
    "PULL_REQUEST_TARGET_FORBIDDEN",
    "PERMISSION_EXCEEDS_CLASS",
    "JOB_WRITE_PERMISSION_UNGOVERNED",
    "WRITE_JOB_NOT_MANUAL_DISPATCH_ONLY",
    "MUTABLE_ACTION_REFERENCE",
    "CHECKOUT_PERSIST_DEFAULT",
    "CHECKOUT_CREDENTIALS_PERSIST",
    "UNTRUSTED_EXPRESSION_IN_RUN",
    "CODEQL_ACTION_REVISION_DRIFT",
}
OPERABILITY_CODES = {
    "TOP_LEVEL_PERMISSIONS_MISSING",
    "CONCURRENCY_MISSING",
    "PUSH_PR_PATH_FILTER_DRIFT",
    "MUTABLE_RUNNER_LABEL",
    "JOB_TIMEOUT_MISSING",
    "ARTIFACT_NOT_ALWAYS_UPLOADED",
    "ARTIFACT_RETENTION_UNDECLARED",
    "INLINE_PROGRAM_OVERSIZED",
    "FAILURE_SWALLOWED",
    "DEPENDENCIES_UNLOCKED",
    "CONTINUE_ON_ERROR",
    "MANAGED_RECEIPT_UPLOAD_MISSING",
    "MANAGED_CLAIM_BOUNDARY_MISSING",
}
PROVENANCE_CODES = {
    "VERSIONED_INVENTORY_STALE",
    "INVENTORY_SUMMARY_UNREADABLE",
    "IDENTICAL_YAML_DUPLICATES",
    "REFERENCED_PATH_MISSING",
    "DUPLICATE_IDS",
}
SCIENTIFIC_CODES = {
    "CLAIM_ALLOWED_TRUE",
    "SCIENTIFIC_RESULT_OR_PARAMETER_EMBEDDED",
}
FORMAT_CODES = {
    "UTF8_DECODE_FAILURE",
    "UTF8_BOM",
    "CRLF_LINE_ENDINGS",
    "EMPTY_YAML",
    "MULTI_DOCUMENT_YAML",
    "NULL_DOCUMENT",
}

ZERO_JOB_COMPATIBLE_CODES = STARTUP_CODES | {
    "UNTRUSTED_EXPRESSION_IN_RUN",
}


def _now_iso() -> str:
    return datetime.now(tz=timezone.utc).isoformat().replace("+00:00", "Z")


def _env_identity() -> dict[str, str]:
    def value(name: str) -> str:
        return os.environ.get(name, "TOKEN_VAZIO")
    return {
        "generated_at_utc": _now_iso(),
        "github_sha": value("GITHUB_SHA"),
        "github_run_id": value("GITHUB_RUN_ID"),
        "github_run_attempt": value("GITHUB_RUN_ATTEMPT"),
        "github_workflow": value("GITHUB_WORKFLOW"),
        "github_job": value("GITHUB_JOB"),
    }


def classify_code(code: str) -> str:
    if code in STARTUP_CODES:
        return "startup_preflight"
    if code in SECURITY_CODES:
        return "authority_security"
    if code in OPERABILITY_CODES:
        return "runtime_operability"
    if code in PROVENANCE_CODES:
        return "provenance_inventory"
    if code in SCIENTIFIC_CODES:
        return "scientific_boundary"
    if code in FORMAT_CODES:
        return "format_structure"
    return "unclassified"


def fragment_id(item: dict[str, Any]) -> str:
    canonical = "|".join(
        str(item.get(key, ""))
        for key in ("severity", "code", "path", "job", "step", "message")
    )
    return hashlib.sha256(canonical.encode("utf-8")).hexdigest()[:24]


def explanatory_status(items: list[dict[str, Any]]) -> str:
    if any(str(item.get("code", "")) in ZERO_JOB_COMPATIBLE_CODES for item in items):
        return "ZERO_JOB_COMPATIBLE_STATIC_SIGNATURE"
    if items:
        return "STATIC_ANOMALY_NOT_ZERO_JOB_SPECIFIC"
    return "NO_FINDINGS_FOR_LENS"


def build_fragment_payload(source: dict[str, Any], lens: str) -> dict[str, Any]:
    if lens not in LENSES:
        raise ValueError(f"unsupported lens: {lens}")
    residuals = source.get("residuals", [])
    if not isinstance(residuals, list):
        raise ValueError("source residuals must be a list")

    selected: list[dict[str, Any]] = []
    for raw in residuals:
        if not isinstance(raw, dict):
            continue
        code = str(raw.get("code", ""))
        if classify_code(code) == lens:
            item = dict(raw)
            item["fragment_id"] = fragment_id(item)
            selected.append(item)
    selected.sort(key=lambda x: (
        str(x.get("path", "")),
        str(x.get("job", "")),
        str(x.get("step", "")),
        str(x.get("code", "")),
        x["fragment_id"],
    ))

    code_counts = Counter(str(item.get("code", "")) for item in selected)
    path_counts = Counter(str(item.get("path", "")) for item in selected)
    zero_job_count = sum(
        str(item.get("code", "")) in ZERO_JOB_COMPATIBLE_CODES for item in selected
    )

    return {
        "schema": FRAGMENT_SCHEMA,
        "semantic_role": "ACTION_EXECUTION_TO_RESEARCH_FRAGMENT",
        "lens": lens,
        "source_schema": source.get("schema", "TOKEN_VAZIO"),
        "source_commit_sha": source.get("commit_sha", "TOKEN_VAZIO"),
        "source_decision": source.get("decision", "TOKEN_VAZIO"),
        "temporal_identity": _env_identity(),
        "observation_count": len(selected),
        "zero_job_compatible_observation_count": zero_job_count,
        "explanatory_status": explanatory_status(selected),
        "causal_claim_allowed": False,
        "claim_allowed": False,
        "publication_effect": "NONE",
        "code_counts": dict(sorted(code_counts.items())),
        "top_paths": [{"path": p, "count": n} for p, n in path_counts.most_common(20)],
        "fragments": selected,
        "boundary": (
            "Static YAML/CI findings may be explanatory candidates, but exact temporal identity "
            "or static compatibility alone does not prove the runtime cause of a zero-job event."
        ),
    }


def write_fragment(source_path: Path, lens: str, output_dir: Path) -> Path:
    source = json.loads(source_path.read_text(encoding="utf-8"))
    payload = build_fragment_payload(source, lens)
    output_dir.mkdir(parents=True, exist_ok=True)
    target = output_dir / f"{lens}.json"
    target.write_text(
        json.dumps(payload, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )
    return target


def aggregate_payload(fragment_payloads: list[dict[str, Any]]) -> dict[str, Any]:
    by_lens = {
        str(item.get("lens")): item
        for item in fragment_payloads
        if isinstance(item, dict)
    }
    missing = [lens for lens in LENSES if lens not in by_lens]
    all_fragments: dict[str, dict[str, Any]] = {}
    zero_job_compatible = 0
    total_observations = 0

    lens_summaries = []
    for lens in LENSES:
        payload = by_lens.get(lens)
        if payload is None:
            lens_summaries.append({
                "lens": lens,
                "state": "TOKEN_VAZIO_FRAGMENT_MISSING",
                "observation_count": 0,
                "zero_job_compatible_observation_count": 0,
            })
            continue
        observations = int(payload.get("observation_count", 0))
        compatible = int(payload.get("zero_job_compatible_observation_count", 0))
        total_observations += observations
        zero_job_compatible += compatible
        for fragment in payload.get("fragments", []):
            if isinstance(fragment, dict) and fragment.get("fragment_id"):
                all_fragments[str(fragment["fragment_id"])] = fragment
        lens_summaries.append({
            "lens": lens,
            "state": payload.get("explanatory_status", "TOKEN_VAZIO"),
            "observation_count": observations,
            "zero_job_compatible_observation_count": compatible,
        })

    source_commits = sorted({
        str(item.get("source_commit_sha"))
        for item in fragment_payloads
        if item.get("source_commit_sha") not in (None, "", "TOKEN_VAZIO")
    })
    source_commit = (
        source_commits[0]
        if len(source_commits) == 1
        else "TOKEN_VAZIO_MULTIPLE_SOURCE_COMMITS"
        if source_commits
        else "TOKEN_VAZIO"
    )

    return {
        "schema": AGGREGATE_SCHEMA,
        "semantic_roles": {
            "action_executor": "fragment and distribute static anomalies",
            "research_action": "compare explanatory lenses without promoting causality",
        },
        "source_commit_sha": source_commit,
        "temporal_identity": _env_identity(),
        "expected_lenses": list(LENSES),
        "missing_lenses": missing,
        "lens_summaries": lens_summaries,
        "total_fragment_observations": total_observations,
        "unique_fragment_count": len(all_fragments),
        "zero_job_compatible_fragment_count": zero_job_compatible,
        "causal_conclusion": "TOKEN_VAZIO_CAUSAL_LINK_NOT_ESTABLISHED",
        "decision": "REVIEW_REQUIRED" if missing or zero_job_compatible else "PASS_WITH_RESIDUALS",
        "claim_allowed": False,
        "causal_claim_allowed": False,
        "publication_effect": "NONE",
        "invariants": [
            "SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM",
            "TEMPORAL_IDENTITY != CAUSAL_EXPLANATION",
            "STATIC_SIGNATURE != ZERO_JOB_CAUSE_PROVEN",
            "TOKEN_VAZIO != PASS",
        ],
    }


def aggregate_dir(
    input_dir: Path,
    output_dir: Path,
) -> tuple[Path, dict[str, Any]]:
    payloads = []
    for path in sorted(input_dir.rglob("*.json")):
        try:
            item = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        if item.get("schema") == FRAGMENT_SCHEMA:
            payloads.append(item)

    aggregate = aggregate_payload(payloads)
    output_dir.mkdir(parents=True, exist_ok=True)
    json_path = output_dir / "yaml_anomaly_explanatory_aggregate.json"
    json_path.write_text(
        json.dumps(aggregate, indent=2, sort_keys=True, ensure_ascii=False) + "\n",
        encoding="utf-8",
    )

    md = [
        "# YAML anomaly fragments — explanatory aggregate",
        "",
        f"- source_commit_sha: {aggregate['source_commit_sha']}",
        f"- total_fragment_observations: {aggregate['total_fragment_observations']}",
        f"- unique_fragment_count: {aggregate['unique_fragment_count']}",
        f"- zero_job_compatible_fragment_count: {aggregate['zero_job_compatible_fragment_count']}",
        f"- causal_conclusion: {aggregate['causal_conclusion']}",
        f"- missing_lenses: {', '.join(aggregate['missing_lenses']) if aggregate['missing_lenses'] else 'none'}",
        "- claim_allowed: false",
        "",
        "| lens | state | findings | zero-job compatible |",
        "|---|---|---:|---:|",
    ]
    for row in aggregate["lens_summaries"]:
        md.append(
            f"| {row['lens']} | {row['state']} | {row['observation_count']} | "
            f"{row['zero_job_compatible_observation_count']} |"
        )
    md += [
        "",
        "## Boundary",
        "",
        "Exact temporal identity preserves custody, but it is not by itself a causal explanation. "
        "A zero-job cause requires matching provider/runtime evidence, not only a static YAML signature.",
    ]
    (output_dir / "YAML_ANOMALY_EXPLANATORY_AGGREGATE.md").write_text(
        "\n".join(md) + "\n",
        encoding="utf-8",
    )
    return json_path, aggregate


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    sub = parser.add_subparsers(dest="command", required=True)

    fragment = sub.add_parser("fragment")
    fragment.add_argument("--input", type=Path, required=True)
    fragment.add_argument("--lens", choices=LENSES, required=True)
    fragment.add_argument("--output-dir", type=Path, required=True)

    aggregate = sub.add_parser("aggregate")
    aggregate.add_argument("--input-dir", type=Path, required=True)
    aggregate.add_argument("--output-dir", type=Path, required=True)
    aggregate.add_argument("--enforce-complete", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.command == "fragment":
        target = write_fragment(args.input, args.lens, args.output_dir)
        payload = json.loads(target.read_text(encoding="utf-8"))
        print(json.dumps({
            "lens": payload["lens"],
            "observation_count": payload["observation_count"],
            "zero_job_compatible_observation_count": payload[
                "zero_job_compatible_observation_count"
            ],
            "explanatory_status": payload["explanatory_status"],
        }, sort_keys=True))
        return 0

    _, aggregate = aggregate_dir(args.input_dir, args.output_dir)
    print(json.dumps({
        "decision": aggregate["decision"],
        "missing_lenses": aggregate["missing_lenses"],
        "zero_job_compatible_fragment_count": aggregate[
            "zero_job_compatible_fragment_count"
        ],
    }, sort_keys=True))
    if args.enforce_complete and aggregate["missing_lenses"]:
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
