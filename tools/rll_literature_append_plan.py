"""Read-only append planning for #1247; revisions require separate review."""
import copy
import hashlib
import json

from tools.rll_literature import collect
from tools.rll_literature_writer_preflight import preflight


def _encode(value):
    return (json.dumps(value, sort_keys=True, ensure_ascii=False,
                       allow_nan=False, indent=2) + "\n").encode("utf-8")


def plan_append(baseline, expected_blob, search):
    """Build a DOI-only candidate without overwriting existing evidence.

    search is injected; there is no default network transport or writer.
    Existing-record revisions are returned separately with their full proposed
    content, never incorporated into the append candidate.
    """
    initial = preflight(baseline, baseline, expected_blob)
    if initial["state"] != "NOOP_NO_WRITE":
        return {"candidate": None, "deferred_revisions": {}, "receipt": initial}
    old = json.loads(baseline)
    # The preflight accepts legacy records without a questions mapping.
    # Normalize only the private working copy for collection.
    working = copy.deepcopy(old["records"])
    legacy = {doi for doi, row in working.items()
              if not isinstance(row.get("questions"), dict)}
    for doi in legacy:
        working[doi]["questions"] = {}
    observed = collect(working, search)
    for doi in legacy:
        if not observed[doi]["questions"]:
            # No matching discovery: do not invent a metadata revision.
            if "questions" in old["records"][doi]:
                observed[doi]["questions"] = old["records"][doi]["questions"]
            else:
                observed[doi].pop("questions")
    candidate = copy.deepcopy(old)
    deferred = {}
    for doi, row in observed.items():
        if doi in old["records"]:
            if _encode(row) != _encode(old["records"][doi]):
                deferred[doi] = {
                    "predecessor_sha256": hashlib.sha256(
                        _encode(old["records"][doi])).hexdigest(),
                    "proposed_record": row,
                    "state": "REVIEW_REQUIRED",
                }
        else:
            candidate["records"][doi] = row
    candidate["added_dois"] = sorted(candidate["records"].keys() - old["records"].keys())
    candidate["baseline_sha256"] = hashlib.sha256(baseline).hexdigest()
    raw = _encode(candidate)
    receipt = preflight(baseline, raw, expected_blob)
    receipt["deferred_revision_count"] = len(deferred)
    return {"candidate": None if receipt["state"] == "REJECTED" else raw,
            "deferred_revisions": deferred, "receipt": receipt}
