from __future__ import annotations

from fnmatch import fnmatchcase
from pathlib import Path

import pytest
import yaml

CANONICAL_WORKFLOW = ".github/workflows/rll-pipeline-linear-completo.yml"

PATH_FILTERED_WORKFLOW_REQUIREMENTS = {
    ".github/workflows/dha-fisher-ci.yml": {
        "required_paths": {
            ".github/workflows/dha-fisher-ci.yml",
            "src/**",
            "scripts/run_ln1pz_extractor.py",
            "scripts/run_desi_dha_pipeline.py",
            "scripts/export_dha_forecast.py",
            "tests/test_dha_fisher.py",
            "tests/test_ln1pz_extractor.py",
            "tests/test_desi_dha_extractor.py",
            "pyproject.toml",
        },
        "positive_example": "scripts/run_desi_dha_pipeline.py",
    },
}

MANUAL_SCIENCE_DELEGATES = (
    ".github/workflows/RLL-CI.yml",
    ".github/workflows/RLL_SCIENTIFIC.yml",
    ".github/workflows/bayes_analysis.yml",
)

CANONICAL_REQUIRED_PATHS = {
    CANONICAL_WORKFLOW,
    ".github/workflows/RLL-CI.yml",
    ".github/workflows/RLL_SCIENTIFIC.yml",
    ".github/workflows/bayes_analysis.yml",
    "tools/rll_pipeline_deterministic.py",
    "tools/validate_schema_contracts.py",
    "tools/audit_github_workflows.py",
    "tools/validate_claim_allowed_gate.py",
    "tools/validate_schemas_claim_boundary.py",
    "tests/test_rll_pipeline_deterministic.py",
    "tests/test_scientific_workflow_path_filters.py",
    "src/**",
    "data/**",
    "validation/**",
    "requirements*.txt",
    "pyproject.toml",
}

NON_SCIENCE_CHANGE_EXAMPLES = (
    "docs/README.md",
    "schemas/contract/example.schema.json",
)

SCIENCE_CHANGE_EXAMPLES = (
    "src/run_full_analysis.py",
    "data/real/catalog.csv",
    "validation/run_rll.py",
    "requirements-dev.txt",
    "pyproject.toml",
)


def _workflow(path: str) -> dict:
    loaded = yaml.safe_load(Path(path).read_text(encoding="utf-8"))
    assert isinstance(loaded, dict), f"{path} must be a YAML mapping"
    return loaded


def _workflow_on(path: str) -> dict:
    workflow = _workflow(path)
    workflow_on = workflow["on"] if "on" in workflow else workflow.get(True)
    assert isinstance(workflow_on, dict), f"{path} must define workflow triggers"
    return workflow_on


def _pull_request_paths(path: str) -> list[str]:
    workflow_on = _workflow_on(path)
    pull_request = workflow_on["pull_request"]
    assert isinstance(pull_request, dict), f"{path} must define pull_request settings"
    paths = pull_request.get("paths")
    assert isinstance(paths, list) and paths, f"{path} must define pull_request.paths"
    return paths


def _matches_any(changed_path: str, patterns: list[str]) -> bool:
    """Approximate GitHub path-filter glob semantics, including recursive `**`."""
    return any(fnmatchcase(changed_path, pattern) for pattern in patterns)


@pytest.mark.parametrize("workflow_path", PATH_FILTERED_WORKFLOW_REQUIREMENTS)
def test_independent_scientific_workflows_define_required_pull_request_paths(
    workflow_path: str,
) -> None:
    patterns = set(_pull_request_paths(workflow_path))
    required = PATH_FILTERED_WORKFLOW_REQUIREMENTS[workflow_path]["required_paths"]
    missing = required - patterns
    assert required.issubset(patterns), (
        f"{workflow_path} missing required paths: {sorted(missing)}"
    )


@pytest.mark.parametrize("workflow_path", PATH_FILTERED_WORKFLOW_REQUIREMENTS)
def test_independent_scientific_workflows_ignore_docs_and_schema_only_changes(
    workflow_path: str,
) -> None:
    patterns = _pull_request_paths(workflow_path)
    for changed_path in NON_SCIENCE_CHANGE_EXAMPLES:
        assert not _matches_any(changed_path, patterns)


@pytest.mark.parametrize("workflow_path", PATH_FILTERED_WORKFLOW_REQUIREMENTS)
def test_independent_scientific_workflows_still_trigger_on_representative_change(
    workflow_path: str,
) -> None:
    patterns = _pull_request_paths(workflow_path)
    changed_path = PATH_FILTERED_WORKFLOW_REQUIREMENTS[workflow_path]["positive_example"]
    assert _matches_any(changed_path, patterns), (
        f"{workflow_path} should trigger for {changed_path}; patterns={patterns}"
    )


@pytest.mark.parametrize("workflow_path", MANUAL_SCIENCE_DELEGATES)
def test_legacy_science_entries_are_manual_only(workflow_path: str) -> None:
    workflow_on = _workflow_on(workflow_path)
    assert set(workflow_on) == {"workflow_dispatch"}, (
        f"{workflow_path} must not retain push, pull_request, or schedule triggers"
    )


@pytest.mark.parametrize("workflow_path", MANUAL_SCIENCE_DELEGATES)
def test_legacy_science_entries_delegate_to_canonical_gate(workflow_path: str) -> None:
    workflow = _workflow(workflow_path)
    jobs = workflow.get("jobs")
    assert isinstance(jobs, dict) and len(jobs) == 1
    job = next(iter(jobs.values()))
    assert isinstance(job, dict)
    assert job.get("uses") == f"./{CANONICAL_WORKFLOW}"
    inputs = job.get("with")
    assert isinstance(inputs, dict)
    assert inputs.get("modo") == "apenas_ciencia"


def test_canonical_gate_owns_science_pull_request_routing() -> None:
    patterns = set(_pull_request_paths(CANONICAL_WORKFLOW))
    missing = CANONICAL_REQUIRED_PATHS - patterns
    assert CANONICAL_REQUIRED_PATHS.issubset(patterns), (
        f"{CANONICAL_WORKFLOW} missing canonical routes: {sorted(missing)}"
    )


def test_canonical_gate_ignores_docs_and_schema_only_changes() -> None:
    patterns = _pull_request_paths(CANONICAL_WORKFLOW)
    for changed_path in NON_SCIENCE_CHANGE_EXAMPLES:
        assert not _matches_any(changed_path, patterns)


@pytest.mark.parametrize("changed_path", SCIENCE_CHANGE_EXAMPLES)
def test_canonical_gate_runs_light_dry_run_for_science_changes(changed_path: str) -> None:
    patterns = _pull_request_paths(CANONICAL_WORKFLOW)
    assert _matches_any(changed_path, patterns), (
        f"canonical gate should observe {changed_path}; patterns={patterns}"
    )
