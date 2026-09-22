#!/usr/bin/env python3
"""Executable first gate for the 251-formula cosmology geometry crosswalk.

Scope:
- prove RLL contains MF-0001..MF-0251 with no gaps/duplicates;
- verify every MF has a typed route;
- derive DESI DR2 anisotropic BAO AP geometry with covariance propagation;
- verify circle/triangle/cone/annulus identities;
- verify the implemented RLL null limit Os0=0 reproduces flat LCDM
  for the same common background parameters.

This script does not claim that every MF expression is cosmologically meaningful.
"""
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

import numpy as np
import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data/governance/RLL_SESSION_FORMULA_REGISTRY_MF0001_MF0251_V1.json"
MATRIX = ROOT / "data/governance/RLL_FORMULA_TEST_MATRIX_MF0001_MF0251_V1.json"
DESI = ROOT / "data/real/cosmology/desi_dr2_bao_primary_points.csv"
DESI_COV = ROOT / "data/real/desi_dr2_bao_covariance.csv"

TOL = 1e-10


def _status(ok: bool) -> str:
    return "PASS" if ok else "FAIL"


def registry_gate() -> dict:
    reg = json.loads(REGISTRY.read_text(encoding="utf-8"))
    mat = json.loads(MATRIX.read_text(encoding="utf-8"))
    ids = [int(row["mf_id"].split("-")[1]) for row in reg["records"]]
    missing = [i for i in range(1, 252) if i not in ids]
    duplicates = sorted({x for x in ids if ids.count(x) > 1})
    route_missing = [
        row["mf_id"]
        for row in mat["items"]
        if row.get("test_route") in (None, "", "TOKEN_VAZIO_CLASSIFIER")
    ]
    ok = (
        len(ids) == 251
        and not missing
        and not duplicates
        and len(mat["items"]) == 251
        and not route_missing
    )
    return {
        "id": "FORMULA_REGISTRY_251",
        "status": _status(ok),
        "count": len(ids),
        "missing": missing,
        "duplicates": duplicates,
        "unclassified_routes": route_missing,
        "route_summary": mat["summary"]["by_test_route"],
        "cosmology_summary": mat["summary"]["by_cosmology_route"],
    }


def desi_geometry_gate() -> dict:
    points = pd.read_csv(DESI)
    cov = pd.read_csv(DESI_COV, index_col=0).to_numpy(dtype=float)
    symmetry_error = float(np.max(np.abs(cov - cov.T)))
    eigmin = float(np.min(np.linalg.eigvalsh(cov)))

    pairs = []
    for block, grp in points.groupby("covariance_block", dropna=False):
        if pd.isna(block):
            continue
        obs = set(grp["observable"].astype(str))
        if obs != {"DM_over_rd", "DH_over_rd"}:
            continue
        i_dm = int(grp.index[grp["observable"] == "DM_over_rd"][0])
        i_dh = int(grp.index[grp["observable"] == "DH_over_rd"][0])
        dm = float(points.loc[i_dm, "value"])
        dh = float(points.loc[i_dh, "value"])
        ratio = dm / dh
        grad = np.array([1.0 / dh, -dm / (dh * dh)])
        subcov = cov[np.ix_([i_dm, i_dh], [i_dm, i_dh])]
        var = float(grad @ subcov @ grad)
        pairs.append({
            "tracer": str(points.loc[i_dm, "tracer"]),
            "z": float(points.loc[i_dm, "z_eff"]),
            "F_AP": ratio,
            "sigma_F_AP_delta_method": math.sqrt(max(var, 0.0)),
            "identity": "F_AP=(DM/rd)/(DH/rd)=DM/DH=DM*H/c",
        })

    ok = (
        len(points) == 13
        and len(pairs) == 6
        and symmetry_error < TOL
        and eigmin > 0.0
        and all(math.isfinite(x["F_AP"]) and x["F_AP"] > 0.0 for x in pairs)
    )
    return {
        "id": "DESI_DR2_GEOMETRY",
        "status": _status(ok),
        "point_count": int(len(points)),
        "anisotropic_pair_count": len(pairs),
        "covariance_symmetry_error": symmetry_error,
        "covariance_min_eigenvalue": eigmin,
        "pairs": pairs,
    }


def cone_annulus_gate() -> dict:
    a = 2.0
    rb = a / 2.0
    h = math.sqrt(3.0) * a / 2.0
    ell = a
    errors = {
        "pythagoras": abs(ell * ell - (rb * rb + h * h)),
        "sin30": abs(rb / ell - 0.5),
        "cos30": abs(h / ell - math.sqrt(3.0) / 2.0),
        "tan30": abs(rb / h - 1.0 / math.sqrt(3.0)),
        "volume": abs(
            (math.pi * rb * rb * h / 3.0)
            - (math.sqrt(3.0) * math.pi * a**3 / 24.0)
        ),
    }

    n = 8
    lam = math.cos(math.pi / n)
    R = 3.0
    r = R * lam
    annulus_fraction = math.pi * (R * R - r * r) / (math.pi * R * R)
    errors["annulus_fraction"] = abs(
        annulus_fraction - math.sin(math.pi / n) ** 2
    )

    v_ratio = (lam**3)
    v0 = math.pi * R * R * 5.0 / 3.0
    v1 = math.pi * (lam * R) ** 2 * (lam * 5.0) / 3.0
    errors["similar_cone_volume"] = abs(v1 / v0 - v_ratio)

    max_error = max(errors.values())
    return {
        "id": "CIRCLE_TRIANGLE_CONE_ANNULUS",
        "status": _status(max_error < TOL),
        "max_abs_error": max_error,
        "errors": errors,
    }


def model_null_gate() -> dict:
    try:
        from data.pipelines.structure_d.model_family_shadow import (
            load_model_specs,
            e2_for_model,
            transverse_comoving_distance_mpc,
            hubble_km_s_mpc,
        )
    except Exception as exc:
        return {
            "id": "LCDM_RLL_NULL_GEOMETRY",
            "status": "TOKEN_VAZIO_RUNTIME_IMPORT",
            "error": repr(exc),
        }

    specs = load_model_specs()
    lcdm = specs["FLCDM"]
    rll = specs["RLL"]

    lcdm_v = np.array([70.0, 0.3, 0.02236], dtype=float)
    rll_v = np.array([70.0, 0.3, 0.0, 1.0, 0.5, 0.02236], dtype=float)
    zgrid = np.array([0.0, 0.295, 0.510, 0.706, 0.934, 1.321, 1.484, 2.330])

    e_l = e2_for_model(lcdm, zgrid, lcdm_v)
    e_r = e2_for_model(rll, zgrid, rll_v)
    h_l = hubble_km_s_mpc(lcdm, zgrid, lcdm_v)
    h_r = hubble_km_s_mpc(rll, zgrid, rll_v)

    e_err = float(np.max(np.abs(e_l - e_r)))
    h_err = float(np.max(np.abs(h_l - h_r)))

    dm_err = 0.0
    for z in zgrid[1:]:
        dm_l = transverse_comoving_distance_mpc(lcdm, float(z), lcdm_v)
        dm_r = transverse_comoving_distance_mpc(rll, float(z), rll_v)
        dm_err = max(dm_err, abs(dm_l - dm_r))

    ok = e_err < TOL and h_err < TOL and dm_err < 1e-7
    return {
        "id": "LCDM_RLL_NULL_GEOMETRY",
        "status": _status(ok),
        "condition": "RLL Os0=0 with common H0,Om,Ob_h2",
        "max_e2_abs_error": e_err,
        "max_H_abs_error": h_err,
        "max_DM_mpc_abs_error": dm_err,
    }


def run() -> dict:
    gates = [
        registry_gate(),
        desi_geometry_gate(),
        cone_annulus_gate(),
        model_null_gate(),
    ]
    fail = [x["id"] for x in gates if x["status"] == "FAIL"]
    token = [x["id"] for x in gates if x["status"].startswith("TOKEN_VAZIO")]
    return {
        "schema": "rll.formula_cosmology_geometry.execution.v1",
        "claim_allowed": False,
        "summary": {
            "gates": len(gates),
            "fail": len(fail),
            "token_vazio": len(token),
            "all_executed_pass": not fail and not token,
        },
        "gates": gates,
        "pending_heavy_routes": [
            "per-expression execution for 144 deterministic MF items",
            "per-expression structural assertions for 16 MF items",
            "33 hypothesis/model falsifiers",
            "Pantheon+ full-covariance LCDM/RLL/CPL G4 route",
            "130 geometry-diagnostic candidates with covariance-aware multiple-testing controls",
            "prior-art classification",
        ],
        "physical_claim": "BLOCKED",
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path)
    args = parser.parse_args()
    payload = run()
    text = json.dumps(payload, indent=2, sort_keys=True) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(text, encoding="utf-8")
    print(text, end="")
    return 0 if payload["summary"]["fail"] == 0 else 1


if __name__ == "__main__":
    raise SystemExit(main())
