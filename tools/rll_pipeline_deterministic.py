#!/usr/bin/env python3
"""RLL FASE 24.1 deterministic linear pipeline gate.

Logical states are never conflated:
- OK: command executed and returned zero.
- FAIL: command executed and returned non-zero.
- TOKEN_VAZIO: required executable/input/evidence was not found.
- SKIP: step is outside the selected execution mode.

The gate never injects historical scientific values as current-run evidence.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import os
import subprocess
import sys
import time
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable, Sequence

ROOT = Path(__file__).resolve().parents[1]
RESULTS = ROOT / "results" / "linear"
LOGS = ROOT / "logs" / "linear"
ARTIFACTS = ROOT / "artifacts" / "linear"

VALID_STATES = {"OK", "FAIL", "TOKEN_VAZIO", "SKIP"}
SCIENCE_MODES = {"completo", "apenas_ciencia"}
PHASES_BY_MODE = {
    "dry_run": {0},
    "apenas_dados": {0, 1},
    "apenas_ciencia": {0, 2, 3},
    "apenas_governanca": {0, 6},
    "completo": {0, 1, 2, 3, 4, 5, 6},
}


@dataclass(frozen=True)
class CommandSpec:
    argv: tuple[str, ...]
    requires: tuple[str, ...] = ()


@dataclass(frozen=True)
class Step:
    number: int
    name: str
    phase: int
    origin: str
    critical: bool
    commands: tuple[CommandSpec, ...] = ()
    candidates: tuple[CommandSpec, ...] = ()
    handler: str | None = None


@dataclass
class StepResult:
    number: int
    name: str
    phase: int
    origin: str
    critical: bool
    status: str
    exit_code: int | None
    duration_s: float
    command: str
    detail: str
    log_path: str


def cmd(*argv: str, requires: Sequence[str] = ()) -> CommandSpec:
    return CommandSpec(tuple(argv), tuple(requires))


STEPS: tuple[Step, ...] = (
    Step(2, "instalar_dependencias", 0, "RLL_SCIENTIFIC.yml", True, handler="dependencies"),
    Step(3, "validar_yaml_syntax", 0, "yml-syntax-validation.yml", True, handler="yaml"),
    Step(4, "audit_workflows", 0, "yml-syntax-validation.yml", True,
         commands=(cmd(sys.executable, "tools/audit_github_workflows.py", "--strict",
                       requires=("tools/audit_github_workflows.py",)),)),
    Step(5, "validar_schema_contracts", 0, "validate-schema-contracts.yml", True,
         candidates=(
             cmd(sys.executable, "tools/validate_schema_contracts.py",
                 requires=("tools/validate_schema_contracts.py",)),
             cmd(sys.executable, "scripts/validate_schema_contracts.py",
                 requires=("scripts/validate_schema_contracts.py",)),
         )),
    Step(6, "claim_boundary_gate", 0, "claim-boundary-quality-gates.yml", True,
         commands=(cmd(sys.executable, "tools/validate_claim_allowed_gate.py",
                       requires=("tools/validate_claim_allowed_gate.py",)),)),
    Step(7, "docs_inventory", 1, "repo-real-inventory.yml", False,
         commands=(cmd(sys.executable, "scripts/build_repo_real_inventory.py",
                       requires=("scripts/build_repo_real_inventory.py",)),)),
    Step(8, "validate_data_contract", 1, "real-data-contract-ci.yml", True,
         candidates=(
             cmd(sys.executable, "tools/validate_real_data_contract.py",
                 requires=("tools/validate_real_data_contract.py",)),
             cmd(sys.executable, "-m", "pytest", "-q", "tests", "-k", "real_data_contract",
                 requires=("tests",)),
         )),
    Step(9, "verify_real_sources", 1, "real-data-complete-execution.yml", True,
         commands=(cmd(sys.executable, "scripts/verify_real_source_signatures.py",
                       requires=("scripts/verify_real_source_signatures.py",)),)),
    Step(10, "data_audit", 1, "real-data-complete-execution.yml", True,
         commands=(cmd("bash", "tools/ci/real_data_workflow_policy.sh",
                       requires=("tools/ci/real_data_workflow_policy.sh",)),)),
    Step(11, "raw_manifest_status", 1, "raw-data-manifest-status.yml", False,
         commands=(cmd(sys.executable, "scripts/build_raw_data_manifest_status.py",
                       requires=("scripts/build_raw_data_manifest_status.py",)),)),
    Step(12, "real_seed_ingestion", 1, "real-seed-ingestion-plan.yml", False,
         commands=(cmd(sys.executable, "scripts/build_real_seed_ingestion_plan.py",
                       requires=("scripts/build_real_seed_ingestion_plan.py",)),)),
    Step(13, "pantheon_fit", 2, "rll-validacao-cientifica-completa.yml", True,
         commands=(cmd(sys.executable, "scripts/pantheon/run_rll_vs_pantheon.py",
                       requires=("scripts/pantheon/run_rll_vs_pantheon.py",)),)),
    Step(14, "desi_bao_covariance", 2, "desi-dr2-bao-validation.yml", True,
         commands=(cmd(sys.executable, "scripts/check_desi_dr2_bao_covariance.py",
                       requires=("scripts/check_desi_dr2_bao_covariance.py",)),)),
    Step(15, "desi_bao_nominal", 2, "rll-validacao-cientifica-completa.yml", True,
         commands=(cmd(sys.executable, "scripts/compute_rll_real_pipeline.py", "--desi-only",
                       requires=("scripts/compute_rll_real_pipeline.py",)),)),
    Step(16, "weff_cpl_mapping", 2, "rll-validacao-cientifica-completa.yml", False,
         commands=(cmd(sys.executable, "scripts/compute_weff_cpl_mapping.py",
                       "--w0", "-0.838", "--wa", "-0.62",
                       requires=("scripts/compute_weff_cpl_mapping.py",)),)),
    Step(17, "zt_falsification", 2, "rll-validacao-cientifica-completa.yml", True,
         commands=(cmd(sys.executable, "scripts/slingshot_zt_falsification.py",
                       requires=("scripts/slingshot_zt_falsification.py",)),)),
    Step(18, "h0_grid_scan", 2, "rll-validacao-cientifica-completa.yml", False,
         commands=(cmd(sys.executable, "scripts/run_h0_grid_expansion.py",
                       requires=("scripts/run_h0_grid_expansion.py",)),)),
    Step(19, "rll_ci_validation", 3, "RLL-CI.yml", False,
         commands=(
             cmd(sys.executable, "-m", "validation.run_lcdm", requires=("validation/run_lcdm.py",)),
             cmd(sys.executable, "-m", "validation.run_rll", requires=("validation/run_rll.py",)),
             cmd(sys.executable, "-m", "validation.compare_models", requires=("validation/compare_models.py",)),
             cmd(sys.executable, "-m", "validation.check_falsification",
                 requires=("validation/check_falsification.py",)),
         )),
    Step(20, "rll_scientific_full", 3, "RLL_SCIENTIFIC.yml", False,
         commands=(
             cmd(sys.executable, "validation/load_data.py", requires=("validation/load_data.py",)),
             cmd(sys.executable, "validation/run_lcdm.py", requires=("validation/run_lcdm.py",)),
             cmd(sys.executable, "validation/run_rll.py", requires=("validation/run_rll.py",)),
             cmd(sys.executable, "validation/compare_models.py", requires=("validation/compare_models.py",)),
             cmd(sys.executable, "validation/plot_results.py", requires=("validation/plot_results.py",)),
         )),
    Step(21, "joint_mcmc_p0", 3, "rll-validacao-cientifica-completa.yml", True,
         candidates=(
             cmd(sys.executable, "-m", "data.pipelines.structure_d.run_all",
                 "--bayes", "--bayes-mode", "inference",
                 "--bayes-nwalkers", "32", "--bayes-nsteps", "1000",
                 requires=("data/pipelines/structure_d/run_all.py",)),
             cmd(sys.executable, "data/pipelines/structure_d/run_all.py",
                 "--bayes", "--bayes-mode", "inference",
                 requires=("data/pipelines/structure_d/run_all.py",)),
         )),
    Step(22, "bayes_factor_p0", 3, "rll-validacao-cientifica-completa.yml", True,
         candidates=(
             cmd(sys.executable, "scripts/slingshot_zt_falsification.py", "--bayes-factor",
                 requires=("scripts/slingshot_zt_falsification.py",)),
             cmd(sys.executable, "src/run_full_analysis.py",
                 requires=("src/run_full_analysis.py",)),
         )),
    Step(23, "structure_d_real", 3, "real-data-complete-execution.yml", True,
         candidates=(
             cmd(sys.executable, "-m", "data.pipelines.structure_d.run_all_real",
                 requires=("data/pipelines/structure_d/run_all_real.py",)),
             cmd(sys.executable, "data/pipelines/structure_d/run_all_real.py",
                 requires=("data/pipelines/structure_d/run_all_real.py",)),
         )),
    Step(24, "validacao_real", 4, "validacao_real.yml", False,
         commands=(
             cmd(sys.executable, "validacao_real/fetch_real_data.py",
                 requires=("validacao_real/fetch_real_data.py",)),
             cmd(sys.executable, "validacao_real/compute_validation.py",
                 requires=("validacao_real/compute_validation.py",)),
             cmd(sys.executable, "validacao_real/make_figures.py",
                 requires=("validacao_real/make_figures.py",)),
             cmd(sys.executable, "validacao_real/render_report.py",
                 requires=("validacao_real/render_report.py",)),
         )),
    Step(25, "rll_pipeline_compute", 4, "rll-data-pipeline.yml", False,
         candidates=(
             cmd(sys.executable, "scripts/compute_rll_real_pipeline.py",
                 requires=("scripts/compute_rll_real_pipeline.py",)),
             cmd(sys.executable, "scripts/rll_pipeline.py",
                 "--dataset-group", "all", "--mode", "compute",
                 requires=("scripts/rll_pipeline.py",)),
         )),
    Step(26, "iml_pipeline", 4, "iml_artifact.yml", False,
         commands=(cmd(
             sys.executable, "tools/iml/iml_pipeline.py",
             "--input", "data/iml/daise_input.json",
             "--output", "artifacts/iml/iml_artifact.json",
             "--steps", "42",
             requires=("tools/iml/iml_pipeline.py", "data/iml/daise_input.json"),
         ),)),
    Step(27, "formula_artifacts", 4, "formulas-artifacts.yml", False,
         commands=(
             cmd(sys.executable, "scripts/validate_formulas_manifest.py",
                 requires=("scripts/validate_formulas_manifest.py",)),
             cmd(sys.executable, "tools/formula_artifact_builder.py",
                 "--root", ".", "--outdir", "artifacts/formulas",
                 requires=("tools/formula_artifact_builder.py",)),
         )),
    Step(28, "balance_report", 4, "rll-balance-report.yml", False,
         commands=(cmd(sys.executable, "scripts/rll_balance_report.py", "--metric", "bic",
                       requires=("scripts/rll_balance_report.py",)),)),
    Step(29, "dha_fisher", 4, "dha-fisher-ci.yml", False,
         commands=(
             cmd(sys.executable, "scripts/run_desi_dha_pipeline.py",
                 requires=("scripts/run_desi_dha_pipeline.py",)),
             cmd(sys.executable, "scripts/export_dha_forecast.py",
                 requires=("scripts/export_dha_forecast.py",)),
         )),
    Step(30, "real_seed_validation", 5, "real-seed-validation-v0.yml", False,
         commands=(cmd(sys.executable, "scripts/validation/run_real_seed_validations.py",
                       requires=("scripts/validation/run_real_seed_validations.py",)),)),
    Step(31, "dense_feature_matrix", 5, "dense-feature-matrix.yml", False,
         commands=(cmd(sys.executable, "scripts/data_scan/build_dense_behavior_features.py",
                       requires=("scripts/data_scan/build_dense_behavior_features.py",)),)),
    Step(32, "orbital_shape", 5, "orbital-shape-angular-momentum-validation.yml", False,
         commands=(cmd(sys.executable, "scripts/validation/validate_orbital_shape_angular_momentum.py",
                       requires=("scripts/validation/validate_orbital_shape_angular_momentum.py",)),)),
    Step(33, "bootstrap_validation", 5, "real-data-bootstrap-validation.yml", False,
         commands=(cmd(sys.executable, "scripts/data_scan/scan_real_data_bootstrap.py", "--repo", ".",
                       requires=("scripts/data_scan/scan_real_data_bootstrap.py",)),)),
    Step(34, "sequence_metrics", 5, "validate-sequence-metrics.yml", False,
         commands=(cmd(sys.executable, "-m", "pytest", "-q",
                       "tests/test_calculate_sequence_metrics.py",
                       requires=("tests/test_calculate_sequence_metrics.py",)),)),
    Step(35, "academic_governance", 6, "academic-parameter-governance.yml", True,
         commands=(
             cmd(sys.executable, "tools/validate_academic_parameter_registry.py",
                 requires=("tools/validate_academic_parameter_registry.py",)),
             cmd(sys.executable, "tools/scan_rll_model_evidence.py", "--no-write",
                 requires=("tools/scan_rll_model_evidence.py",)),
             cmd(sys.executable, "tools/run_rll_academic_claim_governance.py", "--no-write",
                 requires=("tools/run_rll_academic_claim_governance.py",)),
             cmd(sys.executable, "tools/make_h0_rd_ablation_matrix.py", "--no-write",
                 requires=("tools/make_h0_rd_ablation_matrix.py",)),
             cmd(sys.executable, "tools/apply_rll_outcome_protocol.py",
                 "--no-write", "--status", "CLAIM_BLOCKED",
                 requires=("tools/apply_rll_outcome_protocol.py",)),
         )),
    Step(36, "six_sigma_controls", 6, "six-sigma-real-data-controls.yml", True,
         commands=(cmd(sys.executable, "tools/validate_six_sigma_real_data_controls.py",
                       requires=("tools/validate_six_sigma_real_data_controls.py",)),)),
    Step(37, "variance_registry", 6, "validate-real-dataset-variance-registry.yml", True,
         commands=(cmd(sys.executable, "tools/validate_real_dataset_variance_registry.py",
                       requires=("tools/validate_real_dataset_variance_registry.py",)),)),
    Step(38, "academic_correlation", 6, "validate-academic-correlation-package.yml", True,
         commands=(cmd(sys.executable, "tools/validate_academic_correlation_package.py",
                       requires=("tools/validate_academic_correlation_package.py",)),)),
    Step(39, "cross_repo_registry", 6, "validate-cross-repo-relationship-registry.yml", True,
         commands=(
             cmd(sys.executable, "tools/validate_cross_repo_relationship_registry.py",
                 requires=("tools/validate_cross_repo_relationship_registry.py",)),
             cmd(sys.executable, "tools/validate_session_operating_system.py",
                 requires=("tools/validate_session_operating_system.py",)),
             cmd(sys.executable, "tools/validate_session_reality_science_claims.py",
                 requires=("tools/validate_session_reality_science_claims.py",)),
             cmd(sys.executable, "tools/validate_session_unified_interaction.py",
                 requires=("tools/validate_session_unified_interaction.py",)),
         )),
    Step(40, "python_tests", 6, "python-tests.yml", True,
         commands=(cmd(sys.executable, "-m", "pytest", "-q", requires=("tests",)),)),
)


def rel(path: Path) -> str:
    try:
        return str(path.relative_to(ROOT))
    except ValueError:
        return str(path)


def path_exists(path: str) -> bool:
    return (ROOT / path).exists()


def ensure_dirs() -> None:
    RESULTS.mkdir(parents=True, exist_ok=True)
    LOGS.mkdir(parents=True, exist_ok=True)
    ARTIFACTS.mkdir(parents=True, exist_ok=True)


def write_log_header(handle, step: Step) -> None:
    handle.write(f"STEP={step.number:02d}\n")
    handle.write(f"NAME={step.name}\n")
    handle.write(f"PHASE={step.phase}\n")
    handle.write(f"ORIGIN={step.origin}\n")
    handle.write(f"CRITICAL={str(step.critical).lower()}\n")
    handle.write(f"UTC={datetime.now(timezone.utc).isoformat()}\n\n")
    handle.flush()


def run_argv(argv: Sequence[str], handle) -> int:
    printable = " ".join(argv)
    handle.write(f"$ {printable}\n")
    handle.flush()
    proc = subprocess.Popen(
        list(argv),
        cwd=ROOT,
        stdout=subprocess.PIPE,
        stderr=subprocess.STDOUT,
        text=True,
        encoding="utf-8",
        errors="replace",
        env={**os.environ, "PYTHONUNBUFFERED": "1"},
    )
    assert proc.stdout is not None
    for line in proc.stdout:
        handle.write(line)
        handle.flush()
        print(line, end="")
    return proc.wait()


def dependency_commands() -> tuple[CommandSpec, ...]:
    if path_exists("requirements.txt"):
        return (
            cmd(sys.executable, "-m", "pip", "install", "-r", "requirements.txt",
                "pytest", "jsonschema", "dynesty", requires=("requirements.txt",)),
        )
    if path_exists("pyproject.toml"):
        return (
            cmd(sys.executable, "-m", "pip", "install", "-e", ".",
                "pytest", "dynesty", requires=("pyproject.toml",)),
        )
    candidates = sorted(ROOT.glob("requirements*.txt"))
    if candidates:
        chosen = rel(candidates[0])
        return (cmd(sys.executable, "-m", "pip", "install", "-r", chosen,
                    requires=(chosen,)),)
    return ()


def yaml_validation(handle) -> tuple[str, int | None, str]:
    try:
        import yaml  # type: ignore
    except ImportError:
        return "TOKEN_VAZIO", None, "PyYAML não está instalado"

    files = sorted((*ROOT.rglob("*.yml"), *ROOT.rglob("*.yaml")))
    files = [p for p in files if ".git" not in p.parts]
    if not files:
        return "TOKEN_VAZIO", None, "nenhum YAML encontrado"

    failures: list[str] = []
    for path in files:
        try:
            list(yaml.safe_load_all(path.read_text(encoding="utf-8")))
            handle.write(f"OK\t{rel(path)}\n")
        except Exception as exc:
            failures.append(f"{rel(path)}: {exc}")
            handle.write(f"FAIL\t{rel(path)}\t{exc}\n")
    handle.flush()
    if failures:
        return "FAIL", 1, f"{len(failures)} YAML(s) inválido(s)"
    return "OK", 0, f"{len(files)} YAML(s) válidos"


def select_commands(step: Step) -> tuple[CommandSpec, ...]:
    if step.handler == "dependencies":
        return dependency_commands()
    if step.candidates:
        for candidate in step.candidates:
            if all(path_exists(path) for path in candidate.requires):
                return (candidate,)
        return ()
    return step.commands


def missing_requirements(commands: Iterable[CommandSpec]) -> list[str]:
    missing: list[str] = []
    for spec in commands:
        missing.extend(path for path in spec.requires if not path_exists(path))
    return sorted(set(missing))


def run_step(step: Step, selected_phases: set[int], mode: str) -> StepResult:
    start = time.monotonic()
    log_path = LOGS / f"step{step.number:02d}_{step.name}.log"

    if step.phase not in selected_phases or (mode == "dry_run" and step.number == 2):
        return StepResult(
            step.number, step.name, step.phase, step.origin, step.critical,
            "SKIP", None, 0.0, "", "fora do modo selecionado", rel(log_path),
        )

    with log_path.open("w", encoding="utf-8") as handle:
        write_log_header(handle, step)

        if step.handler == "yaml":
            status, exit_code, detail = yaml_validation(handle)
            return StepResult(
                step.number, step.name, step.phase, step.origin, step.critical,
                status, exit_code, time.monotonic() - start,
                "internal:yaml.safe_load_all", detail, rel(log_path),
            )

        commands = select_commands(step)
        if not commands:
            detail = "nenhum comando elegível; executável ou entrada obrigatória ausente"
            handle.write(f"TOKEN_VAZIO\t{detail}\n")
            return StepResult(
                step.number, step.name, step.phase, step.origin, step.critical,
                "TOKEN_VAZIO", None, time.monotonic() - start,
                "", detail, rel(log_path),
            )

        missing = missing_requirements(commands)
        if missing:
            detail = "ausentes: " + ", ".join(missing)
            handle.write(f"TOKEN_VAZIO\t{detail}\n")
            return StepResult(
                step.number, step.name, step.phase, step.origin, step.critical,
                "TOKEN_VAZIO", None, time.monotonic() - start,
                " && ".join(" ".join(c.argv) for c in commands),
                detail, rel(log_path),
            )

        command_texts: list[str] = []
        for spec in commands:
            command_texts.append(" ".join(spec.argv))
            exit_code = run_argv(spec.argv, handle)
            if exit_code != 0:
                detail = f"comando retornou exit_code={exit_code}"
                handle.write(f"\nFAIL\t{detail}\n")
                return StepResult(
                    step.number, step.name, step.phase, step.origin, step.critical,
                    "FAIL", exit_code, time.monotonic() - start,
                    " && ".join(command_texts), detail, rel(log_path),
                )

        detail = f"{len(commands)} comando(s) concluído(s)"
        handle.write(f"\nOK\t{detail}\n")
        return StepResult(
            step.number, step.name, step.phase, step.origin, step.critical,
            "OK", 0, time.monotonic() - start,
            " && ".join(command_texts), detail, rel(log_path),
        )


def nested_get(payload: object, dotted_key: str) -> object | None:
    current = payload
    for part in dotted_key.split("."):
        if not isinstance(current, dict) or part not in current:
            return None
        current = current[part]
    return current


def find_metric(candidates: Sequence[tuple[str, Sequence[str]]]) -> dict[str, object]:
    inspected: list[str] = []
    for path_text, keys in candidates:
        path = ROOT / path_text
        inspected.append(path_text)
        if not path.exists():
            continue
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError):
            continue
        for key in keys:
            value = nested_get(payload, key)
            if isinstance(value, (int, float)) and not isinstance(value, bool):
                return {
                    "state": "VERIFIED",
                    "value": float(value),
                    "source": path_text,
                    "key": key,
                }
    return {
        "state": "TOKEN_VAZIO",
        "value": None,
        "source": None,
        "key": None,
        "inspected": inspected,
    }


def evaluate_metric(metric_id: str, value: float | None) -> str:
    if value is None:
        return "TOKEN_VAZIO"
    if metric_id == "F-COS-01":
        return "PASS" if value < 10.0 else "FAIL"
    if metric_id == "F-COS-02":
        return "PASS" if value < 1.05 else "FAIL"
    if metric_id == "F-COS-03":
        return "PASS" if 0.5 <= value <= 1.5 else "FAIL"
    if metric_id == "F-COS-04":
        return "PASS" if value > -5.0 else "FAIL"
    if metric_id == "F-COS-05":
        return "PASS" if value < 150.0 else "FAIL"
    raise ValueError(metric_id)


def build_contract(mode: str) -> dict[str, object]:
    specs = {
        "F-COS-01": {
            "label": "ΔAIC(RLL−ΛCDM)",
            "threshold": "< 10",
            "metric": find_metric((
                ("results/pantheon_plus_resultado_real.json", ("delta_aic", "metrics.delta_aic")),
                ("results/linear/pantheon_plus_resultado_real.json", ("delta_aic", "metrics.delta_aic")),
            )),
        },
        "F-COS-02": {
            "label": "χ² reduzido Pantheon+ RLL",
            "threshold": "< 1.05",
            "metric": find_metric((
                ("results/pantheon_plus_resultado_real.json", ("chi2_red_rll", "metrics.chi2_red_rll")),
                ("results/linear/pantheon_plus_resultado_real.json", ("chi2_red_rll", "metrics.chi2_red_rll")),
            )),
        },
        "F-COS-03": {
            "label": "redshift de transição z_t",
            "threshold": "0.5 ≤ z_t ≤ 1.5",
            "metric": find_metric((
                ("results/rll_fase20_mcmc_bayes.json", ("zt_bao", "metrics.zt_bao", "zt")),
                ("results/slingshot_zt_falsification.json", ("zt_bao", "zt", "metrics.zt_bao")),
            )),
        },
        "F-COS-04": {
            "label": "ln(B10)",
            "threshold": "> -5",
            "metric": find_metric((
                ("results/rll_fase20_mcmc_bayes.json", ("ln_B10", "ln_b10", "metrics.ln_B10")),
                ("data/bayes_result.json", ("ln_B10", "ln_b10", "metrics.ln_B10")),
            )),
        },
        "F-COS-05": {
            "label": "χ² DESI nominal",
            "threshold": "< 150",
            "metric": find_metric((
                ("results/desi_dr2_bao_covariance_chi2.json", ("chi2_nominal", "chi2", "metrics.chi2_nominal")),
                ("results/rll_real_pipeline.json", ("chi2_desi_nominal", "metrics.chi2_desi_nominal")),
            )),
        },
    }

    rows: list[dict[str, object]] = []
    for metric_id, spec in specs.items():
        metric = spec["metric"]
        assert isinstance(metric, dict)
        value = metric.get("value")
        outcome = evaluate_metric(metric_id, value if isinstance(value, float) else None)
        rows.append({
            "id": metric_id,
            "label": spec["label"],
            "threshold": spec["threshold"],
            "state": metric["state"],
            "value": value,
            "outcome": outcome,
            "source": metric.get("source"),
            "key": metric.get("key"),
            "inspected": metric.get("inspected", []),
        })

    contract = {
        "schema_version": "rll.fase24.1.contract.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "mode": mode,
        "claim_allowed": False,
        "claim_boundary": (
            "CLAIM_BLOCKED: resultados só podem ser citados quando materializados "
            "na execução atual; nenhum valor histórico é usado como fallback."
        ),
        "falsifiers": rows,
    }
    (RESULTS / "CONTRATO_FALSIFICADORES_DETERMINISTICO.json").write_text(
        json.dumps(contract, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )

    md = [
        "# CONTRATO DE FALSIFICADORES — FASE 24.1",
        "",
        f"- Gerado em: `{contract['generated_at']}`",
        f"- Modo: `{mode}`",
        "- `claim_allowed=false`",
        "- Política: ausência de arquivo/chave é `TOKEN_VAZIO`; não existe fallback numérico.",
        "",
        "| ID | Métrica | Threshold | Estado da evidência | Valor atual | Resultado | Fonte |",
        "|---|---|---|---|---:|---|---|",
    ]
    for row in rows:
        value = row["value"]
        value_text = "TOKEN_VAZIO" if value is None else f"{value:.8g}"
        md.append(
            f"| {row['id']} | {row['label']} | `{row['threshold']}` | "
            f"`{row['state']}` | {value_text} | `{row['outcome']}` | "
            f"`{row['source'] or 'TOKEN_VAZIO'}` |"
        )
    md.extend((
        "",
        "> Este contrato descreve somente evidência materializada no checkout/run atual.",
        "",
    ))
    (RESULTS / "CONTRATO_FALSIFICADORES_DETERMINISTICO.md").write_text(
        "\n".join(md), encoding="utf-8"
    )
    return contract


def write_status_files(results: Sequence[StepResult]) -> None:
    tsv_path = RESULTS / "step_status.tsv"
    with tsv_path.open("w", encoding="utf-8", newline="") as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow((
            "step", "name", "phase", "origin", "critical", "status",
            "exit_code", "duration_s", "command", "detail", "log_path",
        ))
        for item in results:
            if item.status not in VALID_STATES:
                raise RuntimeError(f"estado inválido: {item.status}")
            writer.writerow((
                f"{item.number:02d}", item.name, item.phase, item.origin,
                str(item.critical).lower(), item.status,
                "" if item.exit_code is None else item.exit_code,
                f"{item.duration_s:.3f}", item.command, item.detail, item.log_path,
            ))

    payload = {
        "schema_version": "rll.fase24.1.step-status.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "steps": [item.__dict__ for item in results],
    }
    (RESULTS / "step_status.json").write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def gate_decision(mode: str, results: Sequence[StepResult], contract: dict[str, object]) -> dict[str, object]:
    blocking_steps = [
        item for item in results
        if item.critical and item.status in {"FAIL", "TOKEN_VAZIO"}
    ]

    metric_blockers: list[str] = []
    if mode in SCIENCE_MODES:
        falsifiers = contract.get("falsifiers", [])
        if isinstance(falsifiers, list):
            metric_blockers = [
                str(row.get("id"))
                for row in falsifiers
                if isinstance(row, dict) and row.get("state") == "TOKEN_VAZIO"
            ]

    status = "BLOCKED" if blocking_steps or metric_blockers else "OK"
    return {
        "status": status,
        "claim_allowed": False,
        "blocking_steps": [
            {
                "step": f"{item.number:02d}",
                "name": item.name,
                "status": item.status,
                "detail": item.detail,
            }
            for item in blocking_steps
        ],
        "metric_token_vazio": metric_blockers,
    }


def write_report(mode: str, results: Sequence[StepResult], contract: dict[str, object],
                 decision: dict[str, object]) -> None:
    counts = {state: 0 for state in sorted(VALID_STATES)}
    for item in results:
        counts[item.status] += 1

    lines = [
        "# RELATÓRIO FINAL — RLL FASE 24.1",
        "",
        f"- Gerado em: `{datetime.now(timezone.utc).isoformat()}`",
        f"- Modo: `{mode}`",
        f"- Gate operacional: **{decision['status']}**",
        "- `claim_allowed=false`",
        "",
        "## Painel",
        "",
        f"- OK: **{counts['OK']}**",
        f"- FAIL: **{counts['FAIL']}**",
        f"- TOKEN_VAZIO: **{counts['TOKEN_VAZIO']}**",
        f"- SKIP: **{counts['SKIP']}**",
        "",
        "## Etapas",
        "",
        "| Step | Fase | Nome | Crítica | Estado | Duração | Origem |",
        "|---:|---:|---|---|---|---:|---|",
    ]
    for item in results:
        lines.append(
            f"| {item.number:02d} | {item.phase} | `{item.name}` | "
            f"{'sim' if item.critical else 'não'} | `{item.status}` | "
            f"{item.duration_s:.2f}s | `{item.origin}` |"
        )

    lines.extend(("", "## Bloqueadores", ""))
    blockers = decision.get("blocking_steps", [])
    metric_blockers = decision.get("metric_token_vazio", [])
    if not blockers and not metric_blockers:
        lines.append("- Nenhum bloqueador operacional no modo selecionado.")
    else:
        for blocker in blockers if isinstance(blockers, list) else []:
            lines.append(
                f"- Step `{blocker['step']}` `{blocker['name']}`: "
                f"`{blocker['status']}` — {blocker['detail']}"
            )
        if metric_blockers:
            lines.append(
                "- Evidência científica não materializada: "
                + ", ".join(f"`{item}`" for item in metric_blockers)
            )

    lines.extend((
        "",
        "## Regra de integridade",
        "",
        "Uma etapa ausente não vira OK. Um valor histórico não vira resultado do run atual. "
        "O artifact é publicado mesmo quando o gate bloqueia, para preservar os logs.",
        "",
        "Consulte `CONTRATO_FALSIFICADORES_DETERMINISTICO.md` e `step_status.tsv`.",
        "",
    ))
    (RESULTS / "RELATORIO_LINEAR_FINAL.md").write_text(
        "\n".join(lines), encoding="utf-8"
    )


def write_checksums() -> None:
    targets = sorted(
        path for base in (RESULTS, LOGS, ARTIFACTS)
        for path in base.rglob("*")
        if path.is_file() and path.name != "CHECKSUMS.sha256"
    )
    checksum_path = RESULTS / "CHECKSUMS.sha256"
    with checksum_path.open("w", encoding="utf-8") as handle:
        for path in targets:
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            handle.write(f"{digest}  {rel(path)}\n")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=tuple(PHASES_BY_MODE), default="dry_run")
    return parser.parse_args()


def main() -> int:
    args = parse_args()
    ensure_dirs()
    selected_phases = PHASES_BY_MODE[args.mode]

    results: list[StepResult] = []
    for step in STEPS:
        print(f"\n=== {step.number:02d} {step.name} ===")
        result = run_step(step, selected_phases, args.mode)
        print(f"STATUS={result.status} DETAIL={result.detail}")
        results.append(result)

    contract = build_contract(args.mode)
    write_status_files(results)
    decision = gate_decision(args.mode, results, contract)
    (RESULTS / "gate_decision.json").write_text(
        json.dumps(decision, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )
    write_report(args.mode, results, contract, decision)
    write_checksums()

    print(json.dumps(decision, ensure_ascii=False, indent=2))
    return 0 if decision["status"] == "OK" else 1


if __name__ == "__main__":
    raise SystemExit(main())
