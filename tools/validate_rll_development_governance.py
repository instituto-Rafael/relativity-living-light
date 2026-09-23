#!/usr/bin/env python3
"""Cross-validate the RLL development governance bundle."""

from __future__ import annotations

import argparse
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
POLICY_PATH = ROOT / "data" / "governance" / "RLL_DEVELOPMENT_SECURITY_ENVELOPE_V1.json"
PURPOSE_PATH = ROOT / "data" / "governance" / "RLL_DATA_USE_PURPOSE_REGISTRY_V1.json"
RISK_PATH = ROOT / "data" / "governance" / "RLL_SECURITY_PRIVACY_RISK_REGISTER_V1.json"
OPERATION_PATH = ROOT / "validacao_real" / "rx_operation.json"
WORKFLOW_PATH = ROOT / ".github" / "workflows" / "validacao_real.yml"


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate():
    errors = []
    warnings = []

    policy = load(POLICY_PATH)
    purpose = load(PURPOSE_PATH)
    risk = load(RISK_PATH)
    operation = load(OPERATION_PATH)
    workflow = WORKFLOW_PATH.read_text(encoding="utf-8")

    if policy.get("schema") != "rll.development_security_envelope.v1":
        errors.append("policy_schema")
    mode = policy.get("mode", {})
    if mode.get("software_development") is not True:
        errors.append("software_development_not_true")
    if mode.get("model_training") is not False:
        errors.append("model_training_must_be_false")
    if mode.get("autonomous_agent") is not False:
        errors.append("autonomous_agent_must_be_false")
    if policy.get("claim_allowed") is not False:
        errors.append("policy_claim_allowed_must_be_false")

    if purpose.get("schema") != "rll.data_use_purpose_registry.v1":
        errors.append("purpose_schema")
    if purpose.get("claim_allowed") is not False:
        errors.append("purpose_claim_allowed_must_be_false")
    if purpose.get("actors", {}).get("autonomous_agent", {}).get("allowed") is not False:
        errors.append("purpose_autonomous_agent_must_be_forbidden")

    if risk.get("schema") != "rll.security_privacy_risk_register.v1":
        errors.append("risk_schema")
    if risk.get("claim_allowed") is not False:
        errors.append("risk_claim_allowed_must_be_false")
    risk_ids = [row.get("id") for row in risk.get("risks", [])]
    if len(risk_ids) != len(set(risk_ids)):
        errors.append("duplicate_risk_ids")
    if len(risk_ids) < 10:
        warnings.append("risk_register_sparse")

    if operation.get("schema") != "rll.development_operation.v1":
        errors.append("operation_schema")
    if operation.get("claim_allowed") is not False:
        errors.append("operation_claim_allowed_must_be_false")
    if operation.get("personal_data_expected") is not False:
        errors.append("operation_personal_data_must_be_false")
    if operation.get("secrets_required") is not False:
        errors.append("operation_secrets_must_be_false")
    if operation.get("destructive_actions") is not False:
        errors.append("operation_destructive_actions_must_be_false")
    if operation.get("shell_free_text") is not False:
        errors.append("operation_shell_free_text_must_be_false")

    allowed_caps = set(policy.get("allowed_capabilities", []))
    op_caps = set(operation.get("capabilities", []))
    extra_caps = sorted(op_caps - allowed_caps)
    if extra_caps:
        errors.append("operation_capability_not_allowlisted:" + ",".join(extra_caps))

    allowed_classes = set(policy.get("data_governance", {}).get("allowed_classes", []))
    op_classes = set(operation.get("data_classes", []))
    extra_classes = sorted(op_classes - allowed_classes)
    if extra_classes:
        errors.append("operation_data_class_not_allowlisted:" + ",".join(extra_classes))

    allowed_hosts = set(policy.get("network", {}).get("exact_hosts", []))
    op_hosts = set(operation.get("network", {}).get("hosts", []))
    extra_hosts = sorted(op_hosts - allowed_hosts)
    if extra_hosts:
        errors.append("operation_network_host_not_allowlisted:" + ",".join(extra_hosts))

    purpose_routes = {
        route.get("route_id"): route
        for route in purpose.get("routes", [])
        if route.get("route_id")
    }
    op_id = operation.get("operation_id")
    if op_id not in purpose_routes:
        errors.append("operation_missing_from_purpose_registry")
    else:
        route = purpose_routes[op_id]
        if route.get("personal_data") is not False:
            errors.append("purpose_route_personal_data_mismatch")
        if route.get("secrets") is not False:
            errors.append("purpose_route_secrets_mismatch")
        route_hosts = set(route.get("network", {}).get("hosts", []))
        if route_hosts != op_hosts:
            errors.append("purpose_route_network_hosts_mismatch")

    required_workflow_fragments = [
        "tests/test_rll_development_guard.py",
        "internal/governance/development_guard.py",
        "--authority-mode reviewed_ci_workflow",
        "tools/rll_security_surface_audit.py --strict",
        "RLL_AUTHORITY_MODE: reviewed_ci_workflow",
        "RX_NETWORK_PROBE: \"0\"",
        "python3 -m validacao_real.run_rx_pipeline",
    ]
    for fragment in required_workflow_fragments:
        if fragment not in workflow:
            errors.append("workflow_missing:" + fragment)
    if "pip install" in workflow:
        errors.append("governed_rx_workflow_must_not_pip_install")

    required_risk_ids = {
        "SEC-01","SEC-02","SEC-03","SEC-04","SEC-05","SEC-06",
        "SEC-07","SEC-08","SEC-09","SEC-10","SEC-11","SEC-12",
        "SEC-13","SEC-14","SEC-15","SEC-16",
    }
    missing_risks = sorted(required_risk_ids - set(risk_ids))
    if missing_risks:
        errors.append("missing_security_risks:" + ",".join(missing_risks))

    return {
        "schema": "rll.development_governance_bundle_validation.v1",
        "pass": not errors,
        "errors": errors,
        "warnings": warnings,
        "claim_allowed": False,
        "checked": [
            str(POLICY_PATH.relative_to(ROOT)),
            str(PURPOSE_PATH.relative_to(ROOT)),
            str(RISK_PATH.relative_to(ROOT)),
            str(OPERATION_PATH.relative_to(ROOT)),
            str(WORKFLOW_PATH.relative_to(ROOT)),
        ],
        "boundary": (
            "Bundle consistency PASS proves only repository contract alignment. "
            "It does not prove runtime isolation, vulnerability absence, external "
            "GitHub settings, legal compliance, or scientific validity."
        ),
    }


def main(argv=None):
    parser = argparse.ArgumentParser(description="Validate RLL development governance bundle")
    parser.add_argument("--json-out", default="results/development_governance_validation.json")
    parser.add_argument("--md-out", default="results/development_governance_validation.md")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    payload = validate()
    json_out = ROOT / args.json_out
    md_out = ROOT / args.md_out
    json_out.parent.mkdir(parents=True, exist_ok=True)
    md_out.parent.mkdir(parents=True, exist_ok=True)
    json_out.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# RLL development governance validation",
        "",
        "- pass: %s" % str(payload["pass"]).lower(),
        "- errors: %d" % len(payload["errors"]),
        "- warnings: %d" % len(payload["warnings"]),
        "",
    ]
    if payload["errors"]:
        lines += ["## Errors", ""]
        lines.extend("- " + item for item in payload["errors"])
    if payload["warnings"]:
        lines += ["", "## Warnings", ""]
        lines.extend("- " + item for item in payload["warnings"])
    md_out.write_text("\n".join(lines) + "\n", encoding="utf-8")

    print(json.dumps(payload, ensure_ascii=False, indent=2))
    if args.strict and not payload["pass"]:
        return 6
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
