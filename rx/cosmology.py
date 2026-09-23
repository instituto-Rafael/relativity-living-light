"""Rx cosmology kernel.

Project-owned stdlib-only implementation of the cosmology mechanics used by RLL.
The mathematical/statistical methods retain their established academic provenance.
No third-party Python imports.
"""

from __future__ import annotations

import math

from .kernel import quad_form, simpson

C_KMS = 299792.458
ORAD = 9.0e-5
Z_CMB_DEFAULT = 1089.92
MODEL_ORDER = ("LCDM", "wCDM", "CPL", "RLL")

PARAM_NAMES = {
    "LCDM": ("H0", "Om", "Ob_h2", "sigma8"),
    "wCDM": ("H0", "Om", "w", "Ob_h2", "sigma8"),
    "CPL": ("H0", "Om", "w0", "wa", "Ob_h2", "sigma8"),
    "RLL": ("H0", "Om", "Os0", "zt", "wt", "Ob_h2", "sigma8"),
}

BOUNDS = {
    "LCDM": ((60.0, 80.0), (0.10, 0.60), (0.018, 0.026), (0.50, 1.10)),
    "wCDM": ((60.0, 80.0), (0.10, 0.60), (-2.0, -0.3), (0.018, 0.026), (0.50, 1.10)),
    "CPL": ((60.0, 80.0), (0.10, 0.60), (-2.0, -0.3), (-3.0, 3.0), (0.018, 0.026), (0.50, 1.10)),
    "RLL": ((60.0, 80.0), (0.10, 0.60), (0.0, 0.25), (0.1, 10.0), (0.05, 2.0), (0.018, 0.026), (0.50, 1.10)),
}


def unpack(model, vector):
    values = {name: float(value) for name, value in zip(PARAM_NAMES[model], vector)}
    values.setdefault("w", -1.0)
    values.setdefault("w0", -1.0)
    values.setdefault("wa", 0.0)
    values.setdefault("Os0", 0.0)
    values.setdefault("zt", 1.0)
    values.setdefault("wt", 0.3)
    return values


def omega_lambda(model, vector):
    p = unpack(model, vector)
    return 1.0 - ORAD - p["Om"] - (p["Os0"] if model == "RLL" else 0.0)


def transition_f(z, zt, wt):
    width = max(float(wt), 1.0e-12)
    arg = max(-500.0, min(500.0, (float(z) - float(zt)) / width))
    return 1.0 / (1.0 + math.exp(arg))


def e2(model, z, vector):
    p = unpack(model, vector)
    zp1 = 1.0 + float(z)
    ol = omega_lambda(model, vector)
    if ol <= 0.0:
        return -1.0
    matter = p["Om"] * zp1**3
    radiation = ORAD * zp1**4
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
        fz = transition_f(z, p["zt"], p["wt"])
        dark = ol + p["Os0"] * (fz + (1.0 - fz) * zp1**3)
    else:
        raise ValueError("unknown model: %s" % model)
    return matter + radiation + dark


def hubble(model, z, vector):
    value = e2(model, z, vector)
    if value <= 0.0:
        return float("nan")
    return unpack(model, vector)["H0"] * math.sqrt(value)


def rd_drag_mpc(model, vector):
    p = unpack(model, vector)
    om_h2 = p["Om"] * (p["H0"] / 100.0) ** 2
    if om_h2 <= 0.0 or p["Ob_h2"] <= 0.0:
        return float("nan")
    return 147.78 * (om_h2 / 0.1432) ** (-0.255) * (p["Ob_h2"] / 0.02236) ** (-0.134)


def comoving_distance_mpc(model, z, vector, steps=512, integration_mode="log1p"):
    z = float(z)
    if z <= 0.0:
        return 0.0
    p = unpack(model, vector)
    h0 = p["H0"]
    if integration_mode == "direct_z":
        return (C_KMS / h0) * simpson(
            lambda zz: 1.0 / math.sqrt(max(e2(model, zz, vector), 1.0e-300)),
            0.0,
            z,
            steps,
        )
    xmax = math.log1p(z)
    return (C_KMS / h0) * simpson(
        lambda xx: math.exp(xx)
        / math.sqrt(max(e2(model, math.exp(xx) - 1.0, vector), 1.0e-300)),
        0.0,
        xmax,
        steps,
    )


def bao_prediction(model, point, vector, steps=512, integration_mode="log1p", cache=None):
    z = float(point["z_eff"])
    key = (model, z, tuple(float(x) for x in vector), steps, integration_mode)
    if cache is not None and key in cache:
        dm = cache[key]
    else:
        dm = comoving_distance_mpc(model, z, vector, steps=steps, integration_mode=integration_mode)
        if cache is not None:
            cache[key] = dm
    hz = hubble(model, z, vector)
    rd = rd_drag_mpc(model, vector)
    observable = str(point["observable"])
    if observable == "DM_over_rd":
        return dm / rd
    if observable == "DH_over_rd":
        return (C_KMS / hz) / rd
    if observable == "DV_over_rd":
        return (z * C_KMS * dm * dm / hz) ** (1.0 / 3.0) / rd
    raise ValueError("unsupported BAO observable: %s" % observable)


def omega_m_z(model, z, vector):
    p = unpack(model, vector)
    value = e2(model, z, vector)
    if value <= 0.0:
        return float("nan")
    return p["Om"] * (1.0 + float(z)) ** 3 / value


def growth_factor(model, z, vector, gamma=0.55, steps=256):
    z = float(z)
    if z <= 0.0:
        return 1.0
    xmax = math.log1p(z)
    integral = simpson(
        lambda xx: max(
            omega_m_z(model, math.exp(xx) - 1.0, vector),
            1.0e-300,
        ) ** gamma,
        0.0,
        xmax,
        steps,
    )
    return math.exp(-integral)


def fsigma8_prediction(model, z, vector, mode="structure_d_proxy", gamma=0.55, steps=256):
    p = unpack(model, vector)
    f = max(omega_m_z(model, z, vector), 1.0e-300) ** gamma
    if mode == "structure_d_proxy":
        return p["sigma8"] * f
    if mode == "freestanding_growth":
        return p["sigma8"] * f * growth_factor(model, z, vector, gamma=gamma, steps=steps)
    raise ValueError("unknown growth mode: %s" % mode)


def cmb_prediction(
    model,
    vector,
    z_cmb=Z_CMB_DEFAULT,
    steps=1024,
    acoustic_mode="structure_d_rd",
    rs_star_mpc=None,
):
    p = unpack(model, vector)
    dc = comoving_distance_mpc(model, z_cmb, vector, steps=steps, integration_mode="log1p")
    r_shift = math.sqrt(p["Om"]) * p["H0"] * dc / C_KMS
    if acoustic_mode == "structure_d_rd":
        sound_scale = rd_drag_mpc(model, vector)
    elif acoustic_mode == "freestanding_rs_star":
        if not rs_star_mpc or rs_star_mpc <= 0.0:
            raise ValueError("rs_star_mpc required for freestanding_rs_star")
        sound_scale = float(rs_star_mpc)
    else:
        raise ValueError("unknown acoustic mode: %s" % acoustic_mode)
    la = math.pi * dc / sound_scale
    return [r_shift, la, p["Ob_h2"]]


def chi2_diagonal(points, prediction_fn, value_key, sigma_key):
    total = 0.0
    predictions = []
    for point in points:
        pred = float(prediction_fn(point))
        obs = float(point[value_key])
        sigma = float(point[sigma_key])
        if sigma <= 0.0 or not math.isfinite(pred):
            return float("inf"), []
        total += ((obs - pred) / sigma) ** 2
        predictions.append(pred)
    return total, predictions


def chi2_covariance(observed, predicted, covariance_inverse):
    residual = [float(o) - float(p) for o, p in zip(observed, predicted)]
    return quad_form(residual, covariance_inverse)
