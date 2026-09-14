#!/usr/bin/env python3
"""RLL governance gate.

Standard-library-only validator and receipt generator. The gate validates
repository-local contracts and reports legacy gaps without converting guidance
into a certification or legal-conformity claim.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Iterable

ROOT = Path(__file__).resolve().parents[1]
PROFILE_PATH = ROOT / "governance" / "rll-governance-profile.v1.json"
SCHEMA_PATH = ROOT / "governance" / "rll-module-contract.schema.json"
MODULE_DIR = ROOT / "governance" / "modules"
WORKFLOW_DIR = ROOT / ".github" / "workflows"
PR_TEMPLATE = ROOT / ".github" / "PULL_REQUEST_TEMPLATE.md"
OUTPUT_DIR = ROOT / "artifacts" / "governance"

ALLOWED_STATES = {
    "DESIGN", "ARCHITECTURE_READY", "IMPLEMENTED", "VALIDATED",
    "OPERATIONAL", "SUSPENDED", "DEPRECATED",
}
ALLOWED_EPISTEMIC = {
    "PROVADO", "EVIDENCIADO", "HIPOTESE", "MODELO_ANALOGICO",
    "PARABOLA", "REFUTADO_COMO_ESCRITO", "TOKEN_VAZIO",
}
HEALTH_DOMAINS = {"biomedicine", "biomedical", "health", "medicine", "genomics"}
REQUIRED_METADATA = {
    "origin", "license", "hash", "version", "collected_at", "unit",
    "uncertainty", "provenance", "update_policy",
}
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
USES_RE = re.compile(r"^\s*-?\s*uses:\s*([^\s#]+)", re.MULTILINE)


class DuplicateKeyError(ValueError):
    pass


def _no_duplicate_keys(pairs: list[tuple[str, Any]]) -> dict[str, Any]:
    obj: dict[str, Any] = {}
    for key, value in pairs:
        if key in obj:
            raise DuplicateKeyError(f"duplicate JSON key: {key}")
        obj[key] = value
    return obj


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"), object_pairs_hook=_no_duplicate_keys)


def canonical_json(value: Any) -> bytes:
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":")).encode("utf-8")


def sha256_path(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


@dataclass
class Finding:
    severity: str
    code: str
    location: str
    message: str

    def as_dict(self) -> dict[str, str]:
        return {
            "severity": self.severity,
            "code": self.code,
            "location": self.location,
            "message": self.message,
        }


@dataclass
class Audit:
    violations: list[Finding] = field(default_factory=list)
    warnings: list[Finding] = field(default_factory=list)
    observations: list[Finding] = field(default_factory=list)

    def add(self, severity: str, code: str, location: str, message: str) -> None:
        finding = Finding(severity, code, location, message)
        if severity == "ERROR":
            self.violations.append(finding)
        elif severity == "WARNING":
            self.warnings.append(finding)
        else:
            self.observations.append(finding)


def require(condition: bool, audit: Audit, code: str, location: str, message: str) -> None:
    if not condition:
        audit.add("ERROR", code, location, message)


def validate_profile(profile: dict[str, Any], audit: Audit) -> None:
    loc = str(PROFILE_PATH.relative_to(ROOT))
    require(profile.get("schema") == "rll.governance_profile.v1", audit, "PROFILE_SCHEMA", loc, "Unexpected profile schema")
    require(profile.get("certification_claim") is False, audit, "NO_CERTIFICATION", loc, "certification_claim MUST be false")
    require(profile.get("conformity_claim") is False, audit, "NO_CONFORMITY", loc, "conformity_claim MUST be false")
    require(profile.get("legal_compliance_claim") is False, audit, "NO_LEGAL_CLAIM", loc, "legal_compliance_claim MUST be false")
    require(profile.get("enforcement_mode") in {"progressive", "strict"}, audit, "ENFORCEMENT_MODE", loc, "Unsupported enforcement mode")
    require(bool(profile.get("claim_boundary")), audit, "CLAIM_BOUNDARY", loc, "claim_boundary is required")
    require(len(profile.get("layers", [])) >= 6, audit, "GOVERNANCE_LAYERS", loc, "At least six governance layers are required")
    refs = profile.get("normative_references", [])
    require(bool(refs), audit, "NORMATIVE_REFS", loc, "Normative reference inventory is empty")
    for index, ref in enumerate(refs):
        rloc = f"{loc}:normative_references[{index}]"
        require(ref.get("certification_basis") is False, audit, "REF_NOT_CERTIFICATION", rloc, "Reference cannot be represented as certification basis")
        require(bool(ref.get("id")) and bool(ref.get("use")), audit, "REF_FIELDS", rloc, "Reference id and use are required")


def validate_module(module: dict[str, Any], path: Path, profile: dict[str, Any], audit: Audit) -> None:
    loc = str(path.relative_to(ROOT))
    for key in profile.get("required_module_fields", []):
        require(key in module, audit, "MODULE_REQUIRED_FIELD", loc, f"Missing required field: {key}")

    require(module.get("state") in ALLOWED_STATES, audit, "MODULE_STATE", loc, "Invalid lifecycle state")
    require(module.get("epistemic_status") in ALLOWED_EPISTEMIC, audit, "EPISTEMIC_STATE", loc, "Invalid epistemic status")
    require(module.get("certification_claim") is False, audit, "MODULE_NO_CERTIFICATION", loc, "certification_claim MUST remain false")
    require(isinstance(module.get("domains"), list) and bool(module.get("domains")), audit, "MODULE_DOMAINS", loc, "At least one domain is required")
    require(isinstance(module.get("scope"), str) and len(module.get("scope", "")) >= 10, audit, "MODULE_SCOPE", loc, "Scope is missing or too short")

    evidence = module.get("evidence", {})
    for key in ("receipts", "tests", "sources", "limitations"):
        require(isinstance(evidence.get(key), list), audit, "EVIDENCE_STRUCTURE", loc, f"evidence.{key} MUST be a list")
    require(bool(evidence.get("limitations")), audit, "LIMITATIONS_REQUIRED", loc, "At least one limitation MUST be declared")

    if module.get("claim_allowed") is True:
        require(module.get("epistemic_status") in {"PROVADO", "EVIDENCIADO"}, audit, "CLAIM_STATE", loc, "claim_allowed=true requires PROVADO or EVIDENCIADO")
        require(bool(evidence.get("receipts")) and bool(evidence.get("tests")), audit, "CLAIM_EVIDENCE", loc, "claim_allowed=true requires receipts and tests")

    data = module.get("data_governance", {})
    metadata = set(data.get("required_metadata", [])) if isinstance(data.get("required_metadata"), list) else set()
    require(REQUIRED_METADATA.issubset(metadata), audit, "DATA_METADATA", loc, f"required_metadata must include {sorted(REQUIRED_METADATA)}")
    for key in ("classification", "retention", "update_policy", "legal_applicability"):
        require(bool(data.get(key)), audit, "DATA_GOVERNANCE_FIELD", loc, f"data_governance.{key} is required")
    legal = str(data.get("legal_applicability", "")).upper()
    require("COMPLIANT" not in legal and "CERTIFIED" not in legal, audit, "LEGAL_OVERCLAIM", loc, "Legal applicability cannot assert compliance or certification")

    security = module.get("security", {})
    require(security.get("least_privilege") is True, audit, "LEAST_PRIVILEGE", loc, "least_privilege MUST be true")
    for key in ("secrets", "integrity", "incident_record"):
        require(bool(security.get(key)), audit, "SECURITY_FIELD", loc, f"security.{key} is required")

    quality = module.get("quality", {})
    for key in ("metrics", "acceptance_criteria", "rejection_criteria"):
        require(isinstance(quality.get(key), list) and bool(quality.get(key)), audit, "QUALITY_FIELD", loc, f"quality.{key} MUST be a non-empty list")
    require(bool(quality.get("change_control")), audit, "CHANGE_CONTROL", loc, "quality.change_control is required")
    require(isinstance(module.get("risks"), list) and bool(module.get("risks")), audit, "RISKS_REQUIRED", loc, "At least one risk is required")
    rollback = module.get("rollback", {})
    for key in ("trigger", "procedure", "verification"):
        require(bool(rollback.get(key)), audit, "ROLLBACK_FIELD", loc, f"rollback.{key} is required")
    require(isinstance(module.get("f_next"), list) and bool(module.get("f_next")), audit, "F_NEXT", loc, "f_next MUST be non-empty")

    domains = {str(item).lower() for item in module.get("domains", [])}
    if domains & HEALTH_DOMAINS:
        require(data.get("personal_data") == "PROHIBITED_BY_DEFAULT", audit, "HEALTH_PERSONAL_DATA", loc, "Health/biomedical modules MUST default-deny personal data")
        require(data.get("sensitive_health_genetic_biometric_data") == "PROHIBITED_BY_DEFAULT", audit, "HEALTH_SENSITIVE_DATA", loc, "Sensitive health/genetic/biometric data MUST be prohibited by default")
        require(data.get("human_participants") == "ETHICS_REVIEW_REQUIRED", audit, "HEALTH_ETHICS", loc, "Human-participant processing MUST require ethics review")


def audit_workflows(audit: Audit) -> dict[str, Any]:
    result = {"files": 0, "external_uses": 0, "mutable_external_uses": [], "missing_permissions": []}
    if not WORKFLOW_DIR.exists():
        audit.add("WARNING", "WORKFLOW_DIR_MISSING", str(WORKFLOW_DIR), "Workflow directory not available")
        return result
    for path in sorted(list(WORKFLOW_DIR.glob("*.yml")) + list(WORKFLOW_DIR.glob("*.yaml"))):
        result["files"] += 1
        text = path.read_text(encoding="utf-8")
        rel = str(path.relative_to(ROOT))
        if not re.search(r"(?m)^permissions:\s*(?:\n|$)", text) and not re.search(r"(?m)^permissions:\s*[^\n]+$", text):
            result["missing_permissions"].append(rel)
        for use in USES_RE.findall(text):
            if use.startswith("./"):
                continue
            result["external_uses"] += 1
            if "@" not in use:
                result["mutable_external_uses"].append({"workflow": rel, "uses": use, "reason": "missing_ref"})
                continue
            ref = use.rsplit("@", 1)[1]
            if not FULL_SHA_RE.fullmatch(ref):
                result["mutable_external_uses"].append({"workflow": rel, "uses": use, "reason": "not_full_commit_sha"})

    governance_rel = ".github/workflows/rll-governance-quality-gate.yml"
    governance_mutable = [x for x in result["mutable_external_uses"] if x["workflow"] == governance_rel]
    for item in governance_mutable:
        audit.add("ERROR", "GOV_WORKFLOW_MUTABLE_ACTION", item["workflow"], f"External action is not pinned to a full commit SHA: {item['uses']}")
    legacy = [x for x in result["mutable_external_uses"] if x["workflow"] != governance_rel]
    if legacy:
        audit.add("WARNING", "LEGACY_MUTABLE_ACTIONS", ".github/workflows", f"{len(legacy)} legacy mutable external action references observed; progressive remediation required")
    if result["missing_permissions"]:
        audit.add("WARNING", "LEGACY_PERMISSIONS", ".github/workflows", f"{len(result['missing_permissions'])} workflows do not declare top-level permissions")
    return result


def validate_pr_template(audit: Audit) -> None:
    loc = str(PR_TEMPLATE.relative_to(ROOT))
    require(PR_TEMPLATE.exists(), audit, "PR_TEMPLATE_MISSING", loc, "Pull request template is required")
    if not PR_TEMPLATE.exists():
        return
    text = PR_TEMPLATE.read_text(encoding="utf-8").lower()
    for marker in ("objetivo", "evidência", "riscos", "rollback", "aceite", "rejeição", "claim_allowed", "certificação"):
        require(marker in text, audit, "PR_TEMPLATE_MARKER", loc, f"Missing PR template marker: {marker}")


def iter_evidence_files() -> Iterable[Path]:
    candidates = [
        PROFILE_PATH,
        SCHEMA_PATH,
        ROOT / "scripts" / "rll_governance_audit.py",
        ROOT / "tests" / "test_rll_governance_audit.py",
        ROOT / ".github" / "workflows" / "rll-governance-quality-gate.yml",
        PR_TEMPLATE,
        ROOT / "docs" / "governance" / "RLL_OPERATIONAL_GOVERNANCE.md",
    ]
    candidates.extend(sorted(MODULE_DIR.glob("*.json")))
    return [path for path in candidates if path.exists()]


def build_report(audit: Audit, workflow_inventory: dict[str, Any], modules: list[dict[str, Any]]) -> tuple[dict[str, Any], str]:
    hashes = {str(path.relative_to(ROOT)): sha256_path(path) for path in iter_evidence_files()}
    evaluated_revision = os.environ.get("GITHUB_SHA", "TOKEN_VAZIO_LOCAL_REVISION")
    decision = "FAIL" if audit.violations else "PASS"
    inputs_sha256 = hashlib.sha256(canonical_json(hashes)).hexdigest()
    receipt = {
        "schema": "rll.governance_receipt.v1",
        "commit_sha": evaluated_revision,
        "workflow": os.environ.get("GITHUB_WORKFLOW", "rll-governance-quality-gate"),
        "job": os.environ.get("GITHUB_JOB", "governance-quality-gate"),
        "publication_effect": "NONE",
        "inputs_sha256": inputs_sha256,
        "decision": decision,
        "residuals": {
            "violations": [item.code for item in audit.violations],
            "warnings": [item.code for item in audit.warnings],
            "unobserved_external_settings": True,
        },
        "evaluated_revision": evaluated_revision,
        "evaluated_at": os.environ.get("RLL_EVALUATED_AT", "TOKEN_VAZIO_DETERMINISTIC_TIME"),
        "status": decision,
        "claim_allowed": False,
        "certification_claim": False,
        "conformity_claim": False,
        "legal_compliance_claim": False,
        "counts": {
            "modules": len(modules),
            "violations": len(audit.violations),
            "warnings": len(audit.warnings),
            "observations": len(audit.observations),
            "workflow_files": workflow_inventory["files"],
            "mutable_external_action_refs": len(workflow_inventory["mutable_external_uses"]),
            "workflows_missing_permissions": len(workflow_inventory["missing_permissions"]),
        },
        "findings": {
            "violations": [item.as_dict() for item in audit.violations],
            "warnings": [item.as_dict() for item in audit.warnings],
            "observations": [item.as_dict() for item in audit.observations],
        },
        "module_states": [
            {
                "module_id": module.get("module_id"),
                "state": module.get("state"),
                "epistemic_status": module.get("epistemic_status"),
                "claim_allowed": module.get("claim_allowed"),
                "f_gap_count": len(module.get("f_gap", [])),
                "f_next_count": len(module.get("f_next", [])),
            }
            for module in modules
        ],
        "file_sha256": hashes,
        "closure": {
            "F_ok": "Repository-local governance contracts were evaluated.",
            "F_gap": "Warnings and unobserved external settings remain explicit; PASS is not certification.",
            "F_next": "Remediate findings by severity, regenerate the receipt and obtain domain-specific review where applicable."
        }
    }
    receipt["receipt_sha256"] = hashlib.sha256(canonical_json(receipt)).hexdigest()

    lines = [
        "# RLL Governance Audit Report",
        "",
        f"- **Status:** `{receipt['status']}`",
        f"- **Revision:** `{receipt['evaluated_revision']}`",
        "- **Certification:** `false`",
        "- **Conformity claim:** `false`",
        "- **Legal compliance claim:** `false`",
        f"- **Receipt SHA-256:** `{receipt['receipt_sha256']}`",
        "",
        "## Observado e medido",
        "",
        f"- Modules: {receipt['counts']['modules']}",
        f"- Workflow files: {receipt['counts']['workflow_files']}",
        f"- Violations: {receipt['counts']['violations']}",
        f"- Warnings: {receipt['counts']['warnings']}",
        f"- Mutable external action references observed: {receipt['counts']['mutable_external_action_refs']}",
        f"- Workflows without explicit top-level permissions: {receipt['counts']['workflows_missing_permissions']}",
        "",
        "## Não observado / limites",
        "",
        "- External branch-protection settings, organization policies, secrets configuration, ethics approvals and legal applicability are not proven by repository files.",
        "- A PASS proves only that the repository-local contract passed this gate at the declared revision.",
        "",
        "## Violações",
        "",
    ]
    lines.extend([f"- `{f.code}` — {f.location}: {f.message}" for f in audit.violations] or ["- None"])
    lines.extend(["", "## Lacunas e avisos", ""])
    lines.extend([f"- `{f.code}` — {f.location}: {f.message}" for f in audit.warnings] or ["- None"])
    lines.extend(["", "## Módulos", ""])
    for module in modules:
        lines.append(f"- `{module.get('module_id')}`: state=`{module.get('state')}`, epistemic=`{module.get('epistemic_status')}`, claim_allowed=`{str(module.get('claim_allowed')).lower()}`")
    lines.extend([
        "",
        "## Fechamento Ω",
        "",
        f"- **F_ok:** {receipt['closure']['F_ok']}",
        f"- **F_gap:** {receipt['closure']['F_gap']}",
        f"- **F_next:** {receipt['closure']['F_next']}",
        "",
    ])
    return receipt, "\n".join(lines)


def run(write_report: bool = False) -> tuple[Audit, dict[str, Any], str]:
    audit = Audit()
    try:
        profile = load_json(PROFILE_PATH)
    except Exception as exc:
        audit.add("ERROR", "PROFILE_LOAD", str(PROFILE_PATH), str(exc))
        profile = {}
    validate_profile(profile, audit)

    modules: list[dict[str, Any]] = []
    for path in sorted(MODULE_DIR.glob("*.json")):
        try:
            module = load_json(path)
            modules.append(module)
            validate_module(module, path, profile, audit)
        except Exception as exc:
            audit.add("ERROR", "MODULE_LOAD", str(path.relative_to(ROOT)), str(exc))
    require(bool(modules), audit, "NO_MODULES", str(MODULE_DIR.relative_to(ROOT)), "At least one governed module is required")

    workflow_inventory = audit_workflows(audit)
    validate_pr_template(audit)
    receipt, report = build_report(audit, workflow_inventory, modules)
    if write_report:
        OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
        (OUTPUT_DIR / "rll_governance_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
        (OUTPUT_DIR / "RLL_GOVERNANCE_REPORT.md").write_text(report, encoding="utf-8")
    return audit, receipt, report


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate RLL governance contracts and emit a non-certification receipt")
    parser.add_argument("--strict", action="store_true", help="Return non-zero when contract violations exist")
    parser.add_argument("--write-report", action="store_true", help="Write JSON receipt and Markdown report")
    args = parser.parse_args()
    audit, receipt, report = run(write_report=args.write_report)
    print(report)
    print(json.dumps({"status": receipt["status"], "receipt_sha256": receipt["receipt_sha256"]}, sort_keys=True))
    return 1 if args.strict and audit.violations else 0


if __name__ == "__main__":
    sys.exit(main())
