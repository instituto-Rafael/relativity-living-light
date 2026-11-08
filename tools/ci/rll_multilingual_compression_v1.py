#!/usr/bin/env python3
"""Audit-only four-language compression oracle; manually annotated facts, no NLP.

Not an automatic translator, scientific validation, or Bayesian evidence.
"""
from __future__ import annotations
import argparse
import json
from pathlib import Path
import zlib

ROOT=Path(__file__).resolve().parents[2]
LOCALES=("pt","es","en","fr")
SCHEMA="rll.multilingual_semantic_compression_trial.v1"

def compress(text):
    b=text.encode("utf-8")
    if not b: raise ValueError("TOKEN_VAZIO_EMPTY_TEXT")
    c=zlib.compress(b,level=9)
    if zlib.decompress(c)!=b: raise AssertionError("LOSSLESS_CHECK_FAILED")
    return {"bytes_original":len(b),"bytes_zlib":len(c),
            "fraction_saved":1-len(c)/len(b)}

def atoms(a):
    return {str(k)+"="+str(v) for k,v in a.items()}

def assess(data):
    if data.get("schema")!=SCHEMA or data.get("claim_allowed") is not False:
        raise ValueError("SCHEMA_OR_CLAIM_BOUNDARY")
    if data.get("translation_source")!="HAND_AUTHORED_TOY_NO_INDEPENDENT_REPLICATION":
        raise ValueError("TRANSLATION_PROVENANCE")
    records=data["records"]
    if len(records)!=4 or len({r["id"] for r in records})!=4: raise ValueError("RECORD_INVENTORY")
    scores=[]
    for r in records:
        gold=atoms(r["gold_atoms"])
        if not gold: raise ValueError("TOKEN_VAZIO_GOLD_ATOMS")
        seen=[]
        for lang in LOCALES:
            item=r["translations"].get(lang,{})
            if not item.get("text") or "annotated_atoms" not in item:
                raise ValueError("TOKEN_VAZIO_MISSING_LANGUAGE_OR_ANNOTATION:"+lang)
            got=atoms(item["annotated_atoms"]);seen.append(got)
            scores.append({"claim_id":r["id"],"language":lang,
                           "recall":len(gold&got)/len(gold),
                           "missing":sorted(gold-got),"extra":sorted(got-gold)})
        if len(set.union(*seen)) != len(set.intersection(*seen)):
            scores.append({"claim_id":r["id"],"language":"MULTILINGUAL",
                           "recall":0,"missing":["LANGUAGE_DISAGREEMENT"],"extra":[]})
    text={l:"\n".join(r["translations"][l]["text"] for r in records) for l in LOCALES}
    ratio={l:compress(text[l]) for l in LOCALES}
    minimum=min(z["recall"] for z in scores)
    return {"schema":"rll.multilingual_compression_receipt.v1",
            "state":"PASS_SCOPED_MANUAL_ANNOTATIONS" if minimum==1 else "BLOCKED_ANNOTATED_FACT_MISMATCH",
            "languages":list(LOCALES),"records":len(records),
            "compressor":"zlib.level9.utf8","per_language":ratio,
            "worst_annotated_recall":minimum,"issues":[z for z in scores if z["recall"]<1],
            "automatic_semantic_extraction":"NOT_RUN",
            "automatic_translation":"NOT_RUN",
            "independent_scientific_replication":"NOT_RUN",
            "bayesian_posterior":"TOKEN_VAZIO","claim_allowed":False}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--input",type=Path,default=ROOT/"data/contracts/rll_multilingual_semantic_compression_trial.v1.json")
    ap.add_argument("--output",type=Path)
    ap.add_argument("--require-pass",action="store_true")
    args=ap.parse_args()
    result=assess(json.loads(args.input.read_text(encoding="utf-8")))
    output=json.dumps(result,indent=2,ensure_ascii=False,allow_nan=False)+"\n"
    if args.output:
        args.output.parent.mkdir(parents=True,exist_ok=True)
        args.output.write_text(output,encoding="utf-8")
    print(output)
    return 2 if args.require_pass and result["state"]!="PASS_SCOPED_MANUAL_ANNOTATIONS" else 0

if __name__=="__main__":
    raise SystemExit(main())
