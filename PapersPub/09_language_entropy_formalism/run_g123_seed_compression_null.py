#!/usr/bin/env python3
from __future__ import annotations
import argparse, csv, gzip, hashlib, json, random, statistics
from pathlib import Path

import brotli
import zstandard as zstd

from benchmark_scd1 import aq, pt, merge

LANGS=("eng","spa","por")
SEED=20260921
N_PERM=32
EXPECTED_BASELINE="960d1c6601229ff5dee138e21e826724e94ef4952536dcf97db5b46b70e82c8f"

def b(s:str)->bytes: return s.encode("utf-8")
def sha_bytes(x:bytes)->str: return hashlib.sha256(x).hexdigest()
def jdump(x)->str: return json.dumps(x,ensure_ascii=False,separators=(",",":"),sort_keys=True)

def codecs(data:bytes)->dict[str,int]:
    return {
        "raw":len(data),
        "gzip_9":len(gzip.compress(data,compresslevel=9,mtime=0)),
        "zstd_19":len(zstd.ZstdCompressor(level=19).compress(data)),
        "brotli_11":len(brotli.compress(data,quality=11)),
    }

def build_objects(maps:dict[str,dict[str,str]], refs:list[str]):
    records=[{"ref":r,"lang":l,"text":maps[l][r]} for r in refs for l in LANGS]
    seed_obj={"schema":"SCD1","scope":"normalized_verse_corpus","refs":refs,
              "texts":{l:[maps[l][r] for r in refs] for l in LANGS}}
    recon=[{"ref":r,"lang":l,"text":seed_obj["texts"][l][i]}
           for i,r in enumerate(seed_obj["refs"]) for l in LANGS]
    plain="\n".join("\n".join(maps[l][r] for r in refs) for l in LANGS)
    return jdump(records), jdump(seed_obj), jdump(recon), plain

def load_bible(args):
    eng=merge([(args.eng_root/"eng/json/01.content.json","01"),(args.eng_root/"eng/json/40.content.json","40"),(args.eng_root/"eng/json/43.content.json","43")],aq)
    spa=merge([(args.spa_root/"spa/json/01.content.json","01"),(args.spa_root/"spa/json/40.content.json","40"),(args.spa_root/"spa/json/43.content.json","43")],aq)
    por=merge([(args.por_root/"textos/f4/tr/gen.txt","01"),(args.por_root/"textos/f4/tr/mat.txt","40"),(args.por_root/"textos/f4/tr/joao.txt","43")],pt)
    maps={"eng":eng,"spa":spa,"por":por}
    refs=sorted(set(eng)&set(spa)&set(por))
    return maps,refs

def file_sha(path:Path)->str:
    return hashlib.sha256(path.read_bytes()).hexdigest()

def source_checks(args, reference):
    paths={
      "eng_genesis":args.eng_root/"eng/json/01.content.json", "eng_matthew":args.eng_root/"eng/json/40.content.json", "eng_john":args.eng_root/"eng/json/43.content.json",
      "spa_genesis":args.spa_root/"spa/json/01.content.json", "spa_matthew":args.spa_root/"spa/json/40.content.json", "spa_john":args.spa_root/"spa/json/43.content.json",
      "por_genesis":args.por_root/"textos/f4/tr/gen.txt", "por_matthew":args.por_root/"textos/f4/tr/mat.txt", "por_john":args.por_root/"textos/f4/tr/joao.txt"}
    expected=reference["source_sha256_utf8"]
    out={}
    for k,p in paths.items():
        actual=file_sha(p)
        out[k]={"actual":actual,"expected":expected[k],"match":actual==expected[k]}
    return out

def seed_from_lists(refs, texts, scope):
    obj={"schema":"SCD1","scope":scope,"refs":refs,"texts":texts}
    return jdump(obj)

def unique_labels(n,rng):
    out=set()
    while len(out)<n: out.add(f"{rng.randrange(100_000_000):08d}")
    return list(out)

def null_distributions(refs,maps):
    canonical=seed_from_lists(refs,{l:[maps[l][r] for r in refs] for l in LANGS},"normalized_verse_corpus")
    metric0=codecs(b(canonical))["zstd_19"]
    dist={"common_order_shuffle":[],"independent_language_shuffle":[],"label_permutation":[]}
    for i in range(N_PERM):
        rng=random.Random(SEED+i)
        rr=refs.copy(); rng.shuffle(rr)
        s=seed_from_lists(rr,{l:[maps[l][r] for r in rr] for l in LANGS},"null_common_order")
        dist["common_order_shuffle"].append(codecs(b(s))["zstd_19"])
        texts={l:[maps[l][r] for r in refs] for l in LANGS}
        for l in LANGS: rng.shuffle(texts[l])
        s=seed_from_lists(refs,texts,"null_independent_language")
        dist["independent_language_shuffle"].append(codecs(b(s))["zstd_19"])
        labels=unique_labels(len(refs),rng)
        s=seed_from_lists(labels,{l:[maps[l][r] for r in refs] for l in LANGS},"null_label_permutation")
        dist["label_permutation"].append(codecs(b(s))["zstd_19"])
    summary={}
    for k,v in dist.items():
        better=sum(x<=metric0 for x in v)
        summary[k]={"n":len(v),"canonical_zstd_bytes":metric0,"null_min":min(v),"null_median":statistics.median(v),"null_max":max(v),
                    "null_le_canonical_count":better,"empirical_p_one_sided":round((better+1)/(len(v)+1),6),"samples":v}
    return summary

def load_udhr(path:Path):
    with path.open("r",encoding="utf-8",newline="") as f:
        rows=list(csv.reader(f,delimiter="\t"))
    header=rows[0]; bylang={row[0]:row for row in rows[1:] if row}
    chosen={l:bylang.get(l) for l in LANGS}
    if any(v is None for v in chosen.values()):
        return {"status":"TOKEN_VAZIO_LANGUAGE_ROWS","available_sample":sorted(bylang)[:30]}
    refs=[]; texts={l:[] for l in LANGS}
    for idx,col in enumerate(header[1:],start=1):
        vals=[chosen[l][idx].strip() if idx<len(chosen[l]) else "" for l in LANGS]
        if all(vals):
            refs.append(col)
            for l,val in zip(LANGS,vals): texts[l].append(val)
    records=[{"ref":r,"lang":l,"text":texts[l][i]} for i,r in enumerate(refs) for l in LANGS]
    seed={"schema":"SCD1","scope":"UDHR_parallel_control","refs":refs,"texts":texts}
    recon=[{"ref":r,"lang":l,"text":seed["texts"][l][i]} for i,r in enumerate(seed["refs"]) for l in LANGS]
    plain="\n".join("\n".join(texts[l]) for l in LANGS)
    vr,ss,rr=jdump(records),jdump(seed),jdump(recon)
    return {"status":"ANALYSIS_RUN","aligned_segments":len(refs),"normalized_records":len(records),"exact_reconstruction":vr==rr,
            "sha256":{"baseline":sha_bytes(b(vr)),"reconstructed":sha_bytes(b(rr))},
            "bytes":{"verbose":codecs(b(vr)),"seed":codecs(b(ss)),"plain":codecs(b(plain))}}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--eng-root",type=Path,required=True); ap.add_argument("--spa-root",type=Path,required=True); ap.add_argument("--por-root",type=Path,required=True)
    ap.add_argument("--reference",type=Path,required=True); ap.add_argument("--udhr",type=Path); ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    reference=json.loads(args.reference.read_text(encoding="utf-8"))
    maps,refs=load_bible(args)
    verbose,seed,recon,plain=build_objects(maps,refs)
    checks=source_checks(args,reference)
    g1_ok=all(x["match"] for x in checks.values()) and verbose==recon and sha_bytes(b(verbose))==EXPECTED_BASELINE
    schema_contract=jdump({"schema":"SCD1","refs":"ordered shared reference vector","texts":"language keyed arrays aligned to refs","reconstruction":"cartesian traversal refs-major then lang order eng,spa,por"})
    impl_bytes=(Path(__file__).with_name("benchmark_scd1.py")).stat().st_size
    reps={"verbose":codecs(b(verbose)),"seed":codecs(b(seed)),"plain":codecs(b(plain))}
    best_seed=min(reps["seed"][k] for k in ("gzip_9","zstd_19","brotli_11"))
    best_plain=min(reps["plain"][k] for k in ("gzip_9","zstd_19","brotli_11"))
    custom_overhead=len(b(schema_contract))+impl_bytes
    g2={"representations":reps,"accounting":{
          "mode":"artifact_specific_total_with_repository_local_decoder_upper_bound",
          "schema_contract_bytes":len(b(schema_contract)),"decoder_implementation_bytes":impl_bytes,
          "external_generic_codec_runtime_bytes":"TOKEN_VAZIO_EXTERNAL_RUNTIME",
          "best_seed_compressed_payload_bytes":best_seed,"best_plain_compressed_payload_bytes":best_plain,
          "best_seed_plus_custom_overhead_bytes":best_seed+custom_overhead},
        "strong_claim_pass":best_seed+custom_overhead<best_plain,
        "strong_claim":"SCD1 custom representation beats the best generic-compressed plain-text baseline after counted repository-local schema+decoder overhead."}
    nulls=null_distributions(refs,maps)
    g3_pass=all(v["empirical_p_one_sided"]<=0.05 for v in nulls.values())
    result={"mu_id":"MU-RLL-G123-SEED-COMPRESSION-NULL-20260921","status":"ANALYSIS_RUN","claim_allowed":False,
      "preregistered":{"seed":SEED,"n_permutations":N_PERM,"null_metric":"zstd_19 compressed bytes of SCD1 seed","null_gate":"canonical must beat >=95% of each null family"},
      "G1_seed_reconstruction":{"status":"PASS" if g1_ok else "FAIL","source_sha256":checks,"intersection":len(refs),"normalized_records":len(refs)*3,
         "exact_reconstruction":verbose==recon,"baseline_sha256":sha_bytes(b(verbose)),"reconstructed_sha256":sha_bytes(b(recon)),"expected_baseline_sha256":EXPECTED_BASELINE},
      "G2_total_cost_compression":g2,
      "G3_null_shuffle":{"status":"PASS" if g3_pass else "FAIL_OR_INCONCLUSIVE","nulls":nulls,
         "nonreligious_parallel_control":load_udhr(args.udhr) if args.udhr else {"status":"TOKEN_VAZIO_NO_SOURCE"}},
      "boundaries":["SINTROPIA_OPERACIONAL != ENTROPIA_TERMODINAMICA_NEGATIVA","TOKEN_VAZIO != ZERO","compression payload != total system cost","single-corpus null result != universal semantic law"]}
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))
    if not g1_ok: raise SystemExit(2)

if __name__=="__main__": main()
