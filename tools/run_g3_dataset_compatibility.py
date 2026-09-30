#!/usr/bin/env python3
"""Execute G3 dataset compatibility for DESI DR2 BAO + Pantheon+.

The gate validates source transcription, redshift coverage, Pantheon sample
partition, covariance custody and recorded DESI reconstruction/systematics.
It does not fit RLL and cannot promote a physical claim.
"""
from __future__ import annotations

import argparse
import csv
import importlib.util
import json
import math
import sys
from pathlib import Path
from types import ModuleType
from typing import Any

ROOT = Path(__file__).resolve().parents[1]
CONTRACT = ROOT / "data/contracts/rll_g3_dataset_compatibility.v1.json"
V3 = ROOT / "tools/validate_scientific_validation_orchestrator_v3.py"
DESI_POINTS = ROOT / "data/real/cosmology/desi_dr2_bao_primary_points.csv"
PANTHEON_CATALOG = ROOT / "data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat"


def _module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    return mod


def _json(path: Path) -> dict[str, Any]:
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: expected object")
    return data


def _desi_rows(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as f:
        rows = list(csv.DictReader(f))
    if len(rows) != 13:
        raise ValueError(f"DESI primary vector must contain 13 rows, got {len(rows)}")
    return rows


def _pantheon_summary(path: Path) -> dict[str, Any]:
    with path.open(encoding="utf-8") as f:
        header = f.readline().split()
        idx = {name: i for i, name in enumerate(header)}
        for required in ("zHD", "IS_CALIBRATOR"):
            if required not in idx:
                raise ValueError(f"Pantheon missing {required}")
        zs: list[float] = []
        calibrators = 0
        for line in f:
            if not line.strip():
                continue
            values = line.split()
            z = float(values[idx["zHD"]])
            cal = int(float(values[idx["IS_CALIBRATOR"]]))
            zs.append(z)
            calibrators += cal
    return {
        "rows": len(zs),
        "calibrators": calibrators,
        "cosmology_rows": len(zs) - calibrators,
        "z_min": min(zs),
        "z_max": max(zs),
    }


def _find_row(rows: list[dict[str, str]], tracer: str, observable: str) -> dict[str, str]:
    matches = [r for r in rows if r["tracer"] == tracer and r["observable"] == observable]
    if len(matches) != 1:
        raise ValueError(f"expected one DESI row for {tracer}/{observable}, got {len(matches)}")
    return matches[0]


def build_report(root: Path = ROOT) -> dict[str, Any]:
    contract = _json(root / CONTRACT.relative_to(ROOT))
    v3 = _module("rll_sv_v3_for_g3", root / V3.relative_to(ROOT))
    readiness = v3.build_readiness(root)
    if not readiness.get("g2_ready"):
        return {
            "schema": "rll.g3_dataset_compatibility_receipt.v1",
            "state": "BLOCKED_BY_G2",
            "claim_allowed": False,
            "scientific_confirmation": False,
            "g2_state": readiness.get("gate_states", {}).get("G2"),
            "F_ok": [],
            "F_gap": ["G2 is not receipt-ready"],
            "F_next": "repair G2 without bypass",
        }

    rows = _desi_rows(root / DESI_POINTS.relative_to(ROOT))
    sn = _pantheon_summary(root / PANTHEON_CATALOG.relative_to(ROOT))
    expected_rows = contract["sources"]["desi_dr2"]["table4_primary_rows"]

    source_checks: list[dict[str, Any]] = []
    fap_checks: list[dict[str, Any]] = []
    errors: list[str] = []
    for expected in expected_rows:
        tracer = expected["tracer"]
        if expected.get("observable") == "DV_over_rd":
            actual = _find_row(rows, tracer, "DV_over_rd")
            value_delta = abs(float(actual["value"]) - float(expected["value"]))
            sigma_delta = abs(float(actual["sigma"]) - float(expected["sigma"]))
            ok = value_delta <= 1e-12 and sigma_delta <= 1e-12
            source_checks.append({"tracer": tracer, "type": "DV", "passed": ok, "value_delta": value_delta, "sigma_delta": sigma_delta})
            if not ok:
                errors.append(f"{tracer}: DV transcription mismatch")
            continue

        dm = _find_row(rows, tracer, "DM_over_rd")
        dh = _find_row(rows, tracer, "DH_over_rd")
        direct_fields = [
            (float(dm["value"]), float(expected["dm_over_rd"]), "DM value"),
            (float(dm["sigma"]), float(expected["dm_sigma"]), "DM sigma"),
            (float(dh["value"]), float(expected["dh_over_rd"]), "DH value"),
            (float(dh["sigma"]), float(expected["dh_sigma"]), "DH sigma"),
        ]
        direct_ok = all(abs(a - b) <= 1e-12 for a, b, _ in direct_fields)
        if not direct_ok:
            errors.append(f"{tracer}: primary Table 4 DM/DH transcription mismatch")
        source_checks.append({"tracer": tracer, "type": "DM_DH", "passed": direct_ok})

        ratio = float(dm["value"]) / float(dh["value"])
        source_ratio = float(expected["dm_dh_ratio"])
        source_sigma = float(expected["dm_dh_sigma"])
        residual_sigma = abs(ratio - source_ratio) / source_sigma
        fap_ok = residual_sigma <= 1.0
        fap_checks.append(
            {
                "tracer": tracer,
                "z_eff": float(dm["z_eff"]),
                "repo_dm_over_dh": ratio,
                "primary_table_dm_over_dh": source_ratio,
                "primary_table_sigma": source_sigma,
                "absolute_delta": abs(ratio - source_ratio),
                "delta_in_primary_sigma": residual_sigma,
                "passed": fap_ok,
            }
        )
        if not fap_ok:
            errors.append(f"{tracer}: F_AP proxy outside one published sigma")

    sn_expected = contract["sources"]["pantheon_plus"]
    sn_ok = sn["rows"] == 1701 and sn["calibrators"] == 77 and sn["cosmology_rows"] == 1624
    if not sn_ok:
        errors.append("Pantheon 1701/77/1624 partition mismatch")

    desi_z = [float(row["z_eff"]) for row in rows]
    in_span = [z for z in desi_z if sn["z_min"] <= z <= sn["z_max"]]
    outside = [z for z in desi_z if not (sn["z_min"] <= z <= sn["z_max"])]
    eta_z = len(in_span) / len(desi_z)
    high_z_extension_ok = all(z > sn["z_max"] for z in outside)
    if not high_z_extension_ok:
        errors.append("DESI points outside Pantheon span are not a pure high-z extension")

    method = contract["sources"]["desi_dr2"]["method_facts"]
    reconstruction_recorded = all(str(method.get(key, "")).strip() for key in (
        "galaxy_quasar_reconstruction", "bao_covariance", "distance_basis", "fiducial_cosmology_boundary", "supernova_combination"
    ))
    if not reconstruction_recorded:
        errors.append("DESI reconstruction/systematics provenance incomplete")

    passed = not errors
    state = "PASS_LIMITED_COMPATIBILITY_BRANCH" if passed else "BLOCKED_G3_COMPATIBILITY"
    return {
        "schema": "rll.g3_dataset_compatibility_receipt.v1",
        "state": state,
        "claim_allowed": False,
        "scientific_confirmation": False,
        "g2_state": readiness["gate_states"]["G2"],
        "source_contract": str(CONTRACT.relative_to(ROOT)),
        "desi_source": {"arxiv": "2503.14738v3", "table": 4},
        "pantheon_sources": {"cosmology_arxiv": "2202.04077", "dataset_arxiv": "2112.03863"},
        "eta_z_gate": {
            "definition": contract["diagnostics"]["eta_z"]["definition"],
            "value": eta_z,
            "desi_observables_inside_pantheon_span": len(in_span),
            "desi_observables_total": len(desi_z),
            "pantheon_zHD_span": [sn["z_min"], sn["z_max"]],
            "outside_z": outside,
            "branch": "SHARED_RANGE_PLUS_DESI_HIGH_Z_EXTENSION" if high_z_extension_ok else "BLOCKED",
            "passed": high_z_extension_ok,
        },
        "F_AP_gate": {
            "definition": contract["diagnostics"]["f_ap"]["definition"],
            "checks": fap_checks,
            "passed": all(item["passed"] for item in fap_checks),
        },
        "primary_table_transcription": {"checks": source_checks, "passed": all(item["passed"] for item in source_checks)},
        "SN_sample_comparison": {**sn, "expected_light_curves": sn_expected["expected_light_curves"], "passed": sn_ok},
        "reconstruction_sensitivity_report": {
            "source_recorded": reconstruction_recorded,
            "galaxy_quasar_method": method["galaxy_quasar_reconstruction"],
            "systematics_recorded": method["bao_covariance"],
            "fiducial_cosmology_boundary": method["fiducial_cosmology_boundary"],
            "rll_independent_reconstruction_ablation": "TOKEN_VAZIO_INDEPENDENT_DESI_RECONSTRUCTION_ABLATION",
            "passed_for_joint_branch": reconstruction_recorded,
        },
        "compatibility_decision": {
            "branch": contract["joint_branch"]["name"],
            "allowed": passed,
            "residuals": contract["joint_branch"]["residuals_allowed_but_visible"],
            "interpretation": "Data blocks may enter a declared joint-likelihood branch; this is not evidence for RLL or any model preference.",
        },
        "F_ok": [
            "G2 receipt-aware covariance custody is ready",
            "DESI committed Table 4 values match the pinned primary-publication values" if all(item["passed"] for item in source_checks) else "TOKEN_VAZIO_DESI_TABLE4",
            "DESI DM/DH ratios agree with rounded primary Table 4 ratios within one published sigma" if all(item["passed"] for item in fap_checks) else "TOKEN_VAZIO_F_AP",
            "Pantheon sample partition is 1701/77/1624" if sn_ok else "TOKEN_VAZIO_SN_SAMPLE",
        ],
        "F_gap": errors + [
            "TOKEN_VAZIO_INDEPENDENT_DESI_RECONSTRUCTION_ABLATION",
            "TOKEN_VAZIO_EXPLICIT_CROSS_SURVEY_COVARIANCE_MATRIX",
        ],
        "F_next": "execute fair baseline tournament on this frozen branch; keep reconstruction/cross-survey residuals visible",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Execute RLL G3 DESI/Pantheon compatibility gate")
    parser.add_argument("--json", action="store_true")
    parser.add_argument("--output", type=Path, default=None)
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()
    try:
        report = build_report(ROOT)
    except Exception as exc:
        print(f"[rll] BLOCKED_G3_EXCEPTION: {exc}", file=sys.stderr)
        return 2
    payload = json.dumps(report, indent=2, sort_keys=True, ensure_ascii=False) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(payload, encoding="utf-8")
    if args.json or not args.output:
        print(payload, end="")
    if args.require_pass and report.get("state") != "PASS_LIMITED_COMPATIBILITY_BRANCH":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
