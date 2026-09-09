#!/usr/bin/env python3
"""Ingest GitHub Actions runtime failures without inventing a root cause.

The collector distinguishes a workflow run that failed before GitHub created any
job from a run whose jobs actually executed.  A zero-job failure is evidence of
an execution/platform/workflow-dispatch problem, not evidence for any specific
cause.  Unknown causes remain TOKEN_VAZIO and are review-only.

The tool can operate against the live GitHub REST API or deterministic snapshot
files used by tests/reproduction.  Every mode emits raw-source hashes, a JSONL
observation ledger, a state vector, a receipt, and a human-readable summary.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
from dataclasses import asdict, dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SCHEMA = "rll.github_actions_runtime_ingest.v1"
API_VERSION = "2022-11-28"
DEFAULT_OUTPUT = Path("artifacts/operational-runtime-ingest")


@dataclass(frozen=True)
class Observation:
    id: str
    kind: str
    urgency: str
    state: str
    source: str
    evidence: str
    auto_fixable: bool
    proposed_action: str
    falsifier: str
    provenance: str


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def stable_json(payload: Any) -> bytes:
    return (json.dumps(payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")) + "\n").encode("utf-8")


def observation_id(kind: str, source: str, evidence: str) -> str:
    digest = hashlib.sha256(f"{kind}\0{source}\0{evidence}".encode("utf-8")).hexdigest()[:12]
    return f"OBS-{digest.upper()}"


def make_observation(*, kind: str, urgency: str, state: str, source: str, evidence: str,
                     proposed_action: str, falsifier: str, provenance: str) -> Observation:
    return Observation(
        id=observation_id(kind, source, evidence),
        kind=kind,
        urgency=urgency,
        state=state,
        source=source,
        evidence=evidence,
        auto_fixable=False,
        proposed_action=proposed_action,
        falsifier=falsifier,
        provenance=provenance,
    )


def api_get(url: str, token: str) -> dict[str, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": API_VERSION,
        "User-Agent": "rll-runtime-ingest-v1",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = Request(url, headers=headers)
    with urlopen(request, timeout=30) as response:  # nosec B310: fixed GitHub API URL is constructed by caller
        raw = response.read()
    payload = json.loads(raw.decode("utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("GitHub API response must be a JSON object")
    return payload


def _run_evidence(run: dict[str, Any], total_jobs: int) -> str:
    return ";".join([
        f"run_id={run.get('id', 'TOKEN_VAZIO')}",
        f"workflow={run.get('name', 'TOKEN_VAZIO')}",
        f"event={run.get('event', 'TOKEN_VAZIO')}",
        f"head_sha={run.get('head_sha', 'TOKEN_VAZIO')}",
        f"conclusion={run.get('conclusion', 'TOKEN_VAZIO')}",
        f"created_at={run.get('created_at', 'TOKEN_VAZIO')}",
        f"updated_at={run.get('updated_at', 'TOKEN_VAZIO')}",
        f"total_jobs={total_jobs}",
    ])


def classify_runtime(runs_payload: dict[str, Any], jobs_by_run: dict[int, dict[str, Any]]) -> tuple[list[Observation], dict[str, int]]:
    runs = runs_payload.get("workflow_runs", [])
    if not isinstance(runs, list):
        raise ValueError("runs payload must contain workflow_runs[]")

    observations: list[Observation] = []
    failure_runs = 0
    zero_job_failures = 0
    jobbed_failures = 0
    missing_job_snapshots = 0

    for run in runs:
        if not isinstance(run, dict) or run.get("conclusion") != "failure":
            continue
        failure_runs += 1
        run_id_raw = run.get("id")
        try:
            run_id = int(run_id_raw)
        except (TypeError, ValueError):
            observations.append(make_observation(
                kind="RUNTIME_API_RECORD_INVALID", urgency="P1", state="INCERTEZA_INVALID_RUN_ID",
                source="github-actions-api:runs", evidence=f"run_id={run_id_raw!r}",
                proposed_action="preserve raw snapshot and inspect malformed runtime record",
                falsifier="a valid integer run id is present in a reproduced API snapshot",
                provenance="GitHub Actions REST API snapshot",
            ))
            continue

        jobs_payload = jobs_by_run.get(run_id)
        if jobs_payload is None:
            missing_job_snapshots += 1
            observations.append(make_observation(
                kind="RUNTIME_JOB_SNAPSHOT_MISSING", urgency="P1", state="TOKEN_VAZIO_JOBS_ENDPOINT",
                source=f"github-actions-api:run:{run_id}", evidence=_run_evidence(run, -1),
                proposed_action="retrieve the jobs endpoint for this exact run id and preserve the response hash",
                falsifier="jobs endpoint snapshot exists for the exact run id",
                provenance="runs endpoint present; jobs endpoint absent",
            ))
            continue

        total_jobs_raw = jobs_payload.get("total_count")
        if total_jobs_raw is None:
            jobs = jobs_payload.get("jobs", [])
            total_jobs = len(jobs) if isinstance(jobs, list) else 0
        else:
            try:
                total_jobs = int(total_jobs_raw)
            except (TypeError, ValueError):
                total_jobs = 0

        if total_jobs == 0:
            zero_job_failures += 1
            observations.append(make_observation(
                kind="RUNTIME_ZERO_JOB_FAILURE", urgency="P1", state="TOKEN_VAZIO_ROOT_CAUSE",
                source=f"github-actions-api:run:{run_id}", evidence=_run_evidence(run, total_jobs),
                proposed_action=(
                    "inspect workflow syntax/event eligibility/platform/ruleset state for this exact run; "
                    "do not infer a cause from zero jobs alone"
                ),
                falsifier=(
                    "reproduced jobs snapshot for the same run contains one or more jobs, or a platform/workflow "
                    "receipt establishes the root cause"
                ),
                provenance="GitHub Actions runs endpoint + exact run jobs endpoint",
            ))
        else:
            jobbed_failures += 1

    unique = {obs.id: obs for obs in observations}
    ordered = sorted(unique.values(), key=lambda item: (item.urgency, item.kind, item.source, item.id))
    counts = {
        "failure_runs": failure_runs,
        "zero_job_failures": zero_job_failures,
        "jobbed_failures": jobbed_failures,
        "missing_job_snapshots": missing_job_snapshots,
        "observations": len(ordered),
    }
    return ordered, counts


def api_failure_observation(error: str) -> Observation:
    safe = error.replace("\n", " ")[:500]
    return make_observation(
        kind="RUNTIME_API_INGESTION_FAILURE", urgency="P1", state="TOKEN_VAZIO_EXTERNAL_API",
        source="github-actions-api", evidence=safe,
        proposed_action="retry API ingestion and preserve the first successful raw snapshot; do not invent platform state",
        falsifier="a successful authenticated API snapshot is stored and hash-bound",
        provenance="collector exception boundary",
    )


def write_products(output: Path, *, mode: str, repository: str, runs_payload: dict[str, Any],
                   jobs_by_run: dict[int, dict[str, Any]], observations: list[Observation],
                   counts: dict[str, int], api_error: str | None = None) -> None:
    output.mkdir(parents=True, exist_ok=True)
    raw_dir = output / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    runs_bytes = stable_json(runs_payload)
    (raw_dir / "runs.json").write_bytes(runs_bytes)
    raw_hashes: dict[str, str] = {"raw/runs.json": sha256_bytes(runs_bytes)}
    for run_id, payload in sorted(jobs_by_run.items()):
        name = f"raw/jobs_{run_id}.json"
        data = stable_json(payload)
        (output / name).write_bytes(data)
        raw_hashes[name] = sha256_bytes(data)

    obs_text = "".join(json.dumps(asdict(obs), ensure_ascii=False, sort_keys=True) + "\n" for obs in observations)
    (output / "runtime_observations.jsonl").write_text(obs_text, encoding="utf-8")

    p1 = sum(obs.urgency == "P1" for obs in observations)
    p2 = sum(obs.urgency == "P2" for obs in observations)
    token_vazio = sum("TOKEN_VAZIO" in obs.state for obs in observations)
    vector = {
        "schema": "rll.runtime_operational_state_vector.v1",
        "repository": repository,
        "mode": mode,
        "p0": 0,
        "p1": p1,
        "p2": p2,
        "token_vazio": token_vazio,
        "counts": counts,
        "F_ok": [
            "runs and jobs endpoints are separated",
            "zero-job failure is not assigned an invented root cause",
            "raw API evidence is hash-bound",
        ],
        "F_gap": [obs.id for obs in observations],
        "F_next": [obs.proposed_action for obs in observations[:32]],
        "claim_allowed": False,
        "publication_effect": "NONE",
    }
    (output / "runtime_state_vector.json").write_text(json.dumps(vector, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    receipt = {
        "schema": SCHEMA,
        "generated_at": utc_now(),
        "repository": repository,
        "mode": mode,
        "api_version": API_VERSION,
        "counts": counts,
        "raw_sha256": raw_hashes,
        "observations_sha256": sha256_bytes(obs_text.encode("utf-8")),
        "api_error": api_error,
        "root_cause_inference_from_zero_jobs": "FORBIDDEN",
        "auto_fixable": False,
        "claim_allowed": False,
        "publication_effect": "NONE",
    }
    (output / "runtime_receipt.json").write_text(json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

    lines = [
        "# GitHub Actions Runtime Ingestion", "",
        f"- mode: `{mode}`",
        f"- repository: `{repository}`",
        f"- failure runs inspected: `{counts['failure_runs']}`",
        f"- zero-job failures: `{counts['zero_job_failures']}`",
        f"- jobbed failures: `{counts['jobbed_failures']}`",
        f"- missing job snapshots: `{counts['missing_job_snapshots']}`",
        f"- observations: `{len(observations)}`",
        f"- API state: `{'TOKEN_VAZIO_EXTERNAL_API' if api_error else 'OBSERVED'}`",
        "- root-cause inference from zero jobs: `FORBIDDEN`",
        "- claim_allowed: `false`", "",
        "## Review queue", "",
    ]
    if observations:
        lines.extend(f"- `{o.id}` `{o.kind}` — {o.source}: {o.state}" for o in observations[:100])
    else:
        lines.append("- `NONE`")
    (output / "RUNTIME_SUMMARY.md").write_text("\n".join(lines) + "\n", encoding="utf-8")


def load_snapshot(runs_path: Path, jobs_dir: Path) -> tuple[dict[str, Any], dict[int, dict[str, Any]]]:
    runs = json.loads(runs_path.read_text(encoding="utf-8"))
    if not isinstance(runs, dict):
        raise ValueError("snapshot runs file must contain a JSON object")
    jobs: dict[int, dict[str, Any]] = {}
    if jobs_dir.is_dir():
        for path in sorted(jobs_dir.glob("jobs_*.json")):
            run_id = int(path.stem.removeprefix("jobs_"))
            payload = json.loads(path.read_text(encoding="utf-8"))
            if isinstance(payload, dict):
                jobs[run_id] = payload
    return runs, jobs


def collect_live(repository: str, token: str, max_runs: int) -> tuple[dict[str, Any], dict[int, dict[str, Any]]]:
    if "/" not in repository:
        raise ValueError("repository must be owner/name")
    base = f"https://api.github.com/repos/{repository}"
    runs = api_get(f"{base}/actions/runs?status=failure&per_page={max_runs}", token)
    jobs: dict[int, dict[str, Any]] = {}
    for run in runs.get("workflow_runs", []):
        if not isinstance(run, dict) or run.get("conclusion") != "failure":
            continue
        run_id = run.get("id")
        if isinstance(run_id, int):
            jobs[run_id] = api_get(f"{base}/actions/runs/{run_id}/jobs?per_page=100", token)
    return runs, jobs


def main(argv: Iterable[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--live", action="store_true")
    mode.add_argument("--snapshot-runs", type=Path)
    parser.add_argument("--snapshot-jobs-dir", type=Path)
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "TOKEN_VAZIO_REPOSITORY"))
    parser.add_argument("--max-runs", type=int, default=25)
    parser.add_argument("--output-dir", type=Path, default=DEFAULT_OUTPUT)
    parser.add_argument("--strict-api", action="store_true", help="return non-zero when live API ingestion itself fails")
    args = parser.parse_args(list(argv) if argv is not None else None)

    if args.max_runs < 1 or args.max_runs > 100:
        print("ERROR RUNTIME_INGEST: --max-runs must be in [1,100]")
        return 2

    api_error: str | None = None
    try:
        if args.live:
            runs, jobs = collect_live(args.repository, os.environ.get("GITHUB_TOKEN", ""), args.max_runs)
            mode_name = "LIVE_GITHUB_API"
        else:
            if args.snapshot_jobs_dir is None:
                print("ERROR RUNTIME_INGEST: --snapshot-jobs-dir is required with --snapshot-runs")
                return 2
            runs, jobs = load_snapshot(args.snapshot_runs, args.snapshot_jobs_dir)
            mode_name = "DETERMINISTIC_SNAPSHOT"
        observations, counts = classify_runtime(runs, jobs)
    except (OSError, ValueError, json.JSONDecodeError, HTTPError, URLError) as exc:
        api_error = f"{type(exc).__name__}: {exc}"
        runs, jobs = {"workflow_runs": []}, {}
        observations = [api_failure_observation(api_error)]
        counts = {"failure_runs": 0, "zero_job_failures": 0, "jobbed_failures": 0, "missing_job_snapshots": 0, "observations": 1}
        mode_name = "LIVE_GITHUB_API" if args.live else "DETERMINISTIC_SNAPSHOT"

    write_products(
        args.output_dir, mode=mode_name, repository=args.repository, runs_payload=runs,
        jobs_by_run=jobs, observations=observations, counts=counts, api_error=api_error,
    )
    print(
        "runtime ingest: "
        f"failures={counts['failure_runs']} zero_jobs={counts['zero_job_failures']} "
        f"jobbed={counts['jobbed_failures']} missing_jobs={counts['missing_job_snapshots']} "
        f"api_error={bool(api_error)}"
    )
    return 1 if args.strict_api and api_error else 0


if __name__ == "__main__":
    raise SystemExit(main())
