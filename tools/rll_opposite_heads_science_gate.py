#!/usr/bin/env python3
"""Small deterministic counterexample gates; synthetic, not transformer weights/real spin lab."""
import json
import math
import argparse

H_MHZ=1420.40575177
PLANCK=6.62607015e-34

def dot(a,b):
    return sum(x*y for x,y in zip(a,b))

def check():
    outcomes=[]
    def verify(name,condition,description):
        outcomes.append({'id':name,'pass':bool(condition),'meaning':description})
    h=[2.,-1.]
    w=[3.,4.]
    before=dot(h,w)
    permuted=dot(h[::-1],w[::-1])
    unpaired=dot(h[::-1],w)
    verify('P01',before == permuted, 'Simultaneous head-output and W_O block permutation preserves output')
    verify('P02',unpaired!=before, 'Permuting output heads alone is not a symmetry')
    a=[.7,.2,.1]
    complement=[1-v for v in a]
    verify('P03',math.isclose(sum(a),1.) and math.isclose(sum(complement),2.), '1 minus A is not a probability simplex for three attended tokens')
    verify('P04',math.isclose(sum(v/2. for v in complement),1.), 'Complement can be renormalized but is not a unique causal inverse head')
    # Synthetic binary classification with label=0, positive logit for incorrect class=1.
    def wrong_class_logloss(logit):
        return math.log1p(math.exp(logit))
    verify('P05',wrong_class_logloss(2.-1.) < wrong_class_logloss(2.), 'Negative suppressor can reduce loss on a synthetic target-0 case')
    def interacting(g1,g2): return g1+g2+3*g1*g2
    full=interacting(1,1)
    two_single_drops=2*(full-interacting(0,1))
    verify('P06',two_single_drops != full-interacting(0,0), 'Single-head ablation effects do not add in nonlinear circuits')
    energy=PLANCK*H_MHZ*1e6
    verify('P07',5.8e-6 < energy/1.602176634e-19 < 6.0e-6, 'HI 21cm hyperfine energy reference in eV (not a laboratory run)')
    verify('P08',(2*0+1)==1 and (2*1+1)==3, 'Hydrogen hyperfine F=0 singlet and F=1 triplet degeneracies')
    h_left=2+2
    h_right=3+1
    charge_left=1+0
    charge_right=1+0
    verify('P09',h_left==h_right and charge_left==charge_right, 'H2+ + H2 -> H3+ + H conserves H nuclei and charge')
    xs=[1.,2.,3.]
    def var(x):
        mean=sum(x)/len(x)
        return sum((v-mean)**2 for v in x)/len(x)
    verify('P10',var(xs)>0 and var([0.,0.,0.])==0., 'Degenerate all-zero map cannot preserve informative variance')
    verify('P11',not ('He3' == '³He'), 'Textual ambiguity not silently normalized into an isotope')
    verify('P12',not ('C3' == 'C³⁺'), 'Carbon trimer is not triply ionized carbon')
    verify('P13',not ('H2O' == 'H2O3'), 'Water is not trioxidane')
    verify('P14',not ('spin_flip' == 'attention_head_ablation'), 'Physical spin and neural intervention not the same mechanism')
    return {'schema':'rll.opposite_heads_scoped_math.v1','status':'PASS_SYNTHETIC_ONLY' if all(x['pass'] for x in outcomes) else 'FAIL_SCOPED','tests':outcomes, 'n_pass':sum(x['pass'] for x in outcomes),'n_total':len(outcomes),'synthetic_forward':before,'synthetic_co_permuted':permuted,'synthetic_unpaired':unpaired,'hi_hyperfine_eV_reference':energy/1.602176634e-19,'claim_allowed':False,'scientific_fit_executed':False,'hidden_heads_observed':False}

if __name__=='__main__':
    parser=argparse.ArgumentParser()
    parser.add_argument('--self-test',action='store_true')
    args=parser.parse_args()
    receipt=check()
    print(json.dumps(receipt,ensure_ascii=False,sort_keys=True))
    raise SystemExit(0 if receipt['status']=='PASS_SYNTHETIC_ONLY' else 2)
