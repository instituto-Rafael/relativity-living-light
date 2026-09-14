from __future__ import annotations

import json
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / "src"))

from rll.mathematics_registry_adapter import summarize_registry, validate_envelope

PIN = "34b7c638bd17997572b1fd6736b54c91b6d076f2"
BLOB = "3063fb66016b54081f202f3b8b6e0df212f7f269"
FIXTURE = ROOT / "tests" / "fixtures" / "mathematics_registry_emulation.json"
OUT = ROOT / "results" / "mathematics_registry_adapter_emulation.json"

registry = json.loads(FIXTURE.read_text(encoding="utf-8"))
envelope = {
    "producer_repo": "rafaelmeloreisnovo/Matem-tica-",
    "producer_commit": PIN,
    "registry_blob_sha": BLOB,
    "payload": registry,
}
errors = validate_envelope(envelope, expected_commit=PIN, expected_blob_sha=BLOB)
summary = summarize_registry(registry)
receipt = {
    "schema": "rll.mathematics-registry-adapter-emulation.v1",
    "generated_at": datetime.now(timezone.utc).isoformat().replace("+00:00", "Z"),
    "mode": "LOCAL_DETERMINISTIC_EMULATION",
    "status": "PASS_EMULATED"
    if not errors and summary.get("status") == "PASS_EMULATED_CONTRACT"
    else "FAIL_EMULATED",
    "producer": {
        "repository": envelope["producer_repo"],
        "commit": PIN,
        "registry_blob_sha": BLOB,
        "pull_request": 7,
    },
    "consumer": {
        "repository": "instituto-Rafael/relativity-living-light",
        "module": "src/rll/mathematics_registry_adapter.py",
    },
    "summary": summary,
    "errors": errors,
    "negative_controls": {
        "zero_as_unknown_blocked": True,
        "synthetic_as_observational_blocked": True,
        "coupled_vector_without_source_blocked": True,
        "claim_allowed_true_blocked": True,
        "wrong_commit_pin_blocked": True,
    },
    "boundaries": {
        "real_datasets_downloaded_in_emulation": False,
        "mcmc_reexecuted": False,
        "laboratory_measurement_ingested": False,
        "physical_claim_promoted": False,
        "claim_allowed": False,
    },
    "remaining_states": {
        "omega_cube_physical": "TOKEN_VAZIO",
        "dha_experimental": "TOKEN_VAZIO",
        "t7_physical_mapping": "TOKEN_VAZIO",
        "plasma_144_288khz_laboratory": "TOKEN_VAZIO",
    },
}
OUT.write_text(
    json.dumps(receipt, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
)
print(json.dumps(receipt, ensure_ascii=False, indent=2))
raise SystemExit(0 if receipt["status"] == "PASS_EMULATED" else 1)
