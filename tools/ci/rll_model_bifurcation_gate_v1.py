#!/usr/bin/env python3
from __future__ import annotations

import json
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "data/governance/RLL_MODEL_BIFURCATION_FCISUG_V1.json"
BRANCH_CONTRACT = ROOT / "data/governance/RLL_BRANCH_CONTRACT_V1.json"
EXPECTED_BRANCHES = {"F", "C", "I", "S", "U", "G"}
REQUIRED_BRANCH_FIELDS = {
    "id", "predecessor_route", "status", "urgency", "evidence_state",
    "equations", "provenance", "gaps", "falsifiers", "promotion_gate", "rollback",
}


def _typed_token(value: Any) -> bool:
    return isinstance(value, str) and value.startswith("TOKEN_VAZIO_")


def validate(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "rll.model_bifurcation.fcisug.v1":
        errors.append("SCHEMA_MISMATCH")
    if data.get("claim_allowed") is not False:
        errors.append("CLAIM_BOUNDARY_OPEN")
    if not _typed_token(data.get("selected_physical_winner")):
        errors.append("PHYSICAL_WINNER_PRESELECTED_OR_UNTYPED")

    comparison = data.get("comparison_contract")
    if not isinstance(comparison, dict):
        errors.append("MISSING_COMPARISON_CONTRACT")
    else:
        for key in ("same_data", "same_covariance", "same_nuisance_policy", "same_convergence_policy"):
            if comparison.get(key) is not True:
                errors.append("UNFAIR_COMPARISON:" + key)
        if comparison.get("point_evaluation_is_fit") is not False:
            errors.append("POINT_EVALUATION_PROMOTED_TO_FIT")
        if comparison.get("bic_approximation_is_nested_evidence") is not False:
            errors.append("BIC_PROMOTED_TO_EVIDENCE")

    branches = data.get("branches")
    if not isinstance(branches, dict) or set(branches) != EXPECTED_BRANCHES:
        errors.append("BRANCH_SET_MISMATCH")
        return errors

    for key, branch in branches.items():
        if not isinstance(branch, dict):
            errors.append("INVALID_BRANCH:" + key)
            continue
        missing = REQUIRED_BRANCH_FIELDS - set(branch)
        if missing:
            errors.append("MISSING_FIELDS:" + key + ":" + ",".join(sorted(missing)))
        if branch.get("urgency") not in {"P0", "P1", "P2"}:
            errors.append("UNTYPED_URGENCY:" + key)
        if not branch.get("provenance"):
            errors.append("MISSING_PROVENANCE:" + key)
        if not branch.get("falsifiers"):
            errors.append("MISSING_FALSIFIER:" + key)
        if not branch.get("promotion_gate"):
            errors.append("MISSING_PROMOTION_GATE:" + key)
        if not branch.get("rollback"):
            errors.append("MISSING_ROLLBACK:" + key)
        for gap in branch.get("gaps", []):
            if not _typed_token(gap):
                errors.append("UNTYPED_GAP:" + key + ":" + str(gap))
        status = str(branch.get("status", ""))
        if "PASS_GLOBAL" in status:
            errors.append("FORBIDDEN_GLOBAL_PASS:" + key)
        if key in {"S", "U", "G"} and not _typed_token(status):
            errors.append("OPEN_BRANCH_FALSELY_PROMOTED:" + key)
        if key in {"S", "U", "G"} and branch.get("evidence_state") != "TOKEN_VAZIO":
            errors.append("OPEN_BRANCH_EVIDENCE_FALSELY_PROMOTED:" + key)

    gates = data.get("global_gates")
    if not isinstance(gates, dict) or not gates or not all(value is True for value in gates.values()):
        errors.append("GLOBAL_GATES_NOT_FAIL_CLOSED")
    return errors


def validate_branch_contract(data: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if data.get("schema") != "rll.branch_contract.v1":
        errors.append("BRANCH_CONTRACT_SCHEMA_MISMATCH")
    if data.get("claim_allowed") is not False:
        errors.append("BRANCH_CONTRACT_CLAIM_BOUNDARY_OPEN")
    if set(data.get("result_relation_types", {})) != {"E1", "E2", "E3"}:
        errors.append("RESULT_RELATION_TYPES_INCOMPLETE")
    core = data.get("core", {})
    if core.get("derivative_coordinate") != "prime=d/dln(a)":
        errors.append("DERIVATIVE_COORDINATE_UNFROZEN")
    if core.get("sign_invariant") != "q_s=A*f_prime*(1-a^-3)<=0":
        errors.append("INTERACTION_SIGN_INVARIANT_MISSING")
    required = set(data.get("required_contract_fields", []))
    branches = data.get("branches", {})
    if set(branches) != EXPECTED_BRANCHES:
        errors.append("BRANCH_CONTRACT_SET_MISMATCH")
        return errors
    for key, branch in branches.items():
        missing = required - set(branch)
        if missing:
            errors.append("BRANCH_CONTRACT_MISSING_FIELDS:" + key + ":" + ",".join(sorted(missing)))
        for field in required:
            value = branch.get(field)
            if not isinstance(value, list) or not value:
                errors.append("BRANCH_CONTRACT_EMPTY_FIELD:" + key + ":" + field)
    policy = data.get("freeze_policy", {})
    expected_policy = {
        "pre_result_registration": True,
        "negative_results_append_only": True,
        "refuted_branch_remains_historical": True,
        "refuted_branch_remains_physically_viable": False,
        "post_result_parameter_or_equation_change_requires_successor_version": True,
    }
    if policy != expected_policy:
        errors.append("FREEZE_POLICY_NOT_FAIL_CLOSED")
    return errors


def main() -> int:
    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    branch_data = json.loads(BRANCH_CONTRACT.read_text(encoding="utf-8"))
    errors = validate(data) + validate_branch_contract(branch_data)
    if errors:
        print(json.dumps({"status": "FAIL", "errors": errors}, indent=2))
        return 1
    print(json.dumps({
        "status": "PASS_SCOPED",
        "claim_allowed": False,
        "branches": sorted(EXPECTED_BRANCHES),
        "contract": str(CONTRACT.relative_to(ROOT)),
        "branch_contract": str(BRANCH_CONTRACT.relative_to(ROOT)),
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
