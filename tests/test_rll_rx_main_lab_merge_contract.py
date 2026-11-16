"""Merge safety: preserve main Rx execution fabric and laboratory data-validation gates."""
from __future__ import annotations

import json
from pathlib import Path

import yaml

ROOT = Path(__file__).resolve().parents[1]
SOURCE = ROOT / ".github/workflows/real-data-complete-execution.yml"

# The 13 paths that triggered the lab's Pantheon/scientific workflow before
# merging the main-only Rx source layer. Exact lab items must remain included.
LAB_PATHS = {
    "scripts/download_real_cosmology_inputs.sh",
    "scripts/verify_pantheon_inputs.py",
    "tools/validate_scientific_validation_orchestrator_v3.py",
    "tools/run_g3_dataset_compatibility.py",
    "data/contracts/rll_g3_dataset_compatibility.v1.json",
    "artifacts/pantheon/RLL_PANTHEON_FULL_COVARIANCE_MATERIALIZATION_RECEIPT_20260819_RUN32285275333.json",
    "tests/test_pantheon_materialization_route_v3.py",
    "tests/test_scientific_validation_orchestrator_v3.py",
    "tests/test_g3_dataset_compatibility.py",
    "products/rll-evidence-runner/src/rll_evidence/pantheon_fit.py",
    "products/rll-evidence-runner/src/rll_evidence/pantheon_fit_ascii.py",
    "products/rll-evidence-runner/src/rll_evidence/pantheon_fit_three_model.py",
    ".github/workflows/real-data-complete-execution.yml",
}


def _load():
    return yaml.safe_load(SOURCE.read_text(encoding="utf-8"))


def test_trigger_covers_both_main_and_existing_lab_paths() -> None:
    obj = _load()
    triggers = obj.get("on", obj.get(True))
    paths = triggers["pull_request"]["paths"]
    assert len(paths) == 57 and len(paths) == len(set(paths))
    assert LAB_PATHS.issubset(paths)
    assert "rx/**" in paths
    assert "tools/rll_closure_queue.py" in paths


def test_full_rx_execution_graph_preserved_without_weakening_existing_jobs() -> None:
    obj = _load()
    jobs = obj["jobs"]
    assert {"rx-execution-fabric-pr-gate", "pantheon-full-covariance-pr-gate", "real-data-complete"}.issubset(jobs)
    rx = jobs["rx-execution-fabric-pr-gate"]
    assert "github.event_name == 'pull_request'" in rx["if"]
    assert rx["env"]["PYTHONPATH"] == "."
    names = {step["name"] for step in rx["steps"]}
    for name in (
        "Rx execution-fabric stdlib tests",
        "Rx zero-third-party gate",
        "Rx no-AI runtime gate",
        "Validate fail-closed SCI_GATE execution graph",
        "Build canonical V2 scientific decision packet",
        "Execute canonical Rx engineering plan",
        "Execute aggregate Rx development closure",
        "Upload Rx execution receipt bundle",
    ):
        assert name in names
    upload = next(s for s in rx["steps"] if s["name"] == "Upload Rx execution receipt bundle")
    assert upload["uses"] == "actions/upload-artifact@cf430e030ddbb5b0abf93d22962f4752f3646cd9"


def test_rx_runtime_does_not_expand_network_or_claim_authority() -> None:
    steps = _load()["jobs"]["rx-execution-fabric-pr-gate"]["steps"]
    plan = next(s for s in steps if s["name"] == "Execute canonical Rx engineering plan")
    develop = next(s for s in steps if s["name"] == "Execute aggregate Rx development closure")
    assert plan["env"]["RX_NETWORK_PROBE"] == "0"
    assert develop["env"]["RX_NETWORK_PROBE"] == "0"
    assert develop["env"]["RLL_LEGACY_NETWORK_PROBE"] == "0"
    assert "python3 -m rx" in plan["run"]
    assert "python3 -m rx" in develop["run"]


def test_main_only_rx_code_comes_with_required_contracts() -> None:
    for path in (
        "rx/__init__.py",
        "rx/__main__.py",
        "rx/orchestrator.py",
        "rx/scientific_gates.py",
        "tools/rll_closure_queue.py",
        "tools/rx_no_ai_gate.py",
        "tools/rx_zero_dependency_gate.py",
        "configs/rll_execution_plan.v1.yml",
        "data/governance/RLL_GATE_NAMESPACE_REGISTRY_V1.json",
    ):
        assert (ROOT / path).is_file(), path
    policy = json.loads((ROOT / "data/governance/RLL_GATE_NAMESPACE_REGISTRY_V1.json").read_text(encoding="utf-8"))
    assert isinstance(policy, dict)


def test_runtime_no_ai_guard_has_its_complete_file_set() -> None:
    # The first real Rx CI run found 23 absent active files. The complete set
    # is required, not a lowered gate or a mocked/suppressed missing-file check.
    required = (
        "validacao_real/run_rx_pipeline.py",
        "validacao_real/run_rx_multiprobe.py",
        "validacao_real/compute_validation_stdlib.py",
        "data/pipelines/structure_d/joint_real_likelihood_rx.py",
        "tools/rx_selftest.py",
        "tools/rx_sound_horizon_selftest.py",
        "tools/rx_freestanding65_parity.py",
        "tools/validate_rx_fairness.py",
        "tools/validate_rx_inference.py",
        "tools/rx_dependency_audit.py",
        "tools/rx_dependency_migration_plan.py",
        "tools/rx_development_gate.py",
        "internal/governance/development_guard.py",
        "tools/validate_rll_development_governance.py",
        "tools/rll_security_surface_audit.py",
        "tools/validate_real_data_materialization_security.py",
        "scripts/materialize_real_data_guarded.py",
        "tools/validate_ci_scientific_skills_stdlib_migration.py",
        "tools/validate_calc_data_stdlib_migration.py",
        "tools/validate_watch_config_stdlib_migration.py",
        "tools/validate_credential_authority_stdlib_migration.py",
        "tools/validate_rx_http_migration.py",
        "tools/validate_executable_entrypoint_authority_registry.py",
    )
    assert len(required) == 23
    missing = [p for p in required if not (ROOT / p).is_file()]
    assert missing == [], missing


def test_rx_authority_preflight_remains_fail_closed() -> None:
    security = json.loads((ROOT / "data/governance/RLL_DEVELOPMENT_SECURITY_ENVELOPE_V1.json").read_text(encoding="utf-8"))
    operation = json.loads((ROOT / "configs/rx_cli_operation.json").read_text(encoding="utf-8"))
    assert security["schema"] == "rll.development_security_envelope.v1"
    assert security["default_decision"] == "BLOCK"
    assert security["claim_allowed"] is False
    assert security["human_authority"]["required"] is True
    assert security["human_authority"]["self_authorization"] == "FORBIDDEN"
    assert operation["schema"] == "rll.development_operation.v1"
    assert operation["authority"]["human_required"] is True
    assert operation["authority"]["self_authorized"] is False
    assert operation["autonomy"]["goal_setting"] is False
    assert operation["autonomy"]["scope_expansion"] is False
