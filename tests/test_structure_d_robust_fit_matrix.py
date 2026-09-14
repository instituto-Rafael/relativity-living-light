from __future__ import annotations

import json

import pytest

from scripts import run_structure_d_robust_fit_matrix as matrix


def test_build_output_stem_is_versioned_and_safe() -> None:
    assert matrix.build_output_stem(1, 100) == "joint_real_likelihood_seed_1_maxiter_100"


def test_build_plan_is_dry_run_metadata_only() -> None:
    plan = matrix.build_plan([1, 2], 100)
    assert [item["output_stem"] for item in plan] == [
        "joint_real_likelihood_seed_1_maxiter_100",
        "joint_real_likelihood_seed_2_maxiter_100",
    ]
    assert all("run_structure_d_joint_likelihood.py" in str(item["command"]) for item in plan)


def test_parse_seeds_rejects_empty_or_nonpositive() -> None:
    with pytest.raises(ValueError):
        matrix.parse_seeds("")
    with pytest.raises(ValueError):
        matrix.parse_seeds("0")


def test_prefix_reuses_stem_guard() -> None:
    with pytest.raises(ValueError):
        matrix.build_output_stem(1, 100, "../escape")


def test_validate_plan_rejects_duplicate_stems() -> None:
    item = {"seed": 1, "maxiter": 100, "output_stem": "joint_real_likelihood_seed_1_maxiter_100"}
    with pytest.raises(ValueError, match="unique"):
        matrix.validate_plan([item, dict(item)])


def test_validate_plan_rejects_canonical_smoke_stem() -> None:
    with pytest.raises(ValueError, match="canonical"):
        matrix.validate_plan([{"seed": 1, "maxiter": 100, "output_stem": matrix.CANONICAL_STEM}])


def test_watchdog_marks_dry_run_and_safe_stems() -> None:
    plan = matrix.build_plan([1, 2], 100)
    watchdog = matrix.build_watchdog(plan, "dry_run")
    assert watchdog["overall_status"] == "pass"
    assert watchdog["dry_run_default"] is True
    assert watchdog["unique_output_stems"] is True
    assert watchdog["canonical_stem_blocked"] is True
    assert watchdog["planned_runs"] == 2


def test_existing_output_policy_fail_blocks_collision(tmp_path) -> None:
    plan = matrix.build_plan([1], 100)
    stem = plan[0]["output_stem"]
    (tmp_path / f"{stem}.json").write_text("{}\n", encoding="utf-8")

    with pytest.raises(ValueError, match="already exist"):
        matrix.apply_existing_output_policy(plan, "fail", tmp_path)


def test_existing_output_policy_suffix_allocates_failover_stem(tmp_path) -> None:
    plan = matrix.build_plan([1], 100)
    stem = plan[0]["output_stem"]
    (tmp_path / f"{stem}.json").write_text("{}\n", encoding="utf-8")

    resolved, actions, conflicts = matrix.apply_existing_output_policy(plan, "suffix", tmp_path)

    assert conflicts[stem]
    assert actions[0]["action"] == "suffix_failover"
    assert resolved[0]["output_stem"] == f"{stem}_failover_1"
    assert resolved[0]["command"].endswith(f"--output-stem {stem}_failover_1")


def test_existing_output_policy_skip_removes_conflicting_run(tmp_path) -> None:
    plan = matrix.build_plan([1, 2], 100)
    first_stem = plan[0]["output_stem"]
    (tmp_path / f"{first_stem}.csv").write_text("old\n", encoding="utf-8")

    resolved, actions, conflicts = matrix.apply_existing_output_policy(plan, "skip", tmp_path)

    assert first_stem in conflicts
    assert actions[0]["action"] == "skip_existing"
    assert [item["seed"] for item in resolved] == [2]


def test_plan_output_does_not_create_artificial_backup_on_first_write(tmp_path) -> None:
    output = tmp_path / "robust_fit_plan.json"

    assert matrix.main(["--seeds", "1", "--maxiter", "100", "--prefix", "pytest_plan", "--plan-output", str(output)]) == 0

    payload = json.loads(output.read_text(encoding="utf-8"))
    backup = output.with_suffix(output.suffix + ".bak")
    assert not backup.exists()
    assert payload["mode"] == "dry_run"
    assert payload["failsafe"]["atomic_plan_output"] is True
    assert payload["watchdog"]["overall_status"] == "pass"


def test_plan_output_uses_rollback_backup_when_replacing(tmp_path) -> None:
    output = tmp_path / "robust_fit_plan.json"
    output.write_text('{"old": true}\n', encoding="utf-8")

    assert matrix.main(["--seeds", "1", "--maxiter", "100", "--prefix", "pytest_plan", "--plan-output", str(output)]) == 0

    payload = json.loads(output.read_text(encoding="utf-8"))
    backup = output.with_suffix(output.suffix + ".bak")
    assert backup.exists()
    assert json.loads(backup.read_text(encoding="utf-8"))["old"] is True
    assert payload["mode"] == "dry_run"
    assert payload["failsafe"]["atomic_plan_output"] is True
    assert payload["watchdog"]["overall_status"] == "pass"


def test_planned_output_paths_are_versioned(tmp_path) -> None:
    stem = "joint_real_likelihood_seed_1_maxiter_100"
    paths = matrix.planned_output_paths(stem, tmp_path)
    filenames = [p.name for p in paths]
    assert f"{stem}.csv" in filenames
    assert f"{stem}.json" in filenames
    assert f"{stem}_covariance_manifest.json" in filenames
    assert all(p.parent == tmp_path for p in paths)


def test_versioned_output_paths_are_disjoint_from_canonical(tmp_path) -> None:
    versioned_stem = "joint_real_likelihood_seed_1_maxiter_100"
    canonical_stem = matrix.CANONICAL_STEM

    versioned_paths = {p.name for p in matrix.planned_output_paths(versioned_stem, tmp_path)}
    canonical_paths = {p.name for p in matrix.planned_output_paths(canonical_stem, tmp_path)}

    assert versioned_paths.isdisjoint(canonical_paths), (
        "Versioned output paths must not overlap with canonical output paths"
    )
