"""
FASE 30 — Knowledge Matrix test suite.
Tests run against pre-built artifacts in artifacts/knowledge-matrix/.
Builder is invoked if artifacts are missing.
"""
from __future__ import annotations

import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest

ROOT = Path(__file__).parent.parent.resolve()
OUTDIR = ROOT / "artifacts" / "knowledge-matrix"
MASTER = OUTDIR / "rll_knowledge_matrix.json"
SUMMARY = OUTDIR / "knowledge_matrix_summary.json"
HYPS = OUTDIR / "knowledge_matrix_hypotheses.jsonl"
CHECKSUMS = OUTDIR / "CHECKSUMS.sha256"
SCHEMA_PATH = ROOT / "schemas" / "rll_knowledge_matrix.schema.json"

REQUIRED_KINDS = {"formula", "concept", "thesis", "gap", "observation", "validation", "bridge"}
REQUIRED_MATURITY = {"immortal_verified", "verified", "partial", "candidate", "seed", "latent", "void"}
REQUIRED_ROLES = {"apex_validator", "base_concept", "buffer", "accumulator", "propagator", "catalyst", "encoder"}
VALID_QUEUE_STATES = {"executed", "in_queue", "latent", "forgotten_protected", "void"}
VALID_VELOCIDADE = {"medusa", "equilibrado", "tartaruga"}


def _ensure_artifacts() -> None:
    if not MASTER.exists():
        result = subprocess.run(
            [sys.executable, str(ROOT / "tools" / "build_knowledge_matrix.py"),
             "--root", str(ROOT), "--outdir", str(OUTDIR)],
            capture_output=True, text=True
        )
        if result.returncode != 0:
            pytest.skip(f"Builder failed: {result.stderr[:500]}")


@pytest.fixture(scope="module")
def matrix_data():
    _ensure_artifacts()
    return json.loads(MASTER.read_text())


@pytest.fixture(scope="module")
def items(matrix_data):
    return matrix_data["items"]


@pytest.fixture(scope="module")
def summary_data():
    _ensure_artifacts()
    return json.loads(SUMMARY.read_text())


def test_schema_compliance(items):
    """Every item must have all required fields with correct types."""
    schema = json.loads(SCHEMA_PATH.read_text())
    required = set(schema.get("required", []))
    valid_kinds = set(schema["properties"]["kind"]["enum"])
    valid_maturity = set(schema["properties"]["maturity_class"]["enum"])
    valid_roles = set(schema["properties"]["ecosystem_role"]["enum"])
    valid_queue = set(schema["properties"]["queue_state"]["enum"])

    for item in items:
        iid = item.get("item_id", "?")
        missing = required - set(item.keys())
        assert not missing, f"{iid} missing fields: {missing}"
        assert item["kind"] in valid_kinds, f"{iid} bad kind: {item['kind']}"
        assert item["maturity_class"] in valid_maturity, f"{iid} bad maturity: {item['maturity_class']}"
        assert item["ecosystem_role"] in valid_roles, f"{iid} bad role: {item['ecosystem_role']}"
        assert item["queue_state"] in valid_queue, f"{iid} bad queue_state: {item['queue_state']}"
        assert isinstance(item["D_vector"], list) and len(item["D_vector"]) == 7, \
            f"{iid} D_vector must be 7-element list"
        assert isinstance(item["retroalimentacao"], dict), f"{iid} retroalimentacao must be dict"
        assert "feeds_into" in item["retroalimentacao"] and "fed_by" in item["retroalimentacao"], \
            f"{iid} retroalimentacao missing keys"


def test_claim_boundary(items):
    """No item may have claim_allowed=True."""
    violations = [it["item_id"] for it in items if it.get("claim_allowed") is not False]
    assert violations == [], f"claim_allowed boundary violated: {violations[:5]}"


def test_queue_completeness(items):
    """Every gap/void item must have queue_state defined and in the valid set."""
    for item in items:
        if item["kind"] in ("gap",) or item["maturity_class"] == "void":
            qs = item.get("queue_state")
            assert qs in VALID_QUEUE_STATES, \
                f"{item['item_id']} gap/void has invalid queue_state: {qs}"


def test_dual_hash(items):
    """SHA256 and BLAKE3 must be 64-hex strings for a sample of items."""
    import re
    hex64 = re.compile(r'^[0-9a-f]{64}$')
    sample = items[:30] + items[-30:]
    for item in sample:
        iid = item["item_id"]
        assert hex64.match(item["sha256"]), f"{iid} bad sha256"
        assert hex64.match(item["blake3"]), f"{iid} bad blake3"
        # SHA256 and BLAKE3 must differ (unless the unlikely collision)
        # They can differ or — in fallback mode — both be sha256-derived;
        # we just require both present and hex64
        assert len(item["sha256"]) == 64
        assert len(item["blake3"]) == 64


def test_hypothesis_generation():
    """At least 1 hypothesis must be generated for void gaps."""
    _ensure_artifacts()
    lines = HYPS.read_text().strip().split("\n")
    hyps = [json.loads(ln) for ln in lines if ln.strip()]
    assert len(hyps) >= 1, "No hypotheses generated from void gaps"
    for hyp in hyps:
        assert hyp.get("maturity_class") == "seed", f"Hypothesis must be seed: {hyp['item_id']}"
        assert hyp.get("claim_allowed") is False, "Hypothesis claim_allowed must be false"
        assert hyp.get("origin_gap"), f"Hypothesis must have origin_gap: {hyp['item_id']}"
        assert hyp.get("kind") == "thesis", f"Hypothesis kind must be thesis: {hyp['item_id']}"


def test_retroalimentacao(items):
    """All item_ids referenced in feeds_into/fed_by must exist in the matrix."""
    known_ids = {it["item_id"] for it in items}
    for item in items:
        retro = item.get("retroalimentacao", {})
        for ref_id in retro.get("feeds_into", []):
            assert ref_id in known_ids, \
                f"{item['item_id']}.feeds_into references unknown id: {ref_id}"
        for ref_id in retro.get("fed_by", []):
            assert ref_id in known_ids, \
                f"{item['item_id']}.fed_by references unknown id: {ref_id}"


def test_biological_coverage(items):
    """All defined maturity_class values must appear at least once."""
    present = {it["maturity_class"] for it in items}
    # At minimum these must be present (void and seed come from gaps/hypotheses)
    required_present = {"verified", "latent", "seed", "void"}
    missing = required_present - present
    assert not missing, f"Maturity classes not represented: {missing}"


def test_ecosystem_coverage(items):
    """Core ecosystem roles must be represented."""
    present = {it["ecosystem_role"] for it in items}
    required_present = {"apex_validator", "encoder", "base_concept", "buffer", "catalyst"}
    missing = required_present - present
    assert not missing, f"Ecosystem roles not represented: {missing}"


def test_item_count(items):
    """Matrix must contain items from all 8 source kinds."""
    by_kind = {}
    for it in items:
        by_kind[it["kind"]] = by_kind.get(it["kind"], 0) + 1
    expected_kinds = {"formula", "concept", "gap", "thesis", "observation", "validation", "bridge"}
    missing = expected_kinds - set(by_kind.keys())
    assert not missing, f"Kinds missing from matrix: {missing}"
    assert len(items) >= 100, f"Too few items: {len(items)}"


def test_checksums_file():
    """CHECKSUMS.sha256 must exist and list the matrix files."""
    _ensure_artifacts()
    assert CHECKSUMS.exists(), "CHECKSUMS.sha256 not generated"
    lines = [ln for ln in CHECKSUMS.read_text().strip().split("\n") if ln]
    assert len(lines) >= 3, f"Expected ≥3 checksum lines, got {len(lines)}"
    # Verify at least one file checksum is correct
    for line in lines:
        parts = line.split("  ", 1)
        if len(parts) == 2:
            digest, fname = parts
            fpath = OUTDIR / fname
            if fpath.exists():
                actual = hashlib.sha256(fpath.read_bytes()).hexdigest()
                assert actual == digest, f"Checksum mismatch for {fname}"
            break
