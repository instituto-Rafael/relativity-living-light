from __future__ import annotations

import copy
import hashlib
import json
import os
import platform
import subprocess
import sys
import time
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

import yaml
from jsonschema import Draft202012Validator

SCHEMA_NAME = "rll_evidence_experiment_v1"
RECEIPT_SCHEMA_NAME = "rll_evidence_receipt_v1"
ALLOWED_METRICS = ("chi2", "AIC", "AICc", "BIC", "N", "k", "dof")


class EvidenceError(RuntimeError):
    pass


def canonical_bytes(value: Any) -> bytes:
    return json.dumps(value, sort_keys=True, separators=(",", ":"), ensure_ascii=False).encode("utf-8")


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def sha256_file(path: Path) -> str:
    digest = hashlib.sha256()
    with path.open("rb") as handle:
        for chunk in iter(lambda: handle.read(1024 * 1024), b""):
            digest.update(chunk)
    return digest.hexdigest()


def load_json(path: Path) -> Any:
    return json.loads(path.read_text(encoding="utf-8"))


def load_yaml(path: Path) -> dict[str, Any]:
    value = yaml.safe_load(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise EvidenceError(f"experiment must be a mapping: {path}")
    return value


def resolve_paths(experiment_path: Path, repository_root: Path | None = None) -> tuple[Path, Path, Path]:
    experiment_path = experiment_path.resolve()
    if repository_root is None:
        configured = load_yaml(experiment_path).get("repository_root", ".")
        candidate = Path(str(configured))
        repository_root = candidate if candidate.is_absolute() else (experiment_path.parent / candidate).resolve()
    else:
        repository_root = repository_root.resolve()
    schema_path = repository_root / "products/rll-evidence-runner/schemas/experiment.schema.json"
    return repository_root, experiment_path, schema_path


def _schema_validate(document: dict[str, Any], schema_path: Path) -> list[str]:
    if not schema_path.exists():
        return [f"schema missing: {schema_path}"]
    validator = Draft202012Validator(load_json(schema_path))
    errors = []
    for error in sorted(validator.iter_errors(document), key=lambda item: list(item.path)):
        location = ".".join(str(part) for part in error.absolute_path) or "$"
        errors.append(f"{location}: {error.message}")
    return errors


def _safe_relative(root: Path, configured: str) -> Path:
    candidate = Path(configured)
    if candidate.is_absolute():
        raise EvidenceError(f"absolute paths are forbidden: {configured}")
    resolved = (root / candidate).resolve()
    try:
        resolved.relative_to(root.resolve())
    except ValueError as exc:
        raise EvidenceError(f"path escapes repository root: {configured}") from exc
    return resolved


def _read_sidecar(sidecar: Path) -> str | None:
    if not sidecar.exists():
        return None
    tokens = sidecar.read_text(encoding="utf-8").strip().split()
    if not tokens:
        return None
    digest = tokens[0].lower()
    if len(digest) != 64 or any(ch not in "0123456789abcdef" for ch in digest):
        return None
    return digest


def inspect_input(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    path = _safe_relative(root, str(spec["path"]))
    required = bool(spec.get("required", True))
    record: dict[str, Any] = {
        "id": spec["id"], "path": str(path.relative_to(root)), "required": required,
        "exists": path.exists(), "bytes": None, "sha256": None,
        "expected_bytes": spec.get("expected_bytes"), "expected_sha256": spec.get("expected_sha256"),
        "sidecar": spec.get("sha256_sidecar"), "state": "TOKEN_VAZIO_INPUT_MISSING", "errors": [],
    }
    if not path.exists():
        if not required:
            record["state"] = "OPTIONAL_ABSENT"
        return record
    if not path.is_file():
        record["state"] = "BLOCKED_INPUT_NOT_FILE"
        record["errors"].append("input is not a regular file")
        return record
    record["bytes"] = path.stat().st_size
    record["sha256"] = sha256_file(path)
    if spec.get("expected_bytes") is not None and record["bytes"] != int(spec["expected_bytes"]):
        record["errors"].append("byte count mismatch")
    expected_sha = spec.get("expected_sha256")
    if expected_sha and expected_sha != "TOKEN_VAZIO" and record["sha256"] != str(expected_sha).lower():
        record["errors"].append("SHA-256 mismatch")
    sidecar_name = spec.get("sha256_sidecar")
    if sidecar_name:
        sidecar_digest = _read_sidecar(_safe_relative(root, str(sidecar_name)))
        record["sidecar_sha256"] = sidecar_digest
        if sidecar_digest is None:
            record["errors"].append("missing or invalid SHA-256 sidecar")
        elif sidecar_digest != record["sha256"]:
            record["errors"].append("sidecar SHA-256 mismatch")
    record["state"] = "VERIFIED" if not record["errors"] else "BLOCKED_INPUT_INTEGRITY"
    return record


def validate_experiment(experiment_path: Path, repository_root: Path | None = None) -> dict[str, Any]:
    root, experiment_path, schema_path = resolve_paths(experiment_path, repository_root)
    document = load_yaml(experiment_path)
    schema_errors = _schema_validate(document, schema_path)
    policy_errors: list[str] = []
    if document.get("schema") != SCHEMA_NAME:
        policy_errors.append(f"schema must equal {SCHEMA_NAME}")
    if document.get("claim_allowed") is not False:
        policy_errors.append("claim_allowed must be false")
    if document.get("publication_effect") not in {"NONE", None}:
        policy_errors.append("publication_effect must be NONE")
    for step in document.get("steps", []):
        argv = step.get("argv")
        if not isinstance(argv, list) or not argv or not all(isinstance(item, str) and item for item in argv):
            policy_errors.append(f"step {step.get('id')} argv must be a non-empty string array")
        if any("\x00" in item for item in (argv or [])):
            policy_errors.append(f"step {step.get('id')} contains a NUL byte")
        for key in step.get("env", {}):
            if not str(key).replace("_", "").isalnum() or not str(key)[0].isalpha():
                policy_errors.append(f"step {step.get('id')} has invalid environment key {key!r}")
    inputs = []
    if not schema_errors:
        for spec in document.get("inputs", []):
            try:
                inputs.append(inspect_input(root, spec))
            except EvidenceError as exc:
                policy_errors.append(str(exc))
    required_inputs_ready = all(item["state"] == "VERIFIED" or not item["required"] for item in inputs) if inputs else True
    state = "VALID" if not schema_errors and not policy_errors else "INVALID"
    if state == "VALID" and not required_inputs_ready:
        state = "VALID_WITH_TOKEN_VAZIO"
    return {
        "schema": "rll_evidence_validation_v1", "experiment_id": document.get("experiment_id"),
        "state": state, "claim_allowed": False, "repository_root": str(root),
        "experiment_path": str(experiment_path), "experiment_sha256": sha256_file(experiment_path),
        "schema_errors": schema_errors, "policy_errors": policy_errors, "inputs": inputs,
        "required_inputs_ready": required_inputs_ready,
    }


def _git_commit(root: Path) -> str | None:
    try:
        result = subprocess.run(["git", "rev-parse", "HEAD"], cwd=root, check=True, capture_output=True, text=True, timeout=10)
        return result.stdout.strip()
    except (OSError, subprocess.SubprocessError):
        return None


def _run_step(root: Path, spec: dict[str, Any], default_timeout: int) -> dict[str, Any]:
    argv = [str(item) for item in spec["argv"]]
    env = os.environ.copy()
    env.update({str(k): str(v) for k, v in spec.get("env", {}).items()})
    started = time.monotonic()
    try:
        proc = subprocess.run(argv, cwd=root, env=env, capture_output=True, text=True,
                              timeout=int(spec.get("timeout_seconds", default_timeout)), shell=False)
        exit_code, stdout, stderr, timed_out = proc.returncode, proc.stdout, proc.stderr, False
    except subprocess.TimeoutExpired as exc:
        exit_code, stdout, stderr, timed_out = None, exc.stdout or "", exc.stderr or "", True
    expected_codes = [int(value) for value in spec.get("expected_exit_codes", [0])]
    state = "PASS" if not timed_out and exit_code in expected_codes else "FAIL"
    outputs = []
    for output in spec.get("outputs", []):
        path = _safe_relative(root, str(output["path"]))
        exists = path.exists() and path.is_file()
        item = {
            "path": str(path.relative_to(root)), "required": bool(output.get("required", True)), "exists": exists,
            "bytes": path.stat().st_size if exists else None, "sha256": sha256_file(path) if exists else None,
            "media_type": output.get("media_type", "application/octet-stream"),
        }
        if item["required"] and not exists:
            state = "FAIL"
        outputs.append(item)
    return {
        "id": spec["id"], "argv": argv, "required": bool(spec.get("required", True)),
        "expected_exit_codes": expected_codes, "exit_code": exit_code, "timed_out": timed_out,
        "duration_seconds": round(time.monotonic() - started, 6), "state": state,
        "stdout": stdout[-20000:], "stderr": stderr[-20000:], "outputs": outputs,
    }


def _extract_rows(root: Path, spec: dict[str, Any]) -> dict[str, Any]:
    path = _safe_relative(root, str(spec["path"]))
    result: dict[str, Any] = {"id": spec["id"], "path": str(path.relative_to(root)), "state": "TOKEN_VAZIO_RESULT", "sha256": None, "models": {}, "errors": []}
    if not path.exists():
        result["errors"].append("result artifact missing")
        return result
    try:
        rows: Any = load_json(path)
        for key in spec.get("rows_path", ["rows"]):
            rows = rows[key]
        if not isinstance(rows, list):
            raise TypeError("rows path does not resolve to a list")
        model_key = str(spec.get("model_key", "model"))
        include = set(spec.get("include_models", []))
        metrics = spec.get("metrics", list(ALLOWED_METRICS))
        for row in rows:
            if not isinstance(row, dict) or model_key not in row:
                continue
            model = str(row[model_key])
            if include and model not in include:
                continue
            result["models"][model] = {metric: row.get(metric) for metric in metrics}
        if not result["models"]:
            raise ValueError("no requested model rows found")
        result["sha256"] = sha256_file(path)
        result["state"] = "VERIFIED_LIMITED"
    except (OSError, KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        result["errors"].append(str(exc))
    return result


def _compare_models(extractions: Iterable[dict[str, Any]], comparison: dict[str, Any]) -> dict[str, Any]:
    baseline, candidate = str(comparison["baseline"]), str(comparison["candidate"])
    models: dict[str, dict[str, Any]] = {}
    for extraction in extractions:
        models.update(extraction.get("models", {}))
    state, deltas = "TOKEN_VAZIO_COMPARISON", {}
    metrics = comparison.get("metrics", ["chi2", "AIC", "AICc", "BIC"])
    if baseline in models and candidate in models:
        for metric in metrics:
            left, right = models[candidate].get(metric), models[baseline].get(metric)
            deltas[metric] = float(left) - float(right) if left is not None and right is not None else None
        state = "VERIFIED_LIMITED"
    return {
        "baseline": baseline, "candidate": candidate, "state": state, "metrics": metrics,
        "baseline_values": models.get(baseline), "candidate_values": models.get(candidate),
        "candidate_minus_baseline": deltas, "claim_allowed": False,
    }


def _semantic_payload(receipt: dict[str, Any]) -> dict[str, Any]:
    return {
        "schema": receipt["schema"], "experiment_id": receipt["experiment_id"],
        "experiment_sha256": receipt["experiment_sha256"], "commit_sha": receipt.get("commit_sha"),
        "inputs": [{key: item.get(key) for key in ("id", "path", "required", "bytes", "sha256", "state")} for item in receipt.get("inputs", [])],
        "steps": [{
            "id": item["id"], "argv": item["argv"], "required": item["required"], "exit_code": item["exit_code"],
            "timed_out": item["timed_out"], "state": item["state"],
            "outputs": [{key: out.get(key) for key in ("path", "required", "bytes", "sha256", "exists")} for out in item["outputs"]],
        } for item in receipt.get("steps", [])],
        "extractions": receipt.get("extractions", []), "comparisons": receipt.get("comparisons", []),
        "decision": receipt["decision"], "claim_allowed": False,
    }


def _receipt_hash(receipt: dict[str, Any]) -> str:
    clone = copy.deepcopy(receipt)
    clone.pop("receipt_sha256", None)
    return sha256_bytes(canonical_bytes(clone))


def run_experiment(experiment_path: Path, repository_root: Path | None = None, receipt_override: Path | None = None) -> dict[str, Any]:
    validation = validate_experiment(experiment_path, repository_root)
    if validation["state"] == "INVALID":
        raise EvidenceError("experiment validation failed: " + "; ".join(validation["schema_errors"] + validation["policy_errors"]))
    root, experiment_path, _ = resolve_paths(experiment_path, repository_root)
    document = load_yaml(experiment_path)
    steps = []
    if validation["required_inputs_ready"]:
        for spec in document.get("steps", []):
            step = _run_step(root, spec, int(document.get("execution", {}).get("timeout_seconds", 600)))
            steps.append(step)
            if step["state"] != "PASS" and step["required"]:
                break
    extractions = [_extract_rows(root, spec) for spec in document.get("result_extractors", [])]
    comparisons = [_compare_models(extractions, spec) for spec in document.get("comparisons", [])]
    if not validation["required_inputs_ready"]:
        decision_state = "TOKEN_VAZIO_REQUIRED_INPUT"
    elif any(step["required"] and step["state"] != "PASS" for step in steps):
        decision_state = "BLOCKED_EXECUTION"
    elif any(item["state"] != "VERIFIED_LIMITED" for item in extractions + comparisons):
        decision_state = "TOKEN_VAZIO_RESULT"
    else:
        decision_state = "VERIFIED_LIMITED"
    receipt: dict[str, Any] = {
        "schema": RECEIPT_SCHEMA_NAME, "created_utc": datetime.now(timezone.utc).isoformat(),
        "experiment_id": document["experiment_id"], "experiment_title": document["title"],
        "experiment_path": str(experiment_path.relative_to(root)), "experiment_sha256": sha256_file(experiment_path),
        "commit_sha": _git_commit(root),
        "runtime": {"python": sys.version, "implementation": platform.python_implementation(), "platform": platform.platform()},
        "inputs": validation["inputs"], "steps": steps, "extractions": extractions, "comparisons": comparisons,
        "decision": {"state": decision_state, "claim_allowed": False, "publication_effect": "NONE",
                     "F_ok": document.get("F_ok", []), "F_gap": document.get("F_gap", []), "F_next": document.get("F_next", [])},
        "claim_allowed": False,
    }
    receipt["semantic_sha256"] = sha256_bytes(canonical_bytes(_semantic_payload(receipt)))
    receipt["receipt_sha256"] = _receipt_hash(receipt)
    configured = receipt_override.resolve() if receipt_override else _safe_relative(root, str(document["receipt"]["path"]))
    configured.parent.mkdir(parents=True, exist_ok=True)
    configured.write_text(json.dumps(receipt, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return receipt


def verify_receipt(receipt_path: Path, repository_root: Path | None = None) -> dict[str, Any]:
    receipt_path = receipt_path.resolve()
    receipt = load_json(receipt_path)
    root = repository_root.resolve() if repository_root else Path.cwd().resolve()
    errors: list[str] = []
    if receipt.get("schema") != RECEIPT_SCHEMA_NAME:
        errors.append("receipt schema mismatch")
    if receipt.get("claim_allowed") is not False:
        errors.append("claim_allowed must be false")
    if receipt.get("receipt_sha256") != _receipt_hash(receipt):
        errors.append("receipt SHA-256 mismatch")
    if receipt.get("semantic_sha256") != sha256_bytes(canonical_bytes(_semantic_payload(receipt))):
        errors.append("semantic SHA-256 mismatch")
    checked_files = []
    for item in receipt.get("inputs", []):
        if not item.get("exists"):
            continue
        path = _safe_relative(root, str(item["path"]))
        actual = sha256_file(path) if path.exists() and path.is_file() else None
        if actual != item.get("sha256"):
            errors.append(f"input changed: {item['path']}")
        checked_files.append({"path": item["path"], "expected": item.get("sha256"), "actual": actual})
    for step in receipt.get("steps", []):
        for output in step.get("outputs", []):
            if not output.get("exists"):
                continue
            path = _safe_relative(root, str(output["path"]))
            actual = sha256_file(path) if path.exists() and path.is_file() else None
            if actual != output.get("sha256"):
                errors.append(f"output changed: {output['path']}")
            checked_files.append({"path": output["path"], "expected": output.get("sha256"), "actual": actual})
    return {"schema": "rll_evidence_receipt_verification_v1", "receipt": str(receipt_path),
            "state": "PASS" if not errors else "FAIL", "claim_allowed": False,
            "errors": errors, "checked_files": checked_files}


def compare_receipt(receipt_path: Path, baseline: str, candidate: str) -> dict[str, Any]:
    receipt = load_json(receipt_path)
    models: dict[str, dict[str, Any]] = {}
    for extraction in receipt.get("extractions", []):
        models.update(extraction.get("models", {}))
    return _compare_models([{"models": models}], {"baseline": baseline, "candidate": candidate,
                                                        "metrics": ["chi2", "AIC", "AICc", "BIC"]})
