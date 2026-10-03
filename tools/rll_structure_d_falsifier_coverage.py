#!/usr/bin/env python3
"""Fail-closed coverage gate for the Structure-D real-data scientific route.

This gate does not fit parameters and does not promote a scientific claim. It
checks that the stronger joint real-data route actually reaches the four
observational axes declared for the canonical real profile, that every model
produces finite chi-square components at a deterministic in-bounds probe point,
and that covariance prerequisites are numerically usable.

The legacy ``run_all_real.py`` route is inspected separately. Any active dataset
that it does not consume is preserved as an explicit gap rather than being
reported as used.
"""

from __future__ import annotations

import argparse
import ast
import hashlib
import json
import sys
from datetime import datetime, timezone
from pathlib import Path

import numpy as np

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from data.pipelines.structure_d import joint_real_likelihood as joint  # noqa: E402
from data.pipelines.structure_d.data_access import load_run_config  # noqa: E402

CONFIG_PATH = ROOT / "data" / "pipelines" / "structure_d" / "datasets_config.json"
LEGACY_RUNNER_PATH = ROOT / "data" / "pipelines" / "structure_d" / "run_all_real.py"
REAL_PROFILE = "structure_d_real_validation"
EXPECTED_AXES = ("Hz", "BAO", "fsigma8", "CMB_shift")
JOINT_COMPONENT_BY_AXIS = {
    "Hz": "Hz",
    "BAO": "DESI_DR2_BAO",
    "fsigma8": "fsigma8",
    "CMB_shift": "CMB_shift",
}
AXIS_BY_DATASET_ID = {
    "real_hz": "Hz",
    "real_bao": "BAO",
    "real_desi_dr2_bao": "BAO",
    "real_fsigma8": "fsigma8",
    "real_cmb_shift": "CMB_shift",
}


def _sha256(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def _midpoint_vector(bounds: list[tuple[float, float]]) -> np.ndarray:
    return np.asarray([(float(low) + float(high)) / 2.0 for low, high in bounds], dtype=float)


def _legacy_consumed_dataset_ids(path: Path = LEGACY_RUNNER_PATH) -> list[str]:
    tree = ast.parse(path.read_text(encoding="utf-8"), filename=str(path))
    main_node = next(
        (node for node in tree.body if isinstance(node, (ast.FunctionDef, ast.AsyncFunctionDef)) and node.name == "main"),
        None,
    )
    if main_node is None:
        raise RuntimeError("run_all_real.py has no main()")

    dataset_ids: set[str] = set()
    for node in ast.walk(main_node):
        if not isinstance(node, ast.Subscript):
            continue
        if not isinstance(node.value, ast.Name) or node.value.id != "datasets":
            continue
        slice_node = node.slice
        if isinstance(slice_node, ast.Constant) and isinstance(slice_node.value, str):
            dataset_ids.add(slice_node.value)
    return sorted(dataset_ids)


def _canonical_profile() -> tuple[list[str], list[str], list[str]]:
    cfg = load_run_config(str(CONFIG_PATH))
    profile = cfg.get("profiles", {}).get(REAL_PROFILE)
    if not isinstance(profile, dict):
        raise RuntimeError(f"missing profile: {REAL_PROFILE}")
    active = list(profile.get("active_datasets", []))
    axes = sorted({AXIS_BY_DATASET_ID[item] for item in active if item in AXIS_BY_DATASET_ID})
    unknown = sorted(item for item in active if item not in AXIS_BY_DATASET_ID)
    return active, axes, unknown


def _joint_source_records() -> list[dict[str, object]]:
    paths = [
        joint.HZ_PATH,
        joint.DESI_POINTS_PATH,
        joint.DESI_COV_SUMMARY_PATH,
        joint.FSIGMA8_PATH,
        joint.CMB_SHIFT_PATH,
        joint.PARAMETER_REGISTRY_PATH,
    ]
    if joint.DESI_FULL_COV_PATH.exists():
        paths.append(joint.DESI_FULL_COV_PATH)
    records = []
    for path in paths:
        records.append(
            {
                "path": str(path.relative_to(ROOT)),
                "bytes": path.stat().st_size,
                "sha256": _sha256(path),
            }
        )
    return records


def build_receipt() -> dict[str, object]:
    active_dataset_ids, profile_axes, unknown_dataset_ids = _canonical_profile()
    expected_axes = sorted(EXPECTED_AXES)

    inputs = joint.load_joint_inputs()
    covariance_info = dict(inputs["desi_covariance_info"])
    cmb_covariance = np.asarray(inputs["cmb"].get("covariance", []), dtype=float)
    cmb_covariance_ready = (
        cmb_covariance.shape == (3, 3)
        and np.allclose(cmb_covariance, cmb_covariance.T)
        and bool(np.all(np.linalg.eigvalsh(cmb_covariance) > 0.0))
    )

    model_probes: dict[str, object] = {}
    joint_components = set(JOINT_COMPONENT_BY_AXIS.values())
    probe_failures: list[str] = []
    for model in joint.MODEL_ORDER:
        vector = _midpoint_vector(joint.MODEL_BOUNDS[model])
        components = joint.evaluate_components(model, vector, inputs)
        component_keys = set(components) - {"total"}
        finite = all(np.isfinite(float(components.get(name, np.nan))) for name in joint_components | {"total"})
        non_negative = all(float(components.get(name, -1.0)) >= 0.0 for name in joint_components | {"total"})
        component_sum = float(sum(float(components[name]) for name in joint_components))
        total = float(components["total"])
        additive_close = bool(np.isclose(total, component_sum, rtol=1.0e-10, atol=1.0e-8))
        exact_components = component_keys == joint_components
        state = "PASS" if finite and non_negative and additive_close and exact_components else "FAIL"
        if state != "PASS":
            probe_failures.append(model)
        model_probes[model] = {
            "state": state,
            "probe_vector": [float(value) for value in vector],
            "components": {name: float(components[name]) for name in sorted(joint_components)},
            "total": total,
            "sum_components": component_sum,
            "finite": finite,
            "non_negative": non_negative,
            "additive_close": additive_close,
            "exact_component_set": exact_components,
        }

    legacy_consumed = _legacy_consumed_dataset_ids()
    legacy_unconsumed = sorted(set(active_dataset_ids) - set(legacy_consumed))
    legacy_extra = sorted(set(legacy_consumed) - set(active_dataset_ids))

    falsifiers = [
        {
            "id": "F-COVERAGE-01",
            "name": "canonical_profile_four_axis_coverage",
            "state": "PASS" if profile_axes == expected_axes and not unknown_dataset_ids else "FAIL",
            "observed": profile_axes,
            "expected": expected_axes,
            "unknown_dataset_ids": unknown_dataset_ids,
        },
        {
            "id": "F-COVERAGE-02",
            "name": "joint_route_model_component_finiteness",
            "state": "PASS" if not probe_failures else "FAIL",
            "failed_models": probe_failures,
        },
        {
            "id": "F-COVERAGE-03",
            "name": "desi_covariance_numerical_readiness",
            "state": "PASS" if covariance_info.get("ready") is True else "FAIL",
            "mode": covariance_info.get("mode"),
            "reason": covariance_info.get("reason"),
        },
        {
            "id": "F-COVERAGE-04",
            "name": "cmb_covariance_positive_definite",
            "state": "PASS" if cmb_covariance_ready else "FAIL",
            "shape": list(cmb_covariance.shape),
        },
        {
            "id": "F-COVERAGE-05",
            "name": "legacy_runner_exact_dataset_consumption",
            "state": "KNOWN_GAP" if legacy_unconsumed or legacy_extra else "PASS",
            "active_dataset_ids": active_dataset_ids,
            "legacy_consumed_dataset_ids": legacy_consumed,
            "unconsumed_active_dataset_ids": legacy_unconsumed,
            "legacy_extra_dataset_ids": legacy_extra,
            "claim_allowed": False,
        },
    ]

    blocking = [row["id"] for row in falsifiers if row["state"] == "FAIL"]
    gaps = [row["id"] for row in falsifiers if row["state"] == "KNOWN_GAP"]
    state = "PASS_LIMITED" if not blocking and gaps else "PASS" if not blocking else "FAIL"

    receipt = {
        "schema": "rll.structure_d.falsifier_coverage.v1",
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "state": state,
        "claim_allowed": False,
        "scientific_confirmation": False,
        "fit_executed": False,
        "purpose": (
            "Execution-path falsifier: prove observational-axis reachability, finite chi-square decomposition, "
            "and covariance readiness without treating infrastructure success as theory validation."
        ),
        "canonical_profile": {
            "profile": REAL_PROFILE,
            "active_dataset_ids": active_dataset_ids,
            "scientific_axes": profile_axes,
        },
        "preferred_full_route": {
            "module": "data.pipelines.structure_d.joint_real_likelihood",
            "components": sorted(joint_components),
            "models": list(joint.MODEL_ORDER),
            "dataset_type": "real_observational",
        },
        "legacy_route": {
            "module": "data.pipelines.structure_d.run_all_real",
            "consumed_dataset_ids": legacy_consumed,
            "unconsumed_active_dataset_ids": legacy_unconsumed,
            "claim_allowed": False,
            "note": (
                "Legacy route remains useful for its three-axis background fit, but it is not evidence of "
                "full canonical-profile consumption while active datasets remain unconsumed."
            ),
        },
        "input_sources": _joint_source_records(),
        "input_counts": {
            "hz_rows": int(len(inputs["hz"])),
            "desi_rows": int(len(inputs["desi"])),
            "fsigma8_rows": int(len(inputs["fs8"])),
            "cmb_parameters": int(len(inputs["cmb"].get("parameter_order", []))),
        },
        "covariance": {
            "desi": covariance_info,
            "cmb_positive_definite": cmb_covariance_ready,
        },
        "model_probes": model_probes,
        "falsifiers": falsifiers,
        "blocking_falsifiers": blocking,
        "known_gaps": gaps,
        "F_ok": (
            "Full joint route reaches H(z), DESI DR2 BAO, fσ8 and CMB; four-model deterministic probes are finite "
            "and component-additive; covariance prerequisites are checked."
            if not blocking
            else None
        ),
        "F_gap": (
            "Legacy run_all_real does not consume every active dataset in structure_d_real_validation."
            if "F-COVERAGE-05" in gaps
            else None
        ),
        "F_next": (
            "Promote the joint real-likelihood route as the canonical full-profile falsifier, or explicitly narrow "
            "the legacy runner profile; do not label unconsumed datasets as used."
        ),
    }
    return receipt


def _write_receipt(path: Path, payload: dict[str, object]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--output",
        default="artifacts/structure-d-falsifier-coverage/receipt.json",
        help="Receipt path relative to repository root unless absolute.",
    )
    parser.add_argument(
        "--strict-legacy",
        action="store_true",
        help="Treat the known legacy dataset-consumption gap as blocking.",
    )
    args = parser.parse_args()

    receipt = build_receipt()
    output = Path(args.output)
    if not output.is_absolute():
        output = ROOT / output
    _write_receipt(output, receipt)

    print(json.dumps(receipt, ensure_ascii=False, indent=2))
    if receipt["state"] == "FAIL":
        return 2
    if args.strict_legacy and receipt["known_gaps"]:
        return 3
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
