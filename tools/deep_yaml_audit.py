#!/usr/bin/env python3
"""Deep, report-only audit for every YAML/YML file in the repository.

The audit separates parseability, workflow security/operability, generic manifest
coherence, and cross-file drift. It never promotes a scientific claim.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import re
import sys
from collections import Counter, defaultdict
from dataclasses import asdict, dataclass, field
from pathlib import Path
from typing import Any, Iterable

import yaml

SCHEMA = "rll.yaml_deep_audit.v1"
WORKFLOW_ROOT = Path(".github/workflows")
EXCLUDED_PARTS = {".git", ".venv", "venv", "node_modules", "__pycache__"}
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
ACTION_RE = re.compile(r"^(?!\./)([^/\s]+/[^@\s]+)@(.+)$")
EXPRESSION_RE = re.compile(r"\$\{\{\s*([^}]+?)\s*\}\}")
DANGEROUS_RUN_CONTEXT_RE = re.compile(
    r"^(?:github\.event(?:\.|$)|github\.(?:head_ref|ref_name|actor|triggering_actor)|inputs\.|github\.event\.inputs\.)",
    re.IGNORECASE,
)
SCIENTIFIC_LITERAL_RE = re.compile(
    r"(?i)(?:chi2|χ²|aic|bic|ln[_ ]?b|bayes|omega[_-]?[a-z0-9]*|h0|z_t|w_t|sigma8|fsigma8)"
    r"[^\n]{0,80}(?:[:=]\s*|\"\s*:\s*)[-+]?\d+(?:\.\d+)?(?:[eE][-+]?\d+)?"
)
SWALLOWED_FAILURE_RE = re.compile(r"(?:\|\|\s*true\b|\|\|\s*\{|2>/dev/null\s*\|\|\s*true)")
LOCAL_PATH_KEYS = {
    "script", "validator", "companion_scanner", "companion_table", "companion_doc",
    "contract", "schema_path", "source_file", "source_files", "config_path", "manifest_path",
}
SEVERITY_ORDER = {"ERROR": 0, "HIGH": 1, "MEDIUM": 2, "LOW": 3, "INFO": 4}


class DuplicateKeyError(ValueError):
    pass


class UniqueSafeLoader(yaml.SafeLoader):
    pass


class UniqueBaseLoader(yaml.BaseLoader):
    pass


def _construct_unique_mapping(loader: yaml.Loader, node: yaml.MappingNode, deep: bool = False) -> dict[Any, Any]:
    if hasattr(loader, "flatten_mapping"):
        loader.flatten_mapping(node)
    result: dict[Any, Any] = {}
    for key_node, value_node in node.value:
        key = loader.construct_object(key_node, deep=deep)
        try:
            duplicate = key in result
        except TypeError as exc:
            raise DuplicateKeyError(f"unhashable mapping key at line {key_node.start_mark.line + 1}") from exc
        if duplicate:
            raise DuplicateKeyError(
                f"duplicate key {key!r} at line {key_node.start_mark.line + 1}, column {key_node.start_mark.column + 1}"
            )
        result[key] = loader.construct_object(value_node, deep=deep)
    return result


UniqueSafeLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping)
UniqueBaseLoader.add_constructor(yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG, _construct_unique_mapping)


@dataclass(frozen=True)
class Finding:
    severity: str
    code: str
    path: str
    message: str
    job: str = ""
    step: str = ""


@dataclass
class FileRecord:
    path: str
    category: str
    sha256: str
    bytes: int
    lines: int
    documents: int = 0
    syntax_status: str = "UNKNOWN"
    top_level_type: str = ""
    token_vazio_count: int = 0
    synthetic_marker_count: int = 0
    findings: list[Finding] = field(default_factory=list)

    @property
    def highest_severity(self) -> str:
        if not self.findings:
            return "OK"
        return min((item.severity for item in self.findings), key=lambda x: SEVERITY_ORDER[x])


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def iter_yaml(repo_root: Path) -> Iterable[Path]:
    paths = [*repo_root.rglob("*.yml"), *repo_root.rglob("*.yaml")]
    for path in sorted(set(paths)):
        if not any(part in EXCLUDED_PARTS for part in path.parts):
            yield path


def category_for(rel: str) -> str:
    p = Path(rel)
    if p.parent == WORKFLOW_ROOT:
        return "github_workflow"
    if "fixtures" in p.parts or "examples" in p.parts and "invalid" in p.name:
        return "test_fixture"
    if rel.startswith(".github/To_add/") or rel.startswith("to_Add/"):
        return "staging_or_migration"
    if rel.startswith("docs/yml/"):
        return "governance_or_document_registry"
    if rel.startswith("data/results/") or rel.startswith("results/"):
        return "result_or_receipt_manifest"
    if rel.startswith("data/real/") or rel.startswith("validacao_real/"):
        return "real_data_manifest"
    if rel.startswith("schemas/"):
        return "schema_manifest"
    if rel.startswith("protocols/"):
        return "protocol"
    return "configuration_or_ledger"


def finding(record: FileRecord, severity: str, code: str, message: str, job: str = "", step: str = "") -> None:
    record.findings.append(Finding(severity, code, record.path, message, job, step))


def parse_documents(text: str, workflow: bool) -> list[Any]:
    loader = UniqueBaseLoader if workflow else UniqueSafeLoader
    return list(yaml.load_all(text, Loader=loader))


def walk(value: Any, path: tuple[str, ...] = ()) -> Iterable[tuple[tuple[str, ...], Any]]:
    yield path, value
    if isinstance(value, dict):
        for key, child in value.items():
            yield from walk(child, (*path, str(key)))
    elif isinstance(value, list):
        for index, child in enumerate(value):
            yield from walk(child, (*path, str(index)))


def is_local_path(value: str) -> bool:
    if not value or value.startswith(("http://", "https://", "doi:", "urn:", "${{", "/")):
        return False
    if any(ch in value for ch in ("*", "?", "[", "]", "|", "\n")):
        return False
    return "/" in value or Path(value).suffix.lower() in {
        ".py", ".sh", ".yml", ".yaml", ".json", ".csv", ".md", ".txt", ".toml"
    }


def audit_generic(record: FileRecord, repo_root: Path, docs: list[Any], text: str) -> None:
    if text.startswith("\ufeff"):
        finding(record, "LOW", "UTF8_BOM", "UTF-8 BOM present; normalize for deterministic hashing/tool compatibility")
    if "\r\n" in text:
        finding(record, "LOW", "CRLF_LINE_ENDINGS", "CRLF line endings present")
    if not text.strip():
        finding(record, "HIGH", "EMPTY_YAML", "YAML file is empty")
        return
    if len(docs) > 1:
        finding(record, "MEDIUM", "MULTI_DOCUMENT_YAML", f"contains {len(docs)} YAML documents")
    for doc_index, doc in enumerate(docs):
        if doc is None:
            finding(record, "MEDIUM", "NULL_DOCUMENT", f"document {doc_index + 1} resolves to null")
            continue
        if doc_index == 0:
            record.top_level_type = type(doc).__name__
        for key_path, value in walk(doc):
            leaf = key_path[-1].lower() if key_path else ""
            if leaf == "claim_allowed" and str(value).strip().lower() == "true":
                severity = "INFO" if record.category == "test_fixture" else "ERROR"
                finding(record, severity, "CLAIM_ALLOWED_TRUE", f"claim_allowed=true at {'/'.join(key_path)}")
            if leaf in LOCAL_PATH_KEYS:
                candidates = value if isinstance(value, list) else [value]
                for candidate in candidates:
                    if isinstance(candidate, str) and is_local_path(candidate):
                        target = repo_root / candidate
                        if not target.exists():
                            severity = "INFO" if record.category == "test_fixture" else "MEDIUM"
                            finding(record, severity, "REFERENCED_PATH_MISSING", f"referenced local path does not exist: {candidate}")
        for key_path, value in walk(doc):
            if not isinstance(value, list):
                continue
            ids = [str(item.get("id")) for item in value if isinstance(item, dict) and item.get("id") is not None]
            duplicates = sorted(k for k, n in Counter(ids).items() if n > 1)
            if duplicates:
                finding(record, "HIGH", "DUPLICATE_IDS", f"duplicate id values under {'/'.join(key_path) or '<root>'}: {duplicates}")


def mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def list_value(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def bool_text(value: Any) -> bool:
    return str(value).strip().lower() == "true"


def trigger_names(value: Any) -> set[str]:
    if isinstance(value, dict):
        return {str(k) for k in value}
    if isinstance(value, list):
        return {str(x) for x in value}
    if isinstance(value, str):
        return {value}
    return set()


def recursively_contains_value(value: Any, needles: tuple[str, ...]) -> bool:
    for _, child in walk(value):
        if isinstance(child, str):
            low = child.lower()
            if any(needle in low for needle in needles):
                return True
    return False


def load_contract(repo_root: Path) -> dict[str, Any]:
    path = repo_root / ".github/workflow-architecture/invariants.v1.yml"
    if not path.exists():
        return {}
    docs = parse_documents(path.read_text(encoding="utf-8"), workflow=False)
    return docs[0] if docs and isinstance(docs[0], dict) else {}


def audit_workflow(record: FileRecord, repo_root: Path, doc: Any, contract: dict[str, Any]) -> None:
    if not isinstance(doc, dict):
        finding(record, "ERROR", "WORKFLOW_TOP_LEVEL_NOT_MAPPING", "workflow top level must be a mapping")
        return
    for key in ("name", "on", "jobs"):
        if key not in doc:
            finding(record, "ERROR", "WORKFLOW_REQUIRED_KEY_MISSING", f"missing top-level key: {key}")

    events = trigger_names(doc.get("on"))
    if "pull_request_target" in events:
        finding(record, "ERROR", "PULL_REQUEST_TARGET_FORBIDDEN", "pull_request_target is forbidden without a reviewed exception")

    managed = mapping(mapping(contract.get("managed_workflows")).get(record.path))
    workflow_class = str(managed.get("class", "legacy"))
    requirements = {str(x) for x in list_value(managed.get("require"))}
    classes = mapping(contract.get("workflow_classes"))
    class_policy = mapping(classes.get(workflow_class))

    permissions = mapping(doc.get("permissions"))
    if not permissions:
        finding(record, "HIGH", "TOP_LEVEL_PERMISSIONS_MISSING", "workflow does not declare explicit top-level permissions")
    allowed_permissions = mapping(class_policy.get("allowed_permissions"))
    for permission, level in permissions.items():
        declared = str(level).lower()
        allowed = str(allowed_permissions.get(permission, "none")).lower()
        if declared == "write" and allowed != "write":
            finding(record, "ERROR" if managed else "HIGH", "PERMISSION_EXCEEDS_CLASS", f"{permission}: write exceeds class {workflow_class!r}")
    if class_policy.get("manual_dispatch_only") and events != {"workflow_dispatch"}:
        finding(record, "ERROR", "MANUAL_DISPATCH_ONLY_VIOLATION", f"class {workflow_class} permits only workflow_dispatch; found {sorted(events)}")

    if not doc.get("concurrency"):
        finding(record, "HIGH" if managed else "MEDIUM", "CONCURRENCY_MISSING", "workflow has no concurrency policy")

    on_map = mapping(doc.get("on"))
    push_paths = set(list_value(mapping(on_map.get("push")).get("paths")))
    pr_paths = set(list_value(mapping(on_map.get("pull_request")).get("paths")))
    if push_paths and pr_paths and push_paths != pr_paths:
        finding(record, "MEDIUM", "PUSH_PR_PATH_FILTER_DRIFT", f"push and pull_request paths differ ({len(push_paths)} vs {len(pr_paths)})")

    jobs = mapping(doc.get("jobs"))
    if not jobs:
        finding(record, "ERROR", "JOBS_EMPTY", "jobs must be a non-empty mapping")
        return

    for job_id, raw_job in jobs.items():
        job = mapping(raw_job)
        if not job:
            finding(record, "ERROR", "JOB_NOT_MAPPING", "job must be a mapping", str(job_id))
            continue
        if "uses" in job:
            continue
        if "runs-on" not in job:
            finding(record, "ERROR", "RUNNER_MISSING", "job lacks runs-on or reusable workflow uses", str(job_id))
        runner = str(job.get("runs-on", ""))
        if runner.endswith("-latest"):
            finding(record, "LOW", "MUTABLE_RUNNER_LABEL", f"runner label is mutable: {runner}", str(job_id))
        if job.get("timeout-minutes") is None:
            finding(record, "HIGH" if managed else "MEDIUM", "JOB_TIMEOUT_MISSING", "runner job has no timeout-minutes", str(job_id))

        effective_permissions = mapping(job.get("permissions")) or permissions
        always_allowed = mapping(class_policy.get("allowed_permissions"))
        manual_allowed = mapping(class_policy.get("manual_write_permissions"))
        security = mapping(contract.get("security"))
        write_classes = {
            str(value)
            for value in list_value(
                security.get("write_permissions_require_explicit_workflow_class")
            )
        }
        job_condition = str(job.get("if", ""))
        manual_dispatch_guarded = events == {"workflow_dispatch"} or (
            re.search(
                r"(?:github\.event_name\s*==\s*['\"]workflow_dispatch['\"]|"
                r"['\"]workflow_dispatch['\"]\s*==\s*github\.event_name)",
                job_condition,
            )
            is not None
            and "||" not in job_condition
        )
        for permission, level in effective_permissions.items():
            if str(level).lower() != "write":
                continue
            permanently_allowed = str(always_allowed.get(permission, "none")).lower() == "write"
            manually_allowed = str(manual_allowed.get(permission, "none")).lower() == "write"
            class_is_explicit = workflow_class in write_classes
            if not class_is_explicit or not (permanently_allowed or manually_allowed):
                finding(
                    record,
                    "ERROR" if managed else "HIGH",
                    "JOB_WRITE_PERMISSION_UNGOVERNED",
                    f"job grants {permission}: write without an explicit class permission contract",
                    str(job_id),
                )
                continue
            if (manually_allowed or bool_text(class_policy.get("write_jobs_manual_dispatch_only"))) and not manual_dispatch_guarded:
                finding(
                    record,
                    "ERROR" if managed else "HIGH",
                    "WRITE_JOB_NOT_MANUAL_DISPATCH_ONLY",
                    f"job grants {permission}: write but is not provably restricted to workflow_dispatch",
                    str(job_id),
                )

        steps = list_value(job.get("steps"))
        if not steps:
            finding(record, "ERROR", "JOB_STEPS_EMPTY", "runner job has no steps", str(job_id))
            continue
        codeql_action_refs: set[str] = set()
        for index, raw_step in enumerate(steps):
            step = mapping(raw_step)
            step_name = str(step.get("name", f"step-{index}"))
            uses = str(step.get("uses", ""))
            if uses:
                match = ACTION_RE.match(uses)
                if match and not FULL_SHA_RE.fullmatch(match.group(2)):
                    finding(record, "HIGH", "MUTABLE_ACTION_REFERENCE", f"external action not pinned to full SHA: {uses}", str(job_id), step_name)
                if match and uses.startswith("github/codeql-action/"):
                    codeql_action_refs.add(match.group(2))
                if uses.startswith("actions/checkout@"):
                    persist = mapping(step.get("with")).get("persist-credentials")
                    if persist is None:
                        finding(record, "MEDIUM", "CHECKOUT_PERSIST_DEFAULT", "checkout omits persist-credentials: false", str(job_id), step_name)
                    elif bool_text(persist):
                        finding(record, "HIGH", "CHECKOUT_CREDENTIALS_PERSIST", "checkout persists credentials", str(job_id), step_name)
                if uses.startswith("actions/upload-artifact@"):
                    if str(step.get("if", "")).replace(" ", "") != "always()":
                        finding(record, "MEDIUM", "ARTIFACT_NOT_ALWAYS_UPLOADED", "artifact/receipt can be lost when a prior step fails", str(job_id), step_name)
                    if mapping(step.get("with")).get("retention-days") is None:
                        finding(record, "LOW", "ARTIFACT_RETENTION_UNDECLARED", "artifact retention-days is not explicit", str(job_id), step_name)

            run = step.get("run")
            if run is None:
                continue
            run_text = str(run)
            lines = len(run_text.splitlines())
            limit = 24 if managed and "externalized_algorithm" in requirements else 50
            if lines > limit:
                finding(record, "HIGH" if managed else "MEDIUM", "INLINE_PROGRAM_OVERSIZED", f"inline run block has {lines} lines; limit is {limit}", str(job_id), step_name)
            for expr in EXPRESSION_RE.findall(run_text):
                normalized = expr.strip()
                if DANGEROUS_RUN_CONTEXT_RE.match(normalized):
                    finding(record, "HIGH", "UNTRUSTED_EXPRESSION_IN_RUN", f"expression interpolated directly into shell/code: {normalized}", str(job_id), step_name)
            if SWALLOWED_FAILURE_RE.search(run_text):
                finding(record, "HIGH", "FAILURE_SWALLOWED", "command failure is converted into success without a machine-enforced failure state", str(job_id), step_name)
            if "pip install" in run_text and not any(token in run_text for token in ("requirements.txt", "requirements.lock", "--require-hashes")):
                finding(record, "MEDIUM", "DEPENDENCIES_UNLOCKED", "pip dependencies are installed without a lockfile/hash contract", str(job_id), step_name)
            if SCIENTIFIC_LITERAL_RE.search(run_text):
                finding(record, "HIGH", "SCIENTIFIC_RESULT_OR_PARAMETER_EMBEDDED", "scientific metric/parameter literal appears inside workflow code; move to versioned data/config and compute outputs", str(job_id), step_name)
            if step.get("continue-on-error") is not None:
                finding(record, "MEDIUM", "CONTINUE_ON_ERROR", "continue-on-error requires an explicit residual receipt", str(job_id), step_name)

        if len(codeql_action_refs) > 1:
            finding(
                record,
                "ERROR",
                "CODEQL_ACTION_REVISION_DRIFT",
                "CodeQL init/analyze steps must use one identical reviewed commit SHA; "
                f"found {sorted(codeql_action_refs)}",
                str(job_id),
            )

    if managed and "always_upload_receipt" in requirements:
        upload_steps = [
            mapping(s) for j in jobs.values() if isinstance(j, dict)
            for s in list_value(j.get("steps")) if isinstance(s, dict) and str(s.get("uses", "")).startswith("actions/upload-artifact@")
        ]
        if not upload_steps or not any(str(s.get("if", "")).replace(" ", "") == "always()" for s in upload_steps):
            finding(record, "ERROR", "MANAGED_RECEIPT_UPLOAD_MISSING", "managed workflow lacks an if: always() artifact upload")
    if managed and "claim_boundary" in requirements:
        if not recursively_contains_value(doc, ("claim_allowed", "claim_boundary")):
            finding(record, "ERROR", "MANAGED_CLAIM_BOUNDARY_MISSING", "managed workflow lacks parsed claim-boundary data")


def audit_cross_file(repo_root: Path, records: list[FileRecord], global_findings: list[Finding]) -> None:
    by_hash: dict[str, list[str]] = defaultdict(list)
    for rec in records:
        by_hash[rec.sha256].append(rec.path)
    for digest, paths in sorted(by_hash.items()):
        if len(paths) > 1:
            global_findings.append(Finding("LOW", "IDENTICAL_YAML_DUPLICATES", "<repository>", f"identical YAML content {digest[:12]} in: {paths}"))

    summary_path = repo_root / "data/results/repo_inventory_summary.json"
    if summary_path.exists():
        try:
            summary = json.loads(summary_path.read_text(encoding="utf-8"))
            declared_yaml = summary.get("yml_yaml_files")
            declared_workflows = summary.get("github_workflow_yml_files")
            actual_workflows = sum(r.category == "github_workflow" for r in records)
            if declared_yaml != len(records) or declared_workflows != actual_workflows:
                global_findings.append(Finding(
                    "HIGH", "VERSIONED_INVENTORY_STALE", str(summary_path.relative_to(repo_root)),
                    f"declares YAML/workflows={declared_yaml}/{declared_workflows}; actual={len(records)}/{actual_workflows}"
                ))
        except Exception as exc:
            global_findings.append(Finding("MEDIUM", "INVENTORY_SUMMARY_UNREADABLE", str(summary_path.relative_to(repo_root)), str(exc)))


def write_reports(output_dir: Path, records: list[FileRecord], global_findings: list[Finding], commit_sha: str) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    findings = [item for rec in records for item in rec.findings] + global_findings
    findings.sort(key=lambda x: (SEVERITY_ORDER[x.severity], x.path, x.job, x.step, x.code))
    counts = Counter(item.severity for item in findings)
    code_counts = Counter(item.code for item in findings)
    syntax_failures = sum(rec.syntax_status != "OK" for rec in records)
    workflow_count = sum(rec.category == "github_workflow" for rec in records)
    decision = "FAIL" if syntax_failures or counts["ERROR"] else ("REVIEW_REQUIRED" if counts["HIGH"] else "PASS_WITH_RESIDUALS" if findings else "PASS")
    payload = {
        "schema": SCHEMA,
        "commit_sha": commit_sha,
        "claim_allowed": False,
        "publication_effect": "NONE",
        "decision": decision,
        "yaml_files": len(records),
        "workflow_files": workflow_count,
        "syntax_failures": syntax_failures,
        "severity_counts": dict(counts),
        "code_counts": dict(code_counts),
        "residuals": [asdict(item) for item in findings],
        "files": [
            {
                "path": rec.path,
                "category": rec.category,
                "sha256": rec.sha256,
                "bytes": rec.bytes,
                "lines": rec.lines,
                "documents": rec.documents,
                "syntax_status": rec.syntax_status,
                "top_level_type": rec.top_level_type,
                "token_vazio_count": rec.token_vazio_count,
                "synthetic_marker_count": rec.synthetic_marker_count,
                "highest_severity": rec.highest_severity,
                "finding_codes": sorted({f.code for f in rec.findings}),
            }
            for rec in records
        ],
    }
    (output_dir / "deep_yaml_audit.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    with (output_dir / "yaml_file_matrix.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["path", "category", "syntax", "documents", "sha256", "bytes", "lines", "highest_severity", "finding_codes", "token_vazio_count", "synthetic_marker_count"])
        for rec in records:
            writer.writerow([rec.path, rec.category, rec.syntax_status, rec.documents, rec.sha256, rec.bytes, rec.lines, rec.highest_severity, ",".join(sorted({f.code for f in rec.findings})), rec.token_vazio_count, rec.synthetic_marker_count])

    with (output_dir / "findings.tsv").open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(["severity", "code", "path", "job", "step", "message"])
        for item in findings:
            writer.writerow([item.severity, item.code, item.path, item.job, item.step, item.message])

    md = [
        "# RLL YAML Deep Audit",
        "",
        f"- commit: `{commit_sha or 'TOKEN_VAZIO_COMMIT'}`",
        f"- decision: `{decision}`",
        f"- YAML/YML: `{len(records)}`",
        f"- workflows ativos: `{workflow_count}`",
        f"- falhas sintáticas/chaves duplicadas: `{syntax_failures}`",
        f"- ERROR/HIGH/MEDIUM/LOW/INFO: `{counts['ERROR']}/{counts['HIGH']}/{counts['MEDIUM']}/{counts['LOW']}/{counts['INFO']}`",
        "- claim_allowed: `false`",
        "- publication_effect: `NONE`",
        "",
        "## Contagem por código",
        "",
        "| código | quantidade |",
        "|---|---:|",
    ]
    md.extend(f"| `{code}` | {count} |" for code, count in sorted(code_counts.items(), key=lambda x: (-x[1], x[0])))
    md += ["", "## Achados ERROR/HIGH", "", "| severidade | código | arquivo | job | step | mensagem |", "|---|---|---|---|---|---|"]
    for item in findings:
        if item.severity not in {"ERROR", "HIGH"}:
            continue
        msg = item.message.replace("|", "\\|")
        md.append(f"| {item.severity} | `{item.code}` | `{item.path}` | `{item.job}` | `{item.step}` | {msg} |")
    md += [
        "",
        "## Limite epistemológico",
        "",
        "A auditoria mede estrutura, segurança estática, rastreabilidade e coerência declarativa. Não executa todos os modelos científicos nem converte artefatos CI em prova científica.",
    ]
    (output_dir / "DEEP_YAML_AUDIT.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--repo-root", type=Path, default=Path("."))
    parser.add_argument("--output-dir", type=Path, default=Path("artifacts/yaml-deep-audit"))
    parser.add_argument("--fail-on", choices=("none", "error", "high"), default="none")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    root = args.repo_root.resolve()
    contract = load_contract(root)
    records: list[FileRecord] = []
    for path in iter_yaml(root):
        raw = path.read_bytes()
        rel = path.relative_to(root).as_posix()
        try:
            text = raw.decode("utf-8", errors="strict")
        except UnicodeDecodeError as exc:
            rec = FileRecord(path=rel, category=category_for(rel), sha256=sha256_bytes(raw), bytes=len(raw), lines=0, syntax_status="FAIL")
            finding(rec, "ERROR", "UTF8_DECODE_FAILURE", str(exc))
            records.append(rec)
            continue
        rec = FileRecord(
            path=rel,
            category=category_for(rel),
            sha256=sha256_bytes(raw),
            bytes=len(raw),
            lines=len(text.splitlines()),
            token_vazio_count=text.upper().count("TOKEN_VAZIO"),
            synthetic_marker_count=len(re.findall(r"(?i)\b(?:synthetic|mock|fixture|placeholder|demo)\b", text)),
        )
        try:
            docs = parse_documents(text, workflow=rec.category == "github_workflow")
            rec.documents = len(docs)
            rec.syntax_status = "OK"
            audit_generic(rec, root, docs, text)
            if rec.category == "github_workflow" and docs:
                audit_workflow(rec, root, docs[0], contract)
        except Exception as exc:
            rec.syntax_status = "FAIL"
            code = "DUPLICATE_YAML_KEY" if isinstance(exc, DuplicateKeyError) else "YAML_PARSE_FAILURE"
            finding(rec, "ERROR", code, str(exc).replace("\n", " "))
        records.append(rec)

    global_findings: list[Finding] = []
    audit_cross_file(root, records, global_findings)
    commit_sha = ""
    if (root / ".git/HEAD").exists():
        try:
            import subprocess
            commit_sha = subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=root, text=True).strip()
        except Exception:
            commit_sha = ""
    payload = write_reports(args.output_dir, records, global_findings, commit_sha)
    print(json.dumps({k: payload[k] for k in ("decision", "yaml_files", "workflow_files", "syntax_failures", "severity_counts")}, ensure_ascii=False, indent=2))
    if args.fail_on == "error":
        return 1 if payload["syntax_failures"] or payload["severity_counts"].get("ERROR", 0) else 0
    if args.fail_on == "high":
        return 1 if payload["syntax_failures"] or payload["severity_counts"].get("ERROR", 0) or payload["severity_counts"].get("HIGH", 0) else 0
    return 0


if __name__ == "__main__":
    sys.exit(main())
