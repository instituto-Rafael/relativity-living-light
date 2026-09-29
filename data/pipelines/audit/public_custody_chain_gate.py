from __future__ import annotations

import json
import math
from dataclasses import dataclass
from pathlib import Path
from typing import Any, Iterable
from urllib.parse import urlparse

SCHEMA = "rll.public-custody-chain/v1"
ALLOWED_SOURCE_KINDS = {
    "official_government",
    "regulatory_filing",
    "court_or_legislative_record",
    "official_corporate",
    "official_exchange_or_market_data",
    "official_trade_or_customs_data",
}
ALLOWED_STATES = {"OBSERVED", "DERIVED", "HYPOTHESIS", "TOKEN_VAZIO", "BLOCKED"}
FORBIDDEN_PRIVATE_FIELDS = {
    "ssn",
    "cpf_full_private",
    "private_tax_return",
    "private_bank_account",
    "private_home_address",
    "nonpublic_cap_table",
    "nonpublic_awb",
    "nonpublic_bill_of_lading",
}
HAZARDOUS_PROCUREMENT_RELATIONS = {
    "propellant_supplier_route",
    "hazardous_material_purchase_route",
    "explosive_precursor_route",
}


@dataclass(frozen=True)
class GateResult:
    status: str
    claim_allowed: bool
    errors: tuple[str, ...]
    warnings: tuple[str, ...]
    metrics: dict[str, Any]


def _is_https(url: str) -> bool:
    try:
        parsed = urlparse(url)
    except ValueError:
        return False
    return parsed.scheme == "https" and bool(parsed.netloc)


def _iter_keys(value: Any) -> Iterable[str]:
    if isinstance(value, dict):
        for key, nested in value.items():
            yield str(key)
            yield from _iter_keys(nested)
    elif isinstance(value, list):
        for item in value:
            yield from _iter_keys(item)


def wrap_pi(angle: float) -> float:
    return (angle + math.pi) % (2.0 * math.pi) - math.pi


def torus_distance(a: list[float], b: list[float]) -> float:
    if len(a) != len(b) or not a:
        raise ValueError("toroidal vectors must have the same non-zero length")
    sq = 0.0
    for x, y in zip(a, b):
        if not (0.0 <= x <= 1.0 and 0.0 <= y <= 1.0):
            raise ValueError("toroidal coordinates must be normalized to [0,1]")
        phase = wrap_pi(2.0 * math.pi * (x - y))
        sq += phase * phase
    return math.sqrt(sq / len(a)) / math.pi


def torus_stability(a: list[float], b: list[float]) -> float:
    return max(0.0, min(1.0, 1.0 - torus_distance(a, b)))


def state14(current7: list[float], previous7: list[float]) -> list[float]:
    if len(current7) != 7 or len(previous7) != 7:
        raise ValueError("state14 requires exactly seven state coordinates")
    return current7 + [current - previous for current, previous in zip(current7, previous7)]


def validate_contract(contract: dict[str, Any]) -> GateResult:
    errors: list[str] = []
    warnings: list[str] = []

    if contract.get("schema") != SCHEMA:
        errors.append("schema_mismatch")

    if contract.get("claim_allowed") is not False:
        errors.append("root_claim_must_start_false")

    sources = contract.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources_missing")
        sources = []

    source_ids: set[str] = set()
    for src in sources:
        if not isinstance(src, dict):
            errors.append("source_not_object")
            continue
        sid = src.get("id")
        if not isinstance(sid, str) or not sid:
            errors.append("source_id_missing")
            continue
        if sid in source_ids:
            errors.append(f"duplicate_source:{sid}")
        source_ids.add(sid)
        if src.get("public_record") is not True:
            errors.append(f"source_not_public:{sid}")
        if src.get("source_kind") not in ALLOWED_SOURCE_KINDS:
            errors.append(f"source_kind_not_allowed:{sid}")
        url = src.get("url")
        if not isinstance(url, str) or not _is_https(url):
            errors.append(f"source_url_invalid:{sid}")
        if not src.get("retrieved_at"):
            warnings.append(f"retrieved_at_missing:{sid}")
        if not src.get("sha256"):
            warnings.append(f"TOKEN_VAZIO_HASH:{sid}")

    events = contract.get("events", [])
    event_ids: set[str] = set()
    for event in events:
        if not isinstance(event, dict):
            errors.append("event_not_object")
            continue
        eid = event.get("id")
        if not isinstance(eid, str) or not eid:
            errors.append("event_id_missing")
            continue
        if eid in event_ids:
            errors.append(f"duplicate_event:{eid}")
        event_ids.add(eid)
        refs = event.get("source_refs", [])
        if not refs:
            errors.append(f"event_without_source:{eid}")
        for ref in refs:
            if ref not in source_ids:
                errors.append(f"event_unknown_source:{eid}:{ref}")
        if event.get("event_type") == "investment_announcement":
            if event.get("realized_cash") is True and not event.get("realization_source_refs"):
                errors.append(f"announcement_promoted_to_cash_without_evidence:{eid}")
        if event.get("event_type") == "tax_record":
            if event.get("publication_basis") not in {
                "statutory_public_disclosure",
                "official_public_release",
                "court_authorized_public_release",
            }:
                errors.append(f"tax_record_without_publication_basis:{eid}")

    for key in _iter_keys(contract):
        if key in FORBIDDEN_PRIVATE_FIELDS:
            errors.append(f"forbidden_private_field:{key}")

    edges = contract.get("edges", [])
    for index, edge in enumerate(edges):
        if not isinstance(edge, dict):
            errors.append(f"edge_not_object:{index}")
            continue
        relation = edge.get("relation")
        if relation in HAZARDOUS_PROCUREMENT_RELATIONS:
            errors.append(f"hazardous_procurement_out_of_scope:{index}")
        state = edge.get("state")
        if state not in ALLOWED_STATES:
            errors.append(f"edge_state_invalid:{index}")
        refs = edge.get("source_refs", [])
        for ref in refs:
            if ref not in source_ids:
                errors.append(f"edge_unknown_source:{index}:{ref}")
        if edge.get("causal") is True:
            causal_refs = edge.get("causal_evidence_refs", [])
            if len(causal_refs) < 2:
                errors.append(f"causal_edge_under_evidenced:{index}")
            for ref in causal_refs:
                if ref not in source_ids:
                    errors.append(f"causal_unknown_source:{index}:{ref}")
        elif relation in {"caused", "caused_by", "proof_of_concealment"}:
            errors.append(f"causal_language_without_causal_gate:{index}")

    stability = contract.get("stability")
    metrics: dict[str, Any] = {}
    if isinstance(stability, dict):
        current = stability.get("current7")
        previous = stability.get("previous7")
        if current is not None or previous is not None:
            try:
                if not (isinstance(current, list) and isinstance(previous, list)):
                    raise ValueError
                metrics["torus_stability"] = torus_stability(current, previous)
                metrics["state14"] = state14(current, previous)
            except (TypeError, ValueError):
                errors.append("stability_vector_invalid")
        params = stability.get("author_parameters", {})
        if isinstance(params, dict):
            for name in ("delta_p", "k"):
                item = params.get(name)
                if item is None:
                    warnings.append(f"TOKEN_VAZIO_AUTHOR_PARAMETER:{name}")
                elif isinstance(item, dict) and item.get("status") == "TOKEN_VAZIO":
                    warnings.append(f"TOKEN_VAZIO_AUTHOR_PARAMETER:{name}")

    claim_allowed = False
    status = "FAIL" if errors else "PASS_GATE_CUSTODY_ONLY"
    return GateResult(
        status=status,
        claim_allowed=claim_allowed,
        errors=tuple(errors),
        warnings=tuple(warnings),
        metrics=metrics,
    )


def load_contract(path: str | Path) -> dict[str, Any]:
    return json.loads(Path(path).read_text(encoding="utf-8"))


def main(path: str | Path) -> int:
    result = validate_contract(load_contract(path))
    print(
        json.dumps(
            {
                "status": result.status,
                "claim_allowed": result.claim_allowed,
                "errors": list(result.errors),
                "warnings": list(result.warnings),
                "metrics": result.metrics,
            },
            ensure_ascii=False,
            indent=2,
            sort_keys=True,
        )
    )
    return 0 if not result.errors else 1
