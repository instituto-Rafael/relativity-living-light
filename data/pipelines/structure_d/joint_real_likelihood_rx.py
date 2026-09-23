"""Structure-D zero-dependency successor backed by the Rx multiprobe runtime.

This module is additive. It does not mutate the historical NumPy/Pandas/SciPy
pipeline. It materializes a Structure-D artifact from the versioned Rx physics
contract.

Run:
    python3 -m data.pipelines.structure_d.joint_real_likelihood_rx
"""

from __future__ import annotations

import csv
import json
import runpy
import shutil
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[3]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from rx.contracts import active_contract
from rx.kernel import dump_json, load_json

RX_RESULTS = ROOT / "validacao_real" / "results_rx"
STRUCTURE_RESULTS = ROOT / "results" / "structure_d"
STRUCTURE_RESULTS.mkdir(parents=True, exist_ok=True)

CONTRACT_ID, CONTRACT = active_contract()
if CONTRACT_ID != "RX-STRUCTURE-D-PARITY-V1":
    raise SystemExit("Structure-D Rx successor requires RX-STRUCTURE-D-PARITY-V1")

runpy.run_module("validacao_real.run_rx_multiprobe", run_name="__main__")

source_json = RX_RESULTS / "multiprobe_rx.json"
source_csv = RX_RESULTS / "multiprobe_rx.csv"
if not source_json.exists() or not source_csv.exists():
    raise SystemExit("Rx multiprobe did not materialize expected artifacts")

payload = load_json(source_json)
if payload.get("claim_allowed") is not False:
    raise SystemExit("Rx claim boundary unexpectedly open")
if payload.get("physics_contract", {}).get("id") != CONTRACT_ID:
    raise SystemExit("Rx result physics contract mismatch")

structure_payload = dict(payload)
structure_payload["schema"] = "rll.structure_d.rx_successor.v1"
structure_payload["structure_d_successor"] = {
    "created_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "engine": "Rx",
    "third_party_python_dependencies": [],
    "training": False,
    "ai_runtime": False,
    "legacy_external_pipeline_mutated": False,
    "legacy_module": "data.pipelines.structure_d.joint_real_likelihood_flat",
    "physics_contract_id": CONTRACT_ID,
    "relation": "dependency-free successor for the current flat Structure-D semantics",
}
structure_payload["claim_allowed"] = False
structure_payload["model_selection_claim_allowed"] = False

out_json = STRUCTURE_RESULTS / "joint_real_likelihood_rx.json"
out_csv = STRUCTURE_RESULTS / "joint_real_likelihood_rx.csv"
out_manifest = STRUCTURE_RESULTS / "joint_real_likelihood_rx_manifest.json"

dump_json(out_json, structure_payload)
shutil.copyfile(source_csv, out_csv)

manifest = {
    "schema": "rll.structure_d.rx_successor_manifest.v1",
    "generated_utc": structure_payload["structure_d_successor"]["created_utc"],
    "source_artifact": str(source_json.relative_to(ROOT)),
    "output_json": str(out_json.relative_to(ROOT)),
    "output_csv": str(out_csv.relative_to(ROOT)),
    "physics_contract_id": CONTRACT_ID,
    "physics_contract": CONTRACT,
    "third_party_python_dependencies": [],
    "training": False,
    "ai_runtime": False,
    "claim_allowed": False,
    "legacy_external_pipeline_mutated": False,
}
dump_json(out_manifest, manifest)

print("STRUCTURE_D_RX_SUCCESSOR=PASS")
print("physics_contract=", CONTRACT_ID)
print("third_party_python_dependencies=0 training=False ai_runtime=False")
print("claim_allowed=False")
print("wrote", out_json.relative_to(ROOT))
print("wrote", out_csv.relative_to(ROOT))
print("wrote", out_manifest.relative_to(ROOT))
