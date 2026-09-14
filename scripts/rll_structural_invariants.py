#!/usr/bin/env python3
"""Gera artefatos determinísticos da matemática estrutural RLL.

Este é o Estágio 0: não executa ajuste observacional nem permite alegação de
superioridade. A saída registra fórmulas, grafo estrutural, parâmetros,
diagnósticos geométricos, resíduos dos invariantes e metadados de integridade.
"""
from __future__ import annotations

import argparse
import csv
from dataclasses import asdict
from datetime import datetime, timezone
import hashlib
import json
import os
from pathlib import Path
import sys
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rll_core.structural_invariants import (  # noqa: E402
    RLLParameters,
    deceleration_q,
    dh_over_rd,
    dm_over_rd,
    dv_over_rd,
    e2,
    e2_prime,
    e2_second,
    effective_w_geometry,
    expansion_e,
    jerk_j,
    kretschmann_bar,
    linspace,
    log_hubble_curvature,
    log_hubble_slope,
    ricci_bar,
    scale_factor,
    scan_invariants,
    sector_g,
    transition_f,
)

SCHEMA_ID = "rll.structural_math_artifact.v1"
CLAIM_BOUNDARY = (
    "Structural and algebraic validation only; no observational superiority "
    "claim and no physical confirmation without real-data inference."
)


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", default="artifacts/rll-structural-math")
    parser.add_argument("--z-max", type=float, default=3.0)
    parser.add_argument("--points", type=int, default=301)
    parser.add_argument("--h0", type=float, default=67.4)
    parser.add_argument("--om", type=float, default=0.315)
    parser.add_argument("--orad", type=float, default=9.2e-5)
    parser.add_argument("--os0", type=float, default=0.02)
    parser.add_argument("--zt", type=float, default=1.0)
    parser.add_argument("--wt", type=float, default=0.3)
    parser.add_argument("--ob0", type=float, default=0.0)
    parser.add_argument("--op0", type=float, default=0.0)
    parser.add_argument("--rd-mpc", type=float, default=147.09)
    parser.add_argument("--simpson-n", type=int, default=256)
    parser.add_argument(
        "--cross-check-existing",
        action=argparse.BooleanOptionalAction,
        default=True,
        help="Compare E(z) with validacao_real.compute_validation when importable.",
    )
    return parser.parse_args()


def formula_registry() -> dict[str, Any]:
    formulas = [
        ("RLL-F001", "a(z)", r"a=(1+z)^{-1}", [], "dimensionless"),
        ("RLL-F002", "f(z)", r"f=[1+\exp((z-z_t)/w_t)]^{-1}", ["RLL-F001"], "dimensionless"),
        ("RLL-F003", "g(z)", r"g=f+(1-f)(1+z)^3", ["RLL-F002"], "dimensionless"),
        (
            "RLL-F004",
            "Omega_Lambda",
            r"\Omega_\Lambda=1-\Omega_m-(\Omega_r+\Omega_{B0}+\Omega_{P0})-\Omega_{s0}",
            ["RLL-F003"],
            "dimensionless",
        ),
        (
            "RLL-F005",
            "E2(z)",
            r"E^2=\Omega_m(1+z)^3+(\Omega_r+\Omega_{B0}+\Omega_{P0})(1+z)^4+\Omega_\Lambda+\Omega_{s0}g",
            ["RLL-F003", "RLL-F004"],
            "dimensionless",
        ),
        ("RLL-F006", "f'(z)", r"f'=-f(1-f)/w_t", ["RLL-F002"], "redshift^-1"),
        ("RLL-F007", "f''(z)", r"f''=f(1-f)(1-2f)/w_t^2", ["RLL-F006"], "redshift^-2"),
        (
            "RLL-F008",
            "g'(z)",
            r"g'=f'[1-(1+z)^3]+3(1-f)(1+z)^2",
            ["RLL-F003", "RLL-F006"],
            "redshift^-1",
        ),
        (
            "RLL-F009",
            "g''(z)",
            r"g''=f''[1-(1+z)^3]-6f'(1+z)^2+6(1-f)(1+z)",
            ["RLL-F007", "RLL-F008"],
            "redshift^-2",
        ),
        ("RLL-F010", "S'(z)", r"S'=dE^2/dz", ["RLL-F005", "RLL-F008"], "redshift^-1"),
        ("RLL-F011", "S''(z)", r"S''=d^2E^2/dz^2", ["RLL-F005", "RLL-F009"], "redshift^-2"),
        (
            "RLL-F012",
            "D1(z)",
            r"D_1=d\ln E/d\ln(1+z)=(1+z)S'/(2S)",
            ["RLL-F010"],
            "dimensionless",
        ),
        (
            "RLL-F013",
            "D2(z)",
            r"D_2=dD_1/d\ln(1+z)",
            ["RLL-F010", "RLL-F011", "RLL-F012"],
            "dimensionless",
        ),
        ("RLL-F014", "q(z)", r"q=-1+D_1", ["RLL-F012"], "dimensionless"),
        ("RLL-F015", "w_geom(z)", r"w_{\mathrm{geom}}=-1+(2/3)D_1", ["RLL-F012"], "dimensionless"),
        ("RLL-F016", "j(z)", r"j=q(2q+1)+D_2", ["RLL-F013", "RLL-F014"], "dimensionless"),
        (
            "RLL-F017",
            "Ricci_bar(z)",
            r"\bar R=Rc^2/H_0^2=6E^2(2-D_1)",
            ["RLL-F005", "RLL-F012"],
            "dimensionless",
        ),
        (
            "RLL-F018",
            "Kretschmann_bar(z)",
            r"\bar K=Kc^4/H_0^4=12E^4(1+q^2)",
            ["RLL-F005", "RLL-F014"],
            "dimensionless",
        ),
        (
            "RLL-F019",
            "null_limit",
            r"\Omega_{s0}=\Omega_{B0}=\Omega_{P0}=0\Rightarrow E^2=E^2_{\Lambda\mathrm{CDM}}",
            ["RLL-F005"],
            "identity",
        ),
        ("RLL-F020", "chi(z)", r"\chi=(c/H_0)\int_0^z dz'/E(z')", ["RLL-F005"], "Mpc"),
        ("RLL-F021", "DH/rd", r"D_H/r_d=c/[H_0E(z)r_d]", ["RLL-F005"], "dimensionless"),
        ("RLL-F022", "DM/rd", r"D_M/r_d=\chi/r_d", ["RLL-F020"], "dimensionless"),
        ("RLL-F023", "DV/rd", r"D_V/r_d=[zD_M^2D_H]^{1/3}/r_d", ["RLL-F021", "RLL-F022"], "dimensionless"),
    ]
    return {
        "schema": "rll.formula_registry.v1",
        "claim_boundary": CLAIM_BOUNDARY,
        "assumptions": [
            "spatially flat FLRW background",
            "wt > 0",
            "E2(z) > 0 on the evaluated domain",
            "R_bar and K_bar are normalized curvature scalars under flat-FLRW assumptions",
            "w_geom is a background-effective diagnostic, not a microphysical equation of state",
        ],
        "formulas": [
            {
                "id": fid,
                "symbol": symbol,
                "expression_latex": expression,
                "depends_on": deps,
                "units": units,
                "status": "DERIVED_OR_CANONICAL",
            }
            for fid, symbol, expression, deps, units in formulas
        ],
    }


def structural_map() -> dict[str, Any]:
    nodes = [
        ("parameters", "H0, density parameters, zt, wt, rd"),
        ("transition", "f(z), f', f''"),
        ("sector", "g(z), g', g''"),
        ("background", "E2, E2', E2''"),
        ("geometry", "D1, D2, q, w_geom, j, R_bar, K_bar"),
        ("observables", "DH/rd, DM/rd, DV/rd"),
        ("invariants", "normalization, null limit, positivity, derivative residuals"),
        ("likelihood", "chi2/covariance stage; not executed here"),
        ("model_selection", "AIC/AICc/BIC/Bayes stage; not executed here"),
        ("artifact", "CSV, JSON, Markdown, checksums, GitHub artifact"),
    ]
    edges = [
        ("parameters", "transition", "parameterizes"),
        ("transition", "sector", "constructs"),
        ("parameters", "background", "normalizes"),
        ("sector", "background", "adds superposition sector"),
        ("background", "geometry", "differentiates"),
        ("background", "observables", "integrates"),
        ("transition", "invariants", "bounds/monotonicity"),
        ("background", "invariants", "normalization/null/positivity"),
        ("geometry", "invariants", "identity checks"),
        ("observables", "likelihood", "future real-data input"),
        ("likelihood", "model_selection", "future inference"),
        ("invariants", "artifact", "records"),
        ("geometry", "artifact", "records"),
        ("observables", "artifact", "records"),
    ]
    return {
        "schema": "rll.structural_map.v1",
        "claim_boundary": CLAIM_BOUNDARY,
        "nodes": [{"id": node, "content": content} for node, content in nodes],
        "edges": [{"from": a, "to": b, "relation": relation} for a, b, relation in edges],
        "pipeline_order": [node for node, _ in nodes],
    }


def existing_engine_cross_check(p: RLLParameters, zs: list[float]) -> dict[str, Any]:
    try:
        from validacao_real.compute_validation import Cosmo, E as existing_e
    except Exception as exc:  # evidência registra o estado exato da importação
        return {
            "status": "TOKEN_VAZIO",
            "reason": f"existing engine import unavailable: {type(exc).__name__}: {exc}",
        }

    existing = Cosmo(
        name="RLL",
        H0=p.H0,
        Om=p.Om,
        Or=p.Or,
        Os=p.Os0,
        zt=p.zt,
        wt=p.wt,
        k_params=5,
    )
    residuals = [abs(expansion_e(z, p) - existing_e(existing, z)) for z in zs]
    max_residual = max(residuals)
    return {
        "status": "PASS" if max_residual <= 1e-12 and p.OB0 == 0.0 and p.OP0 == 0.0 else "LIMITED",
        "max_abs_E_residual": max_residual,
        "note": "Existing engine has no OB0/OP0 arguments; exact PASS requires both zero.",
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")


def write_scan_csv(path: Path, p: RLLParameters, zs: list[float], simpson_n: int) -> None:
    fieldnames = [
        "z", "a", "f", "g", "E2", "E", "E2_prime", "E2_second",
        "D1", "D2", "q", "w_geom", "jerk", "Ricci_bar",
        "Kretschmann_bar", "DH_over_rd", "DM_over_rd", "DV_over_rd",
    ]
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=fieldnames)
        writer.writeheader()
        for z in zs:
            writer.writerow({
                "z": f"{z:.12g}",
                "a": f"{scale_factor(z):.12g}",
                "f": f"{transition_f(z, p):.12g}",
                "g": f"{sector_g(z, p):.12g}",
                "E2": f"{e2(z, p):.12g}",
                "E": f"{expansion_e(z, p):.12g}",
                "E2_prime": f"{e2_prime(z, p):.12g}",
                "E2_second": f"{e2_second(z, p):.12g}",
                "D1": f"{log_hubble_slope(z, p):.12g}",
                "D2": f"{log_hubble_curvature(z, p):.12g}",
                "q": f"{deceleration_q(z, p):.12g}",
                "w_geom": f"{effective_w_geometry(z, p):.12g}",
                "jerk": f"{jerk_j(z, p):.12g}",
                "Ricci_bar": f"{ricci_bar(z, p):.12g}",
                "Kretschmann_bar": f"{kretschmann_bar(z, p):.12g}",
                "DH_over_rd": f"{dh_over_rd(z, p):.12g}",
                "DM_over_rd": f"{dm_over_rd(z, p, n=simpson_n):.12g}",
                "DV_over_rd": f"{dv_over_rd(z, p, n=simpson_n):.12g}",
            })


def sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def build_report(summary: dict[str, Any]) -> str:
    inv = summary["invariants"]
    cross = summary["existing_engine_cross_check"]
    return "\n".join([
        "# RLL Structural Mathematics — Stage 0",
        "",
        f"- schema: `{summary['schema']}`",
        f"- generated_utc: `{summary['generated_utc']}`",
        f"- commit: `{summary['commit_sha']}`",
        f"- verdict: **{summary['verdict']}**",
        f"- claim boundary: {summary['claim_boundary']}",
        "",
        "## Pipeline",
        "",
        "`parameters → transition → sector → background → geometry → observables → invariants → artifact`",
        "",
        "Likelihood and model-selection stages are intentionally not executed here.",
        "",
        "## Invariant gates",
        "",
        f"- normalization residual: `{inv['normalization_residual']:.6e}`",
        f"- null-limit maximum residual: `{inv['null_limit_max_abs_residual']:.6e}`",
        f"- minimum E² on grid: `{inv['minimum_e2']:.12g}`",
        f"- transition bounds violation: `{inv['transition_bounds_max_violation']:.6e}`",
        f"- maximum f′ (must be <= 0): `{inv['transition_max_derivative']:.6e}`",
        f"- f′ derivative residual: `{inv['f_prime_max_relative_residual']:.6e}`",
        f"- f″ derivative residual: `{inv['f_second_max_relative_residual']:.6e}`",
        f"- E²′ derivative residual: `{inv['e2_prime_max_relative_residual']:.6e}`",
        f"- E²″ derivative residual: `{inv['e2_second_max_relative_residual']:.6e}`",
        "",
        "## Existing-engine relational check",
        "",
        f"- status: `{cross['status']}`",
        *[f"- {key}: `{value}`" for key, value in cross.items() if key != "status"],
        "",
        "## Interpretation boundary",
        "",
        "PASS means that the expressions satisfy the declared structural gates on the selected grid. "
        "It does not mean observational confirmation, model superiority, or physical discovery.",
        "",
    ])


def main() -> int:
    args = parse_args()
    if args.z_max <= 0.0:
        raise SystemExit("--z-max must be positive")
    if args.points < 3:
        raise SystemExit("--points must be >= 3")
    if args.simpson_n < 2:
        raise SystemExit("--simpson-n must be >= 2")

    p = RLLParameters(
        H0=args.h0,
        Om=args.om,
        Or=args.orad,
        Os0=args.os0,
        zt=args.zt,
        wt=args.wt,
        OB0=args.ob0,
        OP0=args.op0,
        rd_mpc=args.rd_mpc,
    )
    p.validate()
    zs = linspace(0.0, args.z_max, args.points)
    out = Path(args.output)
    out.mkdir(parents=True, exist_ok=True)

    registry = formula_registry()
    graph = structural_map()
    invariants = scan_invariants(p, zs)
    cross = (
        existing_engine_cross_check(p, zs[:: max(1, len(zs) // 25)])
        if args.cross_check_existing
        else {"status": "SKIP", "reason": "disabled by command line"}
    )

    write_json(out / "formula_registry.json", registry)
    write_json(out / "structural_map.json", graph)
    write_scan_csv(out / "invariant_scan.csv", p, zs, args.simpson_n)

    accepted_cross_states = {"PASS", "LIMITED", "TOKEN_VAZIO", "SKIP"}
    verdict = "PASS" if invariants["passed"] and cross["status"] in accepted_cross_states else "FAIL"
    summary = {
        "schema": SCHEMA_ID,
        "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
        "commit_sha": os.environ.get("GITHUB_SHA", "LOCAL_OR_UNKNOWN"),
        "claim_boundary": CLAIM_BOUNDARY,
        "domain": {"z_min": 0.0, "z_max": args.z_max, "points": args.points},
        "parameters": asdict(p),
        "invariants": invariants,
        "existing_engine_cross_check": cross,
        "verdict": verdict,
    }
    write_json(out / "summary.json", summary)
    (out / "REPORT.md").write_text(build_report(summary), encoding="utf-8")

    files = sorted(path for path in out.iterdir() if path.is_file())
    manifest = {
        "schema": "rll.structural_math_manifest.v1",
        "generated_utc": summary["generated_utc"],
        "commit_sha": summary["commit_sha"],
        "claim_boundary": CLAIM_BOUNDARY,
        "verdict": verdict,
        "files": [
            {"path": path.name, "bytes": path.stat().st_size, "sha256": sha256(path)}
            for path in files
        ],
        "next_stage": "real-data likelihood and model comparison through canonical workflow",
    }
    write_json(out / "MANIFEST.json", manifest)

    print(json.dumps(summary, indent=2, ensure_ascii=False))
    print(f"artifacts: {out}")
    return 0 if verdict == "PASS" else 2


if __name__ == "__main__":
    raise SystemExit(main())
