import os
import csv
import json
import time
import numpy as np
import pandas as pd

try:
    from scipy.integrate import quad
    from scipy.optimize import differential_evolution
except ImportError as exc:
    raise ImportError(
        "run_all_real requer SciPy. Instale com `pip install scipy` "
        "(ou `pip install -r requirements.txt`) para habilitar a execução real."
    ) from exc

from .data_access import load_active_datasets
from .likelihood import aic, bic, evaluate_model
from .models import N_FREE_PARAMS_LCDM, N_FREE_PARAMS_RLL

BASE_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", "..", ".."))
RESULTS = os.path.join(BASE_DIR, "results", "structure_d")
DEFAULT_CONFIG = os.path.join("data", "pipelines", "structure_d", "datasets_config.json")
REAL_PROFILE = "structure_d_real_validation"
EXECUTION_TIMING_BASENAME = "execution_timing_real"
MODEL_LCDM = "lcdm"
MODEL_RLL_AGN = "rll_like_agn"
REGIME_REAL = "real"
REGIME_PARTIAL_REAL = "partial_real"

LEGACY_ROUTE_SCOPE = "background_three_axis"
LEGACY_CONSUMED_DATASET_IDS = ("real_hz", "real_bao", "real_cmb_shift")
LEGACY_EFFECTIVE_COVARIANCE_POLICY = "diagonal_only"
SUPPORTED_COVARIANCE_POLICIES = ("prefer_full", "diagonal_only", "full_required")

C_KMS = 299792.458
Z_CMB = 1089.92

EXPECTED_MODEL_COMPARISON_HEADER = [
    "model",
    "regime",
    "chi2",
    "AIC",
    "BIC",
    "N",
    "k",
    "dof",
    "datasets_used",
    "run_name",
    "profile_name",
    "covariance_policy",
]
EXPECTED_MODEL_COMPARISON_FIT_PARAMS_HEADER = ["H0", "Om", "OL", "Ob_h2", "Os0", "zt", "wt"]


def _expected_model_comparison_header(include_fit_params):
    header = list(EXPECTED_MODEL_COMPARISON_HEADER)
    if bool(include_fit_params):
        header.extend(EXPECTED_MODEL_COMPARISON_FIT_PARAMS_HEADER)
    return header


def _validate_model_comparison_header(csv_path, include_fit_params):
    expected_header = _expected_model_comparison_header(include_fit_params)
    actual_header = list(pd.read_csv(csv_path, nrows=0).columns)
    missing = [column for column in expected_header if column not in actual_header]
    if missing:
        raise RuntimeError(
            f"schema mismatch for {os.path.basename(csv_path)}: missing required columns {missing}; got {actual_header}"
        )


def build_legacy_execution_contract(active_dataset_ids, covariance_policy):
    """Describe what this legacy objective actually consumes.

    This is an execution/evidence contract, not a scientific validation claim.
    The objective below uses only diagonal sigma arrays for H(z), BAO and CMB.
    """
    active = list(active_dataset_ids)
    requested_policy = str(covariance_policy)
    if requested_policy not in SUPPORTED_COVARIANCE_POLICIES:
        raise ValueError(
            f"unsupported covariance_policy={requested_policy!r}; "
            f"supported={list(SUPPORTED_COVARIANCE_POLICIES)}"
        )

    consumed = list(LEGACY_CONSUMED_DATASET_IDS)
    missing_required = [dataset_id for dataset_id in consumed if dataset_id not in active]
    if missing_required:
        raise RuntimeError(
            "legacy background objective requires active datasets "
            f"{consumed}; missing from profile: {missing_required}"
        )

    if requested_policy == "full_required":
        raise RuntimeError(
            "covariance_policy='full_required' is incompatible with the legacy "
            "three-axis objective: run_all_real.py evaluates diagonal sigma arrays. "
            "Use the joint real likelihood for claim-bearing full-covariance work."
        )

    unconsumed = [dataset_id for dataset_id in active if dataset_id not in consumed]
    covariance_gap = None
    if requested_policy == "prefer_full":
        covariance_gap = (
            "requested prefer_full, but the legacy objective evaluates diagonal "
            "sigma arrays; effective policy is diagonal_only"
        )

    return {
        "schema": "rll.structure_d.legacy_execution_contract.v1",
        "route_scope": LEGACY_ROUTE_SCOPE,
        "active_datasets_declared": active,
        "datasets_consumed_in_objective": consumed,
        "unconsumed_active_datasets": unconsumed,
        "full_profile_consumed": not unconsumed,
        "datasets_used_semantics": "objective_consumed_only",
        "covariance_policy_requested": requested_policy,
        "covariance_policy_effective": LEGACY_EFFECTIVE_COVARIANCE_POLICY,
        "covariance_gap": covariance_gap,
        "claim_allowed": False,
        "scientific_confirmation": False,
    }


def _f_log(z, zt, wt):
    return 1.0 / (1.0 + np.exp(np.clip((z - zt) / wt, -500, 500)))


def _e2_lcdm(z, om, ol):
    orad = 9e-5
    return om * (1.0 + z) ** 3 + orad * (1.0 + z) ** 4 + ol


def _e2_rll(z, om, ol, os0, zt, wt):
    orad = 9e-5
    fl = _f_log(z, zt, wt)
    sup = os0 * (fl + (1.0 - fl) * (1.0 + z) ** 3)
    return om * (1.0 + z) ** 3 + orad * (1.0 + z) ** 4 + ol + sup


def _hz_lcdm(z, h0, om, ol):
    return h0 * np.sqrt(np.maximum(_e2_lcdm(z, om, ol), 1e-12))


def _hz_rll(z, h0, om, ol, os0, zt, wt):
    return h0 * np.sqrt(np.maximum(_e2_rll(z, om, ol, os0, zt, wt), 1e-12))


def _dc(z_val, hz_fn, *args, cache=None):
    if cache is not None:
        cache_key = (hz_fn.__name__, float(z_val), tuple(float(a) for a in args))
        cached = cache.get(cache_key)
        if cached is not None:
            return cached
    fn = lambda zz: C_KMS / hz_fn(zz, *args)
    val, _ = quad(fn, 0, z_val, limit=150, epsrel=1e-5)
    if cache is not None:
        cache[cache_key] = val
    return val


def _dv_over_rs(z, hz_fn, h0, om, ob_h2, *args, dc_cache=None):
    dc_val = _dc(z, hz_fn, h0, om, *args, cache=dc_cache)
    hz_val = hz_fn(z, h0, om, *args)
    dv = (z * C_KMS / hz_val * dc_val ** 2) ** (1.0 / 3.0)
    rs = _rs_fn(h0, ob_h2, om)
    return dv / rs


def _rs_fn(h0, ob_h2, om):
    return 147.78 * (om * (h0 / 100.0) ** 2 / 0.1432) ** (-0.255) * (ob_h2 / 0.02236) ** (-0.134)


def _chi2_hz_lcdm(z_hz, h_obs, s_h, h0, om, ol):
    h_th = _hz_lcdm(z_hz, h0, om, ol)
    return float(np.sum(((h_obs - h_th) / s_h) ** 2))


def _chi2_hz_rll(z_hz, h_obs, s_h, h0, om, ol, os0, zt, wt):
    h_th = _hz_rll(z_hz, h0, om, ol, os0, zt, wt)
    return float(np.sum(((h_obs - h_th) / s_h) ** 2))


def _chi2_bao_lcdm(z_bao, dv_obs, s_dv, h0, om, ol, ob_h2, dc_cache=None):
    dv_th = np.array(
        [_dv_over_rs(z, _hz_lcdm, h0, om, ob_h2, ol, dc_cache=dc_cache) for z in z_bao],
        dtype=float,
    )
    return float(np.sum(((dv_obs - dv_th) / s_dv) ** 2))


def _chi2_bao_rll(z_bao, dv_obs, s_dv, h0, om, ol, os0, zt, wt, ob_h2, dc_cache=None):
    dv_th = np.array(
        [
            _dv_over_rs(
                z,
                _hz_rll,
                h0,
                om,
                ob_h2,
                ol,
                os0,
                zt,
                wt,
                dc_cache=dc_cache,
            )
            for z in z_bao
        ],
        dtype=float,
    )
    return float(np.sum(((dv_obs - dv_th) / s_dv) ** 2))


def _chi2_cmb_lcdm(r_obs, la_obs, r_sig, la_sig, h0, om, ol, ob_h2, dc_cache=None):
    dc_cmb = _dc(Z_CMB, _hz_lcdm, h0, om, ol, cache=dc_cache)
    r_th = np.sqrt(om) * h0 / C_KMS * dc_cmb
    la_th = np.pi * dc_cmb / _rs_fn(h0, ob_h2, om)
    return ((r_th - r_obs) / r_sig) ** 2 + ((la_th - la_obs) / la_sig) ** 2


def _chi2_cmb_rll(
    r_obs,
    la_obs,
    r_sig,
    la_sig,
    h0,
    om,
    ol,
    os0,
    zt,
    wt,
    ob_h2,
    dc_cache=None,
):
    dc_cmb = _dc(Z_CMB, _hz_rll, h0, om, ol, os0, zt, wt, cache=dc_cache)
    r_th = np.sqrt(om) * h0 / C_KMS * dc_cmb
    la_th = np.pi * dc_cmb / _rs_fn(h0, ob_h2, om)
    return ((r_th - r_obs) / r_sig) ** 2 + ((la_th - la_obs) / la_sig) ** 2


def _obj_lcdm(params, z_hz, h_obs, s_h, z_bao, dv_obs, s_dv, r_obs, la_obs, r_sig, la_sig):
    h0, om, ol, ob_h2 = params
    dc_cache = {}
    c2 = 0.0
    c2 += _chi2_hz_lcdm(z_hz, h_obs, s_h, h0, om, ol)
    c2 += _chi2_bao_lcdm(z_bao, dv_obs, s_dv, h0, om, ol, ob_h2, dc_cache=dc_cache)
    c2 += _chi2_cmb_lcdm(r_obs, la_obs, r_sig, la_sig, h0, om, ol, ob_h2, dc_cache=dc_cache)
    return c2


def _obj_rll(params, z_hz, h_obs, s_h, z_bao, dv_obs, s_dv, r_obs, la_obs, r_sig, la_sig):
    h0, om, ol, os0, zt, wt, ob_h2 = params
    dc_cache = {}
    c2 = 0.0
    c2 += _chi2_hz_rll(z_hz, h_obs, s_h, h0, om, ol, os0, zt, wt)
    c2 += _chi2_bao_rll(
        z_bao,
        dv_obs,
        s_dv,
        h0,
        om,
        ol,
        os0,
        zt,
        wt,
        ob_h2,
        dc_cache=dc_cache,
    )
    c2 += _chi2_cmb_rll(
        r_obs,
        la_obs,
        r_sig,
        la_sig,
        h0,
        om,
        ol,
        os0,
        zt,
        wt,
        ob_h2,
        dc_cache=dc_cache,
    )
    return c2


def _write_error_mode_usage(datasets, consumed_dataset_ids):
    consumed = set(consumed_dataset_ids)
    rows = []
    for dataset_id, entry in datasets.items():
        has_cov = entry.get("covariance") is not None
        has_err = entry.get("errors") is not None
        if has_cov and has_err:
            mode = "both"
        elif has_cov:
            mode = "covariance"
        elif has_err:
            mode = "errors"
        else:
            mode = "none"
        rows.append(
            {
                "dataset_id": dataset_id,
                "observable": entry.get("observable", "unknown"),
                "error_mode": mode,
                "consumed_in_objective": dataset_id in consumed,
            }
        )

    out_error_mode = os.path.join(RESULTS, "error_mode_usage.csv")
    evaluate_model(rows, out_error_mode)
    return out_error_mode


def _write_execution_timing(records, basename=EXECUTION_TIMING_BASENAME):
    csv_path = os.path.join(RESULTS, f"{basename}.csv")
    json_path = os.path.join(RESULTS, f"{basename}.json")

    with open(csv_path, "w", encoding="utf-8", newline="") as fp:
        writer = csv.DictWriter(fp, fieldnames=["block", "duration_seconds"])
        writer.writeheader()
        for record in records:
            writer.writerow(record)

    with open(json_path, "w", encoding="utf-8") as fp:
        json.dump(records, fp, ensure_ascii=False, indent=2)

    return csv_path, json_path


def main(
    config_path=DEFAULT_CONFIG,
    profile_name=REAL_PROFILE,
    output_filename="model_comparison_real.csv",
    covariance_policy="prefer_full",
    include_fit_params=True,
):
    os.makedirs(RESULTS, exist_ok=True)

    timing_records = []

    load_t0 = time.perf_counter()
    cfg_meta, datasets = load_active_datasets(config_path, profile_name=profile_name)
    execution_contract = build_legacy_execution_contract(
        cfg_meta.get("active_datasets", []),
        covariance_policy,
    )

    hz = datasets["real_hz"]
    bao = datasets["real_bao"]
    cmb = datasets["real_cmb_shift"]

    z_hz = hz["z"]
    h_obs = hz["values"]
    s_h = hz["errors"]

    z_bao = bao["z"]
    dv_obs = bao["values"]
    s_dv = bao["errors"]

    r_obs, la_obs = cmb["values"]
    r_sig, la_sig = cmb["errors"]
    timing_records.append({"block": "load", "duration_seconds": time.perf_counter() - load_t0})

    fit_t0 = time.perf_counter()
    n_obs = len(hz["values"]) + len(bao["values"]) + len(cmb["values"])

    bounds_l = [(60.0, 80.0), (0.10, 0.60), (0.50, 0.90), (0.018, 0.026)]
    bounds_r = [
        (60.0, 80.0),
        (0.10, 0.60),
        (0.50, 0.90),
        (0.000, 0.250),
        (0.1, 10.0),
        (0.1, 1.0),
        (0.018, 0.026),
    ]
    lcdm_param_order = ["H0", "Om", "OL", "Ob_h2"]
    rll_param_order = ["H0", "Om", "OL", "Os0", "zt", "wt", "Ob_h2"]
    seed = int(os.environ.get("STRUCTURE_D_SEED", "42"))
    tol = float(os.environ.get("STRUCTURE_D_TOL", "1e-6"))
    lcdm_maxiter = int(os.environ.get("STRUCTURE_D_MAXITER_LCDM", "200"))
    rll_maxiter = int(os.environ.get("STRUCTURE_D_MAXITER_RLL", "300"))
    res_l = differential_evolution(
        lambda p: _obj_lcdm(
            p,
            z_hz,
            h_obs,
            s_h,
            z_bao,
            dv_obs,
            s_dv,
            r_obs,
            la_obs,
            r_sig,
            la_sig,
        ),
        bounds_l,
        seed=seed,
        maxiter=lcdm_maxiter,
        tol=tol,
        workers=1,
    )

    res_r = differential_evolution(
        lambda p: _obj_rll(
            p,
            z_hz,
            h_obs,
            s_h,
            z_bao,
            dv_obs,
            s_dv,
            r_obs,
            la_obs,
            r_sig,
            la_sig,
        ),
        bounds_r,
        seed=seed,
        maxiter=rll_maxiter,
        tol=tol,
        workers=1,
    )

    b_l = res_l.x
    b_r = res_r.x
    c2_l = float(res_l.fun)
    c2_r = float(res_r.fun)
    timing_records.append({"block": "fit", "duration_seconds": time.perf_counter() - fit_t0})

    k_l = N_FREE_PARAMS_LCDM
    k_r = N_FREE_PARAMS_RLL

    consumed_dataset_ids = execution_contract["datasets_consumed_in_objective"]
    datasets_used = ",".join(consumed_dataset_ids)
    effective_covariance_policy = execution_contract["covariance_policy_effective"]
    run_name = cfg_meta["run_name"]
    profile = cfg_meta["profile_name"]

    has_cmb = "real_cmb_shift" in consumed_dataset_ids
    effective_regime = REGIME_REAL if has_cmb else REGIME_PARTIAL_REAL

    row_lcdm = dict(
        model=MODEL_LCDM,
        regime=effective_regime,
        chi2=c2_l,
        AIC=aic(c2_l, k_l),
        BIC=bic(c2_l, k_l, n_obs),
        N=n_obs,
        k=k_l,
        dof=n_obs - k_l,
        fit_params="H0,Om,OL,Ob_h2",
        fixed_params="",
        datasets_used=datasets_used,
        run_name=run_name,
        profile_name=profile,
        covariance_policy=effective_covariance_policy,
    )
    row_rll = dict(
        model=MODEL_RLL_AGN,
        regime=effective_regime,
        chi2=c2_r,
        AIC=aic(c2_r, k_r),
        BIC=bic(c2_r, k_r, n_obs),
        N=n_obs,
        k=k_r,
        dof=n_obs - k_r,
        fit_params="H0,Om,OL,Os0,zt,wt,Ob_h2",
        fixed_params="",
        datasets_used=datasets_used,
        run_name=run_name,
        profile_name=profile,
        covariance_policy=effective_covariance_policy,
    )
    if include_fit_params:
        row_lcdm.update(
            {
                "H0": b_l[0],
                "Om": b_l[1],
                "OL": b_l[2],
                "Ob_h2": b_l[3],
                "Os0": np.nan,
                "zt": np.nan,
                "wt": np.nan,
            }
        )
        row_rll.update(
            {
                "H0": b_r[0],
                "Om": b_r[1],
                "OL": b_r[2],
                "Ob_h2": b_r[6],
                "Os0": b_r[3],
                "zt": b_r[4],
                "wt": b_r[5],
            }
        )

    rows = [row_lcdm, row_rll]

    write_t0 = time.perf_counter()
    out = os.path.join(RESULTS, output_filename)
    out_error_mode = _write_error_mode_usage(datasets, consumed_dataset_ids)
    df = evaluate_model(rows, out)
    _validate_model_comparison_header(out, include_fit_params=include_fit_params)
    fit_metadata = {
        "output_csv": out,
        "profile_name": profile,
        "run_name": run_name,
        "route_scope": LEGACY_ROUTE_SCOPE,
        "claim_allowed": False,
        "scientific_confirmation": False,
        "active_datasets_declared": execution_contract["active_datasets_declared"],
        "datasets_used": consumed_dataset_ids,
        "datasets_consumed_in_objective": consumed_dataset_ids,
        "unconsumed_active_datasets": execution_contract["unconsumed_active_datasets"],
        "full_profile_consumed": execution_contract["full_profile_consumed"],
        "datasets_used_semantics": execution_contract["datasets_used_semantics"],
        "covariance_policy_requested": execution_contract["covariance_policy_requested"],
        "covariance_policy_effective": execution_contract["covariance_policy_effective"],
        "covariance_gap": execution_contract["covariance_gap"],
        "legacy_execution_contract": execution_contract,
        "optimizer": {
            "name": "scipy.optimize.differential_evolution",
            "seed": seed,
            "tol": tol,
            "workers": 1,
        },
        "fit_models": {
            "LCDM": {
                "param_order": lcdm_param_order,
                "bounds": [
                    {"name": name, "min": float(low), "max": float(high)}
                    for name, (low, high) in zip(lcdm_param_order, bounds_l)
                ],
                "maxiter": lcdm_maxiter,
                "best_fit": {
                    name: float(value)
                    for name, value in zip(lcdm_param_order, b_l)
                },
                "chi2": c2_l,
            },
            "RLL_like+AGN": {
                "param_order": rll_param_order,
                "bounds": [
                    {"name": name, "min": float(low), "max": float(high)}
                    for name, (low, high) in zip(rll_param_order, bounds_r)
                ],
                "maxiter": rll_maxiter,
                "best_fit": {
                    name: float(value)
                    for name, value in zip(rll_param_order, b_r)
                },
                "chi2": c2_r,
            },
        },
    }
    metadata_out = os.path.splitext(out)[0] + "_fit_metadata.json"
    with open(metadata_out, "w", encoding="utf-8") as fp:
        json.dump(fit_metadata, fp, ensure_ascii=False, indent=2)

    timing_records.append({"block": "write", "duration_seconds": time.perf_counter() - write_t0})
    timing_csv_path, timing_json_path = _write_execution_timing(timing_records)
    _validate_model_comparison_header(out, include_fit_params=include_fit_params)

    print(df.to_string(index=False))
    print(f"\nWrote: {out}")
    print(f"Wrote: {metadata_out}")
    print(f"Wrote: {timing_csv_path}")
    print(f"Wrote: {timing_json_path}")
    print(f"Wrote: {out_error_mode}")
    return df


if __name__ == "__main__":
    env_profile = os.environ.get("STRUCTURE_D_PROFILE", REAL_PROFILE)
    main(profile_name=env_profile)
