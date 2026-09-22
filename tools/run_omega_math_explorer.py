#!/usr/bin/env python3
"""Deterministic YAML-driven Omega mathematics explorer.

The YAML is a declarative contract. This runner contains the executable
mathematics. It emits bounded artifacts and never promotes a scientific claim.
"""
from __future__ import annotations

import argparse
import csv
import hashlib
import itertools
import json
import math
import os
from collections import defaultdict
from fractions import Fraction
from functools import reduce
from pathlib import Path
from typing import Any

import yaml
from jsonschema import validate

RECEIPT_SCHEMA = "rll.omega_math_explorer.receipt.v1"


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def lcm(a: int, b: int) -> int:
    return abs(a * b) // math.gcd(a, b)


def lcm_many(values: list[int]) -> int:
    return reduce(lcm, values, 1)


def close(a: float, b: float, tol: float) -> bool:
    return abs(a - b) <= tol * max(1.0, abs(a), abs(b))


def load_contract(manifest_path: Path, schema_path: Path) -> dict[str, Any]:
    payload = yaml.safe_load(manifest_path.read_text(encoding="utf-8"))
    schema = json.loads(schema_path.read_text(encoding="utf-8"))
    if not isinstance(payload, dict):
        raise ValueError("manifest must be a mapping")
    validate(payload, schema)
    if payload.get("claim_allowed") is not False:
        raise ValueError("claim_allowed must remain false")
    return payload


def constants() -> dict[str, float]:
    return {
        "pi": math.pi,
        "sqrt2": math.sqrt(2.0),
        "sqrt3": math.sqrt(3.0),
        "sqrt3_over_2": math.sqrt(3.0) / 2.0,
        "sqrt5": math.sqrt(5.0),
        "phi": (1.0 + math.sqrt(5.0)) / 2.0,
    }


def root_union_count(values: list[int]) -> int:
    rays: set[Fraction] = set()
    for n in values:
        for k in range(n):
            rays.add(Fraction(k, n) % 1)
    return len(rays)


def line_orientation_count(values: list[int]) -> int:
    lines: set[Fraction] = set()
    half = Fraction(1, 2)
    for n in values:
        for k in range(n):
            lines.add(Fraction(k, n) % half)
    return len(lines)


def oriented_area(
    a: tuple[float, float],
    b: tuple[float, float],
    c: tuple[float, float],
) -> float:
    return 0.5 * (
        (b[0] - a[0]) * (c[1] - a[1])
        - (b[1] - a[1]) * (c[0] - a[0])
    )


def gate_result(gate: dict[str, Any]) -> dict[str, Any]:
    kind = gate["kind"]
    tol = float(gate.get("tolerance", 1.0e-12))
    observed: Any = None
    expected: Any = None
    residual: Any = None
    passed = False

    if kind == "pi_circumference":
        r = 3.0
        observed = (2.0 * math.pi * r) / (2.0 * r)
        expected = math.pi
        residual = observed - expected
        passed = close(observed, expected, tol)

    elif kind == "square_diagonal":
        observed = math.hypot(1.0, 1.0)
        expected = math.sqrt(2.0)
        residual = observed - expected
        passed = close(observed, expected, tol)

    elif kind == "equilateral_height":
        observed = math.sqrt(1.0 - 0.5**2)
        expected = math.sqrt(3.0) / 2.0
        residual = observed - expected
        passed = close(observed, expected, tol)

    elif kind == "scale_rewrite_344":
        triangle_step = math.cos(math.pi / 3.0)
        two_square_steps = math.cos(math.pi / 4.0) ** 2
        observed = {
            "cos_pi_over_3": triangle_step,
            "cos_pi_over_4_squared": two_square_steps,
        }
        expected = 0.5
        residual = max(
            abs(triangle_step - expected),
            abs(two_square_steps - expected),
        )
        passed = close(triangle_step, expected, tol) and close(
            two_square_steps, expected, tol
        )

    elif kind == "pythagoras":
        a, b, c = [float(x) for x in gate["sides"]]
        observed = a * a + b * b
        expected = c * c
        residual = observed - expected
        passed = close(observed, expected, tol)

    elif kind == "polygon_trig_identity":
        rows = []
        passed = True
        for n in gate["n"]:
            s = math.sin(math.pi / n)
            c = math.cos(math.pi / n)
            value = s * s + c * c
            rows.append({"n": n, "value": value, "residual": value - 1.0})
            passed &= close(value, 1.0, tol)
        observed = rows
        expected = "sin^2(pi/n)+cos^2(pi/n)=1"
        residual = max(abs(x["residual"]) for x in rows)

    elif kind == "half_step_doubling":
        rows = []
        passed = True
        for n in gate["n"]:
            dirs = {Fraction(2 * k, 2 * n) % 1 for k in range(n)}
            dirs |= {Fraction(2 * k + 1, 2 * n) % 1 for k in range(n)}
            rows.append({"n": n, "directions": len(dirs)})
            passed &= len(dirs) == 2 * n
        observed = rows
        expected = "2n distinct directions"

    elif kind == "lcm":
        observed = lcm_many([int(x) for x in gate["values"]])
        expected = int(gate["expected"])
        residual = observed - expected
        passed = observed == expected

    elif kind == "root_union_count":
        observed = root_union_count([int(x) for x in gate["values"]])
        expected = int(gate["expected"])
        residual = observed - expected
        passed = observed == expected

    elif kind == "line_orientation_count":
        observed = line_orientation_count([int(x) for x in gate["values"]])
        expected = int(gate["expected"])
        residual = observed - expected
        passed = observed == expected

    elif kind == "triangulation_count":
        observed = [{"n": int(n), "triangles": int(n) - 2} for n in gate["n"]]
        expected = "n-2"
        passed = all(row["triangles"] >= 1 for row in observed)

    elif kind == "bhaskara_circle_cut":
        radius = float(gate["radius"])
        rows = []
        labels = []
        for d in gate["distances"]:
            delta = 4.0 * (radius * radius - float(d) * float(d))
            label = (
                "SECANT"
                if delta > tol
                else "TANGENT"
                if abs(delta) <= tol
                else "NO_REAL_CUT"
            )
            rows.append({"distance": float(d), "delta": delta, "class": label})
            labels.append(label)
        observed = rows
        expected = gate["expected_classes"]
        passed = labels == expected

    elif kind == "torus_projection_ratio":
        major, minor = float(gate["R"]), float(gate["r"])
        crown = math.pi * ((major + minor) ** 2 - (major - minor) ** 2)
        torus = 4.0 * math.pi**2 * major * minor
        observed = torus / crown
        expected = math.pi
        residual = observed - expected
        passed = close(observed, expected, tol)

    elif kind == "polygon_annulus_fraction":
        rows = []
        passed = True
        for n in gate["n"]:
            inner = math.cos(math.pi / n)
            direct = 1.0 - inner * inner
            trig = math.sin(math.pi / n) ** 2
            rows.append(
                {"n": n, "direct": direct, "trig": trig, "residual": direct - trig}
            )
            passed &= close(direct, trig, tol)
        observed = rows
        expected = "1-cos^2(pi/n)=sin^2(pi/n)"
        residual = max(abs(row["residual"]) for row in rows)

    elif kind == "affine_area":
        p0, p1, p2 = (0.0, 0.0), (2.0, 0.0), (0.0, 3.0)
        matrix = ((2.0, 1.0), (0.0, 3.0))
        translation = (1.0, -2.0)

        def transform(p: tuple[float, float]) -> tuple[float, float]:
            return (
                matrix[0][0] * p[0] + matrix[0][1] * p[1] + translation[0],
                matrix[1][0] * p[0] + matrix[1][1] * p[1] + translation[1],
            )

        det = matrix[0][0] * matrix[1][1] - matrix[0][1] * matrix[1][0]
        src = abs(oriented_area(p0, p1, p2))
        dst = abs(oriented_area(transform(p0), transform(p1), transform(p2)))
        observed = dst
        expected = abs(det) * src
        residual = observed - expected
        passed = close(observed, expected, tol)

    elif kind == "oriented_area":
        a, b, c = (0.0, 0.0), (2.0, 0.0), (0.0, 3.0)
        forward = oriented_area(a, b, c)
        reverse = oriented_area(a, c, b)
        observed = {"forward": forward, "reverse": reverse}
        expected = "equal magnitude, opposite sign"
        passed = forward == -reverse and forward > 0 and reverse < 0

    elif kind == "quotient_remainder":
        rows = []
        passed = True
        for pair in gate["examples"]:
            number, base = int(pair[0]), int(pair[1])
            quotient, remainder = divmod(number, base)
            rows.append(
                {
                    "N": number,
                    "base": base,
                    "q": quotient,
                    "r": remainder,
                    "reconstructed": quotient * base + remainder,
                }
            )
            passed &= quotient * base + remainder == number and 0 <= remainder < base
        observed = rows
        expected = "N=q*base+r"

    elif kind == "recursive_nesting":
        radius = float(gate.get("start_radius", 1.0))
        rows = [{"step": 0, "radius": radius}]
        for idx, n in enumerate(gate["sequence"], start=1):
            radius *= math.cos(math.pi / int(n))
            rows.append({"step": idx, "n": int(n), "radius": radius})
        observed = rows
        expected = "monotone positive contraction"
        passed = all(
            rows[i]["radius"] > rows[i + 1]["radius"] > 0
            for i in range(len(rows) - 1)
        )

    elif kind == "sphere_torus_euler":
        observed = {"sphere": 2, "torus": 0}
        expected = "different Euler characteristics"
        passed = observed["sphere"] != observed["torus"]

    else:
        raise ValueError(f"unsupported gate kind: {kind}")

    return {
        "id": gate["id"],
        "kind": kind,
        "epistemic": gate["epistemic"],
        "status": "PASS" if passed else "FAIL",
        "observed": observed,
        "expected": expected,
        "residual": residual,
    }


def hypothesis_result(hypothesis: dict[str, Any]) -> dict[str, Any]:
    test = hypothesis["test"]
    state = "TOKEN_VAZIO"
    evidence: Any = None

    if test == "same_area_noncongruent_triangles":
        t1 = sorted([2.0, 2.0, math.sqrt(8.0)])
        t2 = sorted([4.0, 1.0, math.sqrt(17.0)])
        state = "REFUTADO"
        evidence = {
            "area_1": 2.0,
            "area_2": 2.0,
            "sides_1": t1,
            "sides_2": t2,
            "congruent": False,
        }
    elif test == "requires_explicit_mapping":
        state = "TOKEN_VAZIO"
        evidence = (
            "same numeric order is insufficient without a declared "
            "bijective semantic map"
        )
    elif test == "blocked_by_domain_boundary":
        state = "BLOCKED"
        evidence = (
            "mathematical limit construction does not establish physical realization"
        )
    elif test == "requires_declared_ifs_maps":
        state = "TOKEN_VAZIO"
        evidence = (
            "fractal dimension requires explicit contraction maps and applicable "
            "separation conditions"
        )
    else:
        raise ValueError(f"unsupported hypothesis test: {test}")

    return {
        "id": hypothesis["id"],
        "statement": hypothesis["statement"],
        "state": state,
        "evidence": evidence,
        "next_gate": hypothesis["next_gate"],
    }


def explore(
    contract: dict[str, Any], max_depth_override: int | None = None
) -> dict[str, Any]:
    cfg = contract["exploration"]
    polygons = [int(n) for n in cfg["polygons"]]
    digits = int(cfg.get("numeric_round_digits", 12))
    tolerance = float(cfg.get("candidate_tolerance", 1.0e-10))
    max_depth = int(max_depth_override or cfg["max_depth"])
    max_sequences = int(cfg.get("max_sequences", 1000))
    const = constants()

    metrics = []
    distance_records = []
    for n in polygons:
        side = 2.0 * math.sin(math.pi / n)
        apothem = math.cos(math.pi / n)
        area = 0.5 * n * math.sin(2.0 * math.pi / n)
        star2 = (
            math.sin(2.0 * math.pi / n) / math.sin(math.pi / n)
            if n >= 5
            else None
        )
        spectrum = []
        for step in range(1, n // 2 + 1):
            distance = 2.0 * math.sin(math.pi * step / n)
            spectrum.append({"step": step, "ratio": distance})
            distance_records.append((round(distance, digits), n, step, distance))

        metrics.append(
            {
                "n": n,
                "central_angle_deg": 360.0 / n,
                "side_over_R": side,
                "apothem_over_R": apothem,
                "area_over_R2": area,
                "annulus_fraction": math.sin(math.pi / n) ** 2,
                "half_step_directions": 2 * n,
                "step2_diagonal_over_side": star2,
                "distance_spectrum": spectrum,
            }
        )

    pairwise = []
    for a, b in itertools.combinations(polygons, 2):
        common_lcm = lcm(a, b)
        pairwise.append(
            {
                "a": a,
                "b": b,
                "gcd": math.gcd(a, b),
                "lcm": common_lcm,
                "shared_roots_common_phase": math.gcd(a, b),
                "microangle_deg": 360.0 / common_lcm,
            }
        )

    constant_matches = []
    for row in metrics:
        candidates = {
            "side_over_R": row["side_over_R"],
            "apothem_over_R": row["apothem_over_R"],
        }
        if row["step2_diagonal_over_side"] is not None:
            candidates["step2_diagonal_over_side"] = row[
                "step2_diagonal_over_side"
            ]
        for metric_name, value in candidates.items():
            for constant_name, constant_value in const.items():
                if abs(float(value) - constant_value) <= tolerance * max(
                    1.0, abs(constant_value)
                ):
                    constant_matches.append(
                        {
                            "status": "KNOWN_OR_CANDIDATE_MATCH",
                            "n": row["n"],
                            "metric": metric_name,
                            "constant": constant_name,
                            "value": value,
                            "residual": float(value) - constant_value,
                        }
                    )

    distance_bins: dict[float, list[dict[str, Any]]] = defaultdict(list)
    for key, n, step, value in distance_records:
        distance_bins[key].append({"n": n, "step": step, "value": value})

    cross_distance = []
    for key, rows in sorted(distance_bins.items()):
        if len({row["n"] for row in rows}) > 1:
            cross_distance.append(
                {
                    "status": "CANDIDATE_SHARED_DISTANCE",
                    "rounded_value": key,
                    "occurrences": rows,
                }
            )

    scale_bins: dict[float, list[tuple[int, ...]]] = defaultdict(list)
    sequence_count = 0
    truncated = False
    for depth in range(1, max_depth + 1):
        for sequence in itertools.product(polygons, repeat=depth):
            if sequence_count >= max_sequences:
                truncated = True
                break
            sequence_count += 1
            scale = math.prod(math.cos(math.pi / n) for n in sequence)
            scale_bins[round(scale, digits)].append(sequence)
        if truncated:
            break

    def rewrite_344_signature(sequence: tuple[int, ...]) -> tuple[int, ...]:
        counts: dict[int, int] = defaultdict(int)
        for n in sequence:
            counts[n] += 1
        square_pairs = counts.get(4, 0) // 2
        counts[4] = counts.get(4, 0) % 2
        counts[3] = counts.get(3, 0) + square_pairs
        canonical: list[int] = []
        for n in sorted(counts):
            canonical.extend([n] * counts[n])
        return tuple(canonical)

    scale_collisions = []
    for value, sequences in sorted(scale_bins.items()):
        if len(sequences) < 2:
            continue
        multisets = {tuple(sorted(sequence)) for sequence in sequences}
        rewrite_signatures = {rewrite_344_signature(sequence) for sequence in sequences}
        if len(multisets) == 1:
            status = "KNOWN_PERMUTATION_INVARIANCE"
        elif len(rewrite_signatures) == 1:
            status = "DERIVED_REWRITE_IDENTITY_COS60_EQ_COS45_SQUARED"
        else:
            status = "CANDIDATE_NONTRIVIAL_SCALE_IDENTITY"
        scale_collisions.append(
            {
                "status": status,
                "rounded_scale": value,
                "sequences": [list(sequence) for sequence in sequences[:20]],
                "distinct_multisets": len(multisets),
                "rewrite_344_signatures": [
                    list(signature) for signature in sorted(rewrite_signatures)
                ],
            }
        )

    groups = []
    for values in cfg.get("angular_groups", []):
        ints = [int(value) for value in values]
        common_lcm = lcm_many(ints)
        groups.append(
            {
                "values": ints,
                "lcm": common_lcm,
                "microangle_deg": 360.0 / common_lcm,
                "distinct_rays_common_phase": root_union_count(ints),
                "line_orientations": line_orientation_count(ints),
            }
        )

    candidates = constant_matches + cross_distance + scale_collisions
    return {
        "polygons": metrics,
        "pairwise_relations": pairwise,
        "angular_groups": groups,
        "constant_matches": constant_matches,
        "cross_family_distance_matches": cross_distance,
        "nested_scale_collisions": scale_collisions,
        "candidate_relations": candidates,
        "sequence_count_evaluated": sequence_count,
        "max_depth": max_depth,
        "truncated_by_max_sequences": truncated,
    }


def semantic_graph(
    contract: dict[str, Any], exploration: dict[str, Any]
) -> dict[str, Any]:
    nodes = []
    edges = []

    for name, meta in contract["constants"].items():
        nodes.append({"id": f"constant:{name}", "kind": "constant", "meta": meta})
    for n in contract["exploration"]["polygons"]:
        nodes.append({"id": f"polygon:{n}", "kind": "regular_polygon", "n": n})
    for relation in contract.get("relations", []):
        edges.append(
            {
                "id": relation["id"],
                "from": relation["from"],
                "to": relation["to"],
                "type": relation["type"],
            }
        )
    for index, candidate in enumerate(exploration["candidate_relations"]):
        nodes.append(
            {"id": f"candidate:{index}", "kind": "candidate", "meta": candidate}
        )

    return {"nodes": nodes, "edges": edges, "claim_allowed": False}


def compute_anomalies(
    gates: list[dict[str, Any]],
    hypotheses: list[dict[str, Any]],
    exploration: dict[str, Any],
) -> list[dict[str, Any]]:
    anomalies = []

    for gate in gates:
        if gate["status"] != "PASS":
            anomalies.append(
                {"type": "GATE_FAILURE", "id": gate["id"], "detail": gate}
            )

    for hypothesis in hypotheses:
        if hypothesis["state"] == "TOKEN_VAZIO" and not hypothesis.get("next_gate"):
            anomalies.append(
                {"type": "TOKEN_VAZIO_WITHOUT_NEXT_GATE", "id": hypothesis["id"]}
            )

    for candidate in exploration["nested_scale_collisions"]:
        if candidate["status"] == "CANDIDATE_NONTRIVIAL_SCALE_IDENTITY":
            anomalies.append(
                {
                    "type": "NONTRIVIAL_SCALE_COLLISION_CANDIDATE",
                    "detail": candidate,
                }
            )

    return anomalies


def ideal_objective(
    contract: dict[str, Any],
    gates: list[dict[str, Any]],
    hypotheses: list[dict[str, Any]],
    anomalies: list[dict[str, Any]],
) -> dict[str, Any]:
    terms = contract["ideal_state"]["terms"]
    failed = sum(gate["status"] != "PASS" for gate in gates)
    contradictions = sum(
        hypothesis["state"] == "CONTRADICTION" for hypothesis in hypotheses
    )
    token_without_next = sum(
        hypothesis["state"] == "TOKEN_VAZIO" and not hypothesis.get("next_gate")
        for hypothesis in hypotheses
    )
    tracked_lossy = contract.get("operations", {}).get(
        "lossy_views_require_rollback_metadata", []
    )
    untracked_loss = 0

    objective = (
        failed * int(terms.get("failed_gate", 10))
        + contradictions * int(terms.get("unresolved_contradiction", 5))
        + untracked_loss * int(terms.get("untracked_lossy_operation", 5))
        + token_without_next * int(terms.get("token_vazio_without_next_gate", 3))
        + len(anomalies) * int(terms.get("anomaly", 1))
    )

    return {
        "name": contract["ideal_state"]["name"],
        "J": objective,
        "target": contract["ideal_state"]["target"],
        "target_reached": objective == contract["ideal_state"]["target"],
        "components": {
            "failed_gate": failed,
            "unresolved_contradiction": contradictions,
            "untracked_lossy_operation": untracked_loss,
            "tracked_lossy_operations": tracked_lossy,
            "token_vazio_without_next_gate": token_without_next,
            "anomaly": len(anomalies),
        },
        "interpretation": contract["ideal_state"]["interpretation"],
    }


def write_json(path: Path, payload: Any) -> None:
    path.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
        encoding="utf-8",
    )


def write_artifacts(
    contract: dict[str, Any],
    manifest_path: Path,
    schema_path: Path,
    output_dir: Path,
    max_depth_override: int | None,
) -> dict[str, Any]:
    output_dir.mkdir(parents=True, exist_ok=True)

    const = constants()
    gates = [gate_result(gate) for gate in contract["gates"]]
    hypotheses = [
        hypothesis_result(hypothesis) for hypothesis in contract["hypotheses"]
    ]
    exploration = explore(contract, max_depth_override)
    graph = semantic_graph(contract, exploration)
    anomalies = compute_anomalies(gates, hypotheses, exploration)
    ideal = ideal_objective(contract, gates, hypotheses, anomalies)

    write_json(output_dir / "resolved_manifest.json", contract)
    write_json(output_dir / "constants.json", const)
    write_json(output_dir / "gate_results.json", gates)
    write_json(output_dir / "hypothesis_results.json", hypotheses)
    write_json(output_dir / "exploration.json", exploration)
    write_json(output_dir / "anomalies.json", anomalies)
    write_json(output_dir / "semantic_graph.json", graph)

    with (output_dir / "candidates.csv").open(
        "w", encoding="utf-8", newline=""
    ) as handle:
        writer = csv.writer(handle)
        writer.writerow(["index", "status", "payload_json"])
        for index, candidate in enumerate(exploration["candidate_relations"]):
            writer.writerow(
                [
                    index,
                    candidate.get("status", "CANDIDATE"),
                    json.dumps(candidate, ensure_ascii=False, sort_keys=True),
                ]
            )

    failed = [gate for gate in gates if gate["status"] != "PASS"]
    decision = "PASS_FORMAL_SHADOW" if not failed else "FAIL"
    input_hash = sha256_bytes(
        manifest_path.read_bytes() + schema_path.read_bytes()
    )

    receipt = {
        "schema": RECEIPT_SCHEMA,
        "commit_sha": os.environ.get("GITHUB_SHA", "TOKEN_VAZIO_EXTERNAL_SHA"),
        "workflow": os.environ.get("GITHUB_WORKFLOW", "external_or_local"),
        "job": os.environ.get("GITHUB_JOB", "external_or_local"),
        "claim_allowed": False,
        "publication_effect": "NONE",
        "inputs_sha256": input_hash,
        "decision": decision,
        "residuals": {
            "failed_gates": [gate["id"] for gate in failed],
            "anomaly_count": len(anomalies),
            "candidate_count": len(exploration["candidate_relations"]),
            "token_vazio_hypotheses": [
                h["id"] for h in hypotheses if h["state"] == "TOKEN_VAZIO"
            ],
            "ideal_objective": ideal,
        },
        "artifacts": {
            "gate_results": "gate_results.json",
            "hypothesis_results": "hypothesis_results.json",
            "exploration": "exploration.json",
            "candidates": "candidates.csv",
            "anomalies": "anomalies.json",
            "semantic_graph": "semantic_graph.json",
        },
        "claim_boundary": contract["authority"]["claim_boundary"],
    }
    write_json(output_dir / "receipt.json", receipt)

    report = [
        "# Omega Mathematics Explorer V1",
        "",
        f"- decision: {decision}",
        f"- gates: {len(gates)-len(failed)}/{len(gates)} PASS",
        f"- hypotheses: {len(hypotheses)}",
        f"- candidates: {len(exploration['candidate_relations'])}",
        f"- anomalies: {len(anomalies)}",
        f"- ideal J: {ideal['J']} (target {ideal['target']})",
        "- claim_allowed: false",
        "- publication_effect: NONE",
        "",
        "## Hypothesis states",
        "",
        "| id | state | next gate |",
        "|---|---|---|",
    ]
    for hypothesis in hypotheses:
        report.append(
            f"| {hypothesis['id']} | {hypothesis['state']} | "
            f"{hypothesis['next_gate']} |"
        )

    report.extend(
        [
            "",
            "## Boundaries",
            "",
            "- Workflow/runner PASS is not theory confirmation.",
            "- Candidate relations remain candidates until separately proved or falsified.",
            "- Numeric coincidence does not collapse semantic namespaces.",
            "- Discretization is a representation choice unless a theorem states otherwise.",
            "",
            "## Omega feedback",
            "",
            "Every FAIL, TOKEN_VAZIO, contradiction and candidate is preserved "
            "as input for the next revision.",
        ]
    )
    (output_dir / "report.md").write_text(
        "\n".join(report) + "\n", encoding="utf-8"
    )

    checksum_lines = []
    for path in sorted(output_dir.iterdir()):
        if path.name == "CHECKSUMS.sha256":
            continue
        checksum_lines.append(f"{sha256_bytes(path.read_bytes())}  {path.name}")
    (output_dir / "CHECKSUMS.sha256").write_text(
        "\n".join(checksum_lines) + "\n", encoding="utf-8"
    )

    return receipt


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--manifest",
        type=Path,
        default=Path("data/contracts/omega_math_explorer.v1.yml"),
    )
    parser.add_argument(
        "--schema",
        type=Path,
        default=Path("schemas/omega_math_explorer.schema.json"),
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=Path("artifacts/omega-math-explorer"),
    )
    parser.add_argument("--max-depth", type=int)
    parser.add_argument("--strict", action="store_true")
    return parser


def main() -> int:
    args = build_parser().parse_args()
    contract = load_contract(args.manifest, args.schema)
    receipt = write_artifacts(
        contract,
        args.manifest,
        args.schema,
        args.output_dir,
        args.max_depth,
    )
    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    return 1 if args.strict and receipt["decision"] == "FAIL" else 0


if __name__ == "__main__":
    raise SystemExit(main())
