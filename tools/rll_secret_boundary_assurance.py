#!/usr/bin/env python3
"""Sanitized assurance for RLL external credentials.

This tool never persists, hashes, or prints secret values. It separates the
GitHub authority probe from the Climate Engine trial-token inspection and emits
only sanitized receipts.
"""
from __future__ import annotations

import argparse
import base64
import hashlib
import json
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

SCHEMA = "rll.secret_boundary_assurance.v1"
CLAIM_BOUNDARY = (
    "Credential presence/authentication metadata only; no scientific, "
    "dataset-rights, or publication claim."
)


def _now_epoch() -> int:
    return int(datetime.now(tz=timezone.utc).timestamp())


def _iso_epoch(value: int | float) -> str:
    return datetime.fromtimestamp(value, tz=timezone.utc).isoformat().replace("+00:00", "Z")


def token_kind(token: str) -> str:
    for prefix, kind in (
        ("github_pat_", "github_fine_grained_pat"),
        ("ghp_", "github_classic_pat"),
        ("gho_", "github_oauth_token"),
        ("ghu_", "github_user_to_server_token"),
        ("ghs_", "github_server_to_server_token"),
        ("ghr_", "github_refresh_token"),
    ):
        if token.startswith(prefix):
            return kind
    if token.count(".") == 2:
        return "jwt"
    return "opaque"


def jwt_metadata(token: str, now: int | None = None) -> dict[str, Any]:
    result: dict[str, Any] = {
        "format": token_kind(token),
        "expiry_observed": False,
        "expires_at_utc": "TOKEN_VAZIO",
        "remaining_seconds": "TOKEN_VAZIO",
        "expired": "TOKEN_VAZIO",
    }
    if token.count(".") != 2:
        return result
    try:
        payload_segment = token.split(".", 2)[1]
        payload_segment += "=" * (-len(payload_segment) % 4)
        payload = json.loads(base64.urlsafe_b64decode(payload_segment.encode("ascii")))
    except (ValueError, UnicodeDecodeError, json.JSONDecodeError):
        result["format"] = "jwt_unparseable_payload"
        return result
    exp = payload.get("exp") if isinstance(payload, dict) else None
    if not isinstance(exp, (int, float)):
        return result
    current = _now_epoch() if now is None else int(now)
    remaining = int(exp) - current
    result.update(
        {
            "format": "jwt",
            "expiry_observed": True,
            "expires_at_utc": _iso_epoch(exp),
            "remaining_seconds": remaining,
            "expired": remaining <= 0,
        }
    )
    return result


def github_scope_observation(scope_header: str | None) -> dict[str, Any]:
    if not scope_header:
        return {
            "scope_introspection": "TOKEN_VAZIO_SCOPE_INTROSPECTION",
            "classic_scopes": [],
            "delete_repo_scope": "TOKEN_VAZIO",
        }
    scopes = sorted({item.strip() for item in scope_header.split(",") if item.strip()})
    return {
        "scope_introspection": "OBSERVED_CLASSIC_SCOPE_HEADER",
        "classic_scopes": scopes,
        "delete_repo_scope": "OBSERVED_PRESENT" if "delete_repo" in scopes else "OBSERVED_ABSENT",
    }


def _header(headers: Any, name: str) -> str | None:
    for key, value in headers.items():
        if str(key).lower() == name.lower():
            return str(value)
    return None


def github_probe(token: str, repository: str) -> dict[str, Any]:
    if not token:
        return {
            "secret_present": False,
            "token_kind": "TOKEN_VAZIO",
            "http_status": "TOKEN_VAZIO",
            "authentication": "TOKEN_VAZIO_SECRET_NOT_AVAILABLE",
            "token_expiration_header": "TOKEN_VAZIO",
            **github_scope_observation(None),
            "deletion_probe_performed": False,
        }

    url = f"https://api.github.com/repos/{repository}"
    request = Request(
        url,
        method="GET",
        headers={
            "Authorization": f"Bearer {token}",
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "RLL-secret-boundary-assurance/1.0",
        },
    )
    status: int | str
    headers: Any = {}
    try:
        with urlopen(request, timeout=12) as response:
            status = int(response.status)
            headers = response.headers
    except HTTPError as exc:
        status = int(exc.code)
        headers = exc.headers
    except URLError:
        status = "NETWORK_ERROR"

    scopes = github_scope_observation(_header(headers, "X-OAuth-Scopes"))
    auth_state = "PASS_AUTHENTICATED_READ" if status == 200 else "FAIL_AUTHENTICATION_OR_AUTHORITY"
    return {
        "secret_present": True,
        "token_kind": token_kind(token),
        "http_status": status,
        "authentication": auth_state,
        "token_expiration_header": _header(headers, "GitHub-Authentication-Token-Expiration")
        or "TOKEN_VAZIO",
        **scopes,
        "deletion_probe_performed": False,
    }


def climate_public_contract() -> dict[str, Any]:
    url = "https://api.climateengine.org/openapi.json"
    request = Request(url, method="GET", headers={"User-Agent": "RLL-secret-boundary-assurance/1.0"})
    try:
        with urlopen(request, timeout=12) as response:
            payload = json.loads(response.read())
        schemes = payload.get("components", {}).get("securitySchemes", {})
        api_key = schemes.get("APIKeyHeader", {})
        return {
            "openapi_observed": True,
            "auth_type": api_key.get("type", "TOKEN_VAZIO"),
            "auth_location": api_key.get("in", "TOKEN_VAZIO"),
            "auth_header_name": api_key.get("name", "TOKEN_VAZIO"),
        }
    except (HTTPError, URLError, ValueError, json.JSONDecodeError):
        return {
            "openapi_observed": False,
            "auth_type": "TOKEN_VAZIO",
            "auth_location": "TOKEN_VAZIO",
            "auth_header_name": "TOKEN_VAZIO",
        }


def climate_probe(token: str) -> dict[str, Any]:
    contract = climate_public_contract()
    if not token:
        return {
            "secret_present": False,
            "token_metadata": {
                "format": "TOKEN_VAZIO",
                "expiry_observed": False,
                "expires_at_utc": "TOKEN_VAZIO",
                "remaining_seconds": "TOKEN_VAZIO",
                "expired": "TOKEN_VAZIO",
            },
            "live_token_validation": "TOKEN_VAZIO_NOT_PERFORMED",
            **contract,
        }
    return {
        "secret_present": True,
        "token_metadata": jwt_metadata(token),
        "live_token_validation": "TOKEN_VAZIO_NOT_PERFORMED",
        **contract,
    }


def _inputs_sha256() -> str:
    safe = {
        "repository": os.environ.get("GITHUB_REPOSITORY", "TOKEN_VAZIO"),
        "run_id": os.environ.get("GITHUB_RUN_ID", "TOKEN_VAZIO"),
        "run_attempt": os.environ.get("GITHUB_RUN_ATTEMPT", "TOKEN_VAZIO"),
        "workflow": os.environ.get("GITHUB_WORKFLOW", "TOKEN_VAZIO"),
        "sha": os.environ.get("GITHUB_SHA", "TOKEN_VAZIO"),
    }
    raw = json.dumps(safe, sort_keys=True, separators=(",", ":")).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def base_receipt(kind: str) -> dict[str, Any]:
    return {
        "schema": SCHEMA,
        "kind": kind,
        "commit_sha": os.environ.get("GITHUB_SHA", "TOKEN_VAZIO"),
        "workflow": os.environ.get("GITHUB_WORKFLOW", "TOKEN_VAZIO"),
        "job": os.environ.get("GITHUB_JOB", "TOKEN_VAZIO"),
        "claim_allowed": False,
        "publication_effect": "NONE",
        "inputs_sha256": _inputs_sha256(),
        "secret_material_persisted": False,
        "secret_hash_persisted": False,
        "claim_boundary": CLAIM_BOUNDARY,
    }


def github_receipt() -> dict[str, Any]:
    receipt = base_receipt("github_pat")
    probe = github_probe(
        os.environ.get("RLL_GITHUB_PAT", ""),
        os.environ.get("GITHUB_REPOSITORY", "instituto-Rafael/relativity-living-light"),
    )
    residuals: list[str] = []
    if not probe["secret_present"]:
        residuals.append("TOKEN_VAZIO_RLL_GITHUB_PAT")
    if probe["scope_introspection"] == "TOKEN_VAZIO_SCOPE_INTROSPECTION":
        residuals.append("TOKEN_VAZIO_GITHUB_SCOPE_INTROSPECTION")
    if probe["delete_repo_scope"] == "OBSERVED_PRESENT":
        residuals.append("DELETE_REPO_SCOPE_PRESENT")
    decision = probe["authentication"]
    receipt.update({"decision": decision, "residuals": residuals, "evidence": probe})
    return receipt


def climate_receipt() -> dict[str, Any]:
    receipt = base_receipt("climate_engine_trial")
    probe = climate_probe(os.environ.get("CLIMATE_ENGINE_TRIAL_TOKEN", ""))
    residuals: list[str] = ["TOKEN_VAZIO_CLIMATE_LIVE_TOKEN_VALIDATION"]
    if not probe["secret_present"]:
        residuals.append("TOKEN_VAZIO_CLIMATE_ENGINE_TRIAL_TOKEN")
        decision = "TOKEN_VAZIO_SECRET_NOT_AVAILABLE"
    elif probe["token_metadata"].get("expired") is True:
        residuals.append("CLIMATE_ENGINE_TRIAL_TOKEN_EXPIRED")
        decision = "FAIL_TOKEN_EXPIRED"
    elif not probe["openapi_observed"]:
        residuals.append("TOKEN_VAZIO_CLIMATE_OPENAPI_CONTRACT")
        decision = "PASS_SECRET_PRESENT_WITH_RESIDUALS"
    else:
        decision = "PASS_LOCAL_TOKEN_LIFETIME_CHECK"
    receipt.update({"decision": decision, "residuals": residuals, "evidence": probe})
    return receipt


def write_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, indent=2, sort_keys=True) + "\n", encoding="utf-8")


def finalize(output_dir: Path) -> dict[str, Any]:
    github_path = output_dir / "github_pat.json"
    climate_path = output_dir / "climate_trial.json"
    github = json.loads(github_path.read_text(encoding="utf-8")) if github_path.exists() else None
    climate = json.loads(climate_path.read_text(encoding="utf-8")) if climate_path.exists() else None
    residuals: list[str] = []
    failures: list[str] = []
    for label, receipt in (("github", github), ("climate", climate)):
        if receipt is None:
            failures.append(f"{label.upper()}_RECEIPT_MISSING")
            continue
        residuals.extend(str(item) for item in receipt.get("residuals", []))
        decision = str(receipt.get("decision", "TOKEN_VAZIO"))
        if decision.startswith("FAIL") or decision.startswith("TOKEN_VAZIO_SECRET"):
            failures.append(f"{label.upper()}:{decision}")
    if github and github.get("evidence", {}).get("delete_repo_scope") == "OBSERVED_PRESENT":
        failures.append("GITHUB_DELETE_REPO_SCOPE_PRESENT")

    combined = base_receipt("combined")
    combined.update(
        {
            "decision": "FAIL_CREDENTIAL_BOUNDARY" if failures else (
                "PASS_WITH_RESIDUALS" if residuals else "PASS"
            ),
            "residuals": sorted(set(residuals)),
            "failures": failures,
            "components": {
                "github": "github_pat.json",
                "climate": "climate_trial.json",
            },
            "authority_boundary": {
                "same_repo_default": "github.token",
                "stored_pat_use": "explicit external/cross-repository authority only",
                "delete_operation": "FORBIDDEN_AND_NOT_PROBED",
                "climate_trial": "TEMPORARY_NON_CANONICAL_PROVIDER_CREDENTIAL",
                "future_dataset_secret": "CLIMATE_ENGINE_DATASET_TOKEN",
            },
        }
    )
    return combined


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("github", "climate", "finalize"), required=True)
    parser.add_argument("--output-dir", default="artifacts/secret-boundary-assurance")
    parser.add_argument("--enforce", action="store_true")
    args = parser.parse_args()
    out = Path(args.output_dir)

    if args.mode == "github":
        payload = github_receipt()
        target = out / "github_pat.json"
    elif args.mode == "climate":
        payload = climate_receipt()
        target = out / "climate_trial.json"
    else:
        payload = finalize(out)
        target = out / "receipt.json"

    write_json(target, payload)
    print(json.dumps({"kind": payload["kind"], "decision": payload["decision"], "residuals": payload["residuals"]}, sort_keys=True))
    if args.enforce and str(payload["decision"]).startswith("FAIL"):
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
