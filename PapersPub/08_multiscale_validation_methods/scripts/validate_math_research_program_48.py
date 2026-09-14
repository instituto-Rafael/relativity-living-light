#!/usr/bin/env python3
"""Dependency-free structural validator for RLL Program-48 + NIBIGUIRI-12 + RIGOR-12."""
from __future__ import annotations
import importlib.util
import json
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MANIFEST = ROOT / "math_research_program_48_20260905.v1.json"
PROGRAM = ROOT / "math_research_program_48_20260905.md"
NIB = ROOT / "nibiguiri_12_isogonal_antagonistic_audit_20260905.md"
RIGOR_MD = ROOT / "rigor_self_critique_method_20260906.md"
RIGOR_METHOD = ROOT / "rigor_self_critique_method_20260906.v1.json"
RIGOR_ENGINE = ROOT / "scripts" / "rigor_self_critique_matrix.py"


def require(cond: bool, msg: str) -> None:
    if not cond:
        raise AssertionError(msg)


def load_engine():
    spec = importlib.util.spec_from_file_location("rigor_engine", RIGOR_ENGINE)
    require(spec is not None and spec.loader is not None, "load RIGOR engine")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def main() -> int:
    data = json.loads(MANIFEST.read_text(encoding="utf-8"))
    units = data["research_units"]
    lenses = data["nibiguiri_12"]
    ids = [x["id"] for x in units]
    nids = [x["id"] for x in lenses]
    counts = data["counts"]

    checks = []
    def check(name: str, cond: bool) -> None:
        require(cond, name)
        checks.append(name)

    check("16 thesis programs", sum(x["type"] == "THESIS_PROGRAM" for x in units) == 16)
    check("32 mathematical hypotheses", sum(x["type"] == "MATHEMATICAL_HYPOTHESIS" for x in units) == 32)
    check("48 unique research units", len(units) == len(set(ids)) == 48)
    check("canonical T ids", ids[:16] == [f"T{i:02d}" for i in range(1, 17)])
    check("canonical H ids", ids[16:] == [f"H{i:02d}" for i in range(1, 33)])
    check("12 unique Nibiguiri lenses", len(lenses) == len(set(nids)) == 12)
    check("isogonal 30-degree spokes", [x["angle_deg"] for x in lenses] == list(range(0, 360, 30)))
    by_id = {x["id"]: x for x in lenses}
    check("six 180-degree antagonistic pairs", all((by_id[x["opposite"]]["angle_deg"] - x["angle_deg"]) % 360 == 180 for x in lenses))
    check("opposition involution", all(by_id[by_id[n]["opposite"]]["opposite"] == n for n in nids))
    check("576 Nibiguiri audit cells", counts["audit_matrix_cells"] == len(units) * len(lenses) == 576)

    program_text = PROGRAM.read_text(encoding="utf-8")
    nib_text = NIB.read_text(encoding="utf-8")
    check("all research ids in human registry", all(i in program_text for i in ids))
    check("all Nibiguiri ids in human registry", all(i in nib_text for i in nids))
    check("TOKEN_VAZIO preserved", "TOKEN_VAZIO" in program_text and "TOKEN_VAZIO" in nib_text)
    check("hash is not proof gate", data["theory_hashing"]["hash_is_proof"] is False)

    for path in (RIGOR_MD, RIGOR_METHOD, RIGOR_ENGINE):
        check(f"RIGOR artifact exists: {path.name}", path.is_file())

    method = json.loads(RIGOR_METHOD.read_text(encoding="utf-8"))
    engine = load_engine()
    assessment = engine.blank_assessment(data, method)
    report = {uid: engine.compute_one(rec, method) for uid, rec in assessment["research_units"].items()}
    dim_ids = [d["id"] for d in method["dimensions"]]
    check("RIGOR dimensions RG01..RG12", dim_ids == [f"RG{i:02d}" for i in range(1, 13)])
    check("RIGOR base matrix 48x12=576", method["autocritique"]["base_matrix_cells"] == 576)
    check("RIGOR adversarial tensor 48x12x12=6912", method["autocritique"]["adversarial_tensor_cells"] == 6912)
    check("RIGOR initial assessment covers 48", len(assessment["research_units"]) == 48)
    check("RIGOR initial assessment is TOKEN_VAZIO not zero", all(v == "TOKEN_VAZIO" for rec in assessment["research_units"].values() for v in rec["scores_by_dimension"].values()))
    check("RIGOR report baseline unassessed", all(x["rigor_class"] == "R0_UNASSESSED" for x in report.values()))
    check("RIGOR report baseline blocked", all(x["promotion_decision"] == "BLOCKED" for x in report.values()))

    check("RIGOR engine validates authored baseline", engine.validate(data, method, assessment) == [])
    check("TOKEN_VAZIO excluded from numeric averaging", engine.numeric("TOKEN_VAZIO") is False and engine.numeric(0) is True)
    generated = engine.blank_assessment(data, method)
    check("blank assessment deterministic 48", len(generated["research_units"]) == 48)
    adversarial_count = sum(len(engine.adversarial_prompts(uid, method)) for uid in generated["research_units"])
    check("generated adversarial prompts =6912", adversarial_count == 6912)

    print("RLL_MATH_PROGRAM_48_NIBIGUIRI12_RIGOR12")
    for name in checks:
        print("PASS", name)
    print(f"PASS_TOTAL={len(checks)}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
