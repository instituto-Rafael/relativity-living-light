import json
from pathlib import Path

from tools.github_actions_runtime_ingest import classify_runtime, main


def _run(run_id: int, *, conclusion: str = "failure") -> dict:
    return {
        "id": run_id,
        "name": "Example Workflow",
        "event": "pull_request",
        "head_sha": "a" * 40,
        "conclusion": conclusion,
        "created_at": "2026-08-16T00:00:00Z",
        "updated_at": "2026-08-16T00:00:10Z",
    }


def test_zero_job_failure_is_review_only_token_vazio() -> None:
    observations, counts = classify_runtime(
        {"workflow_runs": [_run(101)]},
        {101: {"total_count": 0, "jobs": []}},
    )
    assert counts["failure_runs"] == 1
    assert counts["zero_job_failures"] == 1
    assert counts["jobbed_failures"] == 0
    assert len(observations) == 1
    obs = observations[0]
    assert obs.kind == "RUNTIME_ZERO_JOB_FAILURE"
    assert obs.urgency == "P1"
    assert obs.state == "TOKEN_VAZIO_ROOT_CAUSE"
    assert obs.auto_fixable is False
    assert "do not infer a cause" in obs.proposed_action


def test_jobbed_failure_is_not_mislabeled_zero_job() -> None:
    observations, counts = classify_runtime(
        {"workflow_runs": [_run(202)]},
        {202: {"total_count": 1, "jobs": [{"id": 1, "conclusion": "failure"}]}},
    )
    assert counts["failure_runs"] == 1
    assert counts["zero_job_failures"] == 0
    assert counts["jobbed_failures"] == 1
    assert observations == []


def test_missing_jobs_snapshot_remains_explicit_gap() -> None:
    observations, counts = classify_runtime({"workflow_runs": [_run(303)]}, {})
    assert counts["missing_job_snapshots"] == 1
    assert observations[0].kind == "RUNTIME_JOB_SNAPSHOT_MISSING"
    assert observations[0].state == "TOKEN_VAZIO_JOBS_ENDPOINT"


def test_nonfailure_run_is_not_promoted_to_runtime_failure() -> None:
    observations, counts = classify_runtime(
        {"workflow_runs": [_run(404, conclusion="success")]},
        {404: {"total_count": 0, "jobs": []}},
    )
    assert counts["failure_runs"] == 0
    assert observations == []


def test_snapshot_mode_writes_hash_bound_products(tmp_path: Path) -> None:
    runs_path = tmp_path / "runs.json"
    jobs_dir = tmp_path / "jobs"
    out = tmp_path / "out"
    jobs_dir.mkdir()
    runs_path.write_text(json.dumps({"workflow_runs": [_run(505)]}), encoding="utf-8")
    (jobs_dir / "jobs_505.json").write_text(json.dumps({"total_count": 0, "jobs": []}), encoding="utf-8")

    rc = main([
        "--snapshot-runs", str(runs_path),
        "--snapshot-jobs-dir", str(jobs_dir),
        "--repository", "owner/repo",
        "--output-dir", str(out),
    ])
    assert rc == 0
    for name in (
        "runtime_observations.jsonl",
        "runtime_state_vector.json",
        "runtime_receipt.json",
        "RUNTIME_SUMMARY.md",
        "raw/runs.json",
        "raw/jobs_505.json",
    ):
        assert (out / name).is_file(), name

    receipt = json.loads((out / "runtime_receipt.json").read_text(encoding="utf-8"))
    vector = json.loads((out / "runtime_state_vector.json").read_text(encoding="utf-8"))
    assert receipt["claim_allowed"] is False
    assert receipt["auto_fixable"] is False
    assert receipt["root_cause_inference_from_zero_jobs"] == "FORBIDDEN"
    assert receipt["raw_sha256"]["raw/runs.json"]
    assert receipt["observations_sha256"]
    assert vector["p0"] == 0
    assert vector["p1"] == 1
    assert vector["token_vazio"] == 1
