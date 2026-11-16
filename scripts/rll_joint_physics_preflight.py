#!/usr/bin/env python3
"""Read-only, stdlib-only science preflight for the archived Structure-D joint fit.

Does not change models, priors, source JSONs, or historical fit outputs.
Flags are investigation gates, never claims of model falsification or repair.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import math
from pathlib import Path

SCHEMA = "rll.joint_physics_preflight.v1"
FUNCTIONS = ("e2_lcdm", "e2_wcdm", "e2_cpl", "e2_rll", "hz_from_e2", "cmb_shift_prediction", "fsigma8_prediction")


def source_facts(source: str) -> dict:
    tree = ast.parse(source)
    functions = {node.name: node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef))}
    radiation = None
    for node in tree.body:
        if isinstance(node, ast.Assign) and any(isinstance(target, ast.Name) and target.id == "ORAD" for target in node.targets):
            try:
                radiation = float(ast.literal_eval(node.value))
            except (TypeError, ValueError):
                radiation = None
    def calls(name: str) -> set[str]:
        node = functions.get(name)
        return {sub.func.id for sub in ast.walk(node) if isinstance(sub, ast.Call) and isinstance(sub.func, ast.Name)} if node else set()
    cmb_calls = calls("cmb_shift_prediction")
    growth_calls = calls("fsigma8_prediction")
    rll = functions.get("e2_rll")
    rll_source = ast.get_source_segment(source, rll) if rll else ""
    return {
        "radiation_density": radiation,
        "functions_present": {name: name in functions for name in FUNCTIONS},
        "cmb_uses_rd_drag_mpc": "rd_drag_mpc" in cmb_calls,
        "growth_uses_omega_m_z_approximation": "omega_m_z_from_e2" in growth_calls,
        "rll_superposition_contains_cubic": "** 3" in (rll_source or ""),
    }


def audit(payload: dict, source: str) -> dict:
    facts = source_facts(source)
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("expected a nonempty list of fitted model rows")
    flags = []
    if facts["radiation_density"] is None or not all(facts["functions_present"].values()):
        flags.append("TOKEN_VAZIO_SOURCE_FORMULA_GUARD")
    model_diagnostics = []
    for row in rows:
        for name in ("model", "H0", "Om", "OL", "BIC"):
            if name not in row:
                raise ValueError(f"model row missing {name}")
        h0, om, ol = (float(row[name]) for name in ("H0", "Om", "OL"))
        os0 = float(row.get("Os0") or 0.0)
        radiation = facts["radiation_density"]
        e2_0 = om + ol + radiation + os0 if radiation is not None else None
        ratio = math.sqrt(e2_0) if e2_0 is not None and e2_0 > 0 else None
        if ratio is not None and not math.isclose(ratio, 1.0, rel_tol=0.0, abs_tol=1e-6):
            flags.append("H0_NORMALIZATION_REQUIRES_PHYSICAL_CONVENTION_CHECK")
        model_diagnostics.append({
            "model": row["model"], "E2_0_algebraic": e2_0,
            "H_z0_over_fitted_H0_algebraic": ratio,
            "H_z0_algebraic": h0 * ratio if ratio is not None else None,
            "BIC_archived": float(row["BIC"]),
            "Os0_archived": row.get("Os0"),
        })
    best_bic = min(rows, key=lambda r: float(r["BIC"]))["model"]
    historical_label = payload.get("interpretation_label")
    if historical_label == "lcdm_preferred" and not best_bic.startswith("LCDM"):
        flags.append("ARCHIVED_INTERPRETATION_LABEL_CONTRADICTS_BIC_ORDER")
    rll_rows = [row for row in rows if str(row["model"]).startswith("RLL")]
    if any(row.get("Os0") == 0 for row in rll_rows):
        flags.append("RLL_NULL_BOUNDARY_ZT_WT_NONIDENTIFIABLE")
    if facts["cmb_uses_rd_drag_mpc"]:
        flags.append("CMB_RD_VS_RS_RECOMBINATION_REVIEW")
    if facts["growth_uses_omega_m_z_approximation"]:
        flags.append("FSIGMA8_MISSING_EXPLICIT_GROWTH_FACTOR_REVIEW")
    if facts["rll_superposition_contains_cubic"]:
        flags.append("RLL_HIGH_Z_SCALING_VS_HISTORICAL_RADIATION_CLAIM_REVIEW")
    return {
        "schema": SCHEMA,
        "source_sha256": hashlib.sha256(source.encode("utf-8")).hexdigest(),
        "archived_result_created_utc": payload.get("created_utc"),
        "historical_interpretation_label": historical_label,
        "best_BIC_model_in_archived_rows": best_bic,
        "model_diagnostics": model_diagnostics,
        "source_facts": facts,
        "flags": sorted(set(flags)),
        "claim_allowed": False,
        "state": "FALSIFIER_CANDIDATES_NOT_RECOMPUTED_FIT",
        "scope": "archived_results_and_source_formula_preflight_only",
        "next_gate": "independent_numerical_source_falsifier_then_model_aware_recompute",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--source", type=Path, default=Path("data/pipelines/structure_d/joint_real_likelihood.py"))
    parser.add_argument("--result", type=Path, default=Path("results/structure_d/joint_real_likelihood.json"))
    parser.add_argument("--output", type=Path, help="optional new path; no historical artifact is edited")
    args = parser.parse_args()
    source = args.source.read_text(encoding="utf-8")
    content = args.result.read_bytes()
    receipt = audit(json.loads(content), source)
    receipt["archived_result_sha256"] = hashlib.sha256(content).hexdigest()
    rendered = json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True) + "\n"
    if args.output:
        if args.output.resolve() in (args.source.resolve(), args.result.resolve()):
            parser.error("refusing to overwrite scientific source or historical result")
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(rendered, encoding="utf-8")
    else:
        print(rendered, end="")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
