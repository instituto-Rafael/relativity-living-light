"""Deterministic command router for the Rx RLL development runtime.

No model training. No AI runtime. No third-party Python dependencies.
"""

from __future__ import annotations

import argparse
import os
import runpy
import sys
from datetime import datetime, timezone
from pathlib import Path

from internal.governance.development_guard import evaluate_operation
from .contracts import active_contract, load_contracts
from .kernel import dump_json, load_json

ROOT = Path(__file__).resolve().parents[1]
SECURITY_POLICY_PATH = ROOT / "data" / "governance" / "RLL_DEVELOPMENT_SECURITY_ENVELOPE_V1.json"
CLI_OPERATION_PATH = ROOT / "configs" / "rx_cli_operation.json"


def _security_preflight(command):
    policy = load_json(SECURITY_POLICY_PATH)
    operation = load_json(CLI_OPERATION_PATH)
    runtime_authority_mode = os.environ.get(
        "RLL_AUTHORITY_MODE",
        operation.get("authority", {}).get("default_runtime_mode", "explicit_local_command"),
    )
    receipt = evaluate_operation(
        policy,
        operation,
        runtime_authority_mode=runtime_authority_mode,
    )
    receipt["rx_cli_command"] = command
    if receipt["decision"] != "ALLOW":
        raise SystemExit(
            "Rx CLI security preflight blocked execution: "
            + receipt["decision"]
            + " "
            + "; ".join(receipt["reasons"])
        )
    out_dir = ROOT / "results"
    out_dir.mkdir(parents=True, exist_ok=True)
    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    out = out_dir / ("rx_cli_security_preflight_" + stamp + "_" + command + ".json")
    dump_json(out, receipt)
    print("RX_CLI_SECURITY_PREFLIGHT=ALLOW", "authority=", runtime_authority_mode)
    print("wrote", out.relative_to(ROOT))


def _tool(name):
    runpy.run_path(str(ROOT / "tools" / name), run_name="__main__")


def _tool_args(name, args):
    previous = sys.argv[:]
    try:
        sys.argv = [name] + list(args)
        runpy.run_path(str(ROOT / "tools" / name), run_name="__main__")
    finally:
        sys.argv = previous


def _module(name):
    runpy.run_module(name, run_name="__main__")


def status():
    contract_id, contract = active_contract()
    payload = load_contracts()
    print("RLL_RX_STATUS")
    print("training=False")
    print("ai_runtime=False")
    print("third_party_python_dependencies=0")
    print("active_contract=", contract_id)
    print("active_contract_state=", contract.get("state"))
    print("claim_allowed=", contract.get("claim_allowed"))
    print("contracts:")
    for key, value in payload["contracts"].items():
        print(" ", key, "->", value.get("state"))


def selftest():
    _tool("rx_no_ai_gate.py")
    _tool("rx_zero_dependency_gate.py")
    _tool("rx_selftest.py")
    _tool("validate_rx_fairness.py")
    _tool("validate_rx_inference.py")\n    _tool("validate_rx_dha.py")
    _tool("validate_rx_dha.py")
    _tool("rx_sound_horizon_selftest.py")
    _tool("rx_freestanding65_parity.py")


def validate():
    _module("validacao_real.run_rx_pipeline")
    _module("validacao_real.run_rx_multiprobe")
    _module("data.pipelines.structure_d.joint_real_likelihood_rx")


def parity():
    _tool("rx_sound_horizon_selftest.py")
    _tool("rx_freestanding65_parity.py")
    _tool("rx_semantic_parity.py")


def audit():
    _tool_args("validate_rll_development_governance.py", ["--strict"])
    _tool("validate_executable_entrypoint_authority_registry.py")
    _tool("validate_validacao_real_serialization_parity.py")
    _tool("validate_validacao_real_zero_dependency.py")
    _tool("validate_inventory_config_parity.py")
    _tool("validate_rll_plot_migration.py")
    _tool("validate_rx_http_migration.py")
    _tool("validate_credential_authority_stdlib_migration.py")
    _tool("validate_watch_config_stdlib_migration.py")
    _tool("validate_calc_data_stdlib_migration.py")
    _tool("validate_validation_deterministic_stdlib.py")
    _tool("validate_ci_scientific_skills_stdlib_migration.py")
    _tool("validate_rx_fairness.py")
    _tool("validate_rx_inference.py")\n    _tool("validate_rx_dha.py")
    _tool("validate_validation_simple_claim_boundary.py")
    _tool("validate_real_data_materialization_security.py")
    _tool_args("rll_security_surface_audit.py", ["--strict"])
    _tool("rx_dependency_audit.py")
    _tool("rx_dependency_migration_plan.py")


def develop():
    _tool_args("validate_rll_development_governance.py", ["--strict"])
    _tool("validate_executable_entrypoint_authority_registry.py")
    _tool("validate_validacao_real_serialization_parity.py")
    _tool("validate_validacao_real_zero_dependency.py")
    _tool("validate_inventory_config_parity.py")
    _tool("validate_rll_plot_migration.py")
    _tool("validate_rx_http_migration.py")
    _tool("validate_credential_authority_stdlib_migration.py")
    _tool("validate_watch_config_stdlib_migration.py")
    _tool("validate_calc_data_stdlib_migration.py")
    _tool("validate_rx_fairness.py")
    _tool("validate_rx_inference.py")\n    _tool("validate_rx_dha.py")
    _tool_args("rll_security_surface_audit.py", ["--strict"])
    _tool("rx_no_ai_gate.py")
    _tool("rx_zero_dependency_gate.py")
    _tool("rx_selftest.py")
    _tool("rx_sound_horizon_selftest.py")
    _tool("rx_freestanding65_parity.py")
    _module("validacao_real.run_rx_pipeline")
    _module("validacao_real.run_rx_multiprobe")
    _module("data.pipelines.structure_d.joint_real_likelihood_rx")
    _tool("rx_semantic_parity.py")
    _tool("rx_dependency_audit.py")
    _tool("rx_dependency_migration_plan.py")
    _tool("rx_development_gate.py")
    print("RLL_RX_DEVELOPMENT=PASS")


def orchestrate(plan="configs/rll_execution_plan.v1.yml", execute=True):
    from .orchestrator import orchestrate as run_execution_fabric

    result = run_execution_fabric(plan_path=plan, execute=execute)
    print("RLL_RX_ORCHESTRATE=" + result["status"])
    print("run_id=" + result["run_id"])
    print("physics_contract=" + result["physics_contract"])
    print("regimes=" + ",".join(result["regimes"]))
    print("selected_formula_count=" + str(result["selected_formula_count"]))
    print("rejected_formula_count=" + str(result["rejected_formula_count"]))
    print("claim_allowed=False")
    return result


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python3 -m rx",
        description="RLL Rx deterministic development runtime; no AI, no training.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=("status", "selftest", "validate", "parity", "audit", "develop", "orchestrate"),
    )
    parser.add_argument(
        "--plan",
        default="configs/rll_execution_plan.v1.yml",
        help="Execution plan for the orchestrate command.",
    )
    parser.add_argument(
        "--no-execute",
        action="store_true",
        help="Build the execution graph and receipts without running scientific routes.",
    )
    args = parser.parse_args(argv)

    commands = {
        "status": status,
        "selftest": selftest,
        "validate": validate,
        "parity": parity,
        "audit": audit,
        "develop": develop,
        "orchestrate": lambda: orchestrate(
            plan=args.plan,
            execute=not args.no_execute,
        ),
    }
    if args.command != "status":
        _security_preflight(args.command)
    commands[args.command]()


if __name__ == "__main__":
    main()