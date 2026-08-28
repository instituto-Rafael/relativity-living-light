import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
PATH = ROOT / "data/science/rll_recent_literature_controls_20260828.v1.json"


def load():
    return json.loads(PATH.read_text(encoding="utf-8"))


def test_controls_never_increment_data_weight_or_independence():
    c = load()
    assert c["claim_allowed"] is False
    assert c["publication_ready"] is False
    assert c["mode"] == "APPEND_ONLY_NO_DATA_WEIGHT_INCREMENT"
    assert c["controls"]
    for item in c["controls"]:
        assert item["independence_credit"] is False
        assert item["data_weight_increment"] is False


def test_august_controls_have_exact_roles():
    c = load()
    by_id = {item["id"]: item for item in c["controls"]}
    assert by_id["MNRAS_DDE_20260826"]["role"] == "G6_METHODOLOGY_CONTROL"
    assert "COMPARATOR" in by_id["PRD_COUPLED_DE_20260824"]["role"]
    assert "COMPARATOR" in by_id["PRD_ANTON_SCHMIDT_20260817"]["role"]


def test_sigma_and_bayes_are_not_collapsed():
    c = load()
    assert "PREFERENCE_SIGMA_NE_DECISIVE_BAYES" in c["invariants"]
    assert "PUBLISHED_BAYES_NE_REPRODUCED_BAYES" in c["invariants"]
    mnras = next(item for item in c["controls"] if item["id"] == "MNRAS_DDE_20260826")
    assert "DOES_NOT_SUPPORT_RLL" in mnras["rll_effect"]


def test_new_paper_is_not_new_data():
    c = load()
    assert "NEW_PAPER_NE_NEW_DATA" in c["invariants"]
    assert "SAME_DATA_REANALYSIS_NE_INDEPENDENT_REPLICATION" in c["invariants"]
