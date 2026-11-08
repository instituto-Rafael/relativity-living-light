#!/usr/bin/env python3
"""Typed Unicode/illustrative IPA vs synthetic acoustics vs toy astrophysical chronospectroscopy.
Never conflate acoustic, gravitational, quantum and cosmological wave phenomena.
SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM.
"""
from __future__ import annotations
import argparse
from collections import Counter
import csv
import hashlib
import json
import math
from pathlib import Path
import struct
import unicodedata
import wave
import zlib

SAMPLE_RATE=8000
SAMPLE_COUNT=4000
C=299792458.0


def entropy(items):
    if not items: raise ValueError("empty distribution")
    counts=Counter(items); n=len(items)
    return -sum((v/n)*math.log2(v/n) for v in counts.values())


def word_measure(row):
    text=row["word"]
    raw=text.encode("utf-8")
    segments=row["ipa_segments"]
    if not segments or not all(isinstance(s,str) and s for s in segments):
        raise ValueError("missing segmented IPA")
    bclasses=Counter(unicodedata.bidirectional(ch) or "UNDEFINED" for ch in text)
    return {"language":row["id"],"word":text,"unicode_nfc":unicodedata.normalize("NFC",text),
            "source_utf8_bytes":len(raw),"source_sha256":hashlib.sha256(raw).hexdigest(),
            "source_entropy_per_byte":entropy(raw),
            "phonetic_ipa":row["ipa"],"ipa_segment_count":len(segments),
            "ipa_token_entropy_exploratory":entropy(segments),
            "prosody":row["prosody"],"writing_direction":row["direction"],
            "bidi_classes_logical_codepoints":dict(sorted(bclasses.items())),
            "zlib9_bytes":len(zlib.compress(raw,9)),"zlib_exact_roundtrip":zlib.decompress(zlib.compress(raw,9))==raw,
            "not_a_language_entropy_estimate":True}


def f0_hz(mode,t):
    if not 0<=t<=1: raise ValueError("normalized time outside [0,1]")
    if mode=="ma1_high_level": return 208.0
    if mode=="ma3_fall_rise":
        return 184.0-75.0*(t/0.6) if t<=0.6 else 109.0+68.0*((t-0.6)/0.4)
    raise ValueError("unknown synthetic tone")


def make_waveform(mode,n=SAMPLE_COUNT,rate=SAMPLE_RATE):
    if rate<1000 or n<=0 or n>16000: raise ValueError("unsupported wave size")
    phase=0.; values=[]; contours=[]
    for i in range(n):
        u=i/max(1,n-1)
        hz=f0_hz(mode,u)
        phase+=2*math.pi*hz/rate
        # Synthetic two-harmonic pressure proxy: normalized PCM, not Pa.
        envelope=0.12+0.88*math.sin(math.pi*u)**2
        v=envelope*(0.65*math.sin(phase)+0.2*math.sin(2*phase))
        values.append(v)
        contours.append(hz)
    return values,contours


def dft_summary(xs,rate=SAMPLE_RATE):
    if len(xs)<32 or len(xs)>512: raise ValueError("DFT bounded 32..512")
    n=len(xs)
    window=[x*(0.5-0.5*math.cos(2*math.pi*i/(n-1))) for i,x in enumerate(xs)]
    energies=[]
    for k in range(1,n//2):
        re=sum(x*math.cos(2*math.pi*k*i/n) for i,x in enumerate(window))
        im=-sum(x*math.sin(2*math.pi*k*i/n) for i,x in enumerate(window))
        energies.append(re*re+im*im)
    total=sum(energies)
    if total<=0:return {"spectral_power_entropy_bits":"TOKEN_VAZIO_ZERO_ENERGY","centroid_hz":"TOKEN_VAZIO_ZERO_ENERGY"}
    ps=[x/total for x in energies if x>0]
    return {"spectral_power_entropy_bits":-sum(p*math.log2(p) for p in ps),
            "centroid_hz":sum((k+1)*(rate/n)*e for k,e in enumerate(energies))/total}


def write_wav(path,values,rate=SAMPLE_RATE):
    path.parent.mkdir(parents=True,exist_ok=True)
    pcm=b"".join(struct.pack("<h",int(round(max(-1,min(1,v))*32767))) for v in values)
    with wave.open(str(path),"wb") as w:
        w.setnchannels(1);w.setsampwidth(2);w.setframerate(rate);w.writeframes(pcm)
    return hashlib.sha256(pcm).hexdigest()


def special_relativity(beta):
    if not (0<=beta<1):raise ValueError("beta must be subluminal")
    g=1/math.sqrt(1-beta*beta)
    # For a purely radial, receding emitter in inertial flat spacetime.
    return {"beta":beta,"gamma":g,"moving_clock_proper_dt_per_frame_dt":1/g,
            "receding_radial_doppler_1_plus_z":math.sqrt((1+beta)/(1-beta)),
            "local_light_speed_m_s":C,"scope":"SPECIAL_RELATIVITY_INERTIAL_RADIAL_TOY_ONLY"}


def stellar_age_discrepancy(star,region,cov=0,common_epoch=True):
    if not common_epoch:raise ValueError("cannot compare ages from unmatched epochs")
    a,sa=map(float,star);b,sb=map(float,region)
    if sa<0 or sb<0:raise ValueError("negative standard deviation")
    v=sa*sa+sb*sb-2*float(cov)
    if v<=0:raise ValueError("zero/nonphysical difference variance")
    return {"star_age_minus_local_population_gyr":a-b,
            "difference_std_gyr":math.sqrt(v),"difference_z_score":(a-b)/math.sqrt(v),
            "physical_interpretation":"A discrepancy is not a causality diagnosis; migration, selection, metallicity and age systematics must be evaluated."}


def produce(doc,outdir):
    if doc.get("schema")!="rll.phonetic_chronospectral.pilot_v1":raise ValueError("schema mismatch")
    lang=doc["language_items"]
    if len(lang)!=10 or len({x["id"] for x in lang})!=10:raise ValueError("10 language pilot mandatory")
    if len({x["word"].encode('utf-8') for x in lang})>=len(lang):raise ValueError("need at least one shared orthography across languages")
    outdir=Path(outdir);outdir.mkdir(parents=True,exist_ok=True)
    rows=[word_measure(x) for x in lang]
    waves={}
    for mode in ("ma1_high_level","ma3_fall_rise"):
        values,contours=make_waveform(mode)
        rawsha=write_wav(outdir/(mode+"_SYNTHETIC_NOT_HUMAN.wav"),values)
        block=dft_summary(values[900:1156])
        waves[mode]={"declared_model":"ILLUSTRATIVE_F0_ONLY_NOT_NATIVE_MANDARIN_AUDIO",
                     "rate_hz":SAMPLE_RATE,"samples":SAMPLE_COUNT,"duration_s":SAMPLE_COUNT/SAMPLE_RATE,
                     "f0_start_hz":contours[0],"f0_mid_hz":contours[SAMPLE_COUNT//2],"f0_end_hz":contours[-1],
                     "normalized_rms":math.sqrt(sum(v*v for v in values)/len(values)),
                     "center_window_dft":block,"pcm16_samples_sha256":rawsha,
                     "physical_acoustic_pressure_pa":"TOKEN_VAZIO_NO_CALIBRATION"}
    context={"astrophysics":{"sr_toy_beta_0p6":special_relativity(0.6),
                             "local_older_interloper_toy":stellar_age_discrepancy((12,1),(2,0.5)),
                             "lookback_time":"TOKEN_VAZIO_REQUIRES_PINNED_HZ_COSMOLOGY_AND_SOURCE_REDSHIFT",
                             "redshift_correction":"TOKEN_VAZIO_SEPARATE_COSMOLOGICAL_PECULIAR_GRAVITATIONAL_COMPONENTS",
                             "stellar_ages_and_membership":"TOKEN_VAZIO_SPECTROSCOPY_ASTROMETRY_CHEMICAL_AND_COVARIANCE",
                             "gravitational_wave_observation":"TOKEN_VAZIO_WAVE_STRAIN_WITH_PROVENANCE"},
             "non_equivalences":["IPA != native speech recording", "waveform FFT != language entropy",
               "acoustic pressure wave != quantum wavefunction != gravitational strain",
               "two same-entropy representations do not imply equal semantics or dynamics",
               "old star in region != older than the universe", "constant speed of light in local vacuum"]}
    result={"schema":"rll.phonetic_chronospectral.receipt_v1", "state":"PASS_SCOPED_SYNTHETIC_PENDING_EXTERNAL_VALIDATION",
            "claim_allowed":False,"phonetics_model_authored":True,"native_speech_measured":False,
            "sampled_speech":False,"real_cosmology_observations":False,"pilot_source":doc["source_anchor"],
            "phonetic_items":rows,"semantic_controls":doc["contrast_controls"],
            "synthetic_tonal_waves":waves,**context,
            "gap":doc["language_specific_gaps"]+["TOKEN_VAZIO_SPECTRO_TEMPORAL_COVARIANCE", "TOKEN_VAZIO_GRAVITY_DYNAMICAL_PERTURBATION"]}
    target=outdir/"receipt.json"
    target.write_text(json.dumps(result,ensure_ascii=False,sort_keys=True,indent=2)+"\n",encoding="utf-8")
    with (outdir/"phoneme_pilot.csv").open("w",newline="",encoding="utf-8") as f:
        writer=csv.DictWriter(f,fieldnames=["language","word","phonetic_ipa","source_utf8_bytes","source_entropy_per_byte","ipa_token_entropy_exploratory","zlib9_bytes","writing_direction"])
        writer.writeheader();writer.writerows({k:x[k] for k in writer.fieldnames} for x in rows)
    return result


def main():
    p=argparse.ArgumentParser()
    p.add_argument("--source",type=Path,default=Path(__file__).resolve().parents[1]/"data/experiments/rll_phonetic_chronospectral_v1/pilot_10_languages.json")
    p.add_argument("--outdir",type=Path,default=Path(__file__).resolve().parents[1]/"data/experiments/rll_phonetic_chronospectral_v1/generated")
    a=p.parse_args();result=produce(json.loads(a.source.read_text(encoding="utf-8")),a.outdir)
    print(json.dumps({"state":result["state"],"languages":len(result["phonetic_items"]),"waves":list(result["synthetic_tonal_waves"]),"outdir":str(a.outdir)},ensure_ascii=False))
if __name__=="__main__":main()
