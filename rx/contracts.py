"""Rx physics-contract loader.

Stdlib only. Physics changes require a new versioned contract.
"""

from __future__ import annotations

import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTRACTS_PATH = ROOT / "configs" / "rx_physics_contracts.json"


def load_contracts():
    return json.loads(CONTRACTS_PATH.read_text(encoding="utf-8"))


def active_contract():
    payload = load_contracts()
    contract_id = payload["active_contract"]
    return contract_id, payload["contracts"][contract_id]


def require_contract(contract_id):
    payload = load_contracts()
    return payload["contracts"][contract_id]
