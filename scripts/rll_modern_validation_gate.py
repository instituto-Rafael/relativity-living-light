#!/usr/bin/env python3
"""Fail-closed evaluator for modern RLL observational-validation gaps.

The evaluator never treats a paper citation, BIC proxy, backend import, or dataset
name as materialized scientific evidence.  A gap closes only when the registry's
required receipt exists, is explicitly VERIFIED, preserves claim_allowed=false,
and contains the declared provenance/result fields.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

SCHEMA = "rll.modern_validation_gate_receipt.v1"
REGISTRY_SCHEMA = "rll.modern_validation_gap_registry.v1"
DEFAULT_REGISTRY = Path("data/governance/RLL_MODERN_VALIDATION_GAPS_20260807_V1.json")


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as stream:
        for chunk in iter(lambda: stream.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: JSON root must be an object")
    return value


def git_sha(repo_root: Path) -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"], cwd=repo_root, text=True, stderr=subprocess.DEVNULL
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def validate_registry(registry: dict[str, Any]) -> None:
    if registry.get("schema") != REGISTRY_SCHEMA:
        raise ValueError(f"registry schema must be {REGISTRY_SCHEMA!r}")
    if registry.get("claim_allowed") is not False:
        raise ValueError("registry must preserve claim_allowed=false")
    if registry.get("publication_ready") is not False:
        raise ValueError("registry must preserve publication_ready=false")
    policy = registry.get("policy")
    if not isinstance(policy, dict):
        raise ValueError("registry policy must be an object")
    required_policy = {
        "token_vazio_is_auditable_state": True,
        "paper_is_context_not_materialized_evidence": True,
        "bic_proxy_is_not_bayesian_evidence": True,
        "backend_import_is_not_perturbation_validation": True,
        "dataset_name_is_not_likelihood_provenance": True,
        "all_models_must_share_data_priors_and_nuisance_policy": True,
        "negative_results_must_be_preserved": True,
    }
    for key, expected in required_policy.items():
        if policy.get(key) is not expected:
            raise ValueError(f"registry policy {key!r} must be {expected!r}")
    gates = registry.get("gates")
    if not isinstance(gates, list) or not gates:
        raise ValueError("registry requires a non-empty gates list")
    seen: set[str] = set()
    for idx, gate in enumerate(gates):
        if not isinstance(gate, dict):
            raise ValueError(f"gate {idx} must be an object")
        gate_id = gate.get("id")
        if not isinstance(gate_id, str) or not gate_id:
            raise ValueError(f"gate {idx} requires an id")
        if gate_id in seen:
            raise ValueError(f"duplicate gate id: {gate_id}")
        seen.add(gate_id)
        if gate.get("priority") not in {"P0", "P1", "P2"}:
            raise ValueError(f"{gate_id}: unsupported priority")
        token = gate.get("token_vazio")
        if not isinstance(token, str) or not token.startswith("TOKEN_VAZIO_"):
            raise ValueError(f"{gate_id}: token_vazio must be explicit")
        artifacts = gate.get("required_artifacts")
        if not isinstance(artifacts, list) or not artifacts:
            raise ValueError(f"{gate_id}: required_artifacts must be non-empty")
        for artifact in artifacts:
            if not isinstance(artifact, dict):
                raise ValueError(f"{gate_id}: artifact contract must be an object")
            for key in ("id", "path", "expected_state", "required_keys"):
                if key not in artifact:
                    raise ValueError(f"{gate_id}: artifact contract missing {key}")


def _meaningfully_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        return bool(value.strip())
    if isinstance(value, (list, tuple, dict, set)):
        return bool(value)
    return True


def validate_materialized_receipt(path: Path, contract: dict[str, Any]) -> tuple[bool, list[str], dict[str, Any] | None]:
    if not path.is_file():
        return False, ["missing_receipt"], None
    try:
        payload = load_json(path)
    except (OSError, json.JSONDecodeError, ValueError) as exc:
        return False, [f"invalid_json:{type(exc).__name__}"], None

    reasons: list[str] = []
    expected_state = contract.get("expected_state", "VERIFIED")
    if payload.get("state") != expected_state:
        reasons.append(f"state_not_{expected_state}")
    if payload.get("claim_allowed") is not False:
        reasons.append("claim_allowed_must_be_false")

    required_keys = contract.get("required_keys", [])
    if not isinstance(required_keys, list):
        reasons.append("invalid_required_keys_contract")
    else:
        for key in required_keys:
            if key not in payload or not _meaningfully_present(payload.get(key)):
                reasons.append(f"missing_or_empty:{key}")

    # Real Bayesian evidence is not closed by a sampler run without an explicit
    # independent reproduction, even when a producer accidentally labels itself VERIFIED.
    if "independent_replication" in required_keys and payload.get("independent_replication") is not True:
        reasons.append("independent_replication_not_true")

    return not reasons, sorted(set(reasons)), payload


def evaluate_registry(registry: dict[str, Any], repo_root: Path) -> dict[str, Any]:
    validate_registry(registry)
    gate_results: list[dict[str, Any]] = []
    token_vazio: list[str] = []

    for gate in registry["gates"]:
        artifact_results: list[dict[str, Any]] = []
        gate_verified = True
        for contract in gate["required_artifacts"]:
            rel_path = Path(str(contract["path"]))
            path = repo_root / rel_path
            verified, reasons, _payload = validate_materialized_receipt(path, contract)
            gate_verified = gate_verified and verified
            artifact_results.append(
                {
                    "id": contract["id"],
                    "path": rel_path.as_posix(),
                    "exists": path.is_file(),
                    "verified": verified,
                    "sha256": sha256_file(path) if path.is_file() else None,
                    "reasons": reasons,
                }
            )

        if not gate_verified:
            token_vazio.append(str(gate["token_vazio"]))
        gate_results.append(
            {
                "id": gate["id"],
                "priority": gate["priority"],
                "state": "VERIFIED_MATERIALIZED_RECEIPT" if gate_verified else "BLOCKED_TOKEN_VAZIO",
                "verified": gate_verified,
                "token_vazio": None if gate_verified else gate["token_vazio"],
                "artifacts": artifact_results,
            }
        )

    unresolved_p0 = [g["id"] for g in gate_results if g["priority"] == "P0" and not g["verified"]]
    unresolved_p1 = [g["id"] for g in gate_results if g["priority"] == "P1" and not g["verified"]]
    all_verified = all(g["verified"] for g in gate_results)
    p0_ready = not unresolved_p0

    if all_verified:
        scientific_gate = "READY_FOR_INDEPENDENT_HUMAN_REVIEW"
        next_action = "INDEPENDENT_HUMAN_REVIEW_REQUIRED"
    elif not p0_ready:
        scientific_gate = "BLOCKED_P0_TOKEN_VAZIO"
        next_action = f"MATERIALIZE_RECEIPT:{unresolved_p0[0]}"
    else:
        scientific_gate = "P0_READY_P1_BLOCKED"
        next_action = f"MATERIALIZE_RECEIPT:{unresolved_p1[0]}" if unresolved_p1 else "REVIEW_REGISTRY"

    return {
        "schema": SCHEMA,
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "scientific_gate": scientific_gate,
        "claim_allowed": False,
        "publication_ready": False,
        "automatic_promotion_forbidden": True,
        "p0_ready": p0_ready,
        "all_gates_verified": all_verified,
        "unresolved_p0": unresolved_p0,
        "unresolved_p1": unresolved_p1,
        "token_vazio": sorted(set(token_vazio)),
        "gates": gate_results,
        "next_action": next_action,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--registry", type=Path, default=DEFAULT_REGISTRY)
    parser.add_argument("--repo-root", type=Path, default=Path(__file__).resolve().parents[1])
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()

    repo_root = args.repo_root.resolve()
    registry_path = args.registry if args.registry.is_absolute() else repo_root / args.registry
    registry = load_json(registry_path)
    receipt = evaluate_registry(registry, repo_root)
    receipt.update(
        {
            "repository": registry.get("repository"),
            "source_git_sha": git_sha(repo_root),
            "registry_path": str(registry_path.relative_to(repo_root)),
            "registry_sha256": sha256_file(registry_path),
        }
    )

    output = args.output if args.output.is_absolute() else repo_root / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(receipt, ensure_ascii=False, indent=2, sort_keys=True))
    return 0 if receipt["all_gates_verified"] else 3


if __name__ == "__main__":
    raise SystemExit(main())
