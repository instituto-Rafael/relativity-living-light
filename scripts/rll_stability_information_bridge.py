#!/usr/bin/env python3
"""RLL: interpret SCD1 trilingual compression as information metrics only.
Do not infer cyclone or atmospheric thermodynamic entropy from text encoding.
"""
from __future__ import annotations
import bz2, gzip, hashlib, json, lzma, math
from collections import Counter
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
SCD1=ROOT/"PapersPub/09_language_entropy_formalism/results/SCD1_20260920.json"

# Original multilingual synthetic fixture, NOT biblical corpus or weather data.
SAMPLE={
 "eng":"The warm sea stores energy. The wind moves moist air. A storm can change its structure.",
 "spa":"El mar cálido almacena energía. El viento mueve aire húmedo. Una tormenta puede cambiar su estructura.",
 "por":"O mar quente armazena energia. O vento move ar úmido. Uma tempestade pode mudar sua estrutura.",
}
def measure(text: str) -> dict:
    payload=((text+"\n")*64).encode("utf-8")
    freq=Counter(payload)
    h=-sum((n/len(payload))*math.log2(n/len(payload)) for n in freq.values())
    encoded={"gzip":gzip.compress(payload,compresslevel=9,mtime=0),
             "bz2":bz2.compress(payload,compresslevel=9),
             "lzma":lzma.compress(payload,preset=9)}
    assert gzip.decompress(encoded["gzip"])==payload
    assert bz2.decompress(encoded["bz2"])==payload
    assert lzma.decompress(encoded["lzma"])==payload
    return {"raw_bytes":len(payload),"entropy_bits_per_byte":round(h,8),
      "compressed_bytes":{k:len(v) for k,v in encoded.items()},
      "compressed_to_raw_ratio":{k:round(len(v)/len(payload),8) for k,v in encoded.items()},
      "sha256_utf8":hashlib.sha256(payload).hexdigest(),"lossless":True}

def run(scd1: Path=SCD1) -> dict:
    fixture={lang:measure(txt) for lang,txt in SAMPLE.items()}
    ratios={x:fixture[x]["compressed_to_raw_ratio"]["gzip"] for x in fixture}
    assert len(set(ratios.values()))>1, "Counterexample must have unequal ratios"
    receipt={"schema":"rll.stability_information.receipt.v1",
      "claim_allowed":False,"physical_coupling_established":False,
      "forecast_skill_established":False,
      "compression_rate_identical_across_languages":False,
      "scope":"ORIGINAL_SYNTHETIC_COUNTEREXAMPLE_PLUS_PREVIOUS_SCD1_METADATA",
      "synthetic_fixture":fixture,"scd1":"TOKEN_VAZIO_PREDECESSOR_NOT_READ"}
    if scd1.is_file():
        v=json.loads(scd1.read_text(encoding="utf-8"))
        assert v["normalized_records"]==10449
        assert v["verse_counts_raw"]["intersection"]==3483
        assert v["exact_reconstruction"]["normalized_json_equal"] is True
        assert v["bytes"]["scd1_shared_refs_seed"]>v["bytes"]["plain_text_only"]
        receipt["scd1"]={
          "state":"PREVIOUS_MEASUREMENTS_REUSED_NOT_RERUN",
          "books":["Genesis","Matthew","John"],
          "languages":["eng","spa","por"],
          "aligned_verses_per_language":3483,"records":10449,
          "seed_vs_verbose_pct":v["deltas"]["seed_vs_verbose_pct"],
          "seed_vs_plain_pct":v["deltas"]["seed_vs_plain_pct"],
          "per_language_compression_ratio":"TOKEN_VAZIO_UNMEASURED_BY_SCD1",
          "normalized_reconstruction_pass":True}
    return receipt

if __name__=="__main__":
    print(json.dumps(run(),sort_keys=True,ensure_ascii=False,indent=2))
