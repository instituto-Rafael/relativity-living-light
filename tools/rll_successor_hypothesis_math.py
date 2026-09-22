#!/usr/bin/env python3
"""Deterministic mathematics for the append-only RLL successor-hypothesis intake.

This module closes only algebraic/identifiability gaps. It does not evaluate
observational support and it never promotes a scientific claim.
"""

from __future__ import annotations

import math

S_RLL = math.sqrt(3.0) / 2.0
A_CROSS = S_RLL * S_RLL  # exactly 3/4


def h03_w_eff(z: float) -> float:
    """Effective separately-conserved EoS for rho_DE(z)/rho_DE0 = S_RLL**z.

    From d ln rho / dz = 3(1+w)/(1+z),
    w(z) = -1 + (1+z) ln(S_RLL)/3.
    """
    z = float(z)
    if z <= -1.0:
        raise ValueError("h03_w_eff requires z > -1")
    return -1.0 + (1.0 + z) * math.log(S_RLL) / 3.0


def h03_dw_dz() -> float:
    """Constant slope of the H03 effective equation of state."""
    return math.log(S_RLL) / 3.0


def h51_w(a: float, amplitude: float) -> float:
    """Successor fixed-crossing hypothesis: w(a)=-1+A(a-3/4)."""
    return -1.0 + float(amplitude) * (float(a) - A_CROSS)


def h51_to_cpl(amplitude: float) -> tuple[float, float]:
    """Return the exactly equivalent CPL pair (w0, wa)."""
    amplitude = float(amplitude)
    return -1.0 + amplitude / 4.0, -amplitude


def h51_cpl_constraint_residual(w0: float, wa: float) -> float:
    """Zero iff the CPL pair lies on H51: wa = -4(w0+1)."""
    return float(wa) + 4.0 * (float(w0) + 1.0)


def logistic_transition(z: float, zt: float, wt: float) -> float:
    """RLL logistic transition used only for the null-identifiability check."""
    if float(wt) <= 0.0:
        raise ValueError("wt must be > 0")
    x = max(-500.0, min(500.0, (float(z) - float(zt)) / float(wt)))
    return 1.0 / (1.0 + math.exp(x))


def rll_superposition_term(z: float, os0: float, zt: float, wt: float) -> float:
    """RLL superposition contribution in E^2, excluding background terms."""
    fz = logistic_transition(z, zt, wt)
    return float(os0) * (fz + (1.0 - fz) * (1.0 + float(z)) ** 3)


def rll_null_shape_identifiable(os0: float) -> bool:
    """At Os0=0, zt and wt vanish from E^2 and are not identifiable."""
    return float(os0) != 0.0


if __name__ == "__main__":
    w0_h03 = h03_w_eff(0.0)
    w0, wa = h51_to_cpl(1.0)
    print(f"S_RLL={S_RLL:.16g}")
    print(f"S_RLL^2={A_CROSS:.16g}")
    print(f"H03_w(z=0)={w0_h03:.16g}")
    print(f"H03_dw_dz={h03_dw_dz():.16g}")
    print(f"H51_A1=(w0={w0:.16g}, wa={wa:.16g})")
    print("claim_allowed=false")
