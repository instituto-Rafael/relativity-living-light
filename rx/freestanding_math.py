"""Python-stdlib mirror of the canonical freestanding C math.

This exists only for implementation parity testing. It mirrors the algorithms in
core/lowlevel_runtime/c/rll_canonical_real.c and the Q16 evidence mechanics in
rll_canonical_real_inputs.c. No third-party imports.
"""

from __future__ import annotations

import math
from decimal import Decimal, ROUND_HALF_UP

C_KMS = 299792.458
PI = 3.1415926535897932384626433832795
LN2 = 0.69314718055994530941723212145818
LN10 = 2.3025850929940456840179914546844
BIG = 1.0e300
Q16 = 65536


def fs_sqrt(x):
    if not (x > 0.0):
        return 0.0 if x == 0.0 else -1.0
    g = x if x > 1.0 else 1.0
    for _ in range(28):
        g = 0.5 * (g + x / g)
    return g


def fs_cbrt(x):
    g = 1.0
    if x == 0.0:
        return 0.0
    if x < 0.0:
        return -fs_cbrt(-x)
    while g * g * g < x and g < 1.0e100:
        g *= 2.0
    while (g * 0.5) ** 3 > x:
        g *= 0.5
    for _ in range(24):
        g = (2.0 * g + x / (g * g)) / 3.0
    return g


def fs_exp(x):
    term = 1.0
    total = 1.0
    scale = 1.0
    x = max(-60.0, min(60.0, x))
    while x > LN2:
        x -= LN2
        scale *= 2.0
    while x < -LN2:
        x += LN2
        scale *= 0.5
    for i in range(1, 19):
        term *= x / float(i)
        total += term
    return total * scale


def fs_log(x):
    if not (x > 0.0):
        return -BIG
    k = 0.0
    while x > 1.5:
        x *= 0.5
        k += 1.0
    while x < 0.75:
        x *= 2.0
        k -= 1.0
    y = (x - 1.0) / (x + 1.0)
    y2 = y * y
    term = y
    total = 0.0
    for n in range(1, 32, 2):
        total += term / float(n)
        term *= y2
    return 2.0 * total + k * LN2


def fs_pow_pos(x, p):
    if not (x > 0.0):
        return -1.0
    return fs_exp(p * fs_log(x))


def transition(z, p):
    width = p["wt"]
    if not (width > 0.0):
        return -1.0
    arg = max(-60.0, min(60.0, (z - p["zt"]) / width))
    return 1.0 / (1.0 + fs_exp(arg))


def e2(z, p, model):
    zp1 = 1.0 + z
    matter = p["Om"] * zp1 * zp1 * zp1
    radiation = p["Or"] * zp1 * zp1 * zp1 * zp1
    if model == "LCDM":
        value = matter + radiation + (1.0 - p["Om"] - p["Or"])
    elif model == "RLL":
        fz = transition(z, p)
        ol = 1.0 - p["Om"] - p["Or"] - p["Os0"]
        value = matter + radiation + ol + p["Os0"] * (
            fz + (1.0 - fz) * zp1 * zp1 * zp1
        )
    else:
        raise ValueError(model)
    return value


def e(z, p, model):
    value = e2(z, p, model)
    return fs_sqrt(value) if value > 0.0 else -1.0


def comoving_distance(z, p, model):
    if z == 0.0:
        return 0.0
    n = max(128, min(4096, int(p["steps"])))
    if n & 1:
        n += 1
    xmax = fs_log(1.0 + z)
    h = xmax / float(n)
    total = 0.0
    for i in range(n + 1):
        x = h * float(i)
        zp1 = fs_exp(x)
        zi = zp1 - 1.0
        ei = e(zi, p, model)
        integrand = zp1 / ei
        weight = 1.0 if i in (0, n) else (4.0 if i & 1 else 2.0)
        total += weight * integrand
    return (C_KMS / p["H0"]) * (h / 3.0) * total


def omega_m_z(z, p, model):
    zp1 = 1.0 + z
    value = e2(z, p, model)
    return p["Om"] * zp1 * zp1 * zp1 / value


def growth_factor(z, p, model):
    n = max(128, min(2048, int(p["steps"])))
    if n & 1:
        n += 1
    xmax = fs_log(1.0 + z)
    h = xmax / float(n)
    total = 0.0
    for i in range(n + 1):
        x = h * float(i)
        zi = fs_exp(x) - 1.0
        omz = omega_m_z(zi, p, model)
        f = fs_pow_pos(omz, p["gamma"])
        weight = 1.0 if i in (0, n) else (4.0 if i & 1 else 2.0)
        total += weight * f
    return fs_exp(-(h / 3.0) * total)


def predict(observable, z, p, model):
    if observable == "HZ":
        return p["H0"] * e(z, p, model)
    if observable == "FS8":
        omz = omega_m_z(z, p, model)
        f = fs_pow_pos(omz, p["gamma"])
        d = growth_factor(z, p, model)
        return f * p["sigma8"] * d
    if observable == "DH":
        return (C_KMS / (p["H0"] * e(z, p, model))) / p["rd"]
    if observable in ("DM", "DV"):
        dc = comoving_distance(z, p, model)
        if observable == "DM":
            return dc / p["rd"]
        dh = C_KMS / (p["H0"] * e(z, p, model))
        return fs_cbrt(z * dc * dc * dh) / p["rd"]
    if observable in ("CMB_R", "CMB_LA"):
        dc = comoving_distance(z, p, model)
        if observable == "CMB_R":
            return fs_sqrt(p["Om"]) * p["H0"] * dc / C_KMS
        return PI * dc / p["rs_star"]
    if observable == "OBH2":
        h100 = p["H0"] / 100.0
        return p["Ob"] * h100 * h100
    raise ValueError(observable)


def q16_from_float(value):
    scaled = float(value) * Q16
    return int(scaled + 0.5) if scaled >= 0.0 else int(scaled - 0.5)


def q16_from_text(text):
    value = Decimal(str(text)) * Decimal(Q16)
    return int(value.to_integral_value(rounding=ROUND_HALF_UP))


def q16_to_float(value):
    return float(value) / Q16


def trunc_div(num, den):
    if den == 0:
        raise ZeroDivisionError
    sign = -1 if (num < 0) ^ (den < 0) else 1
    return sign * (abs(int(num)) // abs(int(den)))


def chi_diag_q16(obs_q16, model_q16, sigma_q16):
    delta = int(obs_q16) - int(model_q16)
    ratio = trunc_div(delta << 16, int(sigma_q16))
    return (abs(ratio) * abs(ratio)) >> 16


def inverse_corr_q16(r):
    c00 = r[4] * r[8] - r[5] * r[7]
    c01 = -(r[3] * r[8] - r[5] * r[6])
    c02 = r[3] * r[7] - r[4] * r[6]
    c10 = -(r[1] * r[8] - r[2] * r[7])
    c11 = r[0] * r[8] - r[2] * r[6]
    c12 = -(r[0] * r[7] - r[1] * r[6])
    c20 = r[1] * r[5] - r[2] * r[4]
    c21 = -(r[0] * r[5] - r[2] * r[3])
    c22 = r[0] * r[4] - r[1] * r[3]
    det = r[0] * c00 + r[1] * c01 + r[2] * c02
    cof = [c00, c10, c20, c01, c11, c21, c02, c12, c22]
    den = det >> 17
    if den <= 0:
        raise ValueError("correlation matrix not invertible in Q16 contract")
    return [trunc_div(x << 15, den) for x in cof]


def cmb_chi_q16(obs, model, sigma, correlation):
    inv = inverse_corr_q16(correlation)
    u = [trunc_div((obs[i] - model[i]) << 16, sigma[i]) for i in range(3)]
    tmp = []
    for i in range(3):
        acc = 0
        for j in range(3):
            acc += (inv[i * 3 + j] * u[j]) >> 16
        tmp.append(acc)
    chi = 0
    for i in range(3):
        chi += (u[i] * tmp[i]) >> 16
    return chi
