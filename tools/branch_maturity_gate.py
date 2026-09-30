#!/usr/bin/env python3
"""Fail-closed branch maturity gate for the RLL promotion topology.

The gate evaluates repository-local implementation maturity. It distinguishes
operational policy files from tests, fixtures and documentation so adversarial
examples can prove a rejection rule without being mistaken for active state.
It never validates scientific claims and always emits ``claim_allowed=false``.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import subprocess
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Iterable

import yaml

SCHEMA = "rll.branch_maturity_gate.v1"
PROTECTED_BRANCHES = {"main", "rll/lab", "rll/integration", "rll/release"}
STAGE_BY_BASE = {
    "rll/lab": ("LAB", 40),
    "rll/integration": ("INTEGRATION", 60),
    "rll/release": ("RELEASE", 80),
    "main": ("MAIN", 90),
}
TEXT_LIMIT = 1_000_000
CLAIM_TRUE_RE = re.compile(
    r"(?im)^\s*claim_allowed\s*:\s*(?:true|yes|on|1)\s*(?:#.*)?$"
)
NEXT_STEP_RE = re.compile(
    r"(?i)(?:F_next|next[_ -]?(?:step|test|action|verification)|pr[oó]ximo passo)"
)
TOKEN_VAZIO_RE = re.compile(r"TOKEN_VAZIO")
POLICY_SUFFIXES = {".yml", ".yaml", ".json", ".toml"}
NON_OPERATIONAL_PREFIXES = (
    "tests/",
    "test/",
    "fixtures/",
    "examples/",
    "docs/",
    "papers/",
)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    message: str
    path: str = ""


@dataclass(frozen=True)
class Promotion:
    stage: str
    threshold: int
    valid: bool
    reason: str


def normalize_ref(ref: str) -> str:
    for prefix in ("refs/heads/", "origin/"):
        if ref.startswith(prefix):
            return ref[len(prefix) :]
    return ref


def promotion_for(head_ref: str, base_ref: str) -> Promotion:
    head = normalize_ref(head_ref)
    base = normalize_ref(base_ref)
    stage_info = STAGE_BY_BASE.get(base)
    if stage_info is None:
        return Promotion("UNKNOWN", 100, False, f"unsupported base branch: {base}")
    stage, threshold = stage_info
    if base == "rll/lab":
        valid = head not in PROTECTED_BRANCHES and head != base
        reason = (
            "feature/research branch enters laboratory"
            if valid
            else "laboratory accepts only non-protected source branches"
        )
    elif base == "rll/integration":
        valid = head == "rll/lab"
        reason = "laboratory promotes to integration" if valid else "integration accepts only rll/lab"
    elif base == "rll/release":
        valid = head == "rll/integration"
        reason = "integration promotes to release" if valid else "release accepts only rll/integration"
    else:
        valid = head == "rll/release"
        reason = "release promotes to main" if valid else "main accepts only rll/release"
    return Promotion(stage, threshold, valid, reason)


def changed_files(base_sha: str, head_sha: str) -> list[str]:
    result = subprocess.run(
        ["git", "diff", "--name-only", "--diff-filter=ACMRTUXB", base_sha, head_sha],
        check=True,
        capture_output=True,
        text=True,
    )
    return sorted({line.strip() for line in result.stdout.splitlines() if line.strip()})


def domains_for(path: str) -> set[str]:
    p = path.lower()
    domains: set[str] = set()
    if p.startswith(("data/", "datasets/", "results/", "validation/", "validacao_real/")):
        domains.add("data")
    if p.startswith(("src/", "models/", "analysis/", "scripts/", "tools/")) or p.endswith(
        (".c", ".h", ".py", ".rs", ".go")
    ):
        domains.add("implementation")
    if p.startswith("tests/") or "/test" in p or p.endswith(("_test.py", ".spec.ts", ".test.js")):
        domains.add("tests")
    if p.startswith((".github/", "governance/", "schemas/", "protocols/")):
        domains.add("governance")
    if p.startswith(("docs/", "papers/")) or Path(p).name.startswith("readme") or p.endswith(".md"):
        domains.add("documentation")
    if any(token in p for token in ("receipt", "evidence", "manifest", "checksum", "provenance", "ledger")):
        domains.add("evidence")
    return domains or {"other"}


def forbidden_path(path: str) -> bool:
    p = path.lower()
    name = Path(p).name
    forbidden_names = {
        ".env",
        "rclone.conf",
        "id_rsa",
        "id_ed25519",
        "credentials.json",
        "service-account.json",
        "secrets.yml",
        "secrets.yaml",
    }
    return (
        name in forbidden_names
        or p.startswith(".ssh/")
        or p.endswith((".pem", ".p12", ".pfx", ".key"))
    )


def claim_policy_surface(path: str) -> bool:
    """Return true only for structured operational state, never prose/test fixtures."""
    p = path.lower().lstrip("./")
    if p.startswith(NON_OPERATIONAL_PREFIXES):
        return False
    return Path(p).suffix in POLICY_SUFFIXES


def read_text(root: Path, rel: str) -> str | None:
    path = root / rel
    if not path.is_file() or path.stat().st_size > TEXT_LIMIT:
        return None
    raw = path.read_bytes()
    if b"\0" in raw:
        return None
    return raw.decode("utf-8", errors="replace")


def inspect_files(root: Path, files: Iterable[str]) -> tuple[dict[str, object], list[Finding]]:
    findings: list[Finding] = []
    domains: set[str] = set()
    token_vazio = 0
    next_step = 0
    evidence_files = 0
    yaml_files = 0
    policy_files = 0
    policy_scan_skipped = 0

    for rel in files:
        rel_domains = domains_for(rel)
        domains.update(rel_domains)
        if "evidence" in rel_domains:
            evidence_files += 1
        if forbidden_path(rel):
            findings.append(
                Finding(
                    "ERROR",
                    "FORBIDDEN_SENSITIVE_PATH",
                    "sensitive file path may not enter CI history",
                    rel,
                )
            )
        text = read_text(root, rel)
        if text is None:
            continue
        token_vazio += len(TOKEN_VAZIO_RE.findall(text))
        next_step += len(NEXT_STEP_RE.findall(text))

        if claim_policy_surface(rel):
            policy_files += 1
            if CLAIM_TRUE_RE.search(text):
                findings.append(
                    Finding(
                        "ERROR",
                        "CLAIM_ALLOWED_TRUE",
                        "claim_allowed=true is forbidden in operational promotion inputs",
                        rel,
                    )
                )
        elif CLAIM_TRUE_RE.search(text):
            policy_scan_skipped += 1

        if Path(rel).suffix.lower() in {".yml", ".yaml"}:
            yaml_files += 1
            try:
                list(yaml.safe_load_all(text))
            except yaml.YAMLError as exc:
                findings.append(
                    Finding("ERROR", "YAML_PARSE_ERROR", str(exc).splitlines()[0], rel)
                )

    return {
        "domains": sorted(domains),
        "token_vazio_count": token_vazio,
        "next_step_marker_count": next_step,
        "evidence_file_count": evidence_files,
        "yaml_file_count": yaml_files,
        "claim_policy_file_count": policy_files,
        "claim_policy_scan_skipped_count": policy_scan_skipped,
    }, findings


def status_ok(value: str) -> bool:
    return value.lower() in {"success", "pass", "passed", "ok"}


def evaluate(
    *,
    root: Path,
    head_ref: str,
    base_ref: str,
    base_sha: str,
    head_sha: str,
    tests_status: str,
    architecture_status: str,
    docs_status: str,
    workflow: str,
    job: str,
    files: list[str] | None = None,
) -> dict[str, object]:
    promotion = promotion_for(head_ref, base_ref)
    files = changed_files(base_sha, head_sha) if files is None else sorted(set(files))
    inspection, findings = inspect_files(root, files)
    domains = set(inspection["domains"])

    if not promotion.valid:
        findings.append(Finding("ERROR", "INVALID_BRANCH_TRANSITION", promotion.reason))
    if not files:
        findings.append(Finding("ERROR", "EMPTY_CHANGESET", "promotion has no changed files"))
    if not status_ok(tests_status):
        findings.append(Finding("ERROR", "TESTS_NOT_PASSING", f"test status: {tests_status}"))
    if not status_ok(architecture_status):
        findings.append(
            Finding("ERROR", "ARCHITECTURE_NOT_PASSING", f"architecture status: {architecture_status}")
        )
    if not status_ok(docs_status):
        findings.append(
            Finding(
                "ERROR",
                "WORKFLOW_DOCS_NOT_PASSING",
                f"documentation contract status: {docs_status}",
            )
        )

    scientific_change = bool(domains & {"data", "implementation"})
    explicit_gap = inspection["token_vazio_count"] > 0 and inspection["next_step_marker_count"] > 0
    evidence_present = inspection["evidence_file_count"] > 0
    if promotion.stage in {"RELEASE", "MAIN"} and scientific_change and not (
        evidence_present or explicit_gap
    ):
        findings.append(
            Finding(
                "ERROR",
                "EVIDENCE_OR_EXPLICIT_GAP_REQUIRED",
                "release/main scientific changes require evidence/provenance or TOKEN_VAZIO with a verifiable next step",
            )
        )

    if (
        "governance" in domains
        and ".github/workflow-contract.yml" not in files
        and promotion.stage in {"RELEASE", "MAIN"}
    ):
        findings.append(
            Finding(
                "ERROR",
                "GOVERNANCE_CONTRACT_TOUCH_REQUIRED",
                "release/main governance changes must touch .github/workflow-contract.yml",
            )
        )

    score = {
        "topology": 20 if promotion.valid else 0,
        "semantic_amplitude": min(20, 5 + 5 * min(3, len(domains))) if files else 0,
        "validation": 20 if status_ok(tests_status) else 0,
        "evidence": 20 if (not scientific_change or evidence_present) else (15 if explicit_gap else 0),
        "governance": 20
        if status_ok(architecture_status)
        and status_ok(docs_status)
        and not any(
            item.code
            in {"FORBIDDEN_SENSITIVE_PATH", "CLAIM_ALLOWED_TRUE", "YAML_PARSE_ERROR"}
            for item in findings
        )
        else 0,
    }
    total = sum(score.values())
    blocking = [item for item in findings if item.severity == "ERROR"]
    passed = not blocking and total >= promotion.threshold
    decision = f"PASS_{promotion.stage}" if passed else "BLOCKED"

    digest = hashlib.sha256()
    digest.update(normalize_ref(base_ref).encode())
    digest.update(b"\0")
    digest.update(normalize_ref(head_ref).encode())
    for rel in files:
        digest.update(b"\0")
        digest.update(rel.encode())
        path = root / rel
        if path.is_file():
            digest.update(b"\0")
            digest.update(hashlib.sha256(path.read_bytes()).digest())

    return {
        "schema": SCHEMA,
        "commit_sha": head_sha,
        "workflow": workflow,
        "job": job,
        "claim_allowed": False,
        "publication_effect": "NONE",
        "inputs_sha256": digest.hexdigest(),
        "decision": decision,
        "stage": promotion.stage,
        "threshold": promotion.threshold,
        "maturity_score": total,
        "score_components": score,
        "head_ref": normalize_ref(head_ref),
        "base_ref": normalize_ref(base_ref),
        "changed_files": files,
        "inspection": inspection,
        "residuals": [asdict(item) for item in findings],
        "next_decision": (
            "PROMOTION_REVIEW_ALLOWED" if passed else "RESOLVE_RESIDUALS_AND_REEXECUTE"
        ),
        "scientific_boundary": "Structural maturity does not validate a theory, dataset rights, model preference, or independent replication.",
    }


def write_reports(output_dir: Path, payload: dict[str, object]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    (output_dir / "branch_maturity_receipt.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    lines = [
        "# RLL Branch Maturity Receipt",
        "",
        f"- decision: `{payload['decision']}`",
        f"- stage: `{payload['stage']}`",
        f"- score: `{payload['maturity_score']}/{payload['threshold']}`",
        f"- transition: `{payload['head_ref']} → {payload['base_ref']}`",
        "- claim_allowed: `false`",
        "- publication_effect: `NONE`",
        "",
        "## Score",
        "",
        "| dimension | points |",
        "|---|---:|",
    ]
    for key, value in dict(payload["score_components"]).items():
        lines.append(f"| `{key}` | {value} |")
    lines.extend(["", "## Residuals", ""])
    residuals = list(payload["residuals"])
    if residuals:
        lines.extend(["| severity | code | path | message |", "|---|---|---|---|"])
        for item in residuals:
            lines.append(
                f"| {item['severity']} | `{item['code']}` | `{item['path']}` | {item['message']} |"
            )
    else:
        lines.append("No blocking residuals.")
    (output_dir / "BRANCH_MATURITY_REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, default=Path.cwd())
    parser.add_argument("--head-ref", required=True)
    parser.add_argument("--base-ref", required=True)
    parser.add_argument("--base-sha", required=True)
    parser.add_argument("--head-sha", required=True)
    parser.add_argument("--tests-status", required=True)
    parser.add_argument("--architecture-status", required=True)
    parser.add_argument("--docs-status", required=True)
    parser.add_argument("--workflow", required=True)
    parser.add_argument("--job", required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    payload = evaluate(
        root=args.root,
        head_ref=args.head_ref,
        base_ref=args.base_ref,
        base_sha=args.base_sha,
        head_sha=args.head_sha,
        tests_status=args.tests_status,
        architecture_status=args.architecture_status,
        docs_status=args.docs_status,
        workflow=args.workflow,
        job=args.job,
    )
    write_reports(args.output_dir, payload)
    print(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if payload["decision"] != "BLOCKED" else 3


if __name__ == "__main__":
    raise SystemExit(main())
