"""Shadow benchmark for structurally distinct cosmological background models.

This module intentionally does NOT overwrite the canonical joint-real likelihood.
It compares the same materialized H(z) and DESI DR2 BAO inputs under a
predeclared model registry. CMB acoustic-scale and fσ8 terms are excluded until
model-consistent sound-horizon and perturbation backends are available.

Scientific boundary: every emitted result has claim_allowed=false.
"""

from __future__ import annotations

import csv
import hashlib
import json
import math
import os
import subprocess
import time
from dataclasses import dataclass
from io import StringIO
from pathlib import Path
from typing import Any

import numpy as np
import pandas as pd

try:
    from scipy.integrate import quad
    from scipy.optimize import differential_evolution
except ImportError as exc:  # pragma: no cover
    raise ImportError(
        "model_family_shadow requires SciPy. Install with `pip install -r requirements.txt`."
    ) from exc

from .likelihood import aic, aicc, bic, chi2_with_covariance

BASE_DIR = Path(__file__).resolve().parents[3]
CONTRACT_PATH = BASE_DIR / "data" / "contracts" / "cosmology_model_family_shadow.v1.json"
HZ_PATH = BASE_DIR / "data" / "real" / "Hz_data_real.csv"
DESI_POINTS_PATH = BASE_DIR / "data" / "real" / "cosmology" / "desi_dr2_bao_primary_points.csv"
DESI_COV_SUMMARY_PATH = BASE_DIR / "data" / "real" / "cosmology" / "desi_dr2_bao_covariance_summary.csv"
DESI_FULL_COV_PATH = BASE_DIR / "data" / "real" / "desi_dr2_bao_covariance.csv"
RESULTS_DIR = BASE_DIR / "results" / "structure_d"

C_KMS = 299792.458
ORAD = 9.0e-5
OUTPUT_STEM = "model_family_shadow"
CORE_MODEL_IDS = (
    "FLCDM",
    "oLCDM",
    "wCDM",
    "CPL",
    "JBP",
    "BA",
    "PEDE",
    "FSLL1",
    "GCG",
    "RLL",
)
COMPOSITION_MODEL_IDS = (
    "RLL_wCDM",
    "RLL_CPL",
    "RLL_JBP",
    "RLL_BA",
    "RLL_PEDE",
)


@dataclass(frozen=True)
class ModelSpec:
    model_id: str
    kind: str
    geometry: str
    kernel: str
    parameter_names: tuple[str, ...]
    bounds: tuple[tuple[float, float], ...]
    sources: tuple[str, ...]

    @property
    def k(self) -> int:
        return len(self.parameter_names)


def load_contract(path: Path = CONTRACT_PATH) -> dict[str, Any]:
    payload = json.loads(path.read_text(encoding="utf-8"))
    if payload.get("schema") != "rll.cosmology_model_family_shadow.v1":
        raise ValueError("unexpected model-family contract schema")
    if payload.get("claim_allowed") is not False:
        raise ValueError("shadow model-family contract must remain claim_allowed=false")
    return payload


def load_model_specs(contract: dict[str, Any] | None = None) -> dict[str, ModelSpec]:
    contract = contract or load_contract()
    specs: dict[str, ModelSpec] = {}
    for raw in contract["models"]:
        model_id = str(raw["id"])
        if model_id in specs:
            raise ValueError(f"duplicate model id: {model_id}")
        names: list[str] = []
        bounds: list[tuple[float, float]] = []
        for item in raw["parameters"]:
            name = str(item["name"])
            if name in names:
                raise ValueError(f"duplicate parameter {name} in {model_id}")
            low, high = (float(item["bounds"][0]), float(item["bounds"][1]))
            if not math.isfinite(low) or not math.isfinite(high) or not low < high:
                raise ValueError(f"invalid bounds for {model_id}.{name}")
            names.append(name)
            bounds.append((low, high))
        specs[model_id] = ModelSpec(
            model_id=model_id,
            kind=str(raw["kind"]),
            geometry=str(raw["geometry"]),
            kernel=str(raw["kernel"]),
            parameter_names=tuple(names),
            bounds=tuple(bounds),
            sources=tuple(str(x) for x in raw.get("sources", [])),
        )
    expected = set(CORE_MODEL_IDS) | set(COMPOSITION_MODEL_IDS)
    if set(specs) != expected:
        missing = sorted(expected - set(specs))
        extra = sorted(set(specs) - expected)
        raise ValueError(f"model registry mismatch: missing={missing}, extra={extra}")
    return specs


def vector_to_params(
    spec: ModelSpec,
    vector: np.ndarray | list[float] | tuple[float, ...],
) -> dict[str, float]:
    values = np.asarray(vector, dtype=float)
    if values.shape != (spec.k,):
        raise ValueError(f"{spec.model_id} expects {spec.k} parameters, got {values.shape}")
    return {name: float(value) for name, value in zip(spec.parameter_names, values)}


def _transition_f(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    width = max(float(wt), 1.0e-9)
    return 1.0 / (1.0 + np.exp(np.clip((z - float(zt)) / width, -500.0, 500.0)))


def _rll_factor(z: np.ndarray, zt: float, wt: float) -> np.ndarray:
    fz = _transition_f(z, zt, wt)
    return fz + (1.0 - fz) * (1.0 + z) ** 3


def _de_factor(kernel: str, z: np.ndarray, p: dict[str, float]) -> np.ndarray:
    zp1 = 1.0 + z
    if kernel in {"lcdm", "rll_lambda"}:
        return np.ones_like(z)
    if kernel in {"wcdm", "rll_wcdm"}:
        return zp1 ** (3.0 * (1.0 + p["w"]))
    if kernel in {"cpl", "rll_cpl"}:
        return zp1 ** (3.0 * (1.0 + p["w0"] + p["wa"])) * np.exp(
            -3.0 * p["wa"] * z / zp1
        )
    if kernel in {"jbp", "rll_jbp"}:
        return zp1 ** (3.0 * (1.0 + p["w0"])) * np.exp(
            1.5 * p["wa"] * (z / zp1) ** 2
        )
    if kernel in {"ba", "rll_ba"}:
        return zp1 ** (3.0 * (1.0 + p["w0"])) * (1.0 + z * z) ** (1.5 * p["wa"])
    if kernel == "fsll1":
        integral = (
            -0.5 * np.log(zp1)
            + 0.25 * np.log1p(z * z)
            + 0.5 * np.arctan(z)
        )
        return zp1 ** (3.0 * (1.0 + p["w0"])) * np.exp(3.0 * p["wa"] * integral)
    if kernel in {"pede", "rll_pede"}:
        return 1.0 - np.tanh(np.log10(zp1))
    if kernel == "gcg":
        alpha = p["alpha"]
        exponent = 1.0 / (1.0 + alpha)
        interior = p["As"] + (1.0 - p["As"]) * zp1 ** (3.0 * (1.0 + alpha))
        return np.maximum(interior, 1.0e-300) ** exponent
    raise ValueError(f"kernel has no direct dark-energy factor: {kernel}")


def e2_for_model(
    spec: ModelSpec,
    z: np.ndarray | float,
    vector: np.ndarray | list[float] | tuple[float, ...],
) -> np.ndarray:
    z_arr = np.asarray(z, dtype=float)
    if np.any(z_arr < 0.0):
        raise ValueError("shadow benchmark currently supports z >= 0 only")
    p = vector_to_params(spec, vector)
    om = p["Om"]
    zp1 = 1.0 + z_arr

    if spec.geometry == "curved":
        ok = p["Ok"]
        ode0 = 1.0 - ORAD - om - ok
        e2 = om * zp1**3 + ORAD * zp1**4 + ok * zp1**2 + ode0
    elif spec.kernel.startswith("rll_"):
        os0 = p["Os0"]
        ode0 = 1.0 - ORAD - om - os0
        factor = _de_factor(spec.kernel, z_arr, p)
        e2 = (
            om * zp1**3
            + ORAD * zp1**4
            + ode0 * factor
            + os0 * _rll_factor(z_arr, p["zt"], p["wt"])
        )
    elif spec.kernel == "rll_lambda":
        os0 = p["Os0"]
        ode0 = 1.0 - ORAD - om - os0
        e2 = (
            om * zp1**3
            + ORAD * zp1**4
            + ode0
            + os0 * _rll_factor(z_arr, p["zt"], p["wt"])
        )
    else:
        ode0 = 1.0 - ORAD - om
        e2 = om * zp1**3 + ORAD * zp1**4 + ode0 * _de_factor(spec.kernel, z_arr, p)

    return np.asarray(e2, dtype=float)


def closure_fractions(
    spec: ModelSpec,
    vector: np.ndarray | list[float] | tuple[float, ...],
) -> dict[str, float]:
    p = vector_to_params(spec, vector)
    fractions = {"Omega_r0": ORAD, "Omega_m0": p["Om"]}
    if spec.geometry == "curved":
        fractions["Omega_k0"] = p["Ok"]
        fractions["Omega_de0"] = 1.0 - ORAD - p["Om"] - p["Ok"]
    elif spec.kernel.startswith("rll_") or spec.kernel == "rll_lambda":
        fractions["Omega_rll0"] = p["Os0"]
        fractions["Omega_de0"] = 1.0 - ORAD - p["Om"] - p["Os0"]
    else:
        fractions["Omega_de0"] = 1.0 - ORAD - p["Om"]
    return fractions


def is_physically_admissible(
    spec: ModelSpec,
    vector: np.ndarray | list[float] | tuple[float, ...],
) -> bool:
    fractions = closure_fractions(spec, vector)
    if fractions["Omega_m0"] <= 0.0 or fractions.get("Omega_de0", 0.0) <= 0.0:
        return False
    if spec.kernel.startswith("rll_") or spec.kernel == "rll_lambda":
        if fractions.get("Omega_rll0", -1.0) < 0.0:
            return False
    grid = np.array([0.0, 0.25, 0.5, 1.0, 2.5, 10.0, 1089.92])
    e2 = e2_for_model(spec, grid, vector)
    return bool(
        np.all(np.isfinite(e2))
        and np.all(e2 > 0.0)
        and abs(float(e2[0]) - 1.0) < 1.0e-8
    )


def hubble_km_s_mpc(spec: ModelSpec, z: np.ndarray | float, vector: np.ndarray) -> np.ndarray:
    p = vector_to_params(spec, vector)
    return p["H0"] * np.sqrt(np.maximum(e2_for_model(spec, z, vector), 1.0e-300))


def _dimensionless_radial_distance(spec: ModelSpec, z: float, vector: np.ndarray) -> float:
    value, _ = quad(
        lambda zz: 1.0 / math.sqrt(float(e2_for_model(spec, zz, vector))),
        0.0,
        float(z),
        epsrel=1.0e-5,
        limit=200,
    )
    return float(value)


def transverse_comoving_distance_mpc(spec: ModelSpec, z: float, vector: np.ndarray) -> float:
    p = vector_to_params(spec, vector)
    chi = _dimensionless_radial_distance(spec, z, vector)
    dh = C_KMS / p["H0"]
    ok = p.get("Ok", 0.0)
    if abs(ok) < 1.0e-10:
        return dh * chi
    root = math.sqrt(abs(ok))
    if ok > 0.0:
        return dh * math.sinh(root * chi) / root
    return dh * math.sin(root * chi) / root


def rd_drag_mpc(h0: float, om: float, ob_h2: float) -> float:
    om_h2 = float(om) * (float(h0) / 100.0) ** 2
    return float(
        147.78
        * (om_h2 / 0.1432) ** (-0.255)
        * (float(ob_h2) / 0.02236) ** (-0.134)
    )


def bao_prediction(row: pd.Series, spec: ModelSpec, vector: np.ndarray) -> float:
    p = vector_to_params(spec, vector)
    z = float(row["z_eff"])
    dm = transverse_comoving_distance_mpc(spec, z, vector)
    hz = float(hubble_km_s_mpc(spec, z, vector))
    rd = rd_drag_mpc(p["H0"], p["Om"], p["Ob_h2"])
    observable = str(row["observable"])
    if observable == "DV_over_rd":
        dv = (z * C_KMS * dm * dm / hz) ** (1.0 / 3.0)
        return float(dv / rd)
    if observable == "DM_over_rd":
        return float(dm / rd)
    if observable == "DH_over_rd":
        return float((C_KMS / hz) / rd)
    raise ValueError(f"unsupported DESI BAO observable: {observable}")


def _build_block_covariance(points: pd.DataFrame, summary: pd.DataFrame) -> np.ndarray:
    cov = np.diag(points["sigma"].astype(float).to_numpy() ** 2)
    for _, block in summary.iterrows():
        block_name = str(block["covariance_block"])
        idx = points.index[points["covariance_block"] == block_name].tolist()
        if len(idx) != 2:
            raise ValueError(f"DESI covariance block {block_name} must map to two rows")
        i, j = idx
        covariance = float(block["covariance"])
        cov[i, j] = covariance
        cov[j, i] = covariance
    return cov


def load_background_inputs() -> dict[str, Any]:
    hz = pd.read_csv(HZ_PATH)
    desi = pd.read_csv(DESI_POINTS_PATH)
    summary = pd.read_csv(DESI_COV_SUMMARY_PATH)
    if DESI_FULL_COV_PATH.exists():
        full = pd.read_csv(DESI_FULL_COV_PATH, index_col=0).to_numpy(dtype=float)
        if full.shape == (len(desi), len(desi)) and np.all(np.isfinite(full)):
            cov = full
            cov_mode = "official_full"
            cov_path = DESI_FULL_COV_PATH
        else:
            cov = _build_block_covariance(desi, summary)
            cov_mode = "block_summary_fallback"
            cov_path = DESI_COV_SUMMARY_PATH
    else:
        cov = _build_block_covariance(desi, summary)
        cov_mode = "block_summary"
        cov_path = DESI_COV_SUMMARY_PATH
    return {
        "hz": hz,
        "desi": desi,
        "desi_cov": cov,
        "covariance_mode": cov_mode,
        "covariance_path": cov_path,
    }


def _chi2_diag(obs: np.ndarray, pred: np.ndarray, sigma: np.ndarray) -> float:
    return float(np.sum(((obs - pred) / sigma) ** 2))


def evaluate_background_components(
    spec: ModelSpec,
    vector: np.ndarray,
    inputs: dict[str, Any],
) -> dict[str, float]:
    if not is_physically_admissible(spec, vector):
        return {"total": float("inf")}
    hz = inputs["hz"]
    hz_pred = hubble_km_s_mpc(spec, hz["z"].to_numpy(dtype=float), vector)
    chi2_hz = _chi2_diag(
        hz["H_obs"].to_numpy(dtype=float),
        hz_pred,
        hz["sigma_H"].to_numpy(dtype=float),
    )
    desi = inputs["desi"]
    bao_pred = np.array([bao_prediction(row, spec, vector) for _, row in desi.iterrows()])
    chi2_bao = chi2_with_covariance(
        desi["value"].to_numpy(dtype=float),
        bao_pred,
        inputs["desi_cov"],
    )
    return {
        "Hz": float(chi2_hz),
        "DESI_DR2_BAO": float(chi2_bao),
        "total": float(chi2_hz + chi2_bao),
    }


def fit_model(
    spec: ModelSpec,
    inputs: dict[str, Any],
    seed: int,
    maxiter: int,
    tol: float,
) -> tuple[np.ndarray, dict[str, float]]:
    result = differential_evolution(
        lambda vector: evaluate_background_components(
            spec,
            np.asarray(vector, dtype=float),
            inputs,
        )["total"],
        spec.bounds,
        seed=int(seed),
        maxiter=int(maxiter),
        tol=float(tol),
        workers=1,
        polish=True,
    )
    vector = np.asarray(result.x, dtype=float)
    return vector, evaluate_background_components(spec, vector, inputs)


def _sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _git_sha() -> str | None:
    try:
        return subprocess.check_output(
            ["git", "rev-parse", "HEAD"],
            cwd=BASE_DIR,
            text=True,
        ).strip()
    except (subprocess.CalledProcessError, FileNotFoundError, OSError):
        return None


def _atomic_write(path: Path, text: str) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    tmp = path.with_suffix(path.suffix + f".tmp-{os.getpid()}")
    tmp.write_text(text, encoding="utf-8")
    os.replace(tmp, path)


def _rows_to_csv(rows: list[dict[str, Any]]) -> str:
    names: list[str] = []
    for row in rows:
        for key in row:
            if key not in names:
                names.append(key)
    buf = StringIO()
    writer = csv.DictWriter(buf, fieldnames=names, lineterminator="\n")
    writer.writeheader()
    writer.writerows(rows)
    return buf.getvalue()


def _selected_model_ids(mode: str) -> tuple[str, ...]:
    normalized = mode.strip().lower()
    if normalized == "core":
        return CORE_MODEL_IDS
    if normalized == "compositions":
        return COMPOSITION_MODEL_IDS
    if normalized == "all":
        return CORE_MODEL_IDS + COMPOSITION_MODEL_IDS
    raise ValueError("mode must be one of: core, compositions, all")


def run_shadow_benchmark(
    mode: str = "all",
    seed: int | None = None,
    maxiter: int | None = None,
    tol: float | None = None,
) -> dict[str, Any]:
    started = time.perf_counter()
    contract = load_contract()
    specs = load_model_specs(contract)
    inputs = load_background_inputs()
    seed = int(seed if seed is not None else os.environ.get("RLL_MODEL_FAMILY_SEED", "11"))
    maxiter = int(
        maxiter
        if maxiter is not None
        else os.environ.get(
            "RLL_MODEL_FAMILY_MAXITER",
            str(contract["execution_policy"]["default_maxiter"]),
        )
    )
    tol = float(
        tol
        if tol is not None
        else os.environ.get(
            "RLL_MODEL_FAMILY_TOL",
            str(contract["execution_policy"]["default_tol"]),
        )
    )

    selected = _selected_model_ids(mode)
    n_obs = int(len(inputs["hz"]) + len(inputs["desi"]))
    rows: list[dict[str, Any]] = []
    for model_id in selected:
        spec = specs[model_id]
        vector, components = fit_model(spec, inputs, seed, maxiter, tol)
        params = vector_to_params(spec, vector)
        row: dict[str, Any] = {
            "model": model_id,
            "kind": spec.kind,
            "geometry": spec.geometry,
            "chi2": components["total"],
            "AIC": aic(components["total"], spec.k),
            "AICc": aicc(components["total"], spec.k, n_obs),
            "BIC": bic(components["total"], spec.k, n_obs),
            "N": n_obs,
            "k": spec.k,
            "dof": n_obs - spec.k,
            "chi2_Hz": components["Hz"],
            "chi2_DESI_DR2_BAO": components["DESI_DR2_BAO"],
            "claim_allowed": False,
        }
        row.update(params)
        rows.append(row)

    payload = {
        "schema": "rll.cosmology_model_family_shadow.result.v1",
        "created_utc": time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime()),
        "runtime_seconds": time.perf_counter() - started,
        "commit_sha": _git_sha(),
        "claim_allowed": False,
        "publication_effect": "NONE",
        "comparison_scope": contract["scientific_boundary"]["comparison_scope"],
        "canonical_outputs_modified": False,
        "mode": mode,
        "optimizer": {
            "name": contract["execution_policy"]["optimizer"],
            "seed": seed,
            "maxiter": maxiter,
            "tol": tol,
            "post_hoc_bound_changes_forbidden": True,
        },
        "data": {
            "Hz": str(HZ_PATH.relative_to(BASE_DIR)),
            "DESI_DR2_BAO": str(DESI_POINTS_PATH.relative_to(BASE_DIR)),
            "DESI_covariance": str(inputs["covariance_path"].relative_to(BASE_DIR)),
            "DESI_covariance_mode": inputs["covariance_mode"],
            "excluded_terms": contract["scientific_boundary"]["excluded_terms"],
        },
        "input_sha256": {
            str(path.relative_to(BASE_DIR)): _sha256_file(path)
            for path in (
                HZ_PATH,
                DESI_POINTS_PATH,
                inputs["covariance_path"],
                CONTRACT_PATH,
            )
        },
        "model_order": list(selected),
        "rows": rows,
        "interpretation": (
            "Shadow background-only comparison. Rankings are diagnostic, not claims. "
            "No observational value, error, covariance, model bound, or parameter count "
            "may be adapted after seeing a model result."
        ),
    }
    _atomic_write(
        RESULTS_DIR / f"{OUTPUT_STEM}.json",
        json.dumps(payload, ensure_ascii=False, indent=2, allow_nan=False) + "\n",
    )
    _atomic_write(RESULTS_DIR / f"{OUTPUT_STEM}.csv", _rows_to_csv(rows))
    return payload


def main() -> dict[str, Any]:
    mode = os.environ.get("RLL_MODEL_FAMILY_MODE", "all")
    payload = run_shadow_benchmark(mode=mode)
    print(pd.DataFrame(payload["rows"]).to_string(index=False))
    print(f"Wrote: results/structure_d/{OUTPUT_STEM}.json")
    print(f"Wrote: results/structure_d/{OUTPUT_STEM}.csv")
    return payload


if __name__ == "__main__":
    main()
