"""Joint real-data likelihood for the RLL cosmology validation stack.

This module intentionally keeps the current repository data local-first: it uses
materialized an independent cosmic-chronometer H(z) partition, DESI DR2 BAO primary points, the real fσ8 compilation, and the Planck
CMB-shift summary already committed under ``data/``.  It does not download or
invent missing data; when only a published covariance summary is present, the
BAO covariance is built from the committed diagonal errors plus the committed
same-tracer DM/DH correlations.
"""

from __future__ import annotations

import csv
import hashlib
import importlib.util
import json
import os
import subprocess
import sys
import time
from pathlib import Path
from typing import Any, Callable

import numpy as np
import pandas as pd

_IMPORT_BASE_DIR = Path(__file__).resolve().parents[3]
_IMPORT_SRC_DIR = _IMPORT_BASE_DIR / "src"
if str(_IMPORT_SRC_DIR) not in sys.path:
    sys.path.insert(0, str(_IMPORT_SRC_DIR))

try:
    from scipy.integrate import quad
    from scipy.optimize import differential_evolution
except ImportError as exc:  # pragma: no cover - exercised by environment setup
    raise ImportError(
        "joint_real_likelihood requires SciPy. Install with `pip install -r requirements.txt`."
    ) from exc

from rll.cosmology_fairness import covariance_readiness, growth_backend_benchmark_status, load_parameter_origin_registry

from .energy_momentum_bridge import build_fnext_gate
from .likelihood import aic, aicc, bic, chi2_with_covariance
from .synthetic_real_boundary import CLAIM_BOUNDARY, enforce_claim_boundary, interpret_model_comparison

TEXTUAL_OUTPUTS = [
    "results/structure_d/joint_real_likelihood.csv",
    "results/structure_d/joint_real_likelihood.json",
    "results/structure_d/joint_real_likelihood_covariance_manifest.json",
    "results/audit/rll_model_evidence_scan.json",
    "results/audit/rll_model_evidence_scan.md",
]

BASE_DIR = Path(__file__).resolve().parents[3]
RESULTS = BASE_DIR / "results" / "structure_d"

HZ_PATH = BASE_DIR / "data" / "real" / "cosmology" / "Hz_cosmic_chronometers_independent.csv"
DESI_POINTS_PATH = BASE_DIR / "data" / "real" / "cosmology" / "desi_dr2_bao_primary_points.csv"
DESI_COV_SUMMARY_PATH = BASE_DIR / "data" / "real" / "cosmology" / "desi_dr2_bao_covariance_summary.csv"
DESI_FULL_COV_PATH = BASE_DIR / "data" / "real" / "desi_dr2_bao_covariance.csv"
PARAMETER_REGISTRY_PATH = BASE_DIR / "data" / "inputs" / "cosmology_joint" / "parameter_origin_registry.json"
FSIGMA8_PATH = BASE_DIR / "data" / "real" / "cosmology" / "fsigma8_growth_real.csv"
CMB_SHIFT_PATH = BASE_DIR / "data" / "real" / "CMB_shift_real.json"

C_KMS = 299792.458
ORAD = 9.0e-5
Z_CMB_DEFAULT = 1089.92
MODEL_LCDM = "LCDM_joint_real"
MODEL_WCDM = "wCDM_joint_real"
MODEL_CPL = "CPL_w0waCDM_joint_real"
MODEL_RLL = "RLL_joint_real"
MODEL_ORDER = (MODEL_LCDM, MODEL_WCDM, MODEL_CPL, MODEL_RLL)
MODEL_PARAM_NAMES = {
    MODEL_LCDM: ("H0", "Om", "OL", "Ob_h2", "sigma8"),
    MODEL_WCDM: ("H0", "Om", "OL", "w", "Ob_h2", "sigma8"),
    MODEL_CPL: ("H0", "Om", "OL", "w0", "wa", "Ob_h2", "sigma8"),
    MODEL_RLL: ("H0", "Om", "OL", "Os0", "zt", "wt", "Ob_h2", "sigma8"),
}
MODEL_BOUNDS = {
    MODEL_LCDM: [(60.0, 80.0), (0.10, 0.60), (0.40, 1.10), (0.018, 0.026), (0.50, 1.10)],
    MODEL_WCDM: [(60.0, 80.0), (0.10, 0.60), (0.40, 1.10), (-2.0, -0.3), (0.018, 0.026), (0.50, 1.10)],
    MODEL_CPL: [(60.0, 80.0), (0.10, 0.60), (0.40, 1.10), (-2.0, -0.3), (-3.0, 3.0), (0.018, 0.026), (0.50, 1.10)],
    MODEL_RLL: [(60.0, 80.0), (0.10, 0.60), (0.40, 1.10), (0.0, 0.25), (0.1, 10.0), (0.05, 2.0), (0.018, 0.026), (0.50, 1.10)],
}


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as fp:
        for chunk in iter(lambda: fp.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_sha() -> str | None:
    """Return the current HEAD commit SHA, or None if git is unavailable."""
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=BASE_DIR, text=True).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


# Registry-name aliases for parameters whose pipeline names differ from registry entries.
# 'OL' (Omega_Lambda, a free background parameter) resolves to the registry's 'Om' entry
# because the registry tracks the matter density concept and uses Omega_m as the canonical
# label for the matter/energy-budget parameters; OL is separately fitted and always counted.
# 'Ob_h2' is the pipeline label for the physical baryon density recorded as 'omega_b' in the
# registry (Omega_b h^2).
_K_ALIASES: dict[str, str] = {"OL": "Om", "Ob_h2": "omega_b"}

# Status prefix that marks a parameter as required in k.
_K_REQUIRED_PREFIX = "must_report_in_k"


def k_from_registry(param_names: tuple[str, ...], registry: dict) -> int:
    """Compute k from the parameter-origin registry for the given fitted parameter names.

    Every parameter in ``param_names`` is a free parameter being optimised.  This
    function looks each one up in the registry (applying ``_K_ALIASES`` when the
    pipeline name differs from the registry name) and counts those whose
    ``status`` begins with ``must_report_in_k``.  Parameters that are absent
    from the registry are counted conservatively so that k never underestimates
    the true model complexity.

    Registry ``name`` values are expected to be strings; any non-string value is
    coerced with ``str()`` to match the validation applied in
    ``_validate_model_parameter_registry``.
    """
    known = {str(p["name"]): p for p in registry.get("parameters", [])}
    count = 0
    for name in param_names:
        registry_name = _K_ALIASES.get(name, name)
        entry = known.get(registry_name)
        if entry is None:
            # Not found in registry: conservative fallback — count it in k.
            count += 1
            continue
        status = str(entry.get("status", ""))
        if status.startswith(_K_REQUIRED_PREFIX):
            count += 1
    return count


def _atomic_write_text(path: Path, text: str) -> dict[str, str | bool]:
    """Write with rollback marker: previous file is preserved as ``.bak`` first."""

    path.parent.mkdir(parents=True, exist_ok=True)
    backup = path.with_suffix(path.suffix + ".bak")
    tmp = path.with_suffix(path.suffix + f".tmp-{os.getpid()}")
    rollback_available = False
    if path.exists():
        backup.write_bytes(path.read_bytes())
        rollback_available = True
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)
    return {
        "path": str(path.relative_to(BASE_DIR)),
        "backup_path": str(backup.relative_to(BASE_DIR)) if rollback_available else "",
        "rollback_available": rollback_available,
    }


def transition_f(z: np.ndarray | float, zt: float, wt: float) -> np.ndarray:
    z_arr = np.asarray(z, dtype=float)
    width = max(float(wt), 1.0e-6)
    return 1.0 / (1.0 + np.exp(np.clip((z_arr - float(zt)) / width, -500.0, 500.0)))


def e2_lcdm(z: np.ndarray | float, h0: float, om: float, ol: float) -> np.ndarray:
    del h0  # kept in the signature to match the RLL callable interface
    z_arr = np.asarray(z, dtype=float)
    return om * (1.0 + z_arr) ** 3 + ORAD * (1.0 + z_arr) ** 4 + ol


def e2_wcdm(z: np.ndarray | float, h0: float, om: float, ol: float, w: float) -> np.ndarray:
    del h0
    z_arr = np.asarray(z, dtype=float)
    zp1 = 1.0 + z_arr
    return om * zp1**3 + ORAD * zp1**4 + ol * zp1 ** (3.0 * (1.0 + float(w)))


def e2_cpl(z: np.ndarray | float, h0: float, om: float, ol: float, w0: float, wa: float) -> np.ndarray:
    del h0
    z_arr = np.asarray(z, dtype=float)
    zp1 = 1.0 + z_arr
    dark_energy = zp1 ** (3.0 * (1.0 + float(w0) + float(wa))) * np.exp(-3.0 * float(wa) * z_arr / zp1)
    return om * zp1**3 + ORAD * zp1**4 + ol * dark_energy


def e2_rll(z: np.ndarray | float, h0: float, om: float, ol: float, os0: float, zt: float, wt: float) -> np.ndarray:
    del h0
    z_arr = np.asarray(z, dtype=float)
    fz = transition_f(z_arr, zt, wt)
    superposition = os0 * (fz + (1.0 - fz) * (1.0 + z_arr) ** 3)
    return om * (1.0 + z_arr) ** 3 + ORAD * (1.0 + z_arr) ** 4 + ol + superposition


def hz_from_e2(z: np.ndarray | float, e2_fn: Callable, params: tuple[float, ...]) -> np.ndarray:
    h0 = float(params[0])
    return h0 * np.sqrt(np.maximum(e2_fn(z, *params), 1.0e-12))


def rd_drag_mpc(h0: float, om: float, ob_h2: float) -> float:
    """Aubourg/Eisenstein-Hu style calibrated power-law r_d approximation.

    The repository previously fixed r_d.  This function derives it from the
    fitted physical matter and baryon densities, keeping a lightweight formula
    suitable for fast validation and explicit AIC/BIC comparisons.
    """

    om_h2 = float(om) * (float(h0) / 100.0) ** 2
    return float(147.78 * (om_h2 / 0.1432) ** (-0.255) * (float(ob_h2) / 0.02236) ** (-0.134))


def comoving_distance_mpc(z: float, e2_fn: Callable, params: tuple[float, ...], cache: dict | None = None) -> float:
    z_val = float(z)
    key = (e2_fn.__name__, z_val, tuple(float(x) for x in params))
    if cache is not None and key in cache:
        return float(cache[key])

    integrand = lambda zz: C_KMS / float(hz_from_e2(zz, e2_fn, params))
    value, _ = quad(integrand, 0.0, z_val, epsrel=1.0e-5, limit=200)
    if cache is not None:
        cache[key] = float(value)
    return float(value)


def bao_prediction(row: pd.Series, e2_fn: Callable, params: tuple[float, ...], ob_h2: float, cache: dict | None = None) -> float:
    z = float(row["z_eff"])
    dc = comoving_distance_mpc(z, e2_fn, params, cache=cache)
    hz = float(hz_from_e2(z, e2_fn, params))
    rd = rd_drag_mpc(params[0], params[1], ob_h2)
    observable = str(row["observable"])
    if observable == "DV_over_rd":
        dv = (z * C_KMS * dc * dc / hz) ** (1.0 / 3.0)
        return float(dv / rd)
    if observable == "DM_over_rd":
        return float(dc / rd)
    if observable == "DH_over_rd":
        return float((C_KMS / hz) / rd)
    raise ValueError(f"unsupported DESI BAO observable: {observable}")


def build_desi_covariance(points: pd.DataFrame, summary: pd.DataFrame) -> np.ndarray:
    cov = np.diag(points["sigma"].astype(float).to_numpy() ** 2)
    for _, block in summary.iterrows():
        block_name = str(block["covariance_block"])
        idx = points.index[points["covariance_block"] == block_name].tolist()
        if len(idx) != 2:
            raise ValueError(f"DESI covariance block {block_name} must map to exactly two rows")
        i, j = idx
        covariance = float(block["covariance"])
        cov[i, j] = covariance
        cov[j, i] = covariance
    return cov


def omega_m_z_from_e2(z: np.ndarray, e2_fn: Callable, params: tuple[float, ...]) -> np.ndarray:
    z_arr = np.asarray(z, dtype=float)
    om = float(params[1])
    return om * (1.0 + z_arr) ** 3 / np.maximum(e2_fn(z_arr, *params), 1.0e-12)


def fsigma8_prediction(z: np.ndarray, e2_fn: Callable, params: tuple[float, ...], sigma8: float) -> np.ndarray:
    return float(sigma8) * omega_m_z_from_e2(np.asarray(z, dtype=float), e2_fn, params) ** 0.55


def cmb_shift_prediction(e2_fn: Callable, params: tuple[float, ...], ob_h2: float, z_cmb: float, cache: dict | None = None) -> np.ndarray:
    """Predicted Planck-style compressed CMB distance priors [R, l_A, Ob_h2].

    Ob_h2 is itself one of the three compressed CMB parameters (Chen, Huang &
    Wang 2019); the model's own fitted Ob_h2 is its prediction for that slot.
    """

    dc = comoving_distance_mpc(z_cmb, e2_fn, params, cache=cache)
    r_shift = np.sqrt(float(params[1])) * float(params[0]) * dc / C_KMS
    acoustic_scale = np.pi * dc / rd_drag_mpc(params[0], params[1], ob_h2)
    return np.array([r_shift, acoustic_scale, float(ob_h2)], dtype=float)


def _chi2_diag(obs: np.ndarray, pred: np.ndarray, sigma: np.ndarray) -> float:
    return float(np.sum(((np.asarray(obs, dtype=float) - np.asarray(pred, dtype=float)) / np.asarray(sigma, dtype=float)) ** 2))


def _cmb_chi2(cmb: dict, e2_fn: Callable, params: tuple[float, ...], ob_h2: float, cache: dict | None = None) -> float:
    """CMB chi2 term: full [R, l_A, Ob_h2] covariance when committed, else diagonal [R, l_A].

    The covariance-aware path uses the Planck 2018 (Chen, Huang & Wang 2019)
    compressed distance-prior covariance committed in CMB_shift_real.json. The
    diagonal fallback keeps older/minimal CMB fixtures (R, la only) working.
    """

    z_cmb = float(cmb.get("z_CMB", Z_CMB_DEFAULT))
    pred = cmb_shift_prediction(e2_fn, params, ob_h2, z_cmb, cache=cache)
    covariance = cmb.get("covariance")
    parameter_order = cmb.get("parameter_order")
    if covariance is not None and parameter_order == ["R", "la", "ob_h2"]:
        obs = np.array([float(cmb["R_obs"]), float(cmb["la_obs"]), float(cmb["ob_h2_obs"])], dtype=float)
        cov = np.asarray(covariance, dtype=float)
        return chi2_with_covariance(obs, pred, cov)

    obs = np.array([float(cmb["R_obs"]), float(cmb["la_obs"])], dtype=float)
    sig = np.array([float(cmb["R_sig"]), float(cmb["la_sig"])], dtype=float)
    return _chi2_diag(obs, pred[:2], sig)


def load_parameter_registry() -> dict:
    registry = json.loads(PARAMETER_REGISTRY_PATH.read_text(encoding="utf-8"))
    return load_parameter_origin_registry(registry)


def _registry_parameter_names(registry: dict) -> set[str]:
    return {str(item["name"]) for item in registry["parameters"]}


def _validate_model_parameter_registry(registry: dict) -> None:
    known_names = _registry_parameter_names(registry)
    aliases = {"OL": "Om", "Ob_h2": "omega_b"}
    missing: dict[str, list[str]] = {}
    for model, names in MODEL_PARAM_NAMES.items():
        absent = [name for name in names if aliases.get(name, name) not in known_names and name not in known_names]
        if absent:
            missing[model] = absent
    if missing:
        raise ValueError(f"parameter_origin_registry missing fitted parameters: {missing}")


def _load_desi_covariance(points: pd.DataFrame, summary: pd.DataFrame) -> tuple[np.ndarray, dict[str, object]]:
    if DESI_FULL_COV_PATH.exists():
        full_cov = pd.read_csv(DESI_FULL_COV_PATH, index_col=0).to_numpy(dtype=float)
        readiness = covariance_readiness(full_cov, mode="official_full")
        if readiness.ready and full_cov.shape == (len(points), len(points)):
            return full_cov, {
                "path": str(DESI_FULL_COV_PATH.relative_to(BASE_DIR)),
                "source_path": str(DESI_FULL_COV_PATH.relative_to(BASE_DIR)),
                "mode": readiness.mode,
                "ready": readiness.ready,
                "claim_allowed": readiness.claim_allowed,
                "reason": readiness.reason,
                "sha256": _sha256_file(DESI_FULL_COV_PATH),
                "metric": "chi2_with_covariance",
                "baseline": [MODEL_LCDM, MODEL_WCDM, MODEL_CPL],
                "uncertainty_or_covariance_status": "official_full_covariance_matrix",
                "command": "python -m data.pipelines.structure_d.joint_real_likelihood",
                "claim_boundary": (
                    "Covariance readiness is a technical evidence gate for using the official full "
                    "DESI DR2 BAO covariance in chi2_with_covariance; it does not by itself confirm or "
                    "validate RLL against LCDM/CPL."
                ),
            }
    block_cov = build_desi_covariance(points, summary)
    readiness = covariance_readiness(block_cov, mode="block_summary")
    return block_cov, {
        "path": str(DESI_COV_SUMMARY_PATH.relative_to(BASE_DIR)),
        "mode": readiness.mode,
        "ready": readiness.ready,
        "claim_allowed": readiness.claim_allowed,
        "reason": readiness.reason,
        "sha256": _sha256_file(DESI_COV_SUMMARY_PATH),
    }


def load_joint_inputs() -> dict:
    registry = load_parameter_registry()
    _validate_model_parameter_registry(registry)
    hz = pd.read_csv(HZ_PATH)
    desi = pd.read_csv(DESI_POINTS_PATH)
    desi_summary = pd.read_csv(DESI_COV_SUMMARY_PATH)
    fs8 = pd.read_csv(FSIGMA8_PATH)
    cmb = json.loads(CMB_SHIFT_PATH.read_text(encoding="utf-8"))
    desi_cov, covariance_info = _load_desi_covariance(desi, desi_summary)
    return {
        "hz": hz,
        "desi": desi,
        "desi_summary": desi_summary,
        "desi_cov": desi_cov,
        "desi_covariance_info": covariance_info,
        "fs8": fs8,
        "cmb": cmb,
        "parameter_registry": registry,
    }


def _model_runtime(model: str, vector: np.ndarray) -> tuple[Callable, tuple[float, ...], float, float, float, dict[str, float]]:
    if model == MODEL_LCDM:
        h0, om, ol, ob_h2, sigma8 = vector
        return e2_lcdm, (h0, om, ol), h0, ob_h2, sigma8, {}
    if model == MODEL_WCDM:
        h0, om, ol, w, ob_h2, sigma8 = vector
        return e2_wcdm, (h0, om, ol, w), h0, ob_h2, sigma8, {"w": w}
    if model == MODEL_CPL:
        h0, om, ol, w0, wa, ob_h2, sigma8 = vector
        return e2_cpl, (h0, om, ol, w0, wa), h0, ob_h2, sigma8, {"w0": w0, "wa": wa}
    if model == MODEL_RLL:
        h0, om, ol, os0, zt, wt, ob_h2, sigma8 = vector
        return e2_rll, (h0, om, ol, os0, zt, wt), h0, ob_h2, sigma8, {"Os0": os0, "zt": zt, "wt": wt}
    raise ValueError(f"unknown model: {model}")


def evaluate_components(model: str, vector: np.ndarray, inputs: dict) -> dict[str, float]:
    vector = np.asarray(vector, dtype=float)
    e2_fn, params, h0, ob_h2, sigma8, _extra = _model_runtime(model, vector)
    om = float(params[1])
    ol = float(params[2])

    if h0 <= 0.0 or om <= 0.0 or ol <= 0.0 or ob_h2 <= 0.0 or sigma8 <= 0.0:
        return {"total": float("inf")}
    if np.any(e2_fn(np.array([0.0, 2.5, Z_CMB_DEFAULT]), *params) <= 0.0):
        return {"total": float("inf")}

    cache: dict = {}
    hz_df = inputs["hz"]
    hz_pred = hz_from_e2(hz_df["z"].to_numpy(dtype=float), e2_fn, params)
    chi2_hz = _chi2_diag(hz_df["H_obs"].to_numpy(dtype=float), hz_pred, hz_df["sigma_H"].to_numpy(dtype=float))

    desi_df = inputs["desi"]
    bao_pred = np.array([bao_prediction(row, e2_fn, params, ob_h2, cache=cache) for _, row in desi_df.iterrows()])
    chi2_bao = chi2_with_covariance(desi_df["value"].to_numpy(dtype=float), bao_pred, inputs["desi_cov"])

    fs8_df = inputs["fs8"]
    fs8_pred = fsigma8_prediction(fs8_df["z"].to_numpy(dtype=float), e2_fn, params, sigma8)
    chi2_fs8 = _chi2_diag(fs8_df["fs8"].to_numpy(dtype=float), fs8_pred, fs8_df["sigma"].to_numpy(dtype=float))

    chi2_cmb = _cmb_chi2(inputs["cmb"], e2_fn, params, ob_h2, cache=cache)

    total = chi2_hz + chi2_bao + chi2_fs8 + chi2_cmb
    return {
        "Hz": float(chi2_hz),
        "DESI_DR2_BAO": float(chi2_bao),
        "fsigma8": float(chi2_fs8),
        "CMB_shift": float(chi2_cmb),
        "total": float(total),
    }


def fit_model(model: str, inputs: dict, seed: int, maxiter: int, tol: float) -> tuple[np.ndarray, dict[str, float]]:
    try:
        bounds = MODEL_BOUNDS[model]
    except KeyError as exc:
        raise ValueError(f"unknown model: {model}") from exc

    result = differential_evolution(
        lambda values: evaluate_components(model, values, inputs)["total"],
        bounds,
        seed=seed,
        maxiter=maxiter,
        tol=tol,
        workers=1,
        polish=True,
    )
    return np.asarray(result.x, dtype=float), evaluate_components(model, result.x, inputs)


def _json_safe(value):
    if isinstance(value, dict):
        return {key: _json_safe(item) for key, item in value.items()}
    if isinstance(value, list):
        return [_json_safe(item) for item in value]
    if isinstance(value, tuple):
        return [_json_safe(item) for item in value]
    if isinstance(value, np.generic):
        value = value.item()
    if isinstance(value, float) and not np.isfinite(value):
        return None
    return value


def _rows_to_csv(rows: list[dict]) -> str:
    fieldnames = list(rows[0].keys())
    from io import StringIO

    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=fieldnames, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()



def _model_specific_values(model: str, vector: np.ndarray) -> dict[str, float]:
    values = {name: np.nan for name in ("w", "w0", "wa", "Os0", "zt", "wt")}
    for name, value in zip(MODEL_PARAM_NAMES[model], vector):
        if name in values:
            values[name] = float(value)
    return values


def _model_row(
    model: str,
    vector: np.ndarray,
    components: dict[str, float],
    n_obs: int,
    registry: dict | None = None,
    commit_sha: str | None = None,
) -> dict[str, float | int | str | None]:
    """Build a result row for one model fit.

    When *registry* is provided, ``k`` is derived from the parameter-origin
    registry via :func:`k_from_registry` so that every fitted/free/nuisance
    parameter counted by the registry is included.  This makes ``k``, and
    therefore AIC/AICc/BIC, registry-driven rather than hard-coded.

    ``registry_schema`` and ``commit_sha`` are embedded in each row so that
    downstream consumers can audit the provenance of information criteria
    without consulting a separate metadata file.
    """
    vector = np.asarray(vector, dtype=float)
    param_names = MODEL_PARAM_NAMES[model]
    if registry is not None:
        k = k_from_registry(param_names, registry)
    else:
        k = len(param_names)
    registry_schema = registry.get("schema") if registry is not None else None
    base: dict[str, float | int | str | None] = {
        "model": model,
        "chi2": components["total"],
        "AIC": aic(components["total"], k),
        "AICc": aicc(components["total"], k, n_obs),
        "BIC": bic(components["total"], k, n_obs),
        "N": n_obs,
        "k": k,
        "dof": n_obs - k,
        "registry_schema": registry_schema,
        "commit_sha": commit_sha,
        "chi2_Hz": components["Hz"],
        "chi2_DESI_DR2_BAO": components["DESI_DR2_BAO"],
        "chi2_fsigma8": components["fsigma8"],
        "chi2_CMB_shift": components["CMB_shift"],
        "H0": float(vector[0]),
        "Om": float(vector[1]),
        "OL": float(vector[2]),
        "Ob_h2": float(vector[-2]),
        "sigma8": float(vector[-1]),
    }
    base.update(_model_specific_values(model, vector))
    return base


def _delta_against(rows_by_model: dict[str, dict], model: str, baseline: str = MODEL_LCDM) -> dict[str, float]:
    row = rows_by_model[model]
    base = rows_by_model[baseline]
    slug = model.replace("_joint_real", "").replace("_w0waCDM", "").lower()
    return {
        f"delta_chi2_{slug}_minus_lcdm": row["chi2"] - base["chi2"],
        f"delta_aic_{slug}_minus_lcdm": row["AIC"] - base["AIC"],
        f"delta_aicc_{slug}_minus_lcdm": row["AICc"] - base["AICc"],
        f"delta_bic_{slug}_minus_lcdm": row["BIC"] - base["BIC"],
    }

def run_joint_likelihood(output_stem: str = "joint_real_likelihood") -> dict:
    start = time.perf_counter()
    inputs = load_joint_inputs()
    seed = int(os.environ.get("STRUCTURE_D_JOINT_SEED", "42"))
    tol = float(os.environ.get("STRUCTURE_D_JOINT_TOL", "1e-6"))
    default_maxiter = int(os.environ.get("STRUCTURE_D_JOINT_MAXITER", "140"))
    maxiter_by_model = {
        MODEL_LCDM: int(os.environ.get("STRUCTURE_D_JOINT_MAXITER_LCDM", str(default_maxiter))),
        MODEL_WCDM: int(os.environ.get("STRUCTURE_D_JOINT_MAXITER_WCDM", str(default_maxiter))),
        MODEL_CPL: int(os.environ.get("STRUCTURE_D_JOINT_MAXITER_CPL", str(default_maxiter))),
        MODEL_RLL: int(os.environ.get("STRUCTURE_D_JOINT_MAXITER_RLL", str(default_maxiter))),
    }

    fitted: dict[str, tuple[np.ndarray, dict[str, float]]] = {}
    for offset, model in enumerate(MODEL_ORDER):
        fitted[model] = fit_model(model, inputs, seed + offset, maxiter_by_model[model], tol)

    registry = inputs["parameter_registry"]
    commit_sha = _git_sha()
    n_obs = int(len(inputs["hz"]) + len(inputs["desi"]) + len(inputs["fs8"]) + 2)
    rows = [_model_row(model, fitted[model][0], fitted[model][1], n_obs, registry=registry, commit_sha=commit_sha) for model in MODEL_ORDER]
    rows_by_model = {row["model"]: row for row in rows}
    rll_delta = _delta_against(rows_by_model, MODEL_RLL)
    model_deltas = {model: _delta_against(rows_by_model, model) for model in (MODEL_WCDM, MODEL_CPL, MODEL_RLL)}
    growth_benchmark = growth_backend_benchmark_status(require_external=True)

    outputs = []
    outputs.append(_atomic_write_text(RESULTS / f"{output_stem}.csv", _rows_to_csv(rows)))

    # Run the evidence scanner immediately after the CSV is written so that
    # audit outputs are always current when the pipeline produces a new result.
    evidence_scan = _run_evidence_scan(RESULTS / f"{output_stem}.csv", PARAMETER_REGISTRY_PATH)
    # Only append scan output paths to the outputs list for the canonical run.
    if output_stem == _CANONICAL_STEM:
        outputs.append({"path": evidence_scan["scan_json"], "backup_path": "", "rollback_available": False})
        outputs.append({"path": evidence_scan["scan_md"], "backup_path": "", "rollback_available": False})

    payload = {
        "schema": "rll.joint_real_likelihood.v2",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runtime_seconds": time.perf_counter() - start,
        "optimizer": {
            "name": "scipy.optimize.differential_evolution",
            "seed": seed,
            "tol": tol,
            "maxiter_by_model": maxiter_by_model,
            "models": list(MODEL_ORDER),
        },
        "datasets": {
            "Hz": str(HZ_PATH.relative_to(BASE_DIR)),
            "DESI_DR2_BAO_primary": str(DESI_POINTS_PATH.relative_to(BASE_DIR)),
            "DESI_DR2_BAO_covariance": inputs["desi_covariance_info"]["path"],
            "fsigma8": str(FSIGMA8_PATH.relative_to(BASE_DIR)),
            "CMB_shift": str(CMB_SHIFT_PATH.relative_to(BASE_DIR)),
            "parameter_origin_registry": str(PARAMETER_REGISTRY_PATH.relative_to(BASE_DIR)),
        },
        "rd_policy": "derived_power_law_from_H0_Om_Ob_h2_for_all_models",
        "bao_covariance_policy": inputs["desi_covariance_info"],
        "cmb_covariance_policy": {
            "path": str(CMB_SHIFT_PATH.relative_to(BASE_DIR)),
            "mode": "full_3x3_R_la_Ob_h2" if inputs["cmb"].get("covariance") else "diagonal_R_la_only",
            "primary_source": inputs["cmb"].get("primary_source", {}),
            "sha256": _sha256_file(CMB_SHIFT_PATH),
        },
        "growth_benchmark": growth_benchmark,
        "parameter_registry_policy": {
            "path": str(PARAMETER_REGISTRY_PATH.relative_to(BASE_DIR)),
            "schema": registry.get("schema"),
            "required_before_information_criteria": True,
            "sha256": _sha256_file(PARAMETER_REGISTRY_PATH),
            "commit_sha": commit_sha,
            "k_derivation": "registry_driven",
        },
        "covariance_claim_gates": {
            "desi_bao_claim_allowed": inputs["desi_covariance_info"].get("claim_allowed", False),
            "desi_bao_mode": inputs["desi_covariance_info"].get("mode", "unknown"),
            "cmb_claim_allowed": bool(inputs["cmb"].get("covariance")),
            "cmb_mode": "full_3x3_R_la_Ob_h2" if inputs["cmb"].get("covariance") else "diagonal_R_la_only",
            "growth_claim_allowed": bool(growth_benchmark.get("claim_allowed", False)),
            "growth_status": growth_benchmark.get("status", "unknown"),
            "fsigma8_claim_blocked_reason": (
                None if bool(growth_benchmark.get("claim_allowed", False))
                else "CLASS/CAMB backend absent; fσ8 remains an internal approximation proxy"
            ),
        },
        "dataset_type": "real_observational",
        "claim_boundary": CLAIM_BOUNDARY,
        "claim_allowed": False,
        "publication_language": "RLL is a candidate effective dynamic-transition cosmology under real-data evaluation.",
        "interpretation_label": interpret_model_comparison(rll_delta, "real_observational")["interpretation_label"],
        "claim_policy": enforce_claim_boundary("real_observational", rll_delta),
        "model_deltas_vs_lcdm": _json_safe(model_deltas),
        "fnext": _json_safe(build_fnext_gate(rll_delta)),
        "rows": _json_safe(rows),
        "evidence_scan": _json_safe(evidence_scan),
    }
    outputs.append(_atomic_write_text(RESULTS / f"{output_stem}.json", json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n"))

    manifest = {
        "schema": "rll.joint_real_likelihood.covariance_manifest.v2",
        "desi_covariance_shape": list(inputs["desi_cov"].shape),
        "desi_covariance_sha256": hashlib.sha256(inputs["desi_cov"].astype("<f8").tobytes()).hexdigest(),
        "desi_covariance_readiness": inputs["desi_covariance_info"],
        "growth_benchmark": growth_benchmark,
        "input_sha256": {},
        "failsafe": {
            "atomic_write": True,
            "backup_before_replace": True,
            "rollback_instruction": "copy any non-empty *.bak file over the corresponding output if a downstream check fails",
            "raw_datasets_modified": False,
        },
    }
    # Normalize any relative covariance path used in the hash manifest.
    manifest["input_sha256"] = {
        str(path.relative_to(BASE_DIR)): _sha256_file(path)
        for path in [
            HZ_PATH,
            DESI_POINTS_PATH,
            BASE_DIR / inputs["desi_covariance_info"]["path"],
            FSIGMA8_PATH,
            CMB_SHIFT_PATH,
            PARAMETER_REGISTRY_PATH,
        ]
    }
    outputs.append(
        _atomic_write_text(
            RESULTS / f"{output_stem}_covariance_manifest.json",
            json.dumps(manifest, ensure_ascii=False, indent=2) + "\n",
        )
    )
    payload["outputs"] = outputs
    return payload

_OUTPUT_STEM_ENV = "STRUCTURE_D_JOINT_OUTPUT_STEM"
_DEFAULT_OUTPUT_STEM = "joint_real_likelihood"
_CANONICAL_STEM = "joint_real_likelihood"
_SAFE_STEM_CHARS = frozenset(
    "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789_-"
)


def _resolve_main_output_stem() -> str:
    """Read STRUCTURE_D_JOINT_OUTPUT_STEM from environment, falling back to the canonical default.

    When this module is executed directly (e.g. ``python -m data.pipelines.structure_d.joint_real_likelihood``),
    this function ensures the same stem-override contract that ``scripts/run_structure_d_joint_likelihood.py``
    exposes is also respected, preventing accidental canonical-artifact overwrites during robust-fit runs.
    """
    raw = os.environ.get(_OUTPUT_STEM_ENV, _DEFAULT_OUTPUT_STEM).strip()
    if not raw:
        return _CANONICAL_STEM
    # Reject absolute paths, path separators, traversal components, and extensions.
    if raw.startswith(("/", "\\")) or raw in {".", ".."}:
        return _CANONICAL_STEM
    if "/" in raw or "\\" in raw:
        return _CANONICAL_STEM
    if raw.endswith((".json", ".csv", ".tsv")):
        return _CANONICAL_STEM
    # Restrict to a safe character set to prevent shell injection or unexpected
    # filesystem behaviour when the stem is used directly in filenames.
    if not all(c in _SAFE_STEM_CHARS for c in raw):
        return _CANONICAL_STEM
    return raw


def main() -> dict:
    output_stem = _resolve_main_output_stem()
    payload = run_joint_likelihood(output_stem=output_stem)
    print(pd.DataFrame(payload["rows"]).to_string(index=False))
    for output in payload["outputs"]:
        print(f"Wrote: {output['path']}")
    return payload


if __name__ == "__main__":
    main()
