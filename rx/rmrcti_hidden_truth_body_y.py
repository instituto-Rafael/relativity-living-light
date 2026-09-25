"""Synthetic hidden-truth Body-Y benchmark for the RLL geometry router.

Deterministic, dimensionless weak-field toy benchmark. It tests
routing/reconstruction and numerical adaptation. It is not an astrophysical
fit and cannot promote a physical or cosmological claim.
"""
from __future__ import annotations
import math
import random
from typing import Iterable

CLAIM_ALLOWED = False
C_DYN = 50.0
SOFTENING = 0.25
TRUTH_DT = 0.002
ROUTER_DT = 0.08
NOISE_SIGMA = 0.006
SEEDS = (17, 23, 42, 633, 144000)
ARRIVAL_TIMES = tuple(0.45 + 0.20 * i for i in range(15))
OBSERVER = (8.0, 2.0)

TRUTH_MODEL = {
    "mu": 0.08,
    "state0": (-1.4, 0.65, 0.9, -0.04),
    "events": ((1.0, 0.10, -0.12), (1.9, -0.05, 0.09)),
}
CANDIDATES = {
    "truth": TRUTH_MODEL,
    "no_event": {"mu": 0.08, "state0": TRUTH_MODEL["state0"], "events": ()},
    "wrong_event_order": {"mu": 0.08, "state0": TRUTH_MODEL["state0"],
        "events": ((1.0, -0.05, 0.09), (1.9, 0.10, -0.12))},
    "wrong_geometry": {"mu": 0.0, "state0": TRUTH_MODEL["state0"],
        "events": TRUTH_MODEL["events"]},
    "wrong_impulse_sign": {"mu": 0.08, "state0": TRUTH_MODEL["state0"],
        "events": ((1.0, -0.10, 0.12), (1.9, 0.05, -0.09))},
}

def _acceleration(x, y, mu):
    r2 = x*x + y*y + SOFTENING*SOFTENING
    fac = -float(mu)/(r2**1.5)
    return fac*x, fac*y

def _rk4(state, h, mu):
    def deriv(s):
        x,y,vx,vy=s
        ax,ay=_acceleration(x,y,mu)
        return vx,vy,ax,ay
    k1=deriv(state)
    s2=tuple(state[i]+0.5*h*k1[i] for i in range(4)); k2=deriv(s2)
    s3=tuple(state[i]+0.5*h*k2[i] for i in range(4)); k3=deriv(s3)
    s4=tuple(state[i]+h*k3[i] for i in range(4)); k4=deriv(s4)
    return tuple(state[i]+h*(k1[i]+2*k2[i]+2*k3[i]+k4[i])/6.0 for i in range(4))

def _curve_geometry(state, mu):
    x,y,vx,vy=state
    ax,ay=_acceleration(x,y,mu)
    speed=math.hypot(vx,vy)
    curvature=0.0 if speed<=1e-15 else abs(vx*ay-vy*ax)/speed**3
    return {"speed":speed,"curvature":curvature,"acceleration":(ax,ay)}

def _subdivision_for_geometry(state, mu):
    kappa=_curve_geometry(state,mu)["curvature"]
    score=min(1.0,8.0*kappa)
    return 1+int(math.floor(7.0*score+1e-12))

def propagate(model, dt, adaptive, t_end=3.4):
    mu=float(model["mu"]); events=tuple(sorted(model.get("events",())))
    state=tuple(float(v) for v in model["state0"]); t=0.0
    trajectory=[(t,state)]; event_index=0; rk4_steps=0; max_subdivision=1
    def integrate_to(target,t,state):
        nonlocal rk4_steps,max_subdivision
        while t<target-1e-14:
            H=min(dt,target-t)
            sub=_subdivision_for_geometry(state,mu) if adaptive else 1
            max_subdivision=max(max_subdivision,sub); hh=H/sub
            for _ in range(sub):
                state=_rk4(state,hh,mu); t+=hh; rk4_steps+=1
            trajectory.append((t,state))
        return t,state
    while t<t_end-1e-14:
        next_t=min(t+dt,t_end)
        while event_index<len(events) and events[event_index][0]<=next_t+1e-14:
            event_t,dvx,dvy=events[event_index]
            if event_t>t+1e-14: t,state=integrate_to(event_t,t,state)
            x,y,vx,vy=state; state=(x,y,vx+float(dvx),vy+float(dvy))
            trajectory.append((t,state)); event_index+=1
        if t<next_t-1e-14: t,state=integrate_to(next_t,t,state)
    return {"trajectory":trajectory,"rk4_steps":rk4_steps,
        "max_subdivision":max_subdivision,"adaptive":bool(adaptive),"dt":float(dt)}

def _sample(trajectory,t):
    if t<=trajectory[0][0]: return trajectory[0][1]
    if t>=trajectory[-1][0]: return trajectory[-1][1]
    lo,hi=0,len(trajectory)-1
    while hi-lo>1:
        mid=(lo+hi)//2
        if trajectory[mid][0]<=t: lo=mid
        else: hi=mid
    t0,s0=trajectory[lo]; t1,s1=trajectory[hi]
    if abs(t1-t0)<=1e-15: return s1
    w=(t-t0)/(t1-t0)
    return tuple(s0[i]*(1-w)+s1[i]*w for i in range(4))

def retarded_observation(trajectory,arrival_time):
    t_emit=float(arrival_time)
    for _ in range(16):
        state=_sample(trajectory,max(0.0,t_emit))
        distance=math.hypot(state[0]-OBSERVER[0],state[1]-OBSERVER[1])
        updated=max(0.0,float(arrival_time)-distance/C_DYN)
        if abs(updated-t_emit)<1e-13:
            t_emit=updated; break
        t_emit=updated
    state=_sample(trajectory,t_emit)
    return {"arrival_time":float(arrival_time),"emission_time":t_emit,
        "xy_relative":(state[0]-OBSERVER[0],state[1]-OBSERVER[1])}

def _position_rmse(candidate,reference):
    sq=[]
    for t in ARRIVAL_TIMES:
        a=retarded_observation(candidate,t)["xy_relative"]
        b=retarded_observation(reference,t)["xy_relative"]
        sq.append((a[0]-b[0])**2+(a[1]-b[1])**2)
    return math.sqrt(sum(sq)/len(sq))

def _synthetic_observations(reference,seed):
    rng=random.Random(int(seed)); rows=[]
    for t in ARRIVAL_TIMES:
        obs=retarded_observation(reference,t); x,y=obs["xy_relative"]
        rows.append({"arrival_time":t,"x":x+rng.gauss(0,NOISE_SIGMA),
            "y":y+rng.gauss(0,NOISE_SIGMA),"sigma_x":NOISE_SIGMA,
            "sigma_y":NOISE_SIGMA,"cov_xy":0.0})
    return rows

def _g6_mahalanobis_tournament(observations:Iterable[dict],trajectories):
    scores={}; residual_rows={}
    for name,payload in trajectories.items():
        total=0.0; rows=[]; trajectory=payload["trajectory"]
        for row in observations:
            pred=retarded_observation(trajectory,row["arrival_time"])["xy_relative"]
            dx=row["x"]-pred[0]; dy=row["y"]-pred[1]
            d2=(dx/row["sigma_x"])**2+(dy/row["sigma_y"])**2
            total+=d2; rows.append({"arrival_time":row["arrival_time"],"d2":d2})
        scores[name]=total; residual_rows[name]=rows
    order=sorted(scores,key=lambda name:(scores[name],name))
    return {"scores":scores,"order":order,"residuals":residual_rows}

def _delta_p_diagnostic(residuals):
    d2s=[float(r["d2"]) for r in residuals]; ordered=sorted(d2s)
    peak_threshold=ordered[(3*len(ordered))//4]
    stable_threshold=5.991464547107979
    peak=[d<=stable_threshold for d in d2s if d>=peak_threshold]
    nonpeak=[d<=stable_threshold for d in d2s if d<peak_threshold]
    p_peak=sum(peak)/len(peak) if peak else 0.0
    p_nonpeak=sum(nonpeak)/len(nonpeak) if nonpeak else 0.0
    return {"formula":"P(stable=1|peak)-P(stable=1|nonpeak)",
        "peak_definition":"top_quartile_of_predeclared_G6_d2_sequence",
        "stable_definition":"G6_d2<=5.991464547107979",
        "p_stable_peak":p_peak,"p_stable_nonpeak":p_nonpeak,
        "delta_p_op":p_peak-p_nonpeak,"physical_parameter":False}

def _weak_field_gate(reference):
    max_epsilon=0.0; max_beta=0.0; min_radius=math.inf
    mu=float(TRUTH_MODEL["mu"])
    for _,state in reference:
        x,y,vx,vy=state; r=math.hypot(x,y)
        min_radius=min(min_radius,r)
        max_epsilon=max(max_epsilon,mu/(max(r,1e-15)*C_DYN*C_DYN))
        max_beta=max(max_beta,math.hypot(vx,vy)/C_DYN)
    return {"max_GM_over_rc2_proxy":max_epsilon,"max_v_over_c":max_beta,
        "min_radius":min_radius,"declared_tolerance":1e-3,
        "pass":max_epsilon<1e-3 and max_beta<0.05,"strong_field_branch":False}

def run_benchmark():
    reference_payload=propagate(TRUTH_MODEL,TRUTH_DT,False)
    reference=reference_payload["trajectory"]
    fixed_payload=propagate(TRUTH_MODEL,ROUTER_DT,False)
    adaptive_payload=propagate(TRUTH_MODEL,ROUTER_DT,True)
    fixed_rmse=_position_rmse(fixed_payload["trajectory"],reference)
    adaptive_rmse=_position_rmse(adaptive_payload["trajectory"],reference)
    candidate_trajectories={name:propagate(model,ROUTER_DT,True)
        for name,model in CANDIDATES.items()}
    seed_results=[]; recoveries=0; delta_p=[]
    for seed in SEEDS:
        observations=_synthetic_observations(reference,seed)
        tournament=_g6_mahalanobis_tournament(observations,candidate_trajectories)
        recovered=tournament["order"][0]=="truth"; recoveries+=int(recovered)
        diag=_delta_p_diagnostic(tournament["residuals"]["truth"])
        delta_p.append(diag["delta_p_op"])
        seed_results.append({"seed":seed,"winner":tournament["order"][0],
            "truth_recovered":recovered,"order":tournament["order"],
            "scores":tournament["scores"],"truth_delta_p_diagnostic":diag})
    gate=_weak_field_gate(reference)
    return {
        "schema":"rll.rmrcti_hidden_truth_body_y.v1",
        "dataset_type":"synthetic_hidden_truth","claim_allowed":False,
        "physics_scope":"dimensionless weak-field toy benchmark; not an astrophysical fit",
        "hidden_truth":{"scenario":"two_impulse_weak_field_chain",
            "candidate_names":list(CANDIDATES),"candidate_parameters_frozen_before_noise":True},
        "retarded_observation":{"observer":list(OBSERVER),"signal_speed":C_DYN,
            "arrival_count":len(ARRIVAL_TIMES),"iterative_emission_time":True},
        "weak_field_gate":gate,
        "adaptive_numerics":{"fixed_dt":ROUTER_DT,"truth_reference_dt":TRUTH_DT,
            "fixed_position_rmse":fixed_rmse,"adaptive_position_rmse":adaptive_rmse,
            "adaptive_not_worse":adaptive_rmse<=fixed_rmse,
            "fixed_rk4_steps":fixed_payload["rk4_steps"],
            "adaptive_rk4_steps":adaptive_payload["rk4_steps"],
            "adaptive_max_subdivision":adaptive_payload["max_subdivision"],
            "physical_parameters_changed":False},
        "g6_preregistered_primary":{"feature":"retarded_xy_Mahalanobis2",
            "covariance":"diagonal_sigma_0.006_squared",
            "decision":"minimum_total_d2_over_frozen_scenarios",
            "multiple_testing_policy":"no_p_value_claim; any future feature family significance requires Holm correction"},
        "seed_results":seed_results,
        "hidden_truth_recovery":{"recovered":recoveries,"total":len(SEEDS),
            "rate":recoveries/len(SEEDS),"pass":recoveries==len(SEEDS)},
        "rmrcti_adapter":{"delta_p_op_values":delta_p,
            "mean_delta_p_op":sum(delta_p)/len(delta_p),
            "omega_persistence_recovery_fraction":recoveries/len(SEEDS),
            "delta_p_target_0_18_fitted":False,
            "allowed_use":"routing/stability diagnostic only"},
        "controls":{"no_event":True,"wrong_event_order":True,"wrong_geometry":True,
            "wrong_impulse_sign":True,"held_out_noise_seeds":list(SEEDS)},
        "state":"PASS_SYNTHETIC_HIDDEN_TRUTH" if recoveries==len(SEEDS) and gate["pass"]
            else "FAIL_SYNTHETIC_HIDDEN_TRUTH",
    }
