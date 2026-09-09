#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
from pathlib import Path
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_RECORD = ROOT / "data/governance/RLL_ATLAS_G234_EVIDENCE_RECONCILIATION_20260828_V1.json"

EXPECTED_GATES = ("G2_FULL_COVARIANCE", "G3_LIKELIHOOD_PARITY", "G4_BASELINE_RECOVERY")
EXPECTED_RUNTIME = {
    "run_id": 33150360583,
    "artifact_id": 9677562132,
    "head_sha": "a99e5caff4be0dea2a368592c80e36445e45ef89",
    "artifact_digest": "sha256:8bd1ca4aea1e53da2a8cd6da38965c12d66fb11457bb52dd474ed841327d2a97",
}
REQUIRED_BLOCKERS = {
    "TOKEN_VAZIO_EXPLICIT_CROSS_SURVEY_COVARIANCE_MATRIX",
    "TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION",
    "TOKEN_VAZIO_DES_Y6_3X2PT_LIKELIHOOD",
    "TOKEN_VAZIO_ACT_DR6_LCDM_POSTERIOR_CHAIN_REPRODUCTION",
    "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS",
    "TOKEN_VAZIO_RLL_CLASS_CAMB_IMPLEMENTATION",
    "TOKEN_VAZIO_INDEPENDENT_REPLICATION",
    "MCMC_CONVERGENCE",
    "NESTED_SEED_STABILITY",
}
REQUIRED_INVARIANTS = {
    "TOKEN_VAZIO_NE_PASS",
    "PARTIAL_NE_VERIFIED",
    "NEGATIVE_RESULT_IS_EVIDENCE_NOT_REGRESSION",
    "BACKGROUND_FAIRNESS_NE_FULL_PROBE_PARITY",
    "INTERNAL_CI_NE_INDEPENDENT_REPLICATION",
    "CLAIM_ALLOWED_REMAINS_FALSE",
}


def load(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("record must be a JSON object")
    return value


def is_hex(value: Any, n: int) -> bool:
    return isinstance(value, str) and len(value) == n and all(c in "0123456789abcdef" for c in value.lower())


def validate(record: dict[str, Any]) -> list[str]:
    errors: list[str] = []
    if record.get("schema") != "rll.atlas_g234_evidence_reconciliation.v1":
        errors.append("schema mismatch")
    if record.get("append_only") is not True:
        errors.append("append_only must be true")
    if record.get("claim_allowed") is not False or record.get("publication_ready") is not False:
        errors.append("claim_allowed/publication_ready must remain false")

    predecessor = record.get("predecessor", {})
    if predecessor.get("record_id") != "RLL_ATLAS_CONTINUOUS_EVOLUTION_OMEGA6_20260827_V2":
        errors.append("predecessor record mismatch")
    if predecessor.get("git_blob_sha1") != "6affe719819ee52b0d1ced35b364c99e57b73617":
        errors.append("predecessor blob mismatch")

    authority = record.get("authority", {})
    expected_authority = (
        "instituto-Rafael/relativity-living-light",
        1046495816,
        "rll/lab",
        "e6e12097c1fb397a0f923daa84f3760739d4d9d3",
        "7158cb1a6a9e398b06f380cea1282661da39bd27",
    )
    got_authority = (
        authority.get("repository"), authority.get("repository_id"), authority.get("target_branch"),
        authority.get("base_head_sha"), authority.get("base_tree_sha"),
    )
    if got_authority != expected_authority or authority.get("evidence_merged_into_base") is not True:
        errors.append("authority/base lineage mismatch")

    runtime = record.get("runtime_evidence", {})
    if runtime.get("conclusion") != "success":
        errors.append("runtime workflow must be successful")
    for key, expected in EXPECTED_RUNTIME.items():
        if runtime.get(key) != expected:
            errors.append(f"runtime {key} mismatch")
    files = runtime.get("files", [])
    if len(files) != 4 or any(not isinstance(x, dict) or not x.get("path") or not is_hex(x.get("sha256"), 64) for x in files):
        errors.append("runtime evidence files must contain four SHA-256-bound receipts")

    persistent = record.get("persistent_evidence", [])
    if len(persistent) < 4:
        errors.append("persistent evidence set incomplete")
    for item in persistent:
        if not isinstance(item, dict) or not item.get("path") or not is_hex(item.get("git_blob_sha1"), 40):
            errors.append("persistent evidence path/blob invalid")

    frozen = record.get("frozen_background_inputs", {})
    if len(frozen) < 6 or any(not is_hex(v, 64) for v in frozen.values()):
        errors.append("frozen background input SHA-256 set incomplete")

    projection = record.get("effective_projection", [])
    if tuple(g.get("id") for g in projection if isinstance(g, dict)) != EXPECTED_GATES:
        errors.append("effective projection must contain G2/G3/G4 in order")
    for gate in projection:
        gid = gate.get("id")
        if gate.get("from_status") != "TOKEN_VAZIO" or gate.get("status") != "PARTIAL" or gate.get("maturity") != 1:
            errors.append(f"{gid}: only TOKEN_VAZIO -> PARTIAL/maturity=1 is authorized")
        if not gate.get("positive_evidence") or not gate.get("blockers"):
            errors.append(f"{gid}: positive evidence and blockers are required")

    negative = record.get("negative_evidence", {})
    g4 = negative.get("g4_background", {})
    if g4.get("state") != "PASS_LIMITED_G4_BACKGROUND_TOURNAMENT" or g4.get("rll_Omega_s0") != 0.0:
        errors.append("G4 negative/null-boundary evidence must be preserved")
    if not isinstance(g4.get("rll_delta_BIC_vs_LCDM"), (int, float)) or g4["rll_delta_BIC_vs_LCDM"] <= 0:
        errors.append("G4 unfavorable RLL delta_BIC must remain positive")

    g6 = negative.get("g6", {})
    if g6.get("state") != "BLOCKED_G6_CONVERGENCE_OR_EVIDENCE":
        errors.append("G6 blocked state must be preserved")
    if g6.get("convergence_pass_all") is not False:
        errors.append("G6 convergence_pass_all must remain false")
    rhat, threshold = g6.get("rll_max_Rhat"), g6.get("threshold_Rhat")
    if not isinstance(rhat, (int, float)) or not isinstance(threshold, (int, float)) or not rhat > threshold:
        errors.append("G6 RLL Rhat failure must be preserved")
    if set(g6.get("F_gap", [])) != {"MCMC_CONVERGENCE", "NESTED_SEED_STABILITY"}:
        errors.append("G6 convergence/seed-stability gaps must be preserved")

    maturity = record.get("effective_maturity", {})
    if (maturity.get("predecessor_total"), maturity.get("effective_total"), maturity.get("denominator")) != (4, 7, 21):
        errors.append("maturity accounting must remain 4 -> 7 / 21")
    if maturity.get("fraction") != 0.333333:
        errors.append("effective maturity fraction mismatch")

    blockers = set(record.get("mandatory_open_blockers", []))
    if not REQUIRED_BLOCKERS.issubset(blockers):
        errors.append("mandatory open blocker set incomplete")
    invariants = set(record.get("invariants", []))
    if not REQUIRED_INVARIANTS.issubset(invariants):
        errors.append("anti-regression invariant set incomplete")
    return errors


def build_receipt(record: dict[str, Any], errors: list[str]) -> dict[str, Any]:
    return {
        "schema": "rll.atlas_g234_evidence_reconciliation.receipt.v1",
        "record_id": record.get("record_id"),
        "valid": not errors,
        "claim_allowed": False,
        "publication_ready": False,
        "effective_gate_states": {g.get("id"): g.get("status") for g in record.get("effective_projection", []) if isinstance(g, dict)},
        "effective_maturity_fraction": record.get("effective_maturity", {}).get("fraction"),
        "negative_g6_state": record.get("negative_evidence", {}).get("g6", {}).get("state"),
        "open_blockers": record.get("mandatory_open_blockers", []),
        "errors": errors,
        "boundary": "Evidence reconciliation only. PARTIAL is not VERIFIED; CI success is not physical confirmation or independent replication."
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--record", type=Path, default=DEFAULT_RECORD)
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    record = load(args.record)
    errors = validate(record)
    receipt = build_receipt(record, errors)
    text = json.dumps(receipt, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if not errors else 2


if __name__ == "__main__":
    raise SystemExit(main())
