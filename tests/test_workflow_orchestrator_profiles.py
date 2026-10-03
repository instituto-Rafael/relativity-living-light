from pathlib import Path

import yaml

from tools.workflow_orchestrator import load_and_expand_catalog, select_workflows

ROOT = Path(__file__).resolve().parents[1]
CATALOG = ROOT / ".github/workflow-orchestrator/session.yml"
TOWER = ROOT / ".github/workflow-orchestrator/workflows/tower/00-transit-tower.yml"
SESSION_WORKFLOW = ROOT / ".github/workflows/unified-workflow-session-orchestrator.yml"
ACADEMIC_WORKFLOW = ROOT / ".github/workflows/validate-academic-correlation-package.yml"


def selected_ids(catalog, profile):
    return {workflow.workflow_id for workflow in select_workflows(catalog, profile)}


def test_catalog_separates_inventory_from_explicit_dispatch_manifests():
    raw = yaml.safe_load(CATALOG.read_text(encoding="utf-8"))
    assert raw["schema"] == "rll.workflow_orchestrator.catalog.v3"
    assert "workflows" not in raw
    assert raw["workflow_catalog_dirs"] == ["workflows/tower", "workflows/research"]
    assert raw["workflow_inventory"]["patterns"] == ["../workflows/*.y*ml"]
    assert raw["execution"] == {
        "mode": "sequential",
        "stage_barrier": True,
        "max_in_flight": 1,
        "wait_for_completion": True,
        "fail_fast": True,
    }
    tower = yaml.safe_load(TOWER.read_text(encoding="utf-8"))
    tower_ids = {item["id"] for item in tower["workflows"] if item["enabled"]}
    assert {"deterministic_pipeline", "frontier_research_omega"} <= tower_ids
    catalog = load_and_expand_catalog(CATALOG)
    assert len(catalog["workflows"]) == 15
    assert len([item for item in catalog["workflows"] if item["enabled"]]) == 12
    academic = next(item for item in catalog["workflows"] if item["id"] == "academic_correlation_package")
    assert academic["claim_allowed"] is False
    assert academic["publication_effect"] == "NONE"
    assert set(academic["override_allowlist"]) == {"arxiv_id", "related_node_ids", "relation_note"}


def test_profiles_have_bounded_child_timeout_budgets():
    catalog = load_and_expand_catalog(CATALOG)
    expected = {
        "transit_refactor": ({"yaml_deep_audit", "yml_syntax_validation", "workflow_contract_sync_v2", "python_tests", "governance_quality_gate", "real_data_complete_execution"}, 190),
        "full_session": ({"yaml_deep_audit", "yml_syntax_validation", "workflow_contract_sync_v2", "python_tests", "governance_quality_gate", "real_data_complete_execution", "climate_engine_juno_shadow", "metar_earth_field", "rll_real_data_orchestrator"}, 305),
        "quick_session": ({"yaml_deep_audit", "yml_syntax_validation", "workflow_contract_sync_v2", "python_tests", "governance_quality_gate"}, 120),
        "real_data_session": ({"real_data_complete_execution", "climate_engine_juno_shadow", "metar_earth_field", "rll_real_data_orchestrator"}, 185),
        "science_shadow_session": ({"deterministic_pipeline", "frontier_research_omega"}, 190),
        "literature_session": ({"academic_correlation_package"}, 15),
        "pages_preview_session": ({"academic_correlation_package"}, 15),
    }
    for profile, (ids, budget) in expected.items():
        chosen = select_workflows(catalog, profile)
        assert {item.workflow_id for item in chosen} == ids
        assert sum(item.timeout_minutes for item in chosen) == budget
        assert [item.stage for item in chosen] == sorted(item.stage for item in chosen)
        assert budget < 360
    full = selected_ids(catalog, "full_session")
    assert "deterministic_pipeline" not in full
    assert "frontier_research_omega" not in full
    assert selected_ids(catalog, "science_shadow_session").isdisjoint(full)


def test_dispatch_choices_inputs_and_actions_are_bounded():
    catalog = load_and_expand_catalog(CATALOG)
    dispatcher = yaml.safe_load(SESSION_WORKFLOW.read_text(encoding="utf-8"))
    trigger = dispatcher.get("on", dispatcher.get(True, {}))
    choices = trigger["workflow_dispatch"]["inputs"]["profile"]["options"]
    assert choices == ["auto", *catalog["profiles"]]
    job = dispatcher["jobs"]["orchestrate-workflow-session"]
    assert job["timeout-minutes"] == 360
    run = next(step["run"] for step in job["steps"] if step["name"] == "Resolve profile and execute the single-flight transit")
    assert '--ref "$REF_INPUT"' in run
    assert '--overrides "$OVERRIDES_INPUT"' in run
    assert "${{ inputs.profile }}" not in run
    academic = yaml.safe_load(ACADEMIC_WORKFLOW.read_text(encoding="utf-8"))
    assert academic["permissions"] == {"contents": "read"}
    assert academic["jobs"]["validate-and-preview"]["timeout-minutes"] == 15
    actions = [step["uses"] for step in academic["jobs"]["validate-and-preview"]["steps"] if "uses" in step]
    assert all(len(action.rsplit("@", 1)[-1]) == 40 for action in actions)
