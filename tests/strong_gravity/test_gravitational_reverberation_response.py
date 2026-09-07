import math
from data.pipelines.strong_gravity.gravitational_reverberation_response import C_M_S,DampedMode,ReverberationConfig,propagation_delay_s,response_at_observer,response_summary,sample_response

def test_pre_event_response_is_zero():
    cfg=ReverberationConfig(event_time_s=1.0,direct_amplitude=2.0,modes=(DampedMode(1.0,10.0,0.5),),tail_amplitude=0.2,memory_delta=0.1)
    s=response_at_observer(0.5,cfg)
    assert s.total==s.direct==s.ringdown==s.tail==s.memory==0.0

def test_retarded_response_respects_light_speed_bound():
    distance=C_M_S*2.0; cfg=ReverberationConfig(direct_amplitude=1.0)
    assert response_at_observer(1.999,cfg,distance_m=distance).total==0.0
    assert response_at_observer(2.0,cfg,distance_m=distance).direct==1.0
    assert math.isclose(propagation_delay_s(distance),2.0,rel_tol=1e-12)

def test_ringdown_envelope_decays_exponentially():
    mode=DampedMode(1.0,1.0,2.0); cfg=ReverberationConfig(modes=(mode,))
    assert math.isclose(response_at_observer(0,cfg).ringdown,1.0,rel_tol=1e-12)
    assert math.isclose(response_at_observer(2,cfg).ringdown,math.exp(-1),rel_tol=1e-12)
    assert math.isclose(mode.quality_factor,2*math.pi,rel_tol=1e-12)

def test_tail_decays_and_memory_approaches_offset():
    cfg=ReverberationConfig(tail_amplitude=1.0,tail_scale_s=2.0,tail_power=2.0,memory_delta=0.25,memory_rise_s=1.0)
    early=response_at_observer(0,cfg); late=response_at_observer(20,cfg)
    assert late.tail<early.tail and late.memory>early.memory
    assert math.isclose(late.memory,0.25,rel_tol=1e-8)

def test_summary_keeps_energy_bridge_token_vazio():
    cfg=ReverberationConfig(direct_amplitude=1.0,modes=(DampedMode(0.5,5.0,0.2),),memory_delta=0.1)
    summary=response_summary(sample_response(cfg,[0,0.1,0.2,1.0]),cfg)
    assert summary["samples"]==4 and summary["claim_allowed"] is False
    assert summary["energy_mapping"]=="TOKEN_VAZIO"

def test_superluminal_propagation_is_rejected():
    try: propagation_delay_s(1.0,C_M_S*1.0001)
    except ValueError as exc: assert "propagation speed" in str(exc)
    else: raise AssertionError("superluminal propagation must fail closed")
