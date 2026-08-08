#!/usr/bin/env python3
from __future__ import annotations

"""Evaluate the released DESI DR2 all-tracer BAO likelihood at frozen controls.

This is intentionally a likelihood-level probe, not a posterior or joint
cross-block reproduction. It proves that the released Cobaya likelihood can be
executed with a pinned Boltzmann backend and preserves exact log-likelihood
values for fixed, declared cosmologies.
"""

import argparse
import importlib.metadata
import json
import os
import tempfile
from pathlib import Path
from typing import Any, Callable, Sequence

SCHEMA = "rll.desi_dr2_reference_loglike_probe.v1"
LIKELIHOOD = "bao.desi_dr2"
LIKELIHOOD_CLASS = "bao.desi_dr2.desi_bao_all"

CONTROL_POINTS: tuple[dict[str, Any], ...] = (
    {
        "id": "lcdm_plancklike_control",
        "model": "LCDM",
        "params": {
            "ombh2": 0.02237,
            "omch2": 0.1200,
            "H0": 67.4,
            "As": 2.10e-9,
            "ns": 0.965,
            "tau": 0.0544,
            "mnu": 0.06,
            "nnu": 3.044,
        },
    },
    {
        "id": "lcdm_high_h0_stress_control",
        "model": "LCDM",
        "params": {
            "ombh2": 0.02237,
            "omch2": 0.1200,
            "H0": 73.04,
            "As": 2.10e-9,
            "ns": 0.965,
            "tau": 0.0544,
            "mnu": 0.06,
            "nnu": 3.044,
        },
    },
    {
        "id": "cpl_nonlambda_control",
        "model": "CPL",
        "params": {
            "ombh2": 0.02237,
            "omch2": 0.1200,
            "H0": 68.0,
            "As": 2.10e-9,
            "ns": 0.965,
            "tau": 0.0544,
            "mnu": 0.06,
            "nnu": 3.044,
            "w": -0.9,
            "wa": -0.3,
        },
    },
)


def cobaya_loglike(packages_path: Path, point: dict[str, Any]) -> float:
    from cobaya.model import get_model

    params = dict(point["params"])
    theory: dict[str, Any] = {
        "camb": {
            "extra_args": {
                "lens_potential_accuracy": 0,
                "num_massive_neutrinos": 1,
                "nnu": params.get("nnu", 3.044),
            }
        }
    }
    info = {
        "packages_path": str(packages_path),
        "params": params,
        "theory": theory,
        "likelihood": {LIKELIHOOD: None},
        "debug": False,
    }
    model = get_model(info)
    values, derived = model.loglikes({})
    if len(values) != 1:
        raise RuntimeError(f"expected one DESI loglike, got {len(values)}")
    return float(values[0])


def build(
    packages_path: Path,
    evaluator: Callable[[Path, dict[str, Any]], float] = cobaya_loglike,
) -> dict[str, Any]:
    if not packages_path.is_dir():
        raise ValueError("Cobaya packages path missing")
    rows = []
    for point in CONTROL_POINTS:
        value = float(evaluator(packages_path, point))
        if not (-1.0e100 < value < 1.0e100):
            raise ValueError(f"non-finite/invalid loglike for {point['id']}: {value}")
        rows.append({
            "id": point["id"],
            "model": point["model"],
            "params": point["params"],
            "loglike": value,
        })
    return {
        "schema": SCHEMA,
        "state": "DESI_DR2_ALL_TRACER_FIXED_COSMOLOGY_LOGLIKES_EXECUTED",
        "claim_allowed": False,
        "publication_ready": False,
        "token": "TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION",
        "likelihood": {
            "cobaya_component": LIKELIHOOD,
            "class": LIKELIHOOD_CLASS,
            "scope": "DESI DR2 all-tracer BAO only",
            "cobaya_version": importlib.metadata.version("cobaya") if evaluator is cobaya_loglike else "INJECTED_TEST_EVALUATOR",
            "camb_version": importlib.metadata.version("camb") if evaluator is cobaya_loglike else "INJECTED_TEST_EVALUATOR",
        },
        "control_points": rows,
        "resolved_token": None,
        "reduces_token": "TOKEN_VAZIO_DESI_DR2_OFFICIAL_JOINT_CROSSBLOCK_REPRODUCTION",
        "remaining_close_conditions": [
            "freeze an official/published reference value or posterior target rather than only arbitrary control cosmologies",
            "verify observable ordering and covariance files against the DESI DR2 release authority",
            "reproduce the intended LCDM/CPL posterior or joint analysis with pinned priors and sampler diagnostics",
            "audit cross-probe overlap/covariance before use in a multi-probe Bayes factor",
        ],
        "scientific_boundary": (
            "A finite executable BAO log-likelihood at frozen controls proves likelihood plumbing and data custody. "
            "It is not an official joint/cross-block posterior reproduction and provides no RLL evidence by itself."
        ),
    }


def atomic_json(path: Path, payload: dict[str, Any]) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with tempfile.NamedTemporaryFile("w", encoding="utf-8", dir=path.parent, delete=False) as handle:
        tmp = Path(handle.name)
        json.dump(payload, handle, indent=2, sort_keys=True, allow_nan=False)
        handle.write("\n")
        handle.flush()
        os.fsync(handle.fileno())
    try:
        os.replace(tmp, path)
    finally:
        tmp.unlink(missing_ok=True)


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("--packages-path", type=Path, required=True)
    parser.add_argument("--output", type=Path, required=True)
    args = parser.parse_args(argv)
    payload = build(args.packages_path)
    atomic_json(args.output, payload)
    print(json.dumps({
        "state": payload["state"],
        "loglikes": {row["id"]: row["loglike"] for row in payload["control_points"]},
        "claim_allowed": False,
    }, sort_keys=True))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
