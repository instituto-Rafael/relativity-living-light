#!/usr/bin/env python3
"""Matemática estrutural canônica do fundo cosmológico RLL.

Este módulo é determinístico e independente de dados observacionais. Ele valida
a estrutura algébrica/cinemática antes de qualquer likelihood ou ajuste real.

Hipóteses: fundo FLRW espacialmente plano, z > -1, largura wt > 0 e E² > 0.
Os escalares normalizados são R_bar = R c²/H0² e K_bar = K c⁴/H0⁴.
"""
from __future__ import annotations

from dataclasses import asdict, dataclass, replace
import math
from typing import Callable, Iterable

C_KM_S = 299792.458


@dataclass(frozen=True)
class RLLParameters:
    H0: float = 67.4
    Om: float = 0.315
    Or: float = 9.2e-5
    Os0: float = 0.02
    zt: float = 1.0
    wt: float = 0.3
    OB0: float = 0.0
    OP0: float = 0.0
    rd_mpc: float = 147.09

    def validate(self) -> None:
        for name, value in asdict(self).items():
            if not math.isfinite(value):
                raise ValueError(f"{name} must be finite")
        if self.H0 <= 0.0:
            raise ValueError("H0 must be positive")
        if self.rd_mpc <= 0.0:
            raise ValueError("rd_mpc must be positive")
        if self.wt <= 0.0:
            raise ValueError("wt must be positive")
        if self.Om < 0.0 or self.Or < 0.0:
            raise ValueError("Om and Or must be non-negative")

    @property
    def radiation_total(self) -> float:
        return self.Or + self.OB0 + self.OP0

    @property
    def omega_lambda(self) -> float:
        # g(0)=1 exatamente; o setor RLL contribui Os0 em z=0.
        return 1.0 - self.Om - self.radiation_total - self.Os0

    def null_limit(self) -> "RLLParameters":
        return replace(self, Os0=0.0, OB0=0.0, OP0=0.0)


def _validate_z(z: float) -> None:
    if not math.isfinite(z):
        raise ValueError("z must be finite")
    if z <= -1.0:
        raise ValueError("z must be greater than -1")


def scale_factor(z: float) -> float:
    _validate_z(z)
    return 1.0 / (1.0 + z)


def transition_f(z: float, p: RLLParameters) -> float:
    p.validate()
    _validate_z(z)
    x = (z - p.zt) / p.wt
    # Forma estável da logística para evitar overflow.
    if x >= 0.0:
        e = math.exp(-x)
        return e / (1.0 + e)
    e = math.exp(x)
    return 1.0 / (1.0 + e)


def transition_f_prime(z: float, p: RLLParameters) -> float:
    f = transition_f(z, p)
    return -f * (1.0 - f) / p.wt


def transition_f_second(z: float, p: RLLParameters) -> float:
    f = transition_f(z, p)
    return f * (1.0 - f) * (1.0 - 2.0 * f) / (p.wt * p.wt)


def sector_g(z: float, p: RLLParameters) -> float:
    u = 1.0 + z
    f = transition_f(z, p)
    return f + (1.0 - f) * u**3


def sector_g_prime(z: float, p: RLLParameters) -> float:
    u = 1.0 + z
    f = transition_f(z, p)
    fp = transition_f_prime(z, p)
    q = u**3
    qp = 3.0 * u**2
    return fp * (1.0 - q) + (1.0 - f) * qp


def sector_g_second(z: float, p: RLLParameters) -> float:
    u = 1.0 + z
    f = transition_f(z, p)
    fp = transition_f_prime(z, p)
    fpp = transition_f_second(z, p)
    q = u**3
    qp = 3.0 * u**2
    qpp = 6.0 * u
    return fpp * (1.0 - q) - 2.0 * fp * qp + (1.0 - f) * qpp


def e2(z: float, p: RLLParameters) -> float:
    p.validate()
    _validate_z(z)
    u = 1.0 + z
    return (
        p.Om * u**3
        + p.radiation_total * u**4
        + p.omega_lambda
        + p.Os0 * sector_g(z, p)
    )


def e2_prime(z: float, p: RLLParameters) -> float:
    u = 1.0 + z
    return (
        3.0 * p.Om * u**2
        + 4.0 * p.radiation_total * u**3
        + p.Os0 * sector_g_prime(z, p)
    )


def e2_second(z: float, p: RLLParameters) -> float:
    u = 1.0 + z
    return (
        6.0 * p.Om * u
        + 12.0 * p.radiation_total * u**2
        + p.Os0 * sector_g_second(z, p)
    )


def expansion_e(z: float, p: RLLParameters) -> float:
    value = e2(z, p)
    if value <= 0.0:
        raise ValueError(f"E^2(z) must be positive; got {value} at z={z}")
    return math.sqrt(value)


def expansion_e_prime(z: float, p: RLLParameters) -> float:
    return e2_prime(z, p) / (2.0 * expansion_e(z, p))


def log_hubble_slope(z: float, p: RLLParameters) -> float:
    """D1 = d ln(E) / d ln(1+z)."""
    u = 1.0 + z
    s = e2(z, p)
    return 0.5 * u * e2_prime(z, p) / s


def log_hubble_curvature(z: float, p: RLLParameters) -> float:
    """D2 = d² ln(E) / d[ln(1+z)]²."""
    u = 1.0 + z
    s = e2(z, p)
    sp = e2_prime(z, p)
    spp = e2_second(z, p)
    d1 = 0.5 * u * sp / s
    return d1 + 0.5 * u * u * (spp / s - (sp / s) ** 2)


def deceleration_q(z: float, p: RLLParameters) -> float:
    return log_hubble_slope(z, p) - 1.0


def effective_w_geometry(z: float, p: RLLParameters) -> float:
    """Diagnóstico efetivo do fundo; não é EOS microfísica."""
    return -1.0 + (2.0 / 3.0) * log_hubble_slope(z, p)


def jerk_j(z: float, p: RLLParameters) -> float:
    q = deceleration_q(z, p)
    return q * (2.0 * q + 1.0) + log_hubble_curvature(z, p)


def ricci_bar(z: float, p: RLLParameters) -> float:
    """R_bar = R c²/H0² para FLRW espacialmente plano."""
    return 6.0 * e2(z, p) * (2.0 - log_hubble_slope(z, p))


def kretschmann_bar(z: float, p: RLLParameters) -> float:
    """K_bar = K c⁴/H0⁴ para FLRW espacialmente plano."""
    q = deceleration_q(z, p)
    return 12.0 * e2(z, p) ** 2 * (1.0 + q * q)


def _simpson(fn: Callable[[float], float], a: float, b: float, n: int = 512) -> float:
    if b <= a:
        return 0.0
    if n < 2:
        raise ValueError("Simpson n must be >= 2")
    if n % 2:
        n += 1
    h = (b - a) / n
    total = fn(a) + fn(b)
    for i in range(1, n):
        total += (4.0 if i % 2 else 2.0) * fn(a + i * h)
    return total * h / 3.0


def comoving_distance_mpc(z: float, p: RLLParameters, n: int = 512) -> float:
    _validate_z(z)
    if z < 0.0:
        raise ValueError("default distance implementation requires z >= 0")
    integral = _simpson(lambda zp: 1.0 / expansion_e(zp, p), 0.0, z, n=n)
    return (C_KM_S / p.H0) * integral


def dh_over_rd(z: float, p: RLLParameters) -> float:
    return (C_KM_S / (p.H0 * expansion_e(z, p))) / p.rd_mpc


def dm_over_rd(z: float, p: RLLParameters, n: int = 512) -> float:
    return comoving_distance_mpc(z, p, n=n) / p.rd_mpc


def dv_over_rd(z: float, p: RLLParameters, n: int = 512) -> float:
    if z == 0.0:
        return 0.0
    dm = comoving_distance_mpc(z, p, n=n)
    dh = C_KM_S / (p.H0 * expansion_e(z, p))
    return (z * dm * dm * dh) ** (1.0 / 3.0) / p.rd_mpc


def finite_difference_first(fn: Callable[[float], float], z: float, h: float = 1e-5) -> float:
    if z - h <= -1.0:
        return (fn(z + h) - fn(z)) / h
    return (fn(z + h) - fn(z - h)) / (2.0 * h)


def finite_difference_second(fn: Callable[[float], float], z: float, h: float = 2e-4) -> float:
    if z - h <= -1.0:
        return (fn(z + 2.0 * h) - 2.0 * fn(z + h) + fn(z)) / (h * h)
    return (fn(z + h) - 2.0 * fn(z) + fn(z - h)) / (h * h)


def relative_residual(a: float, b: float) -> float:
    return abs(a - b) / max(1.0, abs(a), abs(b))


def linspace(start: float, stop: float, points: int) -> list[float]:
    if points < 2:
        raise ValueError("points must be >= 2")
    step = (stop - start) / (points - 1)
    return [start + i * step for i in range(points)]


def scan_invariants(
    p: RLLParameters,
    z_values: Iterable[float],
    derivative_stride: int = 10,
) -> dict[str, float | bool]:
    p.validate()
    zs = list(z_values)
    if not zs:
        raise ValueError("z_values must not be empty")

    norm_residual = abs(e2(0.0, p) - 1.0)
    null = p.null_limit()
    max_null_residual = 0.0
    min_e2 = math.inf
    max_f_first = -math.inf
    max_f_bounds_violation = 0.0
    max_f_prime_residual = 0.0
    max_f_second_residual = 0.0
    max_e2_prime_residual = 0.0
    max_e2_second_residual = 0.0

    for i, z in enumerate(zs):
        value_e2 = e2(z, p)
        min_e2 = min(min_e2, value_e2)
        f = transition_f(z, p)
        fp = transition_f_prime(z, p)
        max_f_first = max(max_f_first, fp)
        max_f_bounds_violation = max(max_f_bounds_violation, max(0.0, -f, f - 1.0))

        u = 1.0 + z
        lcdm_exact = p.Om * u**3 + p.Or * u**4 + (1.0 - p.Om - p.Or)
        max_null_residual = max(max_null_residual, abs(e2(z, null) - lcdm_exact))

        if i % max(1, derivative_stride) == 0:
            fp_num = finite_difference_first(lambda x: transition_f(x, p), z)
            fpp_num = finite_difference_second(lambda x: transition_f(x, p), z)
            sp_num = finite_difference_first(lambda x: e2(x, p), z)
            spp_num = finite_difference_second(lambda x: e2(x, p), z)
            max_f_prime_residual = max(max_f_prime_residual, relative_residual(fp, fp_num))
            max_f_second_residual = max(
                max_f_second_residual,
                relative_residual(transition_f_second(z, p), fpp_num),
            )
            max_e2_prime_residual = max(
                max_e2_prime_residual,
                relative_residual(e2_prime(z, p), sp_num),
            )
            max_e2_second_residual = max(
                max_e2_second_residual,
                relative_residual(e2_second(z, p), spp_num),
            )

    result: dict[str, float | bool] = {
        "normalization_residual": norm_residual,
        "null_limit_max_abs_residual": max_null_residual,
        "minimum_e2": min_e2,
        "transition_bounds_max_violation": max_f_bounds_violation,
        "transition_max_derivative": max_f_first,
        "f_prime_max_relative_residual": max_f_prime_residual,
        "f_second_max_relative_residual": max_f_second_residual,
        "e2_prime_max_relative_residual": max_e2_prime_residual,
        "e2_second_max_relative_residual": max_e2_second_residual,
    }
    result["passed"] = bool(
        norm_residual <= 1e-12
        and max_null_residual <= 1e-12
        and min_e2 > 0.0
        and max_f_bounds_violation <= 1e-15
        and max_f_first <= 1e-12
        and max_f_prime_residual <= 1e-7
        and max_f_second_residual <= 2e-6
        and max_e2_prime_residual <= 2e-7
        and max_e2_second_residual <= 2e-6
    )
    return result
