#!/usr/bin/env python3
import json
import sys
from pathlib import Path

REQUIRED_GUARDS = (
    "provenance",
    "context",
    "evidence",
    "contradiction",
    "uncertainty",
    "reproduction",
    "rollback",
)

REPRO_BLOCKED = {
    "TOKEN_VAZIO",
    "TOKEN_VAZIO_SUCCESSOR_FIT",
    "BLOCKED",
}

def validate_matrix(data):
    errors = []
    if data.get("claim_allowed") is not False:
        errors.append("matrix:claim_allowed_must_be_false")
    guards = data.get("guards")
    if guards != list(REQUIRED_GUARDS):
        errors.append("matrix:guards_mismatch")
    if not data.get("projection_only"):
        errors.append("matrix:must_be_projection_only")
    if not data.get("source_registries"):
        errors.append("matrix:missing_source_registries")

    ids = set()
    for i, item in enumerate(data.get("workstreams", [])):
        prefix = f"workstreams[{i}]"
        iid = item.get("id")
        if not iid:
            errors.append(f"{prefix}:missing_id")
        elif iid in ids:
            errors.append(f"{prefix}:duplicate_id")
        ids.add(iid)

        if item.get("claim_allowed") is not False:
            errors.append(f"{prefix}:claim_allowed_must_be_false")

        for guard in REQUIRED_GUARDS:
            if guard not in item:
                errors.append(f"{prefix}:missing_{guard}")

        prov = item.get("provenance", {})
        if not prov.get("authority"):
            errors.append(f"{prefix}:provenance_authority_missing")
        if not prov.get("sources"):
            errors.append(f"{prefix}:provenance_sources_empty")

        ctx = item.get("context", {})
        if not ctx.get("scope"):
            errors.append(f"{prefix}:context_scope_missing")
        if not ctx.get("boundary"):
            errors.append(f"{prefix}:context_boundary_missing")

        evidence = item.get("evidence", {})
        if not evidence.get("state"):
            errors.append(f"{prefix}:evidence_state_missing")
        if evidence.get("state") in {"REPRODUCED_PROVIDER","REPRODUCED_NEGATIVE","SOURCE_REPORTED_EVIDENCED"} and not evidence.get("refs"):
            errors.append(f"{prefix}:evidence_refs_required")

        contra = item.get("contradiction", {})
        if not contra.get("state"):
            errors.append(f"{prefix}:contradiction_state_missing")
        if not contra.get("summary"):
            errors.append(f"{prefix}:contradiction_summary_missing")

        uncertainty = item.get("uncertainty", {})
        if not uncertainty.get("state"):
            errors.append(f"{prefix}:uncertainty_state_missing")
        if "open_items" not in uncertainty:
            errors.append(f"{prefix}:uncertainty_open_items_missing")

        reproduction = item.get("reproduction", {})
        if not reproduction.get("state"):
            errors.append(f"{prefix}:reproduction_state_missing")
        if not reproduction.get("procedure"):
            errors.append(f"{prefix}:reproduction_procedure_missing")

        rollback = item.get("rollback", {})
        if rollback.get("state") != "READY":
            errors.append(f"{prefix}:rollback_not_ready")
        if not rollback.get("anchor"):
            errors.append(f"{prefix}:rollback_anchor_missing")
        if not rollback.get("procedure"):
            errors.append(f"{prefix}:rollback_procedure_missing")

        if item.get("state") in {"CLOSED","REPRODUCED"} and reproduction.get("state") in REPRO_BLOCKED:
            errors.append(f"{prefix}:state_exceeds_reproduction")

    domains = {x.get("domain") for x in data.get("workstreams", [])}
    expected = {"background","cmb","growth","real_data","inference","magneto_plasma","literature"}
    missing = expected - domains
    if missing:
        errors.append("matrix:missing_domains:" + ",".join(sorted(missing)))

    return errors

def main():
    path = Path(sys.argv[1] if len(sys.argv) > 1 else "data/governance/RLL_EVIDENCE_EVOLUTION_MATRIX_V1.json")
    data = json.loads(path.read_text(encoding="utf-8"))
    errors = validate_matrix(data)
    if errors:
        print(json.dumps({"status":"FAIL","errors":errors}, indent=2))
        return 1
    print(json.dumps({
        "status":"PASS",
        "workstreams":len(data["workstreams"]),
        "guards":data["guards"],
        "claim_allowed":data["claim_allowed"],
    }, indent=2))
    return 0

if __name__ == "__main__":
    raise SystemExit(main())
