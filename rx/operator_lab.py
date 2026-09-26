"""Fail-closed, stdlib-only RLL Operator Lab V1.

This module is intentionally isolated from canonical Rx formula selection and
scientific-gate closure. It executes a bounded internal allowlist only.
"""
from __future__ import annotations
import hashlib
import json
import math
from copy import deepcopy

VERSION = "rll.operator_lab.v1"
SUPPORTED = {
    "O001", "O006", "O025", "O026", "O027", "O028", "O029",
    "O031", "O032", "O033", "O034", "O035", "O036", "O039",
    "O040", "O042",
}

def canonical_json(obj):
    return json.dumps(obj, sort_keys=True, separators=(",", ":"), ensure_ascii=False, allow_nan=False)

def sha256_obj(obj):
    return hashlib.sha256(canonical_json(obj).encode("utf-8")).hexdigest()

def _blocked(state, reason, falsifiers=None):
    return {"state": state, "reason": reason, "falsifiers": list(falsifiers or [])}

def _num(value):
    if isinstance(value, bool) or not isinstance(value, (int, float)):
        raise TypeError("numeric scalar required")
    result = float(value)
    if not math.isfinite(result):
        raise ValueError("finite numeric scalar required")
    return result

def _unit_guard(envelope, expected):
    unit = envelope.get("unit")
    if unit in (None, "", expected):
        return None
    return _blocked("BLOCKED_TYPE", "unit must be %r, got %r" % (expected, unit), ["F128", "F161"])

def apply_operator(operator_id, envelope, params=None):
    params = params or {}
    if operator_id not in SUPPORTED:
        return _blocked("BLOCKED_UNSUPPORTED", "operator %s is not executable in Operator Lab V1" % operator_id)
    out = deepcopy(envelope)
    value = out.get("value")
    try:
        if operator_id == "O001":
            pass
        elif operator_id == "O006":
            x = _num(value)
            if x == 0.0:
                return _blocked("BLOCKED_DOMAIN", "reciprocal denominator is zero", ["F108"])
            out["value"], out["type"] = 1.0 / x, "real"
        elif operator_id == "O025":
            x = _num(value)
            if x <= 0.0:
                return _blocked("BLOCKED_DOMAIN", "ln requires x>0", ["F121"])
            out["value"], out["type"] = math.log(x), "real"
        elif operator_id == "O026":
            x, base = _num(value), _num(params.get("base"))
            if x <= 0.0:
                return _blocked("BLOCKED_DOMAIN", "log_b requires x>0", ["F121"])
            if base <= 0.0 or base == 1.0:
                return _blocked("BLOCKED_DOMAIN", "log base requires b>0 and b!=1", ["F122"])
            out["value"], out["type"] = math.log(x, base), "real"
        elif operator_id == "O027":
            x, base, depth = _num(value), _num(params.get("base")), params.get("k")
            if not isinstance(depth, int) or isinstance(depth, bool) or not 1 <= depth <= 64:
                return _blocked("BLOCKED_DOMAIN", "iterated log requires integer 1<=k<=64", ["F123"])
            if base <= 0.0 or base == 1.0:
                return _blocked("BLOCKED_DOMAIN", "log base requires b>0 and b!=1", ["F122"])
            result = x
            for idx in range(depth):
                if result <= 0.0:
                    return _blocked("BLOCKED_DOMAIN", "iterated log domain failed at iteration %d" % (idx + 1), ["F123"])
                result = math.log(result, base)
            out["value"], out["type"] = result, "real"
        elif operator_id == "O028":
            result = math.exp(_num(value))
            if not math.isfinite(result):
                return _blocked("BLOCKED_DOMAIN", "exp overflowed finite real domain")
            out["value"], out["type"] = result, "real"
        elif operator_id == "O029":
            x, exponent = _num(value), _num(params.get("exponent"))
            if x < 0.0 and not exponent.is_integer():
                return _blocked("BLOCKED_BRANCH", "negative base with non-integer exponent requires complex branch", ["F133", "F135"])
            result = x ** exponent
            if isinstance(result, complex) or not math.isfinite(float(result)):
                return _blocked("BLOCKED_BRANCH", "result left finite real branch", ["F133"])
            out["value"], out["type"] = float(result), "real"
        elif operator_id == "O031":
            out["value"], out["type"] = math.sin(_num(value)), "real"
        elif operator_id == "O032":
            out["value"], out["type"] = math.cos(_num(value)), "real"
        elif operator_id == "O033":
            x = _num(value)
            if abs(math.cos(x)) <= float(params.get("pole_tolerance", 1e-12)):
                return _blocked("BLOCKED_DOMAIN", "tan pole detected", ["F127"])
            out["value"], out["type"] = math.tan(x), "real"
        elif operator_id == "O034":
            out["value"], out["type"] = math.atan(_num(value)), "real"
            out["branch"] = "principal(-pi/2,pi/2)"
        elif operator_id == "O035":
            guard = _unit_guard(out, "degrees")
            if guard:
                return guard
            out["value"], out["unit"], out["type"] = math.radians(_num(value)), "radians", "real"
        elif operator_id == "O036":
            guard = _unit_guard(out, "radians")
            if guard:
                return guard
            out["value"], out["unit"], out["type"] = math.degrees(_num(value)), "degrees", "real"
        elif operator_id == "O039":
            x, n = _num(value), params.get("n")
            if not isinstance(n, int) or isinstance(n, bool) or n == 0:
                return _blocked("BLOCKED_DOMAIN", "n-th root requires nonzero integer n", ["F135"])
            if n < 0 and x == 0.0:
                return _blocked("BLOCKED_DOMAIN", "negative root index at x=0 is undefined", ["F135"])
            if n % 2 == 0 and x < 0.0:
                return _blocked("BLOCKED_DOMAIN", "even real root requires x>=0", ["F132"])
            result = -((-x) ** (1.0 / n)) if x < 0.0 and n % 2 else x ** (1.0 / n)
            out["value"], out["type"], out["branch"] = float(result), "real", "real"
        elif operator_id == "O040":
            x = _num(value)
            if x < 0.0:
                return _blocked("BLOCKED_DOMAIN", "real sqrt requires x>=0", ["F132"])
            out["value"], out["type"], out["branch"] = math.sqrt(x), "real", "principal_nonnegative"
        elif operator_id == "O042":
            if not isinstance(value, list) or not value:
                return _blocked("BLOCKED_TYPE", "norm2 requires non-empty numeric vector")
            values = [_num(item) for item in value]
            out["value"], out["type"] = math.sqrt(sum(item * item for item in values)), "real"
    except (TypeError, ValueError, OverflowError) as exc:
        return _blocked("BLOCKED_DOMAIN", str(exc))
    lineage = list(envelope.get("lineage") or [])
    lineage.append(operator_id)
    out["lineage"] = lineage
    return {"state": "PASS", "value": out}

def propagate(fixture):
    envelope = deepcopy(fixture.get("input") or {})
    path = fixture.get("path")
    if not isinstance(path, list) or not path:
        result = {"schema": VERSION, "state": "ERROR", "reason": "path must be a non-empty list", "trace": []}
        result["receipt_sha256"] = sha256_obj(result)
        return result
    trace = []
    current = envelope
    for index, step in enumerate(path):
        if not isinstance(step, dict) or "operator_id" not in step:
            result = {"schema": VERSION, "state": "ERROR", "reason": "invalid step at index %d" % index, "trace": trace}
            result["receipt_sha256"] = sha256_obj(result)
            return result
        operator_id = str(step["operator_id"])
        observation = apply_operator(operator_id, current, step.get("params"))
        trace.append({"index": index, "operator_id": operator_id, "observation": observation})
        if observation["state"] != "PASS":
            result = {
                "schema": VERSION, "fixture_id": fixture.get("fixture_id"),
                "state": observation["state"], "reason": observation.get("reason"),
                "falsifiers": observation.get("falsifiers", []), "trace": trace,
                "claim_allowed": False,
            }
            result["receipt_sha256"] = sha256_obj(result)
            return result
        current = observation["value"]
    result = {
        "schema": VERSION, "fixture_id": fixture.get("fixture_id"),
        "state": "PASS", "output": current, "trace": trace, "claim_allowed": False,
    }
    result["receipt_sha256"] = sha256_obj(result)
    return result

def _close(left, right, tolerance):
    try:
        return abs(float(left) - float(right)) <= tolerance
    except Exception:
        return left == right

def evaluate_fixture(fixture):
    observed = propagate(fixture)
    expected_state = fixture.get("expected_state")
    ok = observed.get("state") == expected_state
    notes = []
    if not ok:
        notes.append("state expected %r, observed %r" % (expected_state, observed.get("state")))
    if ok and expected_state == "PASS" and "expected_value" in fixture:
        actual = (observed.get("output") or {}).get("value")
        tolerance = float(fixture.get("tolerance", 1e-12))
        ok = _close(actual, fixture["expected_value"], tolerance)
        if not ok:
            notes.append("value expected %r, observed %r" % (fixture["expected_value"], actual))
    expected_falsifier = fixture.get("expected_falsifier")
    if expected_falsifier and expected_falsifier not in (observed.get("falsifiers") or []):
        ok = False
        notes.append("expected falsifier %s not present" % expected_falsifier)
    return {
        "fixture_id": fixture.get("fixture_id"), "expected_state": expected_state,
        "observed_state": observed.get("state"), "ok": ok, "notes": notes,
        "observation": observed,
    }

def run_suite(suite):
    if suite.get("claim_allowed") is not False:
        raise ValueError("Operator Lab suite must set claim_allowed=false")
    negatives, positives = suite.get("negative"), suite.get("positive")
    if not isinstance(negatives, list) or not negatives:
        return {"schema":"rll.operator_lab.suite_receipt.v1","state":"FAIL_CLOSED","negative_gate":"FAIL","reason":"negative controls are required","claim_allowed":False}
    if not isinstance(positives, list):
        return {"schema":"rll.operator_lab.suite_receipt.v1","state":"FAIL_CLOSED","negative_gate":"FAIL","reason":"positive fixtures list is required","claim_allowed":False}
    results, negative_gate = [], True
    for fixture in negatives:
        row = evaluate_fixture(fixture); results.append({"phase":"negative", **row})
        if not row["ok"] or row["observed_state"] == "PASS":
            negative_gate = False
    if not negative_gate:
        receipt = {
            "schema":"rll.operator_lab.suite_receipt.v1","suite_id":suite.get("suite_id"),
            "state":"FAIL_CLOSED","negative_gate":"FAIL","positive_phase":"NOT_RUN",
            "results":results,"physics_binding":False,"scientific_gate_effect":"NONE",
            "training":False,"ai_runtime":False,"claim_allowed":False,
        }
        receipt["receipt_sha256"] = sha256_obj(receipt)
        return receipt
    positive_gate = True
    for fixture in positives:
        row = evaluate_fixture(fixture); results.append({"phase":"positive", **row})
        if not row["ok"]:
            positive_gate = False
    receipt = {
        "schema":"rll.operator_lab.suite_receipt.v1","suite_id":suite.get("suite_id"),
        "state":"PASS" if positive_gate else "FAIL","negative_gate":"PASS",
        "positive_phase":"PASS" if positive_gate else "FAIL","negative_count":len(negatives),
        "positive_count":len(positives),"results":results,"physics_binding":False,
        "scientific_gate_effect":"NONE","training":False,"ai_runtime":False,
        "claim_allowed":False,
    }
    receipt["receipt_sha256"] = sha256_obj(receipt)
    return receipt
