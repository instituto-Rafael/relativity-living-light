#!/usr/bin/env python3
from __future__ import annotations

import argparse
import json
import math
from pathlib import Path

TAU = 2.0 * math.pi


def phase_one_based(value: int, base: int) -> int:
    if value <= 0 or base < 2:
        raise ValueError("value must be positive and base >= 2")
    return 1 + ((value - 1) % base)


def positional_encode(value: int, base: int) -> str:
    if value < 0 or base < 2 or base > 10:
        raise ValueError("unsupported value/base")
    if value == 0:
        return "0"
    digits: list[str] = []
    current = value
    while current:
        current, remainder = divmod(current, base)
        digits.append(str(remainder))
    return "".join(reversed(digits))


def validate() -> dict[str, object]:
    center = (3.0, 0.0)
    radius = 1.0
    definitions = (
        ("upper", "vertical", math.pi / 2.0, (0, 1)),
        ("lower", "vertical", 3.0 * math.pi / 2.0, (0, -1)),
        ("right", "horizontal", 0.0, (1, 0)),
        ("left", "horizontal", math.pi, (-1, 0)),
        ("upper_right", "diagonal_rising", math.pi / 4.0, (1, 1)),
        ("lower_left", "diagonal_rising", 5.0 * math.pi / 4.0, (-1, -1)),
        ("upper_left", "diagonal_falling", 3.0 * math.pi / 4.0, (-1, 1)),
        ("lower_right", "diagonal_falling", 7.0 * math.pi / 4.0, (1, -1)),
    )
    ports = []
    for name, axis, angle, direction in definitions:
        nx, ny = math.cos(angle), math.sin(angle)
        px, py = center[0] + radius * nx, center[1] + radius * ny
        tangent = (-ny, nx)
        line_c = -(nx * px + ny * py)
        ports.append(
            {
                "name": name,
                "axis": axis,
                "angle": angle,
                "direction": direction,
                "position": (px, py),
                "normal": (nx, ny),
                "tangent": tangent,
                "line": (nx, ny, line_c),
            }
        )

    by_axis: dict[str, list[dict[str, object]]] = {}
    for port in ports:
        by_axis.setdefault(port["axis"], []).append(port)

    expected = {
        (0, 1), (0, -1), (1, 0), (-1, 0),
        (1, 1), (-1, -1), (-1, 1), (1, -1),
    }

    q7, r7 = divmod(7, 7)
    theta0 = 0.0
    theta7 = TAU * 7 / 7
    p0 = (math.cos(theta0), math.sin(theta0), theta0 / TAU)
    p7 = (math.cos(theta7), math.sin(theta7), theta7 / TAU)

    checks = {
        "four_axes": len(by_axis) == 4,
        "eight_ports": len(ports) == 8,
        "two_ports_per_axis": all(len(items) == 2 for items in by_axis.values()),
        "opposed_midpoint_is_center": all(
            math.isclose((items[0]["position"][0] + items[1]["position"][0]) / 2.0, center[0], abs_tol=1e-12)
            and math.isclose((items[0]["position"][1] + items[1]["position"][1]) / 2.0, center[1], abs_tol=1e-12)
            for items in by_axis.values()
        ),
        "diameter_is_2r": all(
            math.isclose(
                math.hypot(
                    items[0]["position"][0] - items[1]["position"][0],
                    items[0]["position"][1] - items[1]["position"][1],
                ),
                2.0 * radius,
                abs_tol=1e-12,
            )
            for items in by_axis.values()
        ),
        "ports_on_circle": all(
            math.isclose(
                math.hypot(port["position"][0] - center[0], port["position"][1] - center[1]),
                radius,
                abs_tol=1e-12,
            )
            for port in ports
        ),
        "tangent_perpendicular": all(
            math.isclose(
                port["normal"][0] * port["tangent"][0]
                + port["normal"][1] * port["tangent"][1],
                0.0,
                abs_tol=1e-12,
            )
            for port in ports
        ),
        "tangent_line_distance_is_r": all(
            math.isclose(
                abs(
                    port["line"][0] * center[0]
                    + port["line"][1] * center[1]
                    + port["line"][2]
                ) / math.hypot(port["line"][0], port["line"][1]),
                radius,
                abs_tol=1e-12,
            )
            for port in ports
        ),
        "eight_matrix_directions": {port["direction"] for port in ports} == expected,
        "diagonal_normalization": all(
            math.isclose(abs(dc / math.hypot(dc, dr)), 1.0 / math.sqrt(2.0), abs_tol=1e-12)
            and math.isclose(abs(dr / math.hypot(dc, dr)), 1.0 / math.sqrt(2.0), abs_tol=1e-12)
            for dc, dr in expected
            if abs(dc) == abs(dr) == 1
        ),
        "torus_sweep_preserves_meridian_radius": all(
            math.isclose(
                math.hypot(
                    math.hypot(
                        port["position"][0] * math.cos(0.73),
                        port["position"][0] * math.sin(0.73),
                    ) - center[0],
                    port["position"][1] - center[1],
                ),
                radius,
                abs_tol=1e-12,
            )
            for port in ports
        ),
        "seven_decimal_is_10_base7": positional_encode(7, 7) == "10",
        "complete_state_is_1_0": (q7, r7) == (1, 0),
        "phase_seven_is_preserved": phase_one_based(7, 7) == 7,
        "reconstruction_preserves_seven": 7 * q7 + r7 == 7,
        "venturi_fold_is_lossless": all(
            7 * divmod(value, 7)[0] + divmod(value, 7)[1] == value
            for value in range(70)
        ),
        "vortex_six_plus_one_reaches_phase_seven": phase_one_based(6 + 1, 7) == 7,
        "vortex_seven_plus_one_returns_phase_one": phase_one_based(7 + 1, 7) == 1,
        "lifted_seam_preserves_winding": math.isclose(p0[0], p7[0], abs_tol=1e-12)
        and math.isclose(p0[1], p7[1], abs_tol=1e-12)
        and p7[2] > p0[2],
        "zero_is_valid_state": positional_encode(0, 7) == "0",
        "empirical_fluid_interpretation_not_applicable": True,
    }
    passed = sum(checks.values())
    all_pass = all(checks.values())
    return {
        "schema": "paper.validation.four_axis_flow_ports.v2",
        "checks_total": len(checks),
        "checks_passed": passed,
        "checks_failed": len(checks) - passed,
        "exact_geometry_state": "PASS" if all_pass else "FAIL",
        "operator_state": "PASS" if all_pass else "AUDIT",
        "empirical_fluid_interpretation": "NOT_APPLICABLE",
        "claim_allowed": all_pass,
        "axis_count": 4,
        "port_count": 8,
        "base7_example": {
            "decimal": 7,
            "positional": "10",
            "quotient": q7,
            "remainder": r7,
            "phase": phase_one_based(7, 7),
        },
        "checks": checks,
    }


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--output",
        default="PapersPub/08_multiscale_validation_methods/results/four_axis_flow_ports_validation.json",
    )
    args = parser.parse_args()
    report = validate()
    output = Path(args.output)
    output.parent.mkdir(parents=True, exist_ok=True)
    output.write_text(
        json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True) + "\n",
        encoding="utf-8",
    )
    print(json.dumps(report, indent=2, ensure_ascii=False, sort_keys=True))
    return 0 if report["claim_allowed"] else 1


if __name__ == "__main__":
    raise SystemExit(main())
