"""Deterministic command router for the Rx RLL development runtime.

No model training. No AI runtime. No third-party Python dependencies.
"""

from __future__ import annotations

import argparse
import runpy
from pathlib import Path

from .contracts import active_contract, load_contracts

ROOT = Path(__file__).resolve().parents[1]


def _tool(name):
    runpy.run_path(str(ROOT / "tools" / name), run_name="__main__")


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
    _tool("rx_dependency_audit.py")


def develop():
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
    _tool("rx_development_gate.py")
    print("RLL_RX_DEVELOPMENT=PASS")


def main(argv=None):
    parser = argparse.ArgumentParser(
        prog="python3 -m rx",
        description="RLL Rx deterministic development runtime; no AI, no training.",
    )
    parser.add_argument(
        "command",
        nargs="?",
        default="status",
        choices=("status", "selftest", "validate", "parity", "audit", "develop"),
    )
    args = parser.parse_args(argv)

    commands = {
        "status": status,
        "selftest": selftest,
        "validate": validate,
        "parity": parity,
        "audit": audit,
        "develop": develop,
    }
    commands[args.command]()


if __name__ == "__main__":
    main()
