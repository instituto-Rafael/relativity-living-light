#!/usr/bin/env python3
"""Build a typed migration plan from the global Rx dependency audit.

This tool plans migration; it does not rewrite files automatically.
"""

from __future__ import annotations

import json
from collections import Counter, defaultdict
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
AUDIT = ROOT / "results" / "rx_dependency_audit.json"
OUT_JSON = ROOT / "results" / "rx_dependency_migration_plan.json"
OUT_MD = ROOT / "results" / "rx_dependency_migration_plan.md"
SERIALIZATION_PARITY = ROOT / "results" / "validacao_real_serialization_parity.json"
VALIDACAO_ZERO_DEP = ROOT / "results" / "validacao_real_zero_dependency_core.json"
INVENTORY_CONFIG_PARITY = ROOT / "results" / "inventory_config_serialization_parity.json"
PLOT_MIGRATION_GATE = ROOT / "results" / "rx_plot_migration_gate.json"
HTTP_MIGRATION_GATE = ROOT / "results" / "rx_http_migration_gate.json"
CREDENTIAL_STDLIB_GATE = ROOT / "results" / "credential_authority_stdlib_migration.json"
WATCH_CONFIG_GATE = ROOT / "results" / "watch_config_stdlib_migration.json"
CALC_DATA_STDLIB_GATE = ROOT / "results" / "calc_data_stdlib_migration.json"
VALIDATION_DETERMINISTIC_GATE = ROOT / "results" / "validation_deterministic_stdlib_migration.json"

if not AUDIT.exists():
    raise SystemExit("dependency audit missing; run tools/rx_dependency_audit.py first")

audit = json.loads(AUDIT.read_text(encoding="utf-8"))

replacement = {
    "numpy": "RX_KERNEL_NUMERIC_OR_DOMAIN_PORT",
    "pandas": "PYTHON_STDLIB_CSV_JSON_OR_RX_IO",
    "scipy": "RX_OPTIMIZER_INTEGRATION_LINEAR_ALGEBRA",
    "yaml": "VERSIONED_JSON_OR_EXPLICIT_SUBSET_PARSER",
    "matplotlib": "RX_SVG_OUTPUT",
    "emcee": "TOKEN_VAZIO_INFERENCE_REPLACEMENT",
    "dynesty": "TOKEN_VAZIO_INFERENCE_REPLACEMENT",
    "astropy": "TOKEN_VAZIO_DOMAIN_REPLACEMENT",
    "requests": "RX_BOUNDED_HTTP_READ_ONLY",
}

def classify(path):
    if path.startswith("data/pipelines/structure_d/"):
        return "RLL_LEGACY_SCIENCE"
    if path.startswith("validacao_real/") or path.startswith("scripts/rll"):
        return "RLL_LEGACY_VALIDATION"
    if path.startswith("tests/"):
        return "TEST_LEGACY"
    if path.startswith("tools/") or path.startswith("internal/"):
        return "TOOLING_GOVERNANCE"
    if "notebook" in path.lower() or path.endswith(".ipynb"):
        return "HISTORICAL_NOTEBOOK"
    return "OTHER_REPOSITORY_CODE"

rows = []
by_class = Counter()
by_module = Counter()
token_vazio = []

for item in audit.get("files", []):
    path = item["path"]
    cls = classify(path)
    modules = list(item.get("external_imports", []))
    routes = {}
    for module in modules:
        route = replacement.get(module, "TOKEN_VAZIO_REPLACEMENT_ROUTE")
        routes[module] = route
        by_module[module] += 1
        if route.startswith("TOKEN_VAZIO"):
            token_vazio.append({"path": path, "module": module, "route": route})
    by_class[cls] += 1
    rows.append({
        "path": path,
        "class": cls,
        "external_imports": modules,
        "replacement_routes": routes,
        "automatic_rewrite_allowed": False,
        "reason": "semantic parity must be demonstrated before replacement",
    })

priority_order = {
    "RLL_LEGACY_SCIENCE": 0,
    "RLL_LEGACY_VALIDATION": 1,
    "TOOLING_GOVERNANCE": 2,
    "TEST_LEGACY": 3,
    "OTHER_REPOSITORY_CODE": 4,
    "HISTORICAL_NOTEBOOK": 5,
}
rows.sort(key=lambda row: (priority_order.get(row["class"], 99), row["path"]))

closed_families = []
if SERIALIZATION_PARITY.exists() and VALIDACAO_ZERO_DEP.exists():
    serialization = json.loads(SERIALIZATION_PARITY.read_text(encoding="utf-8"))
    zero_dep = json.loads(VALIDACAO_ZERO_DEP.read_text(encoding="utf-8"))
    if serialization.get("pass") is True and zero_dep.get("pass") is True:
        closed_families.append({
            "family": "validacao_real_yaml_matplotlib",
            "state": "MIGRATED_WITH_PARITY_GATE",
            "scope": [
                "validacao_real/fetch_real_data.py",
                "validacao_real/compute_validation.py",
                "validacao_real/make_figures.py",
                "validacao_real/render_report.py",
            ],
            "replacements": {
                "yaml": "JSON stdlib / versioned Rx payloads",
                "matplotlib": "rx.kernel.write_svg_chart",
            },
            "evidence": [
                str(SERIALIZATION_PARITY.relative_to(ROOT)),
                str(VALIDACAO_ZERO_DEP.relative_to(ROOT)),
            ],
            "legacy_yaml_preserved": True,
            "scientific_semantics_changed": False,
        })


if INVENTORY_CONFIG_PARITY.exists():
    inventory_parity = json.loads(INVENTORY_CONFIG_PARITY.read_text(encoding="utf-8"))
    docs_inventory_external = any(
        item.get("path") == "tools/docs_inventory.py" and item.get("external_imports")
        for item in audit.get("files", [])
    )
    if inventory_parity.get("pass") is True and not docs_inventory_external:
        closed_families.append({
            "family": "docs_inventory_config_yaml",
            "state": "MIGRATED_WITH_PARITY_GATE",
            "scope": [
                "tools/docs_inventory.py",
                "tools/inventory_config.json",
            ],
            "replacements": {
                "yaml": "JSON stdlib config",
            },
            "evidence": [
                str(INVENTORY_CONFIG_PARITY.relative_to(ROOT)),
                str(AUDIT.relative_to(ROOT)),
            ],
            "legacy_yaml_preserved": True,
            "scientific_semantics_changed": False,
        })


if PLOT_MIGRATION_GATE.exists():
    plot_gate = json.loads(PLOT_MIGRATION_GATE.read_text(encoding="utf-8"))
    plot_external = any(
        item.get("path") == "scripts/generate_rll_plots.py" and item.get("external_imports")
        for item in audit.get("files", [])
    )
    if plot_gate.get("pass") is True and not plot_external:
        closed_families.append({
            "family": "rll_real_run_plotting",
            "state": "MIGRATED_WITH_PARITY_GATE",
            "scope": [
                "scripts/generate_rll_plots.py",
                "rx/kernel.py",
            ],
            "replacements": {
                "pandas": "rx.read_csv / Python stdlib",
                "matplotlib": "Rx SVG renderer",
            },
            "evidence": [
                str(PLOT_MIGRATION_GATE.relative_to(ROOT)),
                str(AUDIT.relative_to(ROOT)),
            ],
            "legacy_png_contract": "mapped_to_svg_in_plots_manifest",
            "scientific_semantics_changed": False,
        })


if HTTP_MIGRATION_GATE.exists():
    http_gate = json.loads(HTTP_MIGRATION_GATE.read_text(encoding="utf-8"))
    if http_gate.get("pass") is True:
        closed_families.append({
            "family": "requests_public_read_fetchers",
            "state": "MIGRATED_WITH_PARITY_GATE",
            "scope": [
                "scripts/fetch_real_sources.py",
                "scripts/fetch_public_astronomy_catalog_samples.py",
                "rx/http.py",
            ],
            "replacements": {
                "requests": "rx.http bounded stdlib HTTPS GET transport",
            },
            "evidence": [
                str(HTTP_MIGRATION_GATE.relative_to(ROOT)),
            ],
            "network_write_allowed": False,
            "scientific_semantics_changed": False,
        })

if HTTP_MIGRATION_GATE.exists():
    http_gate = json.loads(HTTP_MIGRATION_GATE.read_text(encoding="utf-8"))
    if http_gate.get("pass") is True:
        closed_families.append({
            "family": "guarded_import_data_stdlib",
            "state": "MIGRATED_WITH_PARITY_GATE",
            "scope": [
                "scripts/import_data.py",
                ".github/workflows/import-data.yml",
                "rx/http.py",
            ],
            "replacements": {
                "requests": "rx.http bounded stdlib HTTPS GET transport",
                "pandas": "csv/json Python stdlib normalization",
            },
            "evidence": [
                str(HTTP_MIGRATION_GATE.relative_to(ROOT)),
            ],
            "credentialed_mode": "BLOCKED_REQUIRES_SEPARATE_REVIEWED_ROUTE",
            "scientific_semantics_changed": False,
        })

if CREDENTIAL_STDLIB_GATE.exists():
    credential_gate = json.loads(CREDENTIAL_STDLIB_GATE.read_text(encoding="utf-8"))
    if credential_gate.get("pass") is True:
        closed_families.append({
            "family": "credential_authority_pyyaml_stdlib",
            "state": "MIGRATED_WITH_PARITY_GATE",
            "scope": [
                "tools/validate_rll_credential_authority.py",
                "tests/test_rll_credential_authority.py",
            ],
            "replacements": {
                "yaml": "strict workflow-structure scanner over only required credential-governance fields",
            },
            "evidence": [
                str(CREDENTIAL_STDLIB_GATE.relative_to(ROOT)),
            ],
            "general_yaml_parser_claim": False,
            "scientific_semantics_changed": False,
        })

if WATCH_CONFIG_GATE.exists():
    watch_gate = json.loads(WATCH_CONFIG_GATE.read_text(encoding="utf-8"))
    if watch_gate.get("pass") is True:
        closed_families.append({
            "family": "technology_watch_yaml_jsonschema_stdlib",
            "state": "MIGRATED_WITH_PARITY_GATE",
            "scope": [
                "scripts/validate_watch_config.py",
                "rll_inovacao_tecnologica_watch.json",
                "rll_inovacao_tecnologica_watch.yml",
                "schemas/rll_watch.schema.json",
                "rx/yaml_subset.py",
                "rx/schema_subset.py",
            ],
            "replacements": {
                "yaml": "rx.yaml_subset strict parser",
                "jsonschema": "rx.schema_subset strict validator",
            },
            "evidence": [
                str(WATCH_CONFIG_GATE.relative_to(ROOT)),
            ],
            "legacy_yaml_preserved": True,
            "general_yaml_parser_claim": False,
            "general_json_schema_claim": False,
            "scientific_semantics_changed": False,
        })

if CALC_DATA_STDLIB_GATE.exists():
    calc_gate = json.loads(CALC_DATA_STDLIB_GATE.read_text(encoding="utf-8"))
    calc_external = any(
        item.get("path") == "scripts/calc_data.py" and item.get("external_imports")
        for item in audit.get("files", [])
    )
    if calc_gate.get("pass") is True and not calc_external:
        closed_families.append({
            "family": "calc_data_numpy_pandas_stdlib",
            "state": "MIGRATED_WITH_PARITY_GATE",
            "scope": [
                "scripts/calc_data.py",
                ".github/workflows/calc-data.yml",
            ],
            "replacements": {
                "numpy": "math/statistics Python stdlib",
                "pandas": "csv/json Python stdlib",
            },
            "evidence": [
                str(CALC_DATA_STDLIB_GATE.relative_to(ROOT)),
                str(AUDIT.relative_to(ROOT)),
            ],
            "statistics_contract": "mean/median/sample-std/min/max/non-null/sample-head-tail",
            "scientific_semantics_changed": False,
        })


if VALIDATION_DETERMINISTIC_GATE.exists():
    validation_gate = json.loads(VALIDATION_DETERMINISTIC_GATE.read_text(encoding="utf-8"))
    deterministic_paths = {
        "validation/load_data.py",
        "validation/run_lcdm.py",
        "validation/run_rll.py",
        "validation/compare_models.py",
    }
    deterministic_external = any(
        item.get("path") in deterministic_paths and item.get("external_imports")
        for item in audit.get("files", [])
    )
    if validation_gate.get("pass") is True and not deterministic_external:
        closed_families.append({
            "family": "validation_deterministic_numpy_pandas_stdlib",
            "state": "MIGRATED_WITH_PARITY_GATE",
            "scope": sorted(deterministic_paths),
            "legacy_adapter": "validation/load_data_numpy_legacy.py",
            "legacy_consumers": [
                "validation/bayes_rll.py",
                "validation/bayes_compare.py",
            ],
            "replacements": {
                "numpy": "math/list scalar operations",
                "pandas": "csv Python stdlib",
            },
            "evidence": [
                str(VALIDATION_DETERMINISTIC_GATE.relative_to(ROOT)),
                str(AUDIT.relative_to(ROOT)),
            ],
            "bayesian_legacy_migrated": False,
            "scientific_semantics_changed": False,
        })


payload = {
    "schema": "rll.rx.dependency_migration_plan.v1",
    "generated_utc": datetime.now(timezone.utc).replace(microsecond=0).isoformat(),
    "source": str(AUDIT.relative_to(ROOT)),
    "files_with_external_imports": audit.get("python_files_with_external_imports", 0),
    "by_class": dict(by_class),
    "by_module": dict(by_module),
    "rows": rows,
    "token_vazio_replacements": token_vazio,
    "closed_families": closed_families,
    "policy": {
        "automatic_mass_rewrite": False,
        "active_rx_runtime_already_zero_dependency": True,
        "migration_rule": "port -> parity gate -> switch route -> preserve legacy -> rollback",
        "training": False,
        "ai_runtime": False,
    },
    "claim_allowed": False,
}

OUT_JSON.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")

lines = [
    "# Rx dependency migration plan",
    "",
    "Global legacy files with external imports: **%d**." % payload["files_with_external_imports"],
    "",
    "Active Rx runtime remains zero-third-party; this ledger covers legacy/repository-wide debt.",
    "",
    "## By class",
    "",
]
for name, count in sorted(by_class.items(), key=lambda item: (-item[1], item[0])):
    lines.append("- %s: %d" % (name, count))

lines += ["", "## By module", ""]
for name, count in sorted(by_module.items(), key=lambda item: (-item[1], item[0])):
    lines.append("- %s: %d -> %s" % (name, count, replacement.get(name, "TOKEN_VAZIO_REPLACEMENT_ROUTE")))

lines += ["", "## Closed families", ""]
if closed_families:
    for family in closed_families:
        lines.append("- %s: %s" % (family["family"], family["state"]))
else:
    lines.append("- none observed in this execution")

lines += [
    "",
    "## Migration invariant",
    "",
    "port -> parity gate -> switch route -> preserve legacy -> rollback",
    "",
    "No mass search/replace is authorized because NumPy/SciPy/Pandas/YAML imports often encode scientific or serialization semantics, not only syntax.",
]
OUT_MD.write_text("\n".join(lines) + "\n", encoding="utf-8")

print("RX_DEPENDENCY_MIGRATION_PLAN=PASS")
print("files=", payload["files_with_external_imports"])
for name, count in sorted(by_class.items(), key=lambda item: (-item[1], item[0])):
    print(name, count)
print("token_vazio_replacements=", len(token_vazio))
print("closed_families=", len(closed_families))
print("wrote", OUT_JSON.relative_to(ROOT))
print("wrote", OUT_MD.relative_to(ROOT))
