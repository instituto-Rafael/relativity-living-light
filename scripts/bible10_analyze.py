#!/usr/bin/env python3
from __future__ import annotations
import argparse, bz2, collections, gzip, json, lzma, math, re, statistics, unicodedata, zlib
from pathlib import Path

BOOKS=("JHN","GEN","MAT")

def shannon(seq):
    n=len(seq)
    if not n: return 0.0
    c=collections.Counter(seq)
    return -sum((v/n)*math.log2(v/n) for v in c.values())

def conditional_char_entropy(s):
    s=unicodedata.normalize("NFC",s)
    if len(s)<2: return 0.0
    prev=collections.defaultdict(collections.Counter); totals=collections.Counter()
    for a,b in zip(s,s[1:]):
        prev[a][b]+=1; totals[a]+=1
    n=sum(totals.values()); out=0.0
    for a,t in totals.items():
        out += (t/n)*shannon(list(prev[a].elements()))
    return out

def tokenize(s):
    return re.findall(r"[^\W_]+(?:['’][^\W_]+)?|\d+",s.casefold(),flags=re.UNICODE)

def codecs(b):
    out={
      "raw":len(b),
      "zlib_9":len(zlib.compress(b,9)),
      "gzip_9":len(gzip.compress(b,compresslevel=9,mtime=0)),
      "bz2_9":len(bz2.compress(b,compresslevel=9)),
      "lzma_9":len(lzma.compress(b,preset=9))
    }
    try:
        import brotli
        out["brotli_11"]=len(brotli.compress(b,quality=11))
    except Exception:
        out["brotli_11"]="TOKEN_VAZIO_CODEC_UNAVAILABLE"
    try:
        import zstandard as zstd
        out["zstd_19"]=len(zstd.ZstdCompressor(level=19).compress(b))
    except Exception:
        out["zstd_19"]="TOKEN_VAZIO_CODEC_UNAVAILABLE"
    return out

def isprime(n):
    if n<2:return False
    if n%2==0:return n==2
    d=3
    while d*d<=n:
        if n%d==0:return False
        d+=2
    return True

def load_book(path):
    rows=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip(): rows.append(json.loads(line))
    return rows

def book_metrics(rows):
    text="\n".join(r["text"] for r in rows)
    b=text.encode("utf-8"); cps=list(text); toks=tokenize(text)
    comp=codecs(b)
    ratios={k:(v/len(b) if isinstance(v,int) and len(b) else v) for k,v in comp.items() if k!="raw"}
    prime_verse=sum(isprime(int(re.match(r"\d+",str(r["verse"])).group())) for r in rows)
    prime_chapter=sum(isprime(int(r["chapter"])) for r in rows)
    best_codec=min(((k,v) for k,v in comp.items() if k!="raw" and isinstance(v,int)),key=lambda kv:kv[1],default=("TOKEN_VAZIO",0))
    moduli=(2,3,5,7,12,14,40)
    return {
      "verses":len(rows),
      "bytes_utf8":len(b),
      "codepoints":len(cps),
      "tokens_whitespace_wordish":len(toks),
      "mean_bytes_per_verse":round(len(b)/len(rows),6) if rows else 0.0,
      "mean_tokens_per_verse":round(len(toks)/len(rows),6) if rows else 0.0,
      "shannon_bits_per_byte":round(shannon(list(b)),6),
      "shannon_bits_per_codepoint":round(shannon(cps),6),
      "conditional_char_entropy_order1":round(conditional_char_entropy(text),6),
      "token_entropy_bits":round(shannon(toks),6),
      "type_token_ratio":round(len(set(toks))/len(toks),6) if toks else 0,
      "compression_bytes":comp,
      "compression_ratio_to_raw":ratios,
      "best_codec":{"name":best_codec[0],"bytes":best_codec[1]},
      "number_structure":{
        "prime_numbered_verse_rows":prime_verse,
        "rows_in_prime_numbered_chapters":prime_chapter,
        "verse_count_residues":{str(m):len(rows)%m for m in moduli},
        "interpretation":"INDEX_STRUCTURE_ONLY_NOT_CAUSATION"
      }
    }

def ranks(vals):
    order=sorted(range(len(vals)),key=lambda i:vals[i]); r=[0.0]*len(vals); i=0
    while i<len(order):
        j=i
        while j+1<len(order) and vals[order[j+1]]==vals[order[i]]: j+=1
        avg=(i+j+2)/2
        for k in range(i,j+1): r[order[k]]=avg
        i=j+1
    return r

def spearman(a,b):
    if len(a)<2 or len(a)!=len(b): return 0.0
    ra,rb=ranks(a),ranks(b); ma,mb=statistics.mean(ra),statistics.mean(rb)
    num=sum((x-ma)*(y-mb) for x,y in zip(ra,rb))
    da=math.sqrt(sum((x-ma)**2 for x in ra)); db=math.sqrt(sum((y-mb)**2 for y in rb))
    return num/(da*db) if da and db else 0.0

def poincare_distance(u,v):
    nu=sum(x*x for x in u); nv=sum(x*x for x in v)
    d2=sum((x-y)**2 for x,y in zip(u,v))
    den=max(1e-15,(1-nu)*(1-nv))
    return math.acosh(max(1.0,1+2*d2/den))

def euclidean(u,v):
    return math.sqrt(sum((x-y)**2 for x,y in zip(u,v)))

def radial_embeddings(depth, slot, total_slots, scale=.55):
    ang=2*math.pi*(slot+.5)/max(1,total_slots)
    eu=(depth*scale*math.cos(ang),depth*scale*math.sin(ang))
    rho=math.tanh(depth*scale/2)
    hyp=(rho*math.cos(ang),rho*math.sin(ang))
    return eu,hyp

def geometry_ab(corpus):
    nodes=[]
    for book in BOOKS:
        refs=sorted(corpus[book],key=lambda x:(x["chapter"],str(x["verse"])))
        step=max(1,len(refs)//120)
        for r in refs[::step][:120]:
            nodes.append((book,int(r["chapter"]),str(r["verse"])))
    slots=len(nodes); eu=[]; hy=[]; tree=[]
    for i,(book,ch,v) in enumerate(nodes):
        e,h=radial_embeddings(3,i,slots); eu.append(e); hy.append(h); tree.append((book,ch,v))
    gt=[]; de=[]; dh=[]
    for i in range(len(nodes)):
        for j in range(i+1,len(nodes)):
            a,b=tree[i],tree[j]
            if a[0]!=b[0]: g=6
            elif a[1]!=b[1]: g=4
            else: g=2
            gt.append(g); de.append(euclidean(eu[i],eu[j])); dh.append(poincare_distance(hy[i],hy[j]))
    return {
      "sample_nodes":len(nodes),
      "graph_distance_model":"ROOT_BOOK_CHAPTER_VERSE",
      "euclidean_spearman_to_tree":round(spearman(gt,de),6),
      "poincare_spearman_to_tree":round(spearman(gt,dh),6),
      "baseline_state":"DETERMINISTIC_RADIAL_BASELINE_NOT_OPTIMIZED",
      "boundary":"REPRESENTATIONAL_A_B_ONLY_NOT_PHYSICAL_SPACETIME"
    }

def parallel_order_compression(all_rows):
    langs=sorted(all_rows)
    maps={l:{r["ref"]:r["text"] for r in all_rows[l]} for l in langs}
    refs=sorted(set.intersection(*(set(m) for m in maps.values()))) if maps else []
    ref_major="".join(f"{l}\t{r}\t{maps[l][r]}\n" for r in refs for l in langs).encode("utf-8")
    lang_major="".join(f"{l}\t{r}\t{maps[l][r]}\n" for l in langs for r in refs).encode("utf-8")
    cr={"ref_major":codecs(ref_major),"lang_major":codecs(lang_major)}
    deltas={}
    for k in cr["ref_major"]:
        a,b=cr["ref_major"][k],cr["lang_major"].get(k)
        if isinstance(a,int) and isinstance(b,int): deltas[k]=a-b
    return {
      "aligned_refs":len(refs),
      "same_record_multiset":True,
      "compression_bytes":cr,
      "ref_major_minus_lang_major_bytes":deltas,
      "interpretation":"ORDER_LOCALITY_EFFECT_ONLY_NOT_SEMANTIC_INVARIANT"
    }

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--corpus",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    args=ap.parse_args()
    langs=sorted(p.name for p in args.corpus.iterdir() if p.is_dir())
    results={}; per_lang_john_higher={}; per_lang_matthew_concise={}
    rows_by_book={b:{} for b in BOOKS}
    for lang in langs:
        bm={}; corpus_for_geom={}
        for book in BOOKS:
            rows=load_book(args.corpus/lang/f"{book}.jsonl")
            rows_by_book[book][lang]=rows
            bm[book]=book_metrics(rows); corpus_for_geom[book]=rows
        results[lang]={"books":bm,"geometry_ab":geometry_ab(corpus_for_geom)}
        hj=bm["JHN"]["conditional_char_entropy_order1"]
        per_lang_john_higher[lang]={
          "john_gt_genesis":hj>bm["GEN"]["conditional_char_entropy_order1"],
          "john_gt_matthew":hj>bm["MAT"]["conditional_char_entropy_order1"]
        }
        mt=bm["MAT"]["mean_tokens_per_verse"]
        per_lang_matthew_concise[lang]={
          "matthew_lt_john_tokens_per_verse":mt<bm["JHN"]["mean_tokens_per_verse"],
          "matthew_lt_genesis_tokens_per_verse":mt<bm["GEN"]["mean_tokens_per_verse"]
        }
    wins=sum(v["john_gt_genesis"] and v["john_gt_matthew"] for v in per_lang_john_higher.values())
    concise=sum(v["matthew_lt_john_tokens_per_verse"] and v["matthew_lt_genesis_tokens_per_verse"] for v in per_lang_matthew_concise.values())
    parallel={b:parallel_order_compression(rows_by_book[b]) for b in BOOKS}
    out={
      "schema":"rll.bible10.analysis.v1",
      "languages":langs,
      "books":list(BOOKS),
      "results":results,
      "parallel_order_tests":parallel,
      "codec_suite":["raw","zlib_9","gzip_9","bz2_9","lzma_9","brotli_11","zstd_19"],
      "hypotheses":{
        "H_JOHN_ENTROPY":{
          "metric":"conditional_char_entropy_order1",
          "per_language":per_lang_john_higher,
          "john_higher_than_both_count":wins,
          "status":"OBSERVED_UNPROMOTED" if wins else "NOT_SUPPORTED_IN_THIS_METRIC",
          "claim_allowed":False
        },
        "H_MATTHEW_CONCISION_SURROGATE":{
          "metric":"mean_tokens_per_verse",
          "meaning":"orthographic/token-length surrogate only; not semantic directness",
          "per_language":per_lang_matthew_concise,
          "matthew_lower_than_both_count":concise,
          "status":"OBSERVED_UNPROMOTED" if concise else "NOT_SUPPORTED_IN_THIS_SURROGATE",
          "claim_allowed":False
        },
        "H_LOGOS_GENESIS_RELATION":{
          "status":"TOKEN_VAZIO_REQUIRES_EXPLICIT_CROSS_REFERENCE_OR_SEMANTIC_ANNOTATION",
          "claim_allowed":False
        }
      },
      "boundaries":[
        "compression != semantic truth",
        "orthography != phoneme",
        "text corpus != acoustic measurement",
        "prime indexing != prime causation",
        "Poincare representation != physical spacetime"
      ],
      "claim_allowed":False
    }
    args.out.parent.mkdir(parents=True,exist_ok=True)
    args.out.write_text(json.dumps(out,ensure_ascii=False,indent=2,sort_keys=True)+"\n",encoding="utf-8")
    print(json.dumps({"status":"PASS","languages":len(langs),"john_higher_both":wins,"matthew_concise_both":concise,"claim_allowed":False},sort_keys=True))

if __name__=="__main__":
    main()
