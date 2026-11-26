"""Negative-control tests for the BAO boundary audit's independently exported JSON."""
from copy import deepcopy
import json
from pathlib import Path
import pytest
from scipy.optimize import least_squares
import numpy as np

from tools.bao_boundary_gate_v1 import boundary_report
from tools.ci.validate_bao_boundary_receipt_v1 import verify_document

SCHEMA=json.loads((Path(__file__).resolve().parents[1]/
    "schemas/rll_bao_boundary_diagnostics_v1.schema.json").read_text())


def fake_report():
    names={"LCDM":("q_c_over_H0_rd","Omega_m"),
           "wCDM":("q_c_over_H0_rd","Omega_m","w"),
           "RLL":("q_c_over_H0_rd","Omega_m","Omega_s0","z_t","w_t")}
    report={"schema":"rll.bao_only_g4_three_model.v1",
            "state":"BAO_ONLY_EXECUTED","claim_allowed":False,
            "G4_joint_fit":"NOT_RUN","Pantheon_plus":"TOKEN_VAZIO_FULL_COVARIANCE",
            "covariance":"full_13x13_source_order_bound","n_observables":13,
            "data_blobs":{},"models":[],"results":{},
            "rendered_table":{"rows":[],"footnote":"* corner: see boundary_diagnostics"}}
    for model,keys in names.items():
        k=len(keys)
        lo=np.zeros(k);hi=np.ones(k)
        a=np.ones(k)*.4
        if model=="RLL":a[-1]=-.10
        def residual(x):
            return np.asarray(x-a,dtype=float)
        opt=least_squares(residual, np.full(k,.5),bounds=(lo,hi),
                          gtol=1e-13,xtol=1e-13,ftol=1e-13)
        diag=boundary_report(opt,(lo,hi),keys,13)
        chi2=7.803973727991534 if model=="RLL" else 10.1
        display=f"{chi2:.4f}"+("*" if diag["corner_solution"] else "")
        row={"model":model,"N":13,"k":k,"chi2":chi2,
             "AIC":chi2+2*k,"AICc":chi2+2*k+2*k*(k+1)/(13-k-1),
             "BIC":chi2+k,"min_grad_inf":diag["min_grad_inf"],
             "chi2_display":display,"claim_allowed":False,
             "boundary_diagnostics":diag,
             "claim_blocked_reason":diag["claim_blocked_reason"]}
        report["models"].append(row)
        report["results"][model]={"chi2":chi2,"chi2_display":display,
            "min_grad_inf":diag["min_grad_inf"],
            "boundary_diagnostics":diag,
            "claim_allowed":False}
        report["rendered_table"]["rows"].append({"model":model,"chi2":display})
    return report


def test_valid_synthetic_receipt_accepts_only_scoped_contract():
    v=verify_document(fake_report(),SCHEMA)
    assert v["status"]=="PASS_SCOPED_BAO_BOUNDARY_RECEIPT_CONTRACT"
    assert v["claim_allowed"] is False
    assert v["rll_active_sides"]["w_t"]=="LOWER"


@pytest.mark.parametrize("mutation",[
    lambda d:d.update(claim_allowed=True),
    lambda d:d["models"][-1].update(claim_allowed=True),
    lambda d:d["models"][-1].update(chi2_display="7.8040"),
    lambda d:d["results"]["RLL"].update(claim_allowed=True),
    lambda d:d["models"][-1]["boundary_diagnostics"].update(corner_solution=False),
    lambda d:d["models"][-1]["boundary_diagnostics"].update(n_effective_dof=8),
    lambda d:d["models"][-1]["boundary_diagnostics"]["at_boundary"].update(w_t=False),
    lambda d:d["models"][-1].update(min_grad_inf=float("nan")),
    lambda d:d["rendered_table"].update(footnote="No notice"),
])
def test_adversarial_mutations_fail_closed(mutation):
    data=fake_report()
    mutation(data)
    with pytest.raises((ValueError, Exception)):
        verify_document(data,SCHEMA)
