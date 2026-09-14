import json
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]

def load(p): return json.loads((ROOT/p).read_text(encoding="utf-8"))

def test_novoexport_formula_crosswalk_fail_closed():
    c=load("data/contracts/novoexport_formula_crosswalk.v1.json")
    r=load("provenance/receipts/rll_novoexport_formula_ingest_20260828.json")
    assert c["claim_allowed"] is False
    assert r["claim_allowed"] is False
    assert c["source"]["raw018_state"] == "TOKEN_VAZIO_PROVIDER_GAP"
    assert c["canonical_rll_formula_ids"] == [f"RLL-F{i:03d}" for i in range(1,24)]
    assert c["rll_subset"]["occurrences"] == 8793
    assert c["rll_subset"]["canonical_candidates"] == 6333
    assert len(c["rll_subset"]["candidate_index_sha256"]) == 64
    assert c["rll_subset"]["candidate_index_publication"].startswith("HASH_ONLY_PUBLIC_RLL")
    assert r["full_index_publication"] == "WITHHELD_FROM_PUBLIC_REPO_PRIVACY_BOUNDARY"
