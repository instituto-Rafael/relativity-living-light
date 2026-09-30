#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os, sys
from pathlib import Path
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))
from rx.operator_lab import run_suite

def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)
def sha256_file(path):
    return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def dump(path, payload):
    Path(path).write_text(json.dumps(payload, sort_keys=True, indent=2) + "\n", encoding="utf-8")

def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--suite",default="configs/rll_operator_lab_suite_v1.json")
    ap.add_argument("--output-dir",default="results/operator_lab/v1")
    ns=ap.parse_args(argv)
    suite_path=(ROOT/ns.suite).resolve(); out=(ROOT/ns.output_dir).resolve()
    try:
        suite_path.relative_to(ROOT.resolve()); out.relative_to(ROOT.resolve())
    except ValueError as exc:
        raise SystemExit("path escapes repository root") from exc
    suite=json.loads(suite_path.read_text(encoding="utf-8"))
    receipt=run_suite(suite)
    receipt.pop("receipt_sha256",None)
    receipt.update({
        "run_id":suite.get("suite_id"),
        "repo_ref":os.environ.get("GITHUB_SHA","TOKEN_VAZIO_LOCAL_REF"),
        "source_suite":str(suite_path.relative_to(ROOT)),
        "source_suite_sha256":sha256_file(suite_path),
    })
    receipt["receipt_sha256"]=hashlib.sha256(canonical_json(receipt).encode("utf-8")).hexdigest()
    out.mkdir(parents=True,exist_ok=True); dump(out/"receipt.json",receipt)
    manifest={
        "schema":"rll.operator_lab.manifest.v1","state":receipt["state"],
        "source_files":[
            {"path":"rx/operator_lab.py","sha256":sha256_file(ROOT/"rx/operator_lab.py")},
            {"path":str(suite_path.relative_to(ROOT)),"sha256":sha256_file(suite_path)},
            {"path":"data/governance/RLL_OPERATOR_LAB_CONTRACT_V1.json","sha256":sha256_file(ROOT/"data/governance/RLL_OPERATOR_LAB_CONTRACT_V1.json")},
        ],
        "outputs":["receipt.json","manifest.json","checksums.sha256","evidence_envelope.json"],
        "physics_binding":False,"scientific_gate_effect":"NONE","claim_allowed":False
    }
    dump(out/"manifest.json",manifest)
    (out/"checksums.sha256").write_text(
        "%s  receipt.json\n%s  manifest.json\n" % (sha256_file(out/"receipt.json"),sha256_file(out/"manifest.json")),
        encoding="utf-8"
    )
    print(json.dumps({
        "state":receipt["state"],"output_dir":str(out.relative_to(ROOT)),
        "receipt_file_sha256":sha256_file(out/"receipt.json"),
        "receipt_payload_sha256":receipt["receipt_sha256"],"claim_allowed":False
    },sort_keys=True))
    return 0 if receipt["state"]=="PASS" else 3
if __name__=="__main__":
    raise SystemExit(main())
