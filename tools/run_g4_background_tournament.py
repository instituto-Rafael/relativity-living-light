#!/usr/bin/env python3
"""Six-model G4 background tournament for RLL.

Frozen data blocks:
  * pure cosmic-chronometer H(z) rows (legacy BAO-labelled H(z) excluded),
  * DESI DR2 BAO 13-vector with the committed 13x13 covariance,
  * Pantheon+SH0ES with full STAT+SYS covariance and profiled M_B.

Models:
  LCDM, wCDM, CPL, GEDE, IDE Q=3 beta H rho_Lambda, and RLL.

This is deliberately a *background* tournament.  f_sigma8 and CMB are not
silently reused because GEDE/IDE/RLL require model-specific perturbation closure
before those observables can be compared fairly.  Passing this gate therefore
means fair background comparison, not physical confirmation.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import importlib.util
import json
import math
import os
import sys
import time
from dataclasses import dataclass
from pathlib import Path
from types import ModuleType
from typing import Any, Callable, Sequence

import numpy as np
from scipy.linalg import LinAlgError, cho_factor, cho_solve
from scipy.optimize import brentq, minimize

ROOT = Path(__file__).resolve().parents[1]
CONTRACT_PATH = ROOT / "data/contracts/rll_g4_background_tournament.v1.json"
G3_PATH = ROOT / "tools/run_g3_dataset_compatibility.py"
HZ_PATH = ROOT / "data/real/Hz_data_real.csv"
DESI_POINTS_PATH = ROOT / "data/real/cosmology/desi_dr2_bao_primary_points.csv"
DESI_COV_PATH = ROOT / "data/real/desi_dr2_bao_covariance.csv"
PANTHEON_CATALOG = ROOT / "data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES.dat"
PANTHEON_COV = ROOT / "data/real/cosmology/pantheon_plus/Pantheon+_Data/4_DISTANCES_AND_COVAR/Pantheon+SH0ES_STAT+SYS.cov"

C_KM_S = 299_792.458
OMEGA_R0 = 9.0e-5
MODEL_ORDER = ("LCDM", "wCDM", "CPL", "GEDE", "IDE_QrhoLambda", "RLL")
COMMON_NAMES = ("H0", "Omega_m", "omega_b_h2")
COMMON_BOUNDS = ((60.0, 80.0), (0.10, 0.60), (0.018, 0.026))
MODEL_SPEC: dict[str, dict[str, Any]] = {
    "LCDM": {"extra_names": (), "extra_bounds": (), "canonical": (70.0, 0.30, 0.02236)},
    "wCDM": {"extra_names": ("w",), "extra_bounds": ((-2.0, -0.3),), "canonical": (70.0, 0.30, 0.02236, -1.0)},
    "CPL": {"extra_names": ("w0", "wa"), "extra_bounds": ((-2.0, -0.3), (-3.0, 3.0)), "canonical": (70.0, 0.30, 0.02236, -1.0, 0.0)},
    "GEDE": {"extra_names": ("Delta",), "extra_bounds": ((-10.0, 10.0),), "canonical": (70.0, 0.30, 0.02236, 0.0)},
    "IDE_QrhoLambda": {"extra_names": ("beta",), "extra_bounds": ((-0.15, 0.15),), "canonical": (70.0, 0.30, 0.02236, 0.0)},
    "RLL": {
        "extra_names": ("Omega_s0", "z_t", "w_t"),
        "extra_bounds": ((0.0, 0.25), (0.10, 10.0), (0.05, 2.0)),
        "canonical": (70.0, 0.30, 0.02236, 0.0, 1.0, 0.30),
    },
}


@dataclass
class PantheonBlock:
    z_hd: np.ndarray
    z_hel: np.ndarray
    m_b_corr: np.ndarray
    ceph_dist: np.ndarray
    is_calibrator: np.ndarray
    cholesky: tuple[np.ndarray, bool]
    cinv_ones: np.ndarray
    one_cinv_one: float

    @property
    def n(self) -> int:
        return int(self.z_hd.size)


@dataclass
class CCBlock:
    z: np.ndarray
    observed: np.ndarray
    sigma: np.ndarray
    sources: tuple[str, ...]

    @property
    def n(self) -> int:
        return int(self.z.size)


@dataclass
class DESIBlock:
    z: np.ndarray
    observable: tuple[str, ...]
    observed: np.ndarray
    covariance: np.ndarray
    cholesky: tuple[np.ndarray, bool]

    @property
    def n(self) -> int:
        return int(self.z.size)


@dataclass
class TournamentData:
    pantheon: PantheonBlock
    cc: CCBlock
    desi: DESIBlock
    integration_grid: np.ndarray

    @property
    def n(self) -> int:
        return self.pantheon.n + self.cc.n + self.desi.n


def _module(name: str, path: Path) -> ModuleType:
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise ValueError("G4 contract must be an object")
    if value.get("claim_allowed") is not False:
        raise ValueError("G4 contract cannot promote claim_allowed")
    if tuple(value.get("models", {}).keys()) != MODEL_ORDER:
        raise ValueError("G4 contract model order does not match executable model order")
    return value


def load_cc(path: Path = HZ_PATH) -> CCBlock:
    rows: list[tuple[float, float, float, str]] = []
    with path.open(newline="", encoding="utf-8") as handle:
        for row in csv.DictReader(handle):
            source = str(row["source"])
            # Pure cosmic chronometers only.  Labels containing BAO are excluded
            # to avoid hidden cross-survey double counting alongside DESI DR2.
            if not source.startswith("CC_") or "BAO" in source.upper():
                continue
            rows.append((float(row["z"]), float(row["H_obs"]), float(row["sigma_H"]), source))
    if not rows:
        raise ValueError("no pure cosmic-chronometer rows selected")
    return CCBlock(
        z=np.asarray([r[0] for r in rows], dtype=float),
        observed=np.asarray([r[1] for r in rows], dtype=float),
        sigma=np.asarray([r[2] for r in rows], dtype=float),
        sources=tuple(r[3] for r in rows),
    )


def load_desi(points_path: Path = DESI_POINTS_PATH, covariance_path: Path = DESI_COV_PATH) -> DESIBlock:
    rows: list[dict[str, str]]
    with points_path.open(newline="", encoding="utf-8") as handle:
        rows = list(csv.DictReader(handle))
    if len(rows) != 13:
        raise ValueError(f"DESI vector must contain 13 rows, got {len(rows)}")
    matrix = np.loadtxt(covariance_path, delimiter=",", skiprows=1, usecols=range(1, 14), dtype=float)
    if matrix.shape != (13, 13):
        raise ValueError(f"DESI covariance shape={matrix.shape}")
    if not np.allclose(matrix, matrix.T, rtol=0.0, atol=1e-12):
        raise ValueError("DESI covariance is not symmetric")
    if np.any(np.diag(matrix) <= 0.0):
        raise ValueError("DESI covariance diagonal is not positive")
    try:
        factor = cho_factor(matrix, lower=True, check_finite=True)
    except LinAlgError as exc:
        raise ValueError("DESI covariance is not positive definite") from exc
    return DESIBlock(
        z=np.asarray([float(r["z_eff"]) for r in rows], dtype=float),
        observable=tuple(str(r["observable"]) for r in rows),
        observed=np.asarray([float(r["value"]) for r in rows], dtype=float),
        covariance=matrix,
        cholesky=factor,
    )


def _load_full_pantheon_covariance(path: Path, expected_n: int) -> np.ndarray:
    tokens = np.fromfile(path, dtype=float, sep=" ")
    if tokens.size != 1 + expected_n * expected_n:
        raise ValueError(f"Pantheon covariance token count={tokens.size}")
    dimension = int(tokens[0])
    if dimension != expected_n:
        raise ValueError(f"Pantheon covariance dimension={dimension}, expected={expected_n}")
    matrix = tokens[1:].reshape(expected_n, expected_n)
    asymmetry = float(np.max(np.abs(matrix - matrix.T)))
    if asymmetry > 5e-8:
        raise ValueError(f"Pantheon covariance asymmetry exceeds bounded ASCII roundoff: {asymmetry}")
    matrix = 0.5 * (matrix + matrix.T)
    return matrix


def load_pantheon(catalog_path: Path = PANTHEON_CATALOG, covariance_path: Path = PANTHEON_COV) -> PantheonBlock:
    table = np.genfromtxt(catalog_path, names=True, dtype=None, encoding="utf-8")
    if table.shape == ():
        table = np.asarray([table], dtype=table.dtype)
    names = set(table.dtype.names or ())
    required = {"zHD", "zHEL", "m_b_corr", "CEPH_DIST", "IS_CALIBRATOR"}
    if not required.issubset(names):
        raise ValueError(f"Pantheon missing columns {sorted(required - names)}")
    original_n = len(table)
    if original_n != 1701:
        raise ValueError(f"Pantheon catalog rows={original_n}, expected=1701")
    z_hd_all = np.asarray(table["zHD"], dtype=float)
    is_cal_all = np.asarray(table["IS_CALIBRATOR"], dtype=int) == 1
    selection = (z_hd_all > 0.01) | is_cal_all
    full_cov = _load_full_pantheon_covariance(covariance_path, original_n)
    cov = full_cov[np.ix_(selection, selection)]
    try:
        factor = cho_factor(cov, lower=True, check_finite=True)
    except LinAlgError as exc:
        raise ValueError("selected Pantheon covariance is not positive definite") from exc
    ones = np.ones(int(np.count_nonzero(selection)), dtype=float)
    cinv_ones = cho_solve(factor, ones, check_finite=False)
    norm = float(ones @ cinv_ones)
    if not math.isfinite(norm) or norm <= 0.0:
        raise ValueError("invalid Pantheon profile normalization")
    return PantheonBlock(
        z_hd=z_hd_all[selection],
        z_hel=np.asarray(table["zHEL"], dtype=float)[selection],
        m_b_corr=np.asarray(table["m_b_corr"], dtype=float)[selection],
        ceph_dist=np.asarray(table["CEPH_DIST"], dtype=float)[selection],
        is_calibrator=is_cal_all[selection],
        cholesky=factor,
        cinv_ones=cinv_ones,
        one_cinv_one=norm,
    )


def load_data(integration_points: int = 4096) -> TournamentData:
    pantheon = load_pantheon()
    cc = load_cc()
    desi = load_desi()
    z_max = max(float(np.max(pantheon.z_hd)), float(np.max(cc.z)), float(np.max(desi.z)))
    base_grid = np.linspace(0.0, z_max, max(256, int(integration_points)), dtype=float)
    grid = np.unique(np.concatenate((base_grid, pantheon.z_hd, cc.z, desi.z)))
    return TournamentData(pantheon=pantheon, cc=cc, desi=desi, integration_grid=grid)


def parameter_names(model: str) -> tuple[str, ...]:
    spec = MODEL_SPEC[model]
    return COMMON_NAMES + tuple(spec["extra_names"])


def bounds(model: str) -> tuple[tuple[float, float], ...]:
    spec = MODEL_SPEC[model]
    return COMMON_BOUNDS + tuple(spec["extra_bounds"])


def k_for_model(model: str) -> int:
    # All optimized parameters + one analytically profiled Pantheon M_B.
    return len(parameter_names(model)) + 1


def _gede_omega_de(z: np.ndarray | float, omega_de0: float, delta: float, z_t: float) -> np.ndarray:
    z_arr = np.asarray(z, dtype=float)
    den = 1.0 + math.tanh(float(delta) * math.log10(1.0 + float(z_t)))
    if not math.isfinite(den) or abs(den) < 1e-12:
        return np.full_like(z_arr, np.nan)
    arg = float(delta) * np.log10((1.0 + z_arr) / (1.0 + float(z_t)))
    return float(omega_de0) * (1.0 - np.tanh(arg)) / den


def gede_transition_redshift(omega_m: float, delta: float) -> float:
    omega_de0 = 1.0 - float(omega_m) - OMEGA_R0
    if omega_de0 <= 0.0:
        raise ValueError("GEDE requires positive present dark-energy density")
    if abs(float(delta)) < 1e-14:
        return float((omega_de0 / float(omega_m)) ** (1.0 / 3.0) - 1.0)

    def equation(z_t: float) -> float:
        de_at_transition = float(_gede_omega_de(np.asarray([z_t]), omega_de0, delta, z_t)[0])
        return float(omega_m) * (1.0 + z_t) ** 3 - de_at_transition

    low = 0.0
    high = 20.0
    f_low = equation(low)
    f_high = equation(high)
    if not (math.isfinite(f_low) and math.isfinite(f_high) and f_low <= 0.0 <= f_high):
        raise ValueError(f"GEDE transition root is not bracketed: f0={f_low}, f20={f_high}")
    return float(brentq(equation, low, high, xtol=1e-12, rtol=1e-12, maxiter=200))


def e2(model: str, z: np.ndarray | float, parameters: Sequence[float]) -> np.ndarray:
    p = np.asarray(parameters, dtype=float)
    if p.size != len(parameter_names(model)):
        raise ValueError(f"{model}: parameter length {p.size}")
    h0, omega_m, omega_b_h2 = map(float, p[:3])
    if h0 <= 0.0 or omega_m <= 0.0 or omega_b_h2 <= 0.0:
        return np.full_like(np.asarray(z, dtype=float), np.nan)
    z_arr = np.asarray(z, dtype=float)
    zp1 = 1.0 + z_arr
    omega_de0 = 1.0 - omega_m - OMEGA_R0
    if omega_de0 <= 0.0:
        return np.full_like(z_arr, np.nan)

    if model == "LCDM":
        value = omega_m * zp1**3 + OMEGA_R0 * zp1**4 + omega_de0
    elif model == "wCDM":
        w = float(p[3])
        value = omega_m * zp1**3 + OMEGA_R0 * zp1**4 + omega_de0 * zp1 ** (3.0 * (1.0 + w))
    elif model == "CPL":
        w0, wa = map(float, p[3:5])
        dark = zp1 ** (3.0 * (1.0 + w0 + wa)) * np.exp(-3.0 * wa * z_arr / zp1)
        value = omega_m * zp1**3 + OMEGA_R0 * zp1**4 + omega_de0 * dark
    elif model == "GEDE":
        delta = float(p[3])
        try:
            z_t = gede_transition_redshift(omega_m, delta)
        except ValueError:
            return np.full_like(z_arr, np.nan)
        dark = _gede_omega_de(z_arr, omega_de0, delta, z_t)
        value = omega_m * zp1**3 + OMEGA_R0 * zp1**4 + dark
    elif model == "IDE_QrhoLambda":
        beta = float(p[3])
        if beta <= -0.999:
            return np.full_like(z_arr, np.nan)
        h = h0 / 100.0
        omega_b = omega_b_h2 / (h * h)
        omega_c = omega_m - omega_b
        if omega_b <= 0.0 or omega_c <= 0.0:
            return np.full_like(z_arr, np.nan)
        # Primary-source convention: dot(rho_Lambda)=Q,
        # dot(rho_c)=-3H rho_c-Q with Q=3 beta H rho_Lambda.
        # Hence rho_Lambda=rho_Lambda0*a^(3 beta), and the exact background
        # CDM solution is used below.  beta=0 recovers LCDM exactly.
        matter_like_c = omega_c + beta * omega_de0 / (1.0 + beta)
        interacting_vacuum = omega_de0 / (1.0 + beta) * zp1 ** (-3.0 * beta)
        value = (omega_b + matter_like_c) * zp1**3 + OMEGA_R0 * zp1**4 + interacting_vacuum
    elif model == "RLL":
        omega_s0, z_t, w_t = map(float, p[3:6])
        omega_lambda = 1.0 - omega_m - OMEGA_R0 - omega_s0
        if omega_lambda <= 0.0 or w_t <= 0.0:
            return np.full_like(z_arr, np.nan)
        arg = np.clip((z_arr - z_t) / w_t, -500.0, 500.0)
        f_z = 1.0 / (1.0 + np.exp(arg))
        superposition = omega_s0 * (f_z + (1.0 - f_z) * zp1**3)
        value = omega_m * zp1**3 + OMEGA_R0 * zp1**4 + omega_lambda + superposition
    else:
        raise ValueError(f"unsupported model {model}")
    return np.asarray(value, dtype=float)


def rd_drag_mpc(h0: float, omega_m: float, omega_b_h2: float) -> float:
    om_h2 = float(omega_m) * (float(h0) / 100.0) ** 2
    if om_h2 <= 0.0 or omega_b_h2 <= 0.0:
        return math.nan
    return float(147.78 * (om_h2 / 0.1432) ** (-0.255) * (float(omega_b_h2) / 0.02236) ** (-0.134))


def expansion_and_distance(data: TournamentData, model: str, parameters: Sequence[float]) -> tuple[np.ndarray, np.ndarray]:
    squared = e2(model, data.integration_grid, parameters)
    h0 = float(parameters[0])
    if np.any(~np.isfinite(squared)) or np.any(squared <= 0.0):
        raise ValueError("non-physical expansion history")
    hz = h0 * np.sqrt(squared)
    inverse_h = C_KM_S / hz
    dz = np.diff(data.integration_grid)
    dc = np.concatenate(([0.0], np.cumsum(0.5 * (inverse_h[:-1] + inverse_h[1:]) * dz)))
    return hz, dc


def model_predictions(data: TournamentData, model: str, parameters: Sequence[float]) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    _, distance_grid = expansion_and_distance(data, model, parameters)
    h0, omega_m, omega_b_h2 = map(float, parameters[:3])

    # Pantheon distance-modulus component; calibrators use CEPH_DIST exactly as
    # in the existing full-covariance adapter.
    dc_sn = np.interp(data.pantheon.z_hd, data.integration_grid, distance_grid)
    dl = (1.0 + data.pantheon.z_hel) * dc_sn
    non_cal = ~data.pantheon.is_calibrator
    if np.any(dl[non_cal] <= 0.0):
        raise ValueError("non-positive SN luminosity distance")
    mu = np.empty(data.pantheon.n, dtype=float)
    mu[data.pantheon.is_calibrator] = data.pantheon.ceph_dist[data.pantheon.is_calibrator]
    mu[non_cal] = 5.0 * np.log10(dl[non_cal]) + 25.0

    # Pure cosmic chronometers.
    cc_e2 = e2(model, data.cc.z, parameters)
    if np.any(~np.isfinite(cc_e2)) or np.any(cc_e2 <= 0.0):
        raise ValueError("non-physical CC expansion")
    cc_pred = h0 * np.sqrt(cc_e2)

    # DESI DR2 background distances, all using the same r_d policy.
    rd = rd_drag_mpc(h0, omega_m, omega_b_h2)
    if not math.isfinite(rd) or rd <= 0.0:
        raise ValueError("invalid sound-horizon approximation")
    dc_desi = np.interp(data.desi.z, data.integration_grid, distance_grid)
    desi_e2 = e2(model, data.desi.z, parameters)
    desi_h = h0 * np.sqrt(desi_e2)
    desi_pred = np.empty(data.desi.n, dtype=float)
    for i, observable in enumerate(data.desi.observable):
        z = float(data.desi.z[i])
        if observable == "DM_over_rd":
            desi_pred[i] = dc_desi[i] / rd
        elif observable == "DH_over_rd":
            desi_pred[i] = (C_KM_S / desi_h[i]) / rd
        elif observable == "DV_over_rd":
            dv = (z * C_KM_S * dc_desi[i] ** 2 / desi_h[i]) ** (1.0 / 3.0)
            desi_pred[i] = dv / rd
        else:
            raise ValueError(f"unsupported DESI observable {observable}")
    return mu, cc_pred, desi_pred


def profiled_components(data: TournamentData, model: str, parameters: Sequence[float]) -> dict[str, Any]:
    mu, cc_pred, desi_pred = model_predictions(data, model, parameters)

    p_difference = data.pantheon.m_b_corr - mu
    p_weighted_unprofiled = cho_solve(data.pantheon.cholesky, p_difference, check_finite=False)
    m_b = float(np.sum(p_weighted_unprofiled) / data.pantheon.one_cinv_one)
    p_residual = p_difference - m_b
    p_weighted = p_weighted_unprofiled - m_b * data.pantheon.cinv_ones
    p_chi2 = float(p_residual @ p_weighted)

    cc_residual = data.cc.observed - cc_pred
    cc_weighted = cc_residual / (data.cc.sigma**2)
    cc_chi2 = float(np.sum((cc_residual / data.cc.sigma) ** 2))

    d_residual = data.desi.observed - desi_pred
    d_weighted = cho_solve(data.desi.cholesky, d_residual, check_finite=False)
    d_chi2 = float(d_residual @ d_weighted)

    total = p_chi2 + cc_chi2 + d_chi2
    if not math.isfinite(total) or total < -1e-7:
        raise ValueError("invalid total chi2")
    return {
        "total": max(0.0, total),
        "Pantheon": max(0.0, p_chi2),
        "CC": max(0.0, cc_chi2),
        "DESI": max(0.0, d_chi2),
        "M_B": m_b,
        "pantheon_weighted": p_weighted,
        "cc_weighted": cc_weighted,
        "desi_weighted": d_weighted,
    }


def objective_and_gradient(data: TournamentData, model: str, parameters: np.ndarray) -> tuple[float, np.ndarray]:
    try:
        base = profiled_components(data, model, parameters)
    except (ValueError, FloatingPointError, OverflowError):
        return 1e30, np.zeros_like(parameters, dtype=float)

    gradient = np.zeros_like(parameters, dtype=float)
    model_bounds = bounds(model)
    for index, (lower, upper) in enumerate(model_bounds):
        scale = max(1.0, abs(float(parameters[index])), float(upper - lower))
        step = 2.0e-5 * scale
        low = max(float(lower), float(parameters[index]) - step)
        high = min(float(upper), float(parameters[index]) + step)
        if high <= low:
            continue
        plus = np.asarray(parameters, dtype=float).copy()
        minus = np.asarray(parameters, dtype=float).copy()
        plus[index] = high
        minus[index] = low
        try:
            p_mu, p_cc, p_desi = model_predictions(data, model, plus)
            m_mu, m_cc, m_desi = model_predictions(data, model, minus)
        except (ValueError, FloatingPointError, OverflowError):
            gradient[index] = 0.0
            continue
        inv = 1.0 / (high - low)
        d_mu = (p_mu - m_mu) * inv
        d_cc_pred = (p_cc - m_cc) * inv
        d_desi_pred = (p_desi - m_desi) * inv
        # Residual = observed - prediction.  The derivative of the profiled M_B
        # drops out at the optimum of the linear nuisance parameter.
        g_p = -2.0 * float(d_mu @ base["pantheon_weighted"])
        g_cc = -2.0 * float(d_cc_pred @ base["cc_weighted"])
        g_desi = -2.0 * float(d_desi_pred @ base["desi_weighted"])
        gradient[index] = g_p + g_cc + g_desi
    return float(base["total"]), gradient


def information_criteria(chi2: float, n: int, k: int) -> dict[str, float | int]:
    aic = float(chi2 + 2.0 * k)
    denom = n - k - 1
    aicc = float(aic + 2.0 * k * (k + 1) / denom) if denom > 0 else math.inf
    bic = float(chi2 + k * math.log(n))
    return {"chi2": float(chi2), "AIC": aic, "AICc": aicc, "BIC": bic, "N": n, "k": k, "dof": n - k}


def _start(model: str, seed: int, index: int) -> tuple[np.ndarray, str]:
    spec = MODEL_SPEC[model]
    if index == 0:
        return np.asarray(spec["canonical"], dtype=float), "canonical_nested_null_start"
    rng = np.random.default_rng(int(seed))
    b = np.asarray(bounds(model), dtype=float)
    return rng.uniform(b[:, 0], b[:, 1]), "seeded_uniform_multistart"


def _boundary_hits(model: str, values: Sequence[float], fraction: float = 2e-5) -> list[str]:
    hits: list[str] = []
    for name, value, (low, high) in zip(parameter_names(model), values, bounds(model), strict=True):
        tolerance = max(1e-10, fraction * (high - low))
        if abs(float(value) - low) <= tolerance or abs(float(value) - high) <= tolerance:
            hits.append(name)
    return hits


def fit_model(data: TournamentData, model: str, seeds: Sequence[int], maxiter: int, ftol: float) -> dict[str, Any]:
    runs: list[dict[str, Any]] = []
    for index, seed in enumerate(seeds):
        x0, strategy = _start(model, int(seed), index)
        started = time.perf_counter()
        result = minimize(
            lambda x: objective_and_gradient(data, model, np.asarray(x, dtype=float)),
            x0,
            method="L-BFGS-B",
            jac=True,
            bounds=bounds(model),
            options={"maxiter": int(maxiter), "ftol": float(ftol), "gtol": 1e-7, "maxls": 30},
        )
        elapsed = time.perf_counter() - started
        try:
            components = profiled_components(data, model, result.x)
            finite = math.isfinite(float(components["total"]))
        except Exception as exc:
            components = {"total": math.inf, "Pantheon": math.inf, "CC": math.inf, "DESI": math.inf, "M_B": math.nan}
            finite = False
            message = f"{result.message}; postfit={exc}"
        else:
            message = str(result.message)
        runs.append(
            {
                "seed": int(seed),
                "start_strategy": strategy,
                "initial_parameters": dict(zip(parameter_names(model), map(float, x0), strict=True)),
                "parameters": dict(zip(parameter_names(model), map(float, result.x), strict=True)),
                "chi2": float(components["total"]),
                "chi2_Pantheon": float(components["Pantheon"]),
                "chi2_CC": float(components["CC"]),
                "chi2_DESI": float(components["DESI"]),
                "M_B_profiled": float(components["M_B"]),
                "success": bool(result.success and finite),
                "message": message,
                "iterations": int(getattr(result, "nit", -1)),
                "function_evaluations": int(getattr(result, "nfev", -1)),
                "gradient_evaluations": int(getattr(result, "njev", -1)),
                "boundary_hits": _boundary_hits(model, result.x),
                "runtime_seconds": elapsed,
            }
        )
    finite_runs = [run for run in runs if math.isfinite(run["chi2"])]
    if not finite_runs:
        raise RuntimeError(f"{model}: no finite optimization run")
    best = min(finite_runs, key=lambda run: run["chi2"])
    ic = information_criteria(best["chi2"], data.n, k_for_model(model))
    row: dict[str, Any] = {
        "model": model,
        **ic,
        **best["parameters"],
        "M_B_profiled": best["M_B_profiled"],
        "chi2_Pantheon": best["chi2_Pantheon"],
        "chi2_CC": best["chi2_CC"],
        "chi2_DESI": best["chi2_DESI"],
        "best_seed": best["seed"],
        "boundary_hits": best["boundary_hits"],
    }
    chi_values = [float(run["chi2"]) for run in finite_runs]
    return {
        "model": model,
        "status": "PASS" if all(run["success"] for run in runs) else "PASS_WITH_NONCONVERGED_SEED",
        "best": row,
        "runs": runs,
        "stability": {
            "seed_count": len(runs),
            "converged_count": sum(1 for run in runs if run["success"]),
            "finite_count": len(finite_runs),
            "chi2_min": min(chi_values),
            "chi2_max": max(chi_values),
            "chi2_span": max(chi_values) - min(chi_values),
        },
    }


def null_limit_receipt() -> dict[str, Any]:
    z = np.asarray([0.0, 0.1, 0.5, 1.0, 2.33], dtype=float)
    lcdm = np.asarray([70.0, 0.30, 0.02236])
    baseline = e2("LCDM", z, lcdm)
    checks = {
        "GEDE_Delta_0": float(np.max(np.abs(e2("GEDE", z, [70.0, 0.30, 0.02236, 0.0]) - baseline))),
        "IDE_beta_0": float(np.max(np.abs(e2("IDE_QrhoLambda", z, [70.0, 0.30, 0.02236, 0.0]) - baseline))),
        "RLL_Omega_s0_0": float(np.max(np.abs(e2("RLL", z, [70.0, 0.30, 0.02236, 0.0, 1.0, 0.30]) - baseline))),
    }
    return {"checks": checks, "tolerance": 1e-12, "passed": all(value <= 1e-12 for value in checks.values())}


def build_report(*, seeds: Sequence[int] | None = None, maxiter: int | None = None, ftol: float | None = None, integration_points: int | None = None) -> dict[str, Any]:
    contract = load_contract()
    g3 = _module("rll_g3_for_g4", G3_PATH).build_report(ROOT)
    if g3.get("state") != "PASS_LIMITED_COMPATIBILITY_BRANCH":
        raise RuntimeError(f"G3 prerequisite is not satisfied: {g3.get('state')}")

    seeds = tuple(int(x) for x in (seeds or contract["seeds"]))
    maxiter = int(maxiter if maxiter is not None else contract["maxiter"])
    ftol = float(ftol if ftol is not None else contract["ftol"])
    integration_points = int(integration_points if integration_points is not None else contract["integration_points"])
    nulls = null_limit_receipt()
    if not nulls["passed"]:
        raise RuntimeError(f"mandatory null limit failed: {nulls}")

    started = time.perf_counter()
    data = load_data(integration_points=integration_points)
    models: dict[str, Any] = {}
    rows: list[dict[str, Any]] = []
    for model in MODEL_ORDER:
        result = fit_model(data, model, seeds, maxiter, ftol)
        models[model] = result
        rows.append(result["best"])

    by_name = {row["model"]: row for row in rows}
    lcdm = by_name["LCDM"]
    deltas: dict[str, dict[str, float]] = {}
    for model in MODEL_ORDER[1:]:
        row = by_name[model]
        deltas[model] = {
            "delta_chi2": float(row["chi2"] - lcdm["chi2"]),
            "delta_AIC": float(row["AIC"] - lcdm["AIC"]),
            "delta_AICc": float(row["AICc"] - lcdm["AICc"]),
            "delta_BIC": float(row["BIC"] - lcdm["BIC"]),
        }

    all_finite = all(math.isfinite(float(row["chi2"])) for row in rows)
    all_models_present = set(by_name) == set(MODEL_ORDER)
    at_least_one_converged_each = all(models[m]["stability"]["converged_count"] >= 1 for m in MODEL_ORDER)
    state = "PASS_LIMITED_G4_BACKGROUND_TOURNAMENT" if all_finite and all_models_present and at_least_one_converged_each else "BLOCKED_G4_BACKGROUND_TOURNAMENT"

    input_paths = [HZ_PATH, DESI_POINTS_PATH, DESI_COV_PATH, PANTHEON_CATALOG, PANTHEON_COV, CONTRACT_PATH]
    return {
        "schema": "rll.g4_background_tournament_receipt.v1",
        "state": state,
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "claim_allowed": False,
        "scientific_confirmation": False,
        "publication_effect": "NONE",
        "runtime_seconds": time.perf_counter() - started,
        "g3_prerequisite_state": g3["state"],
        "datasets": {
            "Pantheon_rows": data.pantheon.n,
            "pure_CC_rows": data.cc.n,
            "DESI_rows": data.desi.n,
            "N_total": data.n,
            "excluded_Hz_rows_policy": "all H(z) sources not starting CC_ or containing BAO",
            "growth_CMB_policy": "DEFER_TO_G8_G9_NO_PROXY_PROMOTION",
        },
        "input_sha256": {str(path.relative_to(ROOT)): sha256_file(path) for path in input_paths},
        "method": {
            "models": list(MODEL_ORDER),
            "seeds": list(seeds),
            "maxiter": maxiter,
            "ftol": ftol,
            "integration_points": integration_points,
            "optimizer": "multistart L-BFGS-B with analytic-profile nuisance and finite-difference physical gradient",
            "Pantheon_covariance": "full STAT+SYS",
            "DESI_covariance": "full committed 13x13",
            "sound_horizon": "same rd(H0,Omega_m,omega_b_h2) calibrated approximation for all six models",
        },
        "model_source_boundaries": {
            "GEDE": "arXiv:2103.03815v2 Eq.4; Delta prior [-10,10]; z_t derived, not free",
            "IDE_QrhoLambda": "arXiv:1506.06349; Q=3 beta H rho_Lambda; beta prior [-0.15,0.15]",
            "RLL": "repository canonical background; Omega_s0=0 null limit",
        },
        "null_limits": nulls,
        "rows": rows,
        "models": models,
        "deltas_vs_LCDM": deltas,
        "negative_results_preserved": True,
        "scientific_boundary": "A fair background tournament is not perturbation closure, Bayesian evidence, independent replication, or model confirmation.",
        "F_ok": [
            "mandatory LCDM/wCDM/CPL/GEDE/IDE/RLL background models executed on identical frozen blocks" if all_models_present else "TOKEN_VAZIO_MODEL_FAMILY",
            "GEDE/IDE/RLL null limits recover LCDM" if nulls["passed"] else "CONTRADICTION_NULL_LIMIT",
            "full Pantheon and DESI covariances retained",
            "legacy BAO-labelled H(z) rows excluded from the CC block",
        ],
        "F_gap": [
            "G8 perturbation closure remains required before f_sigma8/full-CMB fairness",
            "GEDE/IDE implementations in this gate are background-only despite primary papers treating perturbations",
            "nested-sampling evidence remains G6, not replaced by AIC/AICc/BIC",
            "independent replication remains G10",
        ],
        "F_next": "freeze this tournament as the G4 background manifest; build G5 canonical joint background likelihood around the exact same hashes before inference",
    }


def main() -> int:
    parser = argparse.ArgumentParser(description="Run six-model G4 background fairness tournament")
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--seeds", default="11,23,37,53,71")
    parser.add_argument("--maxiter", type=int, default=250)
    parser.add_argument("--ftol", type=float, default=1e-10)
    parser.add_argument("--integration-points", type=int, default=4096)
    parser.add_argument("--require-pass", action="store_true")
    args = parser.parse_args()
    seeds = tuple(int(item) for item in args.seeds.split(",") if item.strip())
    try:
        report = build_report(seeds=seeds, maxiter=args.maxiter, ftol=args.ftol, integration_points=args.integration_points)
    except Exception as exc:
        print(f"[rll] BLOCKED_G4_EXCEPTION: {exc}", file=sys.stderr)
        return 2
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(json.dumps(report, indent=2, ensure_ascii=False, allow_nan=False) + "\n", encoding="utf-8")
    print(f"{report['state']} N={report['datasets']['N_total']} runtime={report['runtime_seconds']:.3f}s")
    for model in MODEL_ORDER:
        row = next(item for item in report["rows"] if item["model"] == model)
        delta = report["deltas_vs_LCDM"].get(model)
        suffix = "" if delta is None else f" dBIC={delta['delta_BIC']:.6f}"
        print(f"{model}: chi2={row['chi2']:.6f} BIC={row['BIC']:.6f}{suffix} boundary={row['boundary_hits']}")
    print("claim_allowed=false")
    if args.require_pass and report["state"] != "PASS_LIMITED_G4_BACKGROUND_TOURNAMENT":
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
