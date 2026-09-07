"""Bounded gravitational reverberation reference model.

The module implements a *signal-level laboratory* for the decomposition

    direct pulse + damped modes + curvature-like tail + permanent memory.

It is not a numerical-relativity solver and it does not derive quasinormal-mode
frequencies from a black-hole mass/spin.  Those source-specific quantities must
be supplied externally and remain subject to GR/NR validation.
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

    def __post_init__(self) -> None:
        if not math.isfinite(self.amplitude):
            raise ValueError("mode amplitude must be finite")
        if self.frequency_hz < 0.0 or not math.isfinite(self.frequency_hz):
            raise ValueError("frequency_hz must be finite and non-negative")
        if self.damping_time_s <= 0.0 or not math.isfinite(self.damping_time_s):
            raise ValueError("damping_time_s must be finite and > 0")
        if not math.isfinite(self.phase_rad):
            raise ValueError("phase_rad must be finite")

    @property
    def quality_factor(self) -> float:
        """Signal convention Q = pi f tau for exp(-t/tau) damping."""
        return math.pi * self.frequency_hz * self.damping_time_s


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

    def __post_init__(self) -> None:
        if not math.isfinite(self.event_time_s):
            raise ValueError("event_time_s must be finite")
        if not math.isfinite(self.direct_amplitude):
            raise ValueError("direct_amplitude must be finite")
        if self.direct_width_s <= 0.0 or not math.isfinite(self.direct_width_s):
            raise ValueError("direct_width_s must be finite and > 0")
        if not math.isfinite(self.tail_amplitude):
            raise ValueError("tail_amplitude must be finite")
        if self.tail_scale_s <= 0.0 or not math.isfinite(self.tail_scale_s):
            raise ValueError("tail_scale_s must be finite and > 0")
        if self.tail_power <= 0.0 or not math.isfinite(self.tail_power):
            raise ValueError("tail_power must be finite and > 0")
        if not math.isfinite(self.memory_delta):
            raise ValueError("memory_delta must be finite")
        if self.memory_rise_s <= 0.0 or not math.isfinite(self.memory_rise_s):
            raise ValueError("memory_rise_s must be finite and > 0")


@dataclass(frozen=True)
class ResponseSample:
    time_s: float
    retarded_time_s: float
    direct: float
    ringdown: float
    tail: float
    memory: float
    total: float


def propagation_delay_s(distance_m: float, propagation_speed_m_s: float = C_M_S) -> float:
    if distance_m < 0.0 or not math.isfinite(distance_m):
        raise ValueError("distance_m must be finite and non-negative")
    if not 0.0 < propagation_speed_m_s <= C_M_S:
        raise ValueError("propagation speed must be in (0, c]")
    return distance_m / propagation_speed_m_s


def _local_components(local_time_s: float, cfg: ReverberationConfig) -> tuple[float, float, float, float]:
    """Evaluate components at source-local time, with strict causal support."""
    dt = local_time_s - cfg.event_time_s
    if dt < 0.0:
        return 0.0, 0.0, 0.0, 0.0

    direct = cfg.direct_amplitude * math.exp(-0.5 * (dt / cfg.direct_width_s) ** 2)

    ringdown = 0.0
    for mode in cfg.modes:
        ringdown += (
            mode.amplitude
            * math.exp(-dt / mode.damping_time_s)
            * math.cos(2.0 * math.pi * mode.frequency_hz * dt + mode.phase_rad)
        )

    tail = cfg.tail_amplitude * (1.0 + dt / cfg.tail_scale_s) ** (-cfg.tail_power)
    memory = cfg.memory_delta * (1.0 - math.exp(-dt / cfg.memory_rise_s))
    return direct, ringdown, tail, memory


def response_at_observer(
    time_s: float,
    cfg: ReverberationConfig,
    *,
    distance_m: float = 0.0,
    propagation_speed_m_s: float = C_M_S,
) -> ResponseSample:
    """Evaluate the retarded signal at an observer.

    Amplitudes are generic strain-like signal amplitudes. No conversion to
    energy, force or cascade threshold is performed here because that bridge is
    source dependent and currently TOKEN_VAZIO.
    """

    if not math.isfinite(time_s):
        raise ValueError("time_s must be finite")
    delay = propagation_delay_s(distance_m, propagation_speed_m_s)
    retarded = time_s - delay
    direct, ringdown, tail, memory = _local_components(retarded, cfg)
    return ResponseSample(
        time_s=time_s,
        retarded_time_s=retarded,
        direct=direct,
        ringdown=ringdown,
        tail=tail,
        memory=memory,
        total=direct + ringdown + tail + memory,
    )


def sample_response(
    cfg: ReverberationConfig,
    times_s: Iterable[float],
    *,
    distance_m: float = 0.0,
    propagation_speed_m_s: float = C_M_S,
) -> tuple[ResponseSample, ...]:
    return tuple(
        response_at_observer(
            time_s,
            cfg,
            distance_m=distance_m,
            propagation_speed_m_s=propagation_speed_m_s,
        )
        for time_s in times_s
    )


def response_summary(samples: Iterable[ResponseSample], cfg: ReverberationConfig) -> dict:
    sequence = tuple(samples)
    if not sequence:
        raise ValueError("at least one response sample is required")
    return {
        "samples": len(sequence),
        "peak_abs_total": max(abs(sample.total) for sample in sequence),
        "peak_abs_ringdown": max(abs(sample.ringdown) for sample in sequence),
        "final_memory": sequence[-1].memory,
        "configured_memory_delta": cfg.memory_delta,
        "mode_quality_factors": [mode.quality_factor for mode in cfg.modes],
        "claim_allowed": False,
        "energy_mapping": "TOKEN_VAZIO",
    }
