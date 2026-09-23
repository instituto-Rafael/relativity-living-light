#!/usr/bin/env python3
"""SCD1 structural benchmark for Genesis + Matthew + John across ENG/SPA/POR.

Scope: exact reconstruction of the normalized verse corpus only.
This is not a claim of universal compression and does not reconstruct source
editorial metadata/formatting stripped during normalization.
"""
from __future__ import annotations
import argparse, hashlib, html, json, re
from pathlib import Path

BOOKS = {"01": "Genesis", "40": "Matthew", "43": "John"}

def read(p: Path) -> str:
    return p.read_text(encoding="utf-8-sig")

def aq(path: Path) -> dict[str,str]:
    out={}
    for x in json.loads(read(path)):
        s=re.sub(r"<sup\b[^>]*>[\s\S]*?</sup>", "", x.get("content",""), flags=re.I)
        s=re.sub(r"<[^>]+>", " ", s)
        out[str(x["index_reference"])]=re.sub(r"\s+"," ",html.unescape(s)).strip()
    return out

def pt(path: Path, book: str) -> dict[str,str]:
    out={}; ref=None; buf=[]; foot=0
    def flush():
        nonlocal buf
        if ref:
            out[ref]=re.sub(r"\s+"," "," ".join(buf)).strip()
        buf=[]
    for line in read(path).replace("\r","").split("\n"):
        m=re.match(r"^\\v\s+([A-Za-z]+)\.(\d+)\.(\d+)",line)
        if m:
            flush()
            ref=book+f"{int(m.group(2)):03d}{int(m.group(3)):03d}"
            foot=0; continue
        if re.match(r"^\\fn\b",line): foot+=1; continue
        if re.match(r"^\\\*fn\b",line):
            foot=max(0,foot-1); continue
        if foot or line.startswith("\\"): continue
        if ref and line.strip(): buf.append(line.strip())
    flush(); return out

def merge(paths, parser):
    d={}
    for p,b in paths:
        d.update(parser(p,b) if parser is pt else parser(p))
    return d

def sha(s:str)->str:
    return hashlib.sha256(s.encode("utf-8")).hexdigest()

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--eng-root",type=Path,required=True)
    ap.add_argument("--spa-root",type=Path,required=True)
    ap.add_argument("--por-root",type=Path,required=True)
    args=ap.parse_args()
    eng=merge([(args.eng_root/"eng/json/01.content.json","01"),
               (args.eng_root/"eng/json/40.content.json","40"),
               (args.eng_root/"eng/json/43.content.json","43")], aq)
    spa=merge([(args.spa_root/"spa/json/01.content.json","01"),
               (args.spa_root/"spa/json/40.content.json","40"),
               (args.spa_root/"spa/json/43.content.json","43")], aq)
    por=merge([(args.por_root/"textos/f4/tr/gen.txt","01"),
               (args.por_root/"textos/f4/tr/mat.txt","40"),
               (args.por_root/"textos/f4/tr/joao.txt","43")], pt)
    maps={"eng":eng,"spa":spa,"por":por}
    refs=sorted(set(eng)&set(spa)&set(por))
    records=[{"ref":r,"lang":l,"text":maps[l][r]} for r in refs for l in ("eng","spa","por")]
    baseline=json.dumps(records,ensure_ascii=False,separators=(",",":"))
    seed_obj={"schema":"SCD1","scope":"normalized_verse_corpus","refs":refs,
              "texts":{l:[maps[l][r] for r in refs] for l in ("eng","spa","por")}}
    seed=json.dumps(seed_obj,ensure_ascii=False,separators=(",",":"))
    recon=[{"ref":r,"lang":l,"text":seed_obj["texts"][l][i]}
           for i,r in enumerate(seed_obj["refs"]) for l in ("eng","spa","por")]
    recon_s=json.dumps(recon,ensure_ascii=False,separators=(",",":"))
    plain="\n".join("\n".join(maps[l][r] for r in refs) for l in ("eng","spa","por"))
    B=lambda s: len(s.encode("utf-8"))
    b,s,t=B(baseline),B(seed),B(plain)
    result={
      "status":"ANALYSIS_RUN_NORMALIZED_CORPUS",
      "verse_counts_raw":{"eng":len(eng),"spa":len(spa),"por":len(por),"intersection":len(refs)},
      "selected_books":["Genesis","Matthew","John"],
      "normalized_records":len(records),
      "bytes":{"verbose_records_json":b,"scd1_shared_refs_seed":s,"plain_text_only":t},
      "deltas":{"seed_vs_verbose_bytes":b-s,"seed_vs_verbose_pct":round((b-s)*100/b,3),
                "seed_vs_plain_bytes":s-t,"seed_vs_plain_pct":round((s-t)*100/t,3)},
      "exact_reconstruction":{"normalized_json_equal":baseline==recon_s,
          "baseline_sha256":sha(baseline),"reconstructed_sha256":sha(recon_s),"seed_sha256":sha(seed)}
    }
    print(json.dumps(result,ensure_ascii=False,indent=2,sort_keys=True))

if __name__=="__main__":
    main()
