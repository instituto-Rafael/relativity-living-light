from __future__ import annotations
import copy, json
from pathlib import Path
from tools.validate_branch_advance_registry import validate

ROOT=Path(__file__).resolve().parents[1]
REG=ROOT/"data/governance/branch_advance_registry.v2.json"


def payload(): return json.loads(REG.read_text(encoding="utf-8"))

def test_current_registry_passes(): assert validate(payload()) == []

def test_absorbed_requires_zero_ahead():
    p=copy.deepcopy(payload()); e=next(x for x in p["entries"] if x["class"]=="ABSORBED_AHEAD_ZERO"); e["ahead"]=1; assert any("ABSORBED_NONZERO" in x for x in validate(p))

def test_false_ahead_requires_merged_main_evidence():
    p=copy.deepcopy(payload()); e=next(x for x in p["entries"] if x["class"]=="MERGED_HISTORY_FALSE_AHEAD"); e.pop("source_pr"); assert any("FALSE_AHEAD_EVIDENCE" in x for x in validate(p))

def test_unclassified_remainder_stays_token_vazio():
    p=copy.deepcopy(payload()); p["unclassified_remainder"]="DONE"; assert "UNCLASSIFIED_REMAINDER_BOUNDARY" in validate(p)
