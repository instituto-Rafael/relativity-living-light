"""Aggregate the predeclared model-family seeds into an auditable shadow receipt.

The receipt records numerical sensitivity and ranking variation. It does not
convert ranking consensus into probability of truth, publication, or a
scientific claim. Every output remains claim_allowed=false.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
import statistics
import time
from io import StringIO
from pathlib import Path
from typing import Any, Iterable

import yaml

from .model_family_shadow import CONTRACT_PATH, load_contract, run_shadow_benchmark

BASE_DIR = Path(__file__).resolve().parents[3]
RECEIPT_CONTRACT_PATH = (
    BASE_DIR / "data" / "contracts" / "model_family_multiseed_receipt.v1.yml"
)
DEFAULT_OUTPUT_DIR = BASE_DIR / "results" / "structure_d" / "multiseed"
FIXED_ROW_FIELDS = {
    "model",
    "kind",
    "geometry",
    "chi2",
    "AIC",
    "AICc",
    "BIC",
    "N",
    "k",
    "dof",
    "chi2_Hz",
    "chi2_DESI_DR2_BAO",
    "claim_allowed",
}
PRESERVED_METRICS = ("chi2", "AIC", "AICc", "BIC", "chi2_Hz", "chi2_DESI_DR2_BAO")


def _sha256_bytes(raw: bytes) -> str:
    return hashlib.sha256(raw).hexdigest()


def _canonical_json(payload: Any) -> bytes:
    return json.dumps(
        payload,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + ".tmp")
    tmp.write_text(text, encoding="utf-8")
    tmp.replace(path)


def load_receipt_contract(path: Path = RECEIPT_CONTRACT_PATH) -> dict[str, Any]:
    payload = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("multi-seed receipt contract must be a mapping")
    if payload.get("schema") != "rll.cosmology_model_family_multiseed_receipt.v1":
        raise ValueError("unexpected multi-seed receipt contract schema")
    if payload.get("claim_allowed") is not False:
        raise ValueError("multi-seed receipt contract must remain claim_allowed=false")
    if payload.get("publication_effect") != "NONE":
        raise ValueError("multi-seed receipt publication_effect must remain NONE")
    return payload


def _finite_number(value: Any, *, label: str) -> float:
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise ValueError(f"{label} must be numeric")
    number = float(value)
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def _rows_by_model(payload: dict[str, Any]) -> dict[str, dict[str, Any]]:
    rows = payload.get("rows")
    if not isinstance(rows, list) or not rows:
        raise ValueError("shadow payload rows must be a non-empty list")
    mapped: dict[str, dict[str, Any]] = {}
    for raw in rows:
        if not isinstance(raw, dict):
            raise ValueError("shadow row must be a mapping")
        model = str(raw.get("model", ""))
        if not model or model in mapped:
            raise ValueError(f"invalid or duplicate model row: {model!r}")
        if raw.get("claim_allowed") is not False:
            raise ValueError(f"shadow row {model} must remain claim_allowed=false")
        for metric in PRESERVED_METRICS:
            _finite_number(raw.get(metric), label=f"{model}.{metric}")
        mapped[model] = raw
    return mapped


def _rank_models(rows: dict[str, dict[str, Any]], metric: str) -> dict[str, int]:
    ordered = sorted(
        rows,
        key=lambda model: (_finite_number(rows[model].get(metric), label=f"{model}.{metric}"), model),
    )
    return {model: index + 1 for index, model in enumerate(ordered)}


def _parameter_names(row: dict[str, Any]) -> list[str]:
    names: list[str] = []
    for key, value in row.items():
        if key in FIXED_ROW_FIELDS or isinstance(value, bool):
            continue
        if isinstance(value, (int, float)) and math.isfinite(float(value)):
            names.append(str(key))
    return sorted(names)


def _summary(values: Iterable[float]) -> dict[str, float]:
    data = [float(value) for value in values]
    if not data or any(not math.isfinite(value) for value in data):
        raise ValueError("summary requires non-empty finite values")
    low = min(data)
    high = max(data)
    return {
        "min": low,
        "median": float(statistics.median(data)),
        "max": high,
        "span": high - low,
    }


def validate_run_invariants(
    runs: list[dict[str, Any]],
    expected_seeds: list[int],
    ranking_metric: str,
) -> tuple[list[str], dict[str, dict[str, Any]], dict[str, Any]]:
    if len(runs) != len(expected_seeds):
        raise ValueError(f"expected {len(expected_seeds)} runs, received {len(runs)}")
    seeds = [int(run.get("optimizer", {}).get("seed")) for run in runs]
    if seeds != expected_seeds:
        raise ValueError(f"seed order mismatch: expected={expected_seeds}, got={seeds}")

    first = runs[0]
    model_order = [str(value) for value in first.get("model_order", [])]
    input_sha256 = first.get("input_sha256")
    if not model_order or not isinstance(input_sha256, dict) or not input_sha256:
        raise ValueError("first run lacks model order or input hashes")
    first_rows = _rows_by_model(first)
    if set(first_rows) != set(model_order):
        raise ValueError("first run rows do not match model_order")

    rows_per_seed: dict[str, dict[str, Any]] = {}
    for run in runs:
        if run.get("claim_allowed") is not False:
            raise ValueError("every run must remain claim_allowed=false")
        if run.get("publication_effect") != "NONE":
            raise ValueError("every run must remain publication_effect=NONE")
        if run.get("canonical_outputs_modified") is not False:
            raise ValueError("shadow run cannot modify canonical outputs")
        if [str(value) for value in run.get("model_order", [])] != model_order:
            raise ValueError("model order changed between seeds")
        if run.get("input_sha256") != input_sha256:
            raise ValueError("input hashes changed between seeds")
        optimizer = run.get("optimizer", {})
        if optimizer.get("post_hoc_bound_changes_forbidden") is not True:
            raise ValueError("post-hoc bound changes must remain forbidden")
        rows = _rows_by_model(run)
        if set(rows) != set(model_order):
            raise ValueError("model rows changed between seeds")
        seed = str(int(optimizer["seed"]))
        rows_per_seed[seed] = rows
        _rank_models(rows, ranking_metric)
    return model_order, rows_per_seed, input_sha256


def build_receipt(
    runs: list[dict[str, Any]],
    receipt_contract: dict[str, Any],
    source_contract: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    execution = receipt_contract["execution"]
    comparison = receipt_contract["comparison"]
    expected_seeds = [int(value) for value in source_contract["execution_policy"]["predeclared_seeds"]]
    ranking_metric = str(comparison["ranking_metric"])
    model_order, rows_per_seed, input_sha256 = validate_run_invariants(
        runs, expected_seeds, ranking_metric
    )

    seed_ranks = {
        seed: _rank_models(rows, ranking_metric) for seed, rows in rows_per_seed.items()
    }
    summaries: list[dict[str, Any]] = []
    for model in model_order:
        metric_values = {
            metric: [
                _finite_number(rows_per_seed[str(seed)][model][metric], label=f"{seed}.{model}.{metric}")
                for seed in expected_seeds
            ]
            for metric in PRESERVED_METRICS
        }
        ranks = [seed_ranks[str(seed)][model] for seed in expected_seeds]
        first_row = rows_per_seed[str(expected_seeds[0])][model]
        parameter_names = _parameter_names(first_row)
        parameter_summary: dict[str, dict[str, float]] = {}
        for parameter in parameter_names:
            values = [
                _finite_number(
                    rows_per_seed[str(seed)][model].get(parameter),
                    label=f"{seed}.{model}.{parameter}",
                )
                for seed in expected_seeds
            ]
            parameter_summary[parameter] = _summary(values)

        summary: dict[str, Any] = {
            "model": model,
            "kind": str(first_row["kind"]),
            "geometry": str(first_row["geometry"]),
            "ranking_metric": ranking_metric,
            "rank_by_seed": {str(seed): seed_ranks[str(seed)][model] for seed in expected_seeds},
            "rank_min": min(ranks),
            "rank_median": float(statistics.median(ranks)),
            "rank_max": max(ranks),
            "rank_span": max(ranks) - min(ranks),
            "metrics": {metric: _summary(values) for metric, values in metric_values.items()},
            "parameters": parameter_summary,
            "claim_allowed": False,
        }
        summaries.append(summary)

    winners = {
        seed: min(ranks, key=ranks.get) for seed, ranks in seed_ranks.items()
    }
    unique_winners = sorted(set(winners.values()))
    consensus = unique_winners[0] if len(unique_winners) == 1 else "NO_UNANIMOUS_WINNER"
    runtime_seconds = sum(float(run.get("runtime_seconds", 0.0)) for run in runs)
    maxiter_values = {int(run["optimizer"]["maxiter"]) for run in runs}
    tol_values = {float(run["optimizer"]["tol"]) for run in runs}
    if len(maxiter_values) != 1 or len(tol_values) != 1:
        raise ValueError("maxiter/tol changed between seeds")

    payload: dict[str, Any] = {
        "schema": receipt_contract["receipt"]["schema"],
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claim_allowed": False,
        "publication_effect": "NONE",
        "canonical_outputs_modified": False,
        "state": receipt_contract["completion"]["complete_state"],
        "state_does_not_imply": receipt_contract["completion"]["complete_state_does_not_imply"],
        "source_contract": str(CONTRACT_PATH.relative_to(BASE_DIR)),
        "source_contract_sha256": _sha256_bytes(CONTRACT_PATH.read_bytes()),
        "receipt_contract": str(RECEIPT_CONTRACT_PATH.relative_to(BASE_DIR)),
        "receipt_contract_sha256": _sha256_bytes(RECEIPT_CONTRACT_PATH.read_bytes()),
        "mode": execution["mode"],
        "optimizer": {
            "name": source_contract["execution_policy"]["optimizer"],
            "seeds": expected_seeds,
            "maxiter": next(iter(maxiter_values)),
            "tol": next(iter(tol_values)),
            "post_hoc_parameter_or_bound_changes_forbidden": True,
        },
        "input_sha256": input_sha256,
        "model_order": model_order,
        "ranking_metric": ranking_metric,
        "winner_by_seed": winners,
        "ranking_consensus": consensus,
        "robust_ranking_ready": True,
        "runtime_seconds_total": runtime_seconds,
        "residuals": {
            "rank_variation_preserved": True,
            "parameter_variation_preserved": True,
            "models_with_rank_variation": [
                item["model"] for item in summaries if item["rank_span"] > 0
            ],
        },
        "models": summaries,
        "runs": [
            {
                "seed": int(run["optimizer"]["seed"]),
                "commit_sha": run.get("commit_sha"),
                "runtime_seconds": run.get("runtime_seconds"),
                "optimizer": run["optimizer"],
                "rows": run["rows"],
            }
            for run in runs
        ],
        "interpretation": (
            "Complete predeclared-seed shadow comparison. The receipt exposes numerical "
            "variation and ranking residuals; it does not establish physical preference, "
            "independent replication, publication, or claim permission."
        ),
    }
    payload["receipt_sha256"] = _sha256_bytes(_canonical_json(payload))
    return payload, summaries


def summaries_to_csv(summaries: list[dict[str, Any]]) -> str:
    rows: list[dict[str, Any]] = []
    for item in summaries:
        row: dict[str, Any] = {
            "model": item["model"],
            "kind": item["kind"],
            "geometry": item["geometry"],
            "rank_min": item["rank_min"],
            "rank_median": item["rank_median"],
            "rank_max": item["rank_max"],
            "rank_span": item["rank_span"],
            "chi2_min": item["metrics"]["chi2"]["min"],
            "chi2_median": item["metrics"]["chi2"]["median"],
            "chi2_max": item["metrics"]["chi2"]["max"],
            "AICc_min": item["metrics"]["AICc"]["min"],
            "AICc_median": item["metrics"]["AICc"]["median"],
            "AICc_max": item["metrics"]["AICc"]["max"],
            "claim_allowed": False,
        }
        rows.append(row)
    buffer = StringIO()
    writer = csv.DictWriter(buffer, fieldnames=list(rows[0]))
    writer.writeheader()
    writer.writerows(rows)
    return buffer.getvalue()


def receipt_to_markdown(payload: dict[str, Any]) -> str:
    lines = [
        "# Model Family Multi-seed Shadow Receipt",
        "",
        f"- state: `{payload['state']}`",
        f"- seeds: `{payload['optimizer']['seeds']}`",
        f"- maxiter: `{payload['optimizer']['maxiter']}`",
        f"- tol: `{payload['optimizer']['tol']}`",
        f"- ranking metric: `{payload['ranking_metric']}`",
        f"- ranking consensus: `{payload['ranking_consensus']}`",
        f"- receipt SHA-256: `{payload['receipt_sha256']}`",
        "- claim_allowed: `false`",
        "- publication_effect: `NONE`",
        "",
        "| model | rank min | rank median | rank max | rank span | AICc median | chi2 median |",
        "|---|---:|---:|---:|---:|---:|---:|",
    ]
    for item in payload["models"]:
        lines.append(
            f"| {item['model']} | {item['rank_min']} | {item['rank_median']:.1f} | "
            f"{item['rank_max']} | {item['rank_span']} | "
            f"{item['metrics']['AICc']['median']:.9g} | "
            f"{item['metrics']['chi2']['median']:.9g} |"
        )
    lines.extend(
        [
            "",
            "## Boundary",
            "",
            payload["interpretation"],
            "",
            "Rank or parameter variation is preserved as Ω feedback. It is not renamed as success.",
        ]
    )
    return "\n".join(lines) + "\n"


def execute_multiseed(
    mode: str,
    maxiter: int,
    tol: float,
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    receipt_contract = load_receipt_contract()
    source_contract = load_contract()
    expected_mode = str(receipt_contract["execution"]["mode"])
    if mode != expected_mode:
        raise ValueError(f"receipt contract requires mode={expected_mode}, got {mode}")
    seeds = [int(value) for value in source_contract["execution_policy"]["predeclared_seeds"]]
    runs = [
        run_shadow_benchmark(mode=mode, seed=seed, maxiter=maxiter, tol=tol)
        for seed in seeds
    ]
    return build_receipt(runs, receipt_contract, source_contract)


def build_parser() -> argparse.ArgumentParser:
    source_contract = load_contract()
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", default="core", choices=("core",))
    parser.add_argument(
        "--maxiter",
        type=int,
        default=int(source_contract["execution_policy"]["default_maxiter"]),
    )
    parser.add_argument(
        "--tol",
        type=float,
        default=float(source_contract["execution_policy"]["default_tol"]),
    )
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT_DIR)
    return parser


def main() -> int:
    args = build_parser().parse_args()
    if args.maxiter < 1:
        raise ValueError("maxiter must be >= 1")
    if not math.isfinite(args.tol) or args.tol <= 0.0:
        raise ValueError("tol must be finite and > 0")
    payload, summaries = execute_multiseed(args.mode, args.maxiter, args.tol)
    output_dir = args.output_dir
    _atomic_write(
        output_dir / "model_family_multiseed_receipt.json",
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
    )
    _atomic_write(
        output_dir / "model_family_multiseed_summary.csv",
        summaries_to_csv(summaries),
    )
    _atomic_write(
        output_dir / "MODEL_FAMILY_MULTISEED_REPORT.md",
        receipt_to_markdown(payload),
    )
    print(receipt_to_markdown(payload))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
