#!/usr/bin/env python3
"""Fail-closed adapter from RLL Evidence Runner V1 receipts to RLL Studio manifests.

The adapter never promotes scientific authority. A valid Evidence Runner receipt may
produce an executable/observable Studio view, but claim.allowed remains false.
"""
from __future__ import annotations

import argparse
import json
import sys
from pathlib import Path
from typing import Any

ADAPTER_VERSION = "rll-studio-receipt-adapter/1.0.0"
MANIFEST_SCHEMA_VERSION = "rll-experiment-manifest/1.0.0"
RECEIPT_SCHEMA = "rll_evidence_receipt_v1"


class AdapterError(RuntimeError):
    pass


def _load_json(path: Path) -> dict[str, Any]:
    value = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(value, dict):
        raise AdapterError(f"JSON root must be an object: {path}")
    return value


def _decision_to_manifest_state(state: str) -> str:
    return {
        "VERIFIED_LIMITED": "OBSERVED_LIMITED",
        "TOKEN_VAZIO_REQUIRED_INPUT": "TOKEN_VAZIO",
        "TOKEN_VAZIO_RESULT": "TOKEN_VAZIO",
        "BLOCKED_EXECUTION": "BLOCKED",
    }.get(state, "INVALIDATED")


def _decision_to_execution_state(state: str) -> str:
    return {
        "VERIFIED_LIMITED": "PASS",
        "TOKEN_VAZIO_REQUIRED_INPUT": "BLOCKED",
        "TOKEN_VAZIO_RESULT": "PASS",
        "BLOCKED_EXECUTION": "FAIL",
    }.get(state, "INVALIDATED")


def _input_state(state: str) -> str:
    if state == "VERIFIED":
        return "PASS"
    if state in {"TOKEN_VAZIO_INPUT_MISSING", "TOKEN_VAZIO_REQUIRED_INPUT"}:
        return "TOKEN_VAZIO"
    if state == "OPTIONAL_ABSENT":
        return "UNAVAILABLE"
    if state.startswith("BLOCKED_"):
        return "FAIL"
    return "INVALIDATED"


def _limited_state(state: str) -> str:
    if state == "VERIFIED_LIMITED":
        return "OBSERVED_LIMITED"
    if state.startswith("TOKEN_VAZIO"):
        return "TOKEN_VAZIO"
    if state.startswith("BLOCKED"):
        return "BLOCKED"
    if state == "PASS":
        return "PASS"
    if state == "FAIL":
        return "FAIL"
    return "INVALIDATED"


def _safe_text(value: Any, fallback: str = "TOKEN_VAZIO") -> str:
    if value is None or value == "":
        return fallback
    return str(value)


def _comparison_identity(receipt: dict[str, Any]) -> tuple[str, str]:
    comparisons = receipt.get("comparisons") or []
    if comparisons and isinstance(comparisons[0], dict):
        return (
            _safe_text(comparisons[0].get("candidate"), receipt.get("experiment_title")),
            _safe_text(comparisons[0].get("baseline"), ""),
        )
    return _safe_text(receipt.get("experiment_title")), ""


def _dataset_identity(receipt: dict[str, Any]) -> dict[str, str]:
    inputs = receipt.get("inputs") or []
    ids = [_safe_text(item.get("id")) for item in inputs if isinstance(item, dict)]
    return {
        "name": " + ".join(ids) if ids else "TOKEN_VAZIO",
        "version": f"evidence-runner:{_safe_text(receipt.get('experiment_id'))}",
        "hash": _safe_text(receipt.get("semantic_sha256")),
    }


def _evidence_from_receipt(receipt: dict[str, Any], source_receipt: str) -> list[dict[str, Any]]:
    evidence: list[dict[str, Any]] = [
        {
            "id": "receipt-integrity",
            "title": "Integridade do receipt",
            "state": "PASS",
            "summary": "O receipt foi verificado pelo RLL Evidence Runner antes da adaptação.",
            "source": source_receipt,
            "test": "rll-evidence verify",
            "receipt": _safe_text(receipt.get("receipt_sha256")),
            "limitation": "Integridade do receipt não equivale a validação da hipótese científica.",
            "next_gate": "interpretar somente dentro da decision e dos gaps preservados",
        }
    ]

    for item in receipt.get("inputs") or []:
        if not isinstance(item, dict):
            continue
        state = _input_state(_safe_text(item.get("state"), ""))
        evidence.append(
            {
                "id": f"input:{_safe_text(item.get('id'))}",
                "title": f"Input · {_safe_text(item.get('id'))}",
                "state": state,
                "summary": f"Arquivo {_safe_text(item.get('path'))}; SHA-256 {_safe_text(item.get('sha256'))}.",
                "source": _safe_text(item.get("path")),
                "test": "input identity + integrity",
                "receipt": _safe_text(receipt.get("receipt_sha256")),
                "limitation": "Presença e hash do input não provam adequação física ou estatística do dataset.",
                "next_gate": "corrigir integridade/ausência" if state in {"FAIL", "TOKEN_VAZIO"} else "consumir pelo experimento governado",
            }
        )

    for step in receipt.get("steps") or []:
        if not isinstance(step, dict):
            continue
        state = "PASS" if step.get("state") == "PASS" else "FAIL"
        evidence.append(
            {
                "id": f"step:{_safe_text(step.get('id'))}",
                "title": f"Execução · {_safe_text(step.get('id'))}",
                "state": state,
                "summary": f"exit={_safe_text(step.get('exit_code'))}; timeout={bool(step.get('timed_out'))}.",
                "source": _safe_text(receipt.get("experiment_path")),
                "test": "argv execution / expected exit code",
                "receipt": _safe_text(receipt.get("receipt_sha256")),
                "limitation": "Step PASS comprova execução contratada, não verdade científica.",
                "next_gate": "inspecionar stderr/outputs" if state == "FAIL" else "validar outputs e resultados",
            }
        )

    for item in receipt.get("extractions") or []:
        if not isinstance(item, dict):
            continue
        state = _limited_state(_safe_text(item.get("state"), ""))
        evidence.append(
            {
                "id": f"extraction:{_safe_text(item.get('id'))}",
                "title": f"Extração · {_safe_text(item.get('id'))}",
                "state": state,
                "summary": f"Resultado extraído de {_safe_text(item.get('path'))}.",
                "source": _safe_text(item.get("path")),
                "test": "typed result extraction",
                "receipt": _safe_text(receipt.get("receipt_sha256")),
                "limitation": "; ".join(str(x) for x in (item.get("errors") or [])) or "Extração limitada ao escopo declarado pelo runner.",
                "next_gate": "materializar resultado faltante" if state == "TOKEN_VAZIO" else "comparar sob o mesmo contrato",
            }
        )

    for idx, item in enumerate(receipt.get("comparisons") or []):
        if not isinstance(item, dict):
            continue
        state = _limited_state(_safe_text(item.get("state"), ""))
        evidence.append(
            {
                "id": f"comparison:{idx}",
                "title": f"Comparação · {_safe_text(item.get('candidate'))} − {_safe_text(item.get('baseline'))}",
                "state": state,
                "summary": json.dumps(item.get("candidate_minus_baseline") or {}, sort_keys=True, ensure_ascii=False),
                "source": source_receipt,
                "test": "same-receipt candidate-minus-baseline",
                "receipt": _safe_text(receipt.get("receipt_sha256")),
                "limitation": "Diferença numérica não autoriza confirmação, causalidade ou superioridade fora do contrato.",
                "next_gate": "fechar resultado/comparação faltante" if state == "TOKEN_VAZIO" else "replicação e inferência governada",
            }
        )

    decision = receipt.get("decision") or {}
    evidence.append(
        {
            "id": "claim-boundary",
            "title": "Fronteira de claim",
            "state": "BLOCKED",
            "summary": f"Evidence Runner decision={_safe_text(decision.get('state'))}; claim_allowed=false.",
            "source": source_receipt,
            "test": "claim boundary",
            "receipt": _safe_text(receipt.get("receipt_sha256")),
            "limitation": "O adapter é somente transporte semântico; não possui autoridade de promoção.",
            "next_gate": "gate científico/humano independente aplicável ao claim",
        }
    )
    return evidence


def adapt_receipt_document(
    receipt: dict[str, Any], *, source_receipt: str, verification_state: str
) -> dict[str, Any]:
    if verification_state != "PASS":
        raise AdapterError("receipt verification must PASS before adaptation")
    if receipt.get("schema") != RECEIPT_SCHEMA:
        raise AdapterError("unsupported receipt schema")
    if receipt.get("claim_allowed") is not False:
        raise AdapterError("receipt claim_allowed must remain false")
    decision = receipt.get("decision")
    if not isinstance(decision, dict):
        raise AdapterError("receipt decision is missing")
    if decision.get("claim_allowed") is not False or decision.get("publication_effect") != "NONE":
        raise AdapterError("decision violates fail-closed claim boundary")

    decision_state = _safe_text(decision.get("state"), "")
    if decision_state not in {
        "VERIFIED_LIMITED",
        "TOKEN_VAZIO_REQUIRED_INPUT",
        "TOKEN_VAZIO_RESULT",
        "BLOCKED_EXECUTION",
    }:
        raise AdapterError(f"unsupported decision state: {decision_state}")

    model, comparator = _comparison_identity(receipt)
    comparisons = [item for item in (receipt.get("comparisons") or []) if isinstance(item, dict)]
    first_comparison = comparisons[0] if comparisons else {}
    deltas = first_comparison.get("candidate_minus_baseline") or {}
    metrics = [
        {"label": f"Δ{key}", "value": value, "detail": "candidate − baseline"}
        for key, value in sorted(deltas.items())
    ]
    total_duration_ms = round(
        sum(float(step.get("duration_seconds") or 0) for step in (receipt.get("steps") or []) if isinstance(step, dict)) * 1000,
        3,
    )
    f_gap = [str(x) for x in (decision.get("F_gap") or [])]
    f_next = [str(x) for x in (decision.get("F_next") or [])]

    return {
        "schema_version": MANIFEST_SCHEMA_VERSION,
        "manifest_id": f"RLL-STUDIO-{_safe_text(receipt.get('experiment_id'))}-{_safe_text(receipt.get('semantic_sha256'))[:12]}",
        "manifest_state": _decision_to_manifest_state(decision_state),
        "demo": False,
        "summary": (
            f"Receipt {_safe_text(receipt.get('experiment_id'))} verificado e adaptado sem promover claim. "
            f"Decision={decision_state}."
        ),
        "experiment": {
            "id": _safe_text(receipt.get("experiment_id")),
            "name": _safe_text(receipt.get("experiment_title")),
            "created_at": _safe_text(receipt.get("created_utc")),
            "mode": "evidence-runner-receipt",
            "model": model,
            "comparator": comparator,
            "dataset": _dataset_identity(receipt),
            "parameters": {},
        },
        "execution": {
            "state": _decision_to_execution_state(decision_state),
            "method": "RLL Evidence Runner V1",
            "environment": _safe_text((receipt.get("runtime") or {}).get("platform")),
            "commit": _safe_text(receipt.get("commit_sha")),
            "duration_ms": total_duration_ms,
            "receipt": source_receipt,
        },
        "claim": {
            "allowed": False,
            "state": "BLOCKED",
            "reason": (
                "Adapter has no promotion authority. Evidence Runner is claim-bounded; "
                f"decision={decision_state}."
            ),
        },
        "results": {
            "narrative": "Resultados transportados do receipt verificado; interpretação permanece limitada pelo contrato de origem.",
            "metrics": metrics,
            "parameters": [],
            "comparison": {
                "label": f"{model} − {comparator}" if comparator else model,
                "entries": [],
                "caption": "Valores são deltas do mesmo receipt; não constituem claim de superioridade.",
                "candidate_minus_baseline": deltas,
            },
        },
        "evidence": _evidence_from_receipt(receipt, source_receipt),
        "interoperability": [
            {"name": "Evidence Runner receipt", "state": "PASS", "detail": "verificado antes da adaptação"},
            {"name": "Studio Manifest V1", "state": "PASS", "detail": ADAPTER_VERSION},
            {"name": "JSON", "state": "PASS", "detail": "loss-bounded transport"},
            {"name": "Claim promotion", "state": "BLOCKED", "detail": "pipeline-owned; UI authority NONE"},
        ],
        "library": [
            {
                "type": "input",
                "title": _safe_text(item.get("id")),
                "description": f"state={_safe_text(item.get('state'))}; sha256={_safe_text(item.get('sha256'))}",
                "ref": _safe_text(item.get("path")),
            }
            for item in (receipt.get("inputs") or [])
            if isinstance(item, dict)
        ],
        "provenance": {
            "adapter": ADAPTER_VERSION,
            "source_receipt": source_receipt,
            "receipt_sha256": _safe_text(receipt.get("receipt_sha256")),
            "semantic_sha256": _safe_text(receipt.get("semantic_sha256")),
            "experiment_sha256": _safe_text(receipt.get("experiment_sha256")),
            "commit_sha": _safe_text(receipt.get("commit_sha")),
            "verification_state": verification_state,
            "claim_allowed": False,
        },
        "gaps": {
            "F_gap": f_gap,
            "F_next": f_next,
            "claim_allowed": False,
        },
    }


def _verify_with_runner(receipt_path: Path, repository_root: Path) -> dict[str, Any]:
    runner_src = repository_root / "products/rll-evidence-runner/src"
    if not runner_src.is_dir():
        raise AdapterError(f"RLL Evidence Runner source missing: {runner_src}")
    sys.path.insert(0, str(runner_src))
    try:
        from rll_evidence.core import verify_receipt  # type: ignore
    except ImportError as exc:
        raise AdapterError("cannot import RLL Evidence Runner verifier") from exc
    return verify_receipt(receipt_path, repository_root)


def adapt_receipt_file(receipt_path: Path, output_path: Path, repository_root: Path) -> dict[str, Any]:
    repository_root = repository_root.resolve()
    receipt_path = receipt_path.resolve()
    verification = _verify_with_runner(receipt_path, repository_root)
    if verification.get("state") != "PASS":
        raise AdapterError("receipt verification failed: " + "; ".join(verification.get("errors") or []))
    receipt = _load_json(receipt_path)
    try:
        source = str(receipt_path.relative_to(repository_root))
    except ValueError:
        source = str(receipt_path)
    manifest = adapt_receipt_document(receipt, source_receipt=source, verification_state="PASS")
    output_path = output_path.resolve()
    output_path.parent.mkdir(parents=True, exist_ok=True)
    output_path.write_text(json.dumps(manifest, indent=2, sort_keys=True, ensure_ascii=False) + "\n", encoding="utf-8")
    return manifest


def main() -> int:
    parser = argparse.ArgumentParser(description="Adapt a verified RLL Evidence Runner receipt to RLL Studio Manifest V1")
    parser.add_argument("receipt", type=Path)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--repository-root", type=Path, default=Path.cwd())
    args = parser.parse_args()
    try:
        manifest = adapt_receipt_file(args.receipt, args.output, args.repository_root)
    except (AdapterError, OSError, ValueError, KeyError, json.JSONDecodeError) as exc:
        print(json.dumps({"state": "FAIL", "claim_allowed": False, "error": str(exc)}, ensure_ascii=False))
        return 2
    print(json.dumps({
        "state": "PASS",
        "adapter": ADAPTER_VERSION,
        "manifest_id": manifest["manifest_id"],
        "manifest_state": manifest["manifest_state"],
        "claim_allowed": False,
        "output": str(args.output),
    }, ensure_ascii=False))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
