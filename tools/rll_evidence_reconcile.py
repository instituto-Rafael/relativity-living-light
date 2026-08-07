#!/usr/bin/env python3
"""Append-only reconciliation of claim-bounded RLL workflow artifacts."""
from __future__ import annotations
import argparse, csv, hashlib, json, re, sys, zipfile
from dataclasses import dataclass
from datetime import datetime, timezone
from pathlib import Path
from typing import Any, Iterable

SCHEMA = "rll.evidence_reconciliation.v1"
CLASSES = {"E", "C", "H", "P"}

class ReconciliationError(RuntimeError): pass

@dataclass(frozen=True)
class ArtifactBytes:
    path: Path
    sha256: str
    size_bytes: int
    members: dict[str, bytes]
    internal_checksums_valid: bool

def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with path.open("rb") as f:
        for block in iter(lambda: f.read(1 << 20), b""): h.update(block)
    return h.hexdigest()

def _member(members: dict[str, bytes], basename: str) -> bytes | None:
    hits = [v for k, v in members.items() if Path(k).name == basename]
    if len(hits) > 1: raise ReconciliationError(f"duplicate member {basename}")
    return hits[0] if hits else None

def read_artifact_zip(path: Path, expected_sha256: str | None = None) -> ArtifactBytes:
    path = path.resolve()
    if not path.is_file(): raise ReconciliationError(f"ZIP not found: {path}")
    digest = sha256_file(path)
    if expected_sha256 and digest != expected_sha256.lower():
        raise ReconciliationError(f"outer SHA mismatch: {digest} != {expected_sha256.lower()}")
    with zipfile.ZipFile(path) as z:
        bad = z.testzip()
        if bad: raise ReconciliationError(f"ZIP CRC failure: {bad}")
        members = {i.filename: z.read(i.filename) for i in z.infolist() if not i.is_dir()}
    raw = _member(members, "CHECKSUMS.sha256")
    verified = False
    if raw is not None:
        for n, line in enumerate(raw.decode().splitlines(), 1):
            if not line.strip(): continue
            m = re.fullmatch(r"([0-9a-fA-F]{64})\s+(.+)", line.strip())
            if not m: raise ReconciliationError(f"invalid checksum line {n}")
            payload = _member(members, Path(m.group(2)).name)
            if payload is None: raise ReconciliationError(f"missing checksummed member {m.group(2)}")
            if hashlib.sha256(payload).hexdigest() != m.group(1).lower():
                raise ReconciliationError(f"internal SHA mismatch: {m.group(2)}")
        verified = True
    return ArtifactBytes(path, digest, path.stat().st_size, members, verified)

def _json(a: ArtifactBytes, name: str) -> dict[str, Any]:
    raw = _member(a.members, name)
    if raw is None: raise ReconciliationError(f"missing {name}")
    try: obj = json.loads(raw)
    except Exception as e: raise ReconciliationError(f"invalid {name}: {e}") from e
    if not isinstance(obj, dict): raise ReconciliationError(f"{name} must be object")
    return obj

def _text(a: ArtifactBytes, name: str) -> str:
    raw = _member(a.members, name)
    if raw is None: raise ReconciliationError(f"missing {name}")
    return raw.decode("utf-8", "replace")

def _receipt(a: ArtifactBytes) -> list[dict[str, Any]]:
    return [{"artifact": a.path.name, "sha256": a.sha256,
             "internal_checksums_valid": a.internal_checksums_valid}]

def classify_pantheon(a: ArtifactBytes) -> dict[str, Any]:
    r, out = _json(a, "pantheon_fit_result.json"), _text(a, "fit_stdout.txt")
    keys = ("chi2_lcdm", "chi2_rll_original", "aic_lcdm", "aic_rll", "delta_aic_rll_minus_lcdm")
    ok = all(r.get(k) is not None for k in keys)
    failure = None
    if not ok:
        m = re.search(r"ModuleNotFoundError:\s+No module named ['\"]([^'\"]+)", out)
        failure = {"kind": "MODULE_NOT_FOUND", "module": m.group(1)} if m else {
            "kind": "SOURCE_BYTES_NOT_FOUND" if "FileNotFoundError" in out else "UNCLASSIFIED_EXECUTION_FAILURE"}
    return {"metric": "delta_aic_rll_minus_lcdm", "value": r.get(keys[-1]) if ok else None,
            "evidence_class": "C" if ok else "P",
            "state": "CALCULATED_FROM_RUN_OUTPUT" if ok else "TOKEN_VAZIO_EXECUTION_FAILURE",
            "method": "AIC difference from the same materialized run output",
            "source_receipts": _receipt(a), "failure": failure,
            "historical_reference_not_promoted": r.get("reference"), "claim_allowed": False}

def _bic_rows(text: str) -> dict[str, dict[str, float]]:
    rows: dict[str, dict[str, float]] = {}
    for line in text.splitlines():
        t = line.split()
        if len(t) < 8 or t[1].lower() != "real": continue
        model = t[0].lower()
        if model != "lcdm" and not model.startswith("rll"): continue
        try: values = dict(chi2=float(t[2]), aic=float(t[3]), bic=float(t[4]), n=int(t[5]), k=int(t[6]), dof=int(t[7]))
        except ValueError: continue
        rows["lcdm" if model == "lcdm" else "rll"] = values
    return rows

def classify_bayes_proxy(a: ArtifactBytes) -> tuple[dict[str, Any], dict[str, Any]]:
    r, rows = _json(a, "bayes_factor_result.json"), _bic_rows(_text(a, "bayes_bic_run.log"))
    reported = r.get("ln_B10_rll_over_lcdm")
    if isinstance(reported, (int, float)) and not isinstance(reported, bool):
        value, basis = float(reported), "RESULT_JSON"
    elif {"lcdm", "rll"} <= rows.keys():
        dbic = round(rows["rll"]["bic"] - rows["lcdm"]["bic"], 9)
        value, basis = round(-dbic / 2, 10), "RECONSTRUCTED_FROM_MATERIALIZED_BIC_ROWS"
    else: value, basis = None, "TOKEN_VAZIO_INPUT_ROWS"
    proxy = {"metric": "ln_B10_rll_over_lcdm", "value": value,
             "evidence_class": "C" if value is not None else "P",
             "state": "CALCULATED_BIC_PROXY" if value is not None else "TOKEN_VAZIO_BIC_PROXY",
             "method": "BIC proxy (ln B10 ≈ −ΔBIC/2)", "basis": basis,
             "source_metrics": rows, "source_receipts": _receipt(a), "claim_allowed": False}
    if value is not None:
        proxy["delta_bic_rll_minus_lcdm"] = round(rows["rll"]["bic"] - rows["lcdm"]["bic"], 9) if rows else None
        proxy["jeffreys_label"] = ("Forte evidência para RLL" if value > 5 else
            "Evidência substancial para RLL" if value > 2.3 else
            "Evidência fraca para RLL" if value > 0 else
            "Evidência fraca contra RLL" if value > -2.3 else "Evidência substancial contra RLL")
    proxy["falsifier_gate"] = {"id": "F-COS-04", "threshold": "ln(B10) > -5",
        "status": "TOKEN_VAZIO" if value is None else ("PASS" if value > -5 else "FAIL")}
    real = {"metric": "ln_B10_real_nested_sampling", "value": None, "evidence_class": "P",
            "state": "TOKEN_VAZIO_REAL_BAYES_INFERENCE",
            "method": "nested sampling / independently validated posterior evidence",
            "source_receipts": [], "claim_allowed": False,
            "note": "A BIC proxy is class C and cannot substitute real Bayesian evidence."}
    return proxy, real

def validate_result_record(r: dict[str, Any]) -> list[str]:
    e: list[str] = []; c = r.get("evidence_class")
    if c not in CLASSES: e.append("evidence_class must be one of E, C, H, P")
    if r.get("claim_allowed") is not False: e.append("claim_allowed must be false")
    if not r.get("state"): e.append("state must be a non-empty string")
    if c in {"E", "C"}:
        if r.get("value") is None: e.append(f"class {c} requires a materialized value")
        if not r.get("source_receipts"): e.append(f"class {c} requires source_receipts")
    if c == "P":
        if r.get("value") is not None: e.append("class P requires value=null")
        if not str(r.get("state", "")).startswith("TOKEN_VAZIO"): e.append("class P state must start with TOKEN_VAZIO")
    if c in {"C", "H"} and not r.get("method"): e.append(f"class {c} requires method")
    return e

def reconcile(*, run_id: int, source_head_sha: str, result_commit: str, pantheon_zip: Path,
              bayes_zip: Path, pantheon_sha256: str | None = None, bayes_sha256: str | None = None,
              generated_at: str | None = None) -> dict[str, Any]:
    p = classify_pantheon(read_artifact_zip(pantheon_zip, pantheon_sha256))
    b, real = classify_bayes_proxy(read_artifact_zip(bayes_zip, bayes_sha256))
    results = {"pantheon_delta_aic": p, "bayes_bic_proxy": b, "bayes_real_inference": real}
    errors = {k: validate_result_record(v) for k, v in results.items() if validate_result_record(v)}
    if errors: raise ReconciliationError(f"result contract failed: {errors}")
    return {"schema": SCHEMA, "generated_at": generated_at or datetime.now(timezone.utc).isoformat(),
            "repository": "instituto-Rafael/relativity-living-light",
            "canonical_run": {"run_id": run_id, "source_head_sha": source_head_sha, "result_commit": result_commit},
            "invariants": ["catalog_or_checkpoint_is_not_materialized_evidence",
                "derived_value_does_not_replace_source_bytes", "BIC_proxy_is_not_real_Bayesian_evidence",
                "historical_results_are_not_overwritten", "TOKEN_VAZIO_does_not_authorize_invention"],
            "results": results, "closure": {"pantheon_run_31066012098": p["state"],
                "bayes_bic_proxy": b["state"], "real_bayes_inference": real["state"], "claim_allowed": False},
            "claim_allowed": False}

def main(argv: Iterable[str] | None = None) -> int:
    ap = argparse.ArgumentParser(); ap.add_argument("--run-id", required=True, type=int)
    ap.add_argument("--source-head-sha", required=True); ap.add_argument("--result-commit", required=True)
    ap.add_argument("--pantheon-zip", required=True, type=Path); ap.add_argument("--bayes-zip", required=True, type=Path)
    ap.add_argument("--pantheon-sha256"); ap.add_argument("--bayes-sha256"); ap.add_argument("--generated-at")
    ap.add_argument("--output", required=True, type=Path); a = ap.parse_args(argv)
    try:
        payload = reconcile(run_id=a.run_id, source_head_sha=a.source_head_sha, result_commit=a.result_commit,
            pantheon_zip=a.pantheon_zip, bayes_zip=a.bayes_zip, pantheon_sha256=a.pantheon_sha256,
            bayes_sha256=a.bayes_sha256, generated_at=a.generated_at)
        a.output.parent.mkdir(parents=True, exist_ok=True)
        a.output.write_text(json.dumps(payload, ensure_ascii=False, indent=2, sort_keys=True) + "\n")
    except ReconciliationError as e:
        print(f"BLOCKED: {e}", file=sys.stderr); return 2
    print(f"PASS: wrote {a.output}"); return 0

if __name__ == "__main__": raise SystemExit(main())
