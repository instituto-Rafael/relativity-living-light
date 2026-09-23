"""Canonical stdlib-only execution fabric for RLL/Rx."""
from __future__ import annotations

import hashlib
import json
import os
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

from .contracts import load_contracts, require_contract
from .dispersion import route_dispersion
from .formula_selector import load_formula_bindings, select_formulas
from .kernel import dump_json
from .region_router import classify_region
from .yaml_subset import load as load_yaml_subset

ROOT = Path(__file__).resolve().parents[1]

ROUTES = {
    "rx_validation": "validacao_real.run_rx_pipeline",
    "rx_multiprobe": "validacao_real.run_rx_multiprobe",
    "structure_d_rx": "data.pipelines.structure_d.joint_real_likelihood_rx",
}


def _inside_root(path):
    path = Path(path).resolve()
    root = ROOT.resolve()
    try:
        path.relative_to(root)
    except ValueError as exc:
        raise ValueError("path escapes repository root: %s" % path) from exc
    return path


def _repo_path(value):
    path = Path(value)
    if not path.is_absolute():
        path = ROOT / path
    return _inside_root(path)


def _sha256_bytes(data):
    return hashlib.sha256(data).hexdigest()


def _sha256_file(path):
    return _sha256_bytes(Path(path).read_bytes())


def load_execution_plan(path):
    plan_path = _repo_path(path)
    payload = load_yaml_subset(plan_path)
    if not isinstance(payload, dict):
        raise ValueError("execution plan must be a mapping")
    if payload.get("schema") != "rll.rx.execution_plan.v1":
        raise ValueError("unsupported execution plan schema")
    if payload.get("claim_allowed") is not False:
        raise ValueError("execution plan must be fail-closed with claim_allowed=false")
    run = payload.get("run")
    if not isinstance(run, dict) or not str(run.get("id", "")).strip():
        raise ValueError("execution plan requires run.id")
    if not isinstance(payload.get("region"), dict):
        raise ValueError("execution plan requires region mapping")
    if not isinstance(payload.get("observables"), list):
        raise ValueError("execution plan requires observables list")
    if not isinstance(payload.get("dispersion"), dict):
        raise ValueError("execution plan requires dispersion mapping")
    return plan_path, payload


def _run_route(route_id):
    if route_id not in ROUTES:
        raise ValueError("route is not whitelisted: %s" % route_id)
    module = ROUTES[route_id]
    process = subprocess.run(
        [sys.executable, "-m", module],
        cwd=str(ROOT),
        capture_output=True,
        text=True,
        check=False,
        env=dict(os.environ),
    )
    stdout = process.stdout or ""
    stderr = process.stderr or ""
    return {
        "route_id": route_id,
        "module": module,
        "returncode": process.returncode,
        "status": "PASS" if process.returncode == 0 else "FAIL",
        "stdout_sha256": _sha256_bytes(stdout.encode("utf-8")),
        "stderr_sha256": _sha256_bytes(stderr.encode("utf-8")),
        "stdout_tail": stdout.splitlines()[-40:],
        "stderr_tail": stderr.splitlines()[-40:],
    }


def _source_manifest(paths):
    rows = []
    for path in paths:
        path = _repo_path(path)
        if not path.exists():
            rows.append({
                "path": str(path.relative_to(ROOT)),
                "state": "TOKEN_VAZIO_MISSING",
                "sha256": "TOKEN_VAZIO",
            })
            continue
        rows.append({
            "path": str(path.relative_to(ROOT)),
            "state": "PRESENT",
            "sha256": _sha256_file(path),
        })
    return rows


def _write_checksums(output_dir, names):
    lines = []
    for name in names:
        path = output_dir / name
        if path.exists():
            lines.append("%s  %s" % (_sha256_file(path), name))
    (output_dir / "checksums.sha256").write_text("\n".join(lines) + "\n", encoding="utf-8")


def orchestrate(plan_path="configs/rll_execution_plan.v1.yml", execute=True, output_root=None):
    plan_path, plan = load_execution_plan(plan_path)
    contract_id = str(plan.get("physics_contract", ""))
    if not contract_id:
        raise ValueError("physics_contract is required")
    contract = require_contract(contract_id)

    region = classify_region(plan["region"])
    dispersion = route_dispersion(plan["dispersion"])

    registry_path = _repo_path(plan.get("formula_registry"))
    registry = load_formula_bindings(registry_path)
    selection = select_formulas(
        registry,
        region["regimes"],
        plan["observables"],
        dispersion,
    )

    run_id = str(plan["run"]["id"])
    if not all(ch.isalnum() or ch in "._-" for ch in run_id):
        raise ValueError("run.id contains unsupported characters")

    base_output = Path(output_root) if output_root is not None else ROOT / "results" / "rll-execution"
    output_dir = base_output / run_id
    output_dir.mkdir(parents=True, exist_ok=True)

    dump_json(output_dir / "execution_plan.json", plan)
    dump_json(output_dir / "region_classification.json", region)
    dump_json(output_dir / "selected_formulas.json", {
        "schema": selection["schema"],
        "selected_count": selection["selected_count"],
        "selected": selection["selected"],
        "boundary": selection["boundary"],
        "claim_allowed": False,
    })
    dump_json(output_dir / "rejected_formulas.json", {
        "schema": selection["schema"],
        "rejected_count": selection["rejected_count"],
        "rejected": selection["rejected"],
        "boundary": selection["boundary"],
        "claim_allowed": False,
    })
    dump_json(output_dir / "covariance_contract.json", dispersion)

    routes = (plan.get("execution") or {}).get("routes") or []
    if not isinstance(routes, list):
        raise ValueError("execution.routes must be a list")

    route_results = []
    if execute:
        for route_id in routes:
            route_results.append(_run_route(str(route_id)))
    else:
        for route_id in routes:
            if str(route_id) not in ROUTES:
                raise ValueError("route is not whitelisted: %s" % route_id)
            route_results.append({
                "route_id": str(route_id),
                "module": ROUTES[str(route_id)],
                "returncode": None,
                "status": "NOT_RUN",
            })

    contracts = load_contracts()
    canonical_v2 = contracts["contracts"].get("RX-PHYSICS-CANONICAL-V2", {})
    failures = [row for row in route_results if row["status"] == "FAIL"]
    status = "PASS" if not failures and not dispersion["blocked_reasons"] else "FAIL"

    negative_results = {
        "schema": "rll.rx.execution_negative_results.v1",
        "rejected_formula_count": selection["rejected_count"],
        "rejected_formulas": [
            {
                "formula_id": row.get("formula_id"),
                "reasons": row.get("selection_reasons", []),
            }
            for row in selection["rejected"]
        ],
        "canonical_v2_state": canonical_v2.get("state", "TOKEN_VAZIO"),
        "canonical_v2_boundary": (
            "RX-PHYSICS-CANONICAL-V2 is not silently selected. This run uses the "
            "explicit physics_contract declared in the execution plan."
        ),
        "dispersion_blocked_reasons": dispersion["blocked_reasons"],
        "route_failures": [
            {"route_id": row["route_id"], "returncode": row["returncode"]}
            for row in failures
        ],
        "claim_allowed": False,
    }
    dump_json(output_dir / "negative_results.json", negative_results)

    metrics = {
        "schema": "rll.rx.execution_metrics.v1",
        "status": status,
        "execute": bool(execute),
        "physics_contract": contract_id,
        "physics_contract_state": contract.get("state"),
        "regimes": region["regimes"],
        "primary_regime": region["primary_regime"],
        "dispersion_operator": dispersion["operator"],
        "selected_formula_count": selection["selected_count"],
        "rejected_formula_count": selection["rejected_count"],
        "routes": route_results,
        "claim_allowed": False,
    }
    dump_json(output_dir / "metrics.json", metrics)

    source_paths = [
        plan_path,
        registry_path,
        ROOT / "configs" / "rx_physics_contracts.json",
        ROOT / "data" / "governance" / "RLL_DYNAMIC_STRUCTURAL_GEOMETRY_CONTEXT_V1.json",
        ROOT / "data" / "governance" / "RLL_WORLDLINE_CASCADE_FORMULA_ROUTER_V1.json",
    ]
    source_manifest = _source_manifest(source_paths)

    manifest = {
        "schema": "rll.rx.execution_manifest.v1",
        "run_id": run_id,
        "status": status,
        "physics_contract": contract_id,
        "canonical_v2_state": canonical_v2.get("state", "TOKEN_VAZIO"),
        "source_files": source_manifest,
        "outputs": [
            "execution_plan.json",
            "region_classification.json",
            "selected_formulas.json",
            "rejected_formulas.json",
            "covariance_contract.json",
            "metrics.json",
            "negative_results.json",
            "receipt.json",
            "checksums.sha256",
        ],
        "claim_allowed": False,
    }
    dump_json(output_dir / "manifest.json", manifest)

    event_material = json.dumps(
        {
            "plan_sha256": _sha256_file(plan_path),
            "physics_contract": contract_id,
            "repo_ref": os.environ.get("GITHUB_SHA", "TOKEN_VAZIO_LOCAL_REF"),
            "run_id": run_id,
        },
        sort_keys=True,
    ).encode("utf-8")
    receipt = {
        "schema": "rll.rx.execution_receipt.v1",
        "event_id": "RXEXEC-" + _sha256_bytes(event_material)[:20],
        "generated_at_utc": datetime.now(timezone.utc).isoformat(),
        "repo_ref": os.environ.get("GITHUB_SHA", "TOKEN_VAZIO_LOCAL_REF"),
        "command": "python3 -m rx orchestrate --plan %s" % str(plan_path.relative_to(ROOT)),
        "status": status,
        "execute": bool(execute),
        "physics_contract": contract_id,
        "region_primary": region["primary_regime"],
        "regimes": region["regimes"],
        "dispersion_operator": dispersion["operator"],
        "formula_selection_basis": "declared_applicability_only",
        "route_results": route_results,
        "canonical_v2_state": canonical_v2.get("state", "TOKEN_VAZIO"),
        "training": False,
        "ai_runtime": False,
        "third_party_python_dependencies": 0,
        "claim_allowed": False,
        "rollback": "versioned additive execution fabric; legacy workflows remain preserved",
    }
    dump_json(output_dir / "receipt.json", receipt)

    _write_checksums(
        output_dir,
        [
            "execution_plan.json",
            "region_classification.json",
            "selected_formulas.json",
            "rejected_formulas.json",
            "covariance_contract.json",
            "metrics.json",
            "negative_results.json",
            "manifest.json",
            "receipt.json",
        ],
    )

    if status != "PASS":
        raise RuntimeError("Rx execution fabric failed; inspect %s" % output_dir)

    return {
        "status": status,
        "run_id": run_id,
        "output_dir": str(output_dir),
        "physics_contract": contract_id,
        "regimes": region["regimes"],
        "selected_formula_count": selection["selected_count"],
        "rejected_formula_count": selection["rejected_count"],
        "claim_allowed": False,
    }
