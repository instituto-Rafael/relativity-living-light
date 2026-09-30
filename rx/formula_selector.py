"""Declared-applicability formula selector for Rx Execution Fabric."""
from __future__ import annotations

import json
from pathlib import Path


def load_formula_bindings(path):
    payload = json.loads(Path(path).read_text(encoding="utf-8"))
    bindings = payload.get("bindings")
    if not isinstance(bindings, list):
        raise ValueError("formula binding registry requires a bindings list")
    return payload


def select_formulas(registry, regimes, observables, dispersion):
    active_regimes = set(str(x) for x in regimes)
    requested_observables = set(str(x) for x in observables)
    covariance_mode = str(dispersion.get("covariance_mode"))

    selected = []
    rejected = []

    for binding in registry.get("bindings", []):
        formula_id = str(binding.get("formula_id", "TOKEN_VAZIO"))
        reasons = []
        state = str(binding.get("state", "TOKEN_VAZIO"))
        required = set(str(x) for x in binding.get("required_regimes", []))
        any_regime = set(str(x) for x in binding.get("any_regimes", []))
        formula_observables = set(str(x) for x in binding.get("observables", []))
        covariance_modes = set(str(x) for x in binding.get("covariance_modes", []))

        if state != "EXECUTABLE":
            reasons.append("state_not_executable:" + state)
        if required and not required.issubset(active_regimes):
            reasons.append("missing_required_regime:" + ",".join(sorted(required-active_regimes)))
        if any_regime and active_regimes.isdisjoint(any_regime):
            reasons.append("no_allowed_regime_intersection")
        if formula_observables and requested_observables.isdisjoint(formula_observables):
            reasons.append("observable_not_requested")
        if covariance_modes and covariance_mode not in covariance_modes:
            reasons.append("covariance_mode_not_allowed:" + covariance_mode)

        record = dict(binding)
        record["selection_reasons"] = reasons
        if reasons:
            rejected.append(record)
        else:
            record["selection_basis"] = "declared_applicability_only"
            selected.append(record)

    return {
        "schema": "rll.rx.formula_selection.v1",
        "selected": selected,
        "rejected": rejected,
        "selected_count": len(selected),
        "rejected_count": len(rejected),
        "boundary": (
            "Formula selection is based on declared regime, observable, units/contract "
            "metadata and covariance policy; fit quality is not a selector."
        ),
        "claim_allowed": False,
    }
