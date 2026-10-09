#!/usr/bin/env python3
"""Fail-closed prior-art chronology check; stdlib only, no corpus ingestion."""
import datetime as dt
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[1]
DEFAULT = ROOT / "data/governance/RLL_GEOMETRY_PRIOR_ART_CROSSWALK_20261008_V1.json"

def parse_utc(s):
    if not isinstance(s, str) or not s.endswith("Z"):
        raise ValueError("timestamp must be UTC ending in Z")
    date = dt.datetime.fromisoformat(s[:-1] + "+00:00")
    if date.utcoffset() != dt.timedelta(0):
        raise ValueError("timestamp not UTC")
    return date

def validate(payload):
    if payload.get("schema") != "rll.geometry_prior_art_crosswalk.v1":
        raise ValueError("schema mismatch")
    if payload.get("claim_allowed") is not False or payload.get("publication_ready") is not False:
        raise ValueError("scientific publication must remain blocked")
    if payload.get("private_corpus_export_allowed") is not False:
        raise ValueError("private-corpus export cannot be permitted")
    raw = json.dumps(payload, ensure_ascii=False)
    for forbidden in ('"raw_message"', '"message_body"', '"secret_value"', '"private_excerpt"'):
        if forbidden in raw:
            raise ValueError("private content field present")
    obs = payload["observation"]
    at = parse_utc(obs["first_observed_user_input_utc"])
    commit = parse_utc(obs["index_commit_utc"])
    if not at < commit:
        raise ValueError("index commit should not precede indexed message")
    if len(obs.get("index_commit", "")) != 40 or len(obs.get("index_blob_sha", "")) != 40:
        raise ValueError("commit/blob SHA must be full 40-character hex")
    for field in ("index_commit", "index_blob_sha"):
        if any(c not in "0123456789abcdef" for c in obs[field]):
            raise ValueError("invalid git SHA")
    papers = payload.get("papers", [])
    if len(papers) != 2 or len({p["arxiv_id"] for p in papers}) != 2:
        raise ValueError("two distinct paper references required")
    computed = []
    for paper in papers:
        pub = parse_utc(paper["first_arxiv_submission_utc"])
        relation = "USER_TOKEN_BEFORE_PAPER" if at < pub else (
            "PAPER_BEFORE_USER_TOKEN" if at > pub else "SAME_TIMESTAMP")
        if relation != paper["chronology"]:
            raise ValueError("chronology mismatch for " + paper["arxiv_id"])
        if paper.get("independent_priority_claim") is not False:
            raise ValueError("prior-art chronology is not an originality claim")
        if paper.get("exact_equivalence") != "TOKEN_VAZIO_NOT_FORMALLY_COMPARED":
            raise ValueError("equivalence may not be promoted without formal review")
        computed.append({"arxiv_id":paper["arxiv_id"],
                         "chronology":relation,
                         "delta_days":(pub-at).total_seconds()/86400})
    return {"schema":payload["schema"],
            "validation_state":"PASS_SCOPED_CHRONOLOGY_ONLY",
            "claim_allowed":False, "publication_ready":False,
            "papers":computed}

def main():
    path = pathlib.Path(sys.argv[1]) if len(sys.argv) > 1 else DEFAULT
    try:
        result = validate(json.loads(path.read_text(encoding="utf-8")))
    except (ValueError, KeyError, TypeError, OSError, json.JSONDecodeError) as exc:
        print("FAIL_CLOSED: " + str(exc), file=sys.stderr)
        return 1
    print(json.dumps(result, ensure_ascii=False, sort_keys=True, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
