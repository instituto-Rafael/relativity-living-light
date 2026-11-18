#!/usr/bin/env python3
"""G4 RLL effective local CPL slope: background diagnostic only, not a fluid theory.

The formula is the separately-conserved effective *dark-sector decomposition*
of the exact G4 RLL E², NOT the documented separate pressure and not a growth,
CMB, NEC or physical dark-energy detection claim. claim_allowed=False.
"""
from __future__ import annotations
import argparse
import json
import math
from tools import run_g4_background_tournament as g4


def effective_cpl_tangent(omega_m, omega_s0, z_t, w_t):
    om, s, zt, wt = map(float, (omega_m,omega_s0,z_t,w_t))
    r = float(g4.OMEGA_R0)
    if not all(math.isfinite(v) for v in (om,s,zt,wt,r)):
        raise ValueError('all parameter inputs must be finite')
    if not (0 < om < 1 and 0 <= s < 1 and zt > 0 and wt > 0):
        raise ValueError('unsupported parameter domain')
    lam = 1.0 - om - r - s
    G = lam + s
    if lam < 0 or G <= 0:
        raise ValueError('negative constant dark sector or zero total dark density')
    q = zt/wt
    # u0 = 1 - f0, evaluated without 1 - rounded-to-one cancellation.
    if q >= 0:
        small = math.exp(-q)
        u0 = small/(1.0+small)
    else:
        large = math.exp(q)
        u0 = 1.0/(1.0+large)
    f0 = 1.0-u0
    w0 = -1.0 + s*u0/G
    wa = s*u0/G**2 * (2.0*f0*G/wt + 3.0*(lam+s*f0))
    if not all(math.isfinite(x) for x in (w0,wa)):
        raise ValueError('nonfinite local slope')
    if wa < -1e-12 or w0 < -1.0-1e-12:
        raise ValueError('analytic positivity contradiction')
    return {
        'model':'RLL_G4',
        'closure':'SEPARATELY_CONSERVED_EFFECTIVE_DARK_SECTOR_ASSUMPTION',
        'omega_lambda':lam,
        'f0':f0,
        'one_minus_f0':u0,
        'w0_eff':w0,
        'wa_eff_local_tangent':wa,
        'wa_local_nonnegative_under_assumptions':bool(wa>=0),
        'observational_wa_posterior':'TOKEN_VAZIO_NOT_FITTED_TO_MATCHED_CMB_SN_BAO',
        'perturbation_closure':'TOKEN_VAZIO_NOT_DERIVED',
        'fluid_stability':'NOT_TESTED',
        'growth_predictions':'NOT_TESTED',
        'NEC_physical_claim':'NOT_TESTED',
        'claim_allowed':False,
        'status':'BACKGROUND_ANALYTIC_ONLY',
    }


def main():
    parser=argparse.ArgumentParser()
    parser.add_argument('--omega-m',type=float,required=True)
    parser.add_argument('--omega-s0',type=float,required=True)
    parser.add_argument('--z-t',type=float,required=True)
    parser.add_argument('--w-t',type=float,required=True)
    args=parser.parse_args()
    report=effective_cpl_tangent(args.omega_m,args.omega_s0,args.z_t,args.w_t)
    print(json.dumps(report,sort_keys=True,indent=2))


if __name__=='__main__':
    main()
