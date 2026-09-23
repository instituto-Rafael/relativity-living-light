"""Rx sound-horizon mechanics.

Stdlib-only port of the existing FASE18E sound-horizon contract.
This module is additive and does not change the active Rx Structure-D parity
contract.

Methods/formulas retain their established scientific provenance.
"""

from __future__ import annotations

import math

from .cosmology import C_KMS, unpack

OMEGA_GAMMA_H2 = 2.47e-5
Z_STAR_DEFAULT = 1089.92
Z_HIGH_DEFAULT = 5.0e5
RS_STAR_CALIB_FASE18E_MPC = 0.1988165052796944


def z_drag_eh98(omega_m_h2, omega_b_h2):
    omh2 = float(omega_m_h2)
    obh2 = float(omega_b_h2)
    b1 = 0.313 * omh2 ** (-0.419) * (1.0 + 0.607 * omh2 ** 0.674)
    b2 = 0.238 * omh2 ** 0.223
    return (
        1291.0
        * omh2 ** 0.251
        / (1.0 + 0.659 * omh2 ** 0.828)
        * (1.0 + b1 * obh2 ** b2)
    )


def e2_with_omega_r(model, z, vector, omega_r):
    p = unpack(model, vector)
    zp1 = 1.0 + float(z)
    os0 = p["Os0"] if model == "RLL" else 0.0
    ol = 1.0 - p["Om"] - float(omega_r) - os0
    matter = p["Om"] * zp1 ** 3
    radiation = float(omega_r) * zp1 ** 4

    if model == "LCDM":
        dark = ol
    elif model == "wCDM":
        dark = ol * zp1 ** (3.0 * (1.0 + p["w"]))
    elif model == "CPL":
        dark = (
            ol
            * zp1 ** (3.0 * (1.0 + p["w0"] + p["wa"]))
            * math.exp(-3.0 * p["wa"] * float(z) / zp1)
        )
    elif model == "RLL":
        width = max(p["wt"], 1.0e-12)
        arg = max(-500.0, min(500.0, (float(z) - p["zt"]) / width))
        fz = 1.0 / (1.0 + math.exp(arg))
        dark = ol + p["Os0"] * (fz + (1.0 - fz) * zp1 ** 3)
    else:
        raise ValueError("unknown model: %s" % model)
    return matter + radiation + dark


def sound_speed_kms(model, z, vector, omega_gamma_h2=OMEGA_GAMMA_H2):
    p = unpack(model, vector)
    h = p["H0"] / 100.0
    omega_b = p["Ob_h2"] / (h * h)
    omega_gamma = float(omega_gamma_h2) / (h * h)
    rb = (3.0 * omega_b) / (4.0 * omega_gamma) / (1.0 + float(z))
    return C_KMS / math.sqrt(3.0 * (1.0 + rb))


def _cs_over_h(model, z, vector, omega_r, omega_gamma_h2):
    p = unpack(model, vector)
    e2 = e2_with_omega_r(model, z, vector, omega_r)
    if e2 <= 0.0:
        return float("nan")
    hz = p["H0"] * math.sqrt(e2)
    return sound_speed_kms(model, z, vector, omega_gamma_h2) / hz


def _log_trapezoid_integral(
    model,
    z0,
    z1,
    vector,
    omega_r,
    omega_gamma_h2,
    steps,
):
    z0 = max(float(z0), 1.0)
    z1 = max(float(z1), z0)
    n = max(32, int(steps))
    x0 = math.log(z0)
    x1 = math.log(z1)
    dx = (x1 - x0) / n

    total = 0.0
    prev_z = math.exp(x0)
    prev_f = _cs_over_h(model, prev_z, vector, omega_r, omega_gamma_h2)
    for i in range(1, n + 1):
        z = math.exp(x0 + dx * i)
        value = _cs_over_h(model, z, vector, omega_r, omega_gamma_h2)
        total += 0.5 * (prev_f + value) * (z - prev_z)
        prev_z = z
        prev_f = value
    return total


def sound_horizons(
    model,
    vector,
    omega_r=9.18e-5,
    z_star=Z_STAR_DEFAULT,
    z_high=Z_HIGH_DEFAULT,
    steps=4000,
    omega_gamma_h2=OMEGA_GAMMA_H2,
    rs_star_calib_mpc=RS_STAR_CALIB_FASE18E_MPC,
):
    p = unpack(model, vector)
    h = p["H0"] / 100.0
    om_h2 = p["Om"] * h * h
    ob_h2 = p["Ob_h2"]
    z_drag = z_drag_eh98(om_h2, ob_h2)

    rd_body = _log_trapezoid_integral(
        model, z_drag, z_high, vector, omega_r, omega_gamma_h2, steps
    )
    rs_body = _log_trapezoid_integral(
        model, z_star, z_high, vector, omega_r, omega_gamma_h2, steps
    )

    tail = (
        C_KMS
        / math.sqrt(3.0)
        / (p["H0"] * math.sqrt(max(float(omega_r), 1.0e-30)))
        / (1.0 + float(z_high))
    )

    return {
        "z_drag": z_drag,
        "rd_mpc": rd_body + tail,
        "rs_star_raw_mpc": rs_body + tail,
        "rs_star_mpc": rs_body + tail + float(rs_star_calib_mpc),
        "omega_r": float(omega_r),
        "omega_gamma_h2": float(omega_gamma_h2),
        "z_star": float(z_star),
        "z_high": float(z_high),
        "steps": int(steps),
        "rs_star_calib_mpc": float(rs_star_calib_mpc),
    }
