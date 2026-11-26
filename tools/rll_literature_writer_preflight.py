"""Read-only bibliographic append preflight; never authorizes or performs writes."""
import argparse
import hashlib
import json
import math
import re
from pathlib import Path

_BOOKKEEPING = {"added_dois", "retrieved_utc", "execution_mode", "baseline_sha256", "claim_allowed"}
_DOI = re.compile(r"10\.\d{4,9}/\S+\Z")


def blob(raw):
    return hashlib.sha1(b"blob " + str(len(raw)).encode("ascii") + b"\0" + raw).hexdigest()


def _pairs(pairs):
    out = {}
    for key, value in pairs:
        if key in out:
            raise ValueError("DUPLICATE_JSON_KEY")
        out[key] = value
    return out


def _bad_constant(_value):
    raise ValueError("NONFINITE_JSON")


def _finite_float(value):
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("NONFINITE_JSON")
    return result


def _check_claims(node):
    if isinstance(node, dict):
        for key, value in node.items():
            if key == "claim_allowed" and value is not False:
                raise ValueError("CLAIM_NOT_FALSE")
            _check_claims(value)
    elif isinstance(node, list):
        for value in node:
            _check_claims(value)


def _load(raw):
    value = json.loads(raw.decode("utf-8"), object_pairs_hook=_pairs, parse_constant=_bad_constant,
                       parse_float=_finite_float)
    if not isinstance(value, dict) or not isinstance(value.get("records"), dict):
        raise ValueError("RECORDS_CONTRACT")
    _check_claims(value)
    for doi, record in value["records"].items():
        if (not _DOI.fullmatch(doi) or doi != doi.lower() or not isinstance(record, dict)
                or record.get("source") != "https://doi.org/" + doi
                or record.get("claim_allowed") is not False):
            raise ValueError("DOI_RECORD_CONTRACT")
    return value


def _canonical(value):
    return json.dumps(value, sort_keys=True, ensure_ascii=False, allow_nan=False, separators=(",", ":"))


def preflight(baseline, candidate, expected_blob):
    """Verify exact predecessor and append-only DOI records, not the full online writer."""
    receipt = dict(schema="rll.literature_writer_preflight.v1", baseline_blob=blob(baseline),
                   candidate_blob=blob(candidate), baseline_sha256=hashlib.sha256(baseline).hexdigest(),
                   candidate_sha256=hashlib.sha256(candidate).hexdigest(),
                   claim_allowed=False, write_allowed=False, writer_execution="NOT_RUN")
    try:
        if receipt["baseline_blob"] != expected_blob:
            raise ValueError("STALE_PREDECESSOR")
        old, new = _load(baseline), _load(candidate)
        before, after = old["records"], new["records"]
        if not before.keys() <= after.keys():
            raise ValueError("RECORD_REMOVAL")
        if any(_canonical(before[k]) != _canonical(after[k]) for k in before):
            raise ValueError("UNARCHIVED_RECORD_MUTATION")
        protected = (old.keys() | new.keys()) - _BOOKKEEPING - {"records"}
        if any(k not in old or k not in new or _canonical(old[k]) != _canonical(new[k]) for k in protected):
            raise ValueError("UNREVIEWED_METADATA_CHANGE")
        added = sorted(after.keys() - before.keys())
        if added and (new.get("added_dois") != added or new.get("baseline_sha256") != receipt["baseline_sha256"]):
            raise ValueError("DELTA_BINDING_MISMATCH")
        receipt.update(state="CANDIDATE_REQUIRES_AUTHORITY" if added else "NOOP_NO_WRITE",
                       before_count=len(before), after_count=len(after), added_dois=added, reason=None)
    except (ValueError, TypeError, RecursionError) as exc:
        receipt.update(state="REJECTED", reason=str(exc))
    return receipt


def main():
    p = argparse.ArgumentParser(description=__doc__)
    p.add_argument("--baseline", type=Path, required=True)
    p.add_argument("--candidate", type=Path, required=True)
    p.add_argument("--expected-blob", required=True)
    a = p.parse_args()
    result = preflight(a.baseline.read_bytes(), a.candidate.read_bytes(), a.expected_blob)
    print(json.dumps(result, sort_keys=True, allow_nan=False))
    return 0 if result["state"] == "NOOP_NO_WRITE" else 2


if __name__ == "__main__":
    raise SystemExit(main())
