#!/usr/bin/env python3
"""Fail-closed audit for the RLL quantum-vacuum birefringence crosswalk.

The tool reads committed metadata only. It neither fetches external papers/data
nor writes back to the repository; its optional output directory is reserved for
CI artifacts and local receipts.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import subprocess
from datetime import datetime, timezone
from pathlib import Path
from typing import Any


ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/real_sources/rll_quantum_vacuum_birefringence_crosswalk_20260903.v1.json"
EXPECTED_TOKENS = {
    "TV-QED-VB-SOURCE-BYTES-20260903",
    "TV-QED-VB-REPRODUCTION-20260903",
    "TV-RLL-QED-EXACT-FORMULA-20260903",
    "TV-RLL-QED-COSMOLOGY-TRANSFER-20260903",
}
EXPECTED_TESTS = {
    "TEST-QED-VB-REPRODUCE-POLARIMETRY",
    "TEST-RLL-QED-OBSERVABLE-MAP",
    "TEST-RLL-QED-COSMOLOGY-TRANSFER",
}


def sha256(path: Path) -> str:
    return hashlib.sha256(path.read_bytes()).hexdigest()


def git_commit() -> str:
    result = subprocess.run(
        ["git", "rev-parse", "HEAD"],
        cwd=ROOT,
        check=False,
        capture_output=True,
        text=True,
    )
    return result.stdout.strip() if result.returncode == 0 else "TOKEN_VAZIO_GIT_HEAD_UNAVAILABLE"


def require(condition: bool, message: str) -> None:
    if not condition:
        raise ValueError(message)


def validate(path: Path = PATH, profile: str = "light") -> dict[str, Any]:
    """Validate the immutable claim boundary and the selected audit profile."""
    data = json.loads(path.read_text(encoding="utf-8"))
    require(data["schema"] == "rll.quantum_vacuum_birefringence_crosswalk.v1", "unexpected schema")
    require(data["append_only"] is True, "append_only must be true")
    require(data["claim_allowed"] is False, "claim_allowed must remain false")
    require(data["publication_effect"] == "NONE", "publication_effect must remain NONE")

    policy = data["policy"]
    for field in (
        "media_discovery_is_primary_evidence",
        "external_paper_is_rll_confirmation",
        "analogical_relation_is_physical_equivalence",
        "repository_ci_may_write_repository",
        "repository_ci_may_ingest_external_data",
    ):
        require(policy[field] is False, f"policy.{field} must be false")
    require(policy["negative_results_preserved"] is True, "negative results must be preserved")
    require(policy["default_missing_state"] == "TOKEN_VAZIO", "default missing state must be TOKEN_VAZIO")

    sources = {item["source_id"]: item for item in data["sources"]}
    require(
        set(sources) == {
            "SRC-QED-VB-STEWARD-NATURE-2026",
            "SRC-QED-VB-STEWARD-ARXIV-V5-2026",
            "SRC-QED-VB-INOVACAO-20260901",
        },
        "unexpected source set",
    )
    require(sources["SRC-QED-VB-STEWARD-NATURE-2026"]["source_class"] == "PRIMARY_PEER_REVIEWED_PAPER", "Nature source class")
    require(sources["SRC-QED-VB-STEWARD-ARXIV-V5-2026"]["version"] == "v5", "arXiv version must be pinned")
    require(
        sources["SRC-QED-VB-INOVACAO-20260901"]["source_class"] == "DISCOVERY_CONTEXT_NOT_PRIMARY_EVIDENCE",
        "media source must remain discovery-only",
    )
    for source in sources.values():
        require(source["claim_allowed"] is False, f"{source['source_id']} must be claim-closed")
        require(str(source["source_bytes_sha256"]).startswith(("TOKEN_VAZIO_", "OPEN_")), "source hash status missing")

    context = {item["context_id"]: item for item in data["rll_context"]}
    require("RLL-CTX-OBSERVER-MIRROR-PHOTON-GATE-20260815" in context, "synthetic RLL boundary missing")
    require("SYNTHETIC" in context["RLL-CTX-OBSERVER-MIRROR-PHOTON-GATE-20260815"]["evidence_class"], "synthetic boundary weakened")
    require("SEPARATE_OBSERVABLE" in context["RLL-CTX-DESI-DR2-BAO-2026"]["safe_relation"], "DESI boundary weakened")
    require("TOKEN_VAZIO_NO_EXACT_RLL_QED_FORMULA" in context["RLL-CTX-FORMULA-LITERATURE-GRAPH-20260822"]["safe_relation"], "exact-formula gap missing")

    for claim in data["directly_supported"]:
        require(claim["claim_allowed"] is False, "direct-support claim must be closed")
        require(claim["source_ids"], "direct-support claim needs sources")
    for relation in data["analogous_only"]:
        require(relation["claim_allowed"] is False, "analogy must remain claim-closed")
        require("not" in relation["boundary"].lower(), "analogy boundary must be explicit")

    tokens = {item["id"] for item in data["token_vazio"]}
    require(tokens == EXPECTED_TOKENS, "TOKEN_VAZIO set changed without validator update")
    require(all(item["state"].startswith("TOKEN_VAZIO") for item in data["token_vazio"]), "all gaps must remain TOKEN_VAZIO")
    require(all(item["next_verifiable_step"] for item in data["token_vazio"]), "each gap needs a next step")

    if profile == "deep":
        routes = {item["test_id"]: item for item in data["testable_routes"]}
        require(set(routes) == EXPECTED_TESTS, "unexpected test-route set")
        for route in routes.values():
            require(route["state"].startswith("TOKEN_VAZIO"), "test route must remain evidence-open")
            require(len(route["baselines"]) >= 2, "test route needs adversary baseline")
            require(len(route["metrics"]) >= 2, "test route needs multiple metrics")
            require(len(route["required_evidence"]) >= 4, "test route needs an evidence contract")
            require(len(route["falsifier"]) >= 80, "test route falsifier is underspecified")
            require(route["claim_allowed"] is False, "test route must remain claim-closed")
        invariants = set(data["invariants"])
        require("QED_MAGNETAR_OBSERVATION_NE_RLL_CONFIRMATION" in invariants, "primary boundary missing")
        require("CI_ARTIFACT_NE_REPOSITORY_WRITE" in invariants, "CI write boundary missing")
    elif profile != "light":
        raise ValueError(f"unknown profile: {profile}")

    return data


def audit(profile: str, output_dir: Path, path: Path = PATH) -> dict[str, Any]:
    """Validate and write an artifact-only receipt for the selected profile."""
    data = validate(path=path, profile=profile)
    output_dir.mkdir(parents=True, exist_ok=True)
    input_hash = sha256(path)
    receipt = {
        "schema": "rll.quantum_vacuum_birefringence_crosswalk_audit_receipt.v1",
        "record_id": data["record_id"],
        "generated_at_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "audit_profile": profile,
        "commit_sha": git_commit(),
        "input_path": path.relative_to(ROOT).as_posix(),
        "input_sha256": input_hash,
        "claim_allowed": False,
        "publication_effect": "NONE",
        "repository_write_attempted": False,
        "external_data_ingestion_attempted": False,
        "falsification_state": "TOKEN_VAZIO_NO_TYPED_RLL_QED_FORWARD_MODEL",
        "escalation": {
            "on_light_failure": "fail_closed; inspect the artifact and dispatch the deep profile manually",
            "on_source_or_contract_change": "deep profile runs through pull_request or push path filters",
            "daily_deep_profile": "scheduled separately by the workflow"
        },
        "validated": [
            "claim boundary",
            "source-role separation",
            "RLL synthetic-proxy boundary",
            "TOKEN_VAZIO completeness",
            "deep test-route contract" if profile == "deep" else "lightweight metadata contract"
        ]
    }
    (output_dir / "receipt.json").write_text(json.dumps(receipt, indent=2) + "\n", encoding="utf-8")
    (output_dir / "input.sha256").write_text(
        f"{input_hash}  {path.relative_to(ROOT).as_posix()}\n", encoding="utf-8"
    )
    return receipt


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--profile", choices=("light", "deep"), default="light")
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts/rll-quantum-vacuum-crosswalk")
    args = parser.parse_args()
    receipt = audit(args.profile, args.output_dir)
    print(
        "PASS: quantum-vacuum crosswalk is claim-closed "
        f"({receipt['audit_profile']} profile; artifact-only receipt written)"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
