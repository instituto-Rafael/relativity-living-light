#!/usr/bin/env python3
"""Finalize the versioned RX-PHYSICS-CANONICAL-V2 background contract.

This is a background-semantics gate only. It explicitly does not close RLL
perturbations, physical growth, CLASS/CAMB, multiprobe evidence, or claims.
"""
from __future__ import annotations
import argparse, hashlib, json, sys
from pathlib import Path
from typing import Any

ROOT=Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path: sys.path.insert(0,str(ROOT))

from tools.rx_physics_v2_decision_packet import build as build_packet

AUTH=ROOT/"data/governance/RLL_RX_PHYSICS_V2_DECISION_AUTHORITY_V1.json"
CONFIG=ROOT/"configs/rx_physics_contracts.json"
CONV=ROOT/"data/governance/RLL_RX_PHYSICS_CONVERGENCE_V1.json"
OUT=ROOT/"provenance/receipts/RLL_RX_PHYSICS_CANONICAL_V2_BACKGROUND_RECEIPT.json"

def load(path:Path)->dict[str,Any]:
 v=json.loads(path.read_text(encoding="utf-8"))
 if not isinstance(v,dict): raise ValueError(f"{path}: object required")
 return v

def sha(path:Path)->str:
 return hashlib.sha256(path.read_bytes()).hexdigest()

def build()->dict[str,Any]:
 auth=load(AUTH); cfg=load(CONFIG); conv=load(CONV); packet=build_packet()
 target=cfg["contracts"]["RX-PHYSICS-CANONICAL-V2"]
 errors=[]
 if auth.get("claim_allowed") is not False or target.get("claim_allowed") is not False or conv.get("claim_allowed") is not False:
  errors.append("claim_allowed drift")
 if packet.get("blocking_axes") != []:
  errors.append("background decision blockers remain: "+",".join(packet.get("blocking_axes",[])))
 if packet.get("state")!="READY_CANONICAL_V2_BACKGROUND_FINALIZATION":
  errors.append("decision packet not ready for finalization")
 expected={
  "omega_r":"derived_standard_relativistic_radiation",
  "hz_dataset":"data/real/cosmology/Hz_cosmic_chronometers_independent.csv",
  "growth_mode":"EXCLUDED_FROM_BACKGROUND_UNTIL_WS06",
  "bao_sound_horizon":"sound_horizon_integral_required",
  "cmb_acoustic_mode":"rs_star_required",
  "distance_integration":"log1p_simpson",
 }
 for k,v in expected.items():
  if target.get(k)!=v: errors.append(f"target {k} mismatch: {target.get(k)!r}")
 gates=conv.get("gates",{})
 required_gate_states={
  "omega_r":"PASS_DERIVED_STANDARD_RADIATION_AUTHORITY",
  "hz_dataset":"PASS_EVIDENCE_TERMINAL",
  "growth_mode":"PASS_BACKGROUND_BOUNDARY_FROZEN_WAIT_WS06",
  "distance_integration":"PASS_PREREGISTERED_TOLERANCE",
 }
 for k,v in required_gate_states.items():
  if gates.get(k,{}).get("status")!=v: errors.append(f"{k} evidence gate != {v}")
 if target.get("activation_policy")!="NOT_ACTIVE_UNTIL_EXPLICIT_EXECUTION_PLAN_SELECTS_VERSIONED_CONTRACT":
  errors.append("activation must remain explicit")
 if cfg.get("active_contract")=="RX-PHYSICS-CANONICAL-V2":
  errors.append("finalizer must not silently activate canonical V2")
 growth_auth=next(x for x in auth["axes"] if x["id"]=="growth_mode")
 if growth_auth.get("selected_option")!="perturbation_backend_fsigma8":
  errors.append("growth boundary must point to perturbation backend")
 if growth_auth.get("decision_evidence",{}).get("promoted_proxy") is not None:
  errors.append("engineering growth proxy promoted")
 omega_auth=next(x for x in auth["axes"] if x["id"]=="omega_r")
 if omega_auth.get("decision_evidence",{}).get("legacy_fixed_values_promoted") is not False:
  errors.append("legacy fixed Omega_r promoted")
 passed=not errors
 return {
  "schema":"rll.rx.physics_canonical_v2_background_receipt.v1",
  "state":"PASS_VERSIONED_CANONICAL_V2_BACKGROUND_CONTRACT" if passed else "BLOCKED_CANONICAL_V2_BACKGROUND_CONTRACT",
  "claim_allowed":False,
  "scientific_confirmation":False,
  "publication_ready":False,
  "passed":passed,
  "errors":errors,
  "target_contract":"RX-PHYSICS-CANONICAL-V2",
  "target_state_before_receipt":target.get("state"),
  "active_contract_unchanged":cfg.get("active_contract"),
  "selected_background_semantics":expected,
  "evidence_states":required_gate_states,
  "authority_sha256":sha(AUTH),
  "config_sha256":sha(CONFIG),
  "convergence_sha256":sha(CONV),
  "decision_packet_state":packet.get("state"),
  "decision_packet_blocking_axes":packet.get("blocking_axes"),
  "resolved_ws01_decision_tokens":[
    "TOKEN_VAZIO_DECISION:omega_r",
    "TOKEN_VAZIO_DECISION:hz_dataset",
    "TOKEN_VAZIO_DECISION:growth_mode",
    "TOKEN_VAZIO_TOLERANCE_CONTRACT:distance_integration"
  ] if passed else [],
  "downstream_tokens_preserved":[
    "TOKEN_VAZIO_RLL_PERTURBATION_CLOSURE_RELATIONS",
    "TOKEN_VAZIO_RLL_CLASS_CAMB_IMPLEMENTATION",
    "OGB-FS8-001:BLOCKED_UNTIL_PERTURBATION_BACKEND",
    "TOKEN_VAZIO_INDEPENDENT_REPLICATION"
  ],
  "F_next":"WS03: derive/freeze gauge-consistent perturbation closure, especially C07 initial conditions and C08 regular representation; only then hand off independently to CLASS and CAMB.",
  "boundary":"PASS closes only the WS01 versioned background-semantics decision layer. It does not activate the contract automatically, validate RLL physics, provide perturbation-derived growth, close CLASS/CAMB, or permit a scientific claim."
 }

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--output",type=Path,default=OUT);ap.add_argument("--require-pass",action="store_true");args=ap.parse_args()
 r=build(); out=args.output if args.output.is_absolute() else ROOT/args.output
 out.parent.mkdir(parents=True,exist_ok=True)
 out.write_text(json.dumps(r,indent=2,ensure_ascii=False,allow_nan=False)+"\n",encoding="utf-8")
 print(json.dumps({"state":r["state"],"errors":r["errors"],"decision_packet_blocking_axes":r["decision_packet_blocking_axes"],"claim_allowed":False},sort_keys=True))
 return 0 if (r["passed"] or not args.require_pass) else 2
if __name__=="__main__":raise SystemExit(main())
