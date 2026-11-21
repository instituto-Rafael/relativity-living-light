#!/usr/bin/env python3
"""RAFAELIA P0: provider ruleset reconciliation. Agent CLI and trusted Actions.
No admin token on PR jobs, no auto-merge, no deletion, no secret logging.
"""
import argparse
import json
import os
import re
import sys
import urllib.error
import urllib.request
from pathlib import Path

ACTOR = "rafaelmeloreisnovo"
APP_ID = 15368
PROFILES = {
    "instituto-Rafael/relativity-living-light": {
        "name": "RLL main protected promotion",
        "ruleset_id": 23116926,
        "baseline_updated_at": "2026-11-11T14:42:09.192-03:00",
        "branches": ["~DEFAULT_BRANCH", "refs/heads/rll/lab"],
        "checks": ["Branch maturity gate V2", "test"],
    },
    "rafaelmeloreisnovo/RafGitTools": {
        "name": "RAFAELIA P0 controlled promotion v1",
        "ruleset_id": None,
        "baseline_updated_at": None,
        "branches": ["~DEFAULT_BRANCH"],
        "checks": [
            "01 · Workflow topology / START owner + scoped workflows",
            "02 · Coherence / anti-regression",
            "03 · Python / deterministic tests",
        ],
    },
}

class Blocked(RuntimeError):
    pass

class NoRedirect(urllib.request.HTTPRedirectHandler):
    def redirect_request(self, request, fp, code, msg, headers, newurl):
        raise Blocked("HTTP_REDIRECT_DENIED")

def api(method, path, token, payload=None):
    if not path.startswith("/repos/") or not token:
        raise Blocked("API_TARGET_OR_TOKEN_INVALID")
    url = "https://api.github.com" + path
    data = None if payload is None else json.dumps(payload, sort_keys=True).encode()
    req = urllib.request.Request(url, data=data, method=method, headers={
        "Accept": "application/vnd.github+json",
        "X-GitHub-Api-Version": "2022-11-28",
        "Authorization": "Bearer " + token,
        "User-Agent": "rafaelia-provider-p0/1",
        "Content-Type": "application/json",
    })
    try:
        with urllib.request.build_opener(NoRedirect()).open(req, timeout=15) as response:
            raw = response.read(1048576 + 1)
            if len(raw) > 1048576:
                raise Blocked("OVERSIZED_PROVIDER_RESPONSE")
            return json.loads(raw) if raw else {}
    except urllib.error.HTTPError as exc:
        raise Blocked("PROVIDER_HTTP_" + str(exc.code)) from None
    except urllib.error.URLError:
        raise Blocked("PROVIDER_NETWORK_ERROR") from None

def policy(profile, original=None):
    rules = [dict(x) for x in (original or {}).get("rules", [])
             if x.get("type") not in ("pull_request", "required_status_checks")]
    known = {x.get("type") for x in rules}
    for kind in ("deletion", "non_fast_forward"):
        if kind not in known:
            rules.append({"type": kind})
    rules.extend([
        {"type": "pull_request", "parameters": {
            "required_approving_review_count": 1,
            "dismiss_stale_reviews_on_push": True,
            "require_code_owner_review": False,
            "require_last_push_approval": True,
            "required_review_thread_resolution": True,
            "allowed_merge_methods": ["merge", "squash", "rebase"],
        }},
        {"type": "required_status_checks", "parameters": {
            "strict_required_status_checks_policy": True,
            "required_status_checks": [
                {"context": x, "integration_id": APP_ID} for x in profile["checks"]
            ],
        }},
    ])
    return {
        "name": profile["name"], "target": "branch", "enforcement": "active",
        "conditions": {"ref_name": {"include": profile["branches"], "exclude": []}},
        "bypass_actors": [], "rules": rules,
    }

def compliant(found, expected):
    if not found:
        return False
    for key in ("name", "target", "enforcement", "conditions"):
        if found.get(key) != expected.get(key):
            return False
    if found.get("bypass_actors") != []:
        return False
    fr = {x["type"]: x for x in found.get("rules", [])}
    er = {x["type"]: x for x in expected["rules"]}
    if not set(er).issubset(fr):
        return False
    pr = fr["pull_request"].get("parameters", {})
    if type(pr.get("required_approving_review_count")) is not int:
        return False
    if pr["required_approving_review_count"] < 1:
        return False
    if any(pr.get(x) is not True for x in (
        "dismiss_stale_reviews_on_push", "require_last_push_approval",
        "required_review_thread_resolution"
    )):
        return False
    status = fr["required_status_checks"].get("parameters", {})
    return (status.get("strict_required_status_checks_policy") is True
            and { (x.get("context"), x.get("integration_id"))
                  for x in status.get("required_status_checks", []) }
                >= { (x["context"], x["integration_id"])
                      for x in er["required_status_checks"]["parameters"]["required_status_checks"] })

def live(repo, profile, token):
    metadata = api("GET", "/repos/" + repo, token)
    if metadata.get("full_name") != repo or metadata.get("default_branch") != "main":
        raise Blocked("REPOSITORY_IDENTITY_OR_DEFAULT_BRANCH_CHANGED")
    if metadata.get("private"):
        raise Blocked("PRIVATE_REPOSITORY_NOT_IN_SCOPE")
    head = api("GET", "/repos/" + repo + "/branches/main", token)
    head_sha = head.get("commit", {}).get("sha")
    if not isinstance(head_sha, str) or not re.fullmatch("[0-9a-f]{40}", head_sha):
        raise Blocked("MAIN_HEAD_NOT_VERIFIED")
    listed = api("GET", "/repos/" + repo + "/rulesets", token)
    if not isinstance(listed, list):
        raise Blocked("RULESET_LIST_INVALID")
    selected = next((r for r in listed if r.get("name") == profile["name"]), None)
    if profile["ruleset_id"] is not None:
        if not any(r.get("id") == profile["ruleset_id"] for r in listed):
            raise Blocked("EXISTING_RULESET_NOT_FOUND")
        selected = api("GET", "/repos/" + repo + "/rulesets/" + str(profile["ruleset_id"]), token)
    elif listed and not selected:
        raise Blocked("UNRECONCILED_RULESETS_PRESENT")
    elif selected:
        selected = api("GET", "/repos/" + repo + "/rulesets/" + str(selected["id"]), token)
    return head_sha, selected

def receipt(data):
    target = Path("artifacts/rafaelia-provider-p0")
    target.mkdir(parents=True, exist_ok=True)
    (target / "receipt.json").write_text(
        json.dumps(data, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8"
    )
    print(json.dumps(data, ensure_ascii=False, sort_keys=True))

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--mode", choices=("validate", "audit", "apply"), default="validate")
    parser.add_argument("--repo", required=True, choices=list(PROFILES))
    parser.add_argument("--expected-main-sha", default="")
    parser.add_argument("--confirm", default="")
    parser.add_argument("--operator", choices=("actions", "agent"), default="actions")
    args = parser.parse_args()
    profile = PROFILES[args.repo]
    expected = policy(profile)
    if not compliant(expected, expected):
        raise Blocked("STATIC_POLICY_INVALID")
    if args.mode == "validate":
        receipt({"state": "VALIDATED_POLICY_SHAPE_ONLY", "repo": args.repo,
                 "checks": profile["checks"], "claim_allowed": False})
        return 0
    token = os.environ.get("GH_API_TOKEN", "")
    if not token:
        raise Blocked("MISSING_GH_API_TOKEN")
    if args.operator == "actions" and os.environ.get("GITHUB_REPOSITORY") != args.repo:
        raise Blocked("CROSS_REPOSITORY_DISPATCH_DENIED")
    head_sha, current = live(args.repo, profile, token)
    planned = policy(profile, current)
    if args.mode == "audit":
        ok = compliant(current, planned)
        receipt({"state": "ENFORCED_SCOPED_CONFIG" if ok else "BLOCKED_PROVIDER_POLICY",
                 "repo": args.repo, "head_sha": head_sha,
                 "ruleset_id": (current or {}).get("id"),
                 "claim_allowed": False})
        return 0 if ok else 2
    # Writes require explicit human operation + authenticated administrative secret.
    if args.confirm != "APPLY-P0:" + args.repo:
        raise Blocked("EXPLICIT_CONFIRMATION_REQUIRED")
    if args.operator == "actions":
        if (os.environ.get("GITHUB_EVENT_NAME") != "workflow_dispatch"
            or os.environ.get("GITHUB_REF") != "refs/heads/main"
            or os.environ.get("GITHUB_ACTOR") != ACTOR):
            raise Blocked("TRUSTED_ACTIONS_CONTEXT_REQUIRED")
    else:
        if os.environ.get("RAFAELIA_AGENT_APPLY_APPROVED") != "1":
            raise Blocked("AGENT_APPLY_APPROVAL_REQUIRED")
    if not re.fullmatch("[0-9a-f]{40}", args.expected_main_sha):
        raise Blocked("EXPECTED_SHA_REQUIRED")
    if head_sha != args.expected_main_sha:
        raise Blocked("HEAD_MOVED_STOP")
    if current and compliant(current, planned):
        receipt({"state": "NOOP_ALREADY_COMPLIANT_SCOPED", "repo": args.repo,
                 "head_sha": head_sha, "ruleset_id": current["id"],
                 "claim_allowed": False})
        return 0
    if current and profile["ruleset_id"] and (current.get("updated_at") != profile["baseline_updated_at"]):
        raise Blocked("RULESET_BASELINE_CHANGED_REVIEW_REQUIRED")
    if current and profile["ruleset_id"] is None:
        raise Blocked("EXISTING_NEW_POLICY_CHANGED_REVIEW_REQUIRED")
    # Snapshot before mutation. This is a local recovery receipt, not a rollback execution.
    Path("artifacts/rafaelia-provider-p0").mkdir(parents=True, exist_ok=True)
    Path("artifacts/rafaelia-provider-p0/prestate.json").write_text(
        json.dumps({"repo": args.repo, "ruleset": current}, indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    again_sha, again_rule = live(args.repo, profile, token)
    if again_sha != head_sha or again_rule != current:
        raise Blocked("CONCURRENT_PROVIDER_CHANGE_STOP")
    path = "/repos/" + args.repo + "/rulesets"
    if current:
        after = api("PUT", path + "/" + str(current["id"]), token, planned)
    else:
        after = api("POST", path, token, planned)
    new_id = after.get("id")
    if not isinstance(new_id, int):
        raise Blocked("MUTATION_RESPONSE_ID_INVALID")
    verified = api("GET", path + "/" + str(new_id), token)
    if not compliant(verified, planned):
        raise Blocked("PROVIDER_READBACK_FAILED_MANUAL_ROLLBACK_REQUIRED")
    receipt({"state": "PROVIDER_POLICY_READBACK_SCOPED", "repo": args.repo,
             "head_sha": head_sha, "ruleset_id": new_id,
             "configured_checks": profile["checks"],
             "negative_merge_test": "NOT_RUN", "claim_allowed": False})
    return 0

if __name__ == "__main__":
    try:
        sys.exit(main())
    except Blocked as exc:
        receipt({"state": "BLOCKED", "reason": str(exc), "claim_allowed": False})
        sys.exit(2)
