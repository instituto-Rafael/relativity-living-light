#!/usr/bin/env python3
"""Runtime alignment layer for the RLL FASE 24.1 deterministic gate.

This module keeps the original gate API and epistemic states, but binds each
step to the executable contracts currently present in the repository. It also
packages current-run metrics, provenance, an artifact manifest, and a local
checksum verifier. Historical values are never used as fallback evidence.
"""

from __future__ import annotations

import csv
import hashlib
import json
import os
import platform
import re
import shutil
import subprocess
import sys
from dataclasses import replace
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

REPO_ROOT = Path(__file__).resolve().parents[1]
if str(REPO_ROOT) not in sys.path:
    sys.path.insert(0, str(REPO_ROOT))

from tools import rll_pipeline_deterministic as core

ROOT = core.ROOT
RESULTS = core.RESULTS
LOGS = core.LOGS
ARTIFACTS = core.ARTIFACTS
CURRENT_RUN = ARTIFACTS / "current_run"
ORIGINAL_WRITE_REPORT = core.write_report
ORIGINAL_WRITE_CHECKSUMS = core.write_checksums
ORIGINAL_RUN_STEP = core.run_step


def command(*argv: str, requires: Sequence[str] = ()) -> core.CommandSpec:
    return core.CommandSpec(tuple(argv), tuple(requires))


def _replace_step(number: int, **changes: object) -> None:
    core.STEPS = tuple(replace(step, **changes) if step.number == number else step for step in core.STEPS)


def align_step_contracts() -> None:
    py = sys.executable
    _replace_step(7, commands=(command(py, "tools/docs_inventory.py", requires=("tools/docs_inventory.py",)),), candidates=())
    _replace_step(8, commands=(command(
        py, "-m", "pytest", "-q",
        "tests/test_compute_rll_real_pipeline_contract.py",
        "tests/test_desi_dr2_bao_materialized.py",
        "tests/test_structure_d_robust_fit_matrix.py",
        "tests/test_import_raw_json_dataset_basic.py",
        "tests/test_import_raw_json_dataset_invalid.py",
        "tests/test_import_raw_json_dataset_rollback.py",
        "tests/test_import_raw_json_dataset_array.py",
        requires=(
            "tests/test_compute_rll_real_pipeline_contract.py",
            "tests/test_desi_dr2_bao_materialized.py",
            "tests/test_structure_d_robust_fit_matrix.py",
            "tests/test_import_raw_json_dataset_basic.py",
            "tests/test_import_raw_json_dataset_invalid.py",
            "tests/test_import_raw_json_dataset_rollback.py",
            "tests/test_import_raw_json_dataset_array.py",
        ),
    ),), candidates=())
    _replace_step(9, commands=(
        command(py, "tools/verify_real_source_signatures.py", requires=("tools/verify_real_source_signatures.py",)),
        command(py, "tools/real_data_materialization_audit.py", requires=("tools/real_data_materialization_audit.py",)),
    ), candidates=())
    _replace_step(10, commands=(command("bash", "-n", "tools/ci/real_data_workflow_policy.sh",
                                       requires=("tools/ci/real_data_workflow_policy.sh",)),), candidates=())
    _replace_step(11, commands=(command(py, "scripts/data_scan/build_raw_data_manifest_status.py",
                                       requires=("scripts/data_scan/build_raw_data_manifest_status.py",)),), candidates=())
    _replace_step(12, commands=(command(py, "scripts/data_scan/build_real_seed_ingestion_plan.py",
                                       requires=("scripts/data_scan/build_real_seed_ingestion_plan.py",)),), candidates=())
    _replace_step(13, commands=(command(
        "bash", "-lc",
        "COV_DIR=data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR; "
        "COV_FILE=\"$COV_DIR/Pantheon+SH0ES_STAT+SYS.cov\"; "
        "COV_SHA=\"$COV_FILE.sha256\"; "
        "cleanup_pantheon_covariance() { rm -f \"$COV_FILE\" \"$COV_SHA\"; }; "
        "trap cleanup_pantheon_covariance EXIT; "
        f"mkdir -p artifacts/linear/current_run && "
        f"{py} scripts/fetch_pantheon_covariance.py "
        "--output-dir data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR "
        "--receipt artifacts/linear/current_run/pantheon_covariance_materialization.json && "
        f"PYTHONPATH=products/rll-evidence-runner/src {py} -m rll_evidence.pantheon_fit_ascii "
        "--catalog data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat "
        "--covariance data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES_STAT+SYS.cov "
        "--output artifacts/linear/current_run/pantheon_fit_result.json "
        "--seeds 11,23,37,53,71 --maxiter 250 --integration-points 4096 --z-min 0.01",
        requires=(
            "scripts/fetch_pantheon_covariance.py",
            "products/rll-evidence-runner/src/rll_evidence/pantheon_fit_ascii.py",
            "data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat",
        ),
    ),), candidates=())
    _replace_step(15, commands=(command(
        py, "scripts/compute_rll_real_pipeline.py",
        "--output-dir", "artifacts/linear/real-data-contract",
        "--real-data-dir", "data/real", "--data-source", "repo",
        requires=("scripts/compute_rll_real_pipeline.py", "data/real"),
    ),), candidates=())
    _replace_step(16, commands=(command(
        py, "scripts/compute_weff_cpl_mapping.py",
        "--out-csv", "artifacts/linear/current_run/weff_cpl_mapping.csv",
        "--out-json", "artifacts/linear/current_run/weff_cpl_mapping.json",
        "--w0", "-0.838", "--wa", "-0.62",
        requires=("scripts/compute_weff_cpl_mapping.py",),
    ),), candidates=())
    _replace_step(17, commands=(command(
        py, "scripts/slingshot_zt_falsification.py",
        "--protocol", "protocols/05_slingshot_zt_falsification.yml",
        "--out-dir", "artifacts/linear/current_run/zt_scan",
        "--bao", "data/real/cosmology/desi_dr2_bao_primary_points.csv",
        "--hz", "data/real/Hz_data_real.csv",
        requires=(
            "scripts/slingshot_zt_falsification.py",
            "protocols/05_slingshot_zt_falsification.yml",
            "data/real/cosmology/desi_dr2_bao_primary_points.csv",
            "data/real/Hz_data_real.csv",
        ),
    ),), candidates=())
    _replace_step(18, commands=(command(
        py, "scripts/run_h0_grid_expansion.py",
        "--bao", "data/real/cosmology/desi_dr2_bao_primary_points.csv",
        "--hz", "data/real/Hz_data_real.csv",
        "--out-json", "artifacts/linear/current_run/h0_grid_summary.json",
        "--out-csv", "artifacts/linear/current_run/h0_grid_scan.csv",
        "--h0-min", "64.0", "--h0-max", "74.0", "--h0-step", "0.5",
        "--omega-m", "0.315", "--omega-s0", "0.05", "--zt", "1.0", "--wt", "0.3",
        requires=("scripts/run_h0_grid_expansion.py",),
    ),), candidates=())
    inference = command(
        py, "-m", "data.pipelines.structure_d.run_all",
        "--profile", "structure_d_real_validation", "--bayes", "--bayes-mode", "inference",
        "--bayes-seed", "42", "--bayes-nwalkers", "32", "--bayes-nsteps", "1000", "--bayes-nlive", "200",
        requires=("data/pipelines/structure_d/run_all.py",),
    )
    bic_proxy = command(
        py, "-m", "data.pipelines.structure_d.run_all",
        "--profile", "structure_d_real_validation", "--bayes", "--bayes-mode", "bic_proxy", "--bayes-seed", "42",
        requires=("data/pipelines/structure_d/run_all.py",),
    )
    _replace_step(21, commands=(
        command(py, "tools/rll_pipeline_fase24_1_runtime.py", "--prepare-real-bayes",
                requires=("tools/rll_pipeline_fase24_1_runtime.py",)),
        inference,
        command(py, "tools/rll_pipeline_fase24_1_runtime.py", "--validate-real-bayes-inference",
                requires=("tools/rll_pipeline_fase24_1_runtime.py",)),
    ), candidates=())
    _replace_step(22, commands=(
        command(py, "tools/rll_pipeline_fase24_1_runtime.py", "--prepare-real-bayes",
                requires=("tools/rll_pipeline_fase24_1_runtime.py",)),
        bic_proxy,
        command(py, "tools/rll_pipeline_fase24_1_runtime.py", "--materialize-real-bic-proxy",
                requires=("tools/rll_pipeline_fase24_1_runtime.py", "results/structure_d/model_comparison.csv")),
    ), candidates=())
    _replace_step(25, commands=(command(
        py, "scripts/compute_rll_real_pipeline.py",
        "--output-dir", "artifacts/linear/current_run/rll-real-pipeline",
        "--real-data-dir", "data/real", "--data-source", "repo",
        requires=("scripts/compute_rll_real_pipeline.py", "data/real"),
    ),), candidates=())
    _replace_step(26, commands=(command(
        py, "tools/iml/iml_pipeline.py", "--input", "data/iml/daise_input.json",
        "--output", "artifacts/linear/current_run/iml_artifact.json", "--steps", "42",
        requires=("tools/iml/iml_pipeline.py", "data/iml/daise_input.json"),
    ),), candidates=())
    _replace_step(27, commands=(
        command(py, "scripts/validate_formulas_manifest.py", requires=("scripts/validate_formulas_manifest.py",)),
        command(py, "tools/formula_artifact_builder.py", "--root", ".",
                "--outdir", "artifacts/linear/current_run/formulas",
                requires=("tools/formula_artifact_builder.py",)),
    ), candidates=())
    _replace_step(28, commands=(
        command(py, "tools/rll_pipeline_fase24_1_runtime.py", "--materialize-balance-input",
                requires=("tools/rll_pipeline_fase24_1_runtime.py", "results/structure_d/model_comparison_real.csv")),
        command(py, "scripts/rll_balance_report.py",
                "--input", "artifacts/linear/current_run/structure_d_real_metrics.json",
                "--output-md", "artifacts/linear/current_run/rll_balance_report.md",
                "--output-json", "artifacts/linear/current_run/rll_balance_report.json",
                "--metric", "bic", requires=("scripts/rll_balance_report.py",)),
    ), candidates=())
    _replace_step(29, commands=(
        command(py, "scripts/run_desi_dha_pipeline.py", "--output", "artifacts/linear/current_run/desi_dha_pipeline.json",
                requires=("scripts/run_desi_dha_pipeline.py",)),
        command(py, "scripts/export_dha_forecast.py", requires=("scripts/export_dha_forecast.py",)),
    ), candidates=())


def _structure_d_results() -> Path:
    return ROOT / "results" / "structure_d"


def prepare_real_bayes() -> int:
    out = _structure_d_results()
    out.mkdir(parents=True, exist_ok=True)
    for name in (
        "bayes_evidence_inference.csv",
        "bayes_evidence_bic_proxy.csv",
        "bayes_factor_interpretation.csv",
    ):
        (out / name).unlink(missing_ok=True)
    return 0


def validate_real_bayes_inference() -> int:
    out = _structure_d_results()
    contract_path = out / "reproduction_contract.json"
    evidence_path = out / "bayes_evidence_inference.csv"
    contract: dict[str, object] = {}
    if contract_path.is_file():
        try:
            contract = json.loads(contract_path.read_text(encoding="utf-8"))
        except json.JSONDecodeError:
            contract = {}
    profile = contract.get("profile")
    bayes_enabled = contract.get("bayes_enabled") is True
    mode = contract.get("bayes_mode")
    verified = (
        profile == "structure_d_real_validation"
        and bayes_enabled
        and mode == "inference"
        and evidence_path.is_file()
        and evidence_path.stat().st_size > 0
    )
    payload = {
        "schema_version": "rll.structure_d.real_bayes_inference_status.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "state": "VERIFIED" if verified else "TOKEN_VAZIO",
        "claim_allowed": False,
        "profile": profile,
        "bayes_enabled": bayes_enabled,
        "bayes_mode": mode,
        "evidence_path": core.rel(evidence_path),
        "reason": None if verified else (
            "Structure-D real profile currently returns before optional Bayesian inference; "
            "a completed real-data MCMC/nested-sampling artifact was not materialized."
        ),
    }
    CURRENT_RUN.mkdir(parents=True, exist_ok=True)
    status_path = CURRENT_RUN / "real_bayes_inference_status.json"
    status_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0 if verified else 3


def materialize_real_bic_proxy() -> int:
    out = _structure_d_results()
    source = out / "model_comparison.csv"
    if not source.is_file():
        print(f"TOKEN_VAZIO: missing {source}")
        return 3
    rows = list(csv.DictReader(source.read_text(encoding="utf-8").splitlines()))
    baseline = next((row for row in rows if str(row.get("model", "")).strip().lower() == "lcdm"), None)
    candidate = next((row for row in rows if str(row.get("model", "")).strip().lower().startswith("rll")), None)
    if baseline is None or candidate is None:
        print("TOKEN_VAZIO: LCDM/RLL rows absent from real model comparison")
        return 3
    try:
        bic_baseline = float(baseline["BIC"])
        bic_candidate = float(candidate["BIC"])
    except (KeyError, TypeError, ValueError):
        print("TOKEN_VAZIO: BIC columns are not numeric")
        return 3
    delta_bic = bic_candidate - bic_baseline
    log_bayes_factor = -0.5 * delta_bic
    evidence_path = out / "bayes_evidence_bic_proxy.csv"
    interpretation_path = out / "bayes_factor_interpretation.csv"
    with evidence_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.DictWriter(handle, fieldnames=(
            "baseline_model", "candidate_model", "bic_baseline", "bic_candidate",
            "delta_bic_candidate_minus_baseline", "log_bayes_factor", "method", "claim_allowed",
        ))
        writer.writeheader()
        writer.writerow({
            "baseline_model": baseline["model"],
            "candidate_model": candidate["model"],
            "bic_baseline": bic_baseline,
            "bic_candidate": bic_candidate,
            "delta_bic_candidate_minus_baseline": delta_bic,
            "log_bayes_factor": log_bayes_factor,
            "method": "BIC proxy: ln(B10) ≈ -ΔBIC/2",
            "claim_allowed": "false",
        })
    shutil.copy2(evidence_path, interpretation_path)
    payload = {
        "schema_version": "rll.structure_d.real_bic_proxy_status.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "state": "VERIFIED",
        "claim_allowed": False,
        "baseline_model": baseline["model"],
        "candidate_model": candidate["model"],
        "delta_bic_candidate_minus_baseline": delta_bic,
        "log_bayes_factor": log_bayes_factor,
        "method": "BIC proxy only; not MCMC or nested sampling",
        "source": core.rel(source),
    }
    CURRENT_RUN.mkdir(parents=True, exist_ok=True)
    (CURRENT_RUN / "real_bic_proxy_status.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(json.dumps(payload, ensure_ascii=False, indent=2))
    return 0


def materialize_balance_input() -> int:
    source = ROOT / "results" / "structure_d" / "model_comparison_real.csv"
    target = CURRENT_RUN / "structure_d_real_metrics.json"
    if not source.is_file():
        print(f"TOKEN_VAZIO: missing {source}")
        return 3
    models: list[dict[str, object]] = []
    for row in csv.DictReader(source.read_text(encoding="utf-8").splitlines()):
        name = str(row.get("model") or "").strip()
        if not name:
            continue
        item: dict[str, object] = {"model": "RLL" if name.lower().startswith("rll") else name.upper()}
        for source_key, target_key in (("chi2", "chi2"), ("AIC", "aic"), ("BIC", "bic")):
            raw = row.get(source_key)
            try:
                item[target_key] = float(raw) if raw not in (None, "") else None
            except ValueError:
                item[target_key] = None
        models.append(item)
    if not models:
        print("TOKEN_VAZIO: no models parsed")
        return 3
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps({"models": models, "claim_allowed": False}, indent=2) + "\n", encoding="utf-8")
    print(target)
    return 0


def nested_get(payload: object, dotted_key: str) -> object | None:
    current = payload
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def find_json_metric(candidates: Sequence[tuple[str, Sequence[str]]]) -> dict[str, object]:
    inspected: list[str] = []
    for path_text, keys in candidates:
        inspected.append(path_text)
        path = ROOT / path_text
        if not path.is_file():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for key in keys:
            value = nested_get(payload, key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return {"state": "VERIFIED", "value": float(value), "source": path_text, "key": key}
    return {"state": "TOKEN_VAZIO", "value": None, "source": None, "key": None, "inspected": inspected}


def find_csv_metric(candidates: Sequence[tuple[str, Sequence[str]]]) -> dict[str, object]:
    inspected: list[str] = []
    for path_text, keys in candidates:
        inspected.append(path_text)
        path = ROOT / path_text
        if not path.is_file():
            continue
        for index, row in enumerate(csv.DictReader(path.read_text(encoding="utf-8").splitlines())):
            for key in keys:
                try:
                    value = float(row.get(key, ""))
                except (TypeError, ValueError):
                    continue
                return {"state": "VERIFIED", "value": value, "source": path_text, "key": f"row[{index}].{key}"}
    return {"state": "TOKEN_VAZIO", "value": None, "source": None, "key": None, "inspected": inspected}


def materialize_pantheon_metrics() -> None:
    log = LOGS / "step13_pantheon_fit.log"
    result = CURRENT_RUN / "pantheon_fit_result.json"
    output = RESULTS / "pantheon_plus_resultado_real.json"
    payload: dict[str, object] = {
        "schema_version": "rll.pantheon.current-run.v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "claim_allowed": False,
        "source_log": core.rel(log),
        "source_result": core.rel(result),
        "delta_aic": None,
        "chi2_red_rll": None,
        "models": {},
    }
    models: dict[str, dict[str, float]] = {}
    if result.is_file():
        try:
            raw = json.loads(result.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            raw = {}
        rows = raw.get("rows", []) if isinstance(raw, dict) else []
        if isinstance(rows, list):
            for row in rows:
                if not isinstance(row, dict):
                    continue
                name = str(row.get("model", "")).strip()
                if not name:
                    continue
                try:
                    chi2 = float(row["chi2"]); aic = float(row["AIC"])
                    dof = float(row["dof"]); k = float(row["k"])
                except (KeyError, TypeError, ValueError):
                    continue
                models[name] = {"chi2": chi2, "k": k, "dof": dof,
                    "chi2_red": chi2 / dof if dof > 0 else float("nan"), "aic": aic}
        baseline = next((v for k, v in models.items() if "lcdm" in k.lower()), None)
        candidate = next((v for k, v in models.items() if "rll" in k.lower()), None)
        if baseline is not None and candidate is not None:
            payload["state"] = "VERIFIED"
            payload["delta_aic"] = candidate["aic"] - baseline["aic"]
            payload["chi2_red_rll"] = candidate["chi2_red"]
            payload["models"] = models
            output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
            return
    if log.is_file():
        pattern = re.compile(r"^(lcdm|cpl|rll_original|rll_optionA)\s+([0-9.eE+-]+)\s+(\d+)\s+([0-9.eE+-]+)\s+([0-9.eE+-]+)\s*$", re.MULTILINE)
        for match in pattern.finditer(log.read_text(encoding="utf-8", errors="replace")):
            name, chi2, k, reduced, aic = match.groups()
            models[name] = {"chi2": float(chi2), "k": float(k), "chi2_red": float(reduced), "aic": float(aic)}
    if "lcdm" in models and "rll_original" in models:
        payload["state"] = "VERIFIED"
        payload["delta_aic"] = models["rll_original"]["aic"] - models["lcdm"]["aic"]
        payload["chi2_red_rll"] = models["rll_original"]["chi2_red"]
    else:
        payload["state"] = "TOKEN_VAZIO"
        payload["reason"] = "LCDM/RLL current-run rows not parsed"
    payload["models"] = models
    output.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def _copy_if_present(source_text: str, target_text: str | None = None) -> None:
    source = ROOT / source_text
    if not source.is_file():
        return
    target = CURRENT_RUN / (target_text or source.name)
    target.parent.mkdir(parents=True, exist_ok=True)
    shutil.copy2(source, target)


def collect_current_outputs() -> None:
    for source, target in (
        ("results/desi_dr2_bao_covariance_chi2.json", None),
        ("results/structure_d/model_comparison.csv", "structure_d/model_comparison.csv"),
        ("results/structure_d/model_comparison_real.csv", "structure_d/model_comparison_real.csv"),
        ("results/structure_d/model_comparison_real_fit_metadata.json", "structure_d/model_comparison_real_fit_metadata.json"),
        ("results/structure_d/bayes_evidence_inference.csv", "structure_d/bayes_evidence_inference.csv"),
        ("results/structure_d/bayes_evidence_bic_proxy.csv", "structure_d/bayes_evidence_bic_proxy.csv"),
        ("results/structure_d/bayes_factor_interpretation.csv", "structure_d/bayes_factor_interpretation.csv"),
        ("results/structure_d/reproduction_contract.json", "structure_d/reproduction_contract.json"),
        ("results/RELATORIO_VALIDACAO.md", None),
        ("results/dha/fisher_forecast_reference.json", "dha/fisher_forecast_reference.json"),
        ("results/audit/real_source_signature_verification.md", "audit/real_source_signature_verification.md"),
        ("results/audit/real_data_materialization_audit.md", "audit/real_data_materialization_audit.md"),
        ("results/audit/real_data_materialization_audit.json", "audit/real_data_materialization_audit.json"),
    ):
        _copy_if_present(source, target)


def evaluate(metric_id: str, value: float | None) -> str:
    if value is None:
        return "TOKEN_VAZIO"
    return {
        "F-COS-01": value < 10.0,
        "F-COS-02": value < 1.05,
        "F-COS-03": 0.5 <= value <= 1.5,
        "F-COS-04": value > -5.0,
        "F-COS-05": value < 150.0,
    }[metric_id] and "PASS" or "FAIL"


def build_contract(mode: str) -> dict[str, object]:
    materialize_pantheon_metrics()
    collect_current_outputs()
    specs = {
        "F-COS-01": ("ΔAIC(RLL−ΛCDM)", "< 10", find_json_metric((("results/linear/pantheon_plus_resultado_real.json", ("delta_aic",)),))),
        "F-COS-02": ("χ² reduzido Pantheon+ RLL", "< 1.05", find_json_metric((("results/linear/pantheon_plus_resultado_real.json", ("chi2_red_rll",)),))),
        "F-COS-03": ("redshift de transição z_t", "0.5 ≤ z_t ≤ 1.5", find_json_metric((("artifacts/linear/current_run/zt_scan/summary.json", ("assessment.best.zt_bao", "assessment.best.zt_total")),))),
        "F-COS-04": ("ln(B10)", "> -5", find_json_metric((
            ("artifacts/linear/current_run/real_bic_proxy_status.json", ("log_bayes_factor",)),
        ))),
        "F-COS-05": ("χ² DESI nominal", "< 150", find_json_metric((("results/desi_dr2_bao_covariance_chi2.json", ("results.rll.chi2_bao_desi_dr2",)),))),
    }
    rows: list[dict[str, object]] = []
    for metric_id, (label, threshold, metric) in specs.items():
        raw = metric.get("value")
        value = float(raw) if isinstance(raw, (int, float)) and not isinstance(raw, bool) else None
        rows.append({"id": metric_id, "label": label, "threshold": threshold,
                     "state": metric["state"], "value": value, "outcome": evaluate(metric_id, value),
                     "source": metric.get("source"), "key": metric.get("key"),
                     "inspected": metric.get("inspected", [])})
    contract = {
        "schema_version": "rll.fase24.1.contract.v2",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "claim_allowed": False,
        "claim_boundary": "Current-run evidence only; falsifier PASS does not establish global validation or superiority.",
        "falsifiers": rows,
    }
    (RESULTS / "CONTRATO_FALSIFICADORES_DETERMINISTICO.json").write_text(json.dumps(contract, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    md = ["# CONTRATO DE FALSIFICADORES — FASE 24.1", "", "- `claim_allowed=false`", "",
          "| ID | Métrica | Threshold | Evidência | Valor | Resultado | Fonte |",
          "|---|---|---|---|---:|---|---|"]
    for row in rows:
        value_text = "TOKEN_VAZIO" if row["value"] is None else f"{row['value']:.8g}"
        md.append(f"| {row['id']} | {row['label']} | `{row['threshold']}` | `{row['state']}` | {value_text} | `{row['outcome']}` | `{row['source'] or 'TOKEN_VAZIO'}` |")
    (RESULTS / "CONTRATO_FALSIFICADORES_DETERMINISTICO.md").write_text("\n".join(md) + "\n", encoding="utf-8")
    return contract


def run_step(step: core.Step, selected_phases: set[int], mode: str) -> core.StepResult:
    result = ORIGINAL_RUN_STEP(step, selected_phases, mode)
    if step.number == 21 and result.status == "FAIL" and result.exit_code == 3:
        status_path = CURRENT_RUN / "real_bayes_inference_status.json"
        try:
            payload = json.loads(status_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            payload = {}
        if payload.get("state") == "TOKEN_VAZIO":
            return replace(result, status="TOKEN_VAZIO", exit_code=None,
                detail="inferência Bayes real não materializada; estado auditável TOKEN_VAZIO")
    return result


def gate_decision(mode: str, results: Sequence[core.StepResult], contract: dict[str, object]) -> dict[str, object]:
    blocking = [item for item in results if item.critical and item.status in {"FAIL", "TOKEN_VAZIO"}]
    token_vazio: list[str] = []
    failures: list[str] = []
    if mode in core.SCIENCE_MODES:
        rows = contract.get("falsifiers", [])
        if isinstance(rows, list):
            token_vazio = [str(row.get("id")) for row in rows if isinstance(row, dict) and row.get("state") == "TOKEN_VAZIO"]
            failures = [str(row.get("id")) for row in rows if isinstance(row, dict) and row.get("outcome") == "FAIL"]
    return {
        "status": "BLOCKED" if blocking or token_vazio or failures else "OK",
        "claim_allowed": False,
        "blocking_steps": [{"step": f"{item.number:02d}", "name": item.name, "status": item.status, "detail": item.detail} for item in blocking],
        "metric_token_vazio": token_vazio,
        "falsifier_failures": failures,
    }


def write_report(mode: str, results: Sequence[core.StepResult], contract: dict[str, object], decision: dict[str, object]) -> None:
    ORIGINAL_WRITE_REPORT(mode, results, contract, decision)
    failures = decision.get("falsifier_failures", [])
    if failures:
        with (RESULTS / "RELATORIO_LINEAR_FINAL.md").open("a", encoding="utf-8") as handle:
            handle.write("\n## Falsificadores reprovados\n\n")
            handle.write("- " + ", ".join(f"`{item}`" for item in failures) + "\n")


def _git(*args: str) -> str | None:
    try:
        return subprocess.check_output(("git", *args), cwd=ROOT, text=True, stderr=subprocess.DEVNULL).strip() or None
    except (OSError, subprocess.CalledProcessError):
        return None


def write_provenance() -> None:
    decision_path = RESULTS / "gate_decision.json"
    decision = json.loads(decision_path.read_text(encoding="utf-8")) if decision_path.is_file() else {}
    keys = ("GITHUB_ACTION", "GITHUB_ACTOR", "GITHUB_EVENT_NAME", "GITHUB_JOB", "GITHUB_REF", "GITHUB_REF_NAME",
            "GITHUB_REPOSITORY", "GITHUB_RUN_ATTEMPT", "GITHUB_RUN_ID", "GITHUB_RUN_NUMBER", "GITHUB_SHA",
            "GITHUB_WORKFLOW", "GITHUB_WORKFLOW_REF", "RUNNER_ARCH", "RUNNER_NAME", "RUNNER_OS")
    payload = {
        "schema_version": "rll.fase24.1.provenance.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "claim_allowed": False,
        "gate_status": decision.get("status"),
        "repository": os.environ.get("GITHUB_REPOSITORY") or _git("config", "--get", "remote.origin.url"),
        "commit_sha": os.environ.get("GITHUB_SHA") or _git("rev-parse", "HEAD"),
        "branch_or_ref": os.environ.get("GITHUB_REF_NAME") or _git("branch", "--show-current"),
        "python": {"version": sys.version, "executable": sys.executable, "implementation": platform.python_implementation()},
        "platform": {"system": platform.system(), "release": platform.release(), "machine": platform.machine()},
        "github": {key: os.environ.get(key) for key in keys if os.environ.get(key)},
        "boundaries": {"claim_boundary": os.environ.get("CLAIM_BOUNDARY"),
                       "canonical_real_data_workflow": os.environ.get("CANONICAL_REAL_DATA_WORKFLOW"),
                       "synthetic_boundary": os.environ.get("SYNTHETIC_BOUNDARY")},
    }
    (ARTIFACTS / "PROVENANCE.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    try:
        freeze = subprocess.check_output((sys.executable, "-m", "pip", "freeze"), text=True, stderr=subprocess.STDOUT)
    except (OSError, subprocess.CalledProcessError) as exc:
        freeze = f"TOKEN_VAZIO: pip freeze failed: {exc}\n"
    (ARTIFACTS / "PYTHON_ENVIRONMENT.txt").write_text(freeze, encoding="utf-8")


def write_verifier() -> None:
    text = '''#!/usr/bin/env python3
import hashlib
from pathlib import Path
root = Path(__file__).resolve().parents[2]
checksums = root / "results" / "linear" / "CHECKSUMS.sha256"
if not checksums.is_file():
    raise SystemExit("CHECKSUMS.sha256 absent")
failures = []
for line in checksums.read_text(encoding="utf-8").splitlines():
    if not line.strip():
        continue
    digest, name = line.split("  ", 1)
    path = root / name
    if not path.is_file():
        failures.append("MISSING " + name)
    elif hashlib.sha256(path.read_bytes()).hexdigest() != digest:
        failures.append("MISMATCH " + name)
if failures:
    print("\\n".join(failures))
    raise SystemExit(1)
print("RLL artifact checksums: PASS")
'''
    path = ARTIFACTS / "VERIFY_ARTIFACT.py"
    path.write_text(text, encoding="utf-8")
    path.chmod(0o755)


def write_manifest() -> None:
    files: list[dict[str, object]] = []
    for base in (RESULTS, LOGS, ARTIFACTS):
        for path in sorted(base.rglob("*")):
            if not path.is_file() or path.name in {"CHECKSUMS.sha256", "MANIFEST.json"}:
                continue
            data = path.read_bytes()
            files.append({"path": core.rel(path), "bytes": len(data), "sha256": hashlib.sha256(data).hexdigest()})
    payload = {"schema_version": "rll.fase24.1.artifact-manifest.v1",
               "generated_at": datetime.now(timezone.utc).isoformat(),
               "claim_allowed": False, "file_count": len(files), "files": files}
    (ARTIFACTS / "MANIFEST.json").write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def write_checksums() -> None:
    CURRENT_RUN.mkdir(parents=True, exist_ok=True)
    collect_current_outputs()
    write_provenance()
    write_verifier()
    write_manifest()
    ORIGINAL_WRITE_CHECKSUMS()


def install() -> None:
    CURRENT_RUN.mkdir(parents=True, exist_ok=True)
    align_step_contracts()
    core.run_step = run_step
    core.build_contract = build_contract
    core.gate_decision = gate_decision
    core.write_report = write_report
    core.write_checksums = write_checksums


def main() -> int:
    if "--prepare-real-bayes" in sys.argv:
        return prepare_real_bayes()
    if "--validate-real-bayes-inference" in sys.argv:
        return validate_real_bayes_inference()
    if "--materialize-real-bic-proxy" in sys.argv:
        return materialize_real_bic_proxy()
    if "--materialize-balance-input" in sys.argv:
        CURRENT_RUN.mkdir(parents=True, exist_ok=True)
        return materialize_balance_input()
    install()
    return core.main()


if __name__ == "__main__":
    raise SystemExit(main())
