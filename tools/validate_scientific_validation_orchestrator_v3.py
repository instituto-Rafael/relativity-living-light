#!/usr/bin/env python3
"""Receipt-aware successor to Scientific Validation Orchestrator V2.

V3 solves a specific custody problem: large primary inputs need not be committed
into Git to count as materialized evidence. A persisted small receipt may close
G2 only when it is hash-bound to the exact primary source, exact bytes, exact
matrix shape/value count, and a successful strict verifier run.

This changes readiness, not scientific truth. `claim_allowed` remains false.
"""
from __future__ import annotations

import argparse
import importlib.util
import json
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
V2_PATH = ROOT / "tools/validate_scientific_validation_orchestrator_v2.py"
DESI_BINDER_PATH = ROOT / "tools/build_desi_covariance_order_receipt.py"
PANTHEON_RECEIPT_PATH = ROOT / "artifacts/pantheon/RLL_PANTHEON_FULL_COVARIANCE_MATERIALIZATION_RECEIPT_20260819_RUN32285275333.json"

EXPECTED = {
    "provider": "PantheonPlusSH0ES/DataRelease",
    "source_commit": "c447f0fea703fcd0fff57de5000947b5ca81286b",
    "catalog_blob": "cce857db0c15e9ce7a0e0ce77452b6ff62af969a",
    "covariance_blob": "d1a1498154e7ba826df14bdbef35ebcb7f5efba1",
    "catalog_sha256": "1cb0fc379ef066afdc2ffd1857681cc478024570d8a3eba284fb645775198cf8",
    "covariance_sha256": "abf806d966485e64afdb359c87bffc0ecc00d05eff0a31ced66f247385df0fdc",
    "catalog_bytes": 579283,
    "covariance_bytes": 33284960,
    "matrix_dimension": 1701,
    "matrix_values": 2893401,
}

READY_G2_RECEIPT = "READY_G2_INPUTS_BY_HASH_BOUND_MATERIALIZATION_RECEIPT"


class ReceiptValidationError(RuntimeError):
    pass


def _load_module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise ReceiptValidationError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ReceiptValidationError(f"{path}: top-level JSON must be an object")
    return value


def validate_pantheon_receipt(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("schema") != "rll.pantheon_full_covariance_materialization_receipt.v1":
        errors.append("unexpected Pantheon receipt schema")
    if receipt.get("provider") != EXPECTED["provider"]:
        errors.append("Pantheon provider mismatch")
    if receipt.get("source_commit") != EXPECTED["source_commit"]:
        errors.append("Pantheon source commit mismatch")
    blobs = receipt.get("source_git_blobs", {})
    if blobs.get("Pantheon+SH0ES.dat") != EXPECTED["catalog_blob"]:
        errors.append("Pantheon catalog Git blob mismatch")
    if blobs.get("Pantheon+SH0ES_STAT+SYS.cov") != EXPECTED["covariance_blob"]:
        errors.append("Pantheon covariance Git blob mismatch")

    files = receipt.get("files", {})
    catalog = files.get("Pantheon+SH0ES.dat", {})
    covariance = files.get("Pantheon+SH0ES_STAT+SYS.cov", {})
    exact_checks = [
        (catalog.get("sha256"), EXPECTED["catalog_sha256"], "catalog SHA-256"),
        (catalog.get("bytes"), EXPECTED["catalog_bytes"], "catalog size"),
        (covariance.get("sha256"), EXPECTED["covariance_sha256"], "covariance SHA-256"),
        (covariance.get("bytes"), EXPECTED["covariance_bytes"], "covariance size"),
        (covariance.get("matrix_dimension"), EXPECTED["matrix_dimension"], "covariance dimension"),
        (covariance.get("matrix_values"), EXPECTED["matrix_values"], "covariance value count"),
    ]
    for actual, expected, label in exact_checks:
        if actual != expected:
            errors.append(f"{label} mismatch: {actual!r} != {expected!r}")

    if covariance.get("checksum_verified") is not True:
        errors.append("covariance checksum_verified must be true")
    if covariance.get("status") != "READY_FULL_COVARIANCE":
        errors.append("covariance status must be READY_FULL_COVARIANCE")
    if receipt.get("route_state") != "FULL_COVARIANCE_LIKELIHOOD_READY":
        errors.append("route_state must be FULL_COVARIANCE_LIKELIHOOD_READY")
    if receipt.get("full_covariance_likelihood_ready") is not True:
        errors.append("full_covariance_likelihood_ready must be true")
    if receipt.get("f_ok") is not True:
        errors.append("receipt f_ok must be true")
    if receipt.get("claim_allowed") is not False:
        errors.append("receipt claim_allowed must remain false")
    if receipt.get("scientific_confirmation") is not False:
        errors.append("scientific_confirmation must remain false")
    if not receipt.get("github_run_id") or not receipt.get("github_artifact_id"):
        errors.append("GitHub run/artifact custody identifiers are required")
    artifact_digest = str(receipt.get("github_artifact_sha256", ""))
    if len(artifact_digest) != 64:
        errors.append("GitHub artifact SHA-256 must be 64 hex characters")
    return errors


def build_readiness(root: Path = ROOT, pantheon_receipt_path: Path | None = None) -> dict[str, Any]:
    v2 = _load_module("rll_sv_v2", root / V2_PATH.relative_to(ROOT))
    desi_binder = _load_module("rll_desi_order", root / DESI_BINDER_PATH.relative_to(ROOT))
    base = v2.build_readiness(root)

    receipt_path = pantheon_receipt_path or (root / PANTHEON_RECEIPT_PATH.relative_to(ROOT))
    if receipt_path.is_file():
        pantheon_receipt = load_json(receipt_path)
        pantheon_errors = validate_pantheon_receipt(pantheon_receipt)
    else:
        pantheon_receipt = {}
        pantheon_errors = ["TOKEN_VAZIO_PANTHEON_MATERIALIZATION_RECEIPT"]

    try:
        desi_receipt = desi_binder.build_receipt(root)
        desi_errors: list[str] = []
        if desi_receipt.get("state") != "VERIFIED_REPO_ORDER_BINDING":
            desi_errors.append("DESI order binding is not VERIFIED_REPO_ORDER_BINDING")
        if desi_receipt.get("claim_allowed") is not False:
            desi_errors.append("DESI order receipt claim_allowed must remain false")
    except Exception as exc:  # fail closed, preserve exact reason
        desi_receipt = {}
        desi_errors = [f"DESI_BINDING_ERROR: {exc}"]

    g2_ready = not pantheon_errors and not desi_errors
    gate_states = dict(base.get("gate_states", {}))
    if g2_ready:
        gate_states.update(
            {
                "G2": READY_G2_RECEIPT,
                "G3": "READY_TO_EXECUTE_COMPATIBILITY_NOT_PASSED",
                "G4": "BLOCKED_BY_G3_RESULT",
                "G5": "BLOCKED_BY_G3_G4",
                "G6": "BLOCKED_BY_G5",
                "G7": "BLOCKED_BY_G6",
                "G10": "BLOCKED_BY_G6",
                "G11": "BLOCKED_BY_G7_G10",
            }
        )
    else:
        gate_states.update(
            {
                "G2": "BLOCKED_BY_G2_RECEIPT_VALIDATION",
                "G3": "BLOCKED_BY_G2",
                "G4": "BLOCKED_BY_G2_G3",
                "G5": "BLOCKED_BY_G2",
                "G6": "BLOCKED_BY_G5",
            }
        )

    inherited_tokens = [
        token for token in base.get("token_vazio", [])
        if token != "TOKEN_VAZIO_FULL_COVARIANCE"
    ]
    if not g2_ready:
        inherited_tokens.append("TOKEN_VAZIO_OR_BLOCKED_G2_RECEIPT")

    return {
        "schema": "rll.scientific_validation_readiness.v3",
        "repo_ref": base.get("repo_ref"),
        "claim_allowed": False,
        "publication_effect": "NONE",
        "scientific_confirmation": False,
        "g2_ready": g2_ready,
        "gate_states": gate_states,
        "pantheon_materialization": {
            "receipt_path": str(receipt_path.relative_to(root)) if receipt_path.is_relative_to(root) else str(receipt_path),
            "valid": not pantheon_errors,
            "errors": pantheon_errors,
            "route_state": pantheon_receipt.get("route_state"),
            "github_run_id": pantheon_receipt.get("github_run_id"),
            "github_artifact_id": pantheon_receipt.get("github_artifact_id"),
            "artifact_sha256": pantheon_receipt.get("github_artifact_sha256"),
            "covariance_sha256": pantheon_receipt.get("files", {}).get("Pantheon+SH0ES_STAT+SYS.cov", {}).get("sha256"),
        },
        "desi_order_binding": {
            "valid": not desi_errors,
            "errors": desi_errors,
            "state": desi_receipt.get("state"),
            "points_sha256": desi_receipt.get("points_sha256"),
            "covariance_sha256": desi_receipt.get("covariance_sha256"),
            "ordered_vector_identity_sha256": desi_receipt.get("ordered_vector_identity_sha256"),
            "provenance_boundary": desi_receipt.get("provenance_boundary"),
        },
        "token_vazio": sorted(set(inherited_tokens)),
        "boundaries": [
            "external runtime materialization may satisfy G2 only through a persisted exact hash-bound receipt",
            "receipt validity != scientific model validation",
            "G2 ready != G3 compatibility pass",
            "G3 compatibility pass != G4 fair-baseline pass",
            "claim_allowed=false",
        ],
        "F_ok": [
            "Pantheon STAT+SYS full covariance is materialized and verified by persisted CI receipt" if not pantheon_errors else "TOKEN_VAZIO_PANTHEON_RECEIPT",
            "DESI 13x13 covariance is deterministically bound to the repo-local primary vector" if not desi_errors else "TOKEN_VAZIO_DESI_BINDING",
        ],
        "F_gap": [] if g2_ready else pantheon_errors + desi_errors,
        "F_next": "execute G3 compatibility decision; then G4 fairness; only then build G5 canonical likelihood manifest" if g2_ready else "repair G2 receipt validation without bypass",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Receipt-aware scientific validation readiness V3")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--require-g2", action="store_true")
    parser.add_argument("--pantheon-receipt", type=Path, default=None)
    args = parser.parse_args()
    try:
        report = build_readiness(ROOT, args.pantheon_receipt)
    except (OSError, json.JSONDecodeError, ReceiptValidationError) as exc:
        print(f"[rll] BLOCKED_V3: {exc}", file=sys.stderr)
        return 2
    if args.json:
        print(json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False))
    else:
        print(f"G2={report['gate_states']['G2']}")
        print(f"G3={report['gate_states']['G3']}")
        print("claim_allowed=false")
    if args.require_g2 and not report["g2_ready"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
