import json
from pathlib import Path

import pytest
import yaml

from tools.build_research_fragment_site_data import build_bundle
from tools.ingest_arxiv_candidate import make_candidate, normalize_arxiv_identifier, parse_arxiv_atom

ROOT = Path(__file__).resolve().parents[1]
GRAPH_PATH = ROOT / "results/relational_validation/packages/ACADEMIC_CORR_001/relation_graph.json"
PACKAGE_PATH = ROOT / "results/relational_validation/packages/ACADEMIC_CORR_001/package.yml"
BIBLIOGRAPHY_PATH = ROOT / "data/research_fragments/academic_correlation_sources.yml"

ATOM_SAMPLE = b"""<?xml version='1.0' encoding='UTF-8'?>
<feed xmlns='http://www.w3.org/2005/Atom' xmlns:arxiv='http://arxiv.org/schemas/atom'>
  <entry>
    <id>http://arxiv.org/abs/2503.14738v3</id>
    <published>2025-03-18T21:14:12Z</published>
    <updated>2025-10-09T16:45:28Z</updated>
    <title>DESI DR2 Results II: Measurements of Baryon Acoustic Oscillations</title>
    <summary>A bounded metadata test record.</summary>
    <author><name>DESI Collaboration</name></author>
    <category term='astro-ph.CO' />
    <arxiv:doi>10.1103/tr6y-kpc6</arxiv:doi>
    <arxiv:journal_ref>Phys. Rev. D 112, 083515 (2025)</arxiv:journal_ref>
  </entry>
</feed>
"""


def load_inputs():
    graph = json.loads(GRAPH_PATH.read_text(encoding="utf-8"))
    package = yaml.safe_load(PACKAGE_PATH.read_text(encoding="utf-8"))
    bibliography = yaml.safe_load(BIBLIOGRAPHY_PATH.read_text(encoding="utf-8"))
    return graph, package, bibliography


def test_normalize_arxiv_id_and_abstract_url():
    assert normalize_arxiv_identifier("2503.14738") == ("2503.14738", None)
    assert normalize_arxiv_identifier("https://arxiv.org/abs/2503.14738v3") == (
        "2503.14738",
        "v3",
    )


def test_parse_atom_preserves_public_metadata_and_version():
    record = parse_arxiv_atom(ATOM_SAMPLE, "2503.14738")
    assert record["work_id"] == "arxiv:2503.14738v3"
    assert record["authors"] == ["DESI Collaboration"]
    assert record["categories"] == ["astro-ph.CO"]
    assert record["doi"] == "10.1103/tr6y-kpc6"


def test_candidate_rejects_arxiv_api_result_for_different_work():
    graph, _, _ = load_inputs()
    with pytest.raises(ValueError, match="differs from API result"):
        make_candidate(
            ATOM_SAMPLE,
            "2503.14739",
            [],
            "",
            graph,
            "2026-10-02T00:00:00Z",
        )


def test_human_relation_candidates_require_known_nodes_and_a_reason():
    graph, _, _ = load_inputs()
    with pytest.raises(ValueError, match="relation_note is required"):
        make_candidate(
            ATOM_SAMPLE,
            "2503.14738",
            ["RLL"],
            "",
            graph,
            "2026-10-02T00:00:00Z",
        )
    candidate = make_candidate(
        ATOM_SAMPLE,
        "2503.14738",
        ["RLL"],
        "Adversarial context for review.",
        graph,
        "2026-10-02T00:00:00Z",
    )
    assert candidate["claim_allowed"] is False
    assert candidate["candidate_relations"][0]["review_state"] == "RELATIONAL_PENDING"
    assert candidate["candidate_relations"][0]["source_sha256"] == candidate["source_sha256"]


def test_site_bundle_links_references_and_keeps_pending_claim_boundary():
    graph, package, bibliography = load_inputs()
    candidate = make_candidate(
        ATOM_SAMPLE,
        "2503.14738",
        ["RLL"],
        "Adversarial context for review.",
        graph,
        "2026-10-02T00:00:00Z",
        run_id="123",
        actor="researcher",
    )
    bundle = build_bundle(
        graph,
        package,
        bibliography,
        {"relation_graph": "a" * 64, "package": "b" * 64, "bibliography": "c" * 64},
        revision="deadbeef",
        run_id="123",
        candidate=candidate,
    )
    assert bundle["claim_allowed"] is False
    assert len(bundle["bibliography"]) == 2
    assert bundle["candidate_intake"]["source_sha256"] == candidate["source_sha256"]
    assert bundle["edges"][0]["review_state"] == "RELATIONAL_PENDING"
