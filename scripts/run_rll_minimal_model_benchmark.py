#!/usr/bin/env python3
"""Deterministic one-extra-parameter DESI DR2 BAO benchmark for RLL-min.

Purpose
-------
Test the narrow question: can the current RLL transition family buy a DESI DR2
BAO chi-square improvement comparable to ~8--10 with only ONE parameter beyond
an equally profiled LCDM baseline?

Shared fitted/profiled quantities:
- Omega_m (shape)
- q = c / (H0 * r_d) (analytic scale profile)

RLL-min extra quantity:
- Omega_s0 only

Frozen RLL-min transition coordinates:
- z_t = 1.0
- w_t = 0.3

This is intentionally NOT a CMB/full-shape/growth/Bayesian-evidence analysis.
Those gates are emitted as NOT_RUN/TOKEN_VAZIO instead of being inferred from
BAO-only goodness of fit.

SOURCE != ARTIFACT != EXECUTION != EVIDENCE != CLAIM
TOKEN_VAZIO != 0
PROFILE_LIKELIHOOD != BAYESIAN_EVIDENCE
LYA_BAO != LYA_FULL_SHAPE
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
DEFAULT_MEASUREMENTS = ROOT / "data" / "real" / "desi_dr2_bao_measurements.csv"
DEFAULT_COVARIANCE = ROOT / "data" / "real" / "desi_dr2_bao_covariance.csv"

C_KM_S = 299792.458
OMEGA_R = 9.2e-5
ZT_FIXED = 1.0
WT_FIXED = 0.3
SIMPSON_N = 256


@dataclass(frozen=True)
class Fit:
    model: str
    omega_m: float
    omega_s0: float
    q_scale: float
    chi2: float
    k_params: int


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as fh:
        for chunk in iter(lambda: fh.read(1024 * 1024), b""):
            h.update(chunk)
    return h.hexdigest()


def load_measurements(path: Path) -> list[dict[str, object]]:
    with path.open("r", encoding="utf-8", newline="") as fh:
        rows = list(csv.DictReader(fh))
    out: list[dict[str, object]] = []
    for row in rows:
        out.append(
            {
                "index": int(row["index"]),
                "tracer": row["tracer"],
                "z_eff": float(row["z_eff"]),
                "observable": row["observable"],
                "value": float(row["value"]),
                "sigma": float(row["sigma"]),
            }
        )
    return out


def load_covariance(path: Path) -> list[list[float]]:
    rows: list[list[float]] = []
    with path.open("r", encoding="utf-8", newline="") as fh:
        reader = csv.reader(fh)
        next(reader)
        for row in reader:
            rows.append([float(x) for x in row[1:]])
    return rows


def invert_matrix(a: list[list[float]]) -> list[list[float]]:
    n = len(a)
    aug = [
        [float(a[i][j]) for j in range(n)]
        + [1.0 if i == j else 0.0 for j in range(n)]
        for i in range(n)
    ]
    for col in range(n):
        pivot = max(range(col, n), key=lambda r: abs(aug[r][col]))
        if abs(aug[pivot][col]) < 1e-15:
            raise ValueError("singular covariance matrix")
        if pivot != col:
            aug[col], aug[pivot] = aug[pivot], aug[col]
        div = aug[col][col]
        aug[col] = [x / div for x in aug[col]]
        for row in range(n):
            if row == col:
                continue
            factor = aug[row][col]
            aug[row] = [
                aug[row][j] - factor * aug[col][j] for j in range(2 * n)
            ]
    return [row[n:] for row in aug]


def matvec(a: list[list[float]], x: list[float]) -> list[float]:
    return [sum(row[j] * x[j] for j in range(len(x))) for row in a]


def dot(x: list[float], y: list[float]) -> float:
    return sum(a * b for a, b in zip(x, y))


def chi2(residual: list[float], inv_cov: list[list[float]]) -> float:
    return dot(residual, matvec(inv_cov, residual))


def rll_f(z: float, zt: float = ZT_FIXED, wt: float = WT_FIXED) -> float:
    arg = max(-700.0, min(700.0, (z - zt) / wt))
    return 1.0 / (1.0 + math.exp(arg))


def e2_lcdm(z: float, omega_m: float) -> float:
    return omega_m * (1.0 + z) ** 3 + OMEGA_R * (1.0 + z) ** 4 + (1.0 - omega_m - OMEGA_R)


def e2_rll_min(z: float, omega_m: float, omega_s0: float) -> float:
    omega_l = 1.0 - omega_m - OMEGA_R - omega_s0
    fz = rll_f(z)
    return (
        omega_m * (1.0 + z) ** 3
        + OMEGA_R * (1.0 + z) ** 4
        + omega_l
        + omega_s0 * (fz + (1.0 - fz) * (1.0 + z) ** 3)
    )


def simpson_integral_inv_e(z: float, model: str, omega_m: float, omega_s0: float) -> float:
    if z <= 0.0:
        return 0.0
    n = SIMPSON_N if SIMPSON_N % 2 == 0 else SIMPSON_N + 1
    h = z / n

    def inv_e(x: float) -> float:
        e2 = e2_lcdm(x, omega_m) if model == "LCDM" else e2_rll_min(x, omega_m, omega_s0)
        if e2 <= 0.0 or not math.isfinite(e2):
            raise ValueError("non-positive/non-finite E^2")
        return 1.0 / math.sqrt(e2)

    acc = inv_e(0.0) + inv_e(z)
    for i in range(1, n):
        acc += (4.0 if i % 2 else 2.0) * inv_e(i * h)
    return acc * h / 3.0


def shape_vector(
    measurements: list[dict[str, object]],
    model: str,
    omega_m: float,
    omega_s0: float = 0.0,
) -> list[float]:
    by_z: dict[float, tuple[float, float]] = {}
    for row in measurements:
        z = float(row["z_eff"])
        if z not in by_z:
            integral = simpson_integral_inv_e(z, model, omega_m, omega_s0)
            e2 = e2_lcdm(z, omega_m) if model == "LCDM" else e2_rll_min(z, omega_m, omega_s0)
            if e2 <= 0.0:
                raise ValueError("non-positive E^2 at observed redshift")
            by_z[z] = (integral, 1.0 / math.sqrt(e2))

    out: list[float] = []
    for row in measurements:
        z = float(row["z_eff"])
        integral, inv_e = by_z[z]
        observable = str(row["observable"])
        if observable == "DM_over_rd":
            value = integral
        elif observable == "DH_over_rd":
            value = inv_e
        elif observable == "DV_over_rd":
            value = (z * integral * integral * inv_e) ** (1.0 / 3.0)
        else:
            raise ValueError(f"unsupported observable: {observable}")
        out.append(value)
    return out


def profile_q(shape: list[float], observed: list[float], inv_cov: list[list[float]]) -> tuple[float, float]:
    w_y = matvec(inv_cov, observed)
    w_s = matvec(inv_cov, shape)
    denom = dot(shape, w_s)
    if denom <= 0.0:
        raise ValueError("non-positive profile denominator")
    q = dot(shape, w_y) / denom
    residual = [q * s - y for s, y in zip(shape, observed)]
    return q, chi2(residual, inv_cov)


def evaluate(
    measurements: list[dict[str, object]],
    inv_cov: list[list[float]],
    model: str,
    omega_m: float,
    omega_s0: float = 0.0,
) -> tuple[float, float]:
    observed = [float(row["value"]) for row in measurements]
    shape = shape_vector(measurements, model, omega_m, omega_s0)
    return profile_q(shape, observed, inv_cov)


def grid(start: float, stop: float, step: float) -> list[float]:
    count = int(math.floor((stop - start) / step + 1e-12))
    return [start + i * step for i in range(count + 1)]


def fit_lcdm(measurements: list[dict[str, object]], inv_cov: list[list[float]]) -> Fit:
    best: tuple[float, float, float] | None = None
    for om in grid(0.20, 0.40, 0.002):
        q, c2 = evaluate(measurements, inv_cov, "LCDM", om)
        if best is None or c2 < best[0]:
            best = (c2, om, q)
    assert best is not None
    _, om0, _ = best
    for om in grid(max(0.10, om0 - 0.004), min(0.50, om0 + 0.004), 0.0001):
        q, c2 = evaluate(measurements, inv_cov, "LCDM", om)
        if c2 < best[0]:
            best = (c2, om, q)
    c2, om, q = best
    return Fit("LCDM", om, 0.0, q, c2, 2)


def fit_rll_min(measurements: list[dict[str, object]], inv_cov: list[list[float]]) -> Fit:
    best: tuple[float, float, float, float] | None = None
    for om in grid(0.24, 0.36, 0.004):
        for os0 in grid(-0.06, 0.06, 0.004):
            try:
                q, c2 = evaluate(measurements, inv_cov, "RLL_MIN", om, os0)
            except ValueError:
                continue
            if best is None or c2 < best[0]:
                best = (c2, om, os0, q)
    if best is None:
        raise RuntimeError("RLL-min coarse search found no valid point")
    _, om0, os0_0, _ = best
    for om in grid(max(0.10, om0 - 0.008), min(0.50, om0 + 0.008), 0.0005):
        for os0 in grid(max(-0.10, os0_0 - 0.008), min(0.10, os0_0 + 0.008), 0.0005):
            try:
                q, c2 = evaluate(measurements, inv_cov, "RLL_MIN", om, os0)
            except ValueError:
                continue
            if c2 < best[0]:
                best = (c2, om, os0, q)
    c2, om, os0, q = best
    return Fit("RLL_MIN", om, os0, q, c2, 3)


def prediction_vector(measurements: list[dict[str, object]], fit: Fit) -> list[float]:
    model = "LCDM" if fit.model == "LCDM" else "RLL_MIN"
    shape = shape_vector(measurements, model, fit.omega_m, fit.omega_s0)
    return [fit.q_scale * x for x in shape]


def subblock_chi2(
    measurements: list[dict[str, object]],
    covariance: list[list[float]],
    prediction: list[float],
    indices: list[int],
) -> float:
    cov = [[covariance[i][j] for j in indices] for i in indices]
    inv = invert_matrix(cov)
    residual = [prediction[i] - float(measurements[i]["value"]) for i in indices]
    return chi2(residual, inv)


def build_payload(
    measurements_path: Path,
    covariance_path: Path,
    measurements: list[dict[str, object]],
    covariance: list[list[float]],
    lcdm: Fit,
    rll: Fit,
) -> dict[str, object]:
    n = len(measurements)
    dl = rll.chi2 - lcdm.chi2
    aic_l = lcdm.chi2 + 2.0 * lcdm.k_params
    aic_r = rll.chi2 + 2.0 * rll.k_params
    bic_l = lcdm.chi2 + lcdm.k_params * math.log(n)
    bic_r = rll.chi2 + rll.k_params * math.log(n)
    pred_l = prediction_vector(measurements, lcdm)
    pred_r = prediction_vector(measurements, rll)
    lya_indices = [i for i, row in enumerate(measurements) if str(row["tracer"]).lower() == "lya"]
    lya_l = subblock_chi2(measurements, covariance, pred_l, lya_indices)
    lya_r = subblock_chi2(measurements, covariance, pred_r, lya_indices)

    return {
        "schema": "rll.minimal_one_parameter_benchmark.v1",
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "source": {
            "measurements": str(measurements_path.relative_to(ROOT)),
            "measurements_sha256": sha256_file(measurements_path),
            "covariance": str(covariance_path.relative_to(ROOT)),
            "covariance_sha256": sha256_file(covariance_path),
            "n_obs": n,
            "covariance_semantics": "full_13x13_current_repository_materialization",
        },
        "contract": {
            "shared_free_or_profiled": ["Omega_m", "q=c/(H0*r_d)"],
            "rll_min_extra_free": ["Omega_s0"],
            "rll_min_frozen": {"z_t": ZT_FIXED, "w_t": WT_FIXED, "Omega_r": OMEGA_R},
            "target_delta_chi2": [-8.0, -10.0],
            "claim_boundary": "BAO-only profile benchmark; not publication evidence by itself.",
        },
        "fits": {
            "LCDM": lcdm.__dict__,
            "RLL_MIN": rll.__dict__,
        },
        "comparison": {
            "delta_chi2_rll_min_minus_lcdm": dl,
            "delta_aic_rll_min_minus_lcdm": aic_r - aic_l,
            "delta_bic_rll_min_minus_lcdm": bic_r - bic_l,
            "target_minus8_pass": dl <= -8.0,
            "target_minus10_pass": dl <= -10.0,
            "aic_improves": aic_r < aic_l,
            "bic_improves": bic_r < bic_l,
        },
        "lya_bao_only_diagnostic": {
            "indices": lya_indices,
            "LCDM_chi2": lya_l,
            "RLL_MIN_chi2": lya_r,
            "delta_chi2": lya_r - lya_l,
            "epistemic_boundary": "This is the two-point LyA BAO sub-block, NOT DESI 2026 LyA full-shape/AP.",
        },
        "successor_gates": {
            "desi_lya_full_shape": {
                "status": "NOT_RUN",
                "reason": "Requires non-double-counted full-shape/AP likelihood and model prediction interface.",
            },
            "growth_fsigma8": {
                "status": "TOKEN_VAZIO",
                "reason": "RLL-min currently defines background expansion only; no justified perturbation/growth law is bound to this benchmark.",
            },
            "bayesian_evidence": {
                "status": "NOT_RUN",
                "reason": "Profile chi-square/AIC/BIC are not Bayesian evidence; priors and evidence integration are not defined here.",
            },
        },
        "claim_allowed": False,
        "publication_ready": False,
        "R3": {
            "F_ok": [
                "same DESI DR2 BAO vector/covariance used for both models",
                "LCDM and RLL-min profile the same Omega_m and q scale",
                "RLL-min adds only Omega_s0",
                "AIC/BIC computed with one-parameter complexity delta",
                "LyA BAO sub-block explicitly separated from LyA full-shape",
            ],
            "F_gap": [
                "DESI_DR2_LYA_FULLSHAPE_NON_OVERLAP_LIKELIHOOD",
                "RLL_MIN_PERTURBATION_GROWTH_MODEL",
                "RLL_MIN_BAYESIAN_PRIORS_AND_EVIDENCE",
                "CMB_JOINT_LIKELIHOOD_SAME_PARAMETERIZATION",
            ],
            "F_next": "Only if the one-parameter BAO target passes should the same frozen parameterization advance to full-shape, growth and Bayesian evidence. Otherwise revise physics before adding complexity.",
        },
    }


def write_report(payload: dict[str, object], path: Path) -> None:
    comp = payload["comparison"]
    fits = payload["fits"]
    gates = payload["successor_gates"]
    lines = [
        "# RLL-min one-parameter benchmark receipt",
        "",
        f"Generated: `{payload['generated_at_utc']}`",
        "",
        "## Fits",
        "",
        f"- LCDM chi2: `{fits['LCDM']['chi2']:.6f}`",
        f"- RLL-min chi2: `{fits['RLL_MIN']['chi2']:.6f}`",
        f"- delta chi2 (RLL-min - LCDM): `{comp['delta_chi2_rll_min_minus_lcdm']:+.6f}`",
        f"- delta AIC: `{comp['delta_aic_rll_min_minus_lcdm']:+.6f}`",
        f"- delta BIC: `{comp['delta_bic_rll_min_minus_lcdm']:+.6f}`",
        f"- target -8: `{'PASS' if comp['target_minus8_pass'] else 'FAIL'}`",
        f"- target -10: `{'PASS' if comp['target_minus10_pass'] else 'FAIL'}`",
        "",
        "## Successor gates",
        "",
        f"- LyA full-shape: `{gates['desi_lya_full_shape']['status']}`",
        f"- growth/fσ8: `{gates['growth_fsigma8']['status']}`",
        f"- Bayesian evidence: `{gates['bayesian_evidence']['status']}`",
        "",
        "`claim_allowed=false`  ",
        "`publication_ready=false`",
        "",
        "The benchmark must not be described as a full cosmological model comparison.",
    ]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--measurements", type=Path, default=DEFAULT_MEASUREMENTS)
    parser.add_argument("--covariance", type=Path, default=DEFAULT_COVARIANCE)
    parser.add_argument("--output-dir", type=Path, default=ROOT / "artifacts" / "rll-minimal-benchmark")
    args = parser.parse_args()

    measurements = load_measurements(args.measurements)
    covariance = load_covariance(args.covariance)
    if len(measurements) != 13 or len(covariance) != 13 or any(len(row) != 13 for row in covariance):
        raise SystemExit("expected current DESI DR2 13-vector and 13x13 covariance")
    for i in range(13):
        for j in range(13):
            if abs(covariance[i][j] - covariance[j][i]) > 1e-12:
                raise SystemExit("covariance is not symmetric")

    inv_cov = invert_matrix(covariance)
    lcdm = fit_lcdm(measurements, inv_cov)
    rll = fit_rll_min(measurements, inv_cov)
    payload = build_payload(args.measurements, args.covariance, measurements, covariance, lcdm, rll)

    args.output_dir.mkdir(parents=True, exist_ok=True)
    json_path = args.output_dir / "benchmark.json"
    report_path = args.output_dir / "REPORT.md"
    json_path.write_text(json.dumps(payload, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    write_report(payload, report_path)
    print(report_path.read_text(encoding="utf-8"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
