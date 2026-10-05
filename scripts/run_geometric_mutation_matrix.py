#!/usr/bin/env python3
"""Deterministic geometric mutation/sensitivity matrix for RLL frontier CI.

This pipeline explores geometry/projection/fragment mutations and projects their
dimensionless features into bounded RLL background-parameter perturbations.
The projection is explicitly a sensitivity bridge, not a physical coupling law.
Extrinsic folding may shorten an embedding chord but never changes the intrinsic
distance by itself; no wormhole/shortcut claim is emitted.
"""
from __future__ import annotations

import argparse
import csv
import itertools
import json
import math
import sys
from pathlib import Path
from typing import Any, Iterable

import numpy as np
import yaml

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from src.rll.cosmology_fairness import e2_rll_logistic, w_eff_rll_density

SCHEMA = "rll.geometric_mutation_matrix.v1"


def load_contract(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if data.get("schema") != SCHEMA:
        raise ValueError(f"unexpected schema: {data.get('schema')!r}")
    if data.get("claim_allowed") is not False:
        raise ValueError("claim_allowed must remain false")
    sem = data.get("semantics", {})
    if sem.get("physical_wormhole_claim") is not False:
        raise ValueError("physical_wormhole_claim must remain false")
    if sem.get("cross_domain_bridge") != "SENSITIVITY_ONLY_NO_CAUSAL_CLAIM":
        raise ValueError("cross-domain bridge semantics must remain sensitivity-only")
    return data


def _vec(x: Iterable[float]) -> np.ndarray:
    return np.asarray(list(x), dtype=float)


def projection_matrix(name: str, contract: dict[str, Any]) -> np.ndarray:
    if name == "identity":
        return np.eye(3, dtype=float)
    if name == "anisotropic":
        return np.diag(_vec(contract["projection_parameters"]["anisotropic"]))
    if name == "shear":
        s = float(contract["projection_parameters"]["shear_xy"])
        return np.asarray([[1.0, s, 0.0], [0.0, 1.0, 0.0], [0.0, 0.0, 1.0]], dtype=float)
    if name == "extrinsic_fold":
        return np.eye(3, dtype=float)
    raise ValueError(f"unknown projection: {name}")


def apply_projection(point: np.ndarray, name: str, contract: dict[str, Any]) -> np.ndarray:
    p = np.asarray(point, dtype=float)
    if name == "extrinsic_fold":
        pivot = float(contract["projection_parameters"]["fold_pivot_x"])
        out = p.copy()
        out[0] = abs(out[0] - pivot)
        return out
    return projection_matrix(name, contract) @ p


def _safe_acos(x: float) -> float:
    return math.acos(max(-1.0, min(1.0, x)))


def geometry_distance(family: str, p: np.ndarray, q: np.ndarray, contract: dict[str, Any]) -> tuple[float, str]:
    gp = contract["geometry_parameters"]
    p = np.asarray(p, dtype=float)
    q = np.asarray(q, dtype=float)
    if family == "flat":
        return float(np.linalg.norm(q - p)), "EXACT_EUCLIDEAN"
    if family == "spherical":
        radius = float(gp["spherical_radius"])
        pn = p / np.linalg.norm(p)
        qn = q / np.linalg.norm(q)
        return radius * _safe_acos(float(np.dot(pn, qn))), "EXACT_GREAT_CIRCLE_ON_NORMALIZED_DIRECTIONS"
    if family == "hyperbolic":
        radius = float(gp["hyperbolic_radius"])
        pp = float(np.dot(p, p))
        qq = float(np.dot(q, q))
        if pp >= 1.0 or qq >= 1.0:
            return float("nan"), "OUTSIDE_POINCARE_BALL"
        d2 = float(np.dot(p - q, p - q))
        arg = 1.0 + (2.0 * d2) / ((1.0 - pp) * (1.0 - qq))
        return radius * math.acosh(max(1.0, arg)), "EXACT_POINCARE_BALL"
    if family == "toroidal":
        R = float(gp["torus_major_radius"])
        r = float(gp["torus_minor_radius"])
        u1, v1 = 2.0 * math.pi * float(p[0]), 2.0 * math.pi * float(p[1])
        u2, v2 = 2.0 * math.pi * float(q[0]), 2.0 * math.pi * float(q[1])
        du = ((u2 - u1 + math.pi) % (2.0 * math.pi)) - math.pi
        dv = ((v2 - v1 + math.pi) % (2.0 * math.pi)) - math.pi
        vm = 0.5 * (v1 + v2)
        local = math.sqrt(((R + r * math.cos(vm)) * du) ** 2 + (r * dv) ** 2)
        return float(local), "LOCAL_TORUS_METRIC_PROXY"
    raise ValueError(f"unknown geometry family: {family}")


def curvature_proxy(family: str, p: np.ndarray, q: np.ndarray, contract: dict[str, Any]) -> float:
    gp = contract["geometry_parameters"]
    if family == "flat":
        return 0.0
    if family == "spherical":
        r = float(gp["spherical_radius"])
        return 1.0 / (r * r)
    if family == "hyperbolic":
        r = float(gp["hyperbolic_radius"])
        return -1.0 / (r * r)
    if family == "toroidal":
        R = float(gp["torus_major_radius"])
        r = float(gp["torus_minor_radius"])
        vm = math.pi * (float(p[1]) + float(q[1]))
        denom = r * (R + r * math.cos(vm))
        return float(math.cos(vm) / denom)
    raise ValueError(f"unknown geometry family: {family}")


def fragment_measure_ratio(matrix: np.ndarray, dimension: int, scale: float) -> float:
    singular = np.linalg.svd(matrix, compute_uv=False)
    local = float(np.prod(np.sort(singular)[::-1][:dimension]))
    return local * float(scale) ** int(dimension)


def mutate_bridge_matrix(base: np.ndarray, variant: str) -> np.ndarray:
    m = np.asarray(base, dtype=float).copy()
    if variant == "baseline":
        return m
    if variant == "swap_curvature_distance":
        m[:, [0, 1]] = m[:, [1, 0]]
        return m
    if variant == "sign_flip_distance":
        m[:, 1] *= -1.0
        return m
    if variant == "sparse":
        out = np.zeros_like(m)
        out[:, 0] = m[:, 0]
        out[:, 2] = m[:, 2]
        return out
    raise ValueError(f"unknown bridge matrix mutation: {variant}")


def bounded(value: float, bounds: Iterable[float]) -> float:
    lo, hi = [float(x) for x in bounds]
    return min(hi, max(lo, float(value)))


def bridge_to_rll(features: np.ndarray, variant: str, contract: dict[str, Any]) -> dict[str, float]:
    bridge = contract["sensitivity_projection"]
    base_matrix = np.asarray(bridge["matrix"], dtype=float)
    m = mutate_bridge_matrix(base_matrix, variant)
    delta = m @ np.asarray(features, dtype=float)
    rll = contract["baseline"]["rll"]
    bounds = bridge["bounds"]
    return {
        "omega_s0": bounded(float(rll["omega_s0"]) + float(delta[0]), bounds["omega_s0"]),
        "z_t": bounded(float(rll["z_t"]) + float(delta[1]), bounds["z_t"]),
        "w_t": bounded(float(rll["w_t"]) + float(delta[2]), bounds["w_t"]),
    }


def case_rows(contract: dict[str, Any]) -> list[dict[str, Any]]:
    mut = contract["mutations"]
    variants = contract["sensitivity_projection"].get(
        "matrix_mutations",
        ["baseline", "swap_curvature_distance", "sign_flip_distance", "sparse"],
    )
    fragments = list(mut["fragments"].items())
    combos = itertools.product(
        mut["geometry_families"],
        mut["projections"],
        fragments,
        mut["scales"],
        variants,
    )
    rows: list[dict[str, Any]] = []
    p = _vec(contract["baseline"]["reference_points"]["p"])
    q = _vec(contract["baseline"]["reference_points"]["q"])
    z_samples = [float(z) for z in contract["baseline"]["rll"]["z_samples"]]
    om = float(contract["baseline"]["rll"]["omega_m"])

    for idx, (family, projection, fragment_item, scale, bridge_variant) in enumerate(combos):
        fragment, dim = fragment_item
        matrix = projection_matrix(projection, contract)
        p2 = apply_projection(p, projection, contract)
        q2 = apply_projection(q, projection, contract)
        d0, metric_state0 = geometry_distance(family, p, q, contract)

        if projection == "extrinsic_fold":
            d1 = d0
            metric_state1 = metric_state0
            extrinsic = float(np.linalg.norm(q2 - p2))
            noninjective = 1.0
            shortcut_semantics = "EXTRINSIC_ONLY"
        else:
            d1, metric_state1 = geometry_distance(family, p2, q2, contract)
            extrinsic = float(np.linalg.norm(q2 - p2))
            noninjective = 0.0
            shortcut_semantics = "NONE"

        measure = fragment_measure_ratio(matrix, int(dim), float(scale))
        cond = float(np.linalg.cond(matrix))
        curvature = curvature_proxy(family, p, q, contract)
        distance_delta = float(d1 / d0 - 1.0) if d0 > 0.0 and math.isfinite(d1) else float("nan")
        shortcut_ratio = float(extrinsic / d0) if d0 > 0.0 else float("nan")
        features = np.asarray(
            [
                curvature,
                distance_delta,
                math.log(max(measure, 1.0e-15)),
                math.log(max(cond, 1.0)),
                noninjective,
            ],
            dtype=float,
        )
        params = bridge_to_rll(features, bridge_variant, contract)
        e2 = np.asarray(
            e2_rll_logistic(
                np.asarray(z_samples, dtype=float),
                om=om,
                os0=params["omega_s0"],
                zt=params["z_t"],
                wt=params["w_t"],
            ),
            dtype=float,
        )
        weff = np.asarray(
            w_eff_rll_density(np.asarray(z_samples, dtype=float), params["z_t"], params["w_t"]),
            dtype=float,
        )

        row: dict[str, Any] = {
            "case_id": f"GM-{idx:04d}",
            "geometry_family": family,
            "projection": projection,
            "fragment": fragment,
            "fragment_dimension": int(dim),
            "fragment_scale": float(scale),
            "bridge_variant": bridge_variant,
            "metric_state_before": metric_state0,
            "metric_state_after": metric_state1,
            "curvature_proxy": curvature,
            "intrinsic_distance_before": d0,
            "intrinsic_distance_after": d1,
            "distance_delta": distance_delta,
            "extrinsic_distance_after": extrinsic,
            "shortcut_ratio": shortcut_ratio,
            "shortcut_semantics": shortcut_semantics,
            "noninjective": bool(noninjective),
            "measure_ratio": measure,
            "condition_number": cond,
            "matrix_rank": int(np.linalg.matrix_rank(matrix)),
            "omega_s0": params["omega_s0"],
            "z_t": params["z_t"],
            "w_t": params["w_t"],
            "claim_allowed": False,
            "physical_wormhole_claim": False,
            "bridge_semantics": contract["semantics"]["cross_domain_bridge"],
        }
        for z, value in zip(z_samples, e2):
            row[f"e2_z{z:g}"] = float(value)
        for z, value in zip(z_samples, weff):
            row[f"w_eff_z{z:g}"] = float(value)
        rows.append(row)

    max_cases = int(mut["max_cases"])
    if len(rows) > max_cases:
        raise ValueError(f"generated {len(rows)} cases > max_cases={max_cases}")
    return rows


def gate_rows(rows: list[dict[str, Any]], contract: dict[str, Any]) -> dict[str, Any]:
    finite_keys = [
        "curvature_proxy",
        "intrinsic_distance_before",
        "intrinsic_distance_after",
        "distance_delta",
        "extrinsic_distance_after",
        "shortcut_ratio",
        "measure_ratio",
        "condition_number",
        "omega_s0",
        "z_t",
        "w_t",
    ]
    failures: list[str] = []
    if contract["gates"].get("require_finite", True):
        for row in rows:
            for key in finite_keys:
                if not math.isfinite(float(row[key])):
                    failures.append(f"{row['case_id']} non-finite {key}")

    if contract["gates"].get("reject_physical_shortcut_claim", True):
        for row in rows:
            if row["physical_wormhole_claim"]:
                failures.append(f"{row['case_id']} forbidden physical shortcut claim")

    if contract["gates"].get("require_baseline_recovery", True):
        for row in rows:
            if (
                row["geometry_family"] == "flat"
                and row["projection"] == "identity"
                and row["fragment_scale"] == 1.0
            ):
                if abs(float(row["distance_delta"])) > 1.0e-12:
                    failures.append(f"{row['case_id']} baseline distance not recovered")
                if abs(float(row["measure_ratio"]) - 1.0) > 1.0e-12:
                    failures.append(f"{row['case_id']} baseline measure not recovered")

    for row in rows:
        if row["projection"] == "extrinsic_fold":
            if abs(float(row["intrinsic_distance_after"]) - float(row["intrinsic_distance_before"])) > 1.0e-12:
                failures.append(f"{row['case_id']} extrinsic fold changed intrinsic distance")
            if row["shortcut_semantics"] != "EXTRINSIC_ONLY":
                failures.append(f"{row['case_id']} fold semantics not typed")

    return {
        "status": "PASS" if not failures else "FAIL",
        "failure_count": len(failures),
        "failures": failures,
        "claim_allowed": False,
        "publication_effect": "NONE",
    }


def write_rows(rows: list[dict[str, Any]], outdir: Path) -> None:
    outdir.mkdir(parents=True, exist_ok=True)
    (outdir / "cases.jsonl").write_text(
        "".join(json.dumps(row, sort_keys=True) + "\n" for row in rows),
        encoding="utf-8",
    )
    if rows:
        with (outdir / "cases.csv").open("w", encoding="utf-8", newline="") as fh:
            writer = csv.DictWriter(fh, fieldnames=list(rows[0].keys()))
            writer.writeheader()
            writer.writerows(rows)


def cross_correlations(rows: list[dict[str, Any]], threshold: float) -> list[dict[str, Any]]:
    geometry_cols = [
        "curvature_proxy",
        "distance_delta",
        "shortcut_ratio",
        "measure_ratio",
        "condition_number",
        "noninjective",
    ]
    cosmology_cols = [
        "omega_s0",
        "z_t",
        "w_t",
        "e2_z0.5",
        "e2_z1",
        "e2_z2",
        "w_eff_z0.5",
        "w_eff_z1",
        "w_eff_z2",
    ]
    out: list[dict[str, Any]] = []
    for ga in geometry_cols:
        x = np.asarray([float(r[ga]) for r in rows], dtype=float)
        if np.std(x) == 0.0:
            continue
        for cb in cosmology_cols:
            y = np.asarray([float(r[cb]) for r in rows], dtype=float)
            if np.std(y) == 0.0:
                continue
            corr = float(np.corrcoef(x, y)[0, 1])
            if math.isfinite(corr) and abs(corr) >= threshold:
                out.append(
                    {
                        "geometry_feature": ga,
                        "cosmology_response": cb,
                        "pearson_r": corr,
                        "abs_r": abs(corr),
                        "semantics": "SENSITIVITY_TRANSFER_ASSOCIATION_ONLY",
                    }
                )
    return sorted(out, key=lambda item: item["abs_r"], reverse=True)


def bridge_uncertainty(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Quantify dependence on the arbitrary sensitivity bridge, metric by metric."""
    response_cols = ["omega_s0", "z_t", "w_t", "e2_z1", "w_eff_z1"]
    groups: dict[tuple[Any, ...], list[dict[str, Any]]] = {}
    for r in rows:
        key = (r["geometry_family"], r["projection"], r["fragment"], r["fragment_scale"])
        groups.setdefault(key, []).append(r)
    by_metric: dict[str, dict[str, float]] = {}
    for col in response_cols:
        spreads: list[float] = []
        for group in groups.values():
            if len(group) < 2:
                continue
            arr = np.asarray([float(r[col]) for r in group], dtype=float)
            spreads.append(float(np.std(arr)))
        by_metric[col] = {
            "mean_std_across_bridge_variants": float(np.mean(spreads)) if spreads else 0.0,
            "max_std_across_bridge_variants": float(np.max(spreads)) if spreads else 0.0,
        }
    return {"by_metric": by_metric, "semantics": "BRIDGE_CHOICE_SENSITIVITY_NOT_PHYSICAL_UNCERTAINTY"}


def aggregate(root: Path, outdir: Path, contract: dict[str, Any]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for path in sorted(root.rglob("cases.jsonl")):
        for line in path.read_text(encoding="utf-8").splitlines():
            if line.strip():
                rows.append(json.loads(line))
    if not rows:
        raise ValueError(f"no cases.jsonl under {root}")

    dedup = {row["case_id"]: row for row in rows}
    rows = [dedup[k] for k in sorted(dedup)]
    gate = gate_rows(rows, contract)
    min_cases = int(contract["gates"]["correlation_min_cases"])
    if len(rows) < min_cases:
        gate["status"] = "FAIL"
        gate["failures"].append(f"only {len(rows)} cases < correlation_min_cases={min_cases}")
        gate["failure_count"] = len(gate["failures"])

    correlations = cross_correlations(rows, float(contract["gates"]["correlation_abs_threshold"]))
    uncertainty = bridge_uncertainty(rows)
    summary = {
        "schema": "rll.geometric_mutation_matrix.receipt.v1",
        "case_count": len(rows),
        "gate": gate,
        "bridge_uncertainty": uncertainty,
        "cross_correlations": correlations[:20],
        "claim_allowed": False,
        "publication_effect": "NONE",
        "interpretation": {
            "fold": "extrinsic embedding only; no intrinsic/geodesic shortcut claim",
            "cross_domain": "sensitivity transfer only; correlations are not evidence of physical coupling",
        },
    }
    outdir.mkdir(parents=True, exist_ok=True)
    write_rows(rows, outdir)
    (outdir / "summary.json").write_text(json.dumps(summary, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    with (outdir / "cross-correlations.csv").open("w", encoding="utf-8", newline="") as fh:
        fields = ["geometry_feature", "cosmology_response", "pearson_r", "abs_r", "semantics"]
        writer = csv.DictWriter(fh, fieldnames=fields)
        writer.writeheader()
        writer.writerows(correlations)
    report = [
        "# Geometric Mutation Matrix Receipt",
        "",
        f"- cases: {len(rows)}",
        f"- gate: **{gate['status']}**",
        "- claim_allowed: `false`",
        "- publication_effect: `NONE`",
        "- fold semantics: extrinsic embedding only; intrinsic distance is preserved by contract.",
        "- cross-domain semantics: deterministic sensitivity projection only; no causal/physical coupling claim.",
        "- bridge spread: reported per response metric in summary.json",
        "",
        "## Strong sensitivity-transfer associations",
        "",
    ]
    if correlations:
        for item in correlations[:20]:
            report.append(
                f"- `{item['geometry_feature']}` ↔ `{item['cosmology_response']}`: "
                f"r={item['pearson_r']:.6f} ({item['semantics']})"
            )
    else:
        report.append("- none above threshold")
    if gate["failures"]:
        report.extend(["", "## Gate failures", ""] + [f"- {x}" for x in gate["failures"]])
    (outdir / "REPORT.md").write_text("\n".join(report) + "\n", encoding="utf-8")
    return summary


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--contract", type=Path, required=True)
    parser.add_argument("--output-dir", type=Path, required=True)
    parser.add_argument("--shard-index", type=int, default=0)
    parser.add_argument("--shard-count", type=int, default=1)
    parser.add_argument("--aggregate-root", type=Path)
    args = parser.parse_args()

    contract = load_contract(args.contract)
    if args.aggregate_root:
        summary = aggregate(args.aggregate_root, args.output_dir, contract)
        return 0 if summary["gate"]["status"] == "PASS" else 1

    if args.shard_count <= 0 or args.shard_index < 0 or args.shard_index >= args.shard_count:
        raise ValueError("invalid shard index/count")
    rows = case_rows(contract)
    selected = [row for i, row in enumerate(rows) if i % args.shard_count == args.shard_index]
    write_rows(selected, args.output_dir)
    gate = gate_rows(selected, contract)
    (args.output_dir / "shard-gate.json").write_text(json.dumps(gate, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return 0 if gate["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
