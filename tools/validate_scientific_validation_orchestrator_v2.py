#!/usr/bin/env python3
"""Fail-closed readiness engine for the RLL scientific validation orchestrator.

This tool does not fit cosmological parameters and does not promote scientific
claims.  It converts repository state into an auditable dependency/readiness
receipt so that missing evidence remains explicit and downstream stages cannot
be treated as ready when an upstream gate is unresolved.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import subprocess
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "data/contracts/rll_scientific_validation_orchestrator.v1.json"
URGENCY_PATH = ROOT / "data/governance/RLL_SCIENTIFIC_VALIDATION_URGENCY_20260819_V1.json"
PANTHEON_VERIFIER_PATH = ROOT / "scripts/verify_pantheon_inputs.py"
DESI_COVARIANCE_PATH = ROOT / "data/real/desi_dr2_bao_covariance.csv"
STRUCTURAL_CORE_PATH = ROOT / "rll_core/structural_invariants.py"
STRUCTURAL_WORKFLOW_PATH = ROOT / ".github/workflows/rll-structural-math-artifacts.yml"
JOINT_LIKELIHOOD_PATH = ROOT / "data/pipelines/structure_d/joint_real_likelihood.py"
FASE20_PATH = ROOT / "scripts/rll_fase20_mcmc_bayes.py"

READY_G2 = "READY_G2_INPUTS"
TOKEN_VAZIO_G2 = "TOKEN_VAZIO_FULL_COVARIANCE"


class ValidationError(RuntimeError):
    """Raised only for malformed governance inputs, never for an honest gap."""


def sha256_file(path: Path) -> str | None:
    if not path.is_file():
        return None
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValidationError(f"{path}: top-level JSON must be an object")
    return data


def git_sha(root: Path = ROOT) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (OSError, subprocess.CalledProcessError):
        return None


def _cycle_errors(gates: list[dict[str, Any]]) -> list[str]:
    graph = {str(gate.get("id")): [str(x) for x in gate.get("requires", [])] for gate in gates}
    errors: list[str] = []
    visiting: set[str] = set()
    visited: set[str] = set()

    def visit(node: str, trail: tuple[str, ...]) -> None:
        if node in visited:
            return
        if node in visiting:
            errors.append("gate dependency cycle: " + " -> ".join((*trail, node)))
            return
        visiting.add(node)
        for dep in graph.get(node, []):
            if dep in graph:
                visit(dep, (*trail, node))
        visiting.remove(node)
        visited.add(node)

    for node in graph:
        visit(node, ())
    return errors


def validate_contract_data(contract: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if contract.get("schema") != "rll.scientific_validation_orchestrator.v1":
        errors.append("unexpected scientific orchestrator schema")
    if contract.get("claim_allowed") is not False:
        errors.append("contract claim_allowed must remain false")
    if contract.get("publication_effect") != "NONE":
        errors.append("contract publication_effect must remain NONE")
    if contract.get("execution_effect") != "NONE_UNTIL_EXPLICITLY_WIRED":
        errors.append("contract execution_effect must remain inert until explicitly wired")

    gates = contract.get("gates")
    if not isinstance(gates, list) or not gates:
        errors.append("contract gates must be a non-empty list")
        return errors

    ids: list[str] = []
    for gate in gates:
        if not isinstance(gate, dict):
            errors.append("every gate must be an object")
            continue
        gate_id = str(gate.get("id", "")).strip()
        ids.append(gate_id)
        if not gate_id:
            errors.append("gate id must be non-empty")
        for key in ("name", "priority", "requires", "must_produce", "pass_when", "stop_when"):
            if key not in gate:
                errors.append(f"{gate_id or '<missing>'}: missing {key}")
    if len(ids) != len(set(ids)):
        errors.append("gate ids must be unique")
    known = set(ids)
    for gate in gates:
        if not isinstance(gate, dict):
            continue
        gate_id = str(gate.get("id", ""))
        requires = gate.get("requires", [])
        if not isinstance(requires, list):
            errors.append(f"{gate_id}: requires must be a list")
            continue
        unknown = sorted(str(dep) for dep in requires if str(dep) not in known)
        if unknown:
            errors.append(f"{gate_id}: unknown dependencies: {', '.join(unknown)}")
    errors.extend(_cycle_errors([g for g in gates if isinstance(g, dict)]))
    return errors


def validate_urgency_data(ledger: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if ledger.get("schema") != "rll.scientific_validation_urgency.v1":
        errors.append("unexpected urgency ledger schema")
    if ledger.get("claim_allowed") is not False:
        errors.append("urgency ledger claim_allowed must remain false")
    entries = ledger.get("entries")
    if not isinstance(entries, list) or not entries:
        errors.append("urgency entries must be a non-empty list")
        return errors

    required = {
        "id",
        "urgency",
        "target_gate",
        "name",
        "state",
        "prerequisites",
        "source",
        "provider",
        "method",
        "falsifier",
        "providencia",
        "next_observable_step",
        "success_transition",
        "factors",
        "score",
        "claim_allowed",
    }
    ids: list[str] = []
    for entry in entries:
        if not isinstance(entry, dict):
            errors.append("urgency entry must be an object")
            continue
        missing = sorted(required - set(entry))
        entry_id = str(entry.get("id", "<missing>"))
        ids.append(entry_id)
        if missing:
            errors.append(f"{entry_id}: missing fields: {', '.join(missing)}")
            continue
        if entry.get("claim_allowed") is not False:
            errors.append(f"{entry_id}: claim_allowed must remain false")
        factors = entry.get("factors")
        if not isinstance(factors, dict):
            errors.append(f"{entry_id}: factors must be an object")
            continue
        factor_names = (
            "uncertainty_reduction",
            "scientific_leverage",
            "independence",
            "observability",
            "execution_cost",
            "regression_risk",
        )
        if any(name not in factors for name in factor_names):
            errors.append(f"{entry_id}: incomplete priority factors")
            continue
        values = {name: float(factors[name]) for name in factor_names}
        if any(value < 1.0 or value > 5.0 for value in values.values()):
            errors.append(f"{entry_id}: every factor must be in 1..5")
            continue
        expected = (
            values["uncertainty_reduction"]
            * values["scientific_leverage"]
            * values["independence"]
            * values["observability"]
            / (values["execution_cost"] * values["regression_risk"])
        )
        if not math.isclose(float(entry["score"]), expected, rel_tol=0.0, abs_tol=1e-6):
            errors.append(f"{entry_id}: score mismatch ({entry['score']} != {expected})")
        if not str(entry.get("next_observable_step", "")).strip():
            errors.append(f"{entry_id}: next_observable_step must not be empty")
        if not str(entry.get("falsifier", "")).strip():
            errors.append(f"{entry_id}: falsifier must not be empty")
    if len(ids) != len(set(ids)):
        errors.append("urgency ids must be unique")
    return errors


def validate_desi_covariance(path: Path) -> dict[str, Any]:
    result: dict[str, Any] = {
        "path": str(path.relative_to(ROOT)) if path.is_relative_to(ROOT) else str(path),
        "sha256": sha256_file(path),
        "status": "TOKEN_VAZIO_DESI_COVARIANCE",
        "rows": 0,
        "columns": 0,
        "symmetric": False,
        "positive_diagonal": False,
        "claim_allowed": False,
    }
    if not path.is_file():
        return result
    try:
        with path.open(newline="", encoding="utf-8") as handle:
            rows = list(csv.reader(handle))
        if len(rows) != 14 or len(rows[0]) != 14:
            result["status"] = "BLOCKED_DESI_COVARIANCE_SHAPE"
            return result
        header = rows[0][1:]
        if header != [str(i) for i in range(13)]:
            result["status"] = "BLOCKED_DESI_COVARIANCE_HEADER_ORDER"
            return result
        matrix: list[list[float]] = []
        for index, row in enumerate(rows[1:]):
            if len(row) != 14 or row[0] != str(index):
                result["status"] = "BLOCKED_DESI_COVARIANCE_ROW_ORDER"
                return result
            matrix.append([float(value) for value in row[1:]])
    except (OSError, ValueError):
        result["status"] = "BLOCKED_DESI_COVARIANCE_PARSE"
        return result

    result["rows"] = 13
    result["columns"] = 13
    symmetric = all(
        math.isclose(matrix[i][j], matrix[j][i], rel_tol=0.0, abs_tol=1e-12)
        for i in range(13)
        for j in range(13)
    )
    positive_diagonal = all(matrix[i][i] > 0.0 for i in range(13))
    result["symmetric"] = symmetric
    result["positive_diagonal"] = positive_diagonal
    if not symmetric:
        result["status"] = "BLOCKED_DESI_COVARIANCE_ASYMMETRY"
    elif not positive_diagonal:
        result["status"] = "BLOCKED_DESI_COVARIANCE_DIAGONAL"
    else:
        result["status"] = "READY_DESI_13X13_MATRIX"
    return result


def load_pantheon_verifier(path: Path = PANTHEON_VERIFIER_PATH) -> ModuleType:
    spec = importlib.util.spec_from_file_location("rll_pantheon_readiness_v2", path)
    if spec is None or spec.loader is None:
        raise ValidationError(f"cannot load Pantheon verifier: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def pantheon_readiness(root: Path = ROOT) -> dict[str, Any]:
    module = load_pantheon_verifier(root / "scripts/verify_pantheon_inputs.py")
    data_dir = root / module.CANONICAL_DATA_DIR
    report = module._build_report(data_dir)
    report["claim_allowed"] = False
    return report


def _dependency_status(g2_state: str) -> dict[str, str]:
    if g2_state == READY_G2:
        g3 = "READY_TO_EXECUTE_COMPATIBILITY_NOT_PASSED"
        g4 = "WAITING_FOR_G3_RESULT"
        g5 = "READY_TO_BUILD_AFTER_G3_G4"
    else:
        g3 = "BLOCKED_BY_G2"
        g4 = "BLOCKED_BY_G2_G3"
        g5 = "BLOCKED_BY_G2"
    return {
        "G0": "READY_GOVERNANCE_CHECK_NOT_SCIENTIFIC_PASS",
        "G1": "READY_STRUCTURAL_CHECK_NOT_SCIENTIFIC_PASS",
        "G2": g2_state,
        "G3": g3,
        "G4": g4,
        "G5": g5,
        "G6": "BLOCKED_BY_G5",
        "G7": "BLOCKED_BY_G6",
        "G8": "TOKEN_VAZIO_PHYSICAL_CLOSURE",
        "G9": "BLOCKED_BY_G8",
        "G10": "BLOCKED_BY_G6",
        "G11": "BLOCKED_BY_G7_G10",
    }


def build_readiness(root: Path = ROOT) -> dict[str, Any]:
    contract = load_json(root / "data/contracts/rll_scientific_validation_orchestrator.v1.json")
    urgency = load_json(root / "data/governance/RLL_SCIENTIFIC_VALIDATION_URGENCY_20260819_V1.json")
    contract_errors = validate_contract_data(contract)
    urgency_errors = validate_urgency_data(urgency)
    desi = validate_desi_covariance(root / "data/real/desi_dr2_bao_covariance.csv")
    pantheon = pantheon_readiness(root)

    desi_ready = desi["status"] == "READY_DESI_13X13_MATRIX"
    pantheon_full_ready = bool(pantheon.get("full_covariance_likelihood_ready"))
    if desi_ready and pantheon_full_ready:
        g2_state = READY_G2
    elif desi_ready and pantheon.get("route_state") == "TOKEN_VAZIO_FULL_COVARIANCE":
        g2_state = TOKEN_VAZIO_G2
    elif not desi_ready:
        g2_state = "BLOCKED_DESI_COVARIANCE"
    else:
        g2_state = "BLOCKED_PANTHEON_COVARIANCE"

    gate_states = _dependency_status(g2_state)
    readiness_paths = {
        "structural_core": STRUCTURAL_CORE_PATH,
        "structural_workflow": STRUCTURAL_WORKFLOW_PATH,
        "joint_likelihood": JOINT_LIKELIHOOD_PATH,
        "fase20_inference": FASE20_PATH,
    }
    located = {name: path.is_file() for name, path in readiness_paths.items()}

    urgency_entries = urgency["entries"]
    actionable = [
        {
            "id": entry["id"],
            "urgency": entry["urgency"],
            "target_gate": entry["target_gate"],
            "name": entry["name"],
            "state": entry["state"],
            "score": entry["score"],
            "next_observable_step": entry["next_observable_step"],
        }
        for entry in urgency_entries
        if not str(entry["state"]).startswith("BLOCKED_BY_")
    ]
    actionable.sort(key=lambda item: (0 if str(item["urgency"]).startswith("P0") else 1, -float(item["score"]), item["id"]))

    token_vazio = []
    if g2_state == TOKEN_VAZIO_G2:
        token_vazio.append("TOKEN_VAZIO_FULL_COVARIANCE")
    if gate_states["G8"].startswith("TOKEN_VAZIO"):
        token_vazio.append(gate_states["G8"])

    return {
        "schema": "rll.scientific_validation_readiness.v2",
        "repo_ref": git_sha(root),
        "claim_allowed": False,
        "publication_effect": "NONE",
        "scientific_confirmation": False,
        "contract": {
            "path": str(CONTRACT_PATH.relative_to(ROOT)),
            "sha256": sha256_file(root / CONTRACT_PATH.relative_to(ROOT)),
            "valid": not contract_errors,
            "errors": contract_errors,
        },
        "urgency_ledger": {
            "path": str(URGENCY_PATH.relative_to(ROOT)),
            "sha256": sha256_file(root / URGENCY_PATH.relative_to(ROOT)),
            "valid": not urgency_errors,
            "errors": urgency_errors,
        },
        "located_existing_routes": located,
        "G2_inputs": {
            "DESI": desi,
            "PantheonPlus": pantheon,
        },
        "gate_states": gate_states,
        "current_frontier": ["RLL-SV-P0-001", "RLL-SV-P0-002"] if g2_state != READY_G2 else ["G3", "G4", "G5"],
        "actionable_now": actionable,
        "token_vazio": token_vazio,
        "boundaries": {
            "readiness_is_scientific_pass": False,
            "desi_matrix_presence_proves_point_order": False,
            "pantheon_diagonal_diagnostic_is_full_likelihood": False,
            "downstream_gate_can_bypass_failed_prerequisite": False,
            "negative_result_can_be_discarded": False,
        },
        "F_ok": "contract and urgency can be validated; DESI covariance is checked structurally; Pantheon readiness reuses the existing canonical verifier",
        "F_gap": "Pantheon STAT+SYS full covariance and order-bound cross-dataset manifest remain required before canonical G2/G5 promotion",
        "F_next": "materialize verified Pantheon STAT+SYS bytes; bind DESI covariance to ordered primary points; then unlock compatibility and canonical likelihood work",
    }


def write_receipt(path: Path, report: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    path.write_text(payload, encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description="Validate RLL scientific orchestration readiness without promoting claims")
    parser.add_argument("--json", action="store_true", help="print machine-readable readiness receipt")
    parser.add_argument("--write-receipt", type=Path, default=None, help="write readiness JSON to this path")
    parser.add_argument("--require-g2", action="store_true", help="exit non-zero until full-covariance G2 inputs are ready")
    args = parser.parse_args()

    report = build_readiness(ROOT)
    if args.write_receipt is not None:
        write_receipt(args.write_receipt, report)
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print("[rll] scientific validation readiness v2")
        print(f"contract_valid={str(report['contract']['valid']).lower()}")
        print(f"urgency_valid={str(report['urgency_ledger']['valid']).lower()}")
        print(f"G2={report['gate_states']['G2']}")
        print(f"G5={report['gate_states']['G5']}")
        print(f"claim_allowed={str(report['claim_allowed']).lower()}")
        print("frontier=" + ",".join(report["current_frontier"]))

    if not report["contract"]["valid"] or not report["urgency_ledger"]["valid"]:
        return 2
    if args.require_g2 and report["gate_states"]["G2"] != READY_G2:
        return 3
    return 0


if __name__ == "__main__":
    sys.exit(main())
