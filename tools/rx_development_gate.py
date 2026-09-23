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
    "zero_dependency": ROOT / "results" / "rx_zero_dependency_gate.json",
    "selftest": ROOT / "results" / "rx_selftest.json",
    "sound_horizon": ROOT / "results" / "rx_sound_horizon_selftest.json",
    "freestanding65": ROOT / "results" / "rx_freestanding65_parity.json",
    "simple": ROOT / "validacao_real" / "results_rx" / "validation_summary_rx.json",
    "multiprobe": ROOT / "validacao_real" / "results_rx" / "multiprobe_rx.json",
    "parity": ROOT / "results" / "rx_semantic_parity.json",
    "dependency_audit": ROOT / "results" / "rx_dependency_audit.json",
    "migration_plan": ROOT / "results" / "rx_dependency_migration_plan.json",
    "structure_d_rx": ROOT / "results" / "structure_d" / "joint_real_likelihood_rx.json",
    "governance": ROOT / "results" / "development_governance_validation.json",
    "security_surface": ROOT / "results" / "security_surface_audit.json",
    "authority_registry": ROOT / "results" / "executable_entrypoint_authority_registry_validation.json",
    "serialization_parity": ROOT / "results" / "validacao_real_serialization_parity.json",
    "validacao_real_zero_dependency": ROOT / "results" / "validacao_real_zero_dependency_core.json",
    "http_migration": ROOT / "results" / "rx_http_migration_gate.json",
}

cli_security_receipts = sorted(
    (ROOT / "results").glob("rx_cli_security_preflight_*_develop.json")
)
if not cli_security_receipts:
    raise SystemExit("RX_DEVELOPMENT_GATE missing CLI security preflight for develop")
paths["cli_security"] = cli_security_receipts[-1]

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
checks["zero_dependency_gate"] = data["zero_dependency"].get("state") == "PASS"
checks["zero_dependency_list_empty"] = data["zero_dependency"].get("third_party_python_dependencies") == []

checks["governance_bundle_pass"] = data["governance"].get("pass") is True
checks["governance_claim_closed"] = data["governance"].get("claim_allowed") is False
checks["security_surface_strict_pass"] = data["security_surface"].get("strict_pass") is True
checks["security_surface_no_critical"] = data["security_surface"].get("critical_count") == 0
checks["authority_registry_pass"] = data["authority_registry"].get("pass") is True
checks["authority_registry_claim_closed"] = data["authority_registry"].get("claim_allowed") is False
checks["serialization_parity_pass"] = data["serialization_parity"].get("pass") is True
checks["serialization_parity_zero_third_party"] = data["serialization_parity"].get("third_party_python_dependencies") == []
checks["serialization_parity_claim_closed"] = data["serialization_parity"].get("claim_allowed") is False
checks["validacao_real_zero_dependency_pass"] = data["validacao_real_zero_dependency"].get("pass") is True
checks["validacao_real_zero_dependency_list_empty"] = data["validacao_real_zero_dependency"].get("third_party_python_dependencies") == []
checks["validacao_real_zero_dependency_claim_closed"] = data["validacao_real_zero_dependency"].get("claim_allowed") is False
checks["http_migration_pass"] = data["http_migration"].get("pass") is True
checks["http_migration_zero_third_party"] = data["http_migration"].get("third_party_python_dependencies") == []
checks["http_migration_no_network_in_gate"] = data["http_migration"].get("network_requests_performed") == 0
checks["http_migration_claim_closed"] = data["http_migration"].get("claim_allowed") is False
checks["cli_security_allow"] = data["cli_security"].get("decision") == "ALLOW"
checks["cli_security_claim_closed"] = data["cli_security"].get("claim_allowed") is False
checks["selftest_pass"] = bool(data["selftest"].get("pass"))
checks["selftest_no_training"] = data["selftest"].get("training") is False
checks["selftest_no_ai_runtime"] = data["selftest"].get("ai_runtime") is False
checks["selftest_zero_third_party"] = data["selftest"].get("third_party_python_dependencies") == []
checks["sound_horizon_reference_pass"] = data["sound_horizon"].get("pass") is True
checks["sound_horizon_no_training"] = data["sound_horizon"].get("training") is False
checks["sound_horizon_no_ai_runtime"] = data["sound_horizon"].get("ai_runtime") is False
checks["sound_horizon_claim_closed"] = data["sound_horizon"].get("claim_allowed") is False
checks["freestanding65_parity_pass"] = data["freestanding65"].get("pass") is True
checks["freestanding65_surface_N_65"] = data["freestanding65"].get("surface", {}).get("N") == 65
checks["freestanding65_no_training"] = data["freestanding65"].get("training") is False
checks["freestanding65_no_ai_runtime"] = data["freestanding65"].get("ai_runtime") is False
checks["freestanding65_claim_closed"] = data["freestanding65"].get("claim_allowed") is False

simple_runtime = data["simple"].get("runtime", {})
checks["simple_claim_closed"] = data["simple"].get("claim_allowed") is False
checks["simple_zero_third_party"] = simple_runtime.get("third_party_python_dependencies") == []

simple_security_rel = simple_runtime.get("security_preflight", "")
simple_security_path = ROOT / simple_security_rel if simple_security_rel else None
checks["simple_security_preflight_exists"] = bool(simple_security_path and simple_security_path.exists())
if checks["simple_security_preflight_exists"]:
    simple_security = json.loads(simple_security_path.read_text(encoding="utf-8"))
    checks["simple_security_allow"] = simple_security.get("decision") == "ALLOW"
    checks["simple_security_claim_closed"] = simple_security.get("claim_allowed") is False
else:
    checks["simple_security_allow"] = False
    checks["simple_security_claim_closed"] = False

multi = data["multiprobe"]
multi_runtime = multi.get("runtime", {})
surface = multi.get("data_surface", {})
checks["multiprobe_claim_closed"] = multi.get("claim_allowed") is False
checks["multiprobe_no_training"] = multi_runtime.get("training") is False
checks["multiprobe_no_ai_runtime"] = multi_runtime.get("ai_runtime") is False
checks["multiprobe_zero_third_party"] = multi_runtime.get("third_party_python_dependencies") == []

multi_security_rel = multi_runtime.get("security_preflight", "")
multi_security_path = ROOT / multi_security_rel if multi_security_rel else None
checks["multiprobe_security_preflight_exists"] = bool(multi_security_path and multi_security_path.exists())
if checks["multiprobe_security_preflight_exists"]:
    multi_security = json.loads(multi_security_path.read_text(encoding="utf-8"))
    checks["multiprobe_security_allow"] = multi_security.get("decision") == "ALLOW"
    checks["multiprobe_security_claim_closed"] = multi_security.get("claim_allowed") is False
else:
    checks["multiprobe_security_allow"] = False
    checks["multiprobe_security_claim_closed"] = False
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
migration_plan = data["migration_plan"]
checks["migration_plan_materialized"] = isinstance(migration_plan.get("rows"), list)
checks["migration_plan_no_mass_rewrite"] = migration_plan.get("policy", {}).get("automatic_mass_rewrite") is False
checks["migration_plan_active_rx_zero_dependency"] = migration_plan.get("policy", {}).get("active_rx_runtime_already_zero_dependency") is True
closed_families = {
    row.get("family"): row.get("state")
    for row in migration_plan.get("closed_families", [])
}
checks["validacao_real_yaml_matplotlib_migrated"] = (
    closed_families.get("validacao_real_yaml_matplotlib") == "MIGRATED_WITH_PARITY_GATE"
)
checks["requests_public_read_fetchers_migrated"] = (
    closed_families.get("requests_public_read_fetchers") == "MIGRATED_WITH_PARITY_GATE"
)
checks["guarded_import_data_stdlib_migrated"] = (
    closed_families.get("guarded_import_data_stdlib") == "MIGRATED_WITH_PARITY_GATE"
)
checks["docs_inventory_config_yaml_migrated"] = (
    closed_families.get("docs_inventory_config_yaml") == "MIGRATED_WITH_PARITY_GATE"
)

structure_d_rx = data["structure_d_rx"]
successor = structure_d_rx.get("structure_d_successor", {})
checks["structure_d_rx_engine"] = successor.get("engine") == "Rx"
checks["structure_d_rx_zero_third_party"] = successor.get("third_party_python_dependencies") == []
checks["structure_d_rx_no_training"] = successor.get("training") is False
checks["structure_d_rx_no_ai_runtime"] = successor.get("ai_runtime") is False
checks["structure_d_rx_legacy_preserved"] = successor.get("legacy_external_pipeline_mutated") is False
checks["structure_d_rx_claim_closed"] = structure_d_rx.get("claim_allowed") is False

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
        "No-AI runtime gate, zero-dependency runtime, governance bundle validation, entrypoint authority registry, YAML-to-JSON serialization parity, legacy validacao_real zero-dependency core, bounded HTTP requests migration, security-surface audit, CLI/simple/multiprobe security preflights, "
        "sound-horizon vectors, freestanding65 parity, Structure-D Rx successor, simple validation, current multiprobe surface, "
        "nested baselines, semantic parity ledger, dependency audit and migration plan are connected in one executable chain."
    ),
    "F_gap": (
        "Growth/CMB/r_d/Omega_r semantics are not yet unified across Structure-D and freestanding; "
        "repository-wide third-party Python migration beyond the closed validacao_real serialization/presentation, bounded HTTP fetcher, and docs-inventory config families, OS sandbox evidence, external GitHub controls and independent security review remain open."
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
