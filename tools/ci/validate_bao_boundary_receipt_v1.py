#!/usr/bin/env python3
"""Fail-closed audit of the BAO 3-model bounded-fit JSON, not a physics claim.

Consumes the *real*, source-ordered, 13-observable G4-based CLI artifact.
Audits exact tracked Git blob identity as well as diagnostics, and writes a
separate SHA-256 receipt only after all checks pass. claim_allowed=False.
"""
from __future__ import annotations
import argparse
import hashlib
import json
import math
from pathlib import Path
import re
import subprocess
import sys

from jsonschema import Draft202012Validator

ROOT = Path(__file__).resolve().parents[2]
OBSERVATIONS = {
    "points": "data/real/cosmology/desi_dr2_bao_primary_points.csv",
    "covariance": "data/real/desi_dr2_bao_covariance.csv",
}
MODELS = {"LCDM": 2, "wCDM": 3, "RLL": 5}


def fail(msg: str) -> None:
    raise ValueError("BAO_BOUNDARY_RECEIPT_BLOCKED: " + msg)


def _finite_nonnegative(v, name: str) -> float:
    if isinstance(v, bool) or not isinstance(v, (int, float)):
        fail(f"{name} not a number")
    f = float(v)
    if not math.isfinite(f) or f < 0.0:
        fail(f"{name} nonfinite or negative")
    return f


def verify_document(data: dict, boundary_schema: dict) -> dict:
    if not isinstance(data, dict) or data.get("schema") != "rll.bao_only_g4_three_model.v1":
        fail("invalid or missing root schema")
    if data.get("state") != "BAO_ONLY_EXECUTED" or data.get("claim_allowed") is not False:
        fail("fit state or claim promotion")
    if data.get("G4_joint_fit") != "NOT_RUN" or data.get("n_observables") != 13:
        fail("BAO-only scope changed")
    if data.get("Pantheon_plus") != "TOKEN_VAZIO_FULL_COVARIANCE":
        fail("Pantheon+ status changed without separate scientific route")
    if data.get("covariance") != "full_13x13_source_order_bound":
        fail("full source-ordered BAO covariance required")
    if not isinstance(data.get("data_blobs"), dict):
        fail("data source blob identities absent")
    rows = data.get("models")
    results = data.get("results")
    rendering = data.get("rendered_table")
    if not isinstance(rows, list) or not isinstance(results, dict):
        fail("models/results shape invalid")
    if set(results) != set(MODELS) or len(rows) != len(MODELS):
        fail("model keys missing or duplicated")
    if not isinstance(rendering, dict) or not isinstance(rendering.get("rows"), list):
        fail("rendered report absent")
    if len(rendering["rows"]) != len(MODELS):
        fail("rendered model count mismatch")
    footnote = rendering.get("footnote", "")
    if not isinstance(footnote, str) or "corner" not in footnote or "boundary_diagnostics" not in footnote:
        fail("corner explanatory footnote missing")
    Draft202012Validator.check_schema(boundary_schema)
    seen = set()
    for row, rendered in zip(rows, rendering["rows"]):
        if not isinstance(row, dict) or not isinstance(rendered, dict):
            fail("model or render row invalid")
        model = row.get("model")
        if model not in MODELS or model in seen:
            fail("invalid/duplicate model")
        seen.add(model)
        diag = row.get("boundary_diagnostics")
        if not isinstance(diag, dict):
            fail(f"{model}: boundary_diagnostics absent")
        Draft202012Validator(boundary_schema).validate(diag)
        if row.get("claim_allowed") is not False or diag.get("claim_allowed") is not False:
            fail(f"{model}: invalid claim_allowed")
        if diag.get("corner_solution") is not any(diag["at_boundary"].values()):
            fail(f"{model}: corner_solution flag mismatch")
        if diag.get("strict_corner") is not (diag["active_bound_count"] >= 2):
            fail(f"{model}: strict corner/count contradiction")
        if sum(diag["at_boundary"].values()) != diag["active_bound_count"]:
            fail(f"{model}: active bound count contradiction")
        if diag.get("n_residual_dof_nominal") != 13 - MODELS[model]:
            fail(f"{model}: nominal residual DoF incorrect")
        if diag.get("n_effective_dof") is not None or diag.get("n_effective_dof_status") != "TOKEN_VAZIO_NOT_ESTIMATED":
            fail(f"{model}: effective DoF fabricated")
        if row.get("k") != MODELS[model] or row.get("N") != 13:
            fail(f"{model}: parameter or data count mismatch")
        for number_key in ("chi2", "AIC", "AICc", "BIC", "min_grad_inf"):
            _finite_nonnegative(row.get(number_key), f"{model}:{number_key}")
        for number_key in ("optimizer_optimality", "kkt_violation_inf"):
            _finite_nonnegative(diag.get(number_key), f"{model}:{number_key}")
        if row["min_grad_inf"] != diag["min_grad_inf"]:
            fail(f"{model}: gradient drift")
        expected = f"{row['chi2']:.4f}" + ("*" if diag["corner_solution"] else "")
        if row.get("chi2_display") != expected or rendered.get("chi2") != expected or rendered.get("model") != model:
            fail(f"{model}: missing/misleading corner marker")
        corresponding = results[model]
        if not isinstance(corresponding, dict) or corresponding.get("claim_allowed") is not False:
            fail(f"{model}: results object or claim invalid")
        if corresponding.get("boundary_diagnostics") != diag or corresponding.get("min_grad_inf") != diag["min_grad_inf"]:
            fail(f"{model}: results/fit mismatch")
        if corresponding.get("chi2_display") != expected or corresponding.get("chi2") != row["chi2"]:
            fail(f"{model}: result numeric/display mismatch")
        if diag["corner_solution"] and "corner" not in str(row.get("claim_blocked_reason","")).lower():
            fail(f"{model}: missing corner reason")
    if set(seen) != set(MODELS):
        fail("some models not audited")
    rll = results["RLL"]["boundary_diagnostics"]
    if rll["at_boundary"].get("w_t") is not True or rll["at_boundary"].get("Omega_m") is not False:
        fail("current source-bound RLL limit state changed: require review")
    if rll["active_side"].get("w_t") != "LOWER":
        fail("RLL w_t expected lower-bound solution")
    # This is a *regression flag*, not an astrophysical conclusion.
    if abs(results["RLL"]["chi2"] - 7.803973727991534) > 1e-4:
        fail("RLL source-ordered chi2 moved outside preregistered tolerance")
    return {"status":"PASS_SCOPED_BAO_BOUNDARY_RECEIPT_CONTRACT",
            "models_audited":list(MODELS),
            "rll_chi2":results["RLL"]["chi2"],
            "rll_min_grad_inf":results["RLL"]["min_grad_inf"],
            "rll_active_sides":rll["active_side"],
            "rll_kkt_violation_inf":rll["kkt_violation_inf"],
            "rll_optimizer_optimality":rll["optimizer_optimality"],
            "rll_nominal_dof":rll["n_residual_dof_nominal"],
            "claim_allowed":False}


def verify_source_blobs(data: dict, root: Path = ROOT) -> dict:
    got = {}
    for key, relative_path in OBSERVATIONS.items():
        p = root / relative_path
        if not p.is_file():
            fail(f"source file missing {relative_path}")
        proc = subprocess.run(["git", "hash-object", relative_path], cwd=root,
                              text=True, capture_output=True, check=True)
        actual = proc.stdout.strip()
        expected = data["data_blobs"].get(key)
        if not re.fullmatch(r"[0-9a-f]{40}", str(expected)) or actual != expected:
            fail(f"source Git blob mismatch for {key}")
        got[key] = {"git_blob":actual, "sha256":hashlib.sha256(p.read_bytes()).hexdigest()}
    return got


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument("--input", type=Path, required=True)
    parser.add_argument("--schema", type=Path, default=ROOT/"schemas/rll_bao_boundary_diagnostics_v1.schema.json")
    parser.add_argument("--head-sha", type=str, required=True)
    parser.add_argument("--receipt", type=Path, required=True)
    args=parser.parse_args()
    if not re.fullmatch("[0-9a-f]{40}", args.head_sha):
        parser.error("exact 40-hex PR HEAD SHA required")
    if args.receipt.exists():
        parser.error("append-only: receipt already exists")
    try:
        raw=args.input.read_bytes()
        payload=json.loads(raw, parse_constant=lambda v: fail("nonfinite JSON token: "+v))
        schema=json.loads(args.schema.read_text(encoding="utf-8"))
        result=verify_document(payload,schema)
        result.update({"head_sha":args.head_sha,
                       "source_sha256":hashlib.sha256(raw).hexdigest(),
                       "source_path":str(args.input),
                       "source_git_blobs":verify_source_blobs(payload),
                       "claim_allowed":False,
                       "scientific_significance":"NOT_EVALUATED",
                       "G4_joint_fit":"NOT_RUN"})
        args.receipt.parent.mkdir(parents=True,exist_ok=True)
        with args.receipt.open("x",encoding="utf-8") as handle:
            json.dump(result,handle,indent=2,sort_keys=True,allow_nan=False)
            handle.write("\n")
        print(json.dumps({"status":result["status"],
                          "head_sha":args.head_sha,
                          "sha256":result["source_sha256"],
                          "RLL_chi2":result["rll_chi2"],
                          "RLL_min_grad_inf":result["rll_min_grad_inf"],
                          "RLL_kkt_violation_inf":result["rll_kkt_violation_inf"],
                          "claim_allowed":False},sort_keys=True))
    except (ValueError, OSError, KeyError, TypeError) as exc:
        print("BLOCKED_BAO_RECEIPT: "+str(exc),file=sys.stderr)
        raise SystemExit(2)


if __name__=="__main__":
    main()
