"""Bound-constrained least-squares diagnostics, not a physical model claim.

The name corner_solution is maintained as a protocol alias for any active bound;
strict_corner means at least two independently active bounds.
"""
from __future__ import annotations
import math
from typing import Sequence
import numpy as np


def boundary_report(result, bounds, names: Sequence[str], n_observed: int, rel_width_tol=1e-8):
    names = tuple(names)
    lo, hi = (np.asarray(a, dtype=float) for a in bounds)
    x = np.asarray(result.x, dtype=float)
    grad = np.asarray(result.grad, dtype=float)
    if x.ndim != 1 or any(v.shape != x.shape for v in (lo, hi, grad)) or len(names) != len(x):
        raise ValueError('boundary vector/name/gradient dimensions mismatch')
    if len(set(names)) != len(names) or not all(isinstance(n, str) and n for n in names):
        raise ValueError('names must be unique and nonempty')
    if not all(np.all(np.isfinite(v)) for v in (lo, hi, x, grad)) or not np.all(lo < hi):
        raise ValueError('nonfinite or invalid bounds/optimizer result')
    if not isinstance(n_observed, int) or n_observed < len(x):
        raise ValueError('observation count must be an integer >= parameter count')
    if not math.isfinite(rel_width_tol) or not (0 < rel_width_tol < 0.1):
        raise ValueError('relative boundary tolerance invalid')
    width = hi-lo
    dlow = (x-lo)/width
    dhigh = (hi-x)/width
    # Small floating-point feasible violations are tolerated only to the
    # declared relative width threshold; large violations are rejected.
    if np.any(dlow < -rel_width_tol) or np.any(dhigh < -rel_width_tol):
        raise ValueError('optimizer position outside declared bounds')
    at_low = dlow <= rel_width_tol
    at_high = dhigh <= rel_width_tol
    if np.any(at_low & at_high):
        raise ValueError('both bounds active: degenerate parameter width/tolerance')
    at = at_low | at_high
    distance=np.minimum(x-lo, hi-x)
    distance=np.maximum(0.0,distance)  # raw distance; never invent exact zero for near-bound values
    kkt=np.where(at_low, np.minimum(grad,0),
                 np.where(at_high,np.maximum(grad,0),grad))
    opt = float(result.optimality)
    if not math.isfinite(opt):
        raise ValueError('solver optimality is not finite')
    m = int(at.sum())
    return {
       'at_boundary':{name:bool(flag) for name,flag in zip(names,at)},
       'bound_distance':{name:float(d) for name,d in zip(names,distance)},
       'normalized_bound_distance':{name:float(max(0.,min(a,b))) for name,a,b in zip(names,dlow,dhigh)},
       'active_side':{name:('LOWER' if a else 'UPPER' if b else 'INTERIOR') for name,a,b in zip(names,at_low,at_high)},
       'corner_solution':bool(m),
       'strict_corner':bool(m>=2),
       'active_bound_count':m,
       'min_grad_inf':float(np.linalg.norm(grad,ord=np.inf)),
       'optimizer_optimality':opt,
       'kkt_violation_inf':float(np.linalg.norm(kkt,ord=np.inf)),
       'n_residual_dof_nominal':n_observed-len(x),
       'n_effective_dof':None,
       'n_effective_dof_status':'TOKEN_VAZIO_NOT_ESTIMATED',
       'claim_allowed':False,
       'claim_blocked_reason':('corner: '+', '.join(n for n,a in zip(names,at) if a)
                               +' at declared bounds; scientific inference pending'
                               if m else 'SCIENTIFIC_VALIDATION_NOT_ESTABLISHED'),
       'status':'BOUNDARY_DIAGNOSTIC_ONLY',
    }


def gate_boundary_claim(report):
    if not isinstance(report,dict) or report.get('claim_allowed') is not False:
        raise ValueError('claim_allowed must remain false')
    if report.get('corner_solution') is True and 'corner' not in str(report.get('claim_blocked_reason','')).lower():
        raise ValueError('corner result needs explicit warning')
    if not isinstance(report.get('at_boundary'),dict) or report.get('corner_solution') != any(report['at_boundary'].values()):
        raise ValueError('corner flag inconsistent with active bounds')
    return True


def format_chi2(chi2, report):
    gate_boundary_claim(report)
    if not math.isfinite(float(chi2)):
        raise ValueError('chi2 must be finite')
    return f'{float(chi2):.4f}' + ('*' if report['corner_solution'] else '')
