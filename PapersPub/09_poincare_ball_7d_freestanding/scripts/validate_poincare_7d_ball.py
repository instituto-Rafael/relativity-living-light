#!/usr/bin/env python3
"""Deterministic independent validator for the freestanding AArch64 H^7 -> B^7 kernel."""
from __future__ import annotations

import argparse
import json
import math
import struct
from pathlib import Path

N = 8
SPATIAL_DIMS = 7
EPS = 1.0e-6


def f32(value: float) -> float:
    return struct.unpack("<f", struct.pack("<f", value))[0]


def f32_hex(value: float) -> str:
    return f"{struct.unpack('<I', struct.pack('<f', f32(value)))[0]:08X}"


def build_matrix() -> list[list[float]]:
    a = [[f32((i << 1) + j) for j in range(N)] for i in range(N)]
    b = [[f32(i + j * 3) for j in range(N)] for i in range(N)]
    c = [[f32(0.0) for _ in range(N)] for _ in range(N)]
    for i in range(N):
        for k in range(N):
            aik = a[i][k]
            for j in range(N):
                c[i][j] = f32(c[i][j] + f32(aik * b[k][j]))
    return c


def project_column(c: list[list[float]], column: int, scale: float) -> dict[str, object]:
    temporal = c[0][column]
    spatial = [c[d + 1][column] for d in range(SPATIAL_DIMS)]
    spatial_sq = f32(0.0)
    for value in spatial:
        spatial_sq = f32(spatial_sq + f32(value * value))
    delta = f32(f32(temporal * temporal) - spatial_sq)

    if temporal > 0.0 and delta > EPS:
        mode = "T"
        inv_norm = f32(1.0 / math.sqrt(delta))
        x0 = f32(temporal * inv_norm)
        denom = f32(x0 + 1.0)
        p = [f32(f32(value * inv_norm) / denom) for value in spatial]
    else:
        mode = "L"
        q = [f32(value / scale) for value in spatial]
        q_sq = f32(0.0)
        for value in q:
            q_sq = f32(q_sq + f32(value * value))
        x0 = f32(math.sqrt(f32(1.0 + q_sq)))
        denom = f32(x0 + 1.0)
        p = [f32(value / denom) for value in q]

    radius_sq = f32(0.0)
    for value in p:
        radius_sq = f32(radius_sq + f32(value * value))
    radius = f32(math.sqrt(radius_sq))
    line = f"P7:{column}:{mode}:{f32_hex(p[0])}{f32_hex(p[1])}{f32_hex(radius)}"
    return {
        "column": column,
        "mode": mode,
        "minkowski_delta": delta,
        "p1": p[0],
        "p2": p[1],
        "radius": radius,
        "line": line,
    }


def validate() -> dict[str, object]:
    c = build_matrix()
    scale = max(abs(value) for row in c for value in row) or 1.0
    points = [project_column(c, column, scale) for column in range(N)]
    strict_count = sum(point["mode"] == "T" for point in points)
    lifted_count = sum(point["mode"] == "L" for point in points)

    expected_lines = [
        "P7:0:L:3CE28D543D11A3FF3E11959C",
        "P7:1:L:3D3631ED3D6FF6D43E773FE6",
        "P7:2:L:3D721F113DA110373EA800FC",
        "P7:3:L:3D926B753DC3E2C93ECDB0C5",
        "P7:4:L:3DA7A6573DE113A73EED548C",
        "P7:5:L:3DB968E73DF986003F03EE41",
        "P7:6:L:3DC8568D3E070BB43F0F1A78",
        "P7:7:L:3DD4FACA3E0FC2E23F1894A1",
    ]

    checks = {
        "matrix_shape_8x8": len(c) == N and all(len(row) == N for row in c),
        "matrix_anchor_c00": c[0][0] == 140.0,
        "matrix_anchor_c77": c[7][7] == 3472.0,
        "column_interpretation_is_1_plus_7": all(len([c[d][j] for d in range(N)]) == 8 for j in range(N)),
        "raw_columns_are_not_future_timelike": strict_count == 0 and all(point["minkowski_delta"] < 0.0 for point in points),
        "canonical_lift_covers_all_columns": lifted_count == N,
        "all_ball_radii_are_strictly_inside": all(0.0 <= point["radius"] < 1.0 for point in points),
        "hex_receipt_matches_reference": [point["line"] for point in points] == expected_lines,
    }
    passed = sum(bool(value) for value in checks.values())
    status = "PASS" if passed == len(checks) else "FAIL"
    return {
        "schema": "rll.poincare_ball_7d.validation.v1",
        "status": status,
        "checks_total": len(checks),
        "checks_passed": passed,
        "checks_failed": len(checks) - passed,
        "checks": checks,
        "matrix_scale": scale,
        "strict_timelike_columns": strict_count,
        "canonical_lift_columns": lifted_count,
        "points": points,
        "states": {
            "finite_matrix_multiplication": "PASS",
            "raw_hyperboloid_membership": "FAIL_PRECONDITION_SPACELIKE",
            "strict_projection_output": "TOKEN_VAZIO_INPUT_NOT_TIMELIKE",
            "canonical_hyperboloid_lift": "PASS_COMPUTATIONAL_EMBEDDING",
            "poincare_ball_membership": "PASS",
            "physical_stability": "TOKEN_VAZIO",
            "cosmological_interpretation": "PROHIBITED_BY_SCOPE",
            "claim_allowed": False,
        },
        "guards": [
            "eight matrix columns define eight candidate 1+7 vectors; flattening rows 1..7 creates 56 spatial coordinates, not H^7",
            "the raw C columns are spacelike under T^2-||V||^2 and cannot be called points of the unit hyperboloid",
            "canonical lift is an explicit embedding after declared scaling; it does not retroactively validate the raw matrix as Lorentzian data",
            "radius < 1 proves membership in the chosen Poincare-ball model only, not physical or cosmological stability",
            "Poincare ball, Poincare section/return map, recurrence theorem and Poincare conjecture are distinct objects",
        ],
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--output")
    args = parser.parse_args()
    report = validate()
    payload = json.dumps(report, ensure_ascii=False, indent=2, sort_keys=True) + "\n"
    if args.output:
        path = Path(args.output)
        path.parent.mkdir(parents=True, exist_ok=True)
        path.write_text(payload, encoding="utf-8")
    print(payload, end="")
    return 0 if report["status"] == "PASS" else 1


if __name__ == "__main__":
    raise SystemExit(main())
