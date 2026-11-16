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
OPERATION_PATHS = [
    ROOT / "validacao_real" / "rx_operation.json",
    ROOT / "validacao_real" / "rx_multiprobe_operation.json",
    ROOT / "configs" / "rx_cli_operation.json",
]
WORKFLOW_PATHS = [
    ROOT / ".github" / "workflows" / "validacao_real.yml",
    ROOT / ".github" / "workflows" / "rx-development.yml",
]
PROMOTED_PATHS = [
    ROOT / "validacao_real" / "run_rx_pipeline.py",
    ROOT / "validacao_real" / "run_rx_multiprobe.py",
    ROOT / "rx" / "cli.py",
]


def load(path):
    return json.loads(path.read_text(encoding="utf-8"))


def validate_operation(policy, purpose_routes, path):
    errors = []
    operation = load(path)
    prefix = path.relative_to(ROOT).as_posix()

    if operation.get("schema") != "rll.development_operation.v1":
        errors.append(prefix + ":schema")
    for field in ("claim_allowed", "personal_data_expected", "secrets_required", "destructive_actions", "shell_free_text"):
        if operation.get(field) is not False:
            errors.append(prefix + ":" + field + "_must_be_false")

    authority = operation.get("authority", {})
    policy_modes = set(policy.get("human_authority", {}).get("accepted_modes", []))
    op_modes = set(authority.get("permitted_modes", []))
    if authority.get("human_required") is not True:
        errors.append(prefix + ":human_required")
    if authority.get("self_authorized") is not False:
        errors.append(prefix + ":self_authorized")
    if not op_modes or not op_modes.issubset(policy_modes):
        errors.append(prefix + ":authority_modes")

    autonomy = operation.get("autonomy", {})
    for field in ("goal_setting", "scope_expansion", "background_persistence"):
        if autonomy.get(field) is not False:
            errors.append(prefix + ":autonomy_" + field)

    allowed_caps = set(policy.get("allowed_capabilities", []))
    extra_caps = sorted(set(operation.get("capabilities", [])) - allowed_caps)
    if extra_caps:
        errors.append(prefix + ":capability_not_allowlisted:" + ",".join(extra_caps))

    allowed_classes = set(policy.get("data_governance", {}).get("allowed_classes", []))
    extra_classes = sorted(set(operation.get("data_classes", [])) - allowed_classes)
    if extra_classes:
        errors.append(prefix + ":data_class_not_allowlisted:" + ",".join(extra_classes))

    allowed_hosts = set(policy.get("network", {}).get("exact_hosts", []))
    op_hosts = set(operation.get("network", {}).get("hosts", []))
    extra_hosts = sorted(op_hosts - allowed_hosts)
    if extra_hosts:
        errors.append(prefix + ":network_host_not_allowlisted:" + ",".join(extra_hosts))
    if operation.get("network", {}).get("default_enabled") is not False:
        errors.append(prefix + ":network_default_must_be_off")

    op_id = operation.get("operation_id")
    route = purpose_routes.get(op_id)
    if route is None:
        errors.append(prefix + ":missing_from_purpose_registry")
    else:
        if route.get("personal_data") is not False:
            errors.append(prefix + ":purpose_personal_data_mismatch")
        if route.get("secrets") is not False:
            errors.append(prefix + ":purpose_secrets_mismatch")
        route_hosts = set(route.get("network", {}).get("hosts", []))
        if route_hosts != op_hosts:
            errors.append(prefix + ":purpose_network_hosts_mismatch")

    return errors


def validate():
    errors = []
    warnings = []

    policy = load(POLICY_PATH)
    purpose = load(PURPOSE_PATH)
    risk = load(RISK_PATH)

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
    if len(risk_ids) < 16:
        warnings.append("risk_register_sparse")

    purpose_routes = {
        route.get("route_id"): route
        for route in purpose.get("routes", [])
        if route.get("route_id")
    }
    for path in OPERATION_PATHS:
        if not path.exists():
            errors.append("missing_operation:" + path.relative_to(ROOT).as_posix())
            continue
        errors.extend(validate_operation(policy, purpose_routes, path))

    validacao_workflow = WORKFLOW_PATHS[0].read_text(encoding="utf-8")
    required_validation_fragments = [
        "tests/test_rll_development_guard.py",
        "internal/governance/development_guard.py",
        "--authority-mode reviewed_ci_workflow",
        "tools/validate_rll_development_governance.py --strict",
        "tools/rll_security_surface_audit.py --strict",
        "RLL_AUTHORITY_MODE: reviewed_ci_workflow",
        'RX_NETWORK_PROBE: "0"',
        "python3 -m validacao_real.run_rx_pipeline",
    ]
    for fragment in required_validation_fragments:
        if fragment not in validacao_workflow:
            errors.append("validacao_workflow_missing:" + fragment)
    if "pip install" in validacao_workflow:
        errors.append("validacao_workflow_must_not_pip_install")

    rx_workflow = WORKFLOW_PATHS[1].read_text(encoding="utf-8")
    required_rx_fragments = [
        "workflow_dispatch",
        "permissions:",
        "contents: read",
        "persist-credentials: false",
        "tests/test_rll_development_guard.py",
        "tools/validate_rll_development_governance.py --strict",
        "tools/rll_security_surface_audit.py --strict",
        "RLL_AUTHORITY_MODE: reviewed_ci_workflow",
        'RX_NETWORK_PROBE: "0"',
        "python3 -m rx develop",
    ]
    for fragment in required_rx_fragments:
        if fragment not in rx_workflow:
            errors.append("rx_workflow_missing:" + fragment)
    if "pip install" in rx_workflow:
        errors.append("rx_workflow_must_not_pip_install")
    if "contents: write" in rx_workflow:
        errors.append("rx_workflow_contents_write_forbidden")

    promoted = {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in PROMOTED_PATHS
    }
    for rel, source in promoted.items():
        if "evaluate_operation" not in source:
            errors.append(rel + ":missing_security_preflight")
        if "RLL_AUTHORITY_MODE" not in source:
            errors.append(rel + ":missing_runtime_authority_mode")
    if "RX_NETWORK_PROBE" not in promoted["validacao_real/run_rx_pipeline.py"]:
        errors.append("run_rx_pipeline_missing_network_default_gate")

    required_risk_ids = {
        "SEC-01","SEC-02","SEC-03","SEC-04","SEC-05","SEC-06",
        "SEC-07","SEC-08","SEC-09","SEC-10","SEC-11","SEC-12",
        "SEC-13","SEC-14","SEC-15","SEC-16",
    }
    missing_risks = sorted(required_risk_ids - set(risk_ids))
    if missing_risks:
        errors.append("missing_security_risks:" + ",".join(missing_risks))

    checked = [POLICY_PATH, PURPOSE_PATH, RISK_PATH] + OPERATION_PATHS + WORKFLOW_PATHS + PROMOTED_PATHS
    return {
        "schema": "rll.development_governance_bundle_validation.v2",
        "pass": not errors,
        "errors": errors,
        "warnings": warnings,
        "claim_allowed": False,
        "checked": [str(path.relative_to(ROOT)) for path in checked],
        "boundary": (
            "Bundle consistency PASS proves only repository contract alignment. "
            "It does not prove runtime isolation, vulnerability absence, external "
            "GitHub settings, legal compliance, independent security review, or scientific validity."
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
        "- schema: %s" % payload["schema"],
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
