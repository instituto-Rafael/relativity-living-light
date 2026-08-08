#!/usr/bin/env python3
from __future__ import annotations

"""Observe repository branch/ruleset settings through GitHub's read-only API.

No secret value is serialized or printed. The probe records bounded public/
authorized metadata plus response hashes. A successful probe can make the
external-settings TOKEN_VAZIO eligible for an append-only governance closure;
it never changes token state by itself.
"""

import argparse
import hashlib
import json
import os
import tempfile
import urllib.error
import urllib.parse
import urllib.request
from pathlib import Path
from typing import Any, Callable, Sequence

SCHEMA = "rll.github_external_settings_readonly_probe.v1"
TOKEN = "TOKEN_VAZIO_EXTERNAL_SETTINGS"
DEFAULT_BRANCHES = ("main", "rll/release", "rll/integration", "rll/lab")


def canonical_sha256(value: Any) -> str:
    blob = json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


def http_json(url: str, token: str | None = None) -> tuple[int, Any]:
    headers = {
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "User-Agent": "RLL-readonly-settings-probe/1",
    }
    if token:
        headers["Authorization"] = f"Bearer {token}"
    request = urllib.request.Request(url, headers=headers, method="GET")
    try:
        with urllib.request.urlopen(request, timeout=30) as response:
            raw = response.read().decode("utf-8")
            return int(response.status), json.loads(raw) if raw else None
    except urllib.error.HTTPError as exc:
        raw = exc.read().decode("utf-8", errors="replace")
        try:
            body = json.loads(raw) if raw else None
        except json.JSONDecodeError:
            body = {"message": raw[:500]}
        return int(exc.code), body


def bounded_rulesets(body: Any) -> list[dict[str, Any]]:
    if not isinstance(body, list):
        return []
    rows = []
    for item in body:
        if not isinstance(item, dict):
            continue
        rules = item.get("rules") if isinstance(item.get("rules"), list) else []
        rows.append(
            {
                "id": item.get("id"),
                "name": item.get("name"),
                "target": item.get("target"),
                "enforcement": item.get("enforcement"),
                "source_type": item.get("source_type"),
                "rule_types": sorted(
                    str(rule.get("type")) for rule in rules if isinstance(rule, dict) and rule.get("type")
                ),
                "bypass_actor_count": len(item.get("bypass_actors") or []),
            }
        )
    return rows


def bounded_protection(body: Any) -> dict[str, Any] | None:
    if not isinstance(body, dict):
        return None
    checks = body.get("required_status_checks")
    reviews = body.get("required_pull_request_reviews")
    restrictions = body.get("restrictions")
    return {
        "required_status_checks": None
        if not isinstance(checks, dict)
        else {
            "strict": checks.get("strict"),
            "contexts": sorted(map(str, checks.get("contexts") or [])),
            "checks": sorted(
                str(row.get("context"))
                for row in (checks.get("checks") or [])
                if isinstance(row, dict) and row.get("context")
            ),
        },
        "enforce_admins": (body.get("enforce_admins") or {}).get("enabled")
        if isinstance(body.get("enforce_admins"), dict)
        else None,
        "required_pull_request_reviews": None
        if not isinstance(reviews, dict)
        else {
            "dismiss_stale_reviews": reviews.get("dismiss_stale_reviews"),
            "require_code_owner_reviews": reviews.get("require_code_owner_reviews"),
            "required_approving_review_count": reviews.get("required_approving_review_count"),
            "require_last_push_approval": reviews.get("require_last_push_approval"),
        },
        "required_linear_history": (body.get("required_linear_history") or {}).get("enabled")
        if isinstance(body.get("required_linear_history"), dict)
        else None,
        "allow_force_pushes": (body.get("allow_force_pushes") or {}).get("enabled")
        if isinstance(body.get("allow_force_pushes"), dict)
        else None,
        "allow_deletions": (body.get("allow_deletions") or {}).get("enabled")
        if isinstance(body.get("allow_deletions"), dict)
        else None,
        "restriction_actor_counts": None
        if not isinstance(restrictions, dict)
        else {
            "users": len(restrictions.get("users") or []),
            "teams": len(restrictions.get("teams") or []),
            "apps": len(restrictions.get("apps") or []),
        },
    }


def build(
    repository: str,
    branches: Sequence[str] = DEFAULT_BRANCHES,
    token: str | None = None,
    fetcher: Callable[[str, str | None], tuple[int, Any]] = http_json,
) -> dict[str, Any]:
    api = f"https://api.github.com/repos/{repository}"
    rules_status, rules_body = fetcher(f"{api}/rulesets?includes_parents=true", token)
    rulesets = bounded_rulesets(rules_body) if rules_status == 200 else []

    branch_rows: list[dict[str, Any]] = []
    for branch in branches:
        encoded = urllib.parse.quote(branch, safe="")
        meta_status, meta_body = fetcher(f"{api}/branches/{encoded}", token)
        protected = meta_body.get("protected") if meta_status == 200 and isinstance(meta_body, dict) else None
        protection_status, protection_body = fetcher(f"{api}/branches/{encoded}/protection", token)
        protection = bounded_protection(protection_body) if protection_status == 200 else None
        detail_complete = bool(meta_status == 200 and (protected is False or protection_status == 200))
        branch_rows.append(
            {
                "branch": branch,
                "metadata_http_status": meta_status,
                "protected": protected,
                "protection_http_status": protection_status,
                "detail_complete": detail_complete,
                "metadata_response_sha256": canonical_sha256(meta_body),
                "protection_response_sha256": canonical_sha256(protection_body),
                "protection": protection,
            }
        )

    branch_metadata_complete = all(row["metadata_http_status"] == 200 for row in branch_rows)
    protection_detail_complete = all(row["detail_complete"] for row in branch_rows)
    rulesets_observed = rules_status == 200
    resolution_eligible = bool(branch_metadata_complete and protection_detail_complete and rulesets_observed)

    return {
        "schema": SCHEMA,
        "state": "VERIFIED_EXTERNAL_SETTINGS_READONLY" if resolution_eligible else "PARTIAL_EXTERNAL_SETTINGS_OBSERVED",
        "claim_allowed": False,
        "publication_ready": False,
        "publication_effect": "NONE",
        "token": TOKEN,
        "repository": repository,
        "authority": {
            "api": "GitHub REST API 2022-11-28",
            "authenticated": bool(token),
            "read_only": True,
            "secret_material_persisted": False,
        },
        "rulesets": {
            "http_status": rules_status,
            "response_sha256": canonical_sha256(rules_body),
            "observed": rulesets_observed,
            "items": rulesets,
        },
        "branches": branch_rows,
        "summary": {
            "branch_count": len(branch_rows),
            "branch_metadata_complete": branch_metadata_complete,
            "protection_detail_complete": protection_detail_complete,
            "rulesets_observed": rulesets_observed,
            "resolution_eligible": resolution_eligible,
        },
        "resolved_token": None,
        "resolution_candidate": TOKEN if resolution_eligible else None,
        "remaining_close_conditions": []
        if resolution_eligible
        else [
            "obtain read authority for every protected branch's detailed protection configuration",
            "obtain read authority for repository rulesets including inherited rulesets",
            "append a governance transition only after a successful immutable settings receipt",
        ],
        "scientific_boundary": "Repository settings authority is operational governance evidence only; it has no scientific publication effect.",
    }


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--repository", default=os.environ.get("GITHUB_REPOSITORY"))
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args()
    if not args.repository:
        raise SystemExit("repository required")
    payload = build(args.repository, token=os.environ.get("GITHUB_TOKEN"))
    atomic_json(args.output, payload)
    print(json.dumps({"state": payload["state"], **payload["summary"], "claim_allowed": False}, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
