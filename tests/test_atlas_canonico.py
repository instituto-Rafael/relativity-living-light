from pathlib import Path
import re

ROOT = Path(__file__).resolve().parents[1]
ATLAS = ROOT / "docs/atlas_canonico/ATLAS_CANONICO_NUMERADO_V1.md"
SCHEMA = ROOT / "docs/atlas_canonico/atlas.schema.yaml"
RELATIONS = ROOT / "docs/atlas_canonico/relations_v1.tsv"

def test_atlas_numbering():
    text = ATLAS.read_text(encoding="utf-8")
    nums = [int(x) for x in re.findall(r"(?m)^(\d+)\. \[", text)]
    assert len(nums) == 280, f"expected 280 items, got {len(nums)}"
    assert nums == list(range(1, 281)), "atlas numbering must be contiguous 1..280"

def test_epistemic_invariants_present():
    text = ATLAS.read_text(encoding="utf-8")
    for invariant in [
        "SOURCE ≠ ARTEFATO ≠ EXECUÇÃO ≠ EVIDÊNCIA ≠ CLAIM",
        "TOKEN_VAZIO",
        "IMPLEMENTED_UNTESTED",
        "supersedes",
    ]:
        assert invariant in text, invariant

def test_relations_shape_and_item_bounds():
    lines = RELATIONS.read_text(encoding="utf-8").splitlines()
    assert lines[0].split("\t") == ["source_id", "relation", "target_id", "evidence_or_note"]
    for i, line in enumerate(lines[1:], start=2):
        if not line.strip():
            continue
        cols = line.split("\t")
        assert len(cols) == 4, f"line {i}: expected 4 TSV columns"
        for value in (cols[0], cols[2]):
            m = re.fullmatch(r"ITEM-(\d{6})", value)
            if m:
                n = int(m.group(1))
                assert 1 <= n <= 280, f"line {i}: out-of-range item {value}"

def test_relation_types_declared():
    schema = SCHEMA.read_text(encoding="utf-8")
    lines = RELATIONS.read_text(encoding="utf-8").splitlines()[1:]
    relation_types = {line.split("\t")[1] for line in lines if line.strip()}
    for relation in relation_types:
        assert f"  - {relation}" in schema, f"relation not declared in schema: {relation}"
