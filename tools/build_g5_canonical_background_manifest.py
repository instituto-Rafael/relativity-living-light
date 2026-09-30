#!/usr/bin/env python3
"""Build the canonical G5 background-likelihood manifest from a G4 receipt.

G5 does not refit data. It freezes the exact likelihood implementation and
inputs already exercised by G4 so downstream inference cannot silently switch
samples, covariances, nuisance handling, priors/bounds or model definitions.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import sys
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
G4_EXECUTOR = ROOT / "tools/run_g4_background_tournament.py"
G4_CONTRACT = ROOT / "data/contracts/rll_g4_background_tournament.v1.json"
G5_CONTRACT = ROOT / "data/contracts/rll_g5_canonical_background_likelihood.v1.json"
MANDATORY_MODELS = ["LCDM", "wCDM", "CPL", "GEDE", "IDE_QrhoLambda", "RLL"]
HEX64 = re.compile(r"^[0-9a-f]{64}$")


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError(f"{path}: expected JSON object")
    return value


def validate_g4_receipt(receipt: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if receipt.get("schema") != "rll.g4_background_tournament_receipt.v1":
        errors.append("unexpected G4 receipt schema")
    if receipt.get("state") != "PASS_LIMITED_G4_BACKGROUND_TOURNAMENT":
        errors.append("G4 receipt is not PASS_LIMITED_G4_BACKGROUND_TOURNAMENT")
    if receipt.get("claim_allowed") is not False:
        errors.append("G4 claim_allowed must be false")
    if receipt.get("scientific_confirmation") is not False:
        errors.append("G4 scientific_confirmation must be false")
    if receipt.get("negative_results_preserved") is not True:
        errors.append("G4 negative results must be preserved")
    if receipt.get("null_limits", {}).get("passed") is not True:
        errors.append("G4 null-limit receipt did not pass")

    rows = receipt.get("rows", [])
    names = [row.get("model") for row in rows if isinstance(row, dict)]
    if names != MANDATORY_MODELS:
        errors.append(f"mandatory model order mismatch: {names!r}")

    hashes = receipt.get("input_sha256", {})
    if not isinstance(hashes, dict) or not hashes:
        errors.append("G4 input_sha256 is missing")
    else:
        for path, digest in hashes.items():
            if not isinstance(path, str) or not isinstance(digest, str) or HEX64.fullmatch(digest) is None:
                errors.append(f"invalid input hash: {path}={digest}")
    policy = receipt.get("datasets", {}).get("growth_CMB_policy")
    if policy != "DEFER_TO_G8_G9_NO_PROXY_PROMOTION":
        errors.append("growth/CMB deferral boundary changed")
    return errors


def build_manifest(receipt_path: Path, root: Path = ROOT) -> dict[str, Any]:
    receipt_bytes = receipt_path.read_bytes()
    receipt = json.loads(receipt_bytes.decode("utf-8"))
    if not isinstance(receipt, dict):
        raise ValueError("G4 receipt must be an object")
    errors = validate_g4_receipt(receipt)
    if errors:
        return {
            "schema": "rll.g5_canonical_background_likelihood_manifest.v1",
            "state": "BLOCKED_BY_G4_RECEIPT",
            "claim_allowed": False,
            "scientific_confirmation": False,
            "errors": errors,
            "F_ok": [],
            "F_gap": errors,
            "F_next": "repair or regenerate G4 without bypass",
        }

    g4_contract = load_json(root / G4_CONTRACT.relative_to(ROOT))
    parameter_registry = {
        "common": g4_contract["common_parameters"],
        "model_specific": {
            model: g4_contract["models"][model].get("specific_parameters", {})
            for model in MANDATORY_MODELS
        },
        "null_limits": {
            model: g4_contract["models"][model].get("null_limit")
            for model in ("GEDE", "IDE_QrhoLambda", "RLL")
        },
    }
    nuisance_registry = {
        "Pantheon_M_B": {
            "treatment": "analytically_profiled",
            "counted_in_k": True,
            "shared_policy_all_models": True,
        }
    }
    covariance_registry = {
        "PantheonPlus": "full_STAT+SYS",
        "DESI_DR2": "full_13x13",
        "cosmic_chronometers": "published_diagonal_sigma_per_selected_CC_row",
        "cross_survey": "assumed_block_independent_in_declared_background_likelihood; G3 residual remains visible",
    }
    selection_registry = {
        "PantheonPlus": "(zHD > 0.01) OR IS_CALIBRATOR==1",
        "DESI_DR2": "all 13 canonical primary observables in verified repo-local order",
        "cosmic_chronometers": "source starts CC_ and source label does not contain BAO",
        "growth_CMB": "excluded until G8/G9",
    }
    best_fit_summary = {
        row["model"]: {
            key: value
            for key, value in row.items()
            if key in {
                "chi2", "AIC", "AICc", "BIC", "N", "k", "dof", "H0", "Omega_m", "omega_b_h2",
                "w", "w0", "wa", "Delta", "beta", "Omega_s0", "z_t", "w_t", "M_B_profiled",
                "chi2_Pantheon", "chi2_CC", "chi2_DESI", "best_seed", "boundary_hits"
            }
        }
        for row in receipt["rows"]
    }
    event_id = f"RLL-G5-CANONICAL-BACKGROUND-{receipt.get('created_utc', 'UNKNOWN').replace(':','').replace('-','')}"
    return {
        "schema": "rll.g5_canonical_background_likelihood_manifest.v1",
        "state": "READY_G5_CANONICAL_BACKGROUND_LIKELIHOOD",
        "event_id": event_id,
        "scope": "background_only_DESI_DR2_PantheonPlus_pure_cosmic_chronometers",
        "g4_receipt_path": str(receipt_path.relative_to(root)) if receipt_path.is_relative_to(root) else str(receipt_path),
        "g4_receipt_sha256": sha256_bytes(receipt_bytes),
        "executor_path": str(G4_EXECUTOR.relative_to(ROOT)),
        "executor_sha256": sha256_file(root / G4_EXECUTOR.relative_to(ROOT)),
        "g4_contract_path": str(G4_CONTRACT.relative_to(ROOT)),
        "g4_contract_sha256": sha256_file(root / G4_CONTRACT.relative_to(ROOT)),
        "g5_contract_path": str(G5_CONTRACT.relative_to(ROOT)),
        "g5_contract_sha256": sha256_file(root / G5_CONTRACT.relative_to(ROOT)),
        "input_sha256": receipt["input_sha256"],
        "models": MANDATORY_MODELS,
        "parameter_registry": parameter_registry,
        "nuisance_registry": nuisance_registry,
        "covariance_registry": covariance_registry,
        "selection_registry": selection_registry,
        "best_fit_summary": best_fit_summary,
        "deltas_vs_LCDM": receipt.get("deltas_vs_LCDM", {}),
        "negative_results_preserved": True,
        "claim_allowed": False,
        "scientific_confirmation": False,
        "publication_effect": "NONE",
        "boundaries": [
            "READY_G5_CANONICAL_BACKGROUND_LIKELIHOOD != Bayesian evidence",
            "background likelihood != perturbation closure",
            "same-code manifest freeze != independent replication",
            "negative results remain append-only",
        ],
        "F_ok": [
            "G2/G3/G4 prerequisites encoded in the passing G4 receipt",
            "six-model background likelihood frozen by hashes",
            "data/covariance/selection/nuisance/parameter policies are explicit",
        ],
        "F_gap": [
            "G6 multichain MCMC and nested-sampling evidence not yet executed on this exact manifest",
            "G8/G9 perturbation-growth-CMB closure remains open",
            "G10 materially independent replication remains open",
        ],
        "F_next": "execute G6 inference keyed to g4_receipt_sha256 and executor_sha256; reject any route with different input/selection/prior hashes",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Build fail-closed G5 canonical background manifest")
    parser.add_argument("--g4-receipt", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--require-ready", action="store_true")
    args = parser.parse_args()
    try:
        manifest = build_manifest(args.g4_receipt, ROOT)
    except Exception as exc:
        print(f"[rll] BLOCKED_G5_EXCEPTION: {exc}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(manifest, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(manifest["state"])
    print("claim_allowed=false")
    if args.require_ready and manifest["state"] != "READY_G5_CANONICAL_BACKGROUND_LIKELIHOOD":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
