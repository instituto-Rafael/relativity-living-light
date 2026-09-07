"""Bounded gravitational reverberation signal laboratory.

Implements: direct pulse + damped modes + tail + persistent memory.
This is not a numerical-relativity solver. Source-specific mode spectra and
strain/energy mappings must be supplied and validated externally.
"""
from __future__ import annotations
from dataclasses import dataclass
import math
from typing import Iterable, Tuple

C_M_S = 299_792_458.0

@dataclass(frozen=True)
class DampedMode:
    amplitude: float
    frequency_hz: float
    damping_time_s: float
    phase_rad: float = 0.0
    def __post_init__(self):
        if not math.isfinite(self.amplitude): raise ValueError("mode amplitude must be finite")
        if self.frequency_hz < 0 or not math.isfinite(self.frequency_hz): raise ValueError("frequency_hz must be finite and non-negative")
        if self.damping_time_s <= 0 or not math.isfinite(self.damping_time_s): raise ValueError("damping_time_s must be finite and > 0")
        if not math.isfinite(self.phase_rad): raise ValueError("phase_rad must be finite")
    @property
    def quality_factor(self): return math.pi * self.frequency_hz * self.damping_time_s

@dataclass(frozen=True)
class ReverberationConfig:
    event_time_s: float = 0.0
    direct_amplitude: float = 0.0
    direct_width_s: float = 1.0
    modes: Tuple[DampedMode, ...] = ()
    tail_amplitude: float = 0.0
    tail_scale_s: float = 1.0
    tail_power: float = 2.0
    memory_delta: float = 0.0
    memory_rise_s: float = 1.0
    def __post_init__(self):
        vals=(self.event_time_s,self.direct_amplitude,self.tail_amplitude,self.memory_delta)
        if not all(math.isfinite(x) for x in vals): raise ValueError("amplitudes/time must be finite")
        if self.direct_width_s<=0 or not math.isfinite(self.direct_width_s): raise ValueError("direct_width_s must be finite and > 0")
        if self.tail_scale_s<=0 or not math.isfinite(self.tail_scale_s): raise ValueError("tail_scale_s must be finite and > 0")
        if self.tail_power<=0 or not math.isfinite(self.tail_power): raise ValueError("tail_power must be finite and > 0")
        if self.memory_rise_s<=0 or not math.isfinite(self.memory_rise_s): raise ValueError("memory_rise_s must be finite and > 0")

@dataclass(frozen=True)
class ResponseSample:
    time_s: float
    retarded_time_s: float
    direct: float
    ringdown: float
    tail: float
    memory: float
    total: float

def propagation_delay_s(distance_m, propagation_speed_m_s=C_M_S):
    if distance_m < 0 or not math.isfinite(distance_m): raise ValueError("distance_m must be finite and non-negative")
    if not 0 < propagation_speed_m_s <= C_M_S: raise ValueError("propagation speed must be in (0, c]")
    return distance_m / propagation_speed_m_s

def _components(local_time_s, cfg):
    dt=local_time_s-cfg.event_time_s
    if dt<0: return 0.0,0.0,0.0,0.0
    direct=cfg.direct_amplitude*math.exp(-0.5*(dt/cfg.direct_width_s)**2)
    ring=sum(m.amplitude*math.exp(-dt/m.damping_time_s)*math.cos(2*math.pi*m.frequency_hz*dt+m.phase_rad) for m in cfg.modes)
    tail=cfg.tail_amplitude*(1+dt/cfg.tail_scale_s)**(-cfg.tail_power)
    memory=cfg.memory_delta*(1-math.exp(-dt/cfg.memory_rise_s))
    return direct,ring,tail,memory

def response_at_observer(time_s,cfg,*,distance_m=0.0,propagation_speed_m_s=C_M_S):
    if not math.isfinite(time_s): raise ValueError("time_s must be finite")
    ret=time_s-propagation_delay_s(distance_m,propagation_speed_m_s)
    d,r,t,m=_components(ret,cfg)
    return ResponseSample(time_s,ret,d,r,t,m,d+r+t+m)

def sample_response(cfg,times_s:Iterable[float],*,distance_m=0.0,propagation_speed_m_s=C_M_S):
    return tuple(response_at_observer(t,cfg,distance_m=distance_m,propagation_speed_m_s=propagation_speed_m_s) for t in times_s)

def response_summary(samples:Iterable[ResponseSample],cfg):
    s=tuple(samples)
    if not s: raise ValueError("at least one response sample is required")
    return {"samples":len(s),"peak_abs_total":max(abs(x.total) for x in s),"peak_abs_ringdown":max(abs(x.ringdown) for x in s),"final_memory":s[-1].memory,"configured_memory_delta":cfg.memory_delta,"mode_quality_factors":[m.quality_factor for m in cfg.modes],"claim_allowed":False,"energy_mapping":"TOKEN_VAZIO"}
