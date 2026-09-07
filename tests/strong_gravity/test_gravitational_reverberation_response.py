import math

from data.pipelines.strong_gravity.gravitational_reverberation_response import (
    C_M_S,
    DampedMode,
    ReverberationConfig,
    propagation_delay_s,
    response_at_observer,
    response_summary,
    sample_response,
)


def test_pre_event_response_is_strictly_zero():
    cfg = ReverberationConfig(
        event_time_s=1.0,
        direct_amplitude=2.0,
        modes=(DampedMode(1.0, 10.0, 0.5),),
        tail_amplitude=0.2,
        memory_delta=0.1,
    )
    sample = response_at_observer(0.5, cfg)
    assert sample.total == 0.0
    assert sample.direct == 0.0
    assert sample.ringdown == 0.0
    assert sample.tail == 0.0
    assert sample.memory == 0.0


def test_retarded_response_respects_light_speed_bound():
    distance = C_M_S * 2.0
    cfg = ReverberationConfig(event_time_s=0.0, direct_amplitude=1.0)

    before = response_at_observer(1.999, cfg, distance_m=distance)
    arrival = response_at_observer(2.0, cfg, distance_m=distance)

    assert before.total == 0.0
    assert arrival.direct == 1.0
    assert math.isclose(propagation_delay_s(distance), 2.0, rel_tol=1e-12)


def test_ringdown_mode_envelope_decays_exponentially():
    mode = DampedMode(amplitude=1.0, frequency_hz=1.0, damping_time_s=2.0)
    cfg = ReverberationConfig(modes=(mode,))
    at_zero = response_at_observer(0.0, cfg)
    at_two = response_at_observer(2.0, cfg)

    assert math.isclose(at_zero.ringdown, 1.0, rel_tol=1e-12)
    assert math.isclose(at_two.ringdown, math.exp(-1.0), rel_tol=1e-12)
    assert math.isclose(mode.quality_factor, 2.0 * math.pi, rel_tol=1e-12)


def test_tail_decays_and_memory_approaches_persistent_offset():
    cfg = ReverberationConfig(
        tail_amplitude=1.0,
        tail_scale_s=2.0,
        tail_power=2.0,
        memory_delta=0.25,
        memory_rise_s=1.0,
    )
    early = response_at_observer(0.0, cfg)
    late = response_at_observer(20.0, cfg)

    assert late.tail < early.tail
    assert late.memory > early.memory
    assert math.isclose(late.memory, 0.25, rel_tol=1e-8)


def test_summary_keeps_energy_bridge_token_vazio():
    cfg = ReverberationConfig(
        direct_amplitude=1.0,
        modes=(DampedMode(0.5, 5.0, 0.2),),
        memory_delta=0.1,
    )
    samples = sample_response(cfg, [0.0, 0.1, 0.2, 1.0])
    summary = response_summary(samples, cfg)

    assert summary["samples"] == 4
    assert summary["claim_allowed"] is False
    assert summary["energy_mapping"] == "TOKEN_VAZIO"
    assert summary["peak_abs_total"] >= 0.0


def test_superluminal_propagation_is_rejected():
    try:
        propagation_delay_s(1.0, C_M_S * 1.0001)
    except ValueError as exc:
        assert "propagation speed" in str(exc)
    else:
        raise AssertionError("superluminal propagation must fail closed")
