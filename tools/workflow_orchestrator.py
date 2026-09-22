#!/usr/bin/env python3
"""Fail-closed, single-flight orchestration for governed RLL workflows.

The engine inventories every executable workflow but dispatches only workflows
with an explicit specialty manifest.  A child must complete before the next
stage starts.  Structural success never promotes a scientific claim.
"""
from __future__ import annotations

import argparse
import csv
import glob
import hashlib
import json
import os
import re
import time
from dataclasses import asdict, dataclass, replace
from datetime import datetime, timedelta, timezone
from pathlib import Path
from typing import Any, Iterable
from urllib import error, parse, request

import yaml

API_ROOT = "https://api.github.com"
SCHEMA = "rll.unified_workflow_session_orchestrator.v2"
ORCHESTRATOR_FILE = "unified-workflow-session-orchestrator.yml"
RUN_DISCOVERY_CLOCK_SKEW = timedelta(minutes=2)
FULL_SHA_RE = re.compile(r"^[0-9a-f]{40}$")
INVALID_REF_CHARS_RE = re.compile(r"[ ~^:?*\\[]")


@dataclass(frozen=True)
class WorkflowSelection:
    workflow_id: str
    file: str
    stage: int
    specialty: str
    wait_for_completion: bool
    timeout_minutes: int
    inputs: dict[str, Any]
    override_allowlist: tuple[str, ...]
    claim_allowed: bool
    publication_effect: str


class RunTimeoutError(RuntimeError):
    def __init__(self, run_id: int, timeout_minutes: int) -> None:
        super().__init__(
            f"timed out waiting for run {run_id} after {timeout_minutes} minutes"
        )
        self.run_id = run_id


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def sha256_bytes(payload: bytes) -> str:
    return hashlib.sha256(payload).hexdigest()


def sha256_json(payload: Any) -> str:
    encoded = json.dumps(
        payload, ensure_ascii=False, sort_keys=True, separators=(",", ":")
    ).encode("utf-8")
    return sha256_bytes(encoded)


def mapping(value: Any) -> dict[str, Any]:
    return value if isinstance(value, dict) else {}


def sequence(value: Any) -> list[Any]:
    return value if isinstance(value, list) else []


def bool_value(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value).strip().lower() == "true"


def load_yaml_mapping(path: Path) -> dict[str, Any]:
    data = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(data, dict):
        raise ValueError(f"{path}: top-level YAML must be a mapping")
    return data


def load_workflow(path: Path) -> dict[str, Any]:
    # BaseLoader preserves GitHub Actions' `on` key instead of coercing it to
    # the YAML 1.1 boolean True.
    data = yaml.load(path.read_text(encoding="utf-8"), Loader=yaml.BaseLoader)
    if not isinstance(data, dict):
        raise ValueError(f"{path}: workflow top-level YAML must be a mapping")
    return data


def workflow_triggers(document: dict[str, Any]) -> set[str]:
    raw = document.get("on")
    if isinstance(raw, dict):
        return {str(key) for key in raw}
    if isinstance(raw, list):
        return {str(item) for item in raw}
    if isinstance(raw, str) and raw:
        return {raw}
    return set()


def workflow_dispatch_inputs(document: dict[str, Any]) -> dict[str, Any]:
    raw = document.get("on")
    if not isinstance(raw, dict):
        return {}
    dispatch = raw.get("workflow_dispatch")
    if not isinstance(dispatch, dict):
        return {}
    inputs = dispatch.get("inputs")
    return inputs if isinstance(inputs, dict) else {}


def _catalog_manifests(catalog_path: Path, directories: list[str]) -> list[Path]:
    manifests: list[Path] = []
    catalog_root = catalog_path.parent.resolve()
    for directory in directories:
        directory_path = (catalog_path.parent / directory).resolve()
        if not directory_path.is_relative_to(catalog_root):
            raise ValueError(f"catalog directory escapes catalog root: {directory}")
        if not directory_path.is_dir():
            raise ValueError(f"workflow catalog directory not found: {directory}")
        manifests.extend(
            path
            for path in directory_path.rglob("*")
            if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}
        )
    return sorted(set(manifests))


def _workflow_inventory(
    catalog_path: Path,
    repo_root: Path,
    patterns: list[str],
    enabled_files: set[str],
    disabled_files: set[str],
) -> list[dict[str, Any]]:
    workflow_root = (repo_root / ".github" / "workflows").resolve()
    matches: set[Path] = set()
    for pattern in patterns:
        resolved_matches = {
            Path(item).resolve()
            for item in glob.glob(str(catalog_path.parent / pattern))
        }
        if not resolved_matches:
            raise ValueError(f"workflow inventory pattern matched nothing: {pattern}")
        for path in resolved_matches:
            if path.parent != workflow_root:
                raise ValueError(
                    f"workflow inventory path is outside .github/workflows: {path}"
                )
            if path.is_file() and path.suffix.lower() in {".yml", ".yaml"}:
                matches.add(path)

    rows: list[dict[str, Any]] = []
    for path in sorted(matches):
        document = load_workflow(path)
        triggers = sorted(workflow_triggers(document))
        dispatchable = "workflow_dispatch" in triggers
        if path.name == ORCHESTRATOR_FILE:
            classification = "ORCHESTRATOR_SELF"
        elif path.name in enabled_files:
            classification = "TOWER_MANAGED"
        elif path.name in disabled_files:
            classification = "DISABLED_MANIFEST"
        elif dispatchable:
            classification = "STANDALONE_DISPATCHABLE"
        else:
            classification = "EVENT_DRIVEN"
        rows.append(
            {
                "path": path.relative_to(repo_root).as_posix(),
                "file": path.name,
                "sha256": sha256_bytes(path.read_bytes()),
                "triggers": triggers,
                "dispatchable": dispatchable,
                "classification": classification,
            }
        )
    return rows


def load_and_expand_catalog(path: Path) -> dict[str, Any]:
    path = path.resolve()
    data = load_yaml_mapping(path)
    profiles = data.get("profiles")
    if not isinstance(profiles, dict) or not profiles:
        raise ValueError("catalog must contain a non-empty profiles mapping")

    execution = data.get("execution")
    if not isinstance(execution, dict):
        raise ValueError("catalog must contain an execution mapping")
    required_execution = {
        "mode": "sequential",
        "stage_barrier": True,
        "max_in_flight": 1,
        "wait_for_completion": True,
        "fail_fast": True,
    }
    for key, expected in required_execution.items():
        if execution.get(key) != expected:
            raise ValueError(f"execution.{key} must be {expected!r}")

    workflow_dirs = data.get("workflow_catalog_dirs")
    if not isinstance(workflow_dirs, list) or not workflow_dirs or not all(
        isinstance(item, str) for item in workflow_dirs
    ):
        raise ValueError("workflow_catalog_dirs must be a non-empty list of paths")

    workflow_items = data.get("workflows") or []
    if not isinstance(workflow_items, list):
        raise ValueError("workflows must be a list when provided")
    workflow_items = list(workflow_items)
    manifests = _catalog_manifests(path, workflow_dirs)
    for manifest in manifests:
        manifest_data = load_yaml_mapping(manifest)
        if isinstance(manifest_data.get("workflows"), list):
            items = manifest_data["workflows"]
        else:
            items = [manifest_data]
        for item in items:
            if not isinstance(item, dict):
                raise ValueError(f"{manifest}: workflow manifest item must be a mapping")
            copied = dict(item)
            copied["source_manifest"] = manifest.relative_to(path.parent).as_posix()
            workflow_items.append(copied)

    repo_root = path.parent.parent.parent.resolve()
    workflow_root = repo_root / ".github" / "workflows"
    seen_ids: set[str] = set()
    seen_files: set[str] = set()
    enabled_files: set[str] = set()
    disabled_files: set[str] = set()
    residuals: list[str] = []

    for item in workflow_items:
        if not isinstance(item, dict):
            raise ValueError("workflow catalog item must be a mapping")
        workflow_id = str(item.get("id", "")).strip()
        filename = str(item.get("file", "")).strip()
        if not workflow_id or not filename:
            raise ValueError("every workflow manifest requires id and file")
        if workflow_id in seen_ids:
            raise ValueError(f"duplicate workflow id: {workflow_id}")
        if filename in seen_files:
            raise ValueError(f"duplicate workflow file: {filename}")
        seen_ids.add(workflow_id)
        seen_files.add(filename)
        if Path(filename).name != filename or Path(filename).suffix.lower() not in {
            ".yml",
            ".yaml",
        }:
            raise ValueError(f"workflow file must be a direct YAML filename: {filename}")
        if filename == ORCHESTRATOR_FILE:
            raise ValueError("the orchestrator cannot dispatch itself")

        enabled = item.get("enabled", True)
        if not isinstance(enabled, bool):
            raise ValueError(f"{workflow_id}: enabled must be boolean")
        if not enabled:
            disabled_files.add(filename)
            reason = str(item.get("disabled_reason", "")).strip()
            if not reason:
                raise ValueError(f"{workflow_id}: disabled workflow requires disabled_reason")
            residuals.append(f"DISABLED_MANIFEST:{workflow_id}:{reason}")
            continue

        enabled_files.add(filename)
        if item.get("claim_allowed") is not False:
            raise ValueError(f"{workflow_id}: claim_allowed must be false")
        if item.get("publication_effect") != "NONE":
            raise ValueError(f"{workflow_id}: publication_effect must be NONE")
        if item.get("wait_for_completion") is not True:
            raise ValueError(f"{workflow_id}: wait_for_completion must be true")
        try:
            stage = int(item.get("stage"))
            timeout = int(item.get("timeout_minutes"))
        except (TypeError, ValueError) as exc:
            raise ValueError(f"{workflow_id}: stage and timeout_minutes must be integers") from exc
        if stage < 1:
            raise ValueError(f"{workflow_id}: stage must be positive")
        if timeout < 1 or timeout > 360:
            raise ValueError(f"{workflow_id}: timeout_minutes must be in 1..360")
        item["stage"] = stage
        item["timeout_minutes"] = timeout

        workflow_path = workflow_root / filename
        if not workflow_path.is_file():
            raise ValueError(f"{workflow_id}: workflow file not found: {workflow_path}")
        workflow_doc = load_workflow(workflow_path)
        if "workflow_dispatch" not in workflow_triggers(workflow_doc):
            raise ValueError(
                f"{workflow_id}: managed workflow lacks workflow_dispatch: {filename}"
            )

        supplied_inputs = item.get("inputs") or {}
        if not isinstance(supplied_inputs, dict):
            raise ValueError(f"{workflow_id}: inputs must be a mapping")
        declared_inputs = workflow_dispatch_inputs(workflow_doc)
        unknown_inputs = sorted(set(supplied_inputs) - set(declared_inputs))
        if unknown_inputs:
            raise ValueError(
                f"{workflow_id}: manifest supplies unknown workflow inputs: "
                + ", ".join(unknown_inputs)
            )
        missing_required = []
        for input_name, raw_config in declared_inputs.items():
            config = mapping(raw_config)
            if bool_value(config.get("required")) and "default" not in config:
                if input_name not in supplied_inputs:
                    missing_required.append(str(input_name))
        if missing_required:
            raise ValueError(
                f"{workflow_id}: required inputs have no manifest value: "
                + ", ".join(sorted(missing_required))
            )

        allowlist = item.get("override_allowlist") or []
        if not isinstance(allowlist, list) or not all(
            isinstance(name, str) for name in allowlist
        ):
            raise ValueError(f"{workflow_id}: override_allowlist must be a list of names")
        invalid_allowlist = sorted(set(allowlist) - set(declared_inputs))
        if invalid_allowlist:
            raise ValueError(
                f"{workflow_id}: override_allowlist contains unknown inputs: "
                + ", ".join(invalid_allowlist)
            )

    inventory_cfg = data.get("workflow_inventory")
    if not isinstance(inventory_cfg, dict):
        raise ValueError("catalog must contain workflow_inventory")
    patterns = inventory_cfg.get("patterns")
    if not isinstance(patterns, list) or not patterns or not all(
        isinstance(item, str) for item in patterns
    ):
        raise ValueError("workflow_inventory.patterns must be a non-empty list")
    inventory = _workflow_inventory(
        path, repo_root, patterns, enabled_files, disabled_files
    )
    inventory_files = {row["file"] for row in inventory}
    missing_from_inventory = sorted(seen_files - inventory_files)
    if missing_from_inventory:
        raise ValueError(
            "catalog files missing from workflow inventory: "
            + ", ".join(missing_from_inventory)
        )

    catalog_material = [path.read_bytes()]
    catalog_material.extend(manifest.read_bytes() for manifest in manifests)
    data["workflows"] = workflow_items
    data["execution"] = required_execution
    data["workflow_inventory_rows"] = inventory
    data["catalog_residuals"] = residuals
    data["catalog_sha256"] = sha256_bytes(b"\0".join(catalog_material))
    return data


def select_workflows(
    catalog: dict[str, Any], profile: str
) -> list[WorkflowSelection]:
    profile_cfg = mapping(mapping(catalog.get("profiles")).get(profile))
    if not profile_cfg:
        raise ValueError(f"profile '{profile}' not found in catalog")
    include_tags = {str(tag) for tag in sequence(profile_cfg.get("include_tags"))}
    if not include_tags:
        raise ValueError(f"profile '{profile}' must include at least one include_tag")

    selected: list[WorkflowSelection] = []
    for item in sequence(catalog.get("workflows")):
        if not isinstance(item, dict) or item.get("enabled", True) is not True:
            continue
        tags = {str(tag) for tag in sequence(item.get("tags"))}
        if tags.isdisjoint(include_tags):
            continue
        selected.append(
            WorkflowSelection(
                workflow_id=str(item["id"]),
                file=str(item["file"]),
                stage=int(item["stage"]),
                specialty=str(item.get("specialty", "UNCLASSIFIED")),
                wait_for_completion=True,
                timeout_minutes=int(item["timeout_minutes"]),
                inputs=dict(item.get("inputs") or {}),
                override_allowlist=tuple(item.get("override_allowlist") or ()),
                claim_allowed=False,
                publication_effect="NONE",
            )
        )
    selected.sort(key=lambda item: (item.stage, item.workflow_id))
    if not selected:
        raise ValueError(f"profile '{profile}' selected no workflows")
    return selected


def apply_overrides(
    selected: list[WorkflowSelection], overrides_json: str
) -> list[WorkflowSelection]:
    try:
        overrides = json.loads(overrides_json)
    except json.JSONDecodeError as exc:
        raise ValueError("--overrides must be valid JSON") from exc
    if not isinstance(overrides, dict):
        raise ValueError("--overrides must be a JSON object")
    by_id = {workflow.workflow_id: workflow for workflow in selected}
    unknown_workflows = sorted(set(overrides) - set(by_id))
    if unknown_workflows:
        raise ValueError(
            "override references unselected workflow(s): "
            + ", ".join(unknown_workflows)
        )

    result: list[WorkflowSelection] = []
    for workflow in selected:
        values = overrides.get(workflow.workflow_id, {})
        if not isinstance(values, dict):
            raise ValueError(f"overrides.{workflow.workflow_id} must be a JSON object")
        forbidden = sorted(set(values) - set(workflow.override_allowlist))
        if forbidden:
            raise ValueError(
                f"overrides.{workflow.workflow_id} contains forbidden input(s): "
                + ", ".join(forbidden)
            )
        if any(isinstance(value, (dict, list)) or value is None for value in values.values()):
            raise ValueError(
                f"overrides.{workflow.workflow_id} values must be non-null scalars"
            )
        result.append(replace(workflow, inputs={**workflow.inputs, **values}))
    return result


def format_workflow_input(value: Any) -> str:
    if isinstance(value, bool):
        return "true" if value else "false"
    return str(value)


def branch_from_ref(ref: str) -> str:
    branch = ref.removeprefix("refs/heads/")
    if (
        not branch
        or len(branch) > 255
        or branch.startswith(("/", "."))
        or branch.endswith(("/", ".", ".lock"))
        or ".." in branch
        or "//" in branch
        or "@{" in branch
        or "\\" in branch
        or INVALID_REF_CHARS_RE.search(branch)
        or any(part.startswith(".") for part in branch.split("/"))
        or FULL_SHA_RE.fullmatch(branch)
    ):
        raise ValueError(f"ref must be a valid branch name, got: {ref!r}")
    return branch


class ActionsClient:
    def __init__(self, repository: str, token: str) -> None:
        self.repository = repository
        self.token = token
        self._workflow_cache: dict[str, dict[str, Any]] = {}

    def _request(
        self, method: str, path: str, payload: dict[str, Any] | None = None
    ) -> dict[str, Any]:
        body = None
        headers = {
            "Accept": "application/vnd.github+json",
            "Authorization": "Bearer " + self.token,
            "X-GitHub-Api-Version": "2022-11-28",
        }
        if payload is not None:
            body = json.dumps(payload).encode("utf-8")
            headers["Content-Type"] = "application/json"
        req = request.Request(
            f"{API_ROOT}{path}", data=body, method=method, headers=headers
        )
        try:
            with request.urlopen(req, timeout=30) as response:
                raw = response.read().decode("utf-8")
                return json.loads(raw) if raw.strip() else {}
        except error.HTTPError as exc:
            detail = exc.read().decode("utf-8", errors="replace")
            raise RuntimeError(
                f"GitHub API {method} {path} failed: {exc.code} {detail}"
            ) from exc
        except (error.URLError, TimeoutError, UnicodeError, json.JSONDecodeError) as exc:
            raise RuntimeError(f"GitHub API {method} {path} failed: {exc}") from exc

    def resolve_ref(self, branch: str) -> str:
        encoded = parse.quote(branch, safe="")
        data = self._request("GET", f"/repos/{self.repository}/commits/{encoded}")
        sha = str(data.get("sha", ""))
        if not FULL_SHA_RE.fullmatch(sha):
            raise RuntimeError(f"GitHub API returned invalid commit SHA for {branch!r}")
        return sha

    def workflow_by_file(self, workflow_file: str) -> dict[str, Any]:
        if workflow_file not in self._workflow_cache:
            encoded = parse.quote(workflow_file, safe="")
            self._workflow_cache[workflow_file] = self._request(
                "GET", f"/repos/{self.repository}/actions/workflows/{encoded}"
            )
        return self._workflow_cache[workflow_file]

    def dispatch(self, workflow_file: str, ref: str, inputs: dict[str, Any]) -> None:
        payload: dict[str, Any] = {"ref": ref}
        if inputs:
            payload["inputs"] = {
                key: format_workflow_input(value) for key, value in inputs.items()
            }
        encoded = parse.quote(workflow_file, safe="")
        self._request(
            "POST",
            f"/repos/{self.repository}/actions/workflows/{encoded}/dispatches",
            payload,
        )

    def list_workflow_runs(self, workflow_id: int, branch: str) -> list[dict[str, Any]]:
        query = parse.urlencode(
            {"event": "workflow_dispatch", "branch": branch, "per_page": 50}
        )
        data = self._request(
            "GET",
            f"/repos/{self.repository}/actions/workflows/{workflow_id}/runs?{query}",
        )
        runs = data.get("workflow_runs", [])
        if not isinstance(runs, list):
            raise RuntimeError("GitHub API workflow_runs response is not a list")
        return runs

    def run(self, run_id: int) -> dict[str, Any]:
        return self._request(
            "GET", f"/repos/{self.repository}/actions/runs/{run_id}"
        )

    def cancel(self, run_id: int) -> None:
        self._request(
            "POST", f"/repos/{self.repository}/actions/runs/{run_id}/cancel"
        )


def find_dispatched_run(
    client: ActionsClient,
    workflow_numeric_id: int,
    branch: str,
    dispatched_at: datetime,
    known_run_ids: set[int] | None = None,
    timeout_seconds: int = 180,
) -> dict[str, Any]:
    deadline = time.time() + timeout_seconds
    threshold = dispatched_at - RUN_DISCOVERY_CLOCK_SKEW
    known = known_run_ids or set()
    while time.time() < deadline:
        candidates: list[tuple[datetime, dict[str, Any]]] = []
        for run in client.list_workflow_runs(workflow_numeric_id, branch):
            run_id = int(run["id"])
            if run_id in known:
                continue
            created_raw = str(run["created_at"])
            created = datetime.fromisoformat(
                created_raw.removesuffix("Z") + "+00:00"
                if created_raw.endswith("Z")
                else created_raw
            )
            if created >= threshold:
                candidates.append((created, run))
        if candidates:
            return max(candidates, key=lambda item: item[0])[1]
        time.sleep(5)
    raise RuntimeError("dispatched workflow run was not found within 180 seconds")


def wait_for_completion(
    client: ActionsClient, run_id: int, timeout_minutes: int
) -> dict[str, Any]:
    deadline = time.time() + timeout_minutes * 60
    while time.time() < deadline:
        run = client.run(run_id)
        if run.get("status") == "completed":
            return run
        time.sleep(15)
    raise RunTimeoutError(run_id, timeout_minutes)


def _workflow_record(workflow: WorkflowSelection) -> dict[str, Any]:
    return {
        "stage": workflow.stage,
        "specialty": workflow.specialty,
        "id": workflow.workflow_id,
        "file": workflow.file,
        "state": "NOT_STARTED",
        "dispatch": "not_requested",
        "status": "not_requested",
        "conclusion": "not_requested",
        "run_id": None,
        "html_url": "",
        "head_sha": "",
        "inputs_sha256": sha256_json(workflow.inputs),
        "claim_allowed": False,
        "scientific_gate": "BLOCKED",
        "publication_ready": False,
        "publication_effect": "NONE",
        "residuals": [],
    }


def build_payload(
    args: argparse.Namespace,
    catalog: dict[str, Any],
    selected: list[WorkflowSelection],
    commit_sha: str,
) -> dict[str, Any]:
    input_contract = {
        "catalog_sha256": catalog["catalog_sha256"],
        "profile": args.profile,
        "ref": args.ref,
        "dry_run": args.dry_run,
        "overrides_sha256": sha256_bytes(args.overrides.encode("utf-8")),
        "selected": [asdict(item) for item in selected],
    }
    inventory = list(catalog.get("workflow_inventory_rows") or [])
    class_counts: dict[str, int] = {}
    for row in inventory:
        key = str(row["classification"])
        class_counts[key] = class_counts.get(key, 0) + 1
    return {
        "schema": SCHEMA,
        "orchestration_id": "-".join(
            filter(
                None,
                [
                    os.environ.get("GITHUB_RUN_ID", "local"),
                    os.environ.get("GITHUB_RUN_ATTEMPT", "1"),
                    commit_sha[:12] if FULL_SHA_RE.fullmatch(commit_sha) else "token-vazio",
                ],
            )
        ),
        "commit_sha": commit_sha,
        "workflow": os.environ.get("GITHUB_WORKFLOW", ORCHESTRATOR_FILE),
        "job": os.environ.get("GITHUB_JOB", "local"),
        "claim_allowed": False,
        "scientific_gate": "BLOCKED",
        "publication_ready": False,
        "publication_effect": "NONE",
        "inputs_sha256": sha256_json(input_contract),
        "catalog_sha256": catalog["catalog_sha256"],
        "decision": "BLOCKED",
        "failed": False,
        "profile": args.profile,
        "ref": args.ref,
        "dry_run": args.dry_run,
        "wait": True,
        "fail_fast": True,
        "execution": catalog["execution"],
        "started_at": utc_now(),
        "completed_at": None,
        "inventory_summary": {
            "workflow_files": len(inventory),
            "classifications": class_counts,
        },
        "workflow_inventory": inventory,
        "workflows": [_workflow_record(item) for item in selected],
        "residuals": list(catalog.get("catalog_residuals") or []),
    }


def mark_remaining_blocked(
    payload: dict[str, Any], start_index: int, cause: str
) -> None:
    for row in payload["workflows"][start_index:]:
        if row["state"] == "NOT_STARTED":
            row["state"] = "BLOCKED"
            row["status"] = "not_run"
            row["conclusion"] = "not_run"
            row["residuals"].append(f"UPSTREAM_BLOCK:{cause}")


def write_reports(output_dir: Path, payload: dict[str, Any]) -> None:
    output_dir.mkdir(parents=True, exist_ok=True)
    encoded = json.dumps(payload, indent=2, ensure_ascii=False) + "\n"
    (output_dir / "orchestration_receipt.json").write_text(
        encoded, encoding="utf-8"
    )
    # Compatibility path for consumers of v1.
    (output_dir / "orchestration_summary.json").write_text(
        encoded, encoding="utf-8"
    )

    with (output_dir / "workflow_inventory.tsv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle, delimiter="\t")
        writer.writerow(
            ["path", "sha256", "triggers", "dispatchable", "classification"]
        )
        for row in payload.get("workflow_inventory", []):
            writer.writerow(
                [
                    row["path"],
                    row["sha256"],
                    ",".join(row["triggers"]),
                    str(row["dispatchable"]).lower(),
                    row["classification"],
                ]
            )

    lines = [
        "# RLL Transit Tower — Orchestration Receipt",
        "",
        f"- decision: `{payload['decision']}`",
        f"- profile: `{payload.get('profile', 'TOKEN_VAZIO')}`",
        f"- ref: `{payload.get('ref', 'TOKEN_VAZIO')}`",
        f"- commit_sha: `{payload.get('commit_sha', 'TOKEN_VAZIO')}`",
        f"- inputs_sha256: `{payload.get('inputs_sha256', 'TOKEN_VAZIO')}`",
        "- claim_allowed: `false`",
        "- scientific_gate: `BLOCKED`",
        "- publication_ready: `false`",
        "- publication_effect: `NONE`",
        "",
        "| stage | specialty | id | file | state | conclusion | run |",
        "|---:|---|---|---|---|---|---|",
    ]
    for row in payload.get("workflows", []):
        run_link = row.get("html_url") or ""
        lines.append(
            "| {stage} | `{specialty}` | `{id}` | `{file}` | `{state}` | "
            "`{conclusion}` | {run} |".format(
                stage=row.get("stage", ""),
                specialty=row.get("specialty", ""),
                id=row.get("id", ""),
                file=row.get("file", ""),
                state=row.get("state", ""),
                conclusion=row.get("conclusion", ""),
                run=run_link,
            )
        )
    lines.extend(["", "## Residuals", ""])
    residuals = payload.get("residuals", [])
    lines.extend(f"- `{item}`" for item in residuals)
    if not residuals:
        lines.append("- `NONE`")
    lines.extend(
        [
            "",
            "## Claim boundary",
            "",
            "A PASS proves only that the selected repository workflows completed "
            "for the recorded commit. It does not prove RLL, model preference, "
            "publication readiness, independent replication, or physical execution.",
        ]
    )
    (output_dir / "ORCHESTRATION_REPORT.md").write_text(
        "\n".join(lines) + "\n", encoding="utf-8"
    )


def failure_payload(args: argparse.Namespace, message: str) -> dict[str, Any]:
    commit_sha = os.environ.get(
        "ORCHESTRATION_COMMIT_SHA",
        os.environ.get("GITHUB_SHA", "TOKEN_VAZIO_LOCAL_COMMIT"),
    )
    return {
        "schema": SCHEMA,
        "orchestration_id": "local-failure",
        "commit_sha": commit_sha,
        "workflow": os.environ.get("GITHUB_WORKFLOW", ORCHESTRATOR_FILE),
        "job": os.environ.get("GITHUB_JOB", "local"),
        "claim_allowed": False,
        "scientific_gate": "BLOCKED",
        "publication_ready": False,
        "publication_effect": "NONE",
        "inputs_sha256": sha256_json(
            {
                "profile": getattr(args, "profile", "TOKEN_VAZIO"),
                "ref": getattr(args, "ref", "TOKEN_VAZIO"),
            }
        ),
        "decision": "BLOCKED",
        "failed": True,
        "profile": getattr(args, "profile", "TOKEN_VAZIO"),
        "ref": getattr(args, "ref", "TOKEN_VAZIO"),
        "dry_run": bool(getattr(args, "dry_run", False)),
        "wait": bool(getattr(args, "wait", False)),
        "fail_fast": bool(getattr(args, "fail_fast", False)),
        "started_at": utc_now(),
        "completed_at": utc_now(),
        "workflow_inventory": [],
        "workflows": [],
        "residuals": [f"ORCHESTRATOR_PREFLIGHT_BLOCKED:{message}"],
    }


def run(args: argparse.Namespace) -> tuple[int, dict[str, Any]]:
    if not args.wait or not args.fail_fast:
        raise ValueError("sequential transit requires --wait and --fail-fast")
    branch = branch_from_ref(args.ref)
    catalog = load_and_expand_catalog(Path(args.catalog))
    selected = apply_overrides(
        select_workflows(catalog, args.profile), args.overrides
    )

    token = os.environ.get("GITHUB_TOKEN", "")
    repository = os.environ.get("GITHUB_REPOSITORY", "")
    client: ActionsClient | None = None
    if args.dry_run:
        commit_sha = os.environ.get(
            "ORCHESTRATION_COMMIT_SHA",
            os.environ.get("GITHUB_SHA", "TOKEN_VAZIO_LOCAL_COMMIT"),
        )
    else:
        if not token or not repository:
            raise RuntimeError(
                "GITHUB_TOKEN and GITHUB_REPOSITORY are required for dispatch"
            )
        client = ActionsClient(repository, token)
        commit_sha = client.resolve_ref(branch)
        checked_out_sha = os.environ.get("GITHUB_SHA", "")
        if checked_out_sha and checked_out_sha != commit_sha:
            raise RuntimeError(
                f"TARGET_REF_DRIFT: checkout={checked_out_sha} resolved={commit_sha}"
            )

    payload = build_payload(args, catalog, selected, commit_sha)
    if args.dry_run:
        for row in payload["workflows"]:
            row["state"] = "OBSERVED_LIMITED"
            row["dispatch"] = "dry_run"
            row["status"] = "planned"
            row["conclusion"] = "not_executed"
            row["residuals"].append("DRY_RUN_NO_CHILD_EXECUTION")
        payload["decision"] = "OBSERVED_LIMITED"
        payload["residuals"].append("DRY_RUN_NO_CHILD_EXECUTION")
        payload["completed_at"] = utc_now()
        return 0, payload

    if client is None:
        raise RuntimeError("internal client initialization failure")

    metadata: dict[str, dict[str, Any]] = {}
    for workflow in selected:
        meta = client.workflow_by_file(workflow.file)
        if str(meta.get("state", "active")) != "active":
            raise RuntimeError(
                f"workflow is not active: {workflow.file} state={meta.get('state')}"
            )
        if not str(meta.get("id", "")).isdigit():
            raise RuntimeError(f"workflow has invalid numeric id: {workflow.file}")
        metadata[workflow.workflow_id] = meta

    for index, workflow in enumerate(selected):
        row = payload["workflows"][index]
        run_id: int | None = None
        try:
            meta = metadata[workflow.workflow_id]
            workflow_numeric_id = int(meta["id"])
            known_run_ids = {
                int(item["id"])
                for item in client.list_workflow_runs(workflow_numeric_id, branch)
            }
            dispatched_at = datetime.now(timezone.utc)
            client.dispatch(workflow.file, branch, workflow.inputs)
            row["dispatch"] = "ok"
            row["state"] = "DISPATCHED"
            row["status"] = "queued"
            discovered = find_dispatched_run(
                client,
                workflow_numeric_id,
                branch,
                dispatched_at,
                known_run_ids=known_run_ids,
            )
            run_id = int(discovered["id"])
            row["run_id"] = run_id
            row["html_url"] = str(discovered.get("html_url", ""))
            final_run = wait_for_completion(
                client, run_id, workflow.timeout_minutes
            )
            row["status"] = str(final_run.get("status", "unknown"))
            row["conclusion"] = str(final_run.get("conclusion", "unknown"))
            row["html_url"] = str(final_run.get("html_url", row["html_url"]))
            row["head_sha"] = str(final_run.get("head_sha", ""))
            if row["head_sha"] != commit_sha:
                row["state"] = "BLOCKED"
                row["residuals"].append(
                    f"CHILD_HEAD_SHA_DRIFT:{row['head_sha']}:{commit_sha}"
                )
                payload["decision"] = "BLOCKED"
                payload["failed"] = True
                payload["residuals"].append(
                    f"CHILD_HEAD_SHA_DRIFT:{workflow.workflow_id}"
                )
                mark_remaining_blocked(payload, index + 1, workflow.workflow_id)
                break
            if row["conclusion"] != "success":
                row["state"] = "FAIL"
                row["residuals"].append(
                    f"CHILD_CONCLUSION:{row['conclusion']}"
                )
                payload["decision"] = "FAIL"
                payload["failed"] = True
                payload["residuals"].append(
                    f"CHILD_FAILED:{workflow.workflow_id}:{row['conclusion']}"
                )
                mark_remaining_blocked(payload, index + 1, workflow.workflow_id)
                break
            row["state"] = "PASS"
        except RunTimeoutError as exc:
            run_id = exc.run_id
            row["state"] = "BLOCKED"
            row["status"] = "timeout"
            row["conclusion"] = "cancel_requested"
            row["residuals"].append("CHILD_TIMEOUT")
            try:
                client.cancel(run_id)
            except RuntimeError as cancel_exc:
                row["residuals"].append(f"CANCEL_FAILED:{cancel_exc}")
            payload["decision"] = "BLOCKED"
            payload["failed"] = True
            payload["residuals"].append(
                f"CHILD_TIMEOUT:{workflow.workflow_id}:{run_id}"
            )
            mark_remaining_blocked(payload, index + 1, workflow.workflow_id)
            break
        except (RuntimeError, ValueError, KeyError, TypeError) as exc:
            row["state"] = "BLOCKED"
            row["dispatch"] = "error"
            row["status"] = "error"
            row["conclusion"] = "error"
            row["residuals"].append(str(exc))
            if run_id is not None:
                try:
                    client.cancel(run_id)
                    row["residuals"].append("CANCEL_REQUESTED")
                except RuntimeError as cancel_exc:
                    row["residuals"].append(f"CANCEL_FAILED:{cancel_exc}")
            payload["decision"] = "BLOCKED"
            payload["failed"] = True
            payload["residuals"].append(
                f"ORCHESTRATION_BLOCKED:{workflow.workflow_id}:{exc}"
            )
            mark_remaining_blocked(payload, index + 1, workflow.workflow_id)
            break
    else:
        payload["decision"] = "PASS"

    payload["completed_at"] = utc_now()
    return (1 if payload["failed"] else 0), payload


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--catalog", required=True)
    parser.add_argument("--profile", required=True)
    parser.add_argument("--ref", required=True)
    parser.add_argument("--wait", action="store_true")
    parser.add_argument("--fail-fast", action="store_true")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--overrides", default="{}")
    parser.add_argument("--output-dir", required=True)
    return parser


def main(argv: Iterable[str] | None = None) -> int:
    args = build_parser().parse_args(list(argv) if argv is not None else None)
    output_dir = Path(args.output_dir)
    try:
        code, payload = run(args)
    except (OSError, UnicodeError, RuntimeError, ValueError, KeyError, TypeError) as exc:
        payload = failure_payload(args, str(exc))
        code = 2
    write_reports(output_dir, payload)
    print(
        json.dumps(
            {
                "schema": payload["schema"],
                "decision": payload["decision"],
                "commit_sha": payload["commit_sha"],
                "selected": len(payload.get("workflows", [])),
                "residuals": len(payload.get("residuals", [])),
            },
            ensure_ascii=False,
            indent=2,
        )
    )
    return code


if __name__ == "__main__":
    raise SystemExit(main())
