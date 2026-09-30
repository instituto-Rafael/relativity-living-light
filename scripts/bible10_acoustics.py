#!/usr/bin/env python3
"""Bounded WAV/acoustic analysis for the RLL Bible10 experiment.

Digital waveform metrics are always permitted. Physical acoustic energy is emitted
only when a pressure calibration is supplied. E=mc^2 is used only as an optional
energy-equivalent mass conversion, never as the acoustic energy law.
"""
from __future__ import annotations
import argparse, json, math, struct, wave
from pathlib import Path

C0 = 299_792_458.0

def pcm_samples(path: Path):
    with wave.open(str(path), "rb") as w:
        channels=w.getnchannels(); width=w.getsampwidth(); rate=w.getframerate(); n=w.getnframes()
        raw=w.readframes(n)
    if width not in (1,2,3,4): raise ValueError("unsupported_pcm_width")
    vals=[]; step=width*channels
    for off in range(0,len(raw)-step+1,step):
        frame=[]
        for c in range(channels):
            b=raw[off+c*width:off+(c+1)*width]
            if width==1: x=b[0]-128; denom=128.0
            elif width==2: x=struct.unpack('<h',b)[0]; denom=32768.0
            elif width==3:
                x=int.from_bytes(b,'little',signed=False)
                if x & 0x800000: x-=1<<24
                denom=float(1<<23)
            else:
                x=struct.unpack('<i',b)[0]; denom=float(1<<31)
            frame.append(x/denom)
        vals.append(sum(frame)/len(frame))
    return rate,channels,width,vals

def zero_crossing_frequency(samples, rate):
    if len(samples)<2:return 0.0
    crossings=0
    for a,b in zip(samples,samples[1:]):
        if (a<0<=b) or (a>=0>b): crossings+=1
    duration=(len(samples)-1)/rate
    return crossings/(2*duration) if duration>0 else 0.0

def analyze(path: Path, calibration_pa_per_full_scale=None, rho=1.2041, c_sound=343.0):
    rate,channels,width,s=pcm_samples(path)
    if not s: raise ValueError("empty_wave")
    rms=math.sqrt(sum(x*x for x in s)/len(s)); peak=max(abs(x) for x in s)
    duration=len(s)/rate; zcf=zero_crossing_frequency(s,rate)
    physical={
      "state":"TOKEN_VAZIO_NO_PRESSURE_CALIBRATION",
      "plane_progressive_wave_assumption":True,
      "air_density_kg_m3":rho,
      "sound_speed_m_s":c_sound,
      "pressure_rms_pa":"TOKEN_VAZIO",
      "intensity_w_m2":"TOKEN_VAZIO",
      "energy_density_j_m3":"TOKEN_VAZIO",
      "mass_equivalent_density_kg_m3":"TOKEN_VAZIO"
    }
    if calibration_pa_per_full_scale is not None:
        p=rms*float(calibration_pa_per_full_scale)
        intensity=(p*p)/(rho*c_sound)
        energy_density=(p*p)/(rho*c_sound*c_sound)
        physical.update({
          "state":"CALIBRATED_UNDER_DECLARED_PLANE_WAVE_ASSUMPTION",
          "calibration_pa_per_full_scale":float(calibration_pa_per_full_scale),
          "pressure_rms_pa":p,
          "intensity_w_m2":intensity,
          "energy_density_j_m3":energy_density,
          "mass_equivalent_density_kg_m3":energy_density/(C0*C0)
        })
    return {
      "schema":"rll.bible10.acoustics.v1",
      "wav":{"sample_rate_hz":rate,"channels":channels,"sample_width_bytes":width,"samples_mono":len(s),"duration_s":duration,"normalized_rms":rms,"normalized_peak":peak,"zero_crossing_frequency_estimate_hz":zcf},
      "physical":physical,
      "boundaries":[
        "normalized_pcm_amplitude is not pascals without calibration",
        "zero_crossing frequency is a waveform descriptor, not a universal phoneme frequency",
        "sound energy uses acoustic pressure/impedance relations under stated assumptions",
        "E=mc^2 is used only for energy-equivalent mass conversion, not as an acoustic mechanism",
        "thermal energy cannot be inferred from an uncalibrated speech WAV"
      ],
      "claim_allowed":False
    }

def main():
    ap=argparse.ArgumentParser(); ap.add_argument("wav",type=Path); ap.add_argument("--out",type=Path)
    ap.add_argument("--calibration-pa-per-full-scale",type=float); ap.add_argument("--rho",type=float,default=1.2041); ap.add_argument("--sound-speed",type=float,default=343.0)
    a=ap.parse_args(); r=analyze(a.wav,a.calibration_pa_per_full_scale,a.rho,a.sound_speed)
    txt=json.dumps(r,ensure_ascii=False,indent=2,sort_keys=True)+"\n"
    if a.out:
        a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(txt,encoding="utf-8")
    else:
        print(txt,end="")
if __name__=="__main__": main()
