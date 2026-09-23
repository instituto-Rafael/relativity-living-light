#!/usr/bin/env python3
"""Rx development gate.

Aggregates the executable development chain. This is a software-development
gate, not a model-training or AI gate.
"""

from __future__ import annotations

import json
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]

paths = {
    "no_ai": ROOT / "results" / "rx_no_ai_runtime_gate.json",
    "selftest": ROOT / "results" / "rx_selftest.json",
    "sound_horizon": ROOT / "results" / "rx_sound_horizon_selftest.json",
    "simple": ROOT / "validacao_real" / "results_rx" / "validation_summary_rx.json",
    "multiprobe": ROOT / "validacao_real" / "results_rx" / "multiprobe_rx.json",
    "parity": ROOT / "results" / "rx_semantic_parity.json",
    "dependency_audit": ROOT / "results" / "rx_dependency_audit.json",
}

missing = [name for name, path in paths.items() if not path.exists()]
if missing:
    raise SystemExit("RX_DEVELOPMENT_GATE missing artifacts: %s" % ", ".join(missing))

data = {
    name: json.loads(path.read_text(encoding="utf-8"))
    for name, path in paths.items()
}

checks = {}

checks["no_ai_runtime_gate"] = data["no_ai"].get("state") == "PASS"
checks["no_ai_training_false"] = data["no_ai"].get("policy", {}).get("training") is False
checks["no_ai_runtime_false"] = data["no_ai"].get("policy", {}).get("ai_runtime") is False
checks["selftest_pass"] = bool(data["selftest"].get("pass"))
checks["selftest_no_training"] = data["selftest"].get("training") is False
checks["selftest_no_ai_runtime"] = data["selftest"].get("ai_runtime") is False
checks["selftest_zero_third_party"] = data["selftest"].get("third_party_python_dependencies") == []
checks["sound_horizon_reference_pass"] = data["sound_horizon"].get("pass") is True
checks["sound_horizon_no_training"] = data["sound_horizon"].get("training") is False
checks["sound_horizon_no_ai_runtime"] = data["sound_horizon"].get("ai_runtime") is False
checks["sound_horizon_claim_closed"] = data["sound_horizon"].get("claim_allowed") is False

simple_runtime = data["simple"].get("runtime", {})
checks["simple_claim_closed"] = data["simple"].get("claim_allowed") is False
checks["simple_zero_third_party"] = simple_runtime.get("third_party_python_dependencies") == []

multi = data["multiprobe"]
multi_runtime = multi.get("runtime", {})
surface = multi.get("data_surface", {})
checks["multiprobe_claim_closed"] = multi.get("claim_allowed") is False
checks["multiprobe_no_training"] = multi_runtime.get("training") is False
checks["multiprobe_no_ai_runtime"] = multi_runtime.get("ai_runtime") is False
checks["multiprobe_zero_third_party"] = multi_runtime.get("third_party_python_dependencies") == []
checks["multiprobe_N_consistent"] = (
    int(surface.get("N", -1))
    == int(surface.get("Hz", 0))
    + int(surface.get("DESI_DR2_BAO", 0))
    + int(surface.get("fsigma8", 0))
    + int(surface.get("CMB_compressed_parameters", 0))
)
checks["multiprobe_current_N_60"] = int(surface.get("N", -1)) == 60
contract = multi.get("physics_contract", {})
checks["multiprobe_contract_id"] = contract.get("id") == "RX-STRUCTURE-D-PARITY-V1"
checks["multiprobe_contract_claim_closed"] = contract.get("claim_allowed") is False

nested = multi.get("nested_invariants", {})
checks["nested_wCDM"] = bool(nested.get("wCDM", {}).get("pass"))
checks["nested_CPL"] = bool(nested.get("CPL", {}).get("pass"))
checks["nested_RLL"] = bool(nested.get("RLL", {}).get("pass"))

parity = data["parity"]
parity_gates = parity.get("gates", {})
checks["parity_claim_closed"] = parity_gates.get("claim_allowed") is False
checks["parity_background_shared"] = parity_gates.get("background_model_equations_shared") == "PASS_BY_CONTRACT"
checks["growth_divergence_explicit"] = parity_gates.get("growth_semantics_state") == "CONTRACT_DIVERGENCE"
checks["cmb_divergence_explicit"] = parity_gates.get("cmb_acoustic_semantics_state") == "CONTRACT_DIVERGENCE"
checks["rd_divergence_explicit"] = parity_gates.get("rd_semantics_state") == "CONTRACT_DIVERGENCE"
checks["radiation_divergence_explicit"] = parity_gates.get("radiation_density_semantics_state") == "CONTRACT_DIVERGENCE"

audit = data["dependency_audit"]
checks["dependency_audit_materialized"] = isinstance(audit.get("files"), list)

failed = [name for name, passed in checks.items() if not passed]
state = "PASS_WITH_OPEN_CONTRACT_DIVERGENCES" if not failed else "FAIL"

payload = {
    "schema": "rll.rx.development_gate.v1",
    "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "state": state,
    "training": False,
    "ai_runtime": False,
    "claim_allowed": False,
    "checks": checks,
    "failed_checks": failed,
    "open_contract_divergences": [
        "growth: Structure-D sigma8*Omega_m(z)^0.55 vs freestanding f*sigma8*D(z)",
        "CMB acoustic scale: Structure-D r_d vs freestanding r_s(z_star)",
        "sound-horizon calibration: fitted r_d approximation vs pinned/integrated freestanding horizons",
        "radiation density: Structure-D/Rx 9.0e-5 vs FASE18E/freestanding 9.18e-5",
    ],
    "migration_debt": {
        "python_files_with_external_imports": audit.get("python_files_with_external_imports"),
        "external_import_occurrences_by_module": audit.get("external_import_occurrences_by_module", {}),
    },
    "artifacts": {name: str(path.relative_to(ROOT)) for name, path in paths.items()},
    "F_ok": (
        "No-AI runtime gate, Rx stdlib runtime, sound-horizon reference vectors, simple validation, current multiprobe surface, "
        "nested baselines, semantic parity ledger and dependency audit are connected in one executable chain."
    ),
    "F_gap": (
        "Growth/CMB/r_d semantics are not yet unified across Structure-D and freestanding; "
        "repository-wide third-party Python migration remains open."
    ),
    "F_next": (
        "Choose and version one common growth/CMB/sound-horizon contract, then require "
        "numerical parity on the common data surface before retiring legacy Structure-D dependencies."
    ),
}

out_json = ROOT / "results" / "rx_development_gate.json"
out_md = ROOT / "results" / "rx_development_gate.md"
out_json.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

lines = [
    "# Rx development gate",
    "",
    "State: **%s**" % state,
    "",
    "Training: false. AI runtime: false. Claim allowed: false.",
    "",
    "## Checks",
    "",
]
for name, passed in checks.items():
    lines.append("- %s: %s" % (name, "PASS" if passed else "FAIL"))
lines += [
    "",
    "## Open contract divergences",
    "",
]
for item in payload["open_contract_divergences"]:
    lines.append("- " + item)
lines += [
    "",
    "## R3",
    "",
    "- F_ok: " + payload["F_ok"],
    "- F_gap: " + payload["F_gap"],
    "- F_next: " + payload["F_next"],
]
out_md.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("RX_DEVELOPMENT_GATE=" + state)
for name, passed in checks.items():
    print(("PASS " if passed else "FAIL ") + name)
print("claim_allowed=False training=False ai_runtime=False")
print("wrote", out_json.relative_to(ROOT))
print("wrote", out_md.relative_to(ROOT))

if failed:
    raise SystemExit(1)
