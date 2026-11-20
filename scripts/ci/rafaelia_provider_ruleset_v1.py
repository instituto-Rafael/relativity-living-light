#!/usr/bin/env python3
"""RAFAELIA P0: provider ruleset reconciliation. Agent CLI and trusted Actions.
No admin token on PR jobs, no auto-merge, no deletion, no secret logging.
"""
import argparse
import copy
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
        "repository_id": 1046495816,
        "ruleset_id": 23116926,
        "baseline_updated_at": "2026-11-11T14:42:09.192-03:00",
        "branches": ["~DEFAULT_BRANCH", "refs/heads/rll/lab"],
        "checks": ["Branch maturity gate V2", "test"],
    },
    "rafaelmeloreisnovo/RafGitTools": {
        "name": "RAFAELIA P0 controlled promotion v1",
        "repository_id": 1131213900,
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
    """Monotonic tightening: never silently weaken a pre-existing rule.

    If the provider's contract is ambiguous, stop before writing.
    """
    if original is not None and not isinstance(original, dict):
        raise Blocked("PRESTATE_NOT_OBJECT")
    source = original or {}
    original_rules = source.get("rules", [])
    if not isinstance(original_rules, list) or any(
        not isinstance(item, dict) or not isinstance(item.get("type"), str)
        for item in original_rules
    ):
        raise Blocked("MALFORMED_EXISTING_RULES")
    kinds = [item["type"] for item in original_rules]
    if len(kinds) != len(set(kinds)):
        raise Blocked("DUPLICATED_RULE_TYPES")
    rules_by_type = {item["type"]: item for item in original_rules}
    rules = [copy.deepcopy(item) for item in original_rules
             if item["type"] not in ("pull_request", "required_status_checks")]
    for kind in ("deletion", "non_fast_forward"):
        if kind not in kinds:
            rules.append({"type": kind})

    prev_pr = rules_by_type.get("pull_request", {}).get("parameters", {})
    if not isinstance(prev_pr, dict):
        raise Blocked("MALFORMED_EXISTING_REVIEW_POLICY")
    approval = prev_pr.get("required_approving_review_count", 0)
    if type(approval) is not int or approval < 0:
        raise Blocked("INVALID_EXISTING_APPROVAL_COUNT")
    pr_params = copy.deepcopy(prev_pr)
    pr_params["required_approving_review_count"] = max(1, approval)
    for key in ("dismiss_stale_reviews_on_push", "require_last_push_approval",
                "required_review_thread_resolution"):
        pr_params[key] = True
    pr_params.setdefault("allowed_merge_methods", ["merge", "squash", "rebase"])
    if not isinstance(pr_params["allowed_merge_methods"], list) or not pr_params["allowed_merge_methods"]:
        raise Blocked("INVALID_EXISTING_MERGE_METHODS")
    rules.append({"type": "pull_request", "parameters": pr_params})

    prev_status = rules_by_type.get("required_status_checks", {}).get("parameters", {})
    if not isinstance(prev_status, dict):
        raise Blocked("MALFORMED_EXISTING_STATUS_POLICY")
    status = copy.deepcopy(prev_status)
    previous_checks = status.get("required_status_checks", [])
    if not isinstance(previous_checks, list) or any(not isinstance(x, dict) for x in previous_checks):
        raise Blocked("MALFORMED_EXISTING_CHECKS")
    by_context = {}
    for check in previous_checks:
        context = check.get("context")
        if not isinstance(context, str) or not context.strip() or context in by_context:
            raise Blocked("INVALID_OR_DUPLICATED_EXISTING_CHECK")
        by_context[context] = copy.deepcopy(check)
    for context in profile["checks"]:
        existing = by_context.get(context)
        if existing is not None and existing.get("integration_id") != APP_ID:
            raise Blocked("CHECK_APP_ID_CONFLICT")
        by_context[context] = {"context": context, "integration_id": APP_ID}
    status["strict_required_status_checks_policy"] = True
    status["required_status_checks"] = list(by_context.values())
    rules.append({"type": "required_status_checks", "parameters": status})

    old_conditions = copy.deepcopy(source.get("conditions", {}))
    if not isinstance(old_conditions, dict):
        raise Blocked("MALFORMED_EXISTING_CONDITIONS")
    old_ref = old_conditions.get("ref_name", {"include": [], "exclude": []})
    if not isinstance(old_ref, dict):
        raise Blocked("MALFORMED_EXISTING_REF")
    include = old_ref.get("include", [])
    exclude = old_ref.get("exclude", [])
    if (not isinstance(include, list) or not all(isinstance(x, str) for x in include)
        or not isinstance(exclude, list) or exclude):
        raise Blocked("EXCLUSION_OR_UNKNOWN_REF_RULE_REVIEW_REQUIRED")
    # Preserve all preexisting branches and any extra opaque condition metadata.
    old_ref["include"] = list(dict.fromkeys(include + list(profile["branches"])))
    old_ref["exclude"] = []
    old_conditions["ref_name"] = old_ref
    return {
        "name": profile["name"], "target": "branch", "enforcement": "active",
        "conditions": old_conditions,
        "bypass_actors": [], "rules": rules,
    }

def compliant(found, expected):
    """Structural predicate, never a claim that a merge is genuinely blocked."""
    if not isinstance(found, dict) or not isinstance(expected, dict):
        return False
    if any(found.get(x) != expected.get(x) for x in
           ("name", "target", "enforcement", "conditions")):
        return False
    if found.get("bypass_actors") != []:
        return False
    actual = found.get("rules", [])
    required = expected.get("rules", [])
    if (not isinstance(actual, list) or not isinstance(required, list)
        or any(not isinstance(x, dict) or not isinstance(x.get("type"), str) for x in actual)):
        return False
    a_types = [x["type"] for x in actual]
    if len(a_types) != len(set(a_types)):
        return False
    fr = {x["type"]: x for x in actual}
    er = {x["type"]: x for x in required}
    if not set(er).issubset(fr):
        return False
    for name, item in er.items():
        if name not in ("pull_request", "required_status_checks") and fr[name] != item:
            return False
    pr = fr["pull_request"].get("parameters", {})
    exp_pr = er["pull_request"].get("parameters", {})
    if not isinstance(pr, dict) or not isinstance(exp_pr, dict):
        return False
    count = pr.get("required_approving_review_count")
    exp_count = exp_pr.get("required_approving_review_count")
    if (type(count) is not int or type(exp_count) is not int
        or count < exp_count or count < 1):
        return False
    for flag in ("dismiss_stale_reviews_on_push", "require_last_push_approval",
                 "required_review_thread_resolution"):
        if pr.get(flag) is not True:
            return False
    for flag in ("require_code_owner_review", "require_extra_approval_for_unattributed_changes"):
        if exp_pr.get(flag) is True and pr.get(flag) is not True:
            return False
    for key in ("required_reviewers",):
        if exp_pr.get(key) and pr.get(key) != exp_pr.get(key):
            return False
    if exp_pr.get("dismissal_restriction", {}).get("enabled") is True:
        if pr.get("dismissal_restriction") != exp_pr["dismissal_restriction"]:
            return False
    allow = pr.get("allowed_merge_methods")
    exp_allow = exp_pr.get("allowed_merge_methods")
    if not isinstance(allow, list) or not isinstance(exp_allow, list):
        return False
    if not allow or not set(allow).issubset(set(exp_allow)):
        return False
    status = fr["required_status_checks"].get("parameters", {})
    expected_status = er["required_status_checks"].get("parameters", {})
    if not isinstance(status, dict) or status.get("strict_required_status_checks_policy") is not True:
        return False
    checks = status.get("required_status_checks", [])
    required_checks = expected_status.get("required_status_checks", [])
    if not isinstance(checks, list) or not all(isinstance(x, dict) for x in checks):
        return False
    contexts = [x.get("context") for x in checks]
    if any(not isinstance(x, str) or not x.strip() for x in contexts) or len(contexts) != len(set(contexts)):
        return False
    actual_checks = {(x.get("context"), x.get("integration_id")) for x in checks}
    wanted = {(x.get("context"), x.get("integration_id")) for x in required_checks}
    return wanted.issubset(actual_checks)

def live(repo, profile, token):
    metadata = api("GET", "/repos/" + repo, token)
    if (metadata.get("full_name") != repo or metadata.get("default_branch") != "main"
        or metadata.get("id") != profile["repository_id"]):
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
    if len(listed) != (1 if profile["ruleset_id"] is not None else (1 if listed else 0)):
        raise Blocked("UNRECONCILED_ADDITIONAL_RULESETS")
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
    parser.add_argument("--reviewer-login", default="", help="GitHub login eligible to review independently")
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
        receipt({"state": "CONFIG_SHAPE_OBSERVED_ONLY" if ok else "BLOCKED_PROVIDER_POLICY",
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
    # Confirm a distinct collaborator with actual write-level review capability.
    reviewer = args.reviewer_login.strip()
    if (not re.fullmatch(r"[A-Za-z0-9](?:[A-Za-z0-9-]{0,37}[A-Za-z0-9])?", reviewer)
        or reviewer.lower() == ACTOR.lower()):
        raise Blocked("INDEPENDENT_REVIEWER_LOGIN_INVALID_OR_UNKNOWN")
    permission = api("GET", "/repos/" + args.repo + "/collaborators/" + reviewer + "/permission", token)
    if permission.get("permission") not in ("write", "maintain", "admin"):
        raise Blocked("REVIEWER_PERMISSION_NOT_VERIFIED")
    # A permitted account is not proof of a distinct human. Require documented review.
    if os.environ.get("RAFAELIA_REVIEWER_GATE_EVIDENCE") != "REVIEWED_INDEPENDENT_REVIEWER_AND_ROLLBACK":
        raise Blocked("INDEPENDENT_REVIEWER_AND_ROLLBACK_NOT_VERIFIED")
    # Snapshot before mutation. This is a local recovery receipt, not a rollback execution.
    Path("artifacts/rafaelia-provider-p0").mkdir(parents=True, exist_ok=True)
    Path("artifacts/rafaelia-provider-p0/prestate.json").write_text(
        json.dumps({"repo": args.repo, "head_sha": head_sha, "ruleset": current,
                    "rollback": "HUMAN_REVIEW_REQUIRED", "claim_allowed": False},
                   indent=2, sort_keys=True) + "\n",
        encoding="utf-8")
    again_sha, again_rule = live(args.repo, profile, token)
    if again_sha != head_sha or again_rule != current:
        raise Blocked("CONCURRENT_PROVIDER_CHANGE_STOP")
    path = "/repos/" + args.repo + "/rulesets"
    # A network timeout after an HTTP write is an UNKNOWN remote outcome, never a safe retry.
    global WRITE_ATTEMPTED
    WRITE_ATTEMPTED = True
    receipt({"state": "MUTATION_ATTEMPT_BEGIN_REMOTE_OUTCOME_UNKNOWN",
             "repo": args.repo, "head_sha": head_sha,
             "prestate_saved": True, "claim_allowed": False})
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
    receipt({"state": "CONFIG_READBACK_SCOPED_NEGATIVE_TEST_NOT_RUN", "repo": args.repo,
             "head_sha": head_sha, "ruleset_id": new_id,
             "configured_checks": profile["checks"],
             "independent_reviewer_login": reviewer,
             "independence_of_human_identity": "TOKEN_VAZIO_NOT_PROVED_BY_PERMISSION",
             "rollback_test": "NOT_RUN",
             "negative_merge_test": "NOT_RUN", "claim_allowed": False})
    return 0

WRITE_ATTEMPTED = False
if __name__ == "__main__":
    try:
        sys.exit(main())
    except (Blocked, ValueError, TypeError, KeyError, AttributeError, OSError) as exc:
        reason = str(exc) if isinstance(exc, Blocked) else "MALFORMED_OR_UNAVAILABLE_PROVIDER_DATA"
        receipt({"state": "WRITE_OUTCOME_UNKNOWN_REQUIRE_PROVIDER_READBACK" if WRITE_ATTEMPTED else "BLOCKED",
                 "reason": reason, "claim_allowed": False})
        sys.exit(2)
