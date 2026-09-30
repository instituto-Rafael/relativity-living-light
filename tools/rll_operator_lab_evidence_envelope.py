#!/usr/bin/env python3
from __future__ import annotations
import argparse, hashlib, json, os
from copy import deepcopy
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
ANCHOR_STATES={"NOT_PRESENT","DECLARED","VERIFIED","FAILED","TOKEN_VAZIO"}
def canonical_json(obj):
    return json.dumps(obj,sort_keys=True,separators=(",",":"),ensure_ascii=False,allow_nan=False)
def sha256_bytes(data): return hashlib.sha256(data).hexdigest()
def sha256_file(path): return hashlib.sha256(Path(path).read_bytes()).hexdigest()
def root_material(env):
    keys=["schema_version","envelope_id","subject","artifact_digests","manifest_digest","receipt_chain_head","policy_digest","parent_envelope_root","producer","time_attestation","external_anchors"]
    return {key:env.get(key) for key in keys}
def seal(env):
    out=deepcopy(env); out.pop("envelope_root",None)
    out["envelope_root"]={"algorithm":"SHA-256","value":sha256_bytes(canonical_json(root_material(out)).encode("utf-8"))}
    return out
def validate(env):
    errors=[]
    if env.get("schema_version")!="rmr-zipraf-evidence-envelope-v1": errors.append("unsupported schema_version")
    if env.get("claim_allowed") is not False: errors.append("claim_allowed must be false")
    for idx,anchor in enumerate(env.get("external_anchors") or []):
        if anchor.get("state") not in ANCHOR_STATES: errors.append("external anchor %d has invalid state" % idx)
        if anchor.get("state")=="VERIFIED" and not anchor.get("verification_receipt_ref"):
            errors.append("external anchor %d VERIFIED without verification receipt" % idx)
    observed=env.get("envelope_root") or {}
    expected=sha256_bytes(canonical_json(root_material(env)).encode("utf-8"))
    root_ok=observed.get("algorithm")=="SHA-256" and observed.get("value")==expected
    if not root_ok: errors.append("envelope_root mismatch")
    return {"state":"PASS" if not errors else "FAIL","root_state":"VERIFIED" if root_ok else "FAILED","calculated_root_sha256":expected,"errors":errors,"claim_allowed":False}
def build(receipt_path,manifest_path,repo_ref):
    receipt=json.loads(receipt_path.read_text(encoding="utf-8"))
    if receipt.get("claim_allowed") is not False or receipt.get("physics_binding") is not False:
        raise ValueError("Operator Lab receipt violates fail-closed boundary")
    receipt_digest=sha256_file(receipt_path); manifest_digest=sha256_file(manifest_path)
    env={
      "schema_version":"rmr-zipraf-evidence-envelope-v1",
      "envelope_id":"RLL-OPLAB-EVIDENCE-V1-"+receipt_digest[:16],
      "subject":{"kind":"RLL_OPERATOR_LAB_RECEIPT","run_id":receipt.get("run_id"),"physics_binding":False,"scientific_gate_effect":"NONE"},
      "artifact_digests":[{"artifact_ref":str(receipt_path.relative_to(ROOT)),"algorithm":"SHA-256","value":receipt_digest,"verification_state":"VERIFIED_LOCAL"}],
      "manifest_digest":{"algorithm":"SHA-256","value":manifest_digest,"state":"VERIFIED_LOCAL"},
      "receipt_chain_head":{"algorithm":"SHA-256","value":receipt.get("receipt_sha256"),"state":"DECLARED_FROM_RECEIPT"},
      "policy_digest":{"algorithm":"SHA-256","value":sha256_file(ROOT/"data/governance/RLL_OPERATOR_LAB_CONTRACT_V1.json"),"state":"VERIFIED_LOCAL"},
      "parent_envelope_root":None,
      "producer":{"repository":"instituto-Rafael/relativity-living-light","component":"RLL Operator Lab V1"},
      "time_attestation":{"state":"TOKEN_VAZIO_TRUSTED_TIME","trusted_timestamp_state":"TOKEN_VAZIO"},
      "external_anchors":[
        {"type":"GIT_COMMIT_REF","state":"DECLARED" if repo_ref and repo_ref!="TOKEN_VAZIO_LOCAL_REF" else "TOKEN_VAZIO","locator":None if not repo_ref or repo_ref=="TOKEN_VAZIO_LOCAL_REF" else "instituto-Rafael/relativity-living-light@"+repo_ref,"verification_receipt_ref":None},
        {"type":"ED25519_SIGNATURE","state":"TOKEN_VAZIO","locator":None,"verification_receipt_ref":None},
        {"type":"X509_CERTIFICATE_REF","state":"NOT_PRESENT","locator":None,"verification_receipt_ref":None},
        {"type":"RFC3161_TSA_REF","state":"NOT_PRESENT","locator":None,"verification_receipt_ref":None},
        {"type":"ICP_BRASIL_CERT_REF","state":"NOT_PRESENT","locator":None,"verification_receipt_ref":None},
      ],
      "custody_state":"RLL_OPERATOR_LAB_TESTED_LOCAL","claim_allowed":False,"rollback_ref":None,
    }
    return seal(env)
def main(argv=None):
    ap=argparse.ArgumentParser()
    ap.add_argument("--receipt",default="results/operator_lab/v1/receipt.json")
    ap.add_argument("--manifest",default="results/operator_lab/v1/manifest.json")
    ap.add_argument("--output",default="results/operator_lab/v1/evidence_envelope.json")
    ap.add_argument("--repo-ref",default=None); ap.add_argument("--verify",action="store_true")
    ns=ap.parse_args(argv); output=(ROOT/ns.output).resolve()
    try: output.relative_to(ROOT.resolve())
    except ValueError as exc: raise SystemExit("path escapes repository root") from exc
    if ns.verify:
        result=validate(json.loads(output.read_text(encoding="utf-8")))
        print(json.dumps(result,sort_keys=True)); return 0 if result["state"]=="PASS" else 4
    receipt=(ROOT/ns.receipt).resolve(); manifest=(ROOT/ns.manifest).resolve()
    for path in (receipt,manifest):
        try: path.relative_to(ROOT.resolve())
        except ValueError as exc: raise SystemExit("path escapes repository root") from exc
    env=build(receipt,manifest,ns.repo_ref or os.environ.get("GITHUB_SHA","TOKEN_VAZIO_LOCAL_REF"))
    output.parent.mkdir(parents=True,exist_ok=True)
    output.write_text(json.dumps(env,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    result=validate(env)
    print(json.dumps({"state":result["state"],"output":str(output.relative_to(ROOT)),"envelope_root":env["envelope_root"]["value"],"claim_allowed":False},sort_keys=True))
    return 0 if result["state"]=="PASS" else 4
if __name__=="__main__":
    raise SystemExit(main())
