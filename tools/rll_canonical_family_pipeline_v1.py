#!/usr/bin/env python3
"""Canonical orchestration for the bounded RLL family-theory layer.

Route:
SOURCE -> FAMILY EXECUTORS -> CROSS-FAMILY CONTRACT -> GATES -> RECEIPTS -> R3

This pipeline is scientific-governance infrastructure. It can PASS its formal
contracts while keeping physical fluid/cosmology bindings fail-closed.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
from typing import Any

from tools import rll_family_theory_bridge_v1 as bridge
from tools import rll_full_permutation_void_census_v1 as census
from tools import rll_prime_base_abscissa_curve_v1 as abscissa

CLAIM_ALLOWED = False
SOURCE_BOUNDARY = "SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM"
ROOT = Path(__file__).resolve().parents[1]

SOURCE_PATHS = (
    "tools/rll_full_permutation_void_census_v1.py",
    "tools/rll_family_theory_bridge_v1.py",
    "tools/rll_prime_base_abscissa_curve_v1.py",
    "tools/rll_repdigit_geometry_molds_v1.py",
    "tools/rll_geometric_dispersion_false_positive_gate.py",
    "data/epistemic_void/rll_full_permutation_void_census_v1.json",
    "data/epistemic_void/rll_family_theory_bridge_v1.json",
    "docs/research/RLL_FULL_PERMUTATION_VOID_CENSUS_V1.md",
    "docs/research/RLL_SET_NUMBER_GRAPH_PRIME_FLUID_FAMILIES_V1.md",
    "docs/research/RLL_PRIME_BASE_ABSCISSA_CURVE_V1.md",
)

RECEIPT_FILENAMES = (
    "01_source_receipt.json",
    "02_permutation_void_receipt.json",
    "03_family_receipt.json",
    "04_prime_base_abscissa_receipt.json",
    "05_cross_family_receipt.json",
    "06_gate_receipt.json",
)


def json_safe(value: Any) -> Any:
    if isinstance(value, dict):
        return {str(k): json_safe(v) for k, v in value.items()}
    if isinstance(value, (list, tuple, set, frozenset)):
        return [json_safe(v) for v in value]
    return value


def canonical_bytes(value: Any) -> bytes:
    return (json.dumps(json_safe(value), sort_keys=True, indent=2) + "\n").encode("utf-8")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_file(path: Path) -> str:
    return sha256_bytes(path.read_bytes())


def write_json(path: Path, value: Any) -> None:
    path.write_bytes(canonical_bytes(value))


def source_receipt() -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    for rel in SOURCE_PATHS:
        path = ROOT / rel
        if not path.is_file():
            missing.append(rel)
            continue
        rows.append({"path": rel, "bytes": path.stat().st_size, "sha256": sha256_file(path)})
    return {
        "schema": "rll.canonical_family_pipeline.source_receipt.v1",
        "claim_allowed": CLAIM_ALLOWED,
        "source_boundary": SOURCE_BOUNDARY,
        "sources": rows,
        "missing": missing,
    }


def cross_family_receipt() -> dict[str, Any]:
    repunit6 = bridge.repunit(6, 10)
    base10_units = abscissa.unit_primes_for_base(10)
    factor_graph = bridge.factor_incidence_graph((18, 21, 42, 1001, repunit6))
    g3 = bridge.functional_cycles(bridge.functional_graph(7, 3))
    g7 = bridge.functional_cycles(bridge.functional_graph(3, 7))
    crt21_ok = all(
        bridge.crt_reconstruct(bridge.crt_coordinates(n, bridge.CRT_21), bridge.CRT_21) == n
        for n in range(21)
    )
    crt42_ok = all(
        bridge.crt_reconstruct(bridge.crt_coordinates(n, bridge.CRT_42), bridge.CRT_42) == n
        for n in range(42)
    )
    zero_axis = abscissa.modular_axis(21, 7)
    graph_balance = bridge.graph_flow_balance((
        ("source", "junction", 2.0),
        ("junction", "a", 0.75),
        ("junction", "b", 1.25),
    ))
    continuity = bridge.continuity_residual(1.0, 2.0, 3.0, 1.0, 1.0, 6.0)
    fluid_gate = bridge.fluid_binding_gate({"geometry": "tube"})
    geometry = {
        "pentagon": census.regular_mold(5, 1),
        "pentagram": census.regular_mold(5, 2),
        "dodecagon": census.regular_mold(12, 1),
        "dodecagram_12_5": census.regular_mold(12, 5),
    }
    return json_safe({
        "schema": "rll.canonical_family_pipeline.cross_family_receipt.v1",
        "claim_allowed": CLAIM_ALLOWED,
        "source_boundary": SOURCE_BOUNDARY,
        "set_void": {
            "numeric_zero_vs_empty_set": census.void_relation(census.VoidKind.NUMERIC_ZERO, census.VoidKind.EMPTY_SET),
            "numeric_zero_vs_token_vazio": census.void_relation(census.VoidKind.NUMERIC_ZERO, census.VoidKind.TOKEN_VAZIO),
            "residue_zero_class_7": bridge.residue_class_window(7, 0, 3),
        },
        "number_prime_base": {
            "repunit6": repunit6,
            "repunit6_prime_factors": bridge.prime_factors(repunit6),
            "base10_unit_primes": base10_units,
            "base10_unit_prime_period": abscissa.prime_carrier_period(base10_units),
            "period_equals_repunit6": abscissa.prime_carrier_period(base10_units) == repunit6,
        },
        "graphs": {
            "repdigit7_mod3_cycles": g3,
            "repdigit3_mod7_cycles": g7,
            "factor_incidence": factor_graph,
            "crt21_roundtrip": crt21_ok,
            "crt42_roundtrip": crt42_ok,
        },
        "abscissa": {
            "point_21": abscissa.abscissa_point(21),
            "mod7_zero_axis": zero_axis,
            "zero_axis_is_occupied": (
                zero_axis["residue"] == 0
                and zero_axis["zero_state"] == "RESIDUE_ZERO"
                and abs(float(zero_axis["cos"]) - 1.0) < 1e-12
                and abs(float(zero_axis["sin"])) < 1e-12
            ),
        },
        "geometry": geometry,
        "graph_fluid": {
            "node_balance": graph_balance,
            "junction_balance_zero": abs(float(graph_balance["junction"])) < 1e-12,
            "continuity_residual": continuity,
            "continuity_zero": abs(float(continuity)) < 1e-12,
        },
        "physical_boundaries": {
            "fluid_gate": fluid_gate,
            "fluid_binding": bridge.PHYSICAL_FLUID_BINDING_STATE,
            "cosmology_binding": bridge.PHYSICAL_COSMOLOGY_BINDING_STATE,
        },
    })


def gate(gate_id: str, domain: str, passed: bool, evidence: Any, boundary: str) -> dict[str, Any]:
    return {
        "gate_id": gate_id,
        "domain": domain,
        "state": "PASS" if passed else "FAIL",
        "evidence": json_safe(evidence),
        "boundary": boundary,
    }


def evaluate_gates(source: dict[str, Any], census_receipt: dict[str, Any], family_receipt: dict[str, Any], prime_receipt: dict[str, Any], cross: dict[str, Any]) -> list[dict[str, Any]]:
    pg = cross["physical_boundaries"]["fluid_gate"]
    observed_g3 = cross["graphs"]["repdigit7_mod3_cycles"]
    observed_g7 = {tuple(x) for x in cross["graphs"]["repdigit3_mod7_cycles"]}
    expected_g7 = {(0, 3, 5, 4, 1, 6), (2,)}
    return [
        gate("G01-SOURCE-CUSTODY", "provenance", not source["missing"] and len(source["sources"]) == len(SOURCE_PATHS), {"source_count": len(source["sources"]), "missing": source["missing"]}, "Every declared source must exist and be hashed."),
        gate("G02-CLAIM-BOUNDARY", "governance", census_receipt["claim_allowed"] is False and family_receipt["claim_allowed"] is False and prime_receipt["claim_allowed"] is False, {"census": census_receipt["claim_allowed"], "family": family_receipt["claim_allowed"], "prime_base": prime_receipt["claim_allowed"]}, "Formal pipeline success must never auto-promote a physical claim."),
        gate("G03-ZERO-TYPING", "set_void", cross["set_void"]["numeric_zero_vs_empty_set"] == "DISTINCT_OR_NOT_COMPARABLE" and cross["set_void"]["numeric_zero_vs_token_vazio"] == "DISTINCT_OR_NOT_COMPARABLE", cross["set_void"], "ZERO != EMPTY_SET != TOKEN_VAZIO."),
        gate("G04-REPUNIT-PRIME-BASE", "number_prime_base", cross["number_prime_base"]["repunit6"] == 111111 and tuple(cross["number_prime_base"]["repunit6_prime_factors"]) == (3, 7, 11, 13, 37) and cross["number_prime_base"]["period_equals_repunit6"] is True, cross["number_prime_base"], "Base-dependent arithmetic identity is not a universal physical period."),
        gate("G05-FUNCTIONAL-GRAPHS", "graphs", observed_g3 == [[0, 1, 2]] and observed_g7 == expected_g7, {"mod3": observed_g3, "mod7": cross["graphs"]["repdigit3_mod7_cycles"]}, "Functional graph topology is arithmetic, not automatically spatial geometry."),
        gate("G06-CRT-ROUNDTRIP", "crt", cross["graphs"]["crt21_roundtrip"] is True and cross["graphs"]["crt42_roundtrip"] is True, {"crt21": cross["graphs"]["crt21_roundtrip"], "crt42": cross["graphs"]["crt42_roundtrip"]}, "CRT coordinates are exact arithmetic coordinates."),
        gate("G07-ABSCISSA-ZERO", "abscissa", cross["abscissa"]["zero_axis_is_occupied"] is True, cross["abscissa"]["mod7_zero_axis"], "Residue zero is an occupied point, not missing data."),
        gate("G08-GEOMETRY-STEPS", "geometry", cross["geometry"]["pentagon"]["step_angle_rad"] != cross["geometry"]["pentagram"]["step_angle_rad"] and cross["geometry"]["dodecagon"]["step_angle_rad"] != cross["geometry"]["dodecagram_12_5"]["step_angle_rad"], {"pentagon": cross["geometry"]["pentagon"]["schlafli"], "pentagram": cross["geometry"]["pentagram"]["schlafli"], "dodecagon": cross["geometry"]["dodecagon"]["schlafli"], "dodecagram": cross["geometry"]["dodecagram_12_5"]["schlafli"]}, "Polygon and star-polygon remain distinct typed objects."),
        gate("G09-GRAPH-FLOW-CONSERVATION", "graph_fluid", cross["graph_fluid"]["junction_balance_zero"] is True, cross["graph_fluid"]["node_balance"], "Balance zero means conservation, not absence."),
        gate("G10-CONTINUITY-FIXTURE", "fluid_math", cross["graph_fluid"]["continuity_zero"] is True, {"residual": cross["graph_fluid"]["continuity_residual"]}, "Continuity is formal only under declared flow assumptions."),
        gate("G11-FLUID-FAIL-CLOSED", "physical_boundary", pg["state"] == bridge.PHYSICAL_FLUID_BINDING_STATE and pg["claim_allowed"] is False, pg, "Missing physical inputs must keep fluid binding blocked."),
        gate("G12-COSMOLOGY-FAIL-CLOSED", "physical_boundary", cross["physical_boundaries"]["cosmology_binding"] == bridge.PHYSICAL_COSMOLOGY_BINDING_STATE, cross["physical_boundaries"]["cosmology_binding"], "Arithmetic/geometric coherence does not establish RLL cosmological physics."),
    ]


def build_pipeline(output_dir: Path, head_sha: str = "TOKEN_VAZIO_HEAD_SHA", run_id: str = "LOCAL") -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)
    source = source_receipt()
    census_receipt = json_safe(census.receipt())
    family_receipt = json_safe(bridge.family_manifest())
    prime_receipt = json_safe(abscissa.base_prime_receipt())
    cross = cross_family_receipt()
    gates = evaluate_gates(source, census_receipt, family_receipt, prime_receipt, cross)
    gate_receipt = {
        "schema": "rll.canonical_family_pipeline.gate_receipt.v1",
        "claim_allowed": CLAIM_ALLOWED,
        "gate_count": len(gates),
        "pass_count": sum(g["state"] == "PASS" for g in gates),
        "fail_count": sum(g["state"] == "FAIL" for g in gates),
        "gates": gates,
    }
    payloads = (source, census_receipt, family_receipt, prime_receipt, cross, gate_receipt)
    for name, payload in zip(RECEIPT_FILENAMES, payloads):
        write_json(output_dir / name, payload)
    child_receipts = {
        name: {"sha256": sha256_file(output_dir / name), "bytes": (output_dir / name).stat().st_size}
        for name in RECEIPT_FILENAMES
    }
    all_pass = gate_receipt["fail_count"] == 0
    final = {
        "schema": "rll.canonical_family_pipeline.final_receipt.v1",
        "pipeline_state": "PASS_FAIL_CLOSED" if all_pass else "FAIL",
        "claim_allowed": CLAIM_ALLOWED,
        "source_boundary": SOURCE_BOUNDARY,
        "head_sha": str(head_sha),
        "run_id": str(run_id),
        "child_receipts": child_receipts,
        "gates": gates,
        "physical_boundaries": {
            "fluid_binding": bridge.PHYSICAL_FLUID_BINDING_STATE,
            "cosmology_binding": bridge.PHYSICAL_COSMOLOGY_BINDING_STATE,
            "promotion_rule": "Physical promotion requires a separate observable contract, units, provenance, covariance, falsifier and independent reproduction.",
        },
        "r3": {
            "F_ok": "Canonical family pipeline, cross-family gates, receipts and custody hashes materialized.",
            "F_gap": "Physical fluid/cosmology bindings remain intentionally TOKEN_VAZIO; they are outside formal pipeline closure.",
            "F_next": "No implementation gap in this bounded pipeline. Any successor work is a separately preregistered physical-observation binding.",
        },
    }
    write_json(output_dir / "07_final_receipt.json", final)
    (output_dir / "R3.md").write_text(
        "# R3 — Canonical Family Pipeline V1\n\n"
        f"- F_ok: {final['r3']['F_ok']}\n"
        f"- F_gap: {final['r3']['F_gap']}\n"
        f"- F_next: {final['r3']['F_next']}\n\n"
        f"`pipeline_state={final['pipeline_state']}`  \n`claim_allowed=false`\n",
        encoding="utf-8",
    )
    return final


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output-dir", default="artifacts/rll-canonical-family-pipeline")
    parser.add_argument("--head-sha", default="TOKEN_VAZIO_HEAD_SHA")
    parser.add_argument("--run-id", default="LOCAL")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args()
    final = build_pipeline(Path(args.output_dir), args.head_sha, args.run_id)
    print(json.dumps(final, indent=2, sort_keys=True))
    if args.strict and final["pipeline_state"] != "PASS_FAIL_CLOSED":
        return 2
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
