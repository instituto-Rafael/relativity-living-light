#!/usr/bin/env python3
import json
import pathlib
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
CONTRACT = ROOT / "data/contracts/rll_p0_science_closure_20260811.json"
ALLOWED_STATES = {"TOKEN_VAZIO", "PARTIAL", "PASS", "FAIL", "BLOCKED"}


def fail(msg: str) -> None:
    print(f"FAIL: {msg}")
    raise SystemExit(1)


def main() -> int:
    if not CONTRACT.is_file():
        fail(f"missing contract: {CONTRACT}")

    data = json.loads(CONTRACT.read_text(encoding="utf-8"))
    if data.get("claim_allowed") is not False:
        fail("top-level claim_allowed must remain false until promotion gate closes")

    policy = data.get("policy", {})
    for key in (
        "fail_closed",
        "token_vazio_is_valid_state",
        "no_placeholder_promotion",
        "same_data_same_likelihood_same_priors_for_model_comparison",
        "negative_results_must_be_preserved",
        "independent_reproduction_required_for_promotion",
    ):
        if policy.get(key) is not True:
            fail(f"required policy is not true: {key}")

    gates = data.get("gates")
    if not isinstance(gates, list) or not gates:
        fail("gates must be a non-empty list")

    ids = set()
    blocking_open = []
    for gate in gates:
        gid = gate.get("id")
        if not gid or gid in ids:
            fail(f"missing or duplicate gate id: {gid}")
        ids.add(gid)
        if gate.get("priority") != "P0":
            fail(f"P0 closure contract contains non-P0 gate: {gid}")
        state = gate.get("state")
        if state not in ALLOWED_STATES:
            fail(f"invalid state for {gid}: {state}")
        if not gate.get("required") or not gate.get("acceptance") or not gate.get("evidence_path"):
            fail(f"incomplete evidence contract for {gid}")
        if state != "PASS":
            blocking_open.append(gid)

    promotion = data.get("promotion_rule", {})
    if promotion.get("forbid_manual_override") is not True:
        fail("manual promotion override must remain forbidden")
    if blocking_open and promotion.get("claim_allowed") is not False:
        fail("promotion claim_allowed must be false while P0 gates remain open")

    print(json.dumps({
        "status": "PASS",
        "contract": data.get("contract_id"),
        "claim_allowed": False,
        "gate_count": len(gates),
        "open_gate_count": len(blocking_open),
        "open_gates": blocking_open,
        "meaning": "contract integrity passed; scientific hypothesis is not promoted"
    }, indent=2))
    return 0


if __name__ == "__main__":
    sys.exit(main())
