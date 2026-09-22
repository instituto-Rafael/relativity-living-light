from pathlib import Path
import json

from tools.run_omega_math_explorer import load_contract, write_artifacts

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "data/contracts/omega_math_explorer.v1.yml"
SCHEMA = ROOT / "schemas/omega_math_explorer.schema.json"


def test_omega_math_explorer_materializes_reconstructible_artifacts(tmp_path: Path):
    contract = load_contract(MANIFEST, SCHEMA)
    receipt = write_artifacts(contract, MANIFEST, SCHEMA, tmp_path, 2)
    assert receipt["decision"] == "PASS_FORMAL_SHADOW"
    assert receipt["claim_allowed"] is False
    assert receipt["publication_effect"] == "NONE"
    required = {
        "resolved_manifest.json",
        "constants.json",
        "gate_results.json",
        "hypothesis_results.json",
        "exploration.json",
        "candidates.csv",
        "anomalies.json",
        "semantic_graph.json",
        "report.md",
        "receipt.json",
        "CHECKSUMS.sha256",
    }
    assert required <= {path.name for path in tmp_path.iterdir()}


def test_omega_math_core_gates_and_hypothesis_boundaries(tmp_path: Path):
    contract = load_contract(MANIFEST, SCHEMA)
    write_artifacts(contract, MANIFEST, SCHEMA, tmp_path, 2)
    gates = json.loads((tmp_path / "gate_results.json").read_text(encoding="utf-8"))
    assert all(gate["status"] == "PASS" for gate in gates)
    by_id = {gate["id"]: gate for gate in gates}
    assert by_id["G-LCM-5678"]["observed"] == 840
    assert by_id["G-RAYS-5678"]["observed"] == 22
    assert by_id["G-LINES-5678"]["observed"] == 16

    assert by_id["G-SCALE-344"]["status"] == "PASS"
    assert abs(by_id["G-SCALE-344"]["observed"]["cos_pi_over_3"] - 0.5) <= 1.0e-12

    hypotheses = json.loads(
        (tmp_path / "hypothesis_results.json").read_text(encoding="utf-8")
    )
    by_hypothesis = {row["id"]: row for row in hypotheses}
    assert by_hypothesis["H-AREA-UNIVERSAL"]["state"] == "REFUTADO"
    assert by_hypothesis["H-840-SEMANTIC"]["state"] == "TOKEN_VAZIO"
    assert by_hypothesis["H-PHYSICAL-INFINITY"]["state"] == "BLOCKED"


def test_explorer_emits_multidimensional_relations(tmp_path: Path):
    contract = load_contract(MANIFEST, SCHEMA)
    write_artifacts(contract, MANIFEST, SCHEMA, tmp_path, 3)
    exploration = json.loads(
        (tmp_path / "exploration.json").read_text(encoding="utf-8")
    )
    assert {row["n"] for row in exploration["polygons"]} >= {3, 4, 5, 6, 7, 8}
    groups = {
        tuple(row["values"]): row for row in exploration["angular_groups"]
    }
    assert groups[(5, 6, 7, 8)]["lcm"] == 840
    assert groups[(5, 6, 7, 8)]["distinct_rays_common_phase"] == 22
    assert any(
        row["constant"] == "sqrt2" and row["n"] == 4
        for row in exploration["constant_matches"]
    )
    assert any(
        row["constant"] == "sqrt3_over_2" and row["n"] == 6
        for row in exploration["constant_matches"]
    )
    assert any(
        row["constant"] == "phi" and row["n"] == 5
        for row in exploration["constant_matches"]
    )


    rewrites = [
        row for row in exploration["nested_scale_collisions"]
        if row["status"] == "DERIVED_REWRITE_IDENTITY_COS60_EQ_COS45_SQUARED"
    ]
    assert rewrites

    anomalies = json.loads((tmp_path / "anomalies.json").read_text(encoding="utf-8"))
    assert anomalies == []

    receipt = json.loads((tmp_path / "receipt.json").read_text(encoding="utf-8"))
    assert receipt["residuals"]["ideal_objective"]["J"] == 0
    assert receipt["residuals"]["ideal_objective"]["target_reached"] is True
