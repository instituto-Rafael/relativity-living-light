#!/usr/bin/env python3
"""Validate the RLL real-data evidence bridge against local artifacts.

The tool is deliberately offline at execution time: literature identities and
published context are versioned in the registry, while local data hashes and
schemas are verified from the checkout.  Literature context is never treated as
an optimization target or as confirmation of RLL.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import sys
from pathlib import Path
from typing import Any

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
REGISTRY = ROOT / "data" / "governance" / "RLL_EXTERNAL_EVIDENCE_REGISTRY_V1.json"
CONTRACT = ROOT / "data" / "governance" / "RLL_REAL_DATA_VALIDATION_CONTRACT_V2.json"
DEFAULT_OUTPUT = ROOT / "results" / "audit" / "rll_real_data_evidence_bridge.json"


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_json(path: Path) -> dict[str, Any]:
    return json.loads(path.read_text(encoding="utf-8"))


def read_csv(path: Path) -> list[dict[str, str]]:
    with path.open(newline="", encoding="utf-8") as fp:
        return list(csv.DictReader(fp))


def evidence_by_id(registry: dict[str, Any], source_id: str) -> dict[str, Any]:
    return next(item for item in registry["sources"] if item["id"] == source_id)


def validate_hash(entry: dict[str, Any]) -> dict[str, Any]:
    path = ROOT / entry["local_artifact"]
    observed = sha256_file(path) if path.exists() else None
    expected = entry.get("local_sha256")
    return {
        "path": entry["local_artifact"],
        "exists": path.exists(),
        "expected_sha256": expected,
        "observed_sha256": observed,
        "pass": bool(path.exists() and expected and observed == expected),
    }


def validate_hz_partition(contract: dict[str, Any]) -> dict[str, Any]:
    cfg = contract["data_partitions"]["expansion_independent"]
    path = ROOT / cfg["path"]
    rows = read_csv(path)
    sources = sorted({row["source"] for row in rows})
    excluded_present = [x for x in cfg["excludes"] if x in sources]
    return {
        "path": cfg["path"],
        "rows": len(rows),
        "expected_rows": cfg["expected_rows"],
        "sources": sources,
        "excluded_sources_present": excluded_present,
        "pass": len(rows) == cfg["expected_rows"] and sources == ["CC_Moresco2022"] and not excluded_present,
    }


def validate_desi(entry: dict[str, Any], contract: dict[str, Any]) -> dict[str, Any]:
    data_cfg = contract["data_partitions"]["bao"]
    points = read_csv(ROOT / data_cfg["path"])
    cov = np.loadtxt(ROOT / data_cfg["covariance_path"], delimiter=",", skiprows=1, usecols=range(1, 14))
    symmetric = bool(np.allclose(cov, cov.T, rtol=0.0, atol=1e-12))
    eigen_min = float(np.min(np.linalg.eigvalsh(cov))) if symmetric else float("-inf")
    source_ok = all(row.get("source_url") == entry["arxiv_url"] for row in points)
    return {
        "rows": len(points),
        "expected_rows": data_cfg["expected_rows"],
        "source_urls_match_registry": source_ok,
        "covariance_shape": list(cov.shape),
        "covariance_symmetric": symmetric,
        "covariance_min_eigenvalue": eigen_min,
        "covariance_positive_definite": eigen_min > 0.0,
        "pass": (
            len(points) == data_cfg["expected_rows"]
            and source_ok
            and cov.shape == (13, 13)
            and symmetric
            and eigen_min > 0.0
        ),
    }


def validate_cmb(entry: dict[str, Any]) -> dict[str, Any]:
    payload = load_json(ROOT / entry["local_artifact"])
    cov = np.asarray(payload["covariance"], dtype=float)
    eig = np.linalg.eigvalsh(cov)
    source = payload.get("primary_source", {})
    return {
        "parameter_order": payload.get("parameter_order"),
        "source_url": source.get("url"),
        "source_matches_registry": source.get("url") == entry["arxiv_url"],
        "covariance_shape": list(cov.shape),
        "covariance_min_eigenvalue": float(np.min(eig)),
        "acoustic_scale_contract": entry["acoustic_scale_contract"],
        "pass": (
            payload.get("parameter_order") == entry["required_parameter_order"]
            and source.get("url") == entry["arxiv_url"]
            and cov.shape == (3, 3)
            and float(np.min(eig)) > 0.0
        ),
    }


def validate_growth(registry: dict[str, Any]) -> dict[str, Any]:
    entry = evidence_by_id(registry, "FSIGMA8_COMPILATION_MEHRABI_2015")
    rows = read_csv(ROOT / entry["local_artifact"])
    correction = next(x for x in registry["known_provenance_corrections"] if x["id"] == "GROWTH_DOI_CORRECTION_20260912")
    wrong_doi_removed_from_registry = all("stw1614" not in json.dumps(x) for x in registry["sources"])
    return {
        "rows": len(rows),
        "compilation_source": entry["doi"],
        "historical_wrong_doi": correction["historical_value"],
        "historical_artifact_mutated": correction["historical_artifact_mutated"],
        "wrong_doi_absent_from_active_sources": wrong_doi_removed_from_registry,
        "covariance_status": "TOKEN_VAZIO_HETEROGENEOUS",
        "claim_role": "exploratory_only",
        "pass": len(rows) > 0 and entry["doi"].endswith("stv1478") and wrong_doi_removed_from_registry,
    }


def validate_pantheon(entry: dict[str, Any]) -> dict[str, Any]:
    ctx = entry["published_context"]
    return {
        "literature_identity": entry["arxiv"],
        "light_curves": ctx["light_curves"],
        "distinct_sne_ia": ctx["distinct_sne_ia"],
        "redshift_range": [ctx["redshift_min"], ctx["redshift_max"]],
        "benchmark_semantics": entry["benchmark_semantics"],
        "pass": (
            ctx["light_curves"] == 1701
            and ctx["distinct_sne_ia"] == 1550
            and ctx["redshift_min"] == 0.001
            and ctx["redshift_max"] == 2.26
            and entry["benchmark_semantics"] == "context_only_not_fit_target"
        ),
    }


def build_report() -> dict[str, Any]:
    registry = load_json(REGISTRY)
    contract = load_json(CONTRACT)

    desi_entry = evidence_by_id(registry, "DESI_DR2_BAO_2025")
    cmb_entry = evidence_by_id(registry, "PLANCK_2018_DISTANCE_PRIORS")
    pantheon_entry = evidence_by_id(registry, "PANTHEON_PLUS_COSMOLOGY")

    checks = {
        "desi_local_hash": validate_hash(desi_entry),
        "cmb_local_hash": validate_hash(cmb_entry),
        "growth_local_hash": validate_hash(evidence_by_id(registry, "FSIGMA8_COMPILATION_MEHRABI_2015")),
        "hz_independence_partition": validate_hz_partition(contract),
        "desi_schema_covariance": validate_desi(desi_entry, contract),
        "cmb_distance_prior_identity": validate_cmb(cmb_entry),
        "growth_provenance": validate_growth(registry),
        "pantheon_literature_identity": validate_pantheon(pantheon_entry),
    }

    data_bridge_pass = all(item["pass"] for item in checks.values())
    return {
        "schema": "rll.real_data_evidence_bridge_report.v1",
        "data_bridge_pass": data_bridge_pass,
        "background_data_ready_for_successor_fit": data_bridge_pass,
        "full_joint_inference_ready": False,
        "claim_allowed": False,
        "status": "EVIDENCE_BRIDGE_READY_MODEL_GATED" if data_bridge_pass else "EVIDENCE_BRIDGE_BLOCKED",
        "checks": checks,
        "external_benchmarks": {
            "DESI_DR2": desi_entry["published_context"],
            "PantheonPlus": pantheon_entry["published_context"],
        },
        "non_comparability_guard": contract["comparability_rule"],
        "remaining_model_gates": contract["promotion_gates"],
        "invariants": [
            "SOURCE != ARTEFACT != EXECUTION != EVIDENCE != CLAIM",
            "literature similarity != confirmation",
            "historical result != current validated result",
            "published sigma != internal delta-AIC unless likelihood contracts match",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--require-data-ready", action="store_true")
    args = parser.parse_args()

    report = build_report()
    output = args.output if args.output.is_absolute() else ROOT / args.output
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(json.dumps(report, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps(report, indent=2, sort_keys=True))
    return 0 if (not args.require_data_ready or report["data_bridge_pass"]) else 2


if __name__ == "__main__":
    raise SystemExit(main())
