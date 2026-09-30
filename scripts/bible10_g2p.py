#!/usr/bin/env python3
"""Synthetic G2P/TTS adapter for Bible10.

The output is an eSpeak-ng model projection. It is not a recording of native
speakers and must never be labeled measured phonetics. Unsupported voices fail
open as TOKEN_VAZIO instead of aborting the evidence pipeline.
"""
from __future__ import annotations
import argparse, json, shutil, subprocess
from pathlib import Path

def load_rows(path: Path, limit: int):
    rows=[]
    for line in path.read_text(encoding="utf-8").splitlines():
        if line.strip(): rows.append(json.loads(line))
        if len(rows)>=limit: break
    return rows

def ipa_for_text(text: str, voice: str):
    try:
        p=subprocess.run(["espeak-ng","-q","--ipa=3","-v",voice,text],text=True,capture_output=True,check=True)
        return " ".join(p.stdout.split()), "SYNTHETIC_G2P"
    except subprocess.CalledProcessError:
        return "TOKEN_VAZIO", "TOKEN_VAZIO_ESPEAK_VOICE_OR_TEXT"

def render_wav(text: str, voice: str, out: Path):
    try:
        subprocess.run(["espeak-ng","-q","-v",voice,"-w",str(out),text],check=True,capture_output=True)
        return True
    except subprocess.CalledProcessError:
        return False

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--registry",type=Path,required=True)
    ap.add_argument("--corpus",type=Path,required=True)
    ap.add_argument("--out",type=Path,required=True)
    ap.add_argument("--books",default="JHN,GEN,MAT")
    ap.add_argument("--limit-per-book",type=int,default=16)
    ap.add_argument("--render-jhn11",action="store_true")
    a=ap.parse_args()
    if not shutil.which("espeak-ng"): raise SystemExit("TOKEN_VAZIO_ESPEAK_NG_UNAVAILABLE")
    reg=json.loads(a.registry.read_text(encoding="utf-8")); a.out.mkdir(parents=True,exist_ok=True)
    books=[x.strip().upper() for x in a.books.split(',') if x.strip()]
    receipt={"schema":"rll.bible10.synthetic-g2p.v1","engine":"espeak-ng","state":"SYNTHETIC_MODEL_OUTPUT_NOT_GROUND_TRUTH","languages":{},"claim_allowed":False}
    for src in reg["languages"]:
        lang=src["lang"]; voice=src["voice"]; ld=a.out/lang; ld.mkdir(parents=True,exist_ok=True); n=0; empty=0
        with (ld/"phonemes.jsonl").open("w",encoding="utf-8") as f:
            for book in books:
                for row in load_rows(a.corpus/lang/f"{book}.jsonl",a.limit_per_book):
                    ipa,state=ipa_for_text(row["text"],voice)
                    if state!="SYNTHETIC_G2P": empty+=1
                    f.write(json.dumps({"ref":row["ref"],"lang":lang,"voice":voice,"ipa_model_output":ipa,"state":state},ensure_ascii=False,separators=(',',':'))+'\n'); n+=1
        wav=None; wav_state="NOT_REQUESTED"
        if a.render_jhn11:
            first=load_rows(a.corpus/lang/"JHN.jsonl",1)[0]
            candidate=ld/"JHN_1_1.synthetic.wav"
            if render_wav(first["text"],voice,candidate):
                wav=candidate; wav_state="SYNTHETIC_TTS"
            else:
                wav_state="TOKEN_VAZIO_ESPEAK_VOICE_OR_TEXT"
        receipt["languages"][lang]={"voice":voice,"records":n,"g2p_token_vazio_records":empty,"jhn_1_1_wav":str(wav.relative_to(a.out)) if wav else None,"wav_state":wav_state}
    (a.out/"G2P_RECEIPT.json").write_text(json.dumps(receipt,ensure_ascii=False,indent=2,sort_keys=True)+'\n',encoding='utf-8')
    print(json.dumps({"status":"PASS_BOUNDED_SYNTHETIC_G2P","languages":len(reg['languages']),"claim_allowed":False},sort_keys=True))
if __name__=="__main__": main()
