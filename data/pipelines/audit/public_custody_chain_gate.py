from __future__ import annotations

import json
import math
from dataclasses import dataclass
from datetime import datetime
from pathlib import Path
from statistics import variance
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
    "official_public_spending_data",
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
PUBLIC_MONEY_STAGES = {
    "BR": ("empenho", "liquidacao", "pagamento"),
    "US": ("appropriation", "obligation", "outlay"),
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


def _parse_time(value: str) -> datetime:
    normalized = value[:-1] + "+00:00" if value.endswith("Z") else value
    return datetime.fromisoformat(normalized)


def elapsed_hours(start: str, end: str) -> float:
    delta = _parse_time(end) - _parse_time(start)
    return delta.total_seconds() / 3600.0


def shipment_timing(
    *,
    sent_at: str,
    arrived_at: str | None = None,
    received_at: str | None = None,
    deadline_at: str | None = None,
) -> dict[str, float | bool | None]:
    sent = _parse_time(sent_at)
    arrived = _parse_time(arrived_at) if arrived_at else None
    received = _parse_time(received_at) if received_at else None
    deadline = _parse_time(deadline_at) if deadline_at else None

    if arrived is not None and arrived < sent:
        raise ValueError("arrived_before_sent")
    if received is not None and received < sent:
        raise ValueError("received_before_sent")
    if arrived is not None and received is not None and received < arrived:
        raise ValueError("received_before_arrived")

    end = received or arrived
    lead_hours = (end - sent).total_seconds() / 3600.0 if end else None
    arrival_hours = (arrived - sent).total_seconds() / 3600.0 if arrived else None
    receiving_lapse_hours = (
        (received - arrived).total_seconds() / 3600.0
        if received is not None and arrived is not None
        else None
    )
    deadline_slip_hours = (
        (end - deadline).total_seconds() / 3600.0
        if end is not None and deadline is not None
        else None
    )
    return {
        "arrival_lapse_hours": arrival_hours,
        "receiving_lapse_hours": receiving_lapse_hours,
        "lead_time_hours": lead_hours,
        "deadline_slip_hours": deadline_slip_hours,
        "on_time": deadline_slip_hours <= 0.0 if deadline_slip_hours is not None else None,
    }


def bullwhip_ratio(upstream: list[float], downstream: list[float]) -> float | None:
    if len(upstream) != len(downstream) or len(upstream) < 4:
        raise ValueError("bullwhip_requires_equal_series_with_at_least_four_points")
    downstream_var = variance(downstream)
    if downstream_var == 0:
        return None
    return variance(upstream) / downstream_var


def ledger_residual(
    *,
    opening_balance: float,
    inflows: list[float],
    outflows: list[float],
    closing_balance: float,
) -> float:
    return opening_balance + sum(inflows) - sum(outflows) - closing_balance


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


def _validate_source_refs(
    refs: Any,
    source_ids: set[str],
    *,
    owner: str,
    errors: list[str],
) -> None:
    if not isinstance(refs, list) or not refs:
        errors.append(f"{owner}_without_source")
        return
    for ref in refs:
        if ref not in source_ids:
            errors.append(f"{owner}_unknown_source:{ref}")


def validate_contract(contract: dict[str, Any]) -> GateResult:
    errors: list[str] = []
    warnings: list[str] = []
    metrics: dict[str, Any] = {}

    if contract.get("schema") != SCHEMA:
        errors.append("schema_mismatch")
    if contract.get("claim_allowed") is not False:
        errors.append("root_claim_must_start_false")

    sources = contract.get("sources")
    if not isinstance(sources, list) or not sources:
        errors.append("sources_missing")
        sources = []

    source_ids: set[str] = set()
    hashed_sources = 0
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
        if src.get("sha256"):
            hashed_sources += 1
        else:
            warnings.append(f"TOKEN_VAZIO_HASH:{sid}")

    metrics["source_count"] = len(source_ids)
    metrics["source_hash_coverage"] = (
        hashed_sources / len(source_ids) if source_ids else 0.0
    )

    events = contract.get("events", [])
    event_ids: set[str] = set()
    sourced_events = 0
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
        if refs:
            sourced_events += 1
        _validate_source_refs(refs, source_ids, owner=f"event:{eid}", errors=errors)

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

    metrics["event_source_coverage"] = (
        sourced_events / len(events) if events else 1.0
    )

    for key in _iter_keys(contract):
        if key in FORBIDDEN_PRIVATE_FIELDS:
            errors.append(f"forbidden_private_field:{key}")

    roles = contract.get("governance_roles", [])
    current_roles = 0
    for index, role in enumerate(roles):
        if not isinstance(role, dict):
            errors.append(f"governance_role_not_object:{index}")
            continue
        _validate_source_refs(
            role.get("source_refs", []),
            source_ids,
            owner=f"governance_role:{index}",
            errors=errors,
        )
        if not role.get("entity") or not role.get("person") or not role.get("role"):
            errors.append(f"governance_role_identity_missing:{index}")
        start = role.get("effective_from")
        end = role.get("effective_to")
        if not start:
            errors.append(f"governance_role_start_missing:{index}")
        if start and end:
            try:
                if _parse_time(end) < _parse_time(start):
                    errors.append(f"governance_role_negative_interval:{index}")
            except ValueError:
                errors.append(f"governance_role_time_invalid:{index}")
        if role.get("current") is True:
            current_roles += 1
            if end is not None:
                errors.append(f"governance_current_role_has_end:{index}")
            if not role.get("as_of"):
                errors.append(f"governance_current_role_missing_as_of:{index}")
    metrics["governance_role_count"] = len(roles)
    metrics["governance_current_role_count"] = current_roles

    money = contract.get("public_money_flows", [])
    money_trace_stages: dict[str, set[str]] = {}
    for index, flow in enumerate(money):
        if not isinstance(flow, dict):
            errors.append(f"public_money_not_object:{index}")
            continue
        _validate_source_refs(
            flow.get("source_refs", []),
            source_ids,
            owner=f"public_money:{index}",
            errors=errors,
        )
        jurisdiction = flow.get("jurisdiction")
        stage = flow.get("stage")
        allowed = PUBLIC_MONEY_STAGES.get(str(jurisdiction))
        if allowed is None or stage not in allowed:
            errors.append(f"public_money_stage_invalid:{index}")
        amount = flow.get("amount")
        if not isinstance(amount, (int, float)) or isinstance(amount, bool) or amount < 0:
            errors.append(f"public_money_amount_invalid:{index}")
        if not flow.get("currency"):
            errors.append(f"public_money_currency_missing:{index}")
        trace_id = flow.get("trace_id")
        if not trace_id:
            errors.append(f"public_money_trace_id_missing:{index}")
        else:
            money_trace_stages.setdefault(str(trace_id), set()).add(str(stage))

        cash_realized = flow.get("cash_realized")
        if cash_realized is True:
            if jurisdiction == "US" and stage != "outlay":
                errors.append(f"public_money_cash_before_outlay:{index}")
            if jurisdiction == "BR" and stage != "pagamento":
                errors.append(f"public_money_cash_before_payment:{index}")

    for trace_id, stages in sorted(money_trace_stages.items()):
        if stages:
            jurisdiction = next(
                (
                    str(item.get("jurisdiction"))
                    for item in money
                    if isinstance(item, dict) and str(item.get("trace_id")) == trace_id
                ),
                "",
            )
            expected = PUBLIC_MONEY_STAGES.get(jurisdiction, ())
            missing = [stage for stage in expected if stage not in stages]
            if missing:
                warnings.append(
                    f"TOKEN_VAZIO_PUBLIC_MONEY_STAGE:{trace_id}:{','.join(missing)}"
                )

    shipments = contract.get("shipments", [])
    shipment_metrics: dict[str, dict[str, Any]] = {}
    for index, shipment in enumerate(shipments):
        if not isinstance(shipment, dict):
            errors.append(f"shipment_not_object:{index}")
            continue
        sid = str(shipment.get("id") or index)
        _validate_source_refs(
            shipment.get("source_refs", []),
            source_ids,
            owner=f"shipment:{sid}",
            errors=errors,
        )
        if shipment.get("public_record") is not True:
            errors.append(f"shipment_not_public:{sid}")
        sent_at = shipment.get("sent_at")
        if not sent_at:
            errors.append(f"shipment_sent_missing:{sid}")
            continue
        try:
            shipment_metrics[sid] = shipment_timing(
                sent_at=sent_at,
                arrived_at=shipment.get("arrived_at"),
                received_at=shipment.get("received_at"),
                deadline_at=shipment.get("deadline_at"),
            )
        except (TypeError, ValueError):
            errors.append(f"shipment_time_invalid:{sid}")
    metrics["shipment_timing"] = shipment_metrics

    deadlines = contract.get("deadlines", [])
    deadline_metrics: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(deadlines):
        if not isinstance(item, dict):
            errors.append(f"deadline_not_object:{index}")
            continue
        did = str(item.get("id") or index)
        _validate_source_refs(
            item.get("source_refs", []),
            source_ids,
            owner=f"deadline:{did}",
            errors=errors,
        )
        planned = item.get("deadline_at")
        actual = item.get("completed_at")
        if not planned:
            errors.append(f"deadline_missing:{did}")
            continue
        if actual:
            try:
                slip = elapsed_hours(planned, actual)
                deadline_metrics[did] = {
                    "deadline_slip_hours": slip,
                    "on_time": slip <= 0.0,
                }
            except ValueError:
                errors.append(f"deadline_time_invalid:{did}")
        else:
            warnings.append(f"TOKEN_VAZIO_COMPLETION:{did}")
    metrics["deadline_timing"] = deadline_metrics

    bullwhip = contract.get("bullwhip_series", [])
    bullwhip_metrics: dict[str, Any] = {}
    for index, series in enumerate(bullwhip):
        if not isinstance(series, dict):
            errors.append(f"bullwhip_not_object:{index}")
            continue
        bid = str(series.get("id") or index)
        _validate_source_refs(
            series.get("source_refs", []),
            source_ids,
            owner=f"bullwhip:{bid}",
            errors=errors,
        )
        upstream = series.get("upstream")
        downstream = series.get("downstream")
        if not isinstance(upstream, list) or not isinstance(downstream, list):
            errors.append(f"bullwhip_series_invalid:{bid}")
            continue
        try:
            ratio = bullwhip_ratio(
                [float(value) for value in upstream],
                [float(value) for value in downstream],
            )
            if ratio is None:
                warnings.append(f"TOKEN_VAZIO_BULLWHIP_ZERO_DENOMINATOR:{bid}")
            else:
                bullwhip_metrics[bid] = ratio
        except (TypeError, ValueError):
            errors.append(f"bullwhip_series_invalid:{bid}")
    metrics["bullwhip_ratio"] = bullwhip_metrics

    ledgers = contract.get("ledger_reconciliations", [])
    ledger_metrics: dict[str, float] = {}
    for index, ledger in enumerate(ledgers):
        if not isinstance(ledger, dict):
            errors.append(f"ledger_not_object:{index}")
            continue
        lid = str(ledger.get("id") or index)
        _validate_source_refs(
            ledger.get("source_refs", []),
            source_ids,
            owner=f"ledger:{lid}",
            errors=errors,
        )
        try:
            residual = ledger_residual(
                opening_balance=float(ledger["opening_balance"]),
                inflows=[float(v) for v in ledger["inflows"]],
                outflows=[float(v) for v in ledger["outflows"]],
                closing_balance=float(ledger["closing_balance"]),
            )
        except (KeyError, TypeError, ValueError):
            errors.append(f"ledger_values_invalid:{lid}")
            continue
        ledger_metrics[lid] = residual
        tolerance = float(ledger.get("tolerance", 0.0))
        if abs(residual) > tolerance:
            warnings.append(f"LEDGER_RESIDUAL_OUTSIDE_TOLERANCE:{lid}")
    metrics["ledger_residual"] = ledger_metrics

    hypotheses = contract.get("falsifiability_hypotheses", [])
    for index, item in enumerate(hypotheses):
        if not isinstance(item, dict):
            errors.append(f"hypothesis_not_object:{index}")
            continue
        hid = str(item.get("id") or index)
        if not item.get("statement"):
            errors.append(f"hypothesis_statement_missing:{hid}")
        falsifiers = item.get("falsifiers")
        if not isinstance(falsifiers, list) or not falsifiers:
            errors.append(f"hypothesis_falsifier_missing:{hid}")
        if not item.get("metric_or_observable"):
            errors.append(f"hypothesis_observable_missing:{hid}")
        if item.get("state") not in {"HYPOTHESIS", "TOKEN_VAZIO", "BLOCKED"}:
            errors.append(f"hypothesis_state_invalid:{hid}")

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

    metrics["uncertainty"] = {
        "unhashed_sources": len(source_ids) - hashed_sources,
        "warning_count": len(warnings),
        "error_count": len(errors),
    }

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
