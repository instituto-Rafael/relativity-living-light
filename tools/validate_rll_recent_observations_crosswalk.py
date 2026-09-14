#!/usr/bin/env python3
"""Validate the dated, claim-gated RLL recent-observation crosswalk."""

from __future__ import annotations

import json
from datetime import datetime
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/real_sources/rll_recent_observations_crosswalk_20260825.v1.json"


def instant(value: str) -> datetime:
    return datetime.fromisoformat(value.replace("Z", "+00:00"))


def validate(path: Path = PATH) -> dict:
    data = json.loads(path.read_text(encoding="utf-8"))
    assert data["schema"] == "rll.recent_observations_crosswalk.v1"
    assert data["append_only"] is True
    assert data["claim_allowed"] is False
    assert data["policy"]["recent_context_is_evidence"] is False
    assert data["policy"]["publication_alignment_is_confirmation"] is False
    assert data["policy"]["raw_external_datasets_committed_by_this_record"] is False

    checked = instant(data["checked_at_utc"])
    observations = data["observations"]
    assert len(observations) == 5
    ids = {item["observation_id"] for item in observations}
    assert len(ids) == len(observations)
    assert sum(item["last_revision_at_utc"].startswith("2026-") for item in observations) >= 2
    assert sum(item["submitted_at_utc"].startswith("2025-") for item in observations) >= 2
    for item in observations:
        assert item["primary_source"] is True
        assert item["paper_url"].startswith("https://arxiv.org/abs/")
        assert instant(item["submitted_at_utc"]) <= instant(item["last_revision_at_utc"]) <= checked
        assert item["claim_allowed"] is False
        assert item["safe_relation_to_rll"].endswith("NOT_CONFIRMATION")
        assert item["repository_materialization"]
        assert item["rights_state"]
        assert item["likelihood_state"]

    crossings = data["thesis_crossings"]
    thesis_ids = {item["thesis_id"] for item in crossings}
    assert {"LT-001", "LT-002", "LT-003", "LT-004_TO_LT-006"} == thesis_ids
    for crossing in crossings:
        assert set(crossing["observation_ids"]).issubset(ids)
        assert crossing["claim_allowed"] is False
        assert crossing["execution_state"].startswith(("TOKEN_VAZIO_", "NOT_NEEDED_"))
    lt1 = next(item for item in crossings if item["thesis_id"] == "LT-001")
    assert set(lt1["baselines"]) == {"LCDM", "wCDM", "CPL_w0waCDM"}
    assert len(lt1["observation_ids"]) == 5

    gates = data["execution_gates"]
    assert [gate["gate_id"] for gate in gates] == [
        "G0_SOURCE_RIGHTS_FREEZE",
        "G1_OBSERVABLE_SCHEMA",
        "G2_FULL_COVARIANCE",
        "G3_LIKELIHOOD_PARITY",
        "G4_BASELINE_RECOVERY",
        "G5_ROBUST_INFERENCE",
        "G6_GROWTH_PERTURBATIONS",
        "G7_CLAIM_DECISION",
    ]
    assert gates[-1]["state"] == "BLOCKED_BY_G0_TO_G6"
    return data


if __name__ == "__main__":
    validate()
    print("PASS: five primary-source observations are dated, crossed and claim-gated")
