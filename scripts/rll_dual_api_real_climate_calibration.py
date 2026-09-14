#!/usr/bin/env python3
"""RLL dual-API real climate calibration.

GitHub API is used only for provenance/control-plane custody.
Climate Engine API is used for real external climate compute/data products.

SECRET != AUTHORITY != EXECUTION != EVIDENCE != CLAIM
GITHUB_PROVENANCE != CLIMATE_SCIENTIFIC_SIGNAL
"""
from __future__ import annotations

import argparse
import hashlib
import json
import math
import os
import re
import statistics
import sys
import urllib.error
import urllib.parse
import urllib.request
from datetime import datetime, timezone
from pathlib import Path
from typing import Any

GITHUB_API = "https://api.github.com"
CLIMATE_API = "https://api.climateengine.org"
ENV_NAME_RE = re.compile(r"^[A-Z_][A-Z0-9_]*$")
GIT_SELECTOR = "RLL_AGENT_GITHUB_PAT_ENV"
CLIMATE_SELECTOR = "RLL_AGENT_CLIMATE_KEY_ENV"
GIT_ALIASES = (
    "PATGITHUB",
    "RLL_AGENT_PAT",
    "AGENT_GITHUB_PAT",
    "AGENT_PAT",
    "GH_PAT",
    "GIT_PAT",
    "PAT_GIT",
    "GITHUB_TOKEN",
)
CLIMATE_ALIASES = (
    "CLIMATE",
    "CLIMA",
    "CLIMATE_ENGINE_API_KEY",
    "RLL_CLIMATE_ENGINE_TRIAL_TOKEN",
)
MAX_BYTES = 8 * 1024 * 1024


class CalibrationError(RuntimeError):
    pass


def utc_now() -> str:
    return datetime.now(timezone.utc).isoformat().replace("+00:00", "Z")


def resolve_secret(selector_name: str, aliases: tuple[str, ...]) -> tuple[str | None, str | None]:
    selector = os.environ.get(selector_name, "").strip()
    if selector:
        if not ENV_NAME_RE.fullmatch(selector):
            raise CalibrationError(f"TOKEN_VAZIO_INVALID_SELECTOR:{selector_name}")
        value = os.environ.get(selector)
        if not value:
            raise CalibrationError(f"TOKEN_VAZIO_SELECTED_SECRET_ABSENT:{selector_name}")
        return selector, value

    present = [name for name in aliases if os.environ.get(name)]
    if not present:
        return None, None
    if len(present) > 1:
        raise CalibrationError(f"TOKEN_VAZIO_AMBIGUOUS_SECRET:{selector_name}")
    name = present[0]
    return name, os.environ[name]


def _json_request(
    url: str,
    *,
    token: str,
    method: str = "GET",
    body: dict[str, Any] | None = None,
    auth_header: str = "Authorization",
    auth_prefix: str = "",
    timeout: int = 30,
    max_bytes: int = MAX_BYTES,
    user_agent: str = "RLL-DualAPI-Calibration/1",
) -> tuple[int, Any, str, int]:
    parsed = urllib.parse.urlparse(url)
    if parsed.scheme != "https":
        raise CalibrationError("NON_HTTPS_URL_FORBIDDEN")

    payload = None
    headers = {
        "Accept": "application/json",
        "User-Agent": user_agent,
        auth_header: f"{auth_prefix}{token}",
    }
    if body is not None:
        payload = json.dumps(body, separators=(",", ":")).encode("utf-8")
        headers["Content-Type"] = "application/json"

    req = urllib.request.Request(url, data=payload, headers=headers, method=method)
    try:
        with urllib.request.urlopen(req, timeout=timeout) as response:
            raw = response.read(max_bytes + 1)
            if len(raw) > max_bytes:
                raise CalibrationError("RESPONSE_BYTE_CAP_EXCEEDED")
            sha = hashlib.sha256(raw).hexdigest()
            decoded = json.loads(raw.decode("utf-8"))
            return int(response.status), decoded, sha, len(raw)
    except urllib.error.HTTPError as exc:
        raw = exc.read(max_bytes + 1)
        if len(raw) > max_bytes:
            raise CalibrationError("ERROR_RESPONSE_BYTE_CAP_EXCEEDED")
        sha = hashlib.sha256(raw).hexdigest()
        try:
            decoded = json.loads(raw.decode("utf-8"))
        except Exception:
            decoded = {"error": f"HTTP_{exc.code}"}
        return int(exc.code), decoded, sha, len(raw)


def github_provenance(repository: str, ref: str, token: str) -> dict[str, Any]:
    status_repo, repo, repo_sha, repo_bytes = _json_request(
        f"{GITHUB_API}/repos/{repository}",
        token=token,
        auth_prefix="Bearer ",
        user_agent="RLL-DualAPI-GitHub-Provenance/1",
    )
    if status_repo != 200 or not isinstance(repo, dict):
        raise CalibrationError(f"GITHUB_REPOSITORY_PROBE_FAILED:{status_repo}")

    status_commit, commit, commit_sha, commit_bytes = _json_request(
        f"{GITHUB_API}/repos/{repository}/commits/{urllib.parse.quote(ref, safe='')}",
        token=token,
        auth_prefix="Bearer ",
        user_agent="RLL-DualAPI-GitHub-Provenance/1",
    )
    if status_commit != 200 or not isinstance(commit, dict):
        raise CalibrationError(f"GITHUB_COMMIT_PROBE_FAILED:{status_commit}")

    return {
        "role": "CONTROL_PLANE_PROVENANCE_NOT_SCIENTIFIC_CALIBRATION",
        "repository": repository,
        "repository_id": repo.get("id"),
        "default_branch": repo.get("default_branch"),
        "requested_ref": ref,
        "resolved_commit_sha": commit.get("sha"),
        "repository_response_sha256": repo_sha,
        "commit_response_sha256": commit_sha,
        "repository_response_bytes": repo_bytes,
        "commit_response_bytes": commit_bytes,
        "claim_allowed": False,
    }


def climate_metadata(dataset: str, token: str) -> dict[str, Any]:
    query = urllib.parse.urlencode({"dataset": dataset})
    out: dict[str, Any] = {}
    for name, path in (
        ("dataset_dates", "/metadata/dataset_dates"),
        ("dataset_variables", "/metadata/dataset_variables"),
    ):
        status, payload, sha, size = _json_request(
            f"{CLIMATE_API}{path}?{query}",
            token=token,
            method="GET",
            user_agent="RLL-DualAPI-ClimateMetadata/1",
        )
        out[name] = {
            "http_status": status,
            "response_sha256": sha,
            "response_bytes": size,
            "payload": payload,
        }
    return out


def climate_timeseries(
    *,
    dataset: str,
    variable: str,
    coordinates: Any,
    start_date: str,
    end_date: str,
    area_reducer: str,
    token: str,
) -> tuple[int, Any, str, int]:
    body = {
        "dataset": dataset,
        "variable": variable,
        "coordinates": coordinates,
        "start_date": start_date,
        "end_date": end_date,
        "area_reducer": area_reducer,
    }
    return _json_request(
        f"{CLIMATE_API}/timeseries/native/coordinates",
        token=token,
        method="POST",
        body=body,
        user_agent="RLL-DualAPI-ClimateTimeseries/1",
    )


def _candidate_row_lists(value: Any, variable: str) -> list[list[dict[str, Any]]]:
    found: list[list[dict[str, Any]]] = []
    if isinstance(value, list):
        if value and all(isinstance(item, dict) for item in value):
            if any(variable in item for item in value):
                found.append(value)
        for item in value:
            found.extend(_candidate_row_lists(item, variable))
    elif isinstance(value, dict):
        for item in value.values():
            found.extend(_candidate_row_lists(item, variable))
    return found


def extract_rows(payload: Any, variable: str) -> list[dict[str, Any]]:
    if isinstance(payload, dict):
        data = payload.get("Data")
        if isinstance(data, list) and data:
            first = data[0]
            if isinstance(first, dict) and isinstance(first.get("Data"), list):
                rows = first["Data"]
                if all(isinstance(item, dict) for item in rows):
                    return rows
    candidates = _candidate_row_lists(payload, variable)
    return max(candidates, key=len) if candidates else []


def numeric_values(rows: list[dict[str, Any]], variable: str) -> list[float]:
    values: list[float] = []
    for row in rows:
        value = row.get(variable)
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            continue
        f = float(value)
        if not math.isfinite(f):
            continue
        if f == -9999.0:
            continue
        values.append(f)
    return values


def stats(values: list[float]) -> dict[str, Any]:
    if not values:
        return {
            "state": "TOKEN_VAZIO_NO_NUMERIC_SAMPLES",
            "n": 0,
            "mean": None,
            "std_population": None,
            "min": None,
            "max": None,
        }
    return {
        "state": "OBSERVED_PROVIDER_VALUES",
        "n": len(values),
        "mean": statistics.fmean(values),
        "std_population": statistics.pstdev(values),
        "min": min(values),
        "max": max(values),
    }


def calibration_metrics(baseline: dict[str, Any], target: dict[str, Any]) -> dict[str, Any]:
    if baseline["n"] == 0 or target["n"] == 0:
        return {
            "state": "TOKEN_VAZIO_INSUFFICIENT_REAL_SAMPLES",
            "delta_mean": None,
            "z_shift_vs_baseline": None,
            "ratio_target_to_baseline": None,
        }

    delta = target["mean"] - baseline["mean"]
    std = baseline["std_population"]
    z = delta / std if std not in (None, 0.0) else None
    base = baseline["mean"]
    ratio = target["mean"] / base if base not in (None, 0.0) else None
    return {
        "state": "REAL_PROVIDER_CALIBRATION_SUMMARY",
        "delta_mean": delta,
        "z_shift_vs_baseline": z,
        "ratio_target_to_baseline": ratio,
    }


def canonical_coordinate_info(coordinates: Any) -> dict[str, Any]:
    encoded = json.dumps(coordinates, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    point_count = 0
    if isinstance(coordinates, list):
        point_count = len(coordinates)
    return {
        "coordinates_sha256": hashlib.sha256(encoded).hexdigest(),
        "top_level_geometry_count": point_count,
        "coordinates_persisted_in_receipt": False,
    }


def run(args: argparse.Namespace) -> tuple[dict[str, Any], int]:
    coords = json.loads(args.coordinates)
    receipt: dict[str, Any] = {
        "schema": "rll.dual_api_real_climate_calibration.receipt.v1",
        "generated_at_utc": utc_now(),
        "mode": "REAL_API_EXECUTION" if args.execute else "DRY_RUN",
        "claim_allowed": False,
        "separation": {
            "github_api_role": "CONTROL_PLANE_PROVENANCE_NOT_SCIENTIFIC_CALIBRATION",
            "climate_api_role": "EXTERNAL_COMPUTE_PRODUCT_FOR_CALIBRATION",
            "source_compute_evidence_claim_separated": True,
        },
        "request": {
            "dataset": args.dataset,
            "variable": args.variable,
            "area_reducer": args.area_reducer,
            "baseline": [args.baseline_start_date, args.baseline_end_date],
            "target": [args.target_start_date, args.target_end_date],
            **canonical_coordinate_info(coords),
        },
        "credential_receipt": {
            "secret_value_observed": False,
            "secret_value_hashed": False,
            "secret_length_observed": False,
        },
        "gaps": [],
    }

    if not args.execute:
        receipt["gate_status"] = "DRY_RUN_READY"
        receipt["F_next"] = "Execute only in a reviewed manual runtime with both selector-resolved credentials."
        return receipt, 0

    try:
        git_name, git_token = resolve_secret(GIT_SELECTOR, GIT_ALIASES)
        climate_name, climate_token = resolve_secret(CLIMATE_SELECTOR, CLIMATE_ALIASES)
    except CalibrationError as exc:
        receipt["gate_status"] = "BLOCKED_CREDENTIAL_RESOLUTION"
        receipt["gaps"].append(str(exc))
        return receipt, 3

    receipt["credential_receipt"]["github_binding_present"] = bool(git_token)
    receipt["credential_receipt"]["climate_binding_present"] = bool(climate_token)
    receipt["credential_receipt"]["github_binding_name"] = git_name or "TOKEN_VAZIO"
    receipt["credential_receipt"]["climate_binding_name"] = climate_name or "TOKEN_VAZIO"

    if not git_token:
        receipt["gaps"].append("TOKEN_VAZIO_AGENT_GITHUB_AUTHORITY")
    if not climate_token:
        receipt["gaps"].append("TOKEN_VAZIO_CLIMATE_ENGINE_AUTHORITY")
    if receipt["gaps"]:
        receipt["gate_status"] = "BLOCKED_CREDENTIAL"
        return receipt, 3

    try:
        receipt["github_provenance"] = github_provenance(args.repository, args.ref, git_token)
        receipt["climate_metadata"] = climate_metadata(args.dataset, climate_token)

        b_status, b_payload, b_sha, b_bytes = climate_timeseries(
            dataset=args.dataset,
            variable=args.variable,
            coordinates=coords,
            start_date=args.baseline_start_date,
            end_date=args.baseline_end_date,
            area_reducer=args.area_reducer,
            token=climate_token,
        )
        t_status, t_payload, t_sha, t_bytes = climate_timeseries(
            dataset=args.dataset,
            variable=args.variable,
            coordinates=coords,
            start_date=args.target_start_date,
            end_date=args.target_end_date,
            area_reducer=args.area_reducer,
            token=climate_token,
        )
    except (CalibrationError, ValueError, json.JSONDecodeError) as exc:
        receipt["gate_status"] = "API_EXECUTION_FAILED"
        receipt["gaps"].append(type(exc).__name__ + ":" + str(exc))
        return receipt, 4

    receipt["climate_responses"] = {
        "baseline": {"http_status": b_status, "response_sha256": b_sha, "response_bytes": b_bytes},
        "target": {"http_status": t_status, "response_sha256": t_sha, "response_bytes": t_bytes},
    }

    if b_status != 200 or t_status != 200:
        receipt["gate_status"] = "CLIMATE_HTTP_FAILURE"
        receipt["gaps"].append(f"baseline_http={b_status}")
        receipt["gaps"].append(f"target_http={t_status}")
        return receipt, 5

    baseline_rows = extract_rows(b_payload, args.variable)
    target_rows = extract_rows(t_payload, args.variable)
    baseline_stats = stats(numeric_values(baseline_rows, args.variable))
    target_stats = stats(numeric_values(target_rows, args.variable))
    receipt["calibration"] = {
        "baseline": baseline_stats,
        "target": target_stats,
        "comparison": calibration_metrics(baseline_stats, target_stats),
        "provider_state": "EXTERNAL_COMPUTE_PRODUCT",
        "upstream_dataset_authority": "PRESERVE_CLIMATE_ENGINE_UPSTREAM_DATASET_AUTHORITY",
        "causal_claim": "TOKEN_VAZIO",
    }

    if baseline_stats["n"] == 0 or target_stats["n"] == 0:
        receipt["gate_status"] = "REAL_API_OBSERVED_BUT_CALIBRATION_TOKEN_VAZIO"
        receipt["gaps"].append("TOKEN_VAZIO_PROVIDER_SCHEMA_OR_NUMERIC_DATA")
        return receipt, 6

    receipt["gate_status"] = "REAL_API_CALIBRATION_OBSERVED"
    receipt["F_next"] = "Map this provider variable to one declared RLL 8x8 variable with unit conversion and an independent primary-source comparison before any ΔOBS promotion."
    return receipt, 0


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY", "instituto-Rafael/relativity-living-light"))
    parser.add_argument("--ref", default=os.environ.get("GITHUB_SHA", "main"))
    parser.add_argument("--dataset", required=True)
    parser.add_argument("--variable", required=True)
    parser.add_argument("--coordinates", required=True)
    parser.add_argument("--area-reducer", default="mean", choices=["mean", "median", "min", "max"])
    parser.add_argument("--baseline-start-date", required=True)
    parser.add_argument("--baseline-end-date", required=True)
    parser.add_argument("--target-start-date", required=True)
    parser.add_argument("--target-end-date", required=True)
    parser.add_argument("--execute", action="store_true")
    parser.add_argument("--receipt", default="artifacts/science/climate/dual_api_calibration/receipt.json")
    args = parser.parse_args()

    receipt, rc = run(args)
    path = Path(args.receipt)
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(receipt, indent=2, ensure_ascii=False, sort_keys=True) + "\n", encoding="utf-8")
    print(json.dumps({
        "schema": receipt["schema"],
        "mode": receipt["mode"],
        "gate_status": receipt.get("gate_status"),
        "claim_allowed": False,
        "receipt": str(path),
    }, ensure_ascii=False))
    return rc


if __name__ == "__main__":
    raise SystemExit(main())
