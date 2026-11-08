#!/usr/bin/env python3
"""RLL federated PR assurance: offline, typed, fail-closed snapshot contract.

Structural verification only: NO GitHub API, secrets, device execution, merges,
scientific model fit, provider settings mutation, or fabricated live state.
"""
from __future__ import annotations

import argparse
from datetime import date
import hashlib
import json
from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[2]
DEFAULT = ROOT / "data/contracts/rll_federated_pr_assurance_v1.json"
HEAD = re.compile(r"^[0-9a-f]{40}$")
OWNERS = frozenset(("rafaelmeloreisnovo", "instituto-Rafael"))
RISK_LEVELS = {
    "DEVICE_E2E_MISSING": "P0",
    "BOOTSTRAP_REAL_ARM_FAIL": "P0",
    "REMOTE_ARTIFACT_QUOTA": "P1",
    "CI_FAILURE": "P1",
    "BRANCH_MATURITY": "P1",
    "EXTERNAL_PROTECTION_PARTIAL": "P1",
    "ANDROID_BUILD_FAILURE": "P1",
    "SOURCE_PROVENANCE_UNVERIFIED": "P1",
    "DEPENDENCY_MIGRATION_REVIEW": "P2",
}
LEVEL = {"P0": 0, "P1": 1, "P2": 2}
REQUIRED_MISSING = {
    "DEVICE_E2E_MISSING": "DEVICE_OAUTH_INDEXER_RECEIPT",
    "BOOTSTRAP_REAL_ARM_FAIL": "REAL_ARM_BOOTSTRAP_RECEIPT",
    "REMOTE_ARTIFACT_QUOTA": "REMOTE_ARTIFACT_CUSTODY",
    "BRANCH_MATURITY": "OWNER_BRANCH_PROMOTION",
    "EXTERNAL_PROTECTION_PARTIAL": "PROVIDER_RULESET_AUTHORITY",
    "ANDROID_BUILD_FAILURE": "ANDROID_BUILD_SUCCESS",
    "SOURCE_PROVENANCE_UNVERIFIED": "SOURCE_PROVENANCE_VERIFIED",
}

def reject(code: str) -> None:
    raise ValueError(code)

def verify(document: dict, as_of: str | None = None) -> dict:
    if not isinstance(document, dict) or document.get("schema") != "rll.federated_pr_assurance.v1":
        reject("SCHEMA_MISMATCH")
    if document.get("claim_allowed") is not False or document.get("merge_allowed") is not False:
        reject("UNAUTHORIZED_CLAIM_OR_MERGE")
    if document.get("source_class") != "CONNECTED_GITHUB_POINT_IN_TIME_READ_ONLY":
        reject("UNVERIFIED_PROVENANCE_CLASS")
    if document.get("security") != {"network_ci": "DENIED", "secrets_ci": "DENIED",
                                     "writes_ci": "DENIED", "automatic_merge": "DENIED"}:
        reject("SECURITY_BOUNDARY_CHANGED")
    inv = document.get("inventory", {})
    if inv.get("personal_owned_open") != 53 or inv.get("institute_open") != 4 or inv.get("external_firebird_outgoing") != 3:
        reject("INVENTORY_SNAPSHOT_MISMATCH")
    records = document.get("records")
    if not isinstance(records, list) or not records or len(records) > 57:
        reject("INVALID_SCOPED_RECORDS")
    if document.get("reviewed_subset_count") != len(records):
        reject("FALSE_REVIEW_COVERAGE")
    observed = date.fromisoformat(document["observed_utc"])
    check_date = date.fromisoformat(as_of or document["observed_utc"])
    if check_date < observed:
        reject("FUTURE_OBSERVATION")
    stale = (check_date-observed).days > 7
    seen, counts, unclosed = set(), {"P0": 0, "P1": 0, "P2": 0}, []
    for record in records:
        name = record.get("repo")
        number = record.get("pr")
        if not isinstance(name, str) or name.count("/") != 1:
            reject("BAD_REPOSITORY")
        owner = name.split("/", 1)[0]
        if owner not in OWNERS or not isinstance(number, int) or isinstance(number, bool) or number < 1:
            reject("OUT_OF_SCOPE_PR")
        key = name + "#" + str(number)
        if key in seen:
            reject("DUPLICATE_PR")
        seen.add(key)
        url = "https://github.com/" + name + "/pull/" + str(number)
        if record.get("source_url") != url:
            reject("SOURCE_URL_NOT_BOUND")
        head = record.get("head_sha")
        ci = record.get("ci", {})
        if not isinstance(head, str) or not HEAD.fullmatch(head) or ci.get("head_sha") != head:
            reject("CI_NOT_BOUND_TO_EXACT_HEAD")
        if record.get("observed_utc") != document["observed_utc"]:
            reject("SNAPSHOT_DATE_MISMATCH")
        if record.get("draft") not in (True, False) or record.get("merged") is not False:
            reject("NOT_OPEN_UNMERGED")
        nums = [ci.get(x) for x in ("success", "failure", "cancelled", "pending")]
        if any(not isinstance(n, int) or isinstance(n, bool) or n < 0 for n in nums):
            reject("INVALID_CI_COUNTS")
        if ci.get("scope") != "COMMIT_SCOPED_FIRST_PAGE":
            reject("MISREPRESENTED_CI_COVERAGE")
        if sum(nums) == 0:
            reject("CI_TOKEN_VAZIO_NOT_TYPED")
        risks = record.get("risk_codes")
        gaps = record.get("missing_evidence")
        if not isinstance(risks, list) or not risks or len(risks) != len(set(risks)) or any(r not in RISK_LEVELS for r in risks):
            reject("UNKNOWN_OR_DUPLICATED_RISK")
        if not isinstance(gaps, list) or not gaps or len(gaps) != len(set(gaps)):
            reject("MISSING_TYPED_EVIDENCE")
        if ci["failure"] and "CI_FAILURE" not in risks:
            reject("FAILED_CI_PROMOTED")
        if ci["pending"] and "CI_PENDING" not in gaps:
            reject("PENDING_CI_UNACKNOWLEDGED")
        for risk, required in REQUIRED_MISSING.items():
            if risk in risks and required not in gaps:
                reject("REQUIRED_GAP_ERASED:" + required)
        if record.get("claim_allowed") is not False or record.get("merge_allowed") is not False:
            reject("PR_AUTOPROMOTION_FORBIDDEN")
        priority = min((RISK_LEVELS[x] for x in risks), key=LEVEL.__getitem__)
        if record.get("priority") != priority:
            reject("RISK_PRIORITY_UNDERSTATED")
        if record.get("next_owner_action") in ("", None):
            reject("UNASSIGNED_NEXT_ACTION")
        evidence = record.get("evidence_urls")
        if not isinstance(evidence, list) or not evidence or any(
            not isinstance(u, str) or not u.startswith("https://github.com/" + name + "/")
            for u in evidence
        ):
            reject("UNTRUSTED_EVIDENCE_URL")
        counts[priority] += 1
        unclosed.append({"pr": key, "priority": priority, "risk_codes": risks,
                         "missing_evidence": gaps, "gate": "HOLD"})
    digest = hashlib.sha256(json.dumps(document, sort_keys=True,
                          ensure_ascii=False, separators=(",", ":")).encode("utf-8")).hexdigest()
    return {
        "schema": "rll.federated_pr_assurance_receipt.v1",
        "state": "PASS_SCOPED_SCHEMA_ONLY",
        "snapshot_freshness": "STALE" if stale else "CURRENT_WITHIN_7D",
        "snapshot_utc": document["observed_utc"],
        "as_of_utc": check_date.isoformat(),
        "snapshot_sha256_canonical_json": digest,
        "inventory_personal_plus_institute": 57,
        "scoped_records": len(records),
        "not_individually_assessed": 57-len(records),
        "external_firebird_outgoing_separate": 3,
        "scoped_priority_counts": counts,
        "gate": "HOLD_ALL_OBSERVED_PR",
        "unresolved": unclosed,
        "physical_device_execution": "NOT_RUN",
        "live_github_refresh": "NOT_RUN",
        "external_settings_authority": "TOKEN_VAZIO",
        "full_ci_on_all_57": "NOT_RUN",
        "bayesian_science_posterior": "TOKEN_VAZIO",
        "claim_allowed": False,
        "merge_allowed": False,
    }

def main() -> int:
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--input", type=Path, default=DEFAULT)
    ap.add_argument("--output", type=Path)
    ap.add_argument("--as-of", dest="as_of")
    ap.add_argument("--require-schema", action="store_true")
    ap.add_argument("--require-closure", action="store_true")
    args = ap.parse_args()
    doc = json.loads(args.input.read_text(encoding="utf-8"))
    result = verify(doc, args.as_of)
    out = json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2) + "\n"
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        args.output.write_text(out, encoding="utf-8")
    print(out)
    if args.require_closure and (result["gate"] != "PASS" or result["snapshot_freshness"] == "STALE"):
        return 2
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
