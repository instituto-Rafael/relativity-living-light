"""Small, standard-library-only LPT timing/Faraday diagnostic.

Not an orbital ephemeris fit, a plasma inference, or an RLL detection.
Synthetic and user-supplied normalized inputs remain distinguishable.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path


def _finite(value: object, label: str) -> float:
    try:
        number = float(value)
    except (ValueError, TypeError) as error:
        raise ValueError(f"{label} must be numeric") from error
    if not math.isfinite(number):
        raise ValueError(f"{label} must be finite")
    return number


def pulse_timing_residuals(rows: list[dict], period_s: float) -> dict:
    """Subtract a declared spin clock using explicit, strictly increasing cycle IDs.

    Times must be elapsed seconds on ONE declared, pre-corrected time standard.
    Missing pulse indices are not inferred from gaps (aliasing hazard).
    """
    period = _finite(period_s, "period_s")
    if period <= 0 or len(rows) < 2:
        raise ValueError("positive period and >=2 samples required")
    ids, times = [], []
    for row in rows:
        raw_id = str(row["pulse_number"])
        if not raw_id.lstrip("-").isdigit():
            raise ValueError("pulse_number must be an exact integer")
        ids.append(int(raw_id))
        times.append(_finite(row["toa_seconds"], "toa_seconds"))
    if any(b <= a for a, b in zip(ids, ids[1:])):
        raise ValueError("pulse IDs must be strictly increasing")
    if any(b <= a for a, b in zip(times, times[1:])):
        raise ValueError("ToAs must be strictly increasing")
    t0, n0 = times[0], ids[0]
    residuals = [(t - t0) - (n - n0) * period for n, t in zip(ids, times)]
    rms = math.sqrt(sum(r * r for r in residuals) / len(residuals))
    return {
        "operator": "declared_spin_ephemeris_residual_only",
        "n": len(rows), "reference_pulse": n0,
        "residual_seconds": residuals, "rms_seconds": rms,
        "physical_orbital_fit": "NOT_EXECUTED",
        "claim_allowed": False,
    }


def _solve_3x3(matrix: list[list[float]], vector: list[float]) -> list[float]:
    a = [list(row) + [value] for row, value in zip(matrix, vector)]
    scale = max(abs(x) for row in matrix for x in row)
    if scale <= 0 or not math.isfinite(scale):
        raise ValueError("degenerate phase sampling")
    for i in range(3):
        pivot = max(range(i, 3), key=lambda k: abs(a[k][i]))
        if abs(a[pivot][i]) <= scale * 1e-12:
            raise ValueError("degenerate phase sampling")
        a[i], a[pivot] = a[pivot], a[i]
        div = a[i][i]
        for j in range(i, 4):
            a[i][j] /= div
        for k in range(3):
            if k != i:
                mult = a[k][i]
                for j in range(i, 4):
                    a[k][j] -= mult * a[i][j]
    return [a[i][3] for i in range(3)]


def faraday_phase_diagnostic(rows: list[dict]) -> dict:
    """Weighted constant-RM null against a fixed first-harmonic phase template.

    Assumes independent Gaussian RM measurement errors; not a significance,
    binary/orbital solution, or validation of extra physics.
    """
    if len(rows) < 8:
        raise ValueError("at least 8 independent RM samples required")
    design = []
    measurements = []
    weights = []
    phases = []
    for row in rows:
        phase = _finite(row["orbital_phase"], "orbital_phase")
        rm = _finite(row["rm_rad_m2"], "rm_rad_m2")
        sigma = _finite(row["rm_sigma_rad_m2"], "rm_sigma_rad_m2")
        if not 0 <= phase < 1 or sigma <= 0:
            raise ValueError("phase must be in [0,1); RM sigma must be >0")
        phases.append(phase)
        angle = 2 * math.pi * phase
        design.append((1.0, math.sin(angle), math.cos(angle)))
        measurements.append(rm)
        weights.append(1.0 / (sigma * sigma))
    if len(set(phases)) < 4:
        raise ValueError("insufficient distinct phases")
    wsum = sum(weights)
    mean = sum(w * y for w, y in zip(weights, measurements)) / wsum
    null_chi2 = sum(w * (y - mean) ** 2 for w, y in zip(weights, measurements))
    gram = [[sum(w * x[i] * x[j] for x, w in zip(design, weights))
             for j in range(3)] for i in range(3)]
    rhs = [sum(w * x[i] * y for x, w, y in zip(design, weights, measurements))
           for i in range(3)]
    coeff = _solve_3x3(gram, rhs)
    fit_chi2 = sum(w * (y - sum(c * d for c, d in zip(coeff, x))) ** 2
                   for x, y, w in zip(design, measurements, weights))
    delta = null_chi2 - fit_chi2
    if delta < -1e-7 * max(1.0, null_chi2):
        raise ValueError("harmonic fit numerically worse than nested null")
    return {
        "operator": "weighted_RM_constant_vs_orbital_phase_harmonic",
        "n": len(rows), "chi2_null": null_chi2,
        "chi2_first_harmonic": fit_chi2, "delta_chi2": max(0.0, delta),
        "fit_coefficients": {"offset": coeff[0], "sin": coeff[1], "cos": coeff[2]},
        "rm_extraction": "EXTERNAL_NOT_VERIFIED",
        "instrument_systematics": "TOKEN_VAZIO",
        "significance": "NOT_ASSESSED", "claim_allowed": False,
    }


def analyze_csv(path: str, mode: str, period_s: float | None = None) -> dict:
    file = Path(path)
    payload = file.read_bytes()
    with file.open("r", encoding="utf-8-sig", newline="") as f:
        reader = csv.DictReader(f)
        needed = ({"pulse_number", "toa_seconds"} if mode == "toa" else
                  {"orbital_phase", "rm_rad_m2", "rm_sigma_rad_m2"})
        if mode not in {"toa", "rm"} or not needed.issubset(reader.fieldnames or []):
            raise ValueError("invalid mode or missing required CSV columns")
        rows = list(reader)
    if mode == "toa":
        if period_s is None:
            raise ValueError("--period-seconds is required for ToA")
        result = pulse_timing_residuals(rows, period_s)
    else:
        result = faraday_phase_diagnostic(rows)
    result.update({"input_sha256": hashlib.sha256(payload).hexdigest(),
                   "source_identity_verified": False,
                   "input_kind": "USER_NORMALIZED_NOT_UPSTREAM_AUTHENTICATED"})
    return result


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--mode", choices=["toa", "rm"], required=True)
    parser.add_argument("--input", required=True, help="normalized local CSV")
    parser.add_argument("--period-seconds", type=float)
    args = parser.parse_args()
    print(json.dumps(analyze_csv(args.input, args.mode, args.period_seconds),
                     sort_keys=True, indent=2, allow_nan=False))


if __name__ == "__main__":
    main()
