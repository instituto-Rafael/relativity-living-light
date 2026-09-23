#!/usr/bin/env python3
"""Deterministic deny-by-default development guard for RLL.

This is a programmatic policy gate, not an autonomous agent and not an OS sandbox.
It validates a declared operation against a repository policy before execution.
"""

from __future__ import annotations

import argparse
import hashlib
import json
import sys
import urllib.error
import urllib.request
from pathlib import Path, PurePosixPath
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[2]
DEFAULT_POLICY = ROOT / "data" / "governance" / "RLL_DEVELOPMENT_SECURITY_ENVELOPE_V1.json"


def _canonical_hash(value):
    raw = json.dumps(
        value,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(raw).hexdigest()


def _safe_relative_prefix(value):
    text = str(value).strip()
    if not text or "\\" in text or text.startswith("/"):
        return None
    path = PurePosixPath(text)
    if path.is_absolute() or ".." in path.parts or "." in path.parts:
        return None
    normalized = path.as_posix()
    if text.endswith("/") and not normalized.endswith("/"):
        normalized += "/"
    return normalized


def evaluate_operation(policy, operation, runtime_authority_mode=None):
    blockers = []
    reviews = []

    if policy.get("schema") != "rll.development_security_envelope.v1":
        blockers.append("unsupported_policy_schema")
    if operation.get("schema") != "rll.development_operation.v1":
        blockers.append("unsupported_operation_schema")

    authority = operation.get("authority", {})
    allowed_modes = set(policy.get("human_authority", {}).get("accepted_modes", []))
    permitted_modes = set(authority.get("permitted_modes", []))
    runtime_mode = runtime_authority_mode or authority.get("default_runtime_mode")
    if authority.get("human_required") is not True:
        blockers.append("human_authority_not_required")
    if authority.get("self_authorized") is not False:
        blockers.append("self_authorization_not_forbidden")
    if not permitted_modes or not permitted_modes.issubset(allowed_modes):
        blockers.append("operation_authority_modes_not_allowed")
    if runtime_mode not in permitted_modes or runtime_mode not in allowed_modes:
        blockers.append("runtime_authority_mode_not_allowed")

    autonomy = operation.get("autonomy", {})
    for field in ("goal_setting", "scope_expansion", "background_persistence"):
        if autonomy.get(field) is not False:
            blockers.append("autonomy_%s_must_be_false" % field)

    allowed_caps = set(policy.get("allowed_capabilities", []))
    forbidden_caps = set(policy.get("forbidden_capabilities", []))
    requested_caps = set(operation.get("capabilities", []))
    forbidden_requested = sorted(requested_caps & forbidden_caps)
    if forbidden_requested:
        blockers.append("forbidden_capabilities:" + ",".join(forbidden_requested))
    unknown_caps = sorted(requested_caps - allowed_caps)
    if unknown_caps:
        blockers.append("unknown_capabilities:" + ",".join(unknown_caps))

    data_policy = policy.get("data_governance", {})
    allowed_classes = set(data_policy.get("allowed_classes", []))
    denied_classes = set(data_policy.get("denied_by_default", []))
    requested_classes = set(operation.get("data_classes", []))
    denied_requested = sorted(requested_classes & denied_classes)
    if denied_requested:
        blockers.append("denied_data_classes:" + ",".join(denied_requested))
    unknown_classes = sorted(requested_classes - allowed_classes - denied_classes)
    if unknown_classes:
        reviews.append("unknown_data_classes:" + ",".join(unknown_classes))

    if operation.get("personal_data_expected") is not False:
        blockers.append("personal_data_not_permitted_by_this_operation")
    if operation.get("secrets_required") is not False:
        blockers.append("secrets_not_permitted_by_this_operation")
    if operation.get("destructive_actions") is not False:
        blockers.append("destructive_actions_forbidden")
    if operation.get("shell_free_text") is not False:
        blockers.append("free_text_shell_forbidden")
    if operation.get("claim_allowed") is not False:
        blockers.append("operation_cannot_promote_claim")

    fs_policy = policy.get("filesystem", {})
    allowed_write_prefixes = [
        _safe_relative_prefix(x) for x in fs_policy.get("allowed_write_prefixes", [])
    ]
    forbidden_write_prefixes = [
        _safe_relative_prefix(x) for x in fs_policy.get("forbidden_write_prefixes", [])
    ]
    allowed_write_prefixes = [x for x in allowed_write_prefixes if x]
    forbidden_write_prefixes = [x for x in forbidden_write_prefixes if x]

    for raw in operation.get("writes", []):
        path = _safe_relative_prefix(raw)
        if path is None:
            blockers.append("unsafe_write_path:" + str(raw))
            continue
        if any(path.startswith(prefix) for prefix in forbidden_write_prefixes):
            blockers.append("forbidden_write_path:" + path)
            continue
        if not any(path.startswith(prefix) for prefix in allowed_write_prefixes):
            blockers.append("write_path_not_allowlisted:" + path)

    network = operation.get("network", {})
    policy_network = policy.get("network", {})
    allowed_hosts = set(policy_network.get("exact_hosts", []))
    hosts = set(network.get("hosts", []))
    if not hosts.issubset(allowed_hosts):
        blockers.append("network_host_not_allowlisted:" + ",".join(sorted(hosts - allowed_hosts)))
    methods = {str(x).upper() for x in network.get("methods", [])}
    if methods - {"GET", "HEAD"}:
        blockers.append("network_write_method_forbidden:" + ",".join(sorted(methods - {"GET", "HEAD"})))
    if network.get("default_enabled") is not False:
        blockers.append("network_must_default_off")

    if blockers:
        decision = "BLOCK"
        event_type = "POLICY_BLOCK"
    elif reviews:
        decision = "HUMAN_REVIEW"
        event_type = "HUMAN_REVIEW_REQUIRED"
    else:
        decision = "ALLOW"
        event_type = "AUTHORIZED_EXECUTION"

    return {
        "schema": "rll.development_guard.receipt.v1",
        "policy_schema": policy.get("schema", "TOKEN_VAZIO"),
        "operation_id": operation.get("operation_id", "TOKEN_VAZIO"),
        "runtime_authority_mode": runtime_mode,
        "runtime_authority_mode_is_identity_proof": False,
        "decision": decision,
        "event_type": event_type,
        "reasons": blockers + reviews if (blockers or reviews) else ["policy_constraints_satisfied"],
        "policy_sha256": _canonical_hash(policy),
        "operation_sha256": _canonical_hash(operation),
        "claim_allowed": False,
        "security_certification": False,
        "os_sandbox_proven": False,
        "boundary": (
            "Application-layer policy pass authorizes only the declared program route. "
            "It does not prove absence of vulnerabilities, OS sandboxing, legal compliance, "
            "or scientific validity."
        ),
    }


def authorize_url(policy, url):
    parsed = urlsplit(str(url))
    network = policy.get("network", {})
    schemes = set(network.get("schemes", []))
    hosts = set(network.get("exact_hosts", []))

    if parsed.scheme not in schemes:
        raise ValueError("network_scheme_not_allowed")
    if not parsed.hostname or parsed.hostname not in hosts:
        raise ValueError("network_host_not_allowed")
    if parsed.username is not None or parsed.password is not None:
        raise ValueError("url_userinfo_forbidden")
    if parsed.query:
        raise ValueError("url_query_forbidden")
    if parsed.fragment:
        raise ValueError("url_fragment_forbidden")
    try:
        port = parsed.port
    except ValueError as exc:
        raise ValueError("invalid_url_port") from exc
    if port is not None:
        raise ValueError("custom_port_forbidden")
    return parsed.hostname


class _SameHostRedirectHandler(urllib.request.HTTPRedirectHandler):
    def __init__(self, policy, original_host):
        super().__init__()
        self.policy = policy
        self.original_host = original_host

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        new_host = authorize_url(self.policy, newurl)
        if new_host != self.original_host:
            raise urllib.error.URLError("cross_host_redirect_forbidden")
        return super().redirect_request(req, fp, code, msg, headers, newurl)


def safe_public_probe(policy, url, user_agent="RLL-Guard/1.0"):
    host = authorize_url(policy, url)
    network = policy.get("network", {})
    timeout = min(int(network.get("timeout_seconds_max", 20)), 20)
    max_bytes = min(int(network.get("response_bytes_max", 1000000)), 1000000)

    opener = urllib.request.build_opener(_SameHostRedirectHandler(policy, host))
    req = urllib.request.Request(
        url,
        headers={"User-Agent": str(user_agent)},
        method="GET",
    )
    with opener.open(req, timeout=timeout) as response:
        payload = response.read(min(max_bytes, 256) + 1)
        if len(payload) > min(max_bytes, 256):
            payload = payload[: min(max_bytes, 256)]
        return {
            "host": host,
            "status": int(getattr(response, "status", 200)),
            "bytes_sampled": len(payload),
            "content_type": response.headers.get("Content-Type", ""),
        }


def _load(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(argv=None):
    parser = argparse.ArgumentParser(description="RLL deterministic development guard")
    parser.add_argument("--policy", default=str(DEFAULT_POLICY))
    parser.add_argument("--operation", required=True)
    parser.add_argument("--receipt", default="")
    parser.add_argument("--authority-mode", default="")
    parser.add_argument("--strict", action="store_true")
    args = parser.parse_args(argv)

    policy = _load(args.policy)
    operation = _load(args.operation)
    receipt = evaluate_operation(
        policy,
        operation,
        runtime_authority_mode=(args.authority_mode or None),
    )

    if args.receipt:
        out = Path(args.receipt)
        if out.exists():
            raise SystemExit("receipt path already exists; append-only guard refused overwrite")
        out.parent.mkdir(parents=True, exist_ok=True)
        out.write_text(
            json.dumps(receipt, ensure_ascii=False, indent=2) + "\n",
            encoding="utf-8",
        )

    print(json.dumps(receipt, ensure_ascii=False, indent=2))

    if args.strict and receipt["decision"] != "ALLOW":
        return 4 if receipt["decision"] == "BLOCK" else 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
